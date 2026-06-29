#!/usr/bin/env bash
# Test suite for lib/git-utils.sh — is_squash_merged()
# Run from project root: bash tests/test_git_utils.sh

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
    dir=$(mktemp -d "${TMPDIR:-/tmp}/git-utils-test.XXXXXX")
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

# ============================================================================
# Pre-flight
# ============================================================================

if [[ ! -f "$GIT_UTILS" ]]; then
    echo -e "${T_RED}ERROR${T_NC}: $GIT_UTILS not found"
    exit 1
fi

# shellcheck source=../lib/git-utils.sh
source "$GIT_UTILS"

# Create a temp repo on main with initial commit + dev branch
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
# Group 1: SAFE — squash-merged branch
# ============================================================================

echo -e "${T_BLUE}--- Group 1: SAFE (squash-merged branch) ---${T_NC}"

REPO_SQ=$(make_repo)
git -C "$REPO_SQ" checkout dev --quiet
git -C "$REPO_SQ" checkout -b "feature/sq-test" --quiet
add_commit "$REPO_SQ" "feat: feature work" "feature.txt"
git -C "$REPO_SQ" checkout dev --quiet
git -C "$REPO_SQ" merge --squash "feature/sq-test" --quiet
git -C "$REPO_SQ" commit -m "squash: feature work" --quiet

# Explicit branch arg
result=$(cd "$REPO_SQ" && is_squash_merged dev "feature/sq-test")
run_test "squash_merged_explicit_branch_SAFE" "SAFE" "$result"

# Default branch (switch to feature/sq-test, call without branch arg)
result=$(cd "$REPO_SQ" && git checkout "feature/sq-test" --quiet 2>/dev/null && is_squash_merged dev)
run_test "squash_merged_default_current_branch_SAFE" "SAFE" "$result"

# ============================================================================
# Group 2: NOT_MERGED — branch with unmerged commits
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 2: NOT_MERGED (unmerged branch) ---${T_NC}"

REPO_UNM=$(make_repo)
git -C "$REPO_UNM" checkout dev --quiet
git -C "$REPO_UNM" checkout -b "feature/unmerged" --quiet
add_commit "$REPO_UNM" "feat: unmerged work" "work.txt"
git -C "$REPO_UNM" checkout dev --quiet

result=$(cd "$REPO_UNM" && is_squash_merged dev "feature/unmerged")
run_test "unmerged_explicit_branch_NOT_MERGED" "NOT_MERGED" "$result"

# Default branch (switch to unmerged feature, call without branch arg)
result=$(cd "$REPO_UNM" && git checkout "feature/unmerged" --quiet 2>/dev/null && is_squash_merged dev)
run_test "unmerged_default_current_branch_NOT_MERGED" "NOT_MERGED" "$result"

# ============================================================================
# Group 3: UNKNOWN — error conditions
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 3: UNKNOWN (error conditions) ---${T_NC}"

# Outside a git repo
EMPTY_DIR=$(make_tmpdir)
result=$(cd "$EMPTY_DIR" && is_squash_merged dev "feature/anything" 2>/dev/null)
run_test "outside_git_repo_UNKNOWN" "UNKNOWN" "$result"

# Nonexistent branch arg
result=$(cd "$REPO_SQ" && is_squash_merged dev "nonexistent-branch-xyz" 2>/dev/null)
run_test "nonexistent_branch_UNKNOWN" "UNKNOWN" "$result"

# Nonexistent base
result=$(cd "$REPO_SQ" && is_squash_merged "nonexistent-base-xyz" "feature/sq-test" 2>/dev/null)
run_test "nonexistent_base_UNKNOWN" "UNKNOWN" "$result"

# Detached HEAD — git branch --show-current returns empty → branch arg absent → UNKNOWN
REPO_DET=$(make_repo)
git -C "$REPO_DET" checkout --detach HEAD --quiet 2>/dev/null
result=$(cd "$REPO_DET" && is_squash_merged dev 2>/dev/null)
run_test "detached_head_no_branch_UNKNOWN" "UNKNOWN" "$result"

# ============================================================================
# Group 4: Multi-commit squash
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 4: Multi-commit squash ---${T_NC}"

REPO_MULTI=$(make_repo)
git -C "$REPO_MULTI" checkout dev --quiet
git -C "$REPO_MULTI" checkout -b "feature/multi" --quiet
add_commit "$REPO_MULTI" "feat: first" "first.txt"
add_commit "$REPO_MULTI" "feat: second" "second.txt"
git -C "$REPO_MULTI" checkout dev --quiet
git -C "$REPO_MULTI" merge --squash "feature/multi" --quiet
git -C "$REPO_MULTI" commit -m "squash: feature/multi" --quiet

result=$(cd "$REPO_MULTI" && is_squash_merged dev "feature/multi")
run_test "multi_commit_squash_all_SAFE" "SAFE" "$result"

# ============================================================================
# Group 5: Partial squash — first commit cherry-picked to dev, second not
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 5: Partial squash (one commit unmerged) ---${T_NC}"

REPO_PART=$(make_repo)
git -C "$REPO_PART" checkout dev --quiet
git -C "$REPO_PART" checkout -b "feature/partial" --quiet
add_commit "$REPO_PART" "feat: first" "first.txt"
add_commit "$REPO_PART" "feat: second" "second.txt"
git -C "$REPO_PART" checkout dev --quiet
# Cherry-pick only the first feature commit so git cherry shows: - (first), + (second)
git -C "$REPO_PART" cherry-pick "feature/partial~1" --quiet 2>/dev/null

result=$(cd "$REPO_PART" && is_squash_merged dev "feature/partial")
run_test "partial_squash_second_unmerged_NOT_MERGED" "NOT_MERGED" "$result"

# ============================================================================
# Summary
# ============================================================================

echo ""
echo -e "${T_BOLD}===============================${T_NC}"
echo -e "${T_BOLD}  git-utils Test Summary${T_NC}"
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
