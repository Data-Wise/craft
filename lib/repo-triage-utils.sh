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
        {type: "branch+worktree", branch: $b.branch,
         merge_evidence: $b.merge_evidence, ancestor_result: $b.ancestor_result,
         pr_state: $b.pr_state, scoped_diff_result: $b.scoped_diff_result,
         path: $match.path, lock_status: $match.lock_status}
      else
        {type: "branch", branch: $b.branch,
         merge_evidence: $b.merge_evidence, ancestor_result: $b.ancestor_result,
         pr_state: $b.pr_state, scoped_diff_result: $b.scoped_diff_result}
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
