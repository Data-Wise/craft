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
           SURFACES_GH_RELEASE_VERSION="${SURFACES_GH_RELEASE_VERSION-$SBX_VERSION}" \
           SURFACES_DOCS_SITE_VERSION="${SURFACES_DOCS_SITE_VERSION-$SBX_VERSION}" \
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

test_brew_leg_strips_cellar_revision_suffix() {
    echo -e "${T_BLUE}[TEST]${T_NC} BREW: a Cellar revision suffix (_N) is not a real mismatch"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    # `brew list --versions` reports the Cellar dir name, which carries a
    # trailing _N revision suffix on a rebuild-without-bump. "2.37.0_1" is
    # still v2.37.0 -- must align, not block.
    local exit_code=0 output
    output=$(SURFACES_BREW_VERSION="2.37.0_1" run_verify) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "0" "$exit_code" "Cellar-revision-suffixed brew version does not block"
    assert_contains "$stripped" "ALIGNED" "Report summarizes as ALIGNED"

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

test_cowork_mismatch_shows_releases_behind() {
    echo -e "${T_BLUE}[TEST]${T_NC} COWORK: quantified mismatch shows N release(s) behind (craft#199)"
    make_sandbox "2.40.0"; SBX_VERSION="2.40.0"
    git -C "$SANDBOX" init -q
    git -C "$SANDBOX" -c user.email=t@t -c user.name=t commit -q --allow-empty -m init
    for v in 2.36.0 2.37.0 2.38.0 2.39.0 2.40.0; do git -C "$SANDBOX" tag "v$v"; done

    local cowork_dir="$SANDBOX/cowork_plugins"
    mkdir -p "$cowork_dir"
    cat > "$cowork_dir/installed_plugins.json" <<'JSON'
{ "plugins": { "craft@my-mkt": [ { "version": "2.36.0" } ] } }
JSON

    local exit_code=0 output
    output=$(SURFACES_GIT_TAG="" SURFACES_COWORK_STORE="$cowork_dir" run_verify) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "0" "$exit_code" "Quantified cowork mismatch still does not block"
    assert_contains "$stripped" "4 release(s) behind" "Human report shows the releases-behind count"

    local json_output
    json_output=$(SURFACES_GIT_TAG="" SURFACES_COWORK_STORE="$cowork_dir" run_verify --json)
    assert_contains "$json_output" '"releasesBehind": 4' "JSON carries releasesBehind on the cowork leg"

    destroy_sandbox
}

test_cowork_aligned_has_no_releases_behind() {
    echo -e "${T_BLUE}[TEST]${T_NC} COWORK: aligned cowork leg reports releasesBehind null, no count in human output"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    local cowork_dir="$SANDBOX/cowork_plugins"
    mkdir -p "$cowork_dir"
    cat > "$cowork_dir/installed_plugins.json" <<'JSON'
{ "plugins": { "craft@my-mkt": [ { "version": "2.37.0" } ] } }
JSON

    local output
    output=$(SURFACES_COWORK_STORE="$cowork_dir" run_verify)
    local stripped; stripped=$(strip_ansi "$output")
    assert_not_contains "$stripped" "release(s) behind" "Aligned cowork leg shows no releases-behind note"

    local json_output
    json_output=$(SURFACES_COWORK_STORE="$cowork_dir" run_verify --json)
    assert_contains "$json_output" '"releasesBehind": null' "JSON reports releasesBehind null when aligned"

    destroy_sandbox
}

test_cowork_recover_script_reports_no_store() {
    echo -e "${T_BLUE}[TEST]${T_NC} COWORK-RECOVER: no Cowork store on this machine -> exit 0, no drift claimed"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    local exit_code=0 output
    output=$(SURFACES_COWORK_STORE="$SANDBOX/no-such-store" bash "$PROJECT_ROOT/scripts/cowork-recover.sh" "$SANDBOX" 2>&1) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "0" "$exit_code" "No Cowork store -> exit 0"
    assert_contains "$stripped" "nothing to recover" "Reports nothing to recover"

    destroy_sandbox
}

test_cowork_recover_script_prints_manual_steps_on_drift() {
    echo -e "${T_BLUE}[TEST]${T_NC} COWORK-RECOVER: drift -> exit 1 + the 5 manual recovery steps"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    local cowork_dir="$SANDBOX/cowork_plugins"
    mkdir -p "$cowork_dir"
    cat > "$cowork_dir/installed_plugins.json" <<'JSON'
{ "plugins": { "craft@my-mkt": [ { "version": "1.8.0" } ] } }
JSON

    local exit_code=0 output
    output=$(SURFACES_COWORK_STORE="$cowork_dir" bash "$PROJECT_ROOT/scripts/cowork-recover.sh" "$SANDBOX" 2>&1) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "1" "$exit_code" "Drifted Cowork install exits 1"
    assert_contains "$stripped" "Uninstall it" "Recovery steps mention uninstall"
    assert_contains "$stripped" "Cmd-Q" "Recovery steps mention the full Cmd-Q relaunch"

    destroy_sandbox
}

test_cowork_recover_script_aligned_is_noop() {
    echo -e "${T_BLUE}[TEST]${T_NC} COWORK-RECOVER: aligned install -> exit 0, nothing to do"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    local cowork_dir="$SANDBOX/cowork_plugins"
    mkdir -p "$cowork_dir"
    cat > "$cowork_dir/installed_plugins.json" <<'JSON'
{ "plugins": { "craft@my-mkt": [ { "version": "2.37.0" } ] } }
JSON

    local exit_code=0 output
    output=$(SURFACES_COWORK_STORE="$cowork_dir" bash "$PROJECT_ROOT/scripts/cowork-recover.sh" "$SANDBOX" 2>&1) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "0" "$exit_code" "Aligned Cowork install exits 0"
    assert_contains "$stripped" "Nothing to do" "Reports nothing to do"

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
           SURFACES_GH_RELEASE_VERSION="2.37.0" \
           SURFACES_DOCS_SITE_VERSION="2.37.0" \
           HOME="$fake_home" \
           bash "$VERIFY_SCRIPT" 2>&1 ) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "0" "$exit_code" "Cowork glob at depth 4 exits 0"
    assert_contains "$stripped" "cowork" "Cowork leg appears in report (glob found it)"

    destroy_sandbox
}

test_report_only_never_blocks() {
    echo -e "${T_BLUE}[TEST]${T_NC} REPORT-ONLY: mismatch still DRIFTS but never exits 1"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    # Same planted mismatch (stale brew) exercised in test_mismatch_blocks.
    local default_exit=0 default_output
    default_output=$(SURFACES_TAP_FORMULA="" SURFACES_BREW_VERSION="2.36.0" run_verify) || default_exit=$?
    local ro_exit=0 ro_output
    ro_output=$(SURFACES_TAP_FORMULA="" SURFACES_BREW_VERSION="2.36.0" run_verify --report-only) || ro_exit=$?
    local ro_stripped; ro_stripped=$(strip_ansi "$ro_output")

    assert_equals "1" "$default_exit" "Default mode still exits 1 for the same planted mismatch"
    assert_equals "0" "$ro_exit" "--report-only exits 0 for the same planted mismatch"
    assert_contains "$ro_stripped" "DRIFTED" "--report-only prints DRIFTED for the mismatched leg"
    assert_contains "$ro_stripped" "brew-installed" "--report-only report names the drifted leg"

    destroy_sandbox
}

test_report_only_all_legs_aligned() {
    echo -e "${T_BLUE}[TEST]${T_NC} REPORT-ONLY: fully-aligned sandbox prints ALIGNED per surface, exit 0"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    local exit_code=0 output
    output=$(run_verify --report-only) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "0" "$exit_code" "--report-only exits 0 when fully aligned"
    assert_contains "$stripped" "ALIGNED" "--report-only prints ALIGNED for matching legs"
    assert_not_contains "$stripped" "DRIFTED" "No DRIFTED line when nothing mismatched"

    destroy_sandbox
}

test_github_release_leg_aligned_and_drifted() {
    echo -e "${T_BLUE}[TEST]${T_NC} GITHUB RELEASE leg: aligned + drifted, injectable via SURFACES_GH_RELEASE_VERSION"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    local exit_code=0 output
    output=$(run_verify) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")
    assert_equals "0" "$exit_code" "Aligned github-release leg does not block"
    assert_contains "$stripped" "github release" "Report lists the github-release leg"

    local drift_exit=0 drift_output
    drift_output=$(SURFACES_GH_RELEASE_VERSION="2.36.0" run_verify) || drift_exit=$?
    local drift_stripped; drift_stripped=$(strip_ansi "$drift_output")
    assert_equals "1" "$drift_exit" "Stale github-release leg blocks (exit 1)"
    assert_contains "$drift_stripped" "MISMATCH" "Report flags the github-release mismatch"

    destroy_sandbox
}

test_docs_site_leg_aligned_and_drifted() {
    echo -e "${T_BLUE}[TEST]${T_NC} DOCS SITE leg: aligned + drifted, injectable via SURFACES_DOCS_SITE_VERSION"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    local exit_code=0 output
    output=$(run_verify) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")
    assert_equals "0" "$exit_code" "Aligned docs-site leg does not block"
    assert_contains "$stripped" "docs site" "Report lists the docs-site leg"

    local drift_exit=0 drift_output
    drift_output=$(SURFACES_DOCS_SITE_VERSION="2.36.0" run_verify) || drift_exit=$?
    local drift_stripped; drift_stripped=$(strip_ansi "$drift_output")
    assert_equals "1" "$drift_exit" "Stale docs-site leg blocks (exit 1)"
    assert_contains "$drift_stripped" "MISMATCH" "Report flags the docs-site mismatch"

    destroy_sandbox
}

test_docs_site_leg_ignores_historical_version_prose() {
    echo -e "${T_BLUE}[TEST]${T_NC} DOCS SITE leg: regression for the bare-vX.Y.Z false-positive (craft PR #308 bug class)"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    # Fixture reproduces docs/index.md's actual failure shape: a historical
    # "since vX.Y.Z" mention and a versioned site_description meta tag both
    # render BEFORE the real version badge in page order. A bare `grep -o
    # 'v[0-9]+\.[0-9]+\.[0-9]+' | head -1` (the pre-fix pattern in docs.yml
    # and verify-surfaces.sh's resolve_docs_site) matches the historical
    # v2.0.0 mention instead of the real badge — exactly the bug that
    # false-positived scripts/pre-release-check.sh's docs/index.md check for
    # v4.2.0 and v4.3.0. resolve_docs_site must anchor to the version BADGE
    # (version-X.Y.Z) so it extracts 2.37.0, not 2.0.0.
    cat > "$SANDBOX/docs_site_fixture.html" <<'HTML'
<html><head>
<meta name="description" content="Full-stack toolkit. v2.0.0 adds a feature. See NEWS.md.">
</head><body>
<p>Docs authoring moved to folio since v2.0.0.</p>
<p><a href="..."><img alt="Version" src="https://img.shields.io/badge/version-2.37.0-brightgreen.svg" /></a></p>
</body></html>
HTML

    # Use --report-only so the per-leg ALIGNED/DRIFTED/ABSENT word is printed
    # explicitly (see printf '  %-16s %s\n' above resolve_docs_site's caller).
    # A bare exit-code-0 assertion alone would pass vacuously if curl (or its
    # file:// support) were unavailable and resolve_docs_site silently
    # returned empty — "absent" doesn't block, so exit 0 proves nothing on
    # its own. Asserting the docs-site row explicitly reads ALIGNED (not
    # ABSENT) proves the badge was actually resolved and matched 2.37.0, not
    # that the leg silently degraded.
    local exit_code=0 output
    output=$(SURFACES_DOCS_SITE_VERSION="" \
        SURFACES_DOCS_SITE_URL="file://$SANDBOX/docs_site_fixture.html" \
        run_verify --report-only) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "0" "$exit_code" "--report-only never blocks"
    assert_contains "$stripped" "docs site        ALIGNED" \
        "docs-site leg resolves the real badge (2.37.0) — historical v2.0.0 prose is NOT picked up, and the leg did not silently go ABSENT"

    destroy_sandbox
}

test_docs_site_leg_absent_when_no_badge_present() {
    echo -e "${T_BLUE}[TEST]${T_NC} DOCS SITE leg: no version badge on the page -> ABSENT (warn-only), not a false match"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    # Companion to the false-positive regression above: if the page has
    # historical version prose but the badge itself is missing (markup
    # change, badge removed, render failure), resolve_docs_site's anchored
    # grep correctly finds nothing rather than falling back to matching the
    # historical prose. This is a real (if narrow) behavior change from the
    # pre-fix bare grep, which would have "found" v2.0.0 here and, by luck,
    # sometimes been wrong and sometimes right. Anchored-but-silent is the
    # safer failure mode: the leg reports ABSENT (warn, does not block)
    # instead of asserting a value that might be stale prose.
    cat > "$SANDBOX/no_badge_fixture.html" <<'HTML'
<html><head>
<meta name="description" content="Full-stack toolkit. v2.0.0 adds a feature.">
</head><body>
<p>Docs authoring moved to folio since v2.0.0.</p>
</body></html>
HTML

    local exit_code=0 output
    output=$(SURFACES_DOCS_SITE_VERSION="" \
        SURFACES_DOCS_SITE_URL="file://$SANDBOX/no_badge_fixture.html" \
        run_verify --report-only) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "0" "$exit_code" "Absent docs-site leg does not block even without --report-only's blanket no-block"
    assert_contains "$stripped" "docs site        ABSENT" \
        "No badge on the page -> leg reports ABSENT, never falls back to matching historical prose"

    destroy_sandbox
}

test_version_flag_overrides_target() {
    echo -e "${T_BLUE}[TEST]${T_NC} --version: diagnoses a DIFFERENT version than plugin.json's current one"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    # All fixtures are pinned at 2.37.0 (from make_sandbox). Asking the script
    # to check against --version 2.36.0 instead must now report every leg as
    # a MISMATCH against that overridden target, proving --version actually
    # changed what's being compared (not just cosmetic header text).
    local exit_code=0 output
    output=$(run_verify --version 2.36.0) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "1" "$exit_code" "Fixtures at 2.37.0 mismatch an overridden --version 2.36.0 target"
    assert_contains "$stripped" "Surfaces for craft v2.36.0" "Header reflects the --version override, not plugin.json"
    assert_contains "$stripped" "MISMATCH" "Legs now compare against the overridden version"

    # Sanity: a --version matching the fixtures' actual version still aligns.
    local match_exit=0 match_output
    match_output=$(run_verify --version 2.37.0) || match_exit=$?
    assert_equals "0" "$match_exit" "--version matching the real fixture version still exits 0"

    destroy_sandbox
}

test_version_flag_with_report_only() {
    echo -e "${T_BLUE}[TEST]${T_NC} --report-only --version: diagnose a past release without blocking"
    make_sandbox "2.37.0"; SBX_VERSION="2.37.0"

    local exit_code=0 output
    output=$(run_verify --report-only --version 2.36.0) || exit_code=$?
    local stripped; stripped=$(strip_ansi "$output")

    assert_equals "0" "$exit_code" "--report-only --version never blocks even on a full mismatch"
    assert_contains "$stripped" "DRIFTED" "Combined flags still surface DRIFTED legs"

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
    test_brew_leg_strips_cellar_revision_suffix
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
    # craft#199 reopen: quantified Cowork WARN + cowork-recover.sh
    test_cowork_mismatch_shows_releases_behind
    test_cowork_aligned_has_no_releases_behind
    test_cowork_recover_script_reports_no_store
    test_cowork_recover_script_prints_manual_steps_on_drift
    test_cowork_recover_script_aligned_is_noop
    test_aggregator_name_mismatch_blocks
    test_aggregator_correct_name_and_version_passes
    test_cowork_glob_maxdepth
    # Phase 2 additions: --report-only, --version, github-release + docs-site legs
    test_report_only_never_blocks
    test_report_only_all_legs_aligned
    test_github_release_leg_aligned_and_drifted
    test_docs_site_leg_aligned_and_drifted
    test_docs_site_leg_ignores_historical_version_prose
    test_docs_site_leg_absent_when_no_badge_present
    test_version_flag_overrides_target
    test_version_flag_with_report_only
    print_summary
    [ "$FAILED_TESTS" -gt 0 ] && exit 1 || exit 0
}

main "$@"
