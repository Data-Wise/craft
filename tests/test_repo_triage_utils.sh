#!/usr/bin/env bash
# Test suite for lib/repo-triage-utils.sh — merge_candidates() / bucket_candidates()
# Phase 3.1 / 4.1 of ORCHESTRATE-repo-triage.md.
# Run from project root: bash tests/test_repo_triage_utils.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_FILE="${SCRIPT_DIR}/../lib/repo-triage-utils.sh"

T_RED='\033[0;31m'
T_GREEN='\033[0;32m'
T_BLUE='\033[0;34m'
T_BOLD='\033[1m'
T_NC='\033[0m'

TOTAL=0; PASS=0; FAIL=0
declare -a FAILED_NAMES=()
declare -a CLEANUP_FILES=()

cleanup() {
    for f in "${CLEANUP_FILES[@]}"; do
        [[ -f "$f" ]] && rm -f "$f"
    done
}
trap cleanup EXIT

make_tmpfile() {
    local f
    f=$(mktemp "${TMPDIR:-/tmp}/repo-triage-test.XXXXXX")
    CLEANUP_FILES+=("$f")
    echo "$f"
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

if [[ ! -f "$LIB_FILE" ]]; then
    echo -e "${T_RED}ERROR${T_NC}: $LIB_FILE not found"
    exit 1
fi

# shellcheck source=../lib/repo-triage-utils.sh
source "$LIB_FILE"

if ! command -v jq >/dev/null 2>&1; then
    echo -e "${T_RED}ERROR${T_NC}: jq is required for this test suite"
    exit 1
fi

# ============================================================================
# Group 1: merge_candidates — coupled branch+worktree pair
# ============================================================================

echo -e "${T_BLUE}--- Group 1: merge_candidates (coupled pair) ---${T_NC}"

BF=$(make_tmpfile)
WF=$(make_tmpfile)
cat > "$BF" <<'EOF'
{"branch":"feature/a","merge_evidence":"squash-merged","ancestor_result":"ancestor","pr_state":"merged","scoped_diff_result":"clean"}
EOF
cat > "$WF" <<'EOF'
{"path":"/wt/a","branch":"feature/a","is_merged_evidence":"squash-merged","lock_status":"unlocked"}
EOF

OUT=$(merge_candidates "$BF" "$WF")
LINE_COUNT=$(echo "$OUT" | wc -l | tr -d ' ')
run_test "coupled_pair_emits_one_item" "1" "$LINE_COUNT"

TYPE=$(echo "$OUT" | jq -r '.type')
run_test "coupled_pair_type" "branch+worktree" "$TYPE"

PATH_FIELD=$(echo "$OUT" | jq -r '.path')
run_test "coupled_pair_carries_worktree_path" "/wt/a" "$PATH_FIELD"

# ============================================================================
# Group 2: merge_candidates — no coupling (branch-only, worktree-only)
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 2: merge_candidates (no coupling) ---${T_NC}"

BF2=$(make_tmpfile)
WF2=$(make_tmpfile)
cat > "$BF2" <<'EOF'
{"branch":"feature/b","merge_evidence":"not-merged","ancestor_result":"not-ancestor","pr_state":"unknown","scoped_diff_result":"has-diff"}
EOF
cat > "$WF2" <<'EOF'
{"path":"/wt/c","branch":"feature/c","is_merged_evidence":"merged","lock_status":"unlocked"}
EOF

OUT2=$(merge_candidates "$BF2" "$WF2")
BRANCH_ONLY=$(echo "$OUT2" | jq -c 'select(.type == "branch")')
WT_ONLY=$(echo "$OUT2" | jq -c 'select(.type == "worktree")')

run_test "branch_only_present" "1" "$( [[ -n "$BRANCH_ONLY" ]] && echo 1 || echo 0)"
run_test "worktree_only_present" "1" "$( [[ -n "$WT_ONLY" ]] && echo 1 || echo 0)"

# ============================================================================
# Group 3: merge_candidates — dedup (no double-counting a coupled branch)
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 3: merge_candidates (dedup) ---${T_NC}"

BF3=$(make_tmpfile)
WF3=$(make_tmpfile)
cat > "$BF3" <<'EOF'
{"branch":"feature/dup","merge_evidence":"squash-merged","ancestor_result":"ancestor","pr_state":"merged","scoped_diff_result":"clean"}
EOF
cat > "$WF3" <<'EOF'
{"path":"/wt/dup","branch":"feature/dup","is_merged_evidence":"squash-merged","lock_status":"unlocked"}
EOF

OUT3=$(merge_candidates "$BF3" "$WF3")
DUP_COUNT=$(echo "$OUT3" | jq -r '.branch' | grep -c "feature/dup")
run_test "coupled_branch_appears_exactly_once" "1" "$DUP_COUNT"

# ============================================================================
# Group 4: merge_candidates — empty inputs (missing files) don't error
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 4: merge_candidates (empty inputs) ---${T_NC}"

OUT4=$(merge_candidates /nonexistent/branches.jsonl /nonexistent/worktrees.jsonl 2>&1)
run_test "missing_files_produce_no_output" "" "$OUT4"

# ============================================================================
# Group 5: bucket_candidates
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 5: bucket_candidates ---${T_NC}"

BUCKET_OUT=$(printf '%s\n' \
  '{"status":"unclear","evidence":[],"reasoning":"x"}' \
  '{"status":"valid","evidence":[],"reasoning":"y"}' \
  '{"status":"moot","evidence":[],"reasoning":"z"}' \
  | bucket_candidates)

UNCLEAR_BUCKET=$(echo "$BUCKET_OUT" | jq -c 'select(.status == "unclear") | .bucket' | tr -d '"')
run_test "unclear_is_grill_ready" "grill-ready" "$UNCLEAR_BUCKET"

VALID_BUCKET=$(echo "$BUCKET_OUT" | jq -c 'select(.status == "valid") | .bucket' | tr -d '"')
run_test "valid_is_plan_ready" "plan-ready" "$VALID_BUCKET"

MOOT_BUCKET=$(echo "$BUCKET_OUT" | jq -c 'select(.status == "moot") | .bucket' | tr -d '"')
run_test "moot_falls_back_to_defer" "defer" "$MOOT_BUCKET"

# ============================================================================
# Summary
# ============================================================================

echo ""
echo -e "${T_BOLD}===============================${T_NC}"
echo -e "${T_BOLD}  repo-triage-utils Test Summary${T_NC}"
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
