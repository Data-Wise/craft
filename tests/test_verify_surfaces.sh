#!/usr/bin/env bash
#
# Test Suite for scripts/verify-surfaces.sh
#
# verify-surfaces asserts one version across every surface craft controls
# (plugin.json == marketplace.json == git tag == tap formula == brew-installed
# == Code-registered) and warns — never blocks — on the Desktop leg.
#
# Behavior contract (spec D1/D2 + absent-leg decision):
#   - present + match    -> ✅ aligned
#   - present + mismatch -> ❌ BLOCK (exit 1)  [craft-controlled legs only]
#   - absent/unreadable  -> ⚠️ warn (does NOT block)
#   - Desktop/Cowork     -> ⚠️ warn (manual, never auto-verifiable)
#
# External version sources are injected via SURFACES_* env vars so tests run
# against fixtures instead of the live machine.
#
# Usage:
#   ./tests/test_verify_surfaces.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VERIFY_SCRIPT="$PROJECT_ROOT/scripts/verify-surfaces.sh"

T_RED='\033[0;31m'
T_GREEN='\033[0;32m'
T_YELLOW='\033[1;33m'
T_BLUE='\033[0;34m'
T_NC='\033[0m'

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
declare -a FAILED_TEST_NAMES=()

SANDBOX=""

# ----------------------------------------------------------------------------
# Assertions
# ----------------------------------------------------------------------------
pass() { ((PASSED_TESTS++)); echo -e "${T_GREEN}  ✓ PASS${T_NC}: $1"; }
fail() {
    ((FAILED_TESTS++))
    FAILED_TEST_NAMES+=("$1: ${2:-}")
    echo -e "${T_RED}  ✗ FAIL${T_NC}: $1"
    echo -e "${T_RED}    Reason: ${2:-Unknown}${T_NC}"
}

assert_equals() {
    ((TOTAL_TESTS++))
    if [ "$1" = "$2" ]; then pass "$3"; else fail "$3" "Expected '$1', got '$2'"; fi
}

assert_contains() {
    ((TOTAL_TESTS++))
    if echo "$1" | grep -qF -- "$2"; then pass "$3"; else fail "$3" "Expected to find '$2' in output"; fi
}

assert_not_contains() {
    ((TOTAL_TESTS++))
    if echo "$1" | grep -qF -- "$2"; then fail "$3" "Did not expect '$2' in output"; else pass "$3"; fi
}

strip_ansi() { printf '%b' "$1" | sed $'s/\033\[[0-9;]*m//g'; }

# ----------------------------------------------------------------------------
# Sandbox: a fake plugin repo + injectable external sources
# ----------------------------------------------------------------------------
# make_sandbox <version> — builds a fully-aligned plugin at <version>.
# Individual legs are then overridden per-test via env vars.
make_sandbox() {
    local version="$1"
    SANDBOX=$(mktemp -d)
    mkdir -p "$SANDBOX/.claude-plugin"

    cat > "$SANDBOX/.claude-plugin/plugin.json" <<JSON
{ "name": "craft", "version": "${version}", "description": "test" }
JSON

    cat > "$SANDBOX/.claude-plugin/marketplace.json" <<JSON
{ "metadata": { "version": "${version}" }, "plugins": [{ "name": "craft", "version": "${version}" }] }
JSON

    # Fixture tap formula (homebrew-tap Formula/craft.rb url carries the version)
    cat > "$SANDBOX/craft.rb" <<RUBY
class Craft < Formula
  desc "test"
  homepage "https://github.com/Data-Wise/craft"
  url "https://github.com/Data-Wise/craft/archive/refs/tags/v${version}.tar.gz"
end
RUBY

    # Fixture Code-registered store
    cat > "$SANDBOX/installed_plugins.json" <<JSON
{ "version": 2, "plugins": { "craft@local-plugins": [ { "version": "${version}" } ] } }
JSON
}

destroy_sandbox() {
    [ -n "$SANDBOX" ] && [ -d "$SANDBOX" ] && rm -rf "$SANDBOX"
    SANDBOX=""
}

# run_verify [extra args...] — runs verify-surfaces in the sandbox with all
# external legs pointed at fixtures (overridable by exporting before calling).
run_verify() {
    ( cd "$SANDBOX" \
        && SURFACES_GIT_TAG="${SURFACES_GIT_TAG-v${SBX_VERSION}}" \
           SURFACES_TAP_FORMULA="${SURFACES_TAP_FORMULA-$SANDBOX/craft.rb}" \
           SURFACES_BREW_VERSION="${SURFACES_BREW_VERSION-$SBX_VERSION}" \
           SURFACES_INSTALLED_PLUGINS="${SURFACES_INSTALLED_PLUGINS-$SANDBOX/installed_plugins.json}" \
           SURFACES_COWORK_STORE="${SURFACES_COWORK_STORE-/nonexistent/cowork_store}" \
           bash "$VERIFY_SCRIPT" "$@" 2>&1 )
}

# ----------------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------------
test_all_aligned_passes() {
    echo -e "${T_BLUE}[TEST]${T_NC} ALIGNED: every craft leg matches -> exit 0"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    local exit_code=0 output
    output=$(run_verify) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "0" "$exit_code" "All-aligned exits 0"
    assert_contains "$stripped" "Surfaces for craft v2.37.0" "Report has surfaces header"
    assert_contains "$stripped" "marketplace" "Report lists marketplace leg"
    assert_contains "$stripped" "git tag" "Report lists git tag leg"
    assert_contains "$stripped" "brew" "Report lists brew leg"
    assert_contains "$stripped" "Code" "Report lists Code-registered leg"

    destroy_sandbox
}

test_mismatch_blocks() {
    echo -e "${T_BLUE}[TEST]${T_NC} BLOCK: a craft leg present-but-mismatched -> exit 1"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    # Force the tap formula leg to the PREVIOUS version (real, present, wrong).
    local exit_code=0 output
    output=$(SURFACES_TAP_FORMULA="" SURFACES_BREW_VERSION="2.36.0" run_verify) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "1" "$exit_code" "Mismatched craft leg blocks (exit 1)"
    assert_contains "$stripped" "MISMATCH" "Report flags the mismatch"
    assert_contains "$stripped" "BLOCKED" "Report summarizes as BLOCKED"

    destroy_sandbox
}

test_absent_leg_warns_not_block() {
    echo -e "${T_BLUE}[TEST]${T_NC} WARN: an absent craft leg warns but does NOT block"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    # Point the Code-registered store at a non-existent path (absent leg).
    local exit_code=0 output
    output=$(SURFACES_INSTALLED_PLUGINS="$SANDBOX/does-not-exist.json" run_verify) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "0" "$exit_code" "Absent leg does not block (exit 0)"
    assert_contains "$stripped" "not verified" "Absent leg reported as not verified"
    assert_contains "$stripped" "ALIGNED" "Summary still ALIGNED (absent != mismatch)"

    destroy_sandbox
}

test_desktop_is_warn_only() {
    echo -e "${T_BLUE}[TEST]${T_NC} DESKTOP: Desktop leg is always a manual warn"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    local exit_code=0 output
    output=$(run_verify --aggregator Data-Wise/claude-plugins) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "0" "$exit_code" "Desktop warn does not affect exit code"
    assert_contains "$stripped" "Desktop/Cowork" "Report lists Desktop/Cowork surface"
    assert_contains "$stripped" "marketplace add Data-Wise/claude-plugins" "Desktop add step uses aggregator"

    destroy_sandbox
}

test_aggregator_leg_aligned() {
    echo -e "${T_BLUE}[TEST]${T_NC} AGGREGATOR: matching aggregator entry -> aligned, exit 0"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"
    cat > "$SANDBOX/aggregator.json" <<'JSON'
{ "name": "data-wise", "plugins": [
  { "name": "scholar", "version": "3.1.0" },
  { "name": "craft", "version": "2.37.0" }
] }
JSON
    local exit_code=0 output
    output=$(SURFACES_AGGREGATOR_FILE="$SANDBOX/aggregator.json" run_verify) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "0" "$exit_code" "Matching aggregator entry exits 0"
    assert_contains "$stripped" "aggregator" "Report lists the aggregator leg"
    assert_contains "$stripped" "ALIGNED" "Summary ALIGNED when aggregator matches"

    destroy_sandbox
}

test_aggregator_leg_mismatch_blocks() {
    echo -e "${T_BLUE}[TEST]${T_NC} AGGREGATOR: stale aggregator entry -> BLOCK (D5 drift guard)"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"
    cat > "$SANDBOX/aggregator.json" <<'JSON'
{ "name": "data-wise", "plugins": [ { "name": "craft", "version": "2.36.0" } ] }
JSON
    local exit_code=0 output
    output=$(SURFACES_AGGREGATOR_FILE="$SANDBOX/aggregator.json" run_verify) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "1" "$exit_code" "Stale aggregator entry blocks (exit 1)"
    assert_contains "$stripped" "aggregator" "Report names the aggregator leg"
    assert_contains "$stripped" "BLOCKED" "Summary BLOCKED on aggregator drift"

    destroy_sandbox
}

test_aggregator_absent_warns_not_block() {
    echo -e "${T_BLUE}[TEST]${T_NC} AGGREGATOR: requested-but-missing file warns, does NOT block"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    local exit_code=0 output
    output=$(SURFACES_AGGREGATOR_FILE="$SANDBOX/missing-aggregator.json" run_verify) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "0" "$exit_code" "Missing aggregator file does not block"
    assert_contains "$stripped" "ALIGNED" "Summary still ALIGNED (absent aggregator != drift)"

    destroy_sandbox
}

test_no_aggregator_leg_when_unconfigured() {
    echo -e "${T_BLUE}[TEST]${T_NC} AGGREGATOR: leg is omitted entirely when not configured"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    local output; output=$(run_verify)
    local stripped; stripped=$(strip_ansi "$output")
    assert_not_contains "$stripped" "aggregator" "No aggregator leg shown when unconfigured"

    destroy_sandbox
}

test_write_status_matrix() {
    echo -e "${T_BLUE}[TEST]${T_NC} STATUS: --write-status writes the surfaces matrix to .STATUS"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"
    cat > "$SANDBOX/.STATUS" <<'STS'
status: Active
version: 2.37.0
STS

    local exit_code=0
    run_verify --write-status >/dev/null 2>&1 || exit_code=$?
    local status_content; status_content=$(cat "$SANDBOX/.STATUS")

    assert_equals "0" "$exit_code" "Aligned --write-status exits 0"
    assert_contains "$status_content" "## Surfaces" "STATUS gains a Surfaces section"
    assert_contains "$status_content" "craft" "Surfaces matrix lists the plugin"
    assert_contains "$status_content" "2.37.0" "Surfaces matrix carries the version"
    assert_contains "$status_content" "status: Active" "Pre-existing .STATUS content preserved"

    # Idempotent: a second write must not duplicate the section.
    run_verify --write-status >/dev/null 2>&1
    local count
    count=$(grep -c "## Surfaces" "$SANDBOX/.STATUS")
    assert_equals "1" "$count" "Surfaces section is not duplicated on re-run"

    destroy_sandbox
}

test_json_mode() {
    echo -e "${T_BLUE}[TEST]${T_NC} JSON: --json emits valid machine-readable output"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    local output
    output=$(SURFACES_BREW_VERSION="2.36.0" run_verify --json)

    ((TOTAL_TESTS++))
    if echo "$output" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
        pass "JSON output parses"
    else
        fail "JSON output parses" "python3 json.load failed"
    fi
    assert_contains "$output" '"blocked": true' "JSON marks blocked true on mismatch"
    assert_contains "$output" '"version": "2.37.0"' "JSON carries source-of-truth version"

    destroy_sandbox
}

# ----------------------------------------------------------------------------
test_git_tag_leg_detects_lagging_tag() {
    echo -e "${T_BLUE}[TEST]${T_NC} GIT TAG: a tag lagging plugin.json is a real mismatch (not silent 'absent')"
    make_sandbox "2.38.0"; SBX_VERSION="2.38.0"
    # Real repo whose newest tag (v2.37.0) lags plugin.json (2.38.0). This
    # exercises the REAL resolver (no SURFACES_GIT_TAG injection) — the old
    # `tag --list "v${SOT}"` could only return absent/ok here, never mismatch.
    git -C "$SANDBOX" init -q
    git -C "$SANDBOX" -c user.email=t@t -c user.name=t commit -q --allow-empty -m init
    git -C "$SANDBOX" tag v2.36.0
    git -C "$SANDBOX" tag v2.37.0

    local exit_code=0 output
    output=$(SURFACES_GIT_TAG="" run_verify) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "1" "$exit_code" "Lagging git tag (2.37.0 < plugin 2.38.0) blocks (exit 1)"
    assert_contains "$stripped" "MISMATCH" "Report flags the git-tag mismatch"
    assert_contains "$stripped" "2.37.0" "git-tag leg reports the latest real tag, not the SOT"

    destroy_sandbox
}

test_corrupt_marketplace_blocks() {
    echo -e "${T_BLUE}[TEST]${T_NC} CORRUPT: an unparseable craft-controlled surface blocks (not a silent warn)"
    make_sandbox "2.38.1"; SBX_VERSION="2.38.1"
    # Present-but-unparseable marketplace.json — must NOT read as "absent → warn".
    echo '{ not valid json' > "$SANDBOX/.claude-plugin/marketplace.json"

    local exit_code=0 output
    output=$(run_verify) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "1" "$exit_code" "Corrupt marketplace blocks (exit 1)"
    assert_contains "$stripped" "CORRUPT" "Report flags the corrupt surface as blocking"

    destroy_sandbox
}

test_cowork_mismatch_is_warn_only() {
    echo -e "${T_BLUE}[TEST]${T_NC} COWORK: Cowork mismatch -> WARN only, never blocks (exit 0)"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    # Cowork store: wrong version but all BLOCK legs aligned.
    local cowork_dir="$SANDBOX/cowork_plugins"
    mkdir -p "$cowork_dir"
    cat > "$cowork_dir/known_marketplaces.json" <<'JSON'
{ "my-mkt": { "source": { "source": "github", "repo": "Data-Wise/craft" } } }
JSON
    cat > "$cowork_dir/installed_plugins.json" <<JSON
{ "plugins": { "craft@my-mkt": [ { "version": "2.36.0" } ] } }
JSON

    local exit_code=0 output
    output=$(SURFACES_COWORK_STORE="$cowork_dir" run_verify) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "0" "$exit_code" "Cowork mismatch must NOT block (exit 0)"
    assert_contains "$stripped" "cowork" "Report lists the cowork leg"
    assert_contains "$stripped" "ALIGNED" "Summary still ALIGNED (cowork is warn-only)"

    destroy_sandbox
}

test_cowork_absent_is_warn_not_block() {
    echo -e "${T_BLUE}[TEST]${T_NC} COWORK: absent cowork store -> warn, not block"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    local exit_code=0 output
    output=$(SURFACES_COWORK_STORE="$SANDBOX/no-such-cowork-store" run_verify) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "0" "$exit_code" "Absent cowork store does not block"
    assert_contains "$stripped" "ALIGNED" "Summary ALIGNED with absent cowork"

    destroy_sandbox
}

test_aggregator_name_mismatch_blocks() {
    echo -e "${T_BLUE}[TEST]${T_NC} AGGREGATOR NAME: aggregator entry with wrong name -> BLOCK"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"
    cat > "$SANDBOX/aggregator.json" <<'JSON'
{ "name": "data-wise", "plugins": [ { "name": "WRONG-NAME", "version": "2.37.0" } ] }
JSON
    local exit_code=0 output
    output=$(SURFACES_AGGREGATOR_FILE="$SANDBOX/aggregator.json" run_verify) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "1" "$exit_code" "Aggregator name mismatch blocks (exit 1)"
    assert_contains "$stripped" "BLOCKED" "Summary BLOCKED on aggregator name mismatch"

    destroy_sandbox
}

test_aggregator_correct_name_and_version_passes() {
    echo -e "${T_BLUE}[TEST]${T_NC} AGGREGATOR NAME: correct name + version -> exit 0"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"
    cat > "$SANDBOX/aggregator.json" <<'JSON'
{ "name": "data-wise", "plugins": [ { "name": "craft", "version": "2.37.0" } ] }
JSON
    local exit_code=0 output
    output=$(SURFACES_AGGREGATOR_FILE="$SANDBOX/aggregator.json" run_verify) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "0" "$exit_code" "Correct aggregator name + version exits 0"
    assert_contains "$stripped" "ALIGNED" "Summary ALIGNED on correct name + version"

    destroy_sandbox
}

test_cowork_glob_maxdepth() {
    echo -e "${T_BLUE}[TEST]${T_NC} COWORK GLOB: live glob finds file at depth 4 (/*/*/cowork_plugins/installed_plugins.json)"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    # Build the nested structure under a fake HOME to exercise the real find path
    local fake_home="$SANDBOX/fake_home"
    local sessions_dir="$fake_home/Library/Application Support/Claude/local-agent-mode-sessions"
    local cowork_dir="$sessions_dir/session-a/subdir-b/cowork_plugins"
    mkdir -p "$cowork_dir"
    cat > "$cowork_dir/installed_plugins.json" <<JSON
{ "plugins": { "craft@test-mkt": [ { "version": "2.37.0" } ] } }
JSON

    # Run WITHOUT SURFACES_COWORK_STORE so the glob path is exercised.
    # Override HOME to point at our fixture tree; unset SURFACES_COWORK_STORE.
    local exit_code=0 output
    output=$( cd "$SANDBOX" \
        && SURFACES_GIT_TAG="v2.37.0" \
           SURFACES_TAP_FORMULA="$SANDBOX/craft.rb" \
           SURFACES_BREW_VERSION="2.37.0" \
           SURFACES_INSTALLED_PLUGINS="$SANDBOX/installed_plugins.json" \
           HOME="$fake_home" \
           bash "$VERIFY_SCRIPT" 2>&1 ) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "0" "$exit_code" "Cowork glob at depth 4 exits 0"
    assert_contains "$stripped" "cowork" "Cowork leg appears in report (glob found it)"

    destroy_sandbox
}

print_summary() {
    echo ""
    echo -e "${T_BLUE}═══════════════════════════════════════════${T_NC}"
    echo -e "  Total: $TOTAL_TESTS  ${T_GREEN}Passed: $PASSED_TESTS${T_NC}  ${T_RED}Failed: $FAILED_TESTS${T_NC}"
    if [ ${#FAILED_TEST_NAMES[@]} -gt 0 ]; then
        for n in "${FAILED_TEST_NAMES[@]}"; do echo -e "  ${T_RED}✗${T_NC} $n"; done
    fi
}

main() {
    echo -e "${T_BLUE}verify-surfaces.sh Test Suite${T_NC}"
    test_all_aligned_passes
    test_mismatch_blocks
    test_absent_leg_warns_not_block
    test_desktop_is_warn_only
    test_aggregator_leg_aligned
    test_aggregator_leg_mismatch_blocks
    test_aggregator_absent_warns_not_block
    test_no_aggregator_leg_when_unconfigured
    test_write_status_matrix
    test_git_tag_leg_detects_lagging_tag
    test_corrupt_marketplace_blocks
    test_json_mode
    # Task 2 additions
    test_cowork_mismatch_is_warn_only
    test_cowork_absent_is_warn_not_block
    test_aggregator_name_mismatch_blocks
    test_aggregator_correct_name_and_version_passes
    test_cowork_glob_maxdepth
    print_summary
    [ "$FAILED_TESTS" -gt 0 ] && exit 1 || exit 0
}

main "$@"
