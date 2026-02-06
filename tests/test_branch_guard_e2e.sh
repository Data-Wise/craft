#!/usr/bin/env bash
#
# E2E Dogfooding Tests for ~/.claude/hooks/branch-guard.sh
# Tests: Multi-step realistic workflows, config cascades, bypass lifecycle,
#        cross-tool consistency, performance, and real-world scenarios.
#
# Usage:
#   bash tests/test_branch_guard_e2e.sh
#
# Differs from test_branch_guard.sh (unit tests) by exercising full workflows
# with multiple steps and cross-component interactions.
#
# Requirements:
#   - ~/.claude/hooks/branch-guard.sh must exist
#   - git must be available

# Note: Not using 'set -e' because we want tests to continue after failures
set -uo pipefail

# ============================================================================
# Configuration
# ============================================================================

HOOK_SCRIPT="$HOME/.claude/hooks/branch-guard.sh"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color output
T_RED='\033[0;31m'
T_GREEN='\033[0;32m'
T_YELLOW='\033[1;33m'
T_BLUE='\033[0;34m'
T_BOLD='\033[1m'
T_NC='\033[0m'

# Test counters
TOTAL=0
PASS=0
FAIL=0
SKIP=0

declare -a FAILED_NAMES=()

# Temp directories to clean up
declare -a CLEANUP_DIRS=()

# ============================================================================
# Preflight Check
# ============================================================================

if [[ ! -f "$HOOK_SCRIPT" ]]; then
    echo -e "${T_RED}ERROR${T_NC}: Hook script not found at $HOOK_SCRIPT"
    echo "  Create the hook first, then run these tests."
    exit 1
fi

if ! command -v git &>/dev/null; then
    echo -e "${T_RED}ERROR${T_NC}: git is not available"
    exit 1
fi

# ============================================================================
# Helpers (same pattern as test_branch_guard.sh)
# ============================================================================

make_tmpdir() {
    local dir
    dir=$(mktemp -d "${TMPDIR:-/tmp}/branch-guard-e2e.XXXXXX")
    CLEANUP_DIRS+=("$dir")
    echo "$dir"
}

cleanup() {
    for dir in "${CLEANUP_DIRS[@]}"; do
        if [[ -d "$dir" ]]; then
            rm -rf "$dir"
        fi
    done
}
trap cleanup EXIT

init_repo() {
    local no_dev=false
    if [[ "${1:-}" == "--no-dev" ]]; then
        no_dev=true
    fi

    local repo
    repo=$(make_tmpdir)

    (
        cd "$repo"
        git init -b main --quiet
        git config user.email "test@test.com"
        git config user.name "Test"

        mkdir -p src tests .claude docs utils
        echo "# README" > README.md
        echo "print('hello')" > src/app.py
        echo "# Status" > .STATUS
        git add -A
        git commit -m "Initial commit" --quiet

        if [[ "$no_dev" == false ]]; then
            git branch dev
        fi
    )

    echo "$repo"
}

switch_branch() {
    local repo="$1" branch="$2"
    (cd "$repo" && git checkout "$branch" --quiet 2>/dev/null)
}

create_and_switch() {
    local repo="$1" branch="$2"
    (cd "$repo" && git checkout -b "$branch" --quiet 2>/dev/null)
}

json_edit() {
    local file_path="$1" cwd="$2"
    printf '{"tool_name":"Edit","tool_input":{"file_path":"%s","old_string":"x","new_string":"y"},"cwd":"%s"}' \
        "$file_path" "$cwd"
}

json_write() {
    local file_path="$1" cwd="$2"
    printf '{"tool_name":"Write","tool_input":{"file_path":"%s","content":"# new content"},"cwd":"%s"}' \
        "$file_path" "$cwd"
}

json_bash() {
    local command="$1" cwd="$2"
    printf '{"tool_name":"Bash","tool_input":{"command":"%s"},"cwd":"%s"}' \
        "$command" "$cwd"
}

run_test() {
    local name="$1" expected_exit="$2" json="$3" cwd="${4:-}"

    TOTAL=$((TOTAL + 1))

    local actual_exit=0
    local stderr_output=""

    if [[ -n "$cwd" ]]; then
        stderr_output=$(echo "$json" | (cd "$cwd" && bash "$HOOK_SCRIPT") 2>&1 >/dev/null) || actual_exit=$?
    else
        stderr_output=$(echo "$json" | bash "$HOOK_SCRIPT" 2>&1 >/dev/null) || actual_exit=$?
    fi

    if [[ "$actual_exit" -eq "$expected_exit" ]]; then
        PASS=$((PASS + 1))
        echo -e "  ${T_GREEN}PASS${T_NC}  $name  ${T_BOLD}(exit=$actual_exit)${T_NC}"
    else
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$name")
        echo -e "  ${T_RED}FAIL${T_NC}  $name  ${T_BOLD}(expected=$expected_exit, got=$actual_exit)${T_NC}"
        if [[ -n "$stderr_output" ]]; then
            echo -e "        stderr: $(echo "$stderr_output" | head -3)"
        fi
    fi
}

run_test_with_stderr() {
    local name="$1" expected_exit="$2" json="$3" cwd="$4" expected_pattern="$5"

    TOTAL=$((TOTAL + 1))

    local actual_exit=0
    local stderr_output=""
    stderr_output=$(echo "$json" | (cd "$cwd" && bash "$HOOK_SCRIPT") 2>&1 >/dev/null) || actual_exit=$?

    local exit_ok=false pattern_ok=false

    [[ "$actual_exit" -eq "$expected_exit" ]] && exit_ok=true
    if echo "$stderr_output" | grep -qiE "$expected_pattern" 2>/dev/null; then
        pattern_ok=true
    fi

    if [[ "$exit_ok" == true && "$pattern_ok" == true ]]; then
        PASS=$((PASS + 1))
        echo -e "  ${T_GREEN}PASS${T_NC}  $name  ${T_BOLD}(exit=$actual_exit, pattern matched)${T_NC}"
    elif [[ "$exit_ok" == true && "$pattern_ok" == false ]]; then
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$name")
        echo -e "  ${T_RED}FAIL${T_NC}  $name  ${T_BOLD}(exit OK, but stderr missing pattern: '$expected_pattern')${T_NC}"
        echo -e "        stderr: $(echo "$stderr_output" | head -3)"
    else
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$name")
        echo -e "  ${T_RED}FAIL${T_NC}  $name  ${T_BOLD}(expected exit=$expected_exit, got=$actual_exit)${T_NC}"
        if [[ -n "$stderr_output" ]]; then
            echo -e "        stderr: $(echo "$stderr_output" | head -3)"
        fi
    fi
}

# Check that stderr does NOT contain a pattern
run_test_without_stderr() {
    local name="$1" expected_exit="$2" json="$3" cwd="$4" forbidden_pattern="$5"

    TOTAL=$((TOTAL + 1))

    local actual_exit=0
    local stderr_output=""
    stderr_output=$(echo "$json" | (cd "$cwd" && bash "$HOOK_SCRIPT") 2>&1 >/dev/null) || actual_exit=$?

    local exit_ok=false pattern_absent=true

    [[ "$actual_exit" -eq "$expected_exit" ]] && exit_ok=true
    if echo "$stderr_output" | grep -qiE "$forbidden_pattern" 2>/dev/null; then
        pattern_absent=false
    fi

    if [[ "$exit_ok" == true && "$pattern_absent" == true ]]; then
        PASS=$((PASS + 1))
        echo -e "  ${T_GREEN}PASS${T_NC}  $name  ${T_BOLD}(exit=$actual_exit, no forbidden output)${T_NC}"
    elif [[ "$exit_ok" == true && "$pattern_absent" == false ]]; then
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$name")
        echo -e "  ${T_RED}FAIL${T_NC}  $name  ${T_BOLD}(exit OK, but stderr contains forbidden: '$forbidden_pattern')${T_NC}"
        echo -e "        stderr: $(echo "$stderr_output" | head -3)"
    else
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$name")
        echo -e "  ${T_RED}FAIL${T_NC}  $name  ${T_BOLD}(expected exit=$expected_exit, got=$actual_exit)${T_NC}"
    fi
}

skip() {
    local name="$1" reason="${2:-Skipped}"
    TOTAL=$((TOTAL + 1))
    SKIP=$((SKIP + 1))
    echo -e "  ${T_YELLOW}SKIP${T_NC}  $name  ($reason)"
}

# ============================================================================
# Test Groups
# ============================================================================

echo ""
echo -e "${T_BOLD}Branch Guard E2E Dogfooding Tests${T_NC}"
echo -e "${T_BOLD}=================================${T_NC}"
echo -e "Hook: $HOOK_SCRIPT"
echo ""

# --------------------------------------------------------------------------
# Group 1: Full workflow — dev -> feature worktree -> back to dev
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Group 1: Full Workflow (dev -> worktree -> dev) ---${T_NC}"

REPO_WF=$(init_repo)

# Step 1: On dev, new code is blocked
switch_branch "$REPO_WF" "dev"

run_test \
    "e2e_workflow_step1_dev_blocks_new_code" \
    2 \
    "$(json_write "$REPO_WF/src/feature.py" "$REPO_WF")" \
    "$REPO_WF"

# Step 2: Create feature branch, new code is allowed
create_and_switch "$REPO_WF" "feature/new-thing"

run_test \
    "e2e_workflow_step2_feature_allows_new_code" \
    0 \
    "$(json_write "$REPO_WF/src/feature.py" "$REPO_WF")" \
    "$REPO_WF"

# Step 3: Switch back to dev, blocked again
switch_branch "$REPO_WF" "dev"

run_test \
    "e2e_workflow_step3_back_to_dev_blocked_again" \
    2 \
    "$(json_write "$REPO_WF/src/feature.py" "$REPO_WF")" \
    "$REPO_WF"

echo ""

# --------------------------------------------------------------------------
# Group 2: Bypass lifecycle
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Group 2: Bypass Lifecycle ---${T_NC}"

REPO_BP=$(init_repo)
switch_branch "$REPO_BP" "dev"
MARKER_FILE="$REPO_BP/.claude/allow-dev-edit"

# Step 1: Blocked without marker
run_test \
    "e2e_bypass_step1_blocked_without_marker" \
    2 \
    "$(json_write "$REPO_BP/src/new.py" "$REPO_BP")" \
    "$REPO_BP"

# Step 2: Create marker with JSON content -> allowed
mkdir -p "$REPO_BP/.claude"
cat > "$MARKER_FILE" <<'EOF'
{"reason":"testing bypass","timestamp":"2026-02-06T12:00:00Z","branch":"dev"}
EOF

run_test \
    "e2e_bypass_step2_allowed_with_marker" \
    0 \
    "$(json_write "$REPO_BP/src/new.py" "$REPO_BP")" \
    "$REPO_BP"

# Step 3: Verify marker has valid JSON content
TOTAL=$((TOTAL + 1))
if jq -e . "$MARKER_FILE" &>/dev/null; then
    PASS=$((PASS + 1))
    echo -e "  ${T_GREEN}PASS${T_NC}  e2e_bypass_step3_marker_valid_json  ${T_BOLD}(valid JSON)${T_NC}"
elif python3 -c "import json; json.load(open('$MARKER_FILE'))" &>/dev/null; then
    PASS=$((PASS + 1))
    echo -e "  ${T_GREEN}PASS${T_NC}  e2e_bypass_step3_marker_valid_json  ${T_BOLD}(valid JSON via python3)${T_NC}"
else
    FAIL=$((FAIL + 1))
    FAILED_NAMES+=("e2e_bypass_step3_marker_valid_json")
    echo -e "  ${T_RED}FAIL${T_NC}  e2e_bypass_step3_marker_valid_json  ${T_BOLD}(marker not valid JSON)${T_NC}"
fi

# Step 4: Remove marker -> blocked again
rm -f "$MARKER_FILE"

run_test \
    "e2e_bypass_step4_blocked_after_removal" \
    2 \
    "$(json_write "$REPO_BP/src/new.py" "$REPO_BP")" \
    "$REPO_BP"

echo ""

# --------------------------------------------------------------------------
# Group 3: Config cascade
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Group 3: Config Cascade ---${T_NC}"

# Test 3a: No config (auto-detect) — main=block-all, dev=block-new-code
REPO_NC=$(init_repo)
# Ensure no config exists
rm -f "$REPO_NC/.claude/branch-guard.json"

switch_branch "$REPO_NC" "main"
run_test \
    "e2e_config_no_config_main_blocked" \
    2 \
    "$(json_edit "$REPO_NC/README.md" "$REPO_NC")" \
    "$REPO_NC"

switch_branch "$REPO_NC" "dev"
run_test \
    "e2e_config_no_config_dev_blocks_new" \
    2 \
    "$(json_write "$REPO_NC/src/new.py" "$REPO_NC")" \
    "$REPO_NC"

# Test 3b: Custom config overrides auto-detect
# Config says staging=block-all but NOT main
REPO_CC=$(init_repo)
create_and_switch "$REPO_CC" "staging"

mkdir -p "$REPO_CC/.claude"
cat > "$REPO_CC/.claude/branch-guard.json" <<'EOF'
{"staging": "block-all"}
EOF

# staging is blocked via config
run_test \
    "e2e_config_custom_staging_blocked" \
    2 \
    "$(json_edit "$REPO_CC/README.md" "$REPO_CC")" \
    "$REPO_CC"

# main with custom config — config is explicit, main not listed means allowed
switch_branch "$REPO_CC" "main"
run_test \
    "e2e_config_custom_main_not_listed_allowed" \
    0 \
    "$(json_edit "$REPO_CC/README.md" "$REPO_CC")" \
    "$REPO_CC"

# Test 3c: Malformed config falls through gracefully
REPO_BAD=$(init_repo)
mkdir -p "$REPO_BAD/.claude"
echo "this is not json at all {{{" > "$REPO_BAD/.claude/branch-guard.json"

switch_branch "$REPO_BAD" "main"
# With malformed config, extract_json_string won't find the branch -> no protection
run_test \
    "e2e_config_malformed_fallthrough" \
    0 \
    "$(json_edit "$REPO_BAD/README.md" "$REPO_BAD")" \
    "$REPO_BAD"

echo ""

# --------------------------------------------------------------------------
# Group 4: Error messages
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Group 4: Error Messages ---${T_NC}"

REPO_MSG=$(init_repo)
switch_branch "$REPO_MSG" "main"

# Block message contains "BRANCH PROTECTION"
run_test_with_stderr \
    "e2e_errmsg_contains_branch_protection" \
    2 \
    "$(json_edit "$REPO_MSG/src/app.py" "$REPO_MSG")" \
    "$REPO_MSG" \
    "BRANCH PROTECTION"

# Block message includes file path
run_test_with_stderr \
    "e2e_errmsg_includes_file_path" \
    2 \
    "$(json_edit "$REPO_MSG/src/app.py" "$REPO_MSG")" \
    "$REPO_MSG" \
    "src/app.py"

# Block message includes branch name
run_test_with_stderr \
    "e2e_errmsg_includes_branch_name" \
    2 \
    "$(json_edit "$REPO_MSG/src/app.py" "$REPO_MSG")" \
    "$REPO_MSG" \
    "main"

# Dev block message includes options/suggestions
switch_branch "$REPO_MSG" "dev"
run_test_with_stderr \
    "e2e_errmsg_dev_includes_options" \
    2 \
    "$(json_write "$REPO_MSG/src/new.py" "$REPO_MSG")" \
    "$REPO_MSG" \
    "worktree|unprotect|Options"

echo ""

# --------------------------------------------------------------------------
# Group 5: Cross-tool consistency
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Group 5: Cross-Tool Consistency ---${T_NC}"

REPO_CT=$(init_repo)

# Both Edit and Write blocked on main for same file
switch_branch "$REPO_CT" "main"

run_test \
    "e2e_cross_tool_edit_blocked_on_main" \
    2 \
    "$(json_edit "$REPO_CT/src/app.py" "$REPO_CT")" \
    "$REPO_CT"

run_test \
    "e2e_cross_tool_write_blocked_on_main" \
    2 \
    "$(json_write "$REPO_CT/src/app.py" "$REPO_CT")" \
    "$REPO_CT"

# On dev: Edit allowed (existing file) but Write new file blocked
switch_branch "$REPO_CT" "dev"

run_test \
    "e2e_cross_tool_edit_allowed_on_dev" \
    0 \
    "$(json_edit "$REPO_CT/src/app.py" "$REPO_CT")" \
    "$REPO_CT"

run_test \
    "e2e_cross_tool_write_new_blocked_on_dev" \
    2 \
    "$(json_write "$REPO_CT/src/brand_new.py" "$REPO_CT")" \
    "$REPO_CT"

echo ""

# --------------------------------------------------------------------------
# Group 6: Dry-run -> enforcement
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Group 6: Dry-Run -> Enforcement ---${T_NC}"

REPO_DR=$(init_repo)
switch_branch "$REPO_DR" "main"

# Step 1: Enable dry-run — action allowed but logged
mkdir -p "$REPO_DR/.claude"
touch "$REPO_DR/.claude/branch-guard-dryrun"

run_test_with_stderr \
    "e2e_dryrun_allows_with_log" \
    0 \
    "$(json_edit "$REPO_DR/src/app.py" "$REPO_DR")" \
    "$REPO_DR" \
    "DRY.RUN|would block"

# Step 2: Verify stderr contains [DRY-RUN] prefix
TOTAL=$((TOTAL + 1))
DR_STDERR=""
DR_EXIT=0
DR_STDERR=$(echo "$(json_edit "$REPO_DR/src/app.py" "$REPO_DR")" | (cd "$REPO_DR" && bash "$HOOK_SCRIPT") 2>&1 >/dev/null) || DR_EXIT=$?

if echo "$DR_STDERR" | grep -q '\[DRY-RUN\]'; then
    PASS=$((PASS + 1))
    echo -e "  ${T_GREEN}PASS${T_NC}  e2e_dryrun_stderr_has_prefix  ${T_BOLD}(found [DRY-RUN])${T_NC}"
else
    FAIL=$((FAIL + 1))
    FAILED_NAMES+=("e2e_dryrun_stderr_has_prefix")
    echo -e "  ${T_RED}FAIL${T_NC}  e2e_dryrun_stderr_has_prefix  ${T_BOLD}(missing [DRY-RUN] prefix)${T_NC}"
    echo -e "        stderr: $DR_STDERR"
fi

# Step 3: Remove dry-run -> blocks
rm -f "$REPO_DR/.claude/branch-guard-dryrun"

run_test \
    "e2e_dryrun_removed_blocks" \
    2 \
    "$(json_edit "$REPO_DR/src/app.py" "$REPO_DR")" \
    "$REPO_DR"

echo ""

# --------------------------------------------------------------------------
# Group 7: Performance dogfooding
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Group 7: Performance Dogfooding ---${T_NC}"

REPO_PERF=$(init_repo)
switch_branch "$REPO_PERF" "dev"

# Test: 50 invocations complete in < 5s (avg < 100ms each)
TOTAL=$((TOTAL + 1))
PERF_START=$(date +%s%N 2>/dev/null || python3 -c "import time; print(int(time.time()*1e9))")
PERF_JSON="$(json_write "$REPO_PERF/docs/note.md" "$REPO_PERF")"

for _ in $(seq 1 50); do
    echo "$PERF_JSON" | (cd "$REPO_PERF" && bash "$HOOK_SCRIPT") >/dev/null 2>&1 || true
done

PERF_END=$(date +%s%N 2>/dev/null || python3 -c "import time; print(int(time.time()*1e9))")
PERF_MS=$(( (PERF_END - PERF_START) / 1000000 ))

if [[ "$PERF_MS" -lt 5000 ]]; then
    PASS=$((PASS + 1))
    local_avg=$((PERF_MS / 50))
    echo -e "  ${T_GREEN}PASS${T_NC}  e2e_perf_50_invocations  ${T_BOLD}(${PERF_MS}ms total, ~${local_avg}ms avg)${T_NC}"
else
    FAIL=$((FAIL + 1))
    FAILED_NAMES+=("e2e_perf_50_invocations")
    echo -e "  ${T_RED}FAIL${T_NC}  e2e_perf_50_invocations  ${T_BOLD}(${PERF_MS}ms > 5000ms budget)${T_NC}"
fi

# Test: No temp files leaked after invocations
TOTAL=$((TOTAL + 1))
LEAKED_FILES=$(find "${TMPDIR:-/tmp}" -maxdepth 1 -name "branch-guard-*" -newer "$REPO_PERF/README.md" 2>/dev/null | grep -v "branch-guard-e2e" | wc -l | tr -d ' ')

if [[ "$LEAKED_FILES" -eq 0 ]]; then
    PASS=$((PASS + 1))
    echo -e "  ${T_GREEN}PASS${T_NC}  e2e_perf_no_temp_file_leak  ${T_BOLD}(0 leaked files)${T_NC}"
else
    FAIL=$((FAIL + 1))
    FAILED_NAMES+=("e2e_perf_no_temp_file_leak")
    echo -e "  ${T_RED}FAIL${T_NC}  e2e_perf_no_temp_file_leak  ${T_BOLD}($LEAKED_FILES leaked files)${T_NC}"
fi

# Test: No stderr on allow (clean pass-through)
ALLOW_JSON="$(json_write "$REPO_PERF/docs/note.md" "$REPO_PERF")"
run_test_without_stderr \
    "e2e_perf_no_stderr_on_allow" \
    0 \
    "$ALLOW_JSON" \
    "$REPO_PERF" \
    "BRANCH PROTECTION|ERROR|WARNING"

echo ""

# --------------------------------------------------------------------------
# Group 8: Real-world scenarios
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Group 8: Real-World Scenarios ---${T_NC}"

REPO_RW=$(init_repo)
switch_branch "$REPO_RW" "dev"

# Scenario 1: CLAUDE.md edit on dev (allowed — markdown)
run_test \
    "e2e_realworld_claudemd_edit_on_dev" \
    0 \
    "$(json_write "$REPO_RW/CLAUDE.md" "$REPO_RW")" \
    "$REPO_RW"

# Scenario 2: New utils/foo.py on dev (blocked — new code file)
run_test \
    "e2e_realworld_new_utils_py_on_dev" \
    2 \
    "$(json_write "$REPO_RW/utils/foo.py" "$REPO_RW")" \
    "$REPO_RW"

# Scenario 3: tests/test_new.py on dev (allowed — tests directory)
run_test \
    "e2e_realworld_test_file_on_dev" \
    0 \
    "$(json_write "$REPO_RW/tests/test_new.py" "$REPO_RW")" \
    "$REPO_RW"

# Scenario 4: .STATUS on dev (allowed — extension-less)
run_test \
    "e2e_realworld_status_file_on_dev" \
    0 \
    "$(json_write "$REPO_RW/.STATUS" "$REPO_RW")" \
    "$REPO_RW"

# Scenario 5: git push --force-with-lease on dev (blocked)
run_test \
    "e2e_realworld_force_push_with_lease_on_dev" \
    2 \
    "$(json_bash "git push --force-with-lease origin dev" "$REPO_RW")" \
    "$REPO_RW"

echo ""

# ============================================================================
# Summary
# ============================================================================

echo -e "${T_BOLD}===============================${T_NC}"
echo -e "${T_BOLD}  Branch Guard E2E Summary${T_NC}"
echo -e "${T_BOLD}===============================${T_NC}"
echo ""
echo -e "  Total:   ${T_BOLD}$TOTAL${T_NC}"
echo -e "  Passed:  ${T_GREEN}$PASS${T_NC}"
echo -e "  Failed:  ${T_RED}$FAIL${T_NC}"
echo -e "  Skipped: ${T_YELLOW}$SKIP${T_NC}"
echo ""

if [[ $FAIL -gt 0 ]]; then
    echo -e "${T_RED}Failed tests:${T_NC}"
    for name in "${FAILED_NAMES[@]}"; do
        echo -e "  ${T_RED}-${T_NC} $name"
    done
    echo ""
    echo -e "${T_RED}RESULT: FAIL${T_NC}"
    exit 1
else
    echo -e "${T_GREEN}RESULT: ALL TESTS PASSED${T_NC}"
    exit 0
fi
