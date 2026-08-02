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
#
# IMPORTANT: this suite exercises the INSTALLED hook at $HOME/.claude/hooks/,
# NOT the repo copy at scripts/branch-guard.sh. If you edited scripts/branch-guard.sh,
# reinstall first or you will be testing a stale hook:
#   bash scripts/install-branch-guard.sh
# (CI does exactly this before running — see .github/workflows/ci.yml.)

# Note: Not using 'set -e' because we want tests to continue after failures
set -uo pipefail

# ============================================================================
# Configuration
# ============================================================================

# Defaults to the INSTALLED hook (CI installs the PR hook first); override with
# HOOK_SCRIPT=<abs path>/scripts/branch-guard.sh to test the repo copy directly.
HOOK_SCRIPT="${HOOK_SCRIPT:-$HOME/.claude/hooks/branch-guard.sh}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ~/.claude/hooks/branch-guard.sh is a shared install target: cc-config also
# ships a branch-guard.sh and symlinks it there, and deliberately relaxed the
# new-code-on-protected-branch tier from MEDIUM to LOW on 2026-07-28. When that
# is what is installed, this suite would assert craft's expectations against
# another repo's artifact and report a craft failure for a cc-config policy
# decision. Fall back to craft's own copy so a local run still exercises craft's
# logic. CI is unaffected: it runs install-guards.sh first, so the installed
# hook there IS this repo's copy and the integration path is still covered.
if [[ -z "${HOOK_SCRIPT_EXPLICIT:-}" && -L "$HOOK_SCRIPT" ]]; then
    _installed_target="$(cd "$(dirname "$(readlink "$HOOK_SCRIPT")")" 2>/dev/null && pwd)/$(basename "$(readlink "$HOOK_SCRIPT")")"
    _repo_root="$(cd "$SCRIPT_DIR/.." && pwd)"
    if [[ "$_installed_target" != "$_repo_root"/* ]]; then
        echo "NOTE: installed hook is owned by another repo ($_installed_target)"
        echo "      falling back to this repo's scripts/branch-guard.sh"
        echo ""
        HOOK_SCRIPT="$_repo_root/scripts/branch-guard.sh"
    fi
fi

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
# Group 2b: Research integration branch 'draft' (treated exactly like 'dev')
# Research repos (~/projects/research/*) use 'draft' as the integration branch.
# Config: main + draft, NO dev — draft must get the same smart-mode protection.
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Draft Branch Protection (research; same as dev) ---${T_NC}"

REPO_DRAFT=$(init_repo --no-dev)
(cd "$REPO_DRAFT" && git branch draft)
switch_branch "$REPO_DRAFT" "draft"

# Edit existing code on draft -> ALLOW (fixup), mirrors dev Test 2
echo "print('hello')" > "$REPO_DRAFT/src/app.py"
(cd "$REPO_DRAFT" && git add src/app.py && git commit -m "Add app.py" --quiet)
run_test \
    "test_edit_py_on_draft_existing" \
    0 \
    "$(json_edit "$REPO_DRAFT/src/app.py" "$REPO_DRAFT")" \
    "$REPO_DRAFT"

# Write NEW code file on draft -> BLOCK, mirrors dev Test 3
run_test \
    "test_write_new_py_on_draft" \
    2 \
    "$(json_write "$REPO_DRAFT/src/new_module.py" "$REPO_DRAFT")" \
    "$REPO_DRAFT"

# Write new .md on draft -> ALLOW, mirrors dev Test 4
run_test \
    "test_write_new_md_on_draft" \
    0 \
    "$(json_write "$REPO_DRAFT/docs/design.md" "$REPO_DRAFT")" \
    "$REPO_DRAFT"

# Bash git push --force on draft -> BLOCK, mirrors dev Test 15
run_test \
    "test_bash_git_push_force_on_draft" \
    2 \
    "$(json_bash "git push --force" "$REPO_DRAFT")" \
    "$REPO_DRAFT"

# Bash normal commit on draft -> ALLOW, mirrors dev Test 18
run_test \
    "test_bash_git_commit_on_draft" \
    0 \
    "$(json_bash "git commit -m 'docs: update'" "$REPO_DRAFT")" \
    "$REPO_DRAFT"

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

# git reset --hard on main -> CONFIRM (ask, exits 2 in non-interactive mode)
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

# Path traversal with ".." — writing ../nonexistent/evil.py from dev
# After canonicalization the path resolves OUTSIDE the repo. Per the
# documented "non-repo paths are always allowed" semantic (memory files,
# /tmp, etc.), traversal that lands outside the repo is allowed — branch
# protection only enforces against the protected branch's own tree.
# (Earlier behavior here was accidental: pre-canonicalization, the un-
# resolved path stayed inside the repo and got the new-code block. That
# was a leak: it allowed writes that DID resolve outside via cd canonical-
# ization to escape protection, and blocked writes that didn't.)
switch_branch "$REPO_ADV" "dev"

run_test \
    "test_path_traversal_resolves_outside_repo_allowed" \
    0 \
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

# git -C <path> commit on main — FIXED 2026-07-14 (GRILL-branch-guard-
# target-resolution). Was previously NOT caught: the classification regex
# expected "git<space>commit" but saw "git -C ... commit". The regex now
# tolerates an optional -C flag. /some/path doesn't exist on disk, so the
# 8d0 cross-context resolver can't resolve a real target and falls back to
# the session's own branch (main, block-all) — the safe conservative
# default when a -C target can't be verified. Still blocks, as it always
# should have for an unresolvable target on a protected branch.
REPO_GIT_C=$(init_repo)
switch_branch "$REPO_GIT_C" "main"

run_test \
    "test_bash_git_dash_c_commit_on_main_now_caught" \
    2 \
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
    0 \
    "$(json_bash "git checkout -- ." "$REPO_DESTR")" \
    "$REPO_DESTR"
    # now allowed by branch-guard — no-switch-guard owns checkout-discard (ask)

run_test \
    "test_git_restore_discard_on_dev" \
    0 \
    "$(json_bash "git restore ." "$REPO_DESTR")" \
    "$REPO_DESTR"
    # now allowed by branch-guard — no-switch-guard owns restore-discard (ask)

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
# Group 12b: Registry cannot bypass catastrophic ops (v2.40.0 — review #1)
# Disabling/muting branch-guard must NOT bypass rm -rf .git or git branch -D.
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Registry: catastrophic ops stay gated ---${T_NC}"

# run_test_home: like run_test but with a custom HOME so the guard reads a fake
# guards.json instead of the real ~/.claude/guards.json (never touches it).
run_test_home() {
    local name="$1" expected_exit="$2" json="$3" cwd="$4" home="$5"
    TOTAL=$((TOTAL + 1))
    local actual_exit=0
    echo "$json" | (cd "$cwd" && HOME="$home" bash "$HOOK_SCRIPT") >/dev/null 2>&1 || actual_exit=$?
    if [[ "$actual_exit" -eq "$expected_exit" ]]; then
        PASS=$((PASS + 1)); echo -e "  ${T_GREEN}PASS${T_NC}  $name  ${T_BOLD}(exit=$actual_exit)${T_NC}"
    else
        FAIL=$((FAIL + 1)); FAILED_NAMES+=("$name")
        echo -e "  ${T_RED}FAIL${T_NC}  $name  ${T_BOLD}(expected=$expected_exit, got=$actual_exit)${T_NC}"
    fi
}

REPO_CAT=$(init_repo)
FAKE_HOME_OFF=$(make_tmpdir); mkdir -p "$FAKE_HOME_OFF/.claude"
printf '{"guards":{"branch-guard":{"enabled":false}}}\n' > "$FAKE_HOME_OFF/.claude/guards.json"

# rm -rf .git with branch-guard DISABLED -> STILL gated (catastrophic, non-muteable)
run_test_home "test_rm_rf_git_gated_even_when_disabled" 2 \
    "$(json_bash "rm -rf .git" "$REPO_CAT")" "$REPO_CAT" "$FAKE_HOME_OFF"

# git branch -D with branch-guard DISABLED -> STILL gated (catastrophic)
run_test_home "test_branch_D_gated_even_when_disabled" 2 \
    "$(json_bash "git branch -D x" "$REPO_CAT")" "$REPO_CAT" "$FAKE_HOME_OFF"

# Sanity: a NON-catastrophic op (reset --hard) IS bypassed when disabled -> exit 0
run_test_home "test_reset_hard_bypassed_when_disabled" 0 \
    "$(json_bash "git reset --hard HEAD" "$REPO_CAT")" "$REPO_CAT" "$FAKE_HOME_OFF"

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
# Group 14b: stderr-redirect false-crash regression (2026-07-09)
#
# "cat file 2>&1" passes the coarse '>' guard (grep -qE '>[[:space:]]*[^>]'
# — '&' satisfies "any non-'>' char") but the fine extraction pattern
# (grep -oE '>[[:space:]]*[^>|&;[:space:]]+') explicitly excludes '&', so
# it matches nothing. Under this script's `set -euo pipefail`, a bare
# VAR=$(pipeline) assignment where the pipeline's last non-zero exit is
# grep's "no match" (exit 1) kills the whole hook — silently, no stderr,
# exit 1 instead of the normal 0 (allow) or 2 (block/confirm). Any command
# containing 2>&1, 1>&2, etc. triggered this. Fixed by appending `|| true`
# to each of the four BASH_TARGET extraction pipelines so a real no-match
# behaves like the empty-string fallback the `[[ -z "$BASH_TARGET" ]]`
# checks already handle, instead of crashing.
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Stderr-Redirect False-Crash Regression ---${T_NC}"

REPO_SR=$(init_repo)
switch_branch "$REPO_SR" "dev"

# The exact crash trigger: fine-extraction zero-match under set -e/pipefail.
run_test \
    "test_bash_stderr_redirect_2to1_no_crash" \
    0 \
    "$(json_bash "cat README.md 2>&1 | head -5" "$REPO_SR")" \
    "$REPO_SR"

# Same failure mode, different redirect direction.
run_test \
    "test_bash_stderr_redirect_1to2_no_crash" \
    0 \
    "$(json_bash "echo err 1>&2" "$REPO_SR")" \
    "$REPO_SR"

# /dev/null already had explicit handling (BASH_TARGET == /dev/* -> "") —
# confirm it still works alongside the || true change.
run_test \
    "test_bash_stderr_redirect_devnull_allowed" \
    0 \
    "$(json_bash "ls nonexistent 2>/dev/null" "$REPO_SR")" \
    "$REPO_SR"

# A real write-through target MUST still be caught even when the same
# command also contains a 2>&1 that would otherwise zero-match — the fix
# must not weaken detection, only stop the crash.
run_test \
    "test_bash_stderr_redirect_plus_real_writethrough_still_blocked" \
    2 \
    "$(json_bash "echo x > new_file.py 2>&1" "$REPO_SR")" \
    "$REPO_SR"

# tee/cp/touch edge cases where the coarse guard matches but the fine
# extraction can plausibly zero-match — must not crash either.
run_test \
    "test_bash_tee_no_target_no_crash" \
    0 \
    "$(json_bash "echo x | tee" "$REPO_SR")" \
    "$REPO_SR"

echo ""

# --------------------------------------------------------------------------
# Group 14c: heredoc-prose false-positive regression (2026-07-10)
#
# HAS_HEREDOC was only wired to Pattern 1 (redirect). grep is line-oriented,
# so a heredoc body (e.g. a `git commit -m "$(cat <<'EOF' ... EOF)"` message)
# containing a prose line that happens to start with "touch "/"tee "/match
# "cp <word> <word>" was scanned as if it were real shell syntax by Patterns
# 2-4, extracting a bogus BASH_TARGET and firing bash_write_through on plain
# commit-message text. Fixed by gating Patterns 2-4 on HAS_HEREDOC == false,
# same as Pattern 1.
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Heredoc-Prose False-Positive Regression ---${T_NC}"

REPO_HP=$(init_repo)
switch_branch "$REPO_HP" "dev"

# jq -Rn (not json_bash's raw printf interpolation) to correctly escape the
# embedded newlines/quotes a real multi-line heredoc command contains.
json_bash_multiline() {
    local command="$1"
    local cwd="$2"
    jq -Rn --arg cmd "$command" --arg cwd "$cwd" \
        '{tool_name:"Bash",tool_input:{command:$cmd},cwd:$cwd}'
}

# The exact false-positive trigger: "touch " as prose inside a heredoc body.
HEREDOC_TOUCH_CMD='git commit -m "$(cat <<'"'"'EOF'"'"'
fix: repro test

touch exit code was verified as part of this fix
EOF
)"'
run_test \
    "test_bash_heredoc_prose_touch_no_false_confirm" \
    0 \
    "$(json_bash_multiline "$HEREDOC_TOUCH_CMD" "$REPO_HP")" \
    "$REPO_HP"

# Same class, tee prose.
HEREDOC_TEE_CMD='git commit -m "$(cat <<'"'"'EOF'"'"'
fix: pipeline change

tee output to the log for visibility
EOF
)"'
run_test \
    "test_bash_heredoc_prose_tee_no_false_confirm" \
    0 \
    "$(json_bash_multiline "$HEREDOC_TEE_CMD" "$REPO_HP")" \
    "$REPO_HP"

# Same class, cp prose.
HEREDOC_CP_CMD='git commit -m "$(cat <<'"'"'EOF'"'"'
fix: docs move

cp old-name to new-name in the changelog entry
EOF
)"'
run_test \
    "test_bash_heredoc_prose_cp_no_false_confirm" \
    0 \
    "$(json_bash_multiline "$HEREDOC_CP_CMD" "$REPO_HP")" \
    "$REPO_HP"

# Regression must not weaken real detection: a genuine touch of a new code
# file OUTSIDE any heredoc must still be caught.
run_test \
    "test_bash_touch_real_writethrough_still_blocked" \
    2 \
    "$(json_bash "touch new_file.py" "$REPO_HP")" \
    "$REPO_HP"

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

# --------------------------------------------------------------------------
# Group 17: One-shot marker TTL expiration (v2.17.0)
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- One-Shot Marker TTL ---${T_NC}"

REPO_TTL=$(init_repo)
switch_branch "$REPO_TTL" "dev"

# Fresh marker (just created) -> ALLOW
mkdir -p "$REPO_TTL/.claude"
touch "$REPO_TTL/.claude/allow-once"

run_test \
    "test_oneshot_fresh_marker_allowed" \
    0 \
    "$(json_write "$REPO_TTL/src/fresh.py" "$REPO_TTL")" \
    "$REPO_TTL"

# Expired marker (6 minutes old) -> BLOCK
mkdir -p "$REPO_TTL/.claude"
touch "$REPO_TTL/.claude/allow-once"
# Backdate the marker by 6 minutes (360 seconds) using Python (reliable cross-platform)
python3 -c "
import os, time
path = '$REPO_TTL/.claude/allow-once'
t = time.time() - 360
os.utime(path, (t, t))
"

run_test \
    "test_oneshot_expired_marker_blocked" \
    2 \
    "$(json_write "$REPO_TTL/src/expired.py" "$REPO_TTL")" \
    "$REPO_TTL"

# Verify expired marker was cleaned up
if [[ ! -f "$REPO_TTL/.claude/allow-once" ]]; then
    TOTAL=$((TOTAL + 1)); PASS=$((PASS + 1))
    echo -e "  ${T_GREEN}PASS${T_NC}  test_oneshot_expired_marker_cleaned_up  ${T_BOLD}(file removed)${T_NC}"
else
    TOTAL=$((TOTAL + 1)); FAIL=$((FAIL + 1))
    FAILED_NAMES+=("test_oneshot_expired_marker_cleaned_up")
    echo -e "  ${T_RED}FAIL${T_NC}  test_oneshot_expired_marker_cleaned_up  ${T_BOLD}(file still exists)${T_NC}"
fi

echo ""

# --------------------------------------------------------------------------
# Group 18: Broadened rm .git detection (v2.17.0)
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Broadened rm .git Detection ---${T_NC}"

REPO_RM=$(init_repo)
create_and_switch "$REPO_RM" "feature/rm-test"

# rm -fr .git -> CONFIRM (ask, exits 2 in non-interactive mode — was hard-block)
run_test \
    "test_rm_fr_git_blocked" \
    2 \
    "$(json_bash "rm -fr .git" "$REPO_RM")" \
    "$REPO_RM"

# rm -Rf .git -> CONFIRM (ask, exits 2 in non-interactive mode)
run_test \
    "test_rm_Rf_git_blocked" \
    2 \
    "$(json_bash "rm -Rf .git" "$REPO_RM")" \
    "$REPO_RM"

# rm -fR .git -> CONFIRM (ask, exits 2 in non-interactive mode)
run_test \
    "test_rm_fR_git_blocked" \
    2 \
    "$(json_bash "rm -fR .git" "$REPO_RM")" \
    "$REPO_RM"

# rm -f .gitignore -> ALLOW (not .git itself)
run_test \
    "test_rm_gitignore_allowed" \
    0 \
    "$(json_bash "rm -f .gitignore" "$REPO_RM")" \
    "$REPO_RM"

# rm -rf .github -> ALLOW (not .git)
run_test \
    "test_rm_github_dir_allowed" \
    0 \
    "$(json_bash "rm -rf .github" "$REPO_RM")" \
    "$REPO_RM"

echo ""

# --------------------------------------------------------------------------
# Group 19: TOCTOU guard in session counter (v2.17.0)
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Session Counter Edge Cases ---${T_NC}"

REPO_TOCTOU=$(init_repo)
switch_branch "$REPO_TOCTOU" "dev"

# Session counter with missing file — should not error
rm -f "$REPO_TOCTOU/.claude/guard-session-counts"

run_test \
    "test_session_counter_missing_file_no_error" \
    2 \
    "$(json_write "$REPO_TOCTOU/src/new.py" "$REPO_TOCTOU")" \
    "$REPO_TOCTOU"

# Session counter with empty file — should not error
mkdir -p "$REPO_TOCTOU/.claude"
: > "$REPO_TOCTOU/.claude/guard-session-counts"

run_test \
    "test_session_counter_empty_file_no_error" \
    2 \
    "$(json_write "$REPO_TOCTOU/src/new2.py" "$REPO_TOCTOU")" \
    "$REPO_TOCTOU"

# ============================================================================
# Group 20: Squash-merge branch cleanup bypass
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 20: Squash-merge bypass for git branch -D ---${T_NC}"

# 2026-07-29: squash-merged branches no longer get a SILENT exit 0 — the
# new contract is an explicit [CONFIRM] naming the verified evidence (never
# an unconditional allow, never an unconditional block). See branch-guard.sh
# section 8d "Verified-merge confirm gate".

REPO_SQ20=$(init_repo)
(
    cd "$REPO_SQ20"
    git checkout dev --quiet 2>/dev/null
    git checkout -b "feature/sq-merged" --quiet 2>/dev/null
    echo "feature work" > feature.txt
    git add feature.txt
    git commit -m "feat: feature work" --quiet
    git checkout dev --quiet 2>/dev/null
    git merge --squash "feature/sq-merged" --quiet
    git commit -m "squash: feature work" --quiet
)

run_test_with_stderr \
    "test_git_branch_delete_squash_merged_now_CONFIRMS_not_silent" \
    2 \
    "$(json_bash "git branch -D feature/sq-merged" "$REPO_SQ20")" \
    "$REPO_SQ20" \
    "VERIFIED merged"

REPO_UNM20=$(init_repo)
(
    cd "$REPO_UNM20"
    git checkout dev --quiet 2>/dev/null
    git checkout -b "feature/not-merged" --quiet 2>/dev/null
    echo "unmerged work" > work.txt
    git add work.txt
    git commit -m "feat: unmerged work" --quiet
    git checkout dev --quiet 2>/dev/null
)

run_test_with_stderr \
    "test_git_branch_delete_unmerged_BLOCKED_generic_reasoning" \
    2 \
    "$(json_bash "git branch -D feature/not-merged" "$REPO_UNM20")" \
    "$REPO_UNM20" \
    "commits may be lost"

# Strong check (gh pr view + merge-base --is-ancestor): mock `gh` in PATH so
# the test never hits the network. Verifies the PR-backed evidence path
# fires (not just the local is_squash_merged fast path) — the whole reason
# this gate exists is that repos exist where the local check false-negatives
# on a real multi-commit squash merge but `gh`/the PR record still proves it.
REPO_SQ20B=$(init_repo)
(
    cd "$REPO_SQ20B"
    git checkout dev --quiet 2>/dev/null
    git checkout -b "feature/pr-merged" --quiet 2>/dev/null
    echo "a" > a.txt; git add a.txt; git commit -m "feat: a" --quiet
    echo "b" > b.txt; git add b.txt; git commit -m "feat: b" --quiet
    echo "c" > c.txt; git add c.txt; git commit -m "feat: c" --quiet
)
BG_PR_TIP="$(cd "$REPO_SQ20B" && git rev-parse refs/heads/feature/pr-merged)"
(
    cd "$REPO_SQ20B"
    git checkout dev --quiet 2>/dev/null
    git merge --squash "feature/pr-merged" --quiet
    git commit -m "squash: multi-commit feature" --quiet
)
BG_MERGE_SHA="$(cd "$REPO_SQ20B" && git rev-parse dev)"
(
    # Unrelated follow-up commit on dev AFTER the squash-merge — this is
    # what makes the local tree-diff fallback false-negative (dev's tip
    # tree no longer matches the branch's tip tree) while the strong
    # check still correctly sees BG_MERGE_SHA as an ancestor of dev. This
    # is the exact multi-commit-squash false-negative shape documented in
    # repo memory git-cherry-misreports-squash-merges.
    cd "$REPO_SQ20B"
    echo "unrelated" > unrelated.txt
    git add unrelated.txt
    git commit -m "chore: unrelated follow-up" --quiet
)

BG_FAKE_BIN="$(make_tmpdir)"
cat > "$BG_FAKE_BIN/gh" <<EOF
#!/bin/bash
if [[ "\$1" == "pr" && "\$2" == "view" && "\$3" == "feature/pr-merged" ]]; then
  echo '{"number":123,"headRefOid":"${BG_PR_TIP}","mergeCommit":{"oid":"${BG_MERGE_SHA}"},"state":"MERGED"}'
  exit 0
fi
exit 1
EOF
chmod +x "$BG_FAKE_BIN/gh"

BG_STRONG_EXIT=0
BG_STRONG_STDERR=$(echo "$(json_bash "git branch -D feature/pr-merged" "$REPO_SQ20B")" | (cd "$REPO_SQ20B" && PATH="$BG_FAKE_BIN:$PATH" bash "$HOOK_SCRIPT") 2>&1 >/dev/null) || BG_STRONG_EXIT=$?
TOTAL=$((TOTAL + 1))
if [[ "$BG_STRONG_EXIT" -eq 2 ]] && echo "$BG_STRONG_STDERR" | grep -qi "PR #123"; then
    PASS=$((PASS + 1))
    echo -e "  ${T_GREEN}PASS${T_NC}  test_git_branch_delete_strong_check_reports_pr_number  ${T_BOLD}(exit=$BG_STRONG_EXIT, pattern matched)${T_NC}"
else
    FAIL=$((FAIL + 1))
    FAILED_NAMES+=("test_git_branch_delete_strong_check_reports_pr_number")
    echo -e "  ${T_RED}FAIL${T_NC}  test_git_branch_delete_strong_check_reports_pr_number  ${T_BOLD}(expected exit=2 + 'PR #123', got exit=$BG_STRONG_EXIT)${T_NC}"
    echo -e "        stderr: $(echo "$BG_STRONG_STDERR" | head -5)"
fi

# Planted-defect control: one verified branch + one genuinely unmerged
# branch in the SAME -D command must still BLOCK with the generic
# (non-VERIFIED) reasoning — partial verification must never downgrade
# the whole command to a soft confirm.
REPO_MIX20=$(init_repo)
(
    cd "$REPO_MIX20"
    git checkout dev --quiet 2>/dev/null
    git checkout -b "feature/sq-merged-2" --quiet 2>/dev/null
    echo "x" > x.txt; git add x.txt; git commit -m "feat: x" --quiet
    git checkout dev --quiet 2>/dev/null
    git merge --squash "feature/sq-merged-2" --quiet
    git commit -m "squash: x" --quiet
    git checkout -b "feature/not-merged-2" --quiet 2>/dev/null
    echo "y" > y.txt; git add y.txt; git commit -m "feat: y" --quiet
    git checkout dev --quiet 2>/dev/null
)

run_test_with_stderr \
    "test_git_branch_delete_mixed_verified_and_unmerged_still_BLOCKED" \
    2 \
    "$(json_bash "git branch -D feature/sq-merged-2 feature/not-merged-2" "$REPO_MIX20")" \
    "$REPO_MIX20" \
    "commits may be lost"

echo ""

# ============================================================================
# Group 21: GUARD_DRY_RUN=1 / --classify ground-truth mode
# (SPEC-branch-protection-consolidation-2026-07-07 §4.6 #3 / §6 dogfood tier)
# ============================================================================
echo -e "${T_BLUE}--- Group 21: --classify / GUARD_DRY_RUN=1 ground-truth mode ---${T_NC}"

# This mode is additive to the repo script and is not installed system-wide,
# so exercise scripts/branch-guard.sh directly regardless of HOOK_SCRIPT.
CLASSIFY_SCRIPT="$SCRIPT_DIR/../scripts/branch-guard.sh"

run_classify_test() {
    local name="$1"
    local expected_pattern="$2"
    local json="$3"
    local cwd="$4"

    TOTAL=$((TOTAL + 1))
    local out
    out=$(cd "$cwd" && echo "$json" | GUARD_DRY_RUN=1 bash "$CLASSIFY_SCRIPT" 2>&1)

    if echo "$out" | grep -qE "$expected_pattern"; then
        PASS=$((PASS + 1))
        echo -e "  ${T_GREEN}PASS${T_NC}  $name  ${T_BOLD}($out)${T_NC}"
    else
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$name")
        echo -e "  ${T_RED}FAIL${T_NC}  $name  ${T_BOLD}(expected match /$expected_pattern/, got: $out)${T_NC}"
    fi
}

REPO_CLASSIFY=$(init_repo)

run_classify_test \
    "test_classify_commit_on_main_is_BLOCK" \
    "^BLOCK:" \
    "$(json_bash "git commit -m test" "$REPO_CLASSIFY")" \
    "$REPO_CLASSIFY"

switch_branch "$REPO_CLASSIFY" "dev"

run_classify_test \
    "test_classify_new_code_on_dev_is_ASK" \
    "^ASK:" \
    "$(json_write "$REPO_CLASSIFY/newfile.py" "$REPO_CLASSIFY")" \
    "$REPO_CLASSIFY"

run_classify_test \
    "test_classify_edit_existing_on_dev_is_ALLOW" \
    "^ALLOW:" \
    "$(json_write "$REPO_CLASSIFY/README.md" "$REPO_CLASSIFY")" \
    "$REPO_CLASSIFY"

create_and_switch "$REPO_CLASSIFY" "feature/classify-test"

run_classify_test \
    "test_classify_feature_branch_is_ALLOW" \
    "^ALLOW:" \
    "$(json_write "$REPO_CLASSIFY/anything.py" "$REPO_CLASSIFY")" \
    "$REPO_CLASSIFY"

echo ""

# --------------------------------------------------------------------------
# Group: Cross-context target resolution (2026-07-14, GRILL-branch-guard-
# target-resolution) — a leading `cd <path> &&`/`cd <path>;` or `-C <path>`
# retargets the command to a DIFFERENT directory than the session cwd; the
# hook must classify against the RESOLVED target, not the session's own
# branch/protection.
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Cross-Context Target Resolution ---${T_NC}"

# Scenario 1: session on dev, command cd's into an unprotected feature
# worktree and pushes from there — must ALLOW (was: false-positive block,
# because the hook only ever looked at the session's own 'dev' branch).
REPO_XCTX=$(init_repo)
switch_branch "$REPO_XCTX" "dev"
XCTX_WORKTREE=$(make_tmpdir)
rmdir "$XCTX_WORKTREE"
(cd "$REPO_XCTX" && git worktree add --quiet -b feature/xctx-test "$XCTX_WORKTREE" dev)

run_test \
    "test_cd_into_feature_worktree_push_is_ALLOW" \
    0 \
    "$(json_bash "cd $XCTX_WORKTREE && git push origin feature/xctx-test" "$REPO_XCTX")" \
    "$REPO_XCTX"

# Scenario 2: session on dev, command `-C <other-repo>` targets a DIFFERENT
# repository whose current branch is main — must CONFIRM (exit 2, [CONFIRM]
# in stderr), never a hard [BLOCK] with no bypass path. This is the explicit
# "I do not want hard gate to disrupt" decision.
REPO_XCTX2=$(init_repo)
switch_branch "$REPO_XCTX2" "dev"
OTHER_REPO=$(make_tmpdir)
(cd "$OTHER_REPO" && git init -b main --quiet && git config user.email t@t.com && git config user.name T && git commit -m init --quiet --allow-empty)

run_test_with_stderr \
    "test_cross_repo_C_flag_push_to_other_main_is_CONFIRM" \
    2 \
    "$(json_bash "git -C $OTHER_REPO push origin main" "$REPO_XCTX2")" \
    "$REPO_XCTX2" \
    "\[CONFIRM\]"

# Scenario 2b: same cross-repo push must NOT contain a bare "[BLOCK]" tag —
# regression guard against silently reverting to the old hard-block path.
run_test_with_stderr \
    "test_cross_repo_C_flag_push_is_not_hard_BLOCK" \
    2 \
    "$(json_bash "git -C $OTHER_REPO push origin main" "$REPO_XCTX2")" \
    "$REPO_XCTX2" \
    "smart mode"

# Scenario 3: same-repo compound command (no cd/-C retarget) is UNAFFECTED —
# regression guard that the new resolver doesn't touch ordinary same-repo
# classification. `git push --force` on dev still confirms as before.
REPO_XCTX3=$(init_repo)
switch_branch "$REPO_XCTX3" "dev"

run_test_with_stderr \
    "test_same_repo_force_push_still_CONFIRM" \
    2 \
    "$(json_bash "git push --force origin dev" "$REPO_XCTX3")" \
    "$REPO_XCTX3" \
    "\[CONFIRM\]"

# --------------------------------------------------------------------------
# Multi-hop cumulative cd tracking (2026-07-15, guard-cd-resolution) — a
# compound command with MORE THAN ONE cd retargets to the LAST directory, not
# the first. The pre-#284 single-hop resolver (regex anchored ^cd, head -1)
# picked the FIRST cd and would classify against the wrong repo.
# --------------------------------------------------------------------------

# Scenario 4: `cd <main-repo> && cd <feature-worktree> && git push` — the FIRST
# cd lands on a repo checked out on main (would CONFIRM/block if it were the
# target), the SECOND cd lands on an unprotected feature worktree. Cumulative
# tracking must resolve to the worktree → ALLOW (exit 0). Single-hop-first
# would have picked the main repo and blocked — this is the differentiator.
REPO_MH_MAIN=$(init_repo)          # left on main (protected)
REPO_MH_BASE=$(init_repo)
switch_branch "$REPO_MH_BASE" "dev"
MH_WORKTREE=$(make_tmpdir); rmdir "$MH_WORKTREE"
(cd "$REPO_MH_BASE" && git worktree add --quiet -b feature/mh-test "$MH_WORKTREE" dev)

run_test \
    "test_multihop_cd_last_wins_resolves_to_feature_worktree_ALLOW" \
    0 \
    "$(json_bash "cd $REPO_MH_MAIN && cd $MH_WORKTREE && git push origin feature/mh-test" "$REPO_MH_BASE")" \
    "$REPO_MH_BASE"

# Scenario 5: mixed `cd <main-repo> && git -C <feature-worktree> push` — the
# `-C` target (feature worktree) is resolved against the cd'd effective cwd and
# wins → ALLOW (exit 0).
run_test \
    "test_multihop_cd_then_C_flag_resolves_to_feature_worktree_ALLOW" \
    0 \
    "$(json_bash "cd $REPO_MH_MAIN && git -C $MH_WORKTREE push origin feature/mh-test" "$REPO_MH_BASE")" \
    "$REPO_MH_BASE"

# Scenario 6: inverse — `cd <feature-worktree> && cd <main-repo> && git push`.
# Last cd lands on a repo checked out on main; cumulative tracking must resolve
# there and CONFIRM (exit 2), proving last-wins gates the protected target even
# when an unprotected dir came first.
run_test_with_stderr \
    "test_multihop_cd_last_wins_resolves_to_main_CONFIRM" \
    2 \
    "$(json_bash "cd $MH_WORKTREE && cd $REPO_MH_MAIN && git push origin main" "$REPO_MH_BASE")" \
    "$REPO_MH_BASE" \
    "\[CONFIRM\]"

echo ""

# --------------------------------------------------------------------------
# Group 22: Quoted-span + path-scoping false-positive regression (2026-07-16)
#
# Same failure class as Group 14c (heredoc prose), generalized. Patterns 1-4
# coarse-scanned $COMMAND with plain grep, which has no notion of quoting: a
# `>` or `cp `/`tee `/`touch ` substring INSIDE a single- or double-quoted
# argument (an awk/grep/sed program, a search pattern) was scanned as if it
# were real shell syntax. Three of these fired live during a session auditing
# THIS exact bug class: `awk 'NR>=203 && ...'`, `grep -E '>[^=]'`, and a grep
# whose search pattern literally contained "cp " as quoted text. A fourth,
# unrelated bug fired alongside it: `cp <installed-hook> /tmp/...bak` was
# flagged as "creates a new code file on dev" even though /tmp is nowhere
# near the repo — only /dev/* was excluded, not general out-of-repo targets.
#
# Fix: COMMAND_SCAN strips quoted-span CONTENTS before the coarse `grep -q`
# checks (detection only — extraction still runs against the ORIGINAL
# $COMMAND, so a real quoted target survives); BASH_ACTUAL is now checked
# against a PROJECT_ROOT prefix before being flagged.
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Quoted-Span + Path-Scoping Regression ---${T_NC}"

REPO_QS=$(init_repo)
switch_branch "$REPO_QS" "dev"

# The exact awk invocation that fired live: '>=' inside a single-quoted
# program is program syntax, not a shell redirect.
run_test \
    "test_bash_awk_single_quoted_ge_allowed" \
    0 \
    "$(json_bash "awk 'NR>=203 && /^## / {exit} NR>=203' file.md" "$REPO_QS")" \
    "$REPO_QS"

# The exact grep invocation that fired live: '>[^=]' inside a single-quoted
# -E pattern is regex syntax, not a shell redirect.
run_test \
    "test_bash_grep_pattern_with_gt_allowed" \
    0 \
    "$(json_bash "grep -E '>[^=]' scripts/branch-guard.sh" "$REPO_QS")" \
    "$REPO_QS"

# A literal "cp " substring inside a double-quoted grep search pattern (not
# an invocation of cp) must not trip Pattern 3.
run_test \
    "test_bash_grep_quoted_cp_substring_allowed" \
    0 \
    "$(json_bash_multiline 'grep -n "cp \|redirect" tests/test_branch_guard.sh' "$REPO_QS")" \
    "$REPO_QS"

# Backing up an installed hook to /tmp before re-running an installer — the
# real command from the session that surfaced the path-scoping bug. /tmp is
# outside PROJECT_ROOT entirely; must never be flagged as "creates a new
# code file on dev".
run_test \
    "test_bash_cp_to_tmp_outside_repo_allowed" \
    0 \
    "$(json_bash "cp ~/.claude/hooks/branch-guard.sh /tmp/branch-guard-pre-install-copy" "$REPO_QS")" \
    "$REPO_QS"

# Same class: redirecting output to a file under $HOME, well outside the repo.
run_test \
    "test_bash_redirect_to_home_outside_repo_allowed" \
    0 \
    '{"tool_name":"Bash","tool_input":{"command":"echo backup > /tmp/scratch_notes.py"},"cwd":"'"$REPO_QS"'"}' \
    "$REPO_QS"

# --- Regression guards: the fix must not weaken real detection ---

# Two SEPARATE double-quoted strings that each contain exactly one apostrophe,
# straddling a REAL unquoted redirect — proves COMMAND_SCAN's single-quote
# stripping is a combined alternation (resolves quote-type at the first quote
# char) rather than two independent passes. Two independent passes would pair
# the apostrophe in "it's" with the one in "don't" across the redirect in
# between and erase it from the scan, letting a genuine write-through on dev
# go completely undetected — confirmed live as a false negative before this
# test was added (2026-07-16).
run_test \
    "test_bash_cross_quote_apostrophes_dont_eat_real_redirect" \
    2 \
    "$(json_bash_multiline "echo \"it's ready\" > brand_new_cross_quote.py && echo \"don't tell\"" "$REPO_QS")" \
    "$REPO_QS"

# A real redirect immediately after a single-quoted grep pattern must still
# be caught — proves COMMAND_SCAN stripping doesn't eat an UNQUOTED '>'
# elsewhere in the same command.
run_test \
    "test_bash_quoted_pattern_plus_real_redirect_still_blocked" \
    2 \
    "$(json_bash "grep 'pattern' file.py > brand_new_output.py" "$REPO_QS")" \
    "$REPO_QS"

# A real redirect to a quoted target (spaces in the filename) must still be
# caught with the CORRECT target extracted — proves extraction against the
# ORIGINAL command (not the quote-stripped scan copy) still works.
run_test \
    "test_bash_redirect_quoted_target_with_space_still_blocked" \
    2 \
    "$(json_bash "cat > 'new file.py'" "$REPO_QS")" \
    "$REPO_QS"

# cp to a genuinely new code file INSIDE the repo must still be caught —
# proves path-scoping only excludes out-of-repo targets, not in-repo ones.
run_test \
    "test_bash_cp_inside_repo_still_blocked" \
    2 \
    "$(json_bash "cp template.py brand_new_inside.py" "$REPO_QS")" \
    "$REPO_QS"

# A real, unquoted touch of a guard-bypass marker must still fire even when
# the same command also contains an unrelated quoted string mentioning
# "touch" as prose — proves the fix doesn't over-suppress real Pattern 4
# matches just because a quoted decoy exists elsewhere.
run_test \
    "test_bash_real_touch_bypass_with_quoted_decoy_still_blocked" \
    2 \
    "$(json_bash "echo 'note: touch base first' && touch .claude/allow-once" "$REPO_QS")" \
    "$REPO_QS"

echo ""
echo -e "${T_BLUE}--- CRAFT_GUARD_ALLOW_DEV_EDIT Escape Hatch (issue #281) ---${T_NC}"

REPO_DEV_EDIT=$(init_repo)
switch_branch "$REPO_DEV_EDIT" "dev"

# Baseline (no env var): all three call sites (Edit, Write, Bash-touch) must
# still confirm/block exactly as before — this is a regression guard, not new
# behavior.
run_test \
    "test_edit_guard_bypass_marker_still_confirms_without_env" \
    2 \
    "$(json_edit "$REPO_DEV_EDIT/.claude/allow-dev-edit" "$REPO_DEV_EDIT")" \
    "$REPO_DEV_EDIT"

run_test \
    "test_write_guard_bypass_marker_still_confirms_without_env" \
    2 \
    "$(json_write "$REPO_DEV_EDIT/.claude/allow-dev-edit" "$REPO_DEV_EDIT")" \
    "$REPO_DEV_EDIT"

run_test \
    "test_bash_touch_guard_bypass_marker_still_confirms_without_env" \
    2 \
    "$(json_bash "touch .claude/allow-dev-edit" "$REPO_DEV_EDIT")" \
    "$REPO_DEV_EDIT"

# All three guard-bypass-marker confirms must surface the CRAFT_GUARD_ALLOW_DEV_EDIT
# escape hatch (issue #309) — the "Claude writes .claude/allow-once" flow is
# circular for this self-referential action, so the env var is the only
# non-interactive route and must not be discoverable-nowhere. Each check uses
# a FRESH repo/session (not REPO_DEV_EDIT, already 1 encounter deep on these
# action_types above) — suggestions only render at "full" (1st-encounter)
# verbosity; a repeat encounter renders the brief box, which omits them, and
# would false-fail this check for the wrong reason.
REPO_MSG_EDIT=$(init_repo); switch_branch "$REPO_MSG_EDIT" "dev"
run_test_with_stderr \
    "test_edit_guard_bypass_message_mentions_env_var" \
    2 \
    "$(json_edit "$REPO_MSG_EDIT/.claude/allow-dev-edit" "$REPO_MSG_EDIT")" \
    "$REPO_MSG_EDIT" \
    "CRAFT_GUARD_ALLOW_DEV_EDIT"

REPO_MSG_WRITE=$(init_repo); switch_branch "$REPO_MSG_WRITE" "dev"
run_test_with_stderr \
    "test_write_guard_bypass_message_mentions_env_var" \
    2 \
    "$(json_write "$REPO_MSG_WRITE/.claude/allow-dev-edit" "$REPO_MSG_WRITE")" \
    "$REPO_MSG_WRITE" \
    "CRAFT_GUARD_ALLOW_DEV_EDIT"

REPO_MSG_BASH=$(init_repo); switch_branch "$REPO_MSG_BASH" "dev"
run_test_with_stderr \
    "test_bash_touch_guard_bypass_message_mentions_env_var" \
    2 \
    "$(json_bash "touch .claude/allow-dev-edit" "$REPO_MSG_BASH")" \
    "$REPO_MSG_BASH" \
    "CRAFT_GUARD_ALLOW_DEV_EDIT"

# The env-var hint must NOT leak into the unrelated write_new_code confirm —
# that action isn't self-referential, and allow-once genuinely resolves it as
# documented; mentioning the marker-bypass env var there would recreate the
# exact confusion issue #309 reported (a working non-interactive route buried
# among suggestions that don't apply to it).
#
# Both assertions below MUST read the same 1st-encounter capture. Suggest:
# lines only render at "full" (1st-encounter) verbosity — a 2nd+ encounter
# renders "brief", which omits ALL suggestions regardless of content, so
# checking a later call would pass this negative assertion vacuously (it
# would still pass even if the hint WERE mistakenly added to write_new_code)
# rather than actually exercising the code path it's meant to guard.
REPO_MSG_NEWCODE=$(init_repo); switch_branch "$REPO_MSG_NEWCODE" "dev"
NEW_CODE_STDERR=$(echo "$(json_write "$REPO_MSG_NEWCODE/src/unrelated_new.py" "$REPO_MSG_NEWCODE")" | (cd "$REPO_MSG_NEWCODE" && bash "$HOOK_SCRIPT") 2>&1 >/dev/null) || true

TOTAL=$((TOTAL + 1))
if echo "$NEW_CODE_STDERR" | grep -qi "New code files"; then
    PASS=$((PASS + 1))
    echo -e "  ${T_GREEN}PASS${T_NC}  test_write_new_code_message_does_not_mention_env_var  ${T_BOLD}(exit=2, pattern matched)${T_NC}"
else
    FAIL=$((FAIL + 1))
    FAILED_NAMES+=("test_write_new_code_message_does_not_mention_env_var")
    echo -e "  ${T_RED}FAIL${T_NC}  test_write_new_code_message_does_not_mention_env_var  ${T_BOLD}(1st-encounter stderr missing 'New code files')${T_NC}"
fi

TOTAL=$((TOTAL + 1))
if ! echo "$NEW_CODE_STDERR" | grep -q "CRAFT_GUARD_ALLOW_DEV_EDIT"; then
    PASS=$((PASS + 1))
    echo -e "  ${T_GREEN}PASS${T_NC}  test_write_new_code_message_excludes_env_var_hint"
else
    FAIL=$((FAIL + 1))
    FAILED_NAMES+=("test_write_new_code_message_excludes_env_var_hint")
    echo -e "  ${T_RED}FAIL${T_NC}  test_write_new_code_message_excludes_env_var_hint  ${T_BOLD}(env var hint leaked into unrelated confirm)${T_NC}"
fi

# With the env var set: all three call sites exit 0 without a [CONFIRM].
# run_test has no env-injection param, so these three small wrappers pass
# CRAFT_GUARD_ALLOW_DEV_EDIT=1 through to the hook invocation directly.
run_edit_test_with_env() {
    local name="$1" expected="$2" file_path="$3" cwd="$4"
    TOTAL=$((TOTAL + 1))
    local actual_exit=0
    local stderr_output
    stderr_output=$(echo "$(json_edit "$file_path" "$cwd")" | (cd "$cwd" && CRAFT_GUARD_ALLOW_DEV_EDIT=1 bash "$HOOK_SCRIPT") 2>&1 >/dev/null) || actual_exit=$?
    if [[ "$actual_exit" -eq "$expected" ]]; then
        PASS=$((PASS + 1))
        echo -e "  ${T_GREEN}PASS${T_NC}  $name  ${T_BOLD}(exit=$actual_exit)${T_NC}"
    else
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$name")
        echo -e "  ${T_RED}FAIL${T_NC}  $name  ${T_BOLD}(expected=$expected, got=$actual_exit)${T_NC}"
        [[ -n "$stderr_output" ]] && echo -e "        stderr: $(echo "$stderr_output" | head -3)"
    fi
}

run_write_test_with_env() {
    local name="$1" expected="$2" file_path="$3" cwd="$4"
    TOTAL=$((TOTAL + 1))
    local actual_exit=0
    local stderr_output
    stderr_output=$(echo "$(json_write "$file_path" "$cwd")" | (cd "$cwd" && CRAFT_GUARD_ALLOW_DEV_EDIT=1 bash "$HOOK_SCRIPT") 2>&1 >/dev/null) || actual_exit=$?
    if [[ "$actual_exit" -eq "$expected" ]]; then
        PASS=$((PASS + 1))
        echo -e "  ${T_GREEN}PASS${T_NC}  $name  ${T_BOLD}(exit=$actual_exit)${T_NC}"
    else
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$name")
        echo -e "  ${T_RED}FAIL${T_NC}  $name  ${T_BOLD}(expected=$expected, got=$actual_exit)${T_NC}"
        [[ -n "$stderr_output" ]] && echo -e "        stderr: $(echo "$stderr_output" | head -3)"
    fi
}

run_bash_test_with_env() {
    local name="$1" expected="$2" command="$3" cwd="$4"
    TOTAL=$((TOTAL + 1))
    local actual_exit=0
    local stderr_output
    stderr_output=$(echo "$(json_bash "$command" "$cwd")" | (cd "$cwd" && CRAFT_GUARD_ALLOW_DEV_EDIT=1 bash "$HOOK_SCRIPT") 2>&1 >/dev/null) || actual_exit=$?
    if [[ "$actual_exit" -eq "$expected" ]]; then
        PASS=$((PASS + 1))
        echo -e "  ${T_GREEN}PASS${T_NC}  $name  ${T_BOLD}(exit=$actual_exit)${T_NC}"
    else
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$name")
        echo -e "  ${T_RED}FAIL${T_NC}  $name  ${T_BOLD}(expected=$expected, got=$actual_exit)${T_NC}"
        [[ -n "$stderr_output" ]] && echo -e "        stderr: $(echo "$stderr_output" | head -3)"
    fi
}

run_edit_test_with_env \
    "test_edit_guard_bypass_marker_allowed_with_env" \
    0 \
    "$REPO_DEV_EDIT/.claude/allow-dev-edit" \
    "$REPO_DEV_EDIT"

run_write_test_with_env \
    "test_write_guard_bypass_marker_allowed_with_env" \
    0 \
    "$REPO_DEV_EDIT/.claude/allow-dev-edit" \
    "$REPO_DEV_EDIT"

run_bash_test_with_env \
    "test_bash_touch_guard_bypass_marker_allowed_with_env" \
    0 \
    "touch .claude/allow-dev-edit" \
    "$REPO_DEV_EDIT"

# The env var must NOT globalize to unrelated MEDIUM-risk gates (e.g. a
# regular new code file) — it is scoped to the guard-bypass marker only.
run_bash_test_with_env \
    "test_env_var_does_not_globalize_to_unrelated_medium_risk" \
    2 \
    "touch src/unrelated_new_file.py" \
    "$REPO_DEV_EDIT"

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
