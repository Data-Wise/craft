#!/usr/bin/env bash
#
# Test Suite for ~/.claude/hooks/branch-guard.sh
# Tests: Branch protection hook for Claude Code PreToolUse
#
# Usage:
#   ./tests/test_branch_guard.sh           # Run all tests
#   bash tests/test_branch_guard.sh        # Run all tests
#
# Approach:
#   - Creates a temporary git repo for each test group
#   - Pipes JSON to the hook script via stdin
#   - Checks exit code (0=allow, 2=block) and stderr output
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
# Helpers
# ============================================================================

# Create a temp directory and register it for cleanup
make_tmpdir() {
    local dir
    dir=$(mktemp -d "${TMPDIR:-/tmp}/branch-guard-test.XXXXXX")
    CLEANUP_DIRS+=("$dir")
    echo "$dir"
}

# Cleanup all temp directories
cleanup() {
    for dir in "${CLEANUP_DIRS[@]}"; do
        if [[ -d "$dir" ]]; then
            rm -rf "$dir"
        fi
    done
}
trap cleanup EXIT

# Initialize a git repo with main + dev branches and initial commit
# Usage: init_repo [--no-dev]
#   Returns the repo path via stdout
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

        # Initial commit so branches work
        mkdir -p src tests .claude
        echo "# README" > README.md
        git add -A
        git commit -m "Initial commit" --quiet

        if [[ "$no_dev" == false ]]; then
            git branch dev
        fi
    )

    echo "$repo"
}

# Switch branch in a repo
switch_branch() {
    local repo="$1"
    local branch="$2"
    (cd "$repo" && git checkout "$branch" --quiet 2>/dev/null)
}

# Create a branch and switch to it
create_and_switch() {
    local repo="$1"
    local branch="$2"
    (cd "$repo" && git checkout -b "$branch" --quiet 2>/dev/null)
}

# Build JSON for Edit tool
json_edit() {
    local file_path="$1"
    local cwd="$2"
    printf '{"tool_name":"Edit","tool_input":{"file_path":"%s","old_string":"x","new_string":"y"},"cwd":"%s"}' \
        "$file_path" "$cwd"
}

# Build JSON for Write tool
json_write() {
    local file_path="$1"
    local cwd="$2"
    printf '{"tool_name":"Write","tool_input":{"file_path":"%s","content":"# new content"},"cwd":"%s"}' \
        "$file_path" "$cwd"
}

# Build JSON for Bash tool
json_bash() {
    local command="$1"
    local cwd="$2"
    printf '{"tool_name":"Bash","tool_input":{"command":"%s"},"cwd":"%s"}' \
        "$command" "$cwd"
}

# Run the hook and check exit code
# Usage: run_test "test name" expected_exit json_string [cwd]
run_test() {
    local name="$1"
    local expected_exit="$2"
    local json="$3"
    local cwd="${4:-}"

    TOTAL=$((TOTAL + 1))

    # If cwd provided, run from there; otherwise use current dir
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

# Run the hook and also capture stderr for content checking
# Usage: run_test_with_stderr "test name" expected_exit json_string cwd expected_stderr_pattern
run_test_with_stderr() {
    local name="$1"
    local expected_exit="$2"
    local json="$3"
    local cwd="$4"
    local expected_pattern="$5"

    TOTAL=$((TOTAL + 1))

    local actual_exit=0
    local stderr_output=""
    stderr_output=$(echo "$json" | (cd "$cwd" && bash "$HOOK_SCRIPT") 2>&1 >/dev/null) || actual_exit=$?

    local exit_ok=false
    local pattern_ok=false

    [[ "$actual_exit" -eq "$expected_exit" ]] && exit_ok=true
    if echo "$stderr_output" | grep -qi "$expected_pattern" 2>/dev/null; then
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

skip() {
    local name="$1"
    local reason="${2:-Skipped}"
    TOTAL=$((TOTAL + 1))
    SKIP=$((SKIP + 1))
    echo -e "  ${T_YELLOW}SKIP${T_NC}  $name  ($reason)"
}

# ============================================================================
# Test Groups
# ============================================================================

echo ""
echo -e "${T_BOLD}Branch Guard Hook Tests${T_NC}"
echo -e "${T_BOLD}=======================${T_NC}"
echo -e "Hook: $HOOK_SCRIPT"
echo ""

# --------------------------------------------------------------------------
# Group 1: Main branch protection (block-all)
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Main Branch Protection (block-all) ---${T_NC}"

REPO=$(init_repo)
switch_branch "$REPO" "main"

# Test 1: Edit .py on main -> BLOCK
run_test \
    "test_edit_py_on_main" \
    2 \
    "$(json_edit "$REPO/src/app.py" "$REPO")" \
    "$REPO"

# Test 6: Edit .md on main -> BLOCK (block-all means ALL files)
run_test \
    "test_edit_md_on_main" \
    2 \
    "$(json_edit "$REPO/docs/README.md" "$REPO")" \
    "$REPO"

# Test 13: Bash git commit on main -> BLOCK
run_test \
    "test_bash_git_commit_on_main" \
    2 \
    "$(json_bash "git commit -m 'test'" "$REPO")" \
    "$REPO"

# Test 14: Bash git push on main -> BLOCK
run_test \
    "test_bash_git_push_on_main" \
    2 \
    "$(json_bash "git push origin main" "$REPO")" \
    "$REPO"

# Test 17: Bash non-git command on main -> ALLOW (only git-mutating blocked)
run_test \
    "test_bash_non_git_on_main" \
    0 \
    "$(json_bash "ls -la" "$REPO")" \
    "$REPO"

echo ""

# --------------------------------------------------------------------------
# Group 2: Dev branch protection (block-new-code)
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Dev Branch Protection (block-new-code) ---${T_NC}"

REPO_DEV=$(init_repo)
switch_branch "$REPO_DEV" "dev"

# Test 2: Edit existing .py on dev -> ALLOW (fixup)
# Create the file first so it exists
echo "print('hello')" > "$REPO_DEV/src/app.py"
(cd "$REPO_DEV" && git add src/app.py && git commit -m "Add app.py" --quiet)

run_test \
    "test_edit_py_on_dev_existing" \
    0 \
    "$(json_edit "$REPO_DEV/src/app.py" "$REPO_DEV")" \
    "$REPO_DEV"

# Test 3: Write new .py on dev (file doesn't exist) -> BLOCK
run_test \
    "test_write_new_py_on_dev" \
    2 \
    "$(json_write "$REPO_DEV/src/new_module.py" "$REPO_DEV")" \
    "$REPO_DEV"

# Test 4: Write new .md on dev -> ALLOW
run_test \
    "test_write_new_md_on_dev" \
    0 \
    "$(json_write "$REPO_DEV/docs/design.md" "$REPO_DEV")" \
    "$REPO_DEV"

# Test 7: Write .py in tests/ on dev -> ALLOW
run_test \
    "test_write_py_in_tests_on_dev" \
    0 \
    "$(json_write "$REPO_DEV/tests/test_something.py" "$REPO_DEV")" \
    "$REPO_DEV"

# Test 8: Write extension-less file on dev -> ALLOW
run_test \
    "test_write_extensionless_status_on_dev" \
    0 \
    "$(json_write "$REPO_DEV/.STATUS" "$REPO_DEV")" \
    "$REPO_DEV"

# Bonus: Also test Makefile (extension-less)
run_test \
    "test_write_extensionless_makefile_on_dev" \
    0 \
    "$(json_write "$REPO_DEV/Makefile" "$REPO_DEV")" \
    "$REPO_DEV"

# Test 19: Write to existing .py on dev (overwrite) -> ALLOW
echo "print('existing')" > "$REPO_DEV/src/existing.py"
(cd "$REPO_DEV" && git add src/existing.py && git commit -m "Add existing.py" --quiet)

run_test \
    "test_write_existing_py_on_dev" \
    0 \
    "$(json_write "$REPO_DEV/src/existing.py" "$REPO_DEV")" \
    "$REPO_DEV"

# Test 15: Bash git push --force on dev -> BLOCK
run_test \
    "test_bash_git_push_force_on_dev" \
    2 \
    "$(json_bash "git push --force" "$REPO_DEV")" \
    "$REPO_DEV"

# Test 16: Bash git merge on dev -> ALLOW
run_test \
    "test_bash_git_merge_on_dev" \
    0 \
    "$(json_bash "git merge feature/x" "$REPO_DEV")" \
    "$REPO_DEV"

# Bonus: Bash git commit on dev -> ALLOW (doc commits, merge commits)
run_test \
    "test_bash_git_commit_on_dev" \
    0 \
    "$(json_bash "git commit -m 'docs: update'" "$REPO_DEV")" \
    "$REPO_DEV"

# Bonus: Bash git push (no --force) on dev -> ALLOW
run_test \
    "test_bash_git_push_on_dev" \
    0 \
    "$(json_bash "git push origin dev" "$REPO_DEV")" \
    "$REPO_DEV"

echo ""

# --------------------------------------------------------------------------
# Group 3: Feature branch (no restrictions)
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Feature Branch (no restrictions) ---${T_NC}"

REPO_FEAT=$(init_repo)
create_and_switch "$REPO_FEAT" "feature/test"

# Test 5: Write new .py on feature/* -> ALLOW
run_test \
    "test_write_new_py_on_feature" \
    0 \
    "$(json_write "$REPO_FEAT/src/new_module.py" "$REPO_FEAT")" \
    "$REPO_FEAT"

# Bonus: Edit on feature -> ALLOW
run_test \
    "test_edit_py_on_feature" \
    0 \
    "$(json_edit "$REPO_FEAT/src/app.py" "$REPO_FEAT")" \
    "$REPO_FEAT"

# Bonus: Bash git commit on feature -> ALLOW
run_test \
    "test_bash_git_commit_on_feature" \
    0 \
    "$(json_bash "git commit -m 'feat: add feature'" "$REPO_FEAT")" \
    "$REPO_FEAT"

# Bonus: Bash git push --force on feature -> ALLOW (force push OK on feature branches)
run_test \
    "test_bash_git_push_force_on_feature" \
    0 \
    "$(json_bash "git push --force origin feature/test" "$REPO_FEAT")" \
    "$REPO_FEAT"

echo ""

# --------------------------------------------------------------------------
# Group 4: Bypass mechanisms
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Bypass Mechanisms ---${T_NC}"

# Test 9: Bypass marker active on dev -> ALLOW
REPO_BYPASS=$(init_repo)
switch_branch "$REPO_BYPASS" "dev"
mkdir -p "$REPO_BYPASS/.claude"
echo '{"reason":"test","timestamp":"2026-02-06T00:00:00Z"}' > "$REPO_BYPASS/.claude/allow-dev-edit"

run_test \
    "test_bypass_marker_active" \
    0 \
    "$(json_write "$REPO_BYPASS/src/new_code.py" "$REPO_BYPASS")" \
    "$REPO_BYPASS"

# Clean up bypass marker and verify block resumes
rm -f "$REPO_BYPASS/.claude/allow-dev-edit"

run_test \
    "test_bypass_marker_removed_blocks_again" \
    2 \
    "$(json_write "$REPO_BYPASS/src/new_code.py" "$REPO_BYPASS")" \
    "$REPO_BYPASS"

echo ""

# --------------------------------------------------------------------------
# Group 5: Dry-run mode
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Dry-Run Mode ---${T_NC}"

# Test 18: Dry-run mode logs but doesn't block
REPO_DRY=$(init_repo)
switch_branch "$REPO_DRY" "main"
mkdir -p "$REPO_DRY/.claude"
touch "$REPO_DRY/.claude/branch-guard-dryrun"

# In dry-run, action that would be blocked should exit 0 but log
run_test_with_stderr \
    "test_dryrun_mode_allows_with_log" \
    0 \
    "$(json_edit "$REPO_DRY/src/app.py" "$REPO_DRY")" \
    "$REPO_DRY" \
    "dry.run\|DRYRUN\|dryrun\|DRY.RUN\|would block\|would have blocked"

# Remove dry-run marker, verify it blocks again
rm -f "$REPO_DRY/.claude/branch-guard-dryrun"

run_test \
    "test_dryrun_removed_blocks_again" \
    2 \
    "$(json_edit "$REPO_DRY/src/app.py" "$REPO_DRY")" \
    "$REPO_DRY"

echo ""

# --------------------------------------------------------------------------
# Group 6: Edge cases
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Edge Cases ---${T_NC}"

# Test 10: No git repo (non-git directory) -> ALLOW (graceful fallthrough)
NON_GIT_DIR=$(make_tmpdir)

run_test \
    "test_no_git_repo" \
    0 \
    "$(json_edit "$NON_GIT_DIR/src/app.py" "$NON_GIT_DIR")" \
    "$NON_GIT_DIR"

# Test 11: Repo with only main, no dev branch -> only protect main
REPO_NODEV=$(init_repo --no-dev)
switch_branch "$REPO_NODEV" "main"

# Edit on main (no dev) -> still BLOCK (main is always protected)
run_test \
    "test_no_dev_branch_main_still_blocked" \
    2 \
    "$(json_edit "$REPO_NODEV/src/app.py" "$REPO_NODEV")" \
    "$REPO_NODEV"

# Create a non-main, non-dev branch in the no-dev repo -> ALLOW
create_and_switch "$REPO_NODEV" "working"

run_test \
    "test_no_dev_branch_other_branch_allowed" \
    0 \
    "$(json_write "$REPO_NODEV/src/new.py" "$REPO_NODEV")" \
    "$REPO_NODEV"

echo ""

# --------------------------------------------------------------------------
# Group 7: Custom branch-guard.json
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Custom branch-guard.json ---${T_NC}"

# Test 12: Custom config with production=block-all
REPO_CUSTOM=$(init_repo)
create_and_switch "$REPO_CUSTOM" "production"

mkdir -p "$REPO_CUSTOM/.claude"
cat > "$REPO_CUSTOM/.claude/branch-guard.json" <<'JSONEOF'
{
  "production": "block-all"
}
JSONEOF

run_test \
    "test_custom_branch_guard_json_production_blocked" \
    2 \
    "$(json_edit "$REPO_CUSTOM/src/app.py" "$REPO_CUSTOM")" \
    "$REPO_CUSTOM"

# Verify non-listed branch in custom config -> ALLOW
create_and_switch "$REPO_CUSTOM" "staging"

run_test \
    "test_custom_branch_guard_json_unlisted_allowed" \
    0 \
    "$(json_edit "$REPO_CUSTOM/src/app.py" "$REPO_CUSTOM")" \
    "$REPO_CUSTOM"

# Custom config with draft=block-new-code (teaching project style)
REPO_TEACH=$(init_repo)
create_and_switch "$REPO_TEACH" "draft"

mkdir -p "$REPO_TEACH/.claude"
cat > "$REPO_TEACH/.claude/branch-guard.json" <<'JSONEOF'
{
  "production": "block-all",
  "draft": "block-new-code"
}
JSONEOF

# New .py on draft -> BLOCK
run_test \
    "test_custom_draft_new_code_blocked" \
    2 \
    "$(json_write "$REPO_TEACH/src/new_module.py" "$REPO_TEACH")" \
    "$REPO_TEACH"

# .md on draft -> ALLOW
run_test \
    "test_custom_draft_md_allowed" \
    0 \
    "$(json_write "$REPO_TEACH/docs/notes.md" "$REPO_TEACH")" \
    "$REPO_TEACH"

# Existing .py on draft -> ALLOW (fixup)
echo "print('hello')" > "$REPO_TEACH/src/existing.py"
(cd "$REPO_TEACH" && git add src/existing.py && git commit -m "Add file" --quiet)

run_test \
    "test_custom_draft_existing_py_allowed" \
    0 \
    "$(json_edit "$REPO_TEACH/src/existing.py" "$REPO_TEACH")" \
    "$REPO_TEACH"

echo ""

# --------------------------------------------------------------------------
# Group 8: Bash command edge cases
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Bash Command Edge Cases ---${T_NC}"

REPO_BASH=$(init_repo)

# git push --force-with-lease on dev -> should also be blocked
switch_branch "$REPO_BASH" "dev"

run_test \
    "test_bash_git_push_force_with_lease_on_dev" \
    2 \
    "$(json_bash "git push --force-with-lease origin dev" "$REPO_BASH")" \
    "$REPO_BASH"

# git reset --hard on main -> BLOCK
switch_branch "$REPO_BASH" "main"

run_test \
    "test_bash_git_reset_hard_on_main" \
    2 \
    "$(json_bash "git reset --hard HEAD~1" "$REPO_BASH")" \
    "$REPO_BASH"

# Piped command with git commit on main -> BLOCK
run_test \
    "test_bash_piped_git_commit_on_main" \
    2 \
    "$(json_bash "echo test && git commit -m 'sneak'" "$REPO_BASH")" \
    "$REPO_BASH"

# Non-git bash on dev -> ALLOW
switch_branch "$REPO_BASH" "dev"

run_test \
    "test_bash_python_command_on_dev" \
    0 \
    "$(json_bash "python3 -c 'print(1)'" "$REPO_BASH")" \
    "$REPO_BASH"

echo ""

# --------------------------------------------------------------------------
# Group 9: File extension coverage
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- File Extension Coverage ---${T_NC}"

REPO_EXT=$(init_repo)
switch_branch "$REPO_EXT" "dev"

# New .sh on dev -> BLOCK
run_test \
    "test_write_new_sh_on_dev" \
    2 \
    "$(json_write "$REPO_EXT/scripts/deploy.sh" "$REPO_EXT")" \
    "$REPO_EXT"

# New .js on dev -> BLOCK
run_test \
    "test_write_new_js_on_dev" \
    2 \
    "$(json_write "$REPO_EXT/src/index.js" "$REPO_EXT")" \
    "$REPO_EXT"

# New .yml on dev -> BLOCK (config-as-code)
run_test \
    "test_write_new_yml_on_dev" \
    2 \
    "$(json_write "$REPO_EXT/config/app.yml" "$REPO_EXT")" \
    "$REPO_EXT"

# New .json on dev -> BLOCK
run_test \
    "test_write_new_json_on_dev" \
    2 \
    "$(json_write "$REPO_EXT/package.json" "$REPO_EXT")" \
    "$REPO_EXT"

# New Dockerfile (extension-less) on dev -> ALLOW
run_test \
    "test_write_dockerfile_on_dev" \
    0 \
    "$(json_write "$REPO_EXT/Dockerfile" "$REPO_EXT")" \
    "$REPO_EXT"

# New .txt on dev -> ALLOW (not in code extensions list)
run_test \
    "test_write_txt_on_dev" \
    0 \
    "$(json_write "$REPO_EXT/notes.txt" "$REPO_EXT")" \
    "$REPO_EXT"

echo ""

# --------------------------------------------------------------------------
# Group 10: Edge cases — path traversal, symlinks, special branch names,
#            malformed config warning, git -C invocations
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Advanced Edge Cases ---${T_NC}"

REPO_ADV=$(init_repo)

# Path traversal with ".." — writing ../../../etc/foo.py from dev
# The resolved path doesn't exist -> new code file -> BLOCK
switch_branch "$REPO_ADV" "dev"

run_test \
    "test_path_traversal_new_file_blocked" \
    2 \
    "$(json_write "$REPO_ADV/../nonexistent/evil.py" "$REPO_ADV")" \
    "$REPO_ADV"

# Symlink: Create a symlink to an existing file (absolute target), then "write" to it
# The symlink target exists -> -f follows symlinks -> treated as existing file -> ALLOW
(cd "$REPO_ADV" && ln -sf "$REPO_ADV/README.md" src/link-to-readme.py 2>/dev/null)

run_test \
    "test_symlink_to_existing_file_allowed" \
    0 \
    "$(json_write "$REPO_ADV/src/link-to-readme.py" "$REPO_ADV")" \
    "$REPO_ADV"

# Branch name with special regex chars (e.g., "release/v2.0")
# Custom config with that branch name -> should match via jq
mkdir -p "$REPO_ADV/.claude"
cat > "$REPO_ADV/.claude/branch-guard.json" <<'JSONEOF'
{
  "release/v2.0": "block-all",
  "dev": "block-new-code"
}
JSONEOF

create_and_switch "$REPO_ADV" "release/v2.0"

run_test \
    "test_special_branch_name_slash_dot" \
    2 \
    "$(json_edit "$REPO_ADV/README.md" "$REPO_ADV")" \
    "$REPO_ADV"

# Clean up custom config for remaining tests
rm -f "$REPO_ADV/.claude/branch-guard.json"
switch_branch "$REPO_ADV" "dev"

# git -C <path> commit on main — current pattern doesn't catch this
# because grep expects "git<space>commit" but sees "git -C ... commit"
# This is a known limitation — documenting the behavior
REPO_GIT_C=$(init_repo)
switch_branch "$REPO_GIT_C" "main"

run_test \
    "test_bash_git_dash_c_commit_on_main_not_caught" \
    0 \
    "$(json_bash "git -C /some/path commit -m test" "$REPO_GIT_C")" \
    "$REPO_GIT_C"

# Malformed config: should log a WARNING to stderr and fall through to auto-detect
REPO_WARN=$(init_repo)
mkdir -p "$REPO_WARN/.claude"
echo "not valid json {{" > "$REPO_WARN/.claude/branch-guard.json"
switch_branch "$REPO_WARN" "main"

run_test_with_stderr \
    "test_malformed_config_warns_on_stderr" \
    2 \
    "$(json_edit "$REPO_WARN/README.md" "$REPO_WARN")" \
    "$REPO_WARN" \
    "WARNING.*Invalid JSON"

# Write to .STATUS (dot-prefixed extension-less) on dev -> ALLOW
REPO_DOT=$(init_repo)
switch_branch "$REPO_DOT" "dev"

run_test \
    "test_write_dot_status_file_on_dev" \
    0 \
    "$(json_write "$REPO_DOT/.STATUS" "$REPO_DOT")" \
    "$REPO_DOT"

# Write new .R file on dev -> BLOCK (R is in code extensions)
run_test \
    "test_write_new_r_file_on_dev" \
    2 \
    "$(json_write "$REPO_DOT/analysis.R" "$REPO_DOT")" \
    "$REPO_DOT"

echo ""

# --------------------------------------------------------------------------
# Group 11: Smart mode — destructive commands on dev (v2.17.0)
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Destructive Commands on Dev (Smart Mode) ---${T_NC}"

REPO_DESTR=$(init_repo)
switch_branch "$REPO_DESTR" "dev"

run_test \
    "test_git_reset_hard_on_dev" \
    2 \
    "$(json_bash "git reset --hard HEAD" "$REPO_DESTR")" \
    "$REPO_DESTR"

run_test \
    "test_git_checkout_discard_on_dev" \
    2 \
    "$(json_bash "git checkout -- ." "$REPO_DESTR")" \
    "$REPO_DESTR"

run_test \
    "test_git_restore_discard_on_dev" \
    2 \
    "$(json_bash "git restore ." "$REPO_DESTR")" \
    "$REPO_DESTR"

# git restore --staged is safe (only unstages) -> ALLOW
run_test \
    "test_git_restore_staged_allowed" \
    0 \
    "$(json_bash "git restore --staged file.py" "$REPO_DESTR")" \
    "$REPO_DESTR"

run_test \
    "test_git_clean_fd_on_dev" \
    2 \
    "$(json_bash "git clean -fd" "$REPO_DESTR")" \
    "$REPO_DESTR"

run_test \
    "test_git_clean_fx_on_dev" \
    2 \
    "$(json_bash "git clean -fx" "$REPO_DESTR")" \
    "$REPO_DESTR"

run_test \
    "test_git_clean_force_flag_on_dev" \
    2 \
    "$(json_bash "git clean --force" "$REPO_DESTR")" \
    "$REPO_DESTR"

echo ""

# --------------------------------------------------------------------------
# Group 12: Universal catastrophic checks — all branches (v2.17.0)
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Universal Catastrophic Checks ---${T_NC}"

# git branch -D on dev -> BLOCK (MEDIUM, universal)
run_test \
    "test_git_branch_delete_force_on_dev" \
    2 \
    "$(json_bash "git branch -D old-branch" "$REPO_DESTR")" \
    "$REPO_DESTR"

# git branch -D on feature -> BLOCK (universal)
create_and_switch "$REPO_DESTR" "feature/test-univ"

run_test \
    "test_git_branch_delete_force_on_feature" \
    2 \
    "$(json_bash "git branch -D some-branch" "$REPO_DESTR")" \
    "$REPO_DESTR"

# git branch -d (safe delete) -> ALLOW on feature
run_test \
    "test_git_branch_delete_safe_allowed" \
    0 \
    "$(json_bash "git branch -d merged-branch" "$REPO_DESTR")" \
    "$REPO_DESTR"

echo ""

# --------------------------------------------------------------------------
# Group 13: Critical file protection on dev (v2.17.0)
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Critical File Protection ---${T_NC}"

REPO_CRIT=$(init_repo)
switch_branch "$REPO_CRIT" "dev"

# .env write -> BLOCK
run_test \
    "test_write_env_on_dev" \
    2 \
    "$(json_write "$REPO_CRIT/.env" "$REPO_CRIT")" \
    "$REPO_CRIT"

# .env.local write -> BLOCK
run_test \
    "test_write_env_local_on_dev" \
    2 \
    "$(json_write "$REPO_CRIT/.env.local" "$REPO_CRIT")" \
    "$REPO_CRIT"

# .pem edit -> BLOCK
run_test \
    "test_edit_pem_on_dev" \
    2 \
    "$(json_edit "$REPO_CRIT/cert.pem" "$REPO_CRIT")" \
    "$REPO_CRIT"

# .key edit -> BLOCK
run_test \
    "test_edit_key_on_dev" \
    2 \
    "$(json_edit "$REPO_CRIT/server.key" "$REPO_CRIT")" \
    "$REPO_CRIT"

# .secret write -> BLOCK
run_test \
    "test_write_secret_on_dev" \
    2 \
    "$(json_write "$REPO_CRIT/data.secret" "$REPO_CRIT")" \
    "$REPO_CRIT"

# branch-guard.json write -> BLOCK
run_test \
    "test_write_guard_json_on_dev" \
    2 \
    "$(json_write "$REPO_CRIT/.claude/branch-guard.json" "$REPO_CRIT")" \
    "$REPO_CRIT"

# branch-guard.json edit -> BLOCK
run_test \
    "test_edit_guard_json_on_dev" \
    2 \
    "$(json_edit ".claude/branch-guard.json" "$REPO_CRIT")" \
    "$REPO_CRIT"

# Normal file edit still allowed
run_test \
    "test_edit_normal_file_on_dev" \
    0 \
    "$(json_edit "$REPO_CRIT/README.md" "$REPO_CRIT")" \
    "$REPO_CRIT"

echo ""

# --------------------------------------------------------------------------
# Group 14: Bash write-through detection on dev (v2.17.0)
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Bash Write-Through Detection ---${T_NC}"

REPO_WT=$(init_repo)
switch_branch "$REPO_WT" "dev"

# echo > new.py -> BLOCK
run_test \
    "test_bash_redirect_new_py" \
    2 \
    "$(json_bash "echo 'print(1)' > new_file.py" "$REPO_WT")" \
    "$REPO_WT"

# cat > new.sh -> BLOCK
run_test \
    "test_bash_redirect_new_sh" \
    2 \
    "$(json_bash "cat > script.sh" "$REPO_WT")" \
    "$REPO_WT"

# tee new.py -> BLOCK
run_test \
    "test_bash_tee_new_py" \
    2 \
    "$(json_bash "echo x | tee new.py" "$REPO_WT")" \
    "$REPO_WT"

# cp to new.py -> BLOCK
run_test \
    "test_bash_cp_new_py" \
    2 \
    "$(json_bash "cp template.py brand_new.py" "$REPO_WT")" \
    "$REPO_WT"

# echo > notes.md -> ALLOW (markdown)
run_test \
    "test_bash_redirect_md_allowed" \
    0 \
    "$(json_bash "echo hi > notes.md" "$REPO_WT")" \
    "$REPO_WT"

# Redirect to existing file -> ALLOW (overwrite)
echo "existing" > "$REPO_WT/existing.py"
(cd "$REPO_WT" && git add existing.py && git commit -m "add" --quiet)

run_test \
    "test_bash_redirect_existing_allowed" \
    0 \
    "$(json_bash "echo updated > existing.py" "$REPO_WT")" \
    "$REPO_WT"

# Variable in path -> ALLOW (gracefully skip)
run_test \
    "test_bash_redirect_variable_path_allowed" \
    0 \
    '{"tool_name":"Bash","tool_input":{"command":"echo x > $OUTPUT_FILE"},"cwd":"'"$REPO_WT"'"}' \
    "$REPO_WT"

# Write-through on feature branch -> ALLOW (no protection)
create_and_switch "$REPO_WT" "feature/wt-test"

run_test \
    "test_bash_redirect_feature_allowed" \
    0 \
    "$(json_bash "echo x > brand_new.py" "$REPO_WT")" \
    "$REPO_WT"

echo ""

# --------------------------------------------------------------------------
# Group 15: One-shot marker + Session counter (v2.17.0)
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- One-Shot Marker + Session Counter ---${T_NC}"

REPO_ONCE=$(init_repo)
switch_branch "$REPO_ONCE" "dev"

# Without one-shot marker -> BLOCK (new code on dev)
run_test \
    "test_oneshot_without_marker_blocked" \
    2 \
    "$(json_write "$REPO_ONCE/src/app.py" "$REPO_ONCE")" \
    "$REPO_ONCE"

# Create one-shot marker -> ALLOW
mkdir -p "$REPO_ONCE/.claude"
touch "$REPO_ONCE/.claude/allow-once"

run_test \
    "test_oneshot_with_marker_allowed" \
    0 \
    "$(json_write "$REPO_ONCE/src/app.py" "$REPO_ONCE")" \
    "$REPO_ONCE"

# Marker consumed -> BLOCK again
run_test \
    "test_oneshot_marker_consumed" \
    2 \
    "$(json_write "$REPO_ONCE/src/app.py" "$REPO_ONCE")" \
    "$REPO_ONCE"

# Verify marker file is gone
if [[ ! -f "$REPO_ONCE/.claude/allow-once" ]]; then
    TOTAL=$((TOTAL + 1)); PASS=$((PASS + 1))
    echo -e "  ${T_GREEN}PASS${T_NC}  test_oneshot_marker_file_deleted  ${T_BOLD}(file removed)${T_NC}"
else
    TOTAL=$((TOTAL + 1)); FAIL=$((FAIL + 1))
    FAILED_NAMES+=("test_oneshot_marker_file_deleted")
    echo -e "  ${T_RED}FAIL${T_NC}  test_oneshot_marker_file_deleted  ${T_BOLD}(file still exists)${T_NC}"
fi

# Session counter: verify file created after confirm
if [[ -f "$REPO_ONCE/.claude/guard-session-counts" ]]; then
    TOTAL=$((TOTAL + 1)); PASS=$((PASS + 1))
    echo -e "  ${T_GREEN}PASS${T_NC}  test_session_counter_file_created  ${T_BOLD}(file exists)${T_NC}"
else
    TOTAL=$((TOTAL + 1)); FAIL=$((FAIL + 1))
    FAILED_NAMES+=("test_session_counter_file_created")
    echo -e "  ${T_RED}FAIL${T_NC}  test_session_counter_file_created  ${T_BOLD}(file missing)${T_NC}"
fi

echo ""

# --------------------------------------------------------------------------
# Group 16: Verbosity fade (v2.17.0)
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Verbosity Fade ---${T_NC}"

REPO_VERB=$(init_repo)
switch_branch "$REPO_VERB" "dev"

# 1st encounter — full verbosity (should contain "Safe alternatives" or "Why risky")
run_test_with_stderr \
    "test_verbosity_full_first_encounter" \
    2 \
    "$(json_write "$REPO_VERB/src/new1.py" "$REPO_VERB")" \
    "$REPO_VERB" \
    "Safe alternatives\|Why risky\|risky"

# 2nd encounter — brief (should contain BRANCH GUARD but shorter)
run_test_with_stderr \
    "test_verbosity_brief_second_encounter" \
    2 \
    "$(json_write "$REPO_VERB/src/new2.py" "$REPO_VERB")" \
    "$REPO_VERB" \
    "BRANCH GUARD\|CONFIRM"

# 4th+ encounter — minimal (should be just [CONFIRM] one-liner)
# Need 3rd encounter first
run_test \
    "test_verbosity_third_encounter" \
    2 \
    "$(json_write "$REPO_VERB/src/new3.py" "$REPO_VERB")" \
    "$REPO_VERB"

run_test_with_stderr \
    "test_verbosity_minimal_fourth_encounter" \
    2 \
    "$(json_write "$REPO_VERB/src/new4.py" "$REPO_VERB")" \
    "$REPO_VERB" \
    "CONFIRM.*Allow"

echo ""

# ============================================================================
# Summary
# ============================================================================

echo -e "${T_BOLD}===============================${T_NC}"
echo -e "${T_BOLD}  Branch Guard Test Summary${T_NC}"
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
