#!/usr/bin/env bash
#
# Test Suite for ~/.claude/hooks/reference-scope-guard.sh (issue #286)
# Tests: advisory naming-convention hook for Writes/Edits under ~/.claude/reference/
#
# Usage:
#   ./tests/test_reference_scope_guard.sh
#   HOOK_SCRIPT=scripts/reference-scope-guard.sh ./tests/test_reference_scope_guard.sh
#
# Approach:
#   - Pipes JSON {"tool_name":"...","tool_input":{"file_path":"..."},"cwd":"..."} via stdin
#   - Hook is advisory-only: it ALWAYS exits 0, never blocks
#   - Assert exit 0 always; assert whether stderr carries the
#     "[reference-scope-guard]" advisory marker or is silent
#
# IMPORTANT: this suite exercises the INSTALLED hook at $HOME/.claude/hooks/ by
# default, NOT the repo copy at scripts/reference-scope-guard.sh. If you edited
# the repo copy, reinstall first: bash scripts/install-guards.sh
# (or override with HOOK_SCRIPT=scripts/reference-scope-guard.sh to test the
# repo copy directly.)

set -uo pipefail

HOOK_SCRIPT="${HOOK_SCRIPT:-$HOME/.claude/hooks/reference-scope-guard.sh}"

T_RED='\033[0;31m'
T_GREEN='\033[0;32m'
T_YELLOW='\033[1;33m'
T_BOLD='\033[1m'
T_NC='\033[0m'

TOTAL=0
PASS=0
FAIL=0
declare -a FAILED_NAMES=()

if [[ ! -f "$HOOK_SCRIPT" ]]; then
    echo -e "${T_RED}ERROR${T_NC}: Hook script not found at $HOOK_SCRIPT"
    echo "  Install the hook first: bash scripts/install-guards.sh"
    exit 1
fi

if ! command -v jq &>/dev/null; then
    echo -e "${T_RED}ERROR${T_NC}: jq is not available"
    exit 1
fi

json_payload() {
    local tool_name="$1" file_path="$2"
    jq -n --arg tn "$tool_name" --arg fp "$file_path" --arg cwd "/tmp" \
        '{tool_name: $tn, tool_input: {file_path: $fp}, cwd: $cwd}'
}

# run_silent <name> <tool_name> <file_path>
# Asserts exit 0 AND no advisory marker on stderr (in-scope-and-clean, or
# out-of-scope-entirely).
run_silent() {
    local name="$1" tool_name="$2" file_path="$3"
    TOTAL=$((TOTAL + 1))

    local stderr_out exit_code=0
    stderr_out=$(json_payload "$tool_name" "$file_path" | bash "$HOOK_SCRIPT" 2>&1 >/dev/null) || exit_code=$?

    if [[ $exit_code -eq 0 && "$stderr_out" != *"[reference-scope-guard]"* ]]; then
        PASS=$((PASS + 1))
        echo -e "  ${T_GREEN}PASS${T_NC}  $name  ${T_BOLD}(silent)${T_NC}"
    else
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$name")
        echo -e "  ${T_RED}FAIL${T_NC}  $name  ${T_BOLD}(expected silent exit=0; got exit=${exit_code} stderr='${stderr_out:0:120}')${T_NC}"
    fi
}

# run_advisory <name> <tool_name> <file_path> <expected_reason_substring>
# Asserts exit 0 AND the advisory marker + a specific reason appear on stderr.
run_advisory() {
    local name="$1" tool_name="$2" file_path="$3" expected_reason="$4"
    TOTAL=$((TOTAL + 1))

    local stderr_out exit_code=0
    stderr_out=$(json_payload "$tool_name" "$file_path" | bash "$HOOK_SCRIPT" 2>&1 >/dev/null) || exit_code=$?

    if [[ $exit_code -eq 0 && "$stderr_out" == *"[reference-scope-guard]"* && "$stderr_out" == *"$expected_reason"* ]]; then
        PASS=$((PASS + 1))
        echo -e "  ${T_GREEN}PASS${T_NC}  $name  ${T_BOLD}(advisory: $expected_reason)${T_NC}"
    else
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$name")
        echo -e "  ${T_RED}FAIL${T_NC}  $name  ${T_BOLD}(expected advisory containing '$expected_reason'; got exit=${exit_code} stderr='${stderr_out:0:200}')${T_NC}"
    fi
}

echo -e "${T_BOLD}=== In-scope, clean filenames (silent) ===${T_NC}"
run_silent "test_clean_kebab_case_silent" "Write" "$HOME/.claude/reference/shell-workflow.md"
run_silent "test_clean_single_word_silent" "Edit" "$HOME/.claude/reference/email-neovim.md"

echo ""
echo -e "${T_BOLD}=== In-scope, non-conforming filenames (advisory, still exit 0) ===${T_NC}"
run_advisory "test_html_extension_flagged" "Write" "$HOME/.claude/reference/tutor-cookbook.html" "no .html files"
run_advisory "test_spec_prefix_flagged" "Write" "$HOME/.claude/reference/SPEC-proof-tutorial-tooling.md" "no SPEC-*/GRILL-*/BRAINSTORM-* prefix"
run_advisory "test_grill_prefix_flagged" "Edit" "$HOME/.claude/reference/GRILL-foo.md" "no SPEC-*/GRILL-*/BRAINSTORM-* prefix"
run_advisory "test_brainstorm_prefix_flagged" "Write" "$HOME/.claude/reference/brainstorm-thing.md" "no SPEC-*/GRILL-*/BRAINSTORM-* prefix"
run_advisory "test_uppercase_flagged" "Write" "$HOME/.claude/reference/Cookbook.md" "kebab-case"
run_advisory "test_underscore_flagged" "Write" "$HOME/.claude/reference/my_notes.md" "kebab-case"
run_advisory "test_tilde_path_expanded" "Write" "~/.claude/reference/Cookbook.md" "kebab-case"

echo ""
echo -e "${T_BOLD}=== Out of scope (silent regardless of filename shape) ===${T_NC}"
run_silent "test_out_of_scope_directory_silent" "Write" "/some/other/dir/BADNAME.html"
run_silent "test_out_of_scope_reference_prefix_silent" "Write" "$HOME/.claude/reference-old/BADNAME.html"
run_silent "test_bash_tool_not_checked" "Bash" "$HOME/.claude/reference/BADNAME.html"
run_silent "test_read_tool_not_checked" "Read" "$HOME/.claude/reference/BADNAME.html"

echo ""

echo -e "${T_BOLD}======================================${T_NC}"
echo -e "${T_BOLD}  Reference-Scope Guard Test Summary${T_NC}"
echo -e "${T_BOLD}======================================${T_NC}"
echo ""
echo -e "  Total:   ${T_BOLD}$TOTAL${T_NC}"
echo -e "  Passed:  ${T_GREEN}$PASS${T_NC}"
echo -e "  Failed:  ${T_RED}$FAIL${T_NC}"
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
