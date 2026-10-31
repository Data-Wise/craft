#!/bin/bash
# lib/git-utils.sh — Shared git utility functions for craft hooks
# Sourced by branch-guard.sh and other scripts. Requires git.

# is_squash_merged <base> <branch>
# Returns "SAFE" if all commits in <branch> are already in <base> (squash-merged).
# Returns "NOT_MERGED" if branch has unmerged work relative to base.
# Returns "UNKNOWN" if git commands fail (not a git repo, invalid refs, etc.).
#
# Detection strategy (two-pass):
#   1. git cherry (fast path): exact patch-ID match, reliable for single-commit squashes.
#   2. tree diff fallback: if cherry says NOT_MERGED, compare tip trees. When a
#      multi-commit squash is performed, both tips have identical content even though
#      cherry can't see it. Conservative: if base has advanced past the squash,
#      the trees diverge and this correctly returns NOT_MERGED (safe false-negative).
# normalize_merge_evidence <is_squash_merged-result>
# Maps is_squash_merged()'s SAFE/NOT_MERGED/UNKNOWN vocabulary to the
# squash-merged/not-merged/unknown strings both dry-run previews emit.
# Single source of truth so the two previews can't drift on this mapping.
normalize_merge_evidence() {
  case "$1" in
    SAFE) echo "squash-merged" ;;
    NOT_MERGED) echo "not-merged" ;;
    *) echo "unknown" ;;
  esac
}

is_squash_merged() {
  local base="${1:-dev}"
  local branch="${2:-}"
  [[ -z "$branch" ]] && branch=$(git branch --show-current 2>/dev/null) || true
  [[ -z "$branch" ]] && echo "UNKNOWN" && return
  # Validate both refs exist (catches non-git-repo, nonexistent branches, etc.)
  git rev-parse "$base" "$branch" &>/dev/null || { echo "UNKNOWN"; return; }
  local cherry_out
  cherry_out=$(git cherry "$base" "$branch" 2>/dev/null) || { echo "UNKNOWN"; return; }
  if ! echo "$cherry_out" | grep -q '^+'; then
    echo "SAFE"
    return
  fi
  # Fallback: tree comparison handles multi-commit squash merges.
  local diff_out
  diff_out=$(git diff "${base}..${branch}" 2>/dev/null) || { echo "NOT_MERGED"; return; }
  if [[ -z "$diff_out" ]]; then
    echo "SAFE"
  else
    echo "NOT_MERGED"
  fi
}

# worktree_clean_dry_run [base]
# Collection-only preview for `dev/git` Operation 5's `clean` sub-action.
# Emits one JSON object per line (JSONL) — never mutates, never removes a
# worktree, never runs `git worktree remove`/`prune`.
#
# Output contract (repo-triage GRILL Decision 13's join key is `branch`):
#   {"path": <worktree path>, "branch": <branch name>,
#    "is_merged_evidence": "merged"|"squash-merged"|"not-merged"|"unknown",
#    "lock_status": "locked"|"unlocked"}
#
# Skips the main worktree (the one `git worktree list` reports first) and
# any detached-HEAD worktree (no branch to join on).
worktree_clean_dry_run() {
  local base="${1:-dev}"
  local main_worktree
  main_worktree=$(git worktree list --porcelain 2>/dev/null | awk '/^worktree /{print $2; exit}')
  local merged_list
  merged_list=$(git branch --merged "$base" 2>/dev/null | sed 's/^[* ]*//')

  git worktree list --porcelain 2>/dev/null | awk '
    /^worktree / { if (path != "") print path"\t"branch"\t"locked; path=$2; branch=""; locked="unlocked" }
    /^branch /   { b=$2; sub("refs/heads/","",b); branch=b }
    /^locked/    { locked="locked" }
    END          { if (path != "") print path"\t"branch"\t"locked }
  ' | while IFS=$'\t' read -r wpath wbranch wlocked; do
    [[ "$wpath" == "$main_worktree" ]] && continue
    [[ -z "$wbranch" ]] && continue

    local evidence
    if echo "$merged_list" | grep -qx "$wbranch"; then
      evidence="merged"
    else
      evidence=$(normalize_merge_evidence "$(is_squash_merged "$base" "$wbranch")")
    fi

    jq -cn --arg path "$wpath" --arg branch "$wbranch" \
      --arg ev "$evidence" --arg lock "$wlocked" \
      '{path: $path, branch: $branch, is_merged_evidence: $ev, lock_status: $lock}'
  done
}

# _ancestry_state <commit> <ref>
# Maps `git merge-base --is-ancestor` to a three-way answer: exit 0 =
# "ancestor", exit 1 = "not-ancestor", any other exit (fatal error, missing or
# unfetched object, shallow clone) = "unknown". Collapsing the failure case into
# "not-ancestor" would turn "could not check" into a confident negative.
_ancestry_state() {
  [[ -n "${1:-}" && -n "${2:-}" ]] || { echo "unknown"; return; }
  git merge-base --is-ancestor "$1" "$2" 2>/dev/null
  case $? in
    0) echo "ancestor" ;;
    1) echo "not-ancestor" ;;
    *) echo "unknown" ;;
  esac
}

# Largest PR list requested per branch. A result this long may be truncated, so
# it is reported as "unknown" rather than trusted.
_PR_LOOKUP_LIMIT=100

# _pr_evidence <branch> <tip-sha> <base>
# Echoes four space-separated words: pr_state pr_open pr_head_match pr_merge_in_base.
# One `gh` call covers open and merged PRs. Fork PRs (isCrossRepository) are
# ignored: a same-named branch in a fork says nothing about this branch.
# Any lookup failure, a non-array reply, or a list at the request limit yields
# "unknown" for all four, never "none"/"no".
_pr_evidence() {
  local branch="$1" tip="$2" base="$3"
  local unknown="unknown unknown unknown unknown"
  command -v gh >/dev/null 2>&1 || { echo "$unknown"; return; }
  [[ -n "$tip" ]] || { echo "$unknown"; return; }

  local prs count
  prs=$(gh pr list --head "$branch" --state all --limit "$_PR_LOOKUP_LIMIT" \
    --json number,state,headRefOid,mergeCommit,isCrossRepository 2>/dev/null) || { echo "$unknown"; return; }
  count=$(jq -e 'if type == "array" then length else error("not an array") end' <<<"$prs" 2>/dev/null) \
    || { echo "$unknown"; return; }
  (( count < _PR_LOOKUP_LIMIT )) || { echo "$unknown"; return; }

  # `|` is a non-whitespace separator, so empty fields survive `read`. A merged
  # PR with no merge commit is encoded "-" so the oid list is never empty.
  local fields state open head_match oids
  fields=$(jq -r --arg tip "$tip" '
    (map(select((.isCrossRepository // false) | not))) as $same
    | ($same | map(select(.state == "MERGED"))) as $merged
    | ($merged | map(select(.headRefOid == $tip))) as $hit
    | [ (if any(.[]; .state == "MERGED") then "merged" else "unknown" end),
        (if any($same[]; .state == "OPEN") then "yes" else "no" end),
        (if ($hit | length) > 0 then "match"
         elif ($merged | length) > 0 then "mismatch" else "none" end),
        ($hit | map(.mergeCommit.oid // "-") | join(",")) ]
    | join("|")' <<<"$prs" 2>/dev/null) || { echo "$unknown"; return; }
  IFS='|' read -r state open head_match oids <<<"$fields"

  # For a head match, is the PR's merge commit actually reachable from base?
  # yes if any matching PR's merge commit is; unknown if one could not be
  # checked; otherwise no. "na" when there is no head match.
  local merge_in_base="na"
  if [[ "$head_match" == "match" ]]; then
    merge_in_base="no"
    local oid st saw_unknown=0
    for oid in ${oids//,/ }; do
      if [[ "$oid" == "-" ]]; then saw_unknown=1; continue; fi
      st=$(_ancestry_state "$oid" "$base")
      case "$st" in
        ancestor) merge_in_base="yes"; break ;;
        unknown) saw_unknown=1 ;;
      esac
    done
    if [[ "$merge_in_base" != "yes" && "$saw_unknown" == "1" ]]; then
      merge_in_base="unknown"
    fi
  fi
  echo "$state $open $head_match $merge_in_base"
}

# branch_cleanup_dry_run [base]
# Collection-only preview for `dev/git` Operation 4's branch-cleanup step.
# Emits one JSON object per line (JSONL) — never mutates, never runs
# `git branch -D`/`-d`. Evidence only: it emits no verdict.
#
# Output contract (every field is always present; no empty strings):
#   {"branch": <name>, "merge_evidence": "merged"|"squash-merged"|"not-merged"|"unknown",
#    "ancestor_result": "ancestor"|"not-ancestor"|"unknown" ("unknown" on any
#    `merge-base --is-ancestor` exit other than 0/1),
#    "pr_state": "merged"|"unknown" (best-effort; "unknown" when `gh` is unavailable,
#    fails, or no merged PR is found),
#    "pr_open": "yes"|"no"|"unknown" (a same-repo open PR exists for the branch),
#    "pr_head_match": "match"|"mismatch"|"none"|"unknown" (a same-repo merged PR's
#    headRefOid equals the branch tip / merged PRs exist but none match / no merged
#    PR / lookup failed or may be truncated),
#    "pr_merge_in_base": "yes"|"no"|"na"|"unknown" (for a head match, the PR's merge
#    commit is reachable from base; "na" without a head match),
#    "scoped_diff_result": "clean"|"has-diff"|"unknown"
#    ("unknown" when `git diff` itself fails — e.g. a broken ref — never
#    treated as equivalent to a clean diff)}
#
# Skips the base branch, `main`, and the current branch.
branch_cleanup_dry_run() {
  local base="${1:-dev}"
  local current
  current=$(git branch --show-current 2>/dev/null)
  local merged_list
  merged_list=$(git branch --merged "$base" 2>/dev/null | sed 's/^[* ]*//')

  git for-each-ref --format='%(refname:short)' refs/heads/ 2>/dev/null | while read -r branch; do
    [[ "$branch" == "$base" || "$branch" == "main" || "$branch" == "$current" ]] && continue

    local merge_evidence
    if echo "$merged_list" | grep -qx "$branch"; then
      merge_evidence="merged"
    else
      merge_evidence=$(normalize_merge_evidence "$(is_squash_merged "$base" "$branch")")
    fi

    local ancestor_result
    ancestor_result=$(_ancestry_state "$branch" "$base")

    local tip pr_state pr_open pr_head_match pr_merge_in_base
    tip=$(git rev-parse --verify --quiet "refs/heads/${branch}^{commit}" 2>/dev/null) || tip=""
    read -r pr_state pr_open pr_head_match pr_merge_in_base <<<"$(_pr_evidence "$branch" "$tip" "$base")"

    local diff_out scoped_diff_result
    if diff_out=$(git diff "${base}..${branch}" 2>/dev/null); then
      if [[ -z "$diff_out" ]]; then
        scoped_diff_result="clean"
      else
        scoped_diff_result="has-diff"
      fi
    else
      scoped_diff_result="unknown"
    fi

    jq -cn --arg branch "$branch" --arg me "$merge_evidence" --arg ar "$ancestor_result" \
      --arg ps "$pr_state" --arg po "$pr_open" --arg phm "$pr_head_match" \
      --arg pmb "$pr_merge_in_base" --arg sd "$scoped_diff_result" \
      '{branch: $branch, merge_evidence: $me, ancestor_result: $ar, pr_state: $ps,
        pr_open: $po, pr_head_match: $phm, pr_merge_in_base: $pmb,
        scoped_diff_result: $sd}'
  done
}
