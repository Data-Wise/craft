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
      evidence=$(is_squash_merged "$base" "$wbranch")
      case "$evidence" in
        SAFE) evidence="squash-merged" ;;
        NOT_MERGED) evidence="not-merged" ;;
        *) evidence="unknown" ;;
      esac
    fi

    jq -cn --arg path "$wpath" --arg branch "$wbranch" \
      --arg ev "$evidence" --arg lock "$wlocked" \
      '{path: $path, branch: $branch, is_merged_evidence: $ev, lock_status: $lock}'
  done
}

# branch_cleanup_dry_run [base]
# Collection-only preview for `dev/git` Operation 4's branch-cleanup step.
# Emits one JSON object per line (JSONL) — never mutates, never runs
# `git branch -D`/`-d`.
#
# Output contract:
#   {"branch": <name>, "merge_evidence": "merged"|"squash-merged"|"not-merged"|"unknown",
#    "ancestor_result": "ancestor"|"not-ancestor",
#    "pr_state": "merged"|"unknown" (best-effort; "unknown" when `gh` is unavailable
#    or no merged PR is found), "scoped_diff_result": "clean"|"has-diff"}
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
      merge_evidence=$(is_squash_merged "$base" "$branch")
      case "$merge_evidence" in
        SAFE) merge_evidence="squash-merged" ;;
        NOT_MERGED) merge_evidence="not-merged" ;;
        *) merge_evidence="unknown" ;;
      esac
    fi

    local ancestor_result
    if git merge-base --is-ancestor "$branch" "$base" 2>/dev/null; then
      ancestor_result="ancestor"
    else
      ancestor_result="not-ancestor"
    fi

    local pr_state="unknown"
    if command -v gh >/dev/null 2>&1; then
      local pr_num
      pr_num=$(gh pr list --head "$branch" --state merged --json number -q '.[0].number' 2>/dev/null)
      [[ -n "$pr_num" ]] && pr_state="merged"
    fi

    local diff_out scoped_diff_result
    diff_out=$(git diff "${base}..${branch}" 2>/dev/null)
    if [[ -z "$diff_out" ]]; then
      scoped_diff_result="clean"
    else
      scoped_diff_result="has-diff"
    fi

    jq -cn --arg branch "$branch" --arg me "$merge_evidence" --arg ar "$ancestor_result" \
      --arg ps "$pr_state" --arg sd "$scoped_diff_result" \
      '{branch: $branch, merge_evidence: $me, ancestor_result: $ar, pr_state: $ps, scoped_diff_result: $sd}'
  done
}
