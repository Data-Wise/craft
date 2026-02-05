#!/usr/bin/env bash
#
# Test Suite for scripts/formatting.sh
# Tests: Unit, Integration, Edge Cases
#
# Usage:
#   ./tests/test_formatting.sh              # Run all tests
#   ./tests/test_formatting.sh unit         # Run unit tests only
#   ./tests/test_formatting.sh integration  # Run integration tests only
#   ./tests/test_formatting.sh edge         # Run edge case tests only

# Note: Not using 'set -e' because we want tests to continue after failures
set -uo pipefail

# Test configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

# Color output (local to tests, not from formatting.sh)
T_RED='\033[0;31m'
T_GREEN='\033[0;32m'
T_YELLOW='\033[1;33m'
T_BLUE='\033[0;34m'
T_NC='\033[0m'

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

declare -a FAILED_TEST_NAMES=()

# ============================================================================
# Helper Functions
# ============================================================================

log_test() {
    local category="$1"
    local name="$2"
    echo -e "${T_BLUE}[TEST]${T_NC} ${category}: ${name}"
}

pass() {
    local name="$1"
    ((PASSED_TESTS++))
    echo -e "${T_GREEN}  ✓ PASS${T_NC}: $name"
}

fail() {
    local name="$1"
    local reason="${2:-Unknown failure}"
    ((FAILED_TESTS++))
    FAILED_TEST_NAMES+=("$name: $reason")
    echo -e "${T_RED}  ✗ FAIL${T_NC}: $name"
    echo -e "${T_RED}    Reason: $reason${T_NC}"
}

skip_test() {
    local name="$1"
    local reason="${2:-Skipped}"
    ((SKIPPED_TESTS++))
    echo -e "${T_YELLOW}  ⊘ SKIP${T_NC}: $name ($reason)"
}

assert_equals() {
    local expected="$1"
    local actual="$2"
    local test_name="$3"

    ((TOTAL_TESTS++))
    if [ "$expected" = "$actual" ]; then
        pass "$test_name"
    else
        fail "$test_name" "Expected '$expected', got '$actual'"
    fi
}

assert_contains() {
    local haystack="$1"
    local needle="$2"
    local test_name="$3"

    ((TOTAL_TESTS++))
    if echo "$haystack" | grep -qF "$needle"; then
        pass "$test_name"
    else
        fail "$test_name" "Expected to find '$needle' in output"
    fi
}

assert_not_contains() {
    local haystack="$1"
    local needle="$2"
    local test_name="$3"

    ((TOTAL_TESTS++))
    if echo "$haystack" | grep -qF "$needle"; then
        fail "$test_name" "Did not expect to find '$needle' in output"
    else
        pass "$test_name"
    fi
}

assert_line_count() {
    local expected="$1"
    local text="$2"
    local test_name="$3"

    ((TOTAL_TESTS++))
    local actual
    actual=$(echo "$text" | wc -l | tr -d ' ')
    if [ "$expected" = "$actual" ]; then
        pass "$test_name"
    else
        fail "$test_name" "Expected $expected lines, got $actual"
    fi
}

# Strip ANSI codes from text (test helper, independent of formatting.sh)
_test_strip_ansi() {
    printf '%b' "$1" | sed $'s/\033\[[0-9;]*m//g'
}

# Get visible length of a line (test helper)
_test_visible_len() {
    local stripped
    stripped=$(_test_strip_ansi "$1")
    echo ${#stripped}
}

# Verify all lines of output are exactly N visible chars wide
_test_verify_width() {
    local text="$1"
    local expected_width="$2"
    local test_name="$3"

    ((TOTAL_TESTS++))
    local all_ok=true
    local bad_line=""
    local bad_len=0

    while IFS= read -r line; do
        local stripped
        stripped=$(_test_strip_ansi "$line")
        local len=${#stripped}
        if [ "$len" -ne "$expected_width" ]; then
            all_ok=false
            bad_line="$stripped"
            bad_len=$len
            break
        fi
    done <<< "$text"

    if [ "$all_ok" = true ]; then
        pass "$test_name"
    else
        fail "$test_name" "Line has width $bad_len (expected $expected_width): [$bad_line]"
    fi
}

# Source formatting.sh in a clean subshell and run a function
_run_fmt() {
    bash -c "source '$SCRIPTS_DIR/formatting.sh'; $1"
}

# ============================================================================
# UNIT TESTS
# ============================================================================

run_unit_tests() {
    echo -e "\n${T_BLUE}═══════════════════════════════════════════════════════════${T_NC}"
    echo -e "${T_BLUE}  UNIT TESTS - Individual Component Testing${T_NC}"
    echo -e "${T_BLUE}═══════════════════════════════════════════════════════════${T_NC}\n"

    # --- File exists and is executable ---
    log_test "Unit" "Library file exists"
    ((TOTAL_TESTS++))
    if [ -f "$SCRIPTS_DIR/formatting.sh" ]; then
        pass "formatting.sh exists"
    else
        fail "formatting.sh exists" "File not found at $SCRIPTS_DIR/formatting.sh"
    fi

    ((TOTAL_TESTS++))
    if [ -x "$SCRIPTS_DIR/formatting.sh" ]; then
        pass "formatting.sh is executable"
    else
        fail "formatting.sh is executable" "File is not executable"
    fi

    # --- Source guard ---
    log_test "Unit" "Source guard"
    local guard_output
    guard_output=$(_run_fmt 'echo "first"; source scripts/formatting.sh; echo "second"')
    assert_contains "$guard_output" "first" "Source guard: first source works"
    assert_contains "$guard_output" "second" "Source guard: double-source no error"

    # --- Color constants ---
    log_test "Unit" "Color constants defined"
    local colors_output
    colors_output=$(_run_fmt '
        echo "RED=${FMT_RED:+set}"
        echo "GREEN=${FMT_GREEN:+set}"
        echo "YELLOW=${FMT_YELLOW:+set}"
        echo "CYAN=${FMT_CYAN:+set}"
        echo "BLUE=${FMT_BLUE:+set}"
        echo "BOLD=${FMT_BOLD:+set}"
        echo "DIM=${FMT_DIM:+set}"
        echo "NC=${FMT_NC:+set}"
    ')
    assert_contains "$colors_output" "RED=set" "FMT_RED defined"
    assert_contains "$colors_output" "GREEN=set" "FMT_GREEN defined"
    assert_contains "$colors_output" "YELLOW=set" "FMT_YELLOW defined"
    assert_contains "$colors_output" "CYAN=set" "FMT_CYAN defined"
    assert_contains "$colors_output" "BLUE=set" "FMT_BLUE defined"
    assert_contains "$colors_output" "BOLD=set" "FMT_BOLD defined"
    assert_contains "$colors_output" "DIM=set" "FMT_DIM defined"
    assert_contains "$colors_output" "NC=set" "FMT_NC defined"

    # --- _fmt_strip_ansi ---
    log_test "Unit" "ANSI stripping"
    local stripped
    stripped=$(_run_fmt '_fmt_strip_ansi "hello"')
    assert_equals "hello" "$stripped" "strip_ansi: plain text unchanged"

    stripped=$(_run_fmt '_fmt_strip_ansi "\033[0;31mred\033[0m"')
    assert_equals "red" "$stripped" "strip_ansi: single color removed"

    stripped=$(_run_fmt '_fmt_strip_ansi "\033[1;33m\033[0;32mnested\033[0m\033[0m"')
    assert_equals "nested" "$stripped" "strip_ansi: nested colors removed"

    stripped=$(_run_fmt '_fmt_strip_ansi ""')
    assert_equals "" "$stripped" "strip_ansi: empty string"

    # --- _fmt_visible_len ---
    log_test "Unit" "Visible length calculation"
    local vlen
    vlen=$(_run_fmt '_fmt_visible_len "hello"')
    assert_equals "5" "$vlen" "visible_len: plain text = 5"

    vlen=$(_run_fmt '_fmt_visible_len "\033[0;31mhello\033[0m"')
    assert_equals "5" "$vlen" "visible_len: colored text = 5"

    vlen=$(_run_fmt '_fmt_visible_len ""')
    assert_equals "0" "$vlen" "visible_len: empty = 0"

    vlen=$(_run_fmt '_fmt_visible_len "  spaced  "')
    assert_equals "10" "$vlen" "visible_len: spaced text = 10"

    # --- _fmt_repeat ---
    log_test "Unit" "Character repeat"
    local repeated
    repeated=$(_run_fmt '_fmt_repeat "=" 5')
    assert_equals "=====" "$repeated" "repeat: 5 equals signs"

    repeated=$(_run_fmt '_fmt_repeat "-" 0')
    assert_equals "" "$repeated" "repeat: 0 chars = empty"

    repeated=$(_run_fmt '_fmt_repeat "x" 1')
    assert_equals "x" "$repeated" "repeat: single char"

    # --- fmt_set_width ---
    log_test "Unit" "Width setting"
    local width_output
    width_output=$(_run_fmt 'fmt_set_width 50; echo $_FMT_WIDTH')
    assert_equals "50" "$width_output" "fmt_set_width: sets to 50"

    width_output=$(_run_fmt 'echo $_FMT_WIDTH')
    assert_equals "63" "$width_output" "fmt_set_width: default is 63"

    # --- fmt_divider ---
    log_test "Unit" "Divider"
    local divider
    divider=$(_run_fmt 'fmt_divider "═"')
    local div_len=${#divider}
    assert_equals "63" "$div_len" "fmt_divider: default width 63"

    divider=$(_run_fmt 'fmt_divider "-" 10')
    assert_equals "----------" "$divider" "fmt_divider: custom width 10"

    divider=$(_run_fmt 'fmt_divider "=" 5')
    assert_equals "=====" "$divider" "fmt_divider: custom char and width"
}

# ============================================================================
# INTEGRATION TESTS — Full Box Rendering
# ============================================================================

run_integration_tests() {
    echo -e "\n${T_BLUE}═══════════════════════════════════════════════════════════${T_NC}"
    echo -e "${T_BLUE}  INTEGRATION TESTS - Full Box Rendering${T_NC}"
    echo -e "${T_BLUE}═══════════════════════════════════════════════════════════${T_NC}\n"

    # --- Double-line box ---
    log_test "Integration" "Double-line box structure"
    local dbox
    dbox=$(_run_fmt '
        box_header "Test Title"
        box_row "  Content"
        box_empty_row
        box_footer
    ')

    assert_contains "$dbox" "╔" "Double box: has top-left corner"
    assert_contains "$dbox" "╗" "Double box: has top-right corner"
    assert_contains "$dbox" "╠" "Double box: has mid-left"
    assert_contains "$dbox" "╣" "Double box: has mid-right"
    assert_contains "$dbox" "╚" "Double box: has bottom-left"
    assert_contains "$dbox" "╝" "Double box: has bottom-right"
    assert_contains "$dbox" "Test Title" "Double box: contains title"
    assert_contains "$dbox" "Content" "Double box: contains content"

    _test_verify_width "$dbox" 63 "Double box: all lines width 63"

    # --- Single-line box ---
    log_test "Integration" "Single-line box structure"
    local sbox
    sbox=$(_run_fmt '
        box_single "Single Test"
        box_row "  Data row"
        box_empty_row
        box_footer
    ')

    assert_contains "$sbox" "┌" "Single box: has top-left corner"
    assert_contains "$sbox" "┐" "Single box: has top-right corner"
    assert_contains "$sbox" "├" "Single box: has mid-left"
    assert_contains "$sbox" "┤" "Single box: has mid-right"
    assert_contains "$sbox" "└" "Single box: has bottom-left"
    assert_contains "$sbox" "┘" "Single box: has bottom-right"
    assert_contains "$sbox" "Single Test" "Single box: contains title"

    _test_verify_width "$sbox" 63 "Single box: all lines width 63"

    # --- Box with colored content ---
    log_test "Integration" "Box with colored content"
    local cbox
    cbox=$(_run_fmt '
        box_header "Colors"
        box_row "  ${FMT_GREEN}green${FMT_NC} text"
        box_row "  ${FMT_RED}red${FMT_NC} and ${FMT_YELLOW}yellow${FMT_NC}"
        box_footer
    ')

    _test_verify_width "$cbox" 63 "Colored box: all lines width 63"

    # Verify ANSI codes are present in raw output
    ((TOTAL_TESTS++))
    if echo "$cbox" | grep -q $'\033'; then
        pass "Colored box: ANSI codes present in output"
    else
        fail "Colored box: ANSI codes present in output" "No ANSI codes found"
    fi

    # --- Box with title color ---
    log_test "Integration" "Box with title color"
    local tcbox
    tcbox=$(_run_fmt '
        box_header "Colored Title" "$FMT_CYAN"
        box_row "  Body"
        box_footer
    ')
    _test_verify_width "$tcbox" 63 "Title-colored box: all lines width 63"
    assert_contains "$tcbox" "Colored Title" "Title-colored box: title present"

    # --- Box separator ---
    log_test "Integration" "Box separator"
    local sepbox
    sepbox=$(_run_fmt '
        box_header "Sep Test"
        box_row "  Above"
        box_separator
        box_row "  Below"
        box_footer
    ')
    _test_verify_width "$sepbox" 63 "Separator box: all lines width 63"

    # Count separators (╠ appears twice: after title and mid-box)
    ((TOTAL_TESTS++))
    local sep_count
    sep_count=$(echo "$sepbox" | grep -c "╠" || true)
    if [ "$sep_count" -eq 2 ]; then
        pass "Separator box: 2 separators present"
    else
        fail "Separator box: 2 separators present" "Found $sep_count separators"
    fi

    # --- Custom width ---
    log_test "Integration" "Custom width box"
    local wbox
    wbox=$(_run_fmt '
        fmt_set_width 40
        box_single "Narrow"
        box_row "  Short"
        box_footer
    ')
    _test_verify_width "$wbox" 40 "Custom width box: all lines width 40"

    # --- Minimal box (header + footer only) ---
    log_test "Integration" "Minimal box"
    local mbox
    mbox=$(_run_fmt '
        box_header "Min"
        box_footer
    ')
    _test_verify_width "$mbox" 63 "Minimal box: all lines width 63"
    assert_line_count "4" "$mbox" "Minimal box: 4 lines (top, title, sep, bottom)"

    # --- Double box then single box ---
    log_test "Integration" "Sequential boxes (double then single)"
    local seqbox
    seqbox=$(_run_fmt '
        box_header "First"
        box_row "  A"
        box_footer
        box_single "Second"
        box_row "  B"
        box_footer
    ')
    assert_contains "$seqbox" "╔" "Sequential: first box is double"
    assert_contains "$seqbox" "┌" "Sequential: second box is single"
    _test_verify_width "$seqbox" 63 "Sequential: all lines width 63"

    # --- Table rendering ---
    log_test "Integration" "Table rendering"
    local tbox
    tbox=$(_run_fmt '
        box_single "Table"
        box_table "Name|Status|Version" "asciinema|OK|3.0.0" "agg|MISSING|-"
        box_footer
    ')
    assert_contains "$tbox" "Name" "Table: header column present"
    assert_contains "$tbox" "asciinema" "Table: data row 1 present"
    assert_contains "$tbox" "MISSING" "Table: data row 2 present"
    _test_verify_width "$tbox" 63 "Table: all lines width 63"
}

# ============================================================================
# EDGE CASE TESTS
# ============================================================================

run_edge_tests() {
    echo -e "\n${T_BLUE}═══════════════════════════════════════════════════════════${T_NC}"
    echo -e "${T_BLUE}  EDGE CASE TESTS${T_NC}"
    echo -e "${T_BLUE}═══════════════════════════════════════════════════════════${T_NC}\n"

    # --- Empty text in box_row ---
    log_test "Edge" "Empty text in box_row"
    local ebox
    ebox=$(_run_fmt '
        box_single "Empty"
        box_row ""
        box_footer
    ')
    _test_verify_width "$ebox" 63 "Empty row: width 63"

    # --- Long text (should not break box) ---
    log_test "Edge" "Long text (overflow)"
    local lbox
    lbox=$(_run_fmt '
        box_single "Long"
        box_row "This is a very long line that exceeds the box width and should still render"
        box_footer
    ')
    # First and last lines should still be 63
    ((TOTAL_TESTS++))
    local first_line
    first_line=$(echo "$lbox" | head -1)
    local first_len
    first_len=$(_test_visible_len "$first_line")
    if [ "$first_len" -eq 63 ]; then
        pass "Long text: border lines still 63"
    else
        fail "Long text: border lines still 63" "First line is $first_len"
    fi

    # --- Only spaces in box_row ---
    log_test "Edge" "Spaces-only content"
    local spbox
    spbox=$(_run_fmt '
        box_single "Spaces"
        box_row "   "
        box_footer
    ')
    _test_verify_width "$spbox" 63 "Spaces-only row: width 63"

    # --- Special characters ---
    log_test "Edge" "Special characters in content"
    local scbox
    scbox=$(_run_fmt '
        box_single "Special"
        box_row "  Path: ~/.claude/plugins/craft"
        box_row "  URL: https://example.com"
        box_row "  Dollars: \$HOME and \$PATH"
        box_footer
    ')
    _test_verify_width "$scbox" 63 "Special chars: width 63"

    # --- No color parameter ---
    log_test "Edge" "box_row without color parameter"
    local ncbox
    ncbox=$(_run_fmt '
        box_header "No Color"
        box_row "  Plain text"
        box_footer
    ')
    _test_verify_width "$ncbox" 63 "No color param: width 63"

    # --- box_row with explicit color parameter ---
    log_test "Edge" "box_row with color parameter"
    local cpbox
    cpbox=$(_run_fmt '
        box_single "Color Param"
        box_row "  Highlighted line" "$FMT_YELLOW"
        box_footer
    ')
    _test_verify_width "$cpbox" 63 "Color param: width 63"

    # --- Width 10 (minimum practical) ---
    log_test "Edge" "Very narrow box (width 10)"
    local nbox
    nbox=$(_run_fmt '
        fmt_set_width 10
        box_single "Hi"
        box_row " test"
        box_footer
    ')
    _test_verify_width "$nbox" 10 "Narrow box: width 10"

    # --- Width 100 ---
    log_test "Edge" "Wide box (width 100)"
    local wbox
    wbox=$(_run_fmt '
        fmt_set_width 100
        box_header "Wide"
        box_row "  Content"
        box_footer
    ')
    _test_verify_width "$wbox" 100 "Wide box: width 100"

    # --- Multiple empty rows ---
    log_test "Edge" "Multiple empty rows"
    local mebox
    mebox=$(_run_fmt '
        box_single "Multi Empty"
        box_empty_row
        box_empty_row
        box_empty_row
        box_footer
    ')
    _test_verify_width "$mebox" 63 "Multiple empty rows: width 63"
    assert_line_count "7" "$mebox" "Multiple empty rows: 7 lines"

    # --- Divider with various chars ---
    log_test "Edge" "Divider variations"
    local div1
    div1=$(_run_fmt 'fmt_divider "─" 20')
    assert_equals "────────────────────" "$div1" "Divider: 20 dashes"

    local div2
    div2=$(_run_fmt 'fmt_divider "=" 5')
    assert_equals "=====" "$div2" "Divider: 5 equals"

    # --- Verify no color leak (NC reset) ---
    log_test "Edge" "No color leak after colored row"
    local leak_test
    leak_test=$(_run_fmt '
        box_single "Leak Test"
        box_row "  ${FMT_RED}red${FMT_NC}"
        box_row "  should be plain"
        box_footer
    ')
    # The "should be plain" row should not contain ANSI codes
    local plain_row
    plain_row=$(echo "$leak_test" | grep "should be plain")
    ((TOTAL_TESTS++))
    if echo "$plain_row" | grep -q $'\033\[0;31m'; then
        fail "No color leak: plain row has no red ANSI" "Found red ANSI code in plain row"
    else
        pass "No color leak: plain row has no red ANSI"
    fi
}

# ============================================================================
# Results Summary
# ============================================================================

print_summary() {
    echo ""
    echo -e "${T_BLUE}═══════════════════════════════════════════════════════════${T_NC}"
    echo -e "${T_BLUE}  TEST RESULTS${T_NC}"
    echo -e "${T_BLUE}═══════════════════════════════════════════════════════════${T_NC}"
    echo ""
    echo -e "  Total:    $TOTAL_TESTS"
    echo -e "  ${T_GREEN}Passed:   $PASSED_TESTS${T_NC}"
    echo -e "  ${T_RED}Failed:   $FAILED_TESTS${T_NC}"
    echo -e "  ${T_YELLOW}Skipped:  $SKIPPED_TESTS${T_NC}"
    echo ""

    if [ ${#FAILED_TEST_NAMES[@]} -gt 0 ]; then
        echo -e "${T_RED}Failed tests:${T_NC}"
        for name in "${FAILED_TEST_NAMES[@]}"; do
            echo -e "  ${T_RED}✗${T_NC} $name"
        done
        echo ""
    fi

    if [ "$FAILED_TESTS" -eq 0 ]; then
        echo -e "${T_GREEN}All $PASSED_TESTS tests passed!${T_NC}"
    else
        echo -e "${T_RED}$FAILED_TESTS of $TOTAL_TESTS tests failed${T_NC}"
    fi
    echo ""
}

# ============================================================================
# Main
# ============================================================================

main() {
    local suite="${1:-all}"

    echo -e "\n${T_BLUE}formatting.sh Test Suite${T_NC}"
    echo -e "${T_BLUE}========================${T_NC}\n"

    case "$suite" in
        unit)
            run_unit_tests
            ;;
        integration)
            run_integration_tests
            ;;
        edge)
            run_edge_tests
            ;;
        all)
            run_unit_tests
            run_integration_tests
            run_edge_tests
            ;;
        *)
            echo "Usage: $0 {unit|integration|edge|all}"
            exit 1
            ;;
    esac

    print_summary

    if [ "$FAILED_TESTS" -gt 0 ]; then
        exit 1
    fi
}

main "$@"
