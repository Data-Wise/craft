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
