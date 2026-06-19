#!/usr/bin/env bash
#
# Test Suite for ~/.claude/hooks/no-switch-guard.sh
# Tests: Switch/worktree gating hook for Claude Code PreToolUse (Bash)
#
# Usage:
#   ./tests/test_no_switch_guard.sh           # Run all tests
#   bash tests/test_no_switch_guard.sh        # Run all tests
#
# Approach:
#   - Pipes JSON {"tool_input":{"command":"<cmd>"}} to the hook via stdin
#   - Hook always exits 0; decisions are encoded in JSON stdout
#   - GREEN tests: assert exit 0 AND stdout is empty (silent allow)
#   - YELLOW tests: assert exit 0 AND stdout contains "systemMessage"
#   - RED tests: assert exit 0 AND stdout contains "permissionDecision" + "ask"
#
# IMPORTANT: this suite exercises the INSTALLED hook at $HOME/.claude/hooks/,
# NOT the repo copy at scripts/no-switch-guard.sh. If you edited scripts/no-switch-guard.sh,
# reinstall first:
#   bash scripts/install-guards.sh
# (CI does exactly this before running — see .github/workflows/ci.yml.)

# Note: Not using 'set -e' because we want tests to continue after failures
set -uo pipefail

# ============================================================================
# Configuration
# ============================================================================

# Defaults to the INSTALLED hook (CI installs the PR hook first); override with
# HOOK_SCRIPT=scripts/no-switch-guard.sh to test the repo copy directly.
HOOK_SCRIPT="${HOOK_SCRIPT:-$HOME/.claude/hooks/no-switch-guard.sh}"

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
    echo "  Install the hook first: bash scripts/install-guards.sh"
    exit 1
fi

if ! command -v git &>/dev/null; then
    echo -e "${T_RED}ERROR${T_NC}: git is not available"
    exit 1
fi

if ! command -v jq &>/dev/null; then
    echo -e "${T_RED}ERROR${T_NC}: jq is not available"
    exit 1
fi

# ============================================================================
# Helpers
# ============================================================================

# Create a temp directory and register it for cleanup
make_tmpdir() {
    local dir
    dir=$(mktemp -d "${TMPDIR:-/tmp}/no-switch-guard-test.XXXXXX")
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

# Initialize a clean git repo with main + dev branches and an initial commit.
# Returns the repo path via stdout.
init_repo() {
    local repo
    repo=$(make_tmpdir)
    (
        cd "$repo"
        git init -b main --quiet
        git config user.email "test@test.com"
        git config user.name "Test"
        echo "# README" > README.md
        git add -A
        git commit -m "Initial commit" --quiet
        git branch dev
        git checkout dev --quiet 2>/dev/null
    )
    echo "$repo"
}

# Build the JSON payload for a Bash command
json_bash() {
    local command="$1"
    # Use jq to safely encode the command string (handles special chars)
    jq -nc --arg cmd "$command" '{"tool_input":{"command":$cmd}}'
}

# ---------------------------------------------------------------------------
# run_green "test_name" "command" [cwd]
#   Asserts: exit 0 AND stdout is empty (silent allow)
# ---------------------------------------------------------------------------
run_green() {
    local name="$1"
    local cmd="$2"
    local cwd="${3:-}"

    TOTAL=$((TOTAL + 1))

    local stdout exit_code=0
    if [[ -n "$cwd" ]]; then
        stdout=$(json_bash "$cmd" | (cd "$cwd" && bash "$HOOK_SCRIPT")) || exit_code=$?
    else
        stdout=$(json_bash "$cmd" | bash "$HOOK_SCRIPT") || exit_code=$?
    fi

    local exit_ok=false stdout_ok=false
    [[ "$exit_code" -eq 0 ]] && exit_ok=true
    [[ -z "$stdout" ]] && stdout_ok=true

    if [[ "$exit_ok" == true && "$stdout_ok" == true ]]; then
        PASS=$((PASS + 1))
        echo -e "  ${T_GREEN}PASS${T_NC}  $name  ${T_BOLD}(GREEN: silent allow)${T_NC}"
    else
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$name")
        local reason=""
        [[ "$exit_ok" == false ]] && reason+=" exit=${exit_code}≠0"
        [[ "$stdout_ok" == false ]] && reason+=" stdout='${stdout:0:80}'"
        echo -e "  ${T_RED}FAIL${T_NC}  $name  ${T_BOLD}(GREEN: expected silent allow;${reason})${T_NC}"
    fi
}

# ---------------------------------------------------------------------------
# run_yellow "test_name" "command" [cwd]
#   Asserts: exit 0 AND stdout contains "systemMessage"
# ---------------------------------------------------------------------------
run_yellow() {
    local name="$1"
    local cmd="$2"
    local cwd="${3:-}"

    TOTAL=$((TOTAL + 1))

    local stdout exit_code=0
    if [[ -n "$cwd" ]]; then
        stdout=$(json_bash "$cmd" | (cd "$cwd" && bash "$HOOK_SCRIPT")) || exit_code=$?
    else
        stdout=$(json_bash "$cmd" | bash "$HOOK_SCRIPT") || exit_code=$?
    fi

    local exit_ok=false msg_ok=false
    [[ "$exit_code" -eq 0 ]] && exit_ok=true
    echo "$stdout" | grep -q '"systemMessage"' && msg_ok=true

    if [[ "$exit_ok" == true && "$msg_ok" == true ]]; then
        PASS=$((PASS + 1))
        echo -e "  ${T_GREEN}PASS${T_NC}  $name  ${T_BOLD}(YELLOW: announced)${T_NC}"
    else
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$name")
        local reason=""
        [[ "$exit_ok" == false ]] && reason+=" exit=${exit_code}≠0"
        [[ "$msg_ok" == false ]] && reason+=" missing systemMessage. stdout='${stdout:0:120}'"
        echo -e "  ${T_RED}FAIL${T_NC}  $name  ${T_BOLD}(YELLOW: expected announce;${reason})${T_NC}"
    fi
}

# ---------------------------------------------------------------------------
# run_red "test_name" "command" [cwd]
#   Asserts: exit 0 AND stdout contains permissionDecision:"ask"
# ---------------------------------------------------------------------------
run_red() {
    local name="$1"
    local cmd="$2"
    local cwd="${3:-}"

    TOTAL=$((TOTAL + 1))

    local stdout exit_code=0
    if [[ -n "$cwd" ]]; then
        stdout=$(json_bash "$cmd" | (cd "$cwd" && bash "$HOOK_SCRIPT")) || exit_code=$?
    else
        stdout=$(json_bash "$cmd" | bash "$HOOK_SCRIPT") || exit_code=$?
    fi

    local exit_ok=false ask_ok=false
    [[ "$exit_code" -eq 0 ]] && exit_ok=true
    echo "$stdout" | grep -q '"permissionDecision"' && echo "$stdout" | grep -q '"ask"' && ask_ok=true

    if [[ "$exit_ok" == true && "$ask_ok" == true ]]; then
        PASS=$((PASS + 1))
        echo -e "  ${T_GREEN}PASS${T_NC}  $name  ${T_BOLD}(RED: ask prompted)${T_NC}"
    else
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$name")
        local reason=""
        [[ "$exit_ok" == false ]] && reason+=" exit=${exit_code}≠0"
        [[ "$ask_ok" == false ]] && reason+=" missing permissionDecision/ask. stdout='${stdout:0:120}'"
        echo -e "  ${T_RED}FAIL${T_NC}  $name  ${T_BOLD}(RED: expected ask;${reason})${T_NC}"
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
echo -e "${T_BOLD}No-Switch Guard Hook Tests${T_NC}"
echo -e "${T_BOLD}==========================${T_NC}"
echo -e "Hook: $HOOK_SCRIPT"
echo ""

# --------------------------------------------------------------------------
# Group 1: GREEN — read-only inspection (always allow silently)
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- GREEN: Read-Only Inspection (silent allow) ---${T_NC}"

run_green "test_green_branch_show_current" \
    "git branch --show-current"

run_green "test_green_worktree_list" \
    "git worktree list"

run_green "test_green_status" \
    "git status"

run_green "test_green_log_oneline" \
    "git log --oneline -5"

run_green "test_green_diff_head" \
    "git diff HEAD"

run_green "test_green_stash_list" \
    "git stash list"

run_green "test_green_non_git_command" \
    "ls -la"

run_green "test_green_git_fetch" \
    "git fetch origin"

echo ""

# --------------------------------------------------------------------------
# Group 2: YELLOW — allowed with announcement
# Need a clean git repo so is_dirty() returns false.
# Run from the temp repo so the guard checks THAT repo's status, not the
# worktree we're sitting in (which may be dirty).
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- YELLOW: Allowed + Announced ---${T_NC}"

CLEAN_REPO=$(init_repo)

# Switch to a non-main branch in a clean repo -> YELLOW announce
run_yellow "test_yellow_switch_to_dev_clean" \
    "git switch dev" \
    "$CLEAN_REPO"

# worktree add -> YELLOW announce (regardless of tree state)
run_yellow "test_yellow_worktree_add" \
    "git worktree add ~/.git-worktrees/test/feature-x -b feature/x dev" \
    "$CLEAN_REPO"

echo ""

# --------------------------------------------------------------------------
# Group 3: RED — confirmation required
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- RED: Destructive Restore ---${T_NC}"

# git restore (without --staged) -> RED (discards working-tree changes)
run_red "test_red_restore_file" \
    "git restore somefile.txt"

# git restore --staged -> GREEN (only unstages, doesn't discard working-tree changes)
run_green "test_green_restore_staged_allows" \
    "git restore --staged somefile.txt"

# git checkout -- <file> -> RED (destructive restore)
run_red "test_red_checkout_dash_dash" \
    "git checkout -- somefile.txt"

echo ""
echo -e "${T_BLUE}--- RED: New Branch Creation ---${T_NC}"

# git switch -c new-branch -> RED
run_red "test_red_switch_create" \
    "git switch -c new-branch"

# git switch -C new-branch (force-create) -> RED
run_red "test_red_switch_force_create" \
    "git switch -C new-branch"

# git checkout -b new-branch -> RED
run_red "test_red_checkout_dash_b" \
    "git checkout -b new-branch"

# git checkout -B new-branch (force-create) -> RED
run_red "test_red_checkout_dash_B" \
    "git checkout -B new-branch"

echo ""
echo -e "${T_BLUE}--- RED: Switch Onto main/master ---${T_NC}"

CLEAN_REPO2=$(init_repo)

# git switch main -> RED (main is protected)
run_red "test_red_switch_main" \
    "git switch main" \
    "$CLEAN_REPO2"

# git switch master -> RED (master is protected)
run_red "test_red_switch_master" \
    "git switch master"

# git switch origin/main -> RED
run_red "test_red_switch_origin_main" \
    "git switch origin/main"

echo ""
echo -e "${T_BLUE}--- RED: Dirty Working Tree Switch ---${T_NC}"

# Create a dirty repo: unstaged change in working tree
DIRTY_REPO=$(make_tmpdir)
(
    cd "$DIRTY_REPO"
    git init -b main --quiet
    git config user.email "test@test.com"
    git config user.name "Test"
    echo "initial" > README.md
    git add -A
    git commit -m "Initial commit" --quiet
    git branch dev
    # Make tree dirty: untracked file (not staged)
    echo "dirty" > untracked.txt
)

# Switch to dev with dirty tree -> RED
run_red "test_red_switch_dev_dirty_tree" \
    "git switch dev" \
    "$DIRTY_REPO"

echo ""
echo -e "${T_BLUE}--- RED: Destructive Worktree Ops ---${T_NC}"

# git worktree remove -> RED
run_red "test_red_worktree_remove" \
    "git worktree remove ~/.git-worktrees/test/some-tree"

# git worktree move -> RED
run_red "test_red_worktree_move" \
    "git worktree move src dst"

echo ""

# --------------------------------------------------------------------------
# Group 4: Edge cases
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Edge Cases ---${T_NC}"

# Empty command -> GREEN (exit 0, silent)
run_green "test_green_empty_command" \
    ""

# git checkout (without branch = file restore context, no -b or --) -> YELLOW
# This switches to an existing branch if given; without args it's ambiguous.
# The guard treats "git checkout dev" as a switch to existing branch.
run_yellow "test_yellow_checkout_existing_branch" \
    "git checkout dev" \
    "$CLEAN_REPO"

# git checkout -- . on clean repo -> RED (destructive restore)
run_red "test_red_checkout_dash_dash_dot" \
    "git checkout -- ."

echo ""

# --------------------------------------------------------------------------
# Group 5: Registry disable/mute path (#5 — guards.json enable/mute)
# Uses a fake HOME so the real ~/.claude/guards.json is never touched.
# Command is a RED new-branch create, so it would ASK unless the registry
# disables/mutes the guard.
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Registry: disable / mute path ---${T_NC}"

# run_registry name expected(silent|ask) spec command
#   spec ∈ DISABLED | ENABLED | MUTED_FUTURE | MUTED_PAST | CORRUPT
run_registry() {
    local name="$1" expected="$2" spec="$3" cmd="$4"
    TOTAL=$((TOTAL + 1))
    local fh gj t
    fh=$(make_tmpdir); mkdir -p "$fh/.claude"; gj="$fh/.claude/guards.json"
    case "$spec" in
        DISABLED)     printf '{"guards":{"no-switch-guard":{"enabled":false}}}\n' > "$gj" ;;
        ENABLED)      printf '{"guards":{"no-switch-guard":{"enabled":true,"muted_until":null}}}\n' > "$gj" ;;
        MUTED_FUTURE) t=$(date -u -v+1H +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -d "+1 hour" +"%Y-%m-%dT%H:%M:%SZ")
                      printf '{"guards":{"no-switch-guard":{"enabled":true,"muted_until":"%s"}}}\n' "$t" > "$gj" ;;
        MUTED_PAST)   t=$(date -u -v-1H +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -d "-1 hour" +"%Y-%m-%dT%H:%M:%SZ")
                      printf '{"guards":{"no-switch-guard":{"enabled":true,"muted_until":"%s"}}}\n' "$t" > "$gj" ;;
        CORRUPT)      printf '{ not valid json' > "$gj" ;;
    esac
    local stdout exit_code=0
    stdout=$(json_bash "$cmd" | HOME="$fh" bash "$HOOK_SCRIPT") || exit_code=$?
    local ok=false
    if [[ "$expected" == "silent" ]]; then
        [[ "$exit_code" -eq 0 && -z "$stdout" ]] && ok=true
    else
        { [[ "$exit_code" -eq 0 ]] && echo "$stdout" | grep -q '"permissionDecision"' && echo "$stdout" | grep -q '"ask"'; } && ok=true
    fi
    if [[ "$ok" == true ]]; then
        PASS=$((PASS + 1))
        echo -e "  ${T_GREEN}PASS${T_NC}  $name  ${T_BOLD}(registry: $spec → $expected)${T_NC}"
    else
        FAIL=$((FAIL + 1)); FAILED_NAMES+=("$name")
        echo -e "  ${T_RED}FAIL${T_NC}  $name  ${T_BOLD}(registry: $spec expected $expected; exit=$exit_code stdout='${stdout:0:80}')${T_NC}"
    fi
}

# disabled → guard silent (no gating)
run_registry "test_registry_disabled_silent"     silent DISABLED     "git switch -c regtest"
# muted, window not yet expired → silent
run_registry "test_registry_muted_future_silent" silent MUTED_FUTURE "git switch -c regtest"
# muted, window expired → guard active again (ask)
run_registry "test_registry_muted_past_ask"      ask    MUTED_PAST   "git switch -c regtest"
# enabled, not muted → ask (normal)
run_registry "test_registry_enabled_ask"         ask    ENABLED      "git switch -c regtest"
# corrupt guards.json → FAIL OPEN (guard stays active → ask)
run_registry "test_registry_corrupt_failopen"    ask    CORRUPT      "git switch -c regtest"

echo ""

# ============================================================================
# Summary
# ============================================================================

echo -e "${T_BOLD}======================================${T_NC}"
echo -e "${T_BOLD}  No-Switch Guard Test Summary${T_NC}"
echo -e "${T_BOLD}======================================${T_NC}"
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
