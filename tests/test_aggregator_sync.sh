#!/usr/bin/env bash
#
# Test Suite for scripts/aggregator-sync.sh
#
# aggregator-sync updates ONE plugin's version entry in the Data-Wise
# aggregator marketplace.json (the single cross-plugin source of truth), so a
# release can keep the aggregator from drifting (the 5th leg in verify-surfaces).
# It only updates an EXISTING entry — it never silently adds an unknown plugin.
#
# Usage: ./tests/test_aggregator_sync.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SYNC_SCRIPT="$PROJECT_ROOT/scripts/aggregator-sync.sh"

T_RED='\033[0;31m'; T_GREEN='\033[0;32m'; T_BLUE='\033[0;34m'; T_NC='\033[0m'
TOTAL_TESTS=0; PASSED_TESTS=0; FAILED_TESTS=0
declare -a FAILED_TEST_NAMES=()
FIXTURE=""

pass() { ((PASSED_TESTS++)); echo -e "${T_GREEN}  ✓ PASS${T_NC}: $1"; }
fail() { ((FAILED_TESTS++)); FAILED_TEST_NAMES+=("$1: ${2:-}"); echo -e "${T_RED}  ✗ FAIL${T_NC}: $1"; echo -e "${T_RED}    Reason: ${2:-Unknown}${T_NC}"; }
assert_equals() { ((TOTAL_TESTS++)); if [ "$1" = "$2" ]; then pass "$3"; else fail "$3" "Expected '$1', got '$2'"; fi; }

entry_version() { python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(next((p['version'] for p in d['plugins'] if p['name']==sys.argv[2]), 'MISSING'))" "$1" "$2"; }

make_fixture() {
    FIXTURE=$(mktemp)
    cat > "$FIXTURE" <<'JSON'
{ "name": "data-wise", "plugins": [
  { "name": "craft", "version": "2.36.0" },
  { "name": "scholar", "version": "2.24.0" }
] }
JSON
}
destroy_fixture() { [ -n "$FIXTURE" ] && rm -f "$FIXTURE"; FIXTURE=""; }

# ----------------------------------------------------------------------------
test_updates_entry() {
    echo -e "${T_BLUE}[TEST]${T_NC} SYNC: updates the named plugin, leaves others untouched"
    make_fixture
    local exit_code=0
    bash "$SYNC_SCRIPT" --file "$FIXTURE" --plugin craft --version 2.37.0 >/dev/null 2>&1 || exit_code=$?

    assert_equals "0" "$exit_code" "Sync exits 0"
    assert_equals "2.37.0" "$(entry_version "$FIXTURE" craft)" "craft entry updated to 2.37.0"
    assert_equals "2.24.0" "$(entry_version "$FIXTURE" scholar)" "scholar entry untouched"

    # Valid JSON after write.
    ((TOTAL_TESTS++))
    if python3 -c "import json; json.load(open('$FIXTURE'))" 2>/dev/null; then pass "Result is valid JSON"; else fail "Result is valid JSON" "parse failed"; fi
    destroy_fixture
}

test_idempotent() {
    echo -e "${T_BLUE}[TEST]${T_NC} SYNC: re-running with the same version is a clean no-op"
    make_fixture
    bash "$SYNC_SCRIPT" --file "$FIXTURE" --plugin craft --version 2.37.0 >/dev/null 2>&1
    local exit_code=0
    bash "$SYNC_SCRIPT" --file "$FIXTURE" --plugin craft --version 2.37.0 >/dev/null 2>&1 || exit_code=$?
    assert_equals "0" "$exit_code" "Second identical sync exits 0"
    assert_equals "2.37.0" "$(entry_version "$FIXTURE" craft)" "craft still 2.37.0"
    destroy_fixture
}

test_unknown_plugin_errors() {
    echo -e "${T_BLUE}[TEST]${T_NC} SYNC: an unknown plugin is an error, not a silent add"
    make_fixture
    local exit_code=0
    bash "$SYNC_SCRIPT" --file "$FIXTURE" --plugin ghost --version 9.9.9 >/dev/null 2>&1 || exit_code=$?
    ((TOTAL_TESTS++)); [ "$exit_code" != "0" ] && pass "Unknown plugin exits non-zero" || fail "Unknown plugin exits non-zero" "got 0"
    assert_equals "MISSING" "$(entry_version "$FIXTURE" ghost)" "ghost was not added"
    destroy_fixture
}

test_check_mode_no_write() {
    echo -e "${T_BLUE}[TEST]${T_NC} SYNC: --check reports drift but does not modify the file"
    make_fixture
    local before; before=$(cat "$FIXTURE")
    bash "$SYNC_SCRIPT" --file "$FIXTURE" --plugin craft --version 2.37.0 --check >/dev/null 2>&1
    local after; after=$(cat "$FIXTURE")
    assert_equals "$before" "$after" "--check leaves the file unchanged"
    destroy_fixture
}

test_flag_as_value_rejected() {
    echo -e "${T_BLUE}[TEST]${T_NC} ARGS: a flag swallowed as a value is rejected (exit 2, not misleading)"
    make_fixture
    local exit_code=0
    # `--file --plugin craft ...` must NOT set FILE='--plugin'; expect usage error.
    bash "$SYNC_SCRIPT" --file --plugin craft --version 2.37.0 >/dev/null 2>&1 || exit_code=$?
    assert_equals "2" "$exit_code" "--file with a flag-as-value exits 2 (usage error)"
    destroy_fixture
}

print_summary() {
    echo ""
    echo -e "${T_BLUE}═══════════════════════════════════════════${T_NC}"
    echo -e "  Total: $TOTAL_TESTS  ${T_GREEN}Passed: $PASSED_TESTS${T_NC}  ${T_RED}Failed: $FAILED_TESTS${T_NC}"
    for n in "${FAILED_TEST_NAMES[@]:-}"; do [ -n "$n" ] && echo -e "  ${T_RED}✗${T_NC} $n"; done
}

main() {
    echo -e "${T_BLUE}aggregator-sync.sh Test Suite${T_NC}"
    test_updates_entry
    test_idempotent
    test_unknown_plugin_errors
    test_check_mode_no_write
    test_flag_as_value_rejected
    print_summary
    [ "$FAILED_TESTS" -gt 0 ] && exit 1 || exit 0
}

main "$@"
