#!/bin/bash
# lib/repo-triage-utils.sh — merge/bucket helpers for the repo-triage skill.
# Requires jq. Pure JSON transforms — no git calls, no mutation, no network.
# Consumes JSONL emitted by lib/git-utils.sh's worktree_clean_dry_run() /
# branch_cleanup_dry_run() and by utils/repo_triage_classify.py.

# merge_candidates <branch_jsonl_file> <worktree_jsonl_file>
# Joins branch_cleanup_dry_run output with worktree_clean_dry_run output on
# the shared `branch` key (repo-triage GRILL Decision 13) so a branch that
# is also checked out in a worktree renders as ONE candidate item, never
# two independent opt-outs. Emits JSONL to stdout:
#   {"type": "branch+worktree"|"branch"|"worktree", "branch": ..., ...}
# Every field the branch collector emits passes through unchanged (the join adds
# `type`, and for a coupled pair the worktree's `path` and `lock_status`), so
# evidence added to the collector never needs a matching edit here.
# `type: "worktree"` is the rare fallback for a worktree whose branch never
# appeared in the branch stream (e.g. the base/protected branch).
merge_candidates() {
  local branch_file="$1"
  local worktree_file="$2"
  local empty_tmp
  empty_tmp=$(mktemp)
  trap 'rm -f "$empty_tmp"' RETURN

  [[ -f "$branch_file" ]] || branch_file="$empty_tmp"
  [[ -f "$worktree_file" ]] || worktree_file="$empty_tmp"

  jq -c --slurpfile worktrees <(jq -c -s '.' "$worktree_file" 2>/dev/null || echo '[]') '
    . as $b
    | ($worktrees[0] // []) as $wts
    | (($wts | map(select(.branch == $b.branch)) | first)) as $match
    | if $match then
        {type: "branch+worktree"} + $b
          + {path: $match.path, lock_status: $match.lock_status}
      else
        {type: "branch"} + $b
      end
  ' "$branch_file"

  jq -c --slurpfile branches <(jq -c -s '.' "$branch_file" 2>/dev/null || echo '[]') '
    . as $w
    | ($branches[0] // []) as $brs
    | if ([$brs[] | select(.branch == $w.branch)] | length) == 0 then
        {type: "worktree", branch: $w.branch, path: $w.path,
         is_merged_evidence: $w.is_merged_evidence, lock_status: $w.lock_status}
      else empty end
  ' "$worktree_file"
}

# verdict_candidates
# Reads merge_candidates()-shaped JSONL on stdin and adds a `verdict` and a
# one-line `evidence` string to every item (all input fields pass through).
# Report only: a verdict is advice for the user; nothing here deletes anything.
# Rules and precedence are GRILL-branch-triage-verdicts decisions 1, 6, 7, 8, 14, 15:
#
#   UNKNOWN            any of the 8 evidence fields is "unknown", absent, empty or
#                      outside its enum (a worktree-only item has none of them).
#                      Never defaults to delete.
#   KEEP               a live worktree, or an open PR.
#   DELETE-SAFE        the tip is an ancestor of base; OR a merged PR's head equals
#                      the tip AND its merge commit is in base AND the content is
#                      still present (merge_evidence merged/squash-merged, or a
#                      remote holds the tip). PR evidence alone is not enough: a
#                      reverted PR has it too.
#   BACKUP-THEN-DECIDE not landed and upstream_status is none or ahead, so the
#                      tip's only copy is local.
#   KEEP               everything else: tool-owned and not verified landed, or
#                      unmerged but pushed.
verdict_candidates() {
  jq -c '
    def spec: {
      merge_evidence:   ["merged", "squash-merged", "not-merged", "unknown"],
      ancestor_result:  ["ancestor", "not-ancestor", "unknown"],
      pr_open:          ["yes", "no", "unknown"],
      pr_head_match:    ["match", "mismatch", "none", "unknown"],
      pr_merge_in_base: ["yes", "no", "na", "unknown"],
      upstream_status:  ["none", "ahead", "present", "unknown"],
      worktree_status:  ["live", "none", "unknown"],
      owner_hint:       ["tool", "none", "unknown"]
    };
    . as $o
    | (spec | to_entries) as $fields
    | [ $fields[] | . as $e
        | select(($o[$e.key] | type) != "string" or ($e.value | index($o[$e.key])) == null)
        | $e.key ] as $bad
    | [ $fields[] | select($o[.key] == "unknown") | .key ] as $unknown
    | $o + (
        if $bad | length > 0 then
          { verdict: "UNKNOWN",
            evidence: (if $o.type == "worktree"
                       then "worktree-only item: no branch evidence"
                       else "absent or invalid evidence: " + ($bad | join(", ")) end) }
        elif $unknown | length > 0 then
          { verdict: "UNKNOWN", evidence: ("lookup failed: " + ($unknown | join(", "))) }
        elif $o.worktree_status == "live" then
          { verdict: "KEEP", evidence: "live worktree" }
        elif $o.pr_open == "yes" then
          { verdict: "KEEP", evidence: "open PR" }
        elif $o.ancestor_result == "ancestor" then
          { verdict: "DELETE-SAFE", evidence: "tip is an ancestor of base" }
        elif $o.pr_head_match == "match" and $o.pr_merge_in_base == "yes"
             and ($o.merge_evidence | IN("squash-merged", "merged")) then
          { verdict: "DELETE-SAFE",
            evidence: ("merged PR head equals tip, merge commit in base, content present (" + $o.merge_evidence + ")") }
        elif $o.pr_head_match == "match" and $o.pr_merge_in_base == "yes"
             and $o.upstream_status == "present" then
          { verdict: "DELETE-SAFE",
            evidence: "merged PR head equals tip, merge commit in base, a remote holds the tip" }
        elif $o.upstream_status == "none" or $o.upstream_status == "ahead" then
          { verdict: "BACKUP-THEN-DECIDE",
            evidence: ((if $o.upstream_status == "ahead"
                        then "unpushed commits: the tip exists only locally"
                        else "no remote copy: the tip exists only locally" end)
                       + (if $o.pr_head_match == "match"
                          then "; merged PR found but content not proven in base" else "" end)) }
        elif $o.owner_hint == "tool" then
          { verdict: "KEEP", evidence: "tool-owned branch, not verified landed" }
        else
          { verdict: "KEEP", evidence: "unmerged, pushed" }
        end)'
}

# verdict_command_blocks
# Reads verdict_candidates() JSONL on stdin and prints one block per verdict
# class (DELETE-SAFE, BACKUP-THEN-DECIDE, KEEP, UNKNOWN; empty classes are
# omitted): a header with the count, one line per branch with its evidence, and,
# for the two actionable classes only, the commands for the user to run.
#   DELETE-SAFE        git branch -d (ancestor) or -D (squash-merged: git cannot
#                      see it as merged, so -d would refuse)
#   BACKUP-THEN-DECIDE git push [-u] origin <branch>
# KEEP and UNKNOWN never get a command. No remote branch is ever deleted.
# Branch names go through jq's @sh, so quotes, spaces and `$(...)` stay one literal word.
# This only prints text; running anything stays with the user's confirm.
verdict_command_blocks() {
  jq -rs '
    def order: ["DELETE-SAFE", "BACKUP-THEN-DECIDE", "KEEP", "UNKNOWN"];
    def title: {
      "DELETE-SAFE": "landed; safe to delete locally",
      "BACKUP-THEN-DECIDE": "the tip exists only locally; back up before deciding",
      "KEEP": "leave alone",
      "UNKNOWN": "no command is offered; fix the failed lookup and re-run"
    };
    def cmd:
      if .verdict == "DELETE-SAFE" then
        (if .ancestor_result == "ancestor"
         then "git branch -d " + (.branch | @sh)
         else "git branch -D " + (.branch | @sh) end)
      elif .verdict == "BACKUP-THEN-DECIDE" then
        (if .upstream_status == "ahead"
         then "git push origin " + (.branch | @sh)
         else "git push -u origin " + (.branch | @sh) end)
      else empty end;
    . as $all
    | [ order[] as $v
        | ($all | map(select(.verdict == $v)) | sort_by(.branch)) as $items
        | select($items | length > 0)
        | ( ["## \($v) (\($items | length)) — \(title[$v])"]
            + [ $items[] | "  \(.branch)    \(.evidence)" ]
            + ( if $v == "DELETE-SAFE" then
                  [ "# run yourself (local branches only; remote deletes are never printed):" ]
                  + (if any($items[]; .ancestor_result != "ancestor")
                     then [ "# -D is for squash-merged branches: git cannot see them as merged, so -d would refuse" ]
                     else [] end)
                  + [ $items[] | cmd ]
                elif $v == "BACKUP-THEN-DECIDE" then
                  [ "# back up first, then decide:" ] + [ $items[] | cmd ]
                else [] end )
          ) | join("\n") ]
    | join("\n\n")
    | select(length > 0)'
}

# revalidate_verdicts <old_verdicts_jsonl> <new_verdicts_jsonl>
# Evidence can change between the scan and the action (GRILL decision 12): a
# worktree appears, a PR opens, a tip moves. Compares a first scan's
# verdict_candidates() output with a fresh re-scan's, per branch, and emits the
# fresh items with any difference downgraded to UNKNOWN, so a stale verdict is
# never acted on:
#   changed evidence field      -> UNKNOWN, "changed since scan: <fields>"
#   branch only in the re-scan  -> UNKNOWN, "appeared after scan"
#   branch only in the 1st scan -> UNKNOWN, "no longer present"
# An unchanged branch keeps its verdict. A missing or empty first scan means
# nothing is carried over on trust: every re-scanned branch reads UNKNOWN.
revalidate_verdicts() {
  local old_file="$1"
  local new_file="$2"
  local empty_tmp
  empty_tmp=$(mktemp)
  trap 'rm -f "$empty_tmp"' RETURN

  [[ -f "$old_file" ]] || old_file="$empty_tmp"
  [[ -f "$new_file" ]] || new_file="$empty_tmp"

  jq -c --slurpfile old <(jq -c -s '.' "$old_file" 2>/dev/null || echo '[]') '
    def fields: ["merge_evidence", "ancestor_result", "pr_open", "pr_head_match",
                 "pr_merge_in_base", "upstream_status", "worktree_status", "owner_hint"];
    . as $n
    | (($old[0] // []) | map(select(.branch == $n.branch)) | first) as $o
    | if $o == null then
        $n + {verdict: "UNKNOWN", evidence: "appeared after scan"}
      else
        ([fields[] | select($o[.] != $n[.])]) as $diff
        | if ($diff | length) > 0
          then $n + {verdict: "UNKNOWN", evidence: ("changed since scan: " + ($diff | join(", ")))}
          else $n end
      end
  ' "$new_file"

  jq -c --slurpfile new <(jq -c -s '.' "$new_file" 2>/dev/null || echo '[]') '
    . as $o
    | if (($new[0] // []) | map(select(.branch == $o.branch)) | length) == 0
      then {type: $o.type, branch: $o.branch, verdict: "UNKNOWN", evidence: "no longer present"}
      else empty end
  ' "$old_file"
}

# bucket_candidates
# Reads classify_issue()-shaped JSON objects (one per line: {status,
# evidence, reasoning, ...}) from stdin, tags each with a `bucket` field,
# and writes to stdout. Reuses grill's own self-definition
# (skills/workflow/grill/SKILL.md: "load-bearing branch" of unresolved
# questions) rather than inventing a second taxonomy:
#   status == "unclear" -> "grill-ready" (cannot mechanically verify =
#     a genuinely unresolved question)
#   status == "valid"   -> "plan-ready" (premise holds = single clear
#     next action: implement the fix)
#   anything else (e.g. "moot") -> "defer" (moot items are handled by
#     Phase 3's confirm/close flow before bucketing is ever reached; this
#     is a safety fallback, not the primary path for "moot")
bucket_candidates() {
  jq -c '
    if .status == "unclear" then . + {bucket: "grill-ready"}
    elif .status == "valid" then . + {bucket: "plan-ready"}
    else . + {bucket: "defer"}
    end
  '
}
