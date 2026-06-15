#!/usr/bin/env bash
#
# Test Suite for scripts/cache-prune.sh
#
# cache-prune GCs stale local-plugins version-cache dirs, keeping current + 2
# most recent per plugin (D7), and ALWAYS reports what it removes (never a
# silent delete). It operates on CACHE_DIR (env-injectable) so tests run on a
# fixture, never the real ~/.claude cache.
#
# Usage: ./tests/test_cache_prune.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PRUNE_SCRIPT="$PROJECT_ROOT/scripts/cache-prune.sh"

T_RED='\033[0;31m'; T_GREEN='\033[0;32m'; T_BLUE='\033[0;34m'; T_NC='\033[0m'
TOTAL_TESTS=0; PASSED_TESTS=0; FAILED_TESTS=0
declare -a FAILED_TEST_NAMES=()
CACHE=""

pass() { ((PASSED_TESTS++)); echo -e "${T_GREEN}  ✓ PASS${T_NC}: $1"; }
fail() { ((FAILED_TESTS++)); FAILED_TEST_NAMES+=("$1: ${2:-}"); echo -e "${T_RED}  ✗ FAIL${T_NC}: $1"; echo -e "${T_RED}    Reason: ${2:-Unknown}${T_NC}"; }
assert_equals() { ((TOTAL_TESTS++)); if [ "$1" = "$2" ]; then pass "$3"; else fail "$3" "Expected '$1', got '$2'"; fi; }
assert_contains() { ((TOTAL_TESTS++)); if echo "$1" | grep -qF -- "$2"; then pass "$3"; else fail "$3" "Expected to find '$2'"; fi; }
assert_dir_exists() { ((TOTAL_TESTS++)); if [ -d "$1" ]; then pass "$2"; else fail "$2" "Dir missing: $1"; fi; }
assert_dir_absent() { ((TOTAL_TESTS++)); if [ ! -d "$1" ]; then pass "$2"; else fail "$2" "Dir should be gone: $1"; fi; }
strip_ansi() { printf '%b' "$1" | sed $'s/\033\[[0-9;]*m//g'; }

# make_cache <plugin> <ver...> — create a fixture cache with version dirs.
make_cache() {
    CACHE=$(mktemp -d)
    local plugin="$1"; shift
    for v in "$@"; do
        mkdir -p "$CACHE/$plugin/$v"
        echo "stub" > "$CACHE/$plugin/$v/plugin.json"
    done
}
destroy_cache() { [ -n "$CACHE" ] && [ -d "$CACHE" ] && rm -rf "$CACHE"; CACHE=""; }

run_prune() { CACHE_DIR="$CACHE" bash "$PRUNE_SCRIPT" "$@" 2>&1; }

# ----------------------------------------------------------------------------
test_dry_run_reports_but_keeps() {
    echo -e "${T_BLUE}[TEST]${T_NC} DRY-RUN: reports prunable versions but deletes nothing"
    make_cache scholar 2.17.0 2.18.1 2.19.0 2.20.0 2.22.0 2.24.0

    local output; output=$(run_prune)
    local stripped; stripped=$(strip_ansi "$output")

    assert_contains "$stripped" "2.17.0" "Reports oldest version as prunable"
    assert_contains "$stripped" "2.19.0" "Reports 3rd-oldest as prunable"
    # Nothing deleted in dry-run.
    assert_dir_exists "$CACHE/scholar/2.17.0" "Dry-run leaves old dir on disk"
    assert_dir_exists "$CACHE/scholar/2.24.0" "Dry-run leaves newest dir on disk"

    destroy_cache
}

test_prune_keeps_current_plus_two() {
    echo -e "${T_BLUE}[TEST]${T_NC} PRUNE: keeps current + 2 most recent (top 3), removes the rest"
    make_cache scholar 2.17.0 2.18.1 2.19.0 2.20.0 2.22.0 2.24.0

    local exit_code=0 output
    output=$(run_prune --prune) || exit_code=$?

    assert_equals "0" "$exit_code" "Prune exits 0"
    # Kept: top 3 by semver.
    assert_dir_exists "$CACHE/scholar/2.24.0" "Keeps 2.24.0 (current)"
    assert_dir_exists "$CACHE/scholar/2.22.0" "Keeps 2.22.0 (most recent -1)"
    assert_dir_exists "$CACHE/scholar/2.20.0" "Keeps 2.20.0 (most recent -2)"
    # Removed: the older 3.
    assert_dir_absent "$CACHE/scholar/2.19.0" "Removes 2.19.0"
    assert_dir_absent "$CACHE/scholar/2.18.1" "Removes 2.18.1"
    assert_dir_absent "$CACHE/scholar/2.17.0" "Removes 2.17.0"

    local stripped; stripped=$(strip_ansi "$output")
    assert_contains "$stripped" "2.17.0" "Reports what was removed (no silent delete)"

    destroy_cache
}

test_under_threshold_keeps_all() {
    echo -e "${T_BLUE}[TEST]${T_NC} KEEP: a plugin with <=3 versions loses nothing"
    make_cache craft 2.34.0 2.35.0 2.37.0

    run_prune --prune >/dev/null 2>&1
    assert_dir_exists "$CACHE/craft/2.34.0" "3-version plugin keeps oldest"
    assert_dir_exists "$CACHE/craft/2.37.0" "3-version plugin keeps newest"

    destroy_cache
}

test_json_mode() {
    echo -e "${T_BLUE}[TEST]${T_NC} JSON: --json emits valid output listing removals"
    make_cache scholar 2.17.0 2.18.1 2.19.0 2.20.0 2.22.0 2.24.0

    local output; output=$(run_prune --json)
    ((TOTAL_TESTS++))
    if echo "$output" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
        pass "JSON parses"
    else
        fail "JSON parses" "python3 json.load failed"
    fi
    assert_contains "$output" '"prunable"' "JSON has prunable field"

    destroy_cache
}

test_non_semver_dirs_never_pruned() {
    echo -e "${T_BLUE}[TEST]${T_NC} SAFETY: non-semver dirs (dev/backup) are ignored, real versions never pruned by junk-ranking"
    make_cache scholar 2.22.0 2.23.0 2.24.0
    # Junk dirs that `sort -rV` would rank ABOVE real versions, pushing the
    # newest real versions into the prunable tail (the data-loss bug).
    mkdir -p "$CACHE/scholar/dev" "$CACHE/scholar/backup"

    run_prune --prune >/dev/null 2>&1
    assert_dir_exists "$CACHE/scholar/2.24.0" "Newest real version survives (not pruned by junk-ranking)"
    assert_dir_exists "$CACHE/scholar/2.23.0" "2nd real version survives"
    assert_dir_exists "$CACHE/scholar/2.22.0" "3rd real version survives"
    assert_dir_exists "$CACHE/scholar/dev" "Non-semver 'dev' dir left untouched"
    assert_dir_exists "$CACHE/scholar/backup" "Non-semver 'backup' dir left untouched"

    destroy_cache
}

test_installed_version_never_pruned() {
    echo -e "${T_BLUE}[TEST]${T_NC} SAFETY: the installed (pinned) version survives even when older than newest 3"
    make_cache scholar 2.20.0 2.21.0 2.22.0 2.23.0 2.24.0
    local ip; ip=$(mktemp)
    echo '{"plugins": {"scholar@local-plugins": [{"version": "2.20.0"}]}}' > "$ip"

    INSTALLED_PLUGINS="$ip" CACHE_DIR="$CACHE" bash "$PRUNE_SCRIPT" --prune >/dev/null 2>&1
    assert_dir_exists "$CACHE/scholar/2.20.0" "Installed/pinned 2.20.0 survives prune"
    assert_dir_exists "$CACHE/scholar/2.24.0" "Newest version still kept"
    assert_dir_absent "$CACHE/scholar/2.21.0" "Non-installed old version 2.21.0 is pruned"
    rm -f "$ip"

    destroy_cache
}

print_summary() {
    echo ""
    echo -e "${T_BLUE}═══════════════════════════════════════════${T_NC}"
    echo -e "  Total: $TOTAL_TESTS  ${T_GREEN}Passed: $PASSED_TESTS${T_NC}  ${T_RED}Failed: $FAILED_TESTS${T_NC}"
    for n in "${FAILED_TEST_NAMES[@]:-}"; do [ -n "$n" ] && echo -e "  ${T_RED}✗${T_NC} $n"; done
}

main() {
    echo -e "${T_BLUE}cache-prune.sh Test Suite${T_NC}"
    test_dry_run_reports_but_keeps
    test_prune_keeps_current_plus_two
    test_under_threshold_keeps_all
    test_non_semver_dirs_never_pruned
    test_installed_version_never_pruned
    test_json_mode
    print_summary
    [ "$FAILED_TESTS" -gt 0 ] && exit 1 || exit 0
}

main "$@"
