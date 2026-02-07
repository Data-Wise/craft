#!/bin/bash
# Interactive Dogfooding Tests for: branch-guard.sh
# Generated: 2026-02-06
# Run: bash tests/test_branch_guard_interactive.sh
#
# Human-guided QA tests that validate user-facing behavior of the
# branch protection hook. Each test runs a command, shows expected
# vs actual, and prompts the human for pass/fail.
#
# These tests cover aspects that can't be fully automated:
# - Error message readability and formatting
# - Integration with craft commands
# - Perceived responsiveness

set -euo pipefail

# ============================================
# Configuration
# ============================================

HOOK_SCRIPT="$HOME/.claude/hooks/branch-guard.sh"
PASS=0
FAIL=0
TOTAL=0
TOTAL_TESTS=10

# Logging
LOG_DIR="${LOG_DIR:-tests/cli/logs}"
mkdir -p "$LOG_DIR" 2>/dev/null || LOG_DIR="/tmp"
LOG_FILE="$LOG_DIR/branch-guard-interactive-$(date +%Y%m%d-%H%M%S).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

log "=== Branch Guard Interactive Test Session Started ==="
log "Working directory: $(pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ============================================
# Helpers
# ============================================

print_header() {
    echo -e "${BOLD}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}  BRANCH GUARD INTERACTIVE TESTS ($TOTAL_TESTS tests)${NC}"
    echo -e "${BOLD}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "  ${BLUE}Keys:${NC} y=pass, n=fail, s=skip, q=quit"
    echo -e "  ${BLUE}Log:${NC}  $LOG_FILE"
    echo -e "  ${BLUE}Hook:${NC} $HOOK_SCRIPT"
    echo ""
}

run_test() {
    local test_num=$1
    local test_name=$2
    local command=$3
    local expected=$4

    TOTAL=$((TOTAL + 1))

    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}TEST $test_num/$TOTAL_TESTS: $test_name${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "  ${BLUE}Command:${NC} $command"
    echo ""

    log "TEST $test_num: $test_name"
    log "  Command: $command"

    local output
    output=$(bash -c "$command" 2>&1) || true
    log "  Output: $output"

    echo -e "${BLUE}EXPECTED:${NC} $expected"
    echo ""
    echo -e "${GREEN}ACTUAL:${NC}"
    echo "$output"
    echo ""

    read -p "[y=pass, n=fail, s=skip, q=quit] " -n 1 -r
    echo ""

    case "$REPLY" in
        [Yy])
            PASS=$((PASS + 1))
            log "  Result: PASS"
            echo -e "${GREEN}PASS${NC}"
            ;;
        [Ss])
            log "  Result: SKIP"
            echo -e "${YELLOW}SKIP${NC}"
            ;;
        [Qq])
            log "User quit at test $test_num"
            echo -e "${YELLOW}Exiting...${NC}"
            print_summary
            exit 0
            ;;
        *)
            FAIL=$((FAIL + 1))
            log "  Result: FAIL"
            echo -e "${RED}FAIL${NC}"
            read -p "  Notes (optional): " notes
            [[ -n "$notes" ]] && log "  Notes: $notes"
            ;;
    esac
}

print_summary() {
    echo ""
    echo -e "${BOLD}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}  RESULTS: $PASS passed, $FAIL failed (of $TOTAL run)${NC}"
    echo -e "${BOLD}═══════════════════════════════════════════════════════════════${NC}"

    if [[ $FAIL -eq 0 ]]; then
        echo -e "${GREEN}${BOLD}ALL TESTS PASSED!${NC}"
        log "Final: ALL TESTS PASSED ($PASS/$TOTAL)"
    else
        echo -e "${RED}${BOLD}$FAIL TEST(S) FAILED${NC}"
        log "Final: $FAIL TESTS FAILED"
    fi

    log "Summary: $PASS passed, $FAIL failed"
    echo -e "Log: ${BLUE}$LOG_FILE${NC}"
    echo ""
}

# ============================================
# Preflight
# ============================================

if [[ ! -f "$HOOK_SCRIPT" ]]; then
    echo -e "${RED}ERROR${NC}: Hook not found at $HOOK_SCRIPT"
    exit 1
fi

# ============================================
# Main
# ============================================

print_header

# ============================================
# TEST 1: Hook registration in settings.json
# ============================================

run_test 1 "Hook registered in settings.json" \
    "grep -l 'branch-guard' ~/.claude/settings.json ~/.claude/settings.local.json 2>/dev/null || echo 'Not found in settings files'" \
    "Should show file path where branch-guard hook is registered"

# ============================================
# TEST 2: Error message readability (main block)
# ============================================

run_test 2 "Main branch block message is readable" \
    "echo '{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"src/app.py\"},\"cwd\":\"'$(pwd)'\"}' | bash '$HOOK_SCRIPT' 2>&1 || true" \
    "Clear error with: BRANCH PROTECTION header, file path, branch name, actionable suggestion (checkout dev)"

# ============================================
# TEST 3: Dev branch block message is readable
# ============================================

TMPDIR_T3=$(mktemp -d)
(cd "$TMPDIR_T3" && git init -b main --quiet && git config user.email "t@t" && git config user.name "T" && echo x > f && git add -A && git commit -m init --quiet && git branch dev && git checkout dev --quiet 2>/dev/null)

run_test 3 "Dev branch block message is readable" \
    "echo '{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"src/new.py\",\"content\":\"x\"},\"cwd\":\"$TMPDIR_T3\"}' | (cd '$TMPDIR_T3' && bash '$HOOK_SCRIPT') 2>&1 || true" \
    "Clear error with: BRANCH PROTECTION, file path, options (worktree, edit existing, /craft:git:unprotect)"

rm -rf "$TMPDIR_T3"

# ============================================
# TEST 4: Bypass marker from /craft:git:unprotect
# ============================================

run_test 4 "Bypass marker format check" \
    "if [[ -f .claude/allow-dev-edit ]]; then cat .claude/allow-dev-edit; else echo 'No bypass marker active (expected if not on dev with unprotect)'; fi" \
    "Either valid JSON with reason/timestamp/branch, or message that no marker exists"

# ============================================
# TEST 5: /craft:git:status shows Guard line
# ============================================

run_test 5 "Git status command mentions guard" \
    "test -f commands/git/status.md && grep -i 'guard\|protect' commands/git/status.md | head -5 || echo 'status.md not found'" \
    "status.md should reference branch protection / guard indicator"

# ============================================
# TEST 6: /craft:check shows branch context
# ============================================

run_test 6 "Check command references branch protection" \
    "test -f commands/check.md && grep -i 'branch\|guard\|protect' commands/check.md | head -5 || echo 'check.md not found'" \
    "check.md should reference branch protection context"

# ============================================
# TEST 7: /craft:git:worktree has main protection
# ============================================

run_test 7 "Worktree command has main branch check" \
    "test -f commands/git/worktree.md && grep -i 'main\|protect\|refuse\|block' commands/git/worktree.md | head -5 || echo 'worktree.md not found'" \
    "worktree.md should mention refusing to create from main"

# ============================================
# TEST 8: Dry-run logging visible on stderr
# ============================================

TMPDIR_T8=$(mktemp -d)
(cd "$TMPDIR_T8" && git init -b main --quiet && git config user.email "t@t" && git config user.name "T" && echo x > f && git add -A && git commit -m init --quiet && mkdir -p .claude && touch .claude/branch-guard-dryrun)

run_test 8 "Dry-run mode stderr output" \
    "echo '{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"src/app.py\"},\"cwd\":\"$TMPDIR_T8\"}' | (cd '$TMPDIR_T8' && bash '$HOOK_SCRIPT') 2>&1; echo 'exit: '\$?" \
    "Should show [DRY-RUN] prefix in output and exit 0 (not 2)"

rm -rf "$TMPDIR_T8"

# ============================================
# TEST 9: Performance feels instant
# ============================================

run_test 9 "Hook performance feels instant" \
    "time (for i in \$(seq 1 10); do echo '{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"x.md\",\"content\":\"x\"},\"cwd\":\"'$(pwd)'\"}' | bash '$HOOK_SCRIPT' >/dev/null 2>&1 || true; done) 2>&1" \
    "10 invocations should complete in under 1 second (< 100ms each)"

# ============================================
# TEST 10: Config file format
# ============================================

run_test 10 "branch-guard.json config format" \
    "if [[ -f .claude/branch-guard.json ]]; then cat .claude/branch-guard.json; else echo 'No branch-guard.json found'; fi" \
    "JSON with branch names as keys, protection levels as values (block-all, block-new-code)"

# ============================================
# Summary
# ============================================

log "=== Session Completed ==="
print_summary
