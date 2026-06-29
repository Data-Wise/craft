#!/bin/bash
# lib/git-utils.sh — Shared git utility functions for craft hooks
# Sourced by branch-guard.sh and other scripts. Requires git.

# is_squash_merged <base> <branch>
# Returns "SAFE" if all commits in <branch> are already in <base> (squash-merged).
# Returns "NOT_MERGED" if any commit with '+' prefix is found (unmerged work).
# Returns "UNKNOWN" if git cherry fails (not a git repo, invalid refs, etc.).
is_squash_merged() {
  local base="${1:-dev}"
  local branch="${2:-}"
  [[ -z "$branch" ]] && branch=$(git branch --show-current 2>/dev/null) || true
  [[ -z "$branch" ]] && echo "UNKNOWN" && return
  local cherry_out
  cherry_out=$(git cherry "$base" "$branch" 2>/dev/null) || { echo "UNKNOWN"; return; }
  if echo "$cherry_out" | grep -q '^+'; then
    echo "NOT_MERGED"
  else
    echo "SAFE"
  fi
}
