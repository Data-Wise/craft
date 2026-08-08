#!/usr/bin/env bash
# Test suite for lib/git-utils.sh — worktree_clean_dry_run() / branch_cleanup_dry_run()
# Phase 0 of docs/specs/ (see ORCHESTRATE-repo-triage.md) — `dev/git` Operation 5
# and Operation 4's dry-run / structured-output contract.
# Run from project root: bash tests/test_git_dryrun.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GIT_UTILS="${SCRIPT_DIR}/../lib/git-utils.sh"

T_RED='\033[0;31m'
T_GREEN='\033[0;32m'
T_BLUE='\033[0;34m'
T_BOLD='\033[1m'
T_NC='\033[0m'

TOTAL=0; PASS=0; FAIL=0
declare -a FAILED_NAMES=()
declare -a CLEANUP_DIRS=()

cleanup() {
    for dir in "${CLEANUP_DIRS[@]}"; do
        [[ -d "$dir" ]] && rm -rf "$dir"
    done
}
trap cleanup EXIT

make_tmpdir() {
    local dir
    dir=$(mktemp -d "${TMPDIR:-/tmp}/git-dryrun-test.XXXXXX")
    CLEANUP_DIRS+=("$dir")
    echo "$dir"
}

run_test() {
    local name="$1" expected="$2" actual="$3"
    TOTAL=$((TOTAL + 1))
    if [[ "$actual" == "$expected" ]]; then
        PASS=$((PASS + 1))
        echo -e "  ${T_GREEN}PASS${T_NC}  $name"
    else
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$name")
        echo -e "  ${T_RED}FAIL${T_NC}  $name  (expected='$expected', got='$actual')"
    fi
}

assert_true() {
    local name="$1" cond="$2"
    TOTAL=$((TOTAL + 1))
    if [[ "$cond" == "1" ]]; then
        PASS=$((PASS + 1))
        echo -e "  ${T_GREEN}PASS${T_NC}  $name"
    else
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$name")
        echo -e "  ${T_RED}FAIL${T_NC}  $name"
    fi
}

# ============================================================================
# Pre-flight
# ============================================================================

if [[ ! -f "$GIT_UTILS" ]]; then
    echo -e "${T_RED}ERROR${T_NC}: $GIT_UTILS not found"
    exit 1
fi

# shellcheck source=../lib/git-utils.sh
source "$GIT_UTILS"

if ! command -v jq >/dev/null 2>&1; then
    echo -e "${T_RED}ERROR${T_NC}: jq is required for this test suite"
    exit 1
fi

make_repo() {
    local repo
    repo=$(make_tmpdir)
    (
        cd "$repo"
        git init -b main --quiet
        git config user.email "test@test.com"
        git config user.name "Test User"
        echo "# README" > README.md
        git add README.md
        git commit -m "Initial commit" --quiet
        git branch dev
    )
    echo "$repo"
}

add_commit() {
    local repo="$1" msg="$2" file="${3:-file.txt}"
    echo "$msg" >> "${repo}/${file}"
    git -C "$repo" add "$file"
    git -C "$repo" commit -m "$msg" --quiet
}

# ============================================================================
# Group 1: branch_cleanup_dry_run — squash-merged branch, no mutation
# ============================================================================

echo -e "${T_BLUE}--- Group 1: branch_cleanup_dry_run (squash-merged) ---${T_NC}"

REPO1=$(make_repo)
git -C "$REPO1" checkout dev --quiet
git -C "$REPO1" checkout -b "feature/sq-test" --quiet
add_commit "$REPO1" "feat: feature work" "feature.txt"
git -C "$REPO1" checkout dev --quiet
git -C "$REPO1" merge --squash "feature/sq-test" --quiet
git -C "$REPO1" commit -m "squash: feature work" --quiet

BRANCHES_BEFORE=$(git -C "$REPO1" branch --format='%(refname:short)' | sort)
OUT1=$(cd "$REPO1" && branch_cleanup_dry_run dev)
BRANCHES_AFTER=$(git -C "$REPO1" branch --format='%(refname:short)' | sort)

run_test "branch_cleanup_zero_mutation" "$BRANCHES_BEFORE" "$BRANCHES_AFTER"

LINE1=$(echo "$OUT1" | grep '"feature/sq-test"')
run_test "branch_cleanup_emits_squash_candidate" "1" "$( [[ -n "$LINE1" ]] && echo 1 || echo 0)"

MERGE_EVIDENCE=$(echo "$LINE1" | jq -r '.merge_evidence')
run_test "branch_cleanup_merge_evidence_squash" "squash-merged" "$MERGE_EVIDENCE"

SCOPED_DIFF=$(echo "$LINE1" | jq -r '.scoped_diff_result')
run_test "branch_cleanup_scoped_diff_clean" "clean" "$SCOPED_DIFF"

KEYS=$(echo "$LINE1" | jq -S -c 'keys')
run_test "branch_cleanup_output_shape" '["ancestor_result","branch","merge_evidence","pr_state","scoped_diff_result"]' "$KEYS"

# ============================================================================
# Group 2: branch_cleanup_dry_run — active/unmerged branch NOT flagged
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 2: branch_cleanup_dry_run (active branch) ---${T_NC}"

REPO2=$(make_repo)
git -C "$REPO2" checkout dev --quiet
git -C "$REPO2" checkout -b "feature/active" --quiet
add_commit "$REPO2" "feat: still in progress" "wip.txt"
git -C "$REPO2" checkout dev --quiet

OUT2=$(cd "$REPO2" && branch_cleanup_dry_run dev)
LINE2=$(echo "$OUT2" | grep '"feature/active"')
MERGE_EVIDENCE2=$(echo "$LINE2" | jq -r '.merge_evidence')
run_test "branch_cleanup_active_branch_not_merged" "not-merged" "$MERGE_EVIDENCE2"

# ============================================================================
# Group 3: worktree_clean_dry_run — squash-merged worktree, no mutation
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 3: worktree_clean_dry_run (squash-merged worktree) ---${T_NC}"

REPO3=$(make_repo)
git -C "$REPO3" checkout dev --quiet
git -C "$REPO3" checkout -b "feature/wt-sq" --quiet
add_commit "$REPO3" "feat: worktree feature" "wtfeature.txt"
git -C "$REPO3" checkout dev --quiet

WT_DIR=$(make_tmpdir)
rmdir "$WT_DIR" 2>/dev/null || true
git -C "$REPO3" worktree add "$WT_DIR" "feature/wt-sq" --quiet
WT_DIR_RESOLVED=$(cd "$(dirname "$WT_DIR")" && pwd -P)/$(basename "$WT_DIR")

git -C "$REPO3" merge --squash "feature/wt-sq" --quiet
git -C "$REPO3" commit -m "squash: worktree feature" --quiet

WORKTREES_BEFORE=$(git -C "$REPO3" worktree list --porcelain)
OUT3=$(cd "$REPO3" && worktree_clean_dry_run dev)
WORKTREES_AFTER=$(git -C "$REPO3" worktree list --porcelain)

run_test "worktree_clean_zero_mutation" "$WORKTREES_BEFORE" "$WORKTREES_AFTER"

LINE3=$(echo "$OUT3" | grep '"feature/wt-sq"')
run_test "worktree_clean_emits_squash_candidate" "1" "$( [[ -n "$LINE3" ]] && echo 1 || echo 0)"

WT_EVIDENCE=$(echo "$LINE3" | jq -r '.is_merged_evidence')
run_test "worktree_clean_evidence_squash" "squash-merged" "$WT_EVIDENCE"

WT_PATH=$(echo "$LINE3" | jq -r '.path')
run_test "worktree_clean_path_matches" "$WT_DIR_RESOLVED" "$WT_PATH"

WT_KEYS=$(echo "$LINE3" | jq -S -c 'keys')
run_test "worktree_clean_output_shape" '["branch","is_merged_evidence","lock_status","path"]' "$WT_KEYS"

# Main worktree is never emitted as a candidate
MAIN_LINE=$(echo "$OUT3" | grep -c "\"$REPO3\"" || true)
run_test "worktree_clean_excludes_main_worktree" "0" "$MAIN_LINE"

# ============================================================================
# Group 4: Non-goal — neither function calls a mutating git subcommand
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 4: Non-goal (never mutates) ---${T_NC}"

MUTATING_CALLS=$(grep -nE 'git (branch -D|branch -d|worktree remove|worktree prune)' "$GIT_UTILS" | grep -vE '^[0-9]+:[[:space:]]*#' || true)
assert_true "git_utils_never_calls_mutating_commands" "$( [[ -z "$MUTATING_CALLS" ]] && echo 1 || echo 0)"

# ============================================================================
# Summary
# ============================================================================

echo ""
echo -e "${T_BOLD}===============================${T_NC}"
echo -e "${T_BOLD}  git-dryrun Test Summary${T_NC}"
echo -e "${T_BOLD}===============================${T_NC}"
echo ""
echo -e "  Total:  ${T_BOLD}$TOTAL${T_NC}"
echo -e "  Passed: ${T_GREEN}$PASS${T_NC}"
echo -e "  Failed: ${T_RED}$FAIL${T_NC}"
echo ""

if [[ $FAIL -gt 0 ]]; then
    echo -e "${T_RED}Failed tests:${T_NC}"
    for name in "${FAILED_NAMES[@]}"; do
        echo -e "  ${T_RED}-${T_NC} $name"
    done
    echo -e "${T_RED}RESULT: FAIL${T_NC}"
    exit 1
else
    echo -e "${T_GREEN}RESULT: ALL TESTS PASSED${T_NC}"
    exit 0
fi
