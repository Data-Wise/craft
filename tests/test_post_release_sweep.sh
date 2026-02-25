#!/usr/bin/env bash
#
# Test Suite for scripts/post-release-sweep.sh
# Tests: clean repo, stale detection, --fix, --dry-run, --json
#
# Usage:
#   ./tests/test_post_release_sweep.sh              # Run all tests
#   ./tests/test_post_release_sweep.sh unit         # Run unit tests only
#   ./tests/test_post_release_sweep.sh integration  # Run integration tests only

set -uo pipefail

# Test configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SWEEP_SCRIPT="$PROJECT_ROOT/scripts/post-release-sweep.sh"

# Color output
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

SANDBOX=""

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
    if echo "$haystack" | grep -qF -- "$needle"; then
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
    if echo "$haystack" | grep -qF -- "$needle"; then
        fail "$test_name" "Did not expect to find '$needle' in output"
    else
        pass "$test_name"
    fi
}

assert_exit_code() {
    local expected="$1"
    local actual="$2"
    local test_name="$3"

    ((TOTAL_TESTS++))
    if [ "$expected" = "$actual" ]; then
        pass "$test_name"
    else
        fail "$test_name" "Expected exit code $expected, got $actual"
    fi
}

strip_ansi() {
    printf '%b' "$1" | sed $'s/\033\[[0-9;]*m//g'
}

# ============================================================================
# Sandbox Setup/Teardown
# ============================================================================

create_sandbox() {
    SANDBOX=$(mktemp -d)
    mkdir -p "$SANDBOX/.claude-plugin"
    mkdir -p "$SANDBOX/scripts"
    mkdir -p "$SANDBOX/docs/reference"
    mkdir -p "$SANDBOX/docs/guide"
    mkdir -p "$SANDBOX/commands/test"
    mkdir -p "$SANDBOX/skills/test"
    mkdir -p "$SANDBOX/agents"
    mkdir -p "$SANDBOX/docs/specs"

    # Copy required scripts
    cp "$PROJECT_ROOT/scripts/post-release-sweep.sh" "$SANDBOX/scripts/"
    cp "$PROJECT_ROOT/scripts/bump-version.sh" "$SANDBOX/scripts/"
    cp "$PROJECT_ROOT/scripts/bump-version-helper.py" "$SANDBOX/scripts/"
    cp "$PROJECT_ROOT/scripts/formatting.sh" "$SANDBOX/scripts/"

    # Create mock command/skill/agent files
    echo "---" > "$SANDBOX/commands/test/cmd1.md"
    echo "---" > "$SANDBOX/skills/test/SKILL.md"
    echo "---" > "$SANDBOX/agents/agent1.md"
    echo "---" > "$SANDBOX/docs/specs/SPEC-test-2026.md"

    # Create mock plugin.json (version 2.1.0 — prev version 2.0.0 works cleanly)
    cat > "$SANDBOX/.claude-plugin/plugin.json" <<'PJSON'
{
  "name": "test-plugin",
  "version": "2.1.0",
  "description": "Test plugin with 1 commands, 1 agents, 1 skills"
}
PJSON

    # Create mock marketplace.json
    cat > "$SANDBOX/.claude-plugin/marketplace.json" <<'MJSON'
{
  "metadata": { "version": "2.1.0" },
  "plugins": [{ "version": "2.1.0" }]
}
MJSON

    # Create mock package.json
    cat > "$SANDBOX/package.json" <<'PKG'
{ "name": "test-plugin", "version": "2.1.0" }
PKG

    # Create mock CLAUDE.md (consistent with 2.1.0)
    cat > "$SANDBOX/CLAUDE.md" <<'CMD'
# Test Plugin
**Current Version:** v2.1.0 | **Tests:** 50 tests passing
**1 commands** · **1 skills** · **1 agents**
CMD

    # Create mock README.md
    cat > "$SANDBOX/README.md" <<'RMD'
# Test Plugin
![version](https://img.shields.io/badge/version-2.1.0-blue)
**1 commands** · **1 skills** · **1 agents**
1 commands, 1 agents, 1 skills
RMD

    # Create mock docs/index.md
    cat > "$SANDBOX/docs/index.md" <<'IDX'
# Test Plugin
![version](https://img.shields.io/badge/version-2.1.0-blue)
Current version: v2.1.0
1 commands, 1 AI agents, and 1 auto-triggered skills
1 commands, 1 agents, 1 skills
!!! info "Latest: v2.1.0 — Test Release"
    Some content here
IDX

    # Create mock docs/REFCARD.md
    cat > "$SANDBOX/docs/REFCARD.md" <<'REF'
# Quick Reference
```
Version: 2.1.0 (released 2026-01-01)
v2.1.0: Test release
```
REF

    # Create mock docs/DEPENDENCY-ARCHITECTURE.md
    cat > "$SANDBOX/docs/DEPENDENCY-ARCHITECTURE.md" <<'DEP'
# Architecture
**Version**: 2.1.0
DEP

    # Create mock docs/reference/configuration.md
    cat > "$SANDBOX/docs/reference/configuration.md" <<'CFG'
# Configuration
```bash
./scripts/bump-version.sh 2.1.0
```
Version is managed across 13 files.
CFG

    # Create mock mkdocs.yml
    cat > "$SANDBOX/mkdocs.yml" <<'MKD'
site_name: Test
site_description: >-
  Test plugin with 1 commands, 1 agents, 1 skills.
  v2.1.0 adds new features.
MKD

    # Create mock .STATUS
    cat > "$SANDBOX/.STATUS" <<'STS'
version: 2.1.0
counts: 1 commands, 1 skills, 1 agents
STS

    # Create mock CHANGELOG.md
    cat > "$SANDBOX/CHANGELOG.md" <<'CL'
# Changelog
## [2.1.0] — 2026-01-15
### Added
- **New feature** for testing
CL
}

destroy_sandbox() {
    if [ -n "$SANDBOX" ] && [ -d "$SANDBOX" ]; then
        rm -rf "$SANDBOX"
    fi
    SANDBOX=""
}

# ============================================================================
# Unit Tests (run against real project, non-destructive)
# ============================================================================

run_unit_tests() {
    echo ""
    echo -e "${T_BLUE}═══════════════════════════════════════════════════════════${T_NC}"
    echo -e "${T_BLUE}  UNIT TESTS${T_NC}"
    echo -e "${T_BLUE}═══════════════════════════════════════════════════════════${T_NC}"
    echo ""

    test_cli_help
    test_cli_bad_args
    test_clean_repo_exits_zero
}

test_cli_help() {
    log_test "CLI" "help flag"
    local output
    output=$(cd "$PROJECT_ROOT" && bash "$SWEEP_SCRIPT" --help 2>&1)

    assert_contains "$output" "--fix" "Help shows --fix flag"
    assert_contains "$output" "--dry-run" "Help shows --dry-run flag"
    assert_contains "$output" "--version" "Help shows --version flag"
    assert_contains "$output" "--json" "Help shows --json flag"
}

test_cli_bad_args() {
    log_test "CLI" "bad arguments"
    local exit_code=0
    local output
    output=$(cd "$PROJECT_ROOT" && bash "$SWEEP_SCRIPT" --bad-flag 2>&1) || exit_code=$?
    assert_equals "2" "$exit_code" "Bad flag exits with code 2"
}

test_clean_repo_exits_zero() {
    log_test "CLEAN" "clean repo returns exit 0"
    local exit_code=0
    local output
    output=$(cd "$PROJECT_ROOT" && bash "$SWEEP_SCRIPT" 2>&1) || exit_code=$?

    assert_equals "0" "$exit_code" "Clean repo exits with code 0"
    local stripped
    stripped=$(strip_ansi "$output")
    assert_contains "$stripped" "CLEAN" "Output shows CLEAN for Tier 1"
}

# ============================================================================
# Integration Tests (run in sandbox with mock files)
# ============================================================================

run_integration_tests() {
    echo ""
    echo -e "${T_BLUE}═══════════════════════════════════════════════════════════${T_NC}"
    echo -e "${T_BLUE}  INTEGRATION TESTS${T_NC}"
    echo -e "${T_BLUE}═══════════════════════════════════════════════════════════${T_NC}"
    echo ""

    test_stale_version_detected
    test_fix_corrects_stale_refs
    test_dry_run_no_modifications
    test_json_output_valid
    test_clean_sandbox_exits_zero
}

test_stale_version_detected() {
    log_test "DETECT" "stale version in secondary file returns exit 1"
    create_sandbox

    # Add a secondary file with OLD version (2.0.0 — previous of 2.1.0)
    cat > "$SANDBOX/docs/reference/REFCARD-RELEASE.md" <<'STALE'
# Release Reference
Last release: v2.0.0
Pipeline verified for v2.0.0
STALE

    local exit_code=0
    local output
    output=$(cd "$SANDBOX" && bash "$SANDBOX/scripts/post-release-sweep.sh" --version 2.1.0 2>&1) || exit_code=$?

    local stripped
    stripped=$(strip_ansi "$output")
    assert_contains "$stripped" "STALE" "Output shows STALE for old version refs"
    assert_equals "1" "$exit_code" "Stale version detected exits with code 1"

    destroy_sandbox
}

test_fix_corrects_stale_refs() {
    log_test "FIX" "--fix corrects mechanical items"
    create_sandbox

    # Add stale ref file with OLD version (2.0.0 — previous of 2.1.0)
    cat > "$SANDBOX/docs/reference/REFCARD-RELEASE.md" <<'STALE'
# Release Reference
Last release: v2.0.0
Pipeline verified for v2.0.0
STALE

    local exit_code=0
    local output
    output=$(cd "$SANDBOX" && bash "$SANDBOX/scripts/post-release-sweep.sh" --fix --version 2.1.0 2>&1) || exit_code=$?

    local stripped
    stripped=$(strip_ansi "$output")
    assert_contains "$stripped" "FIXED" "Output shows FIXED for auto-corrected refs"

    # Verify file was actually updated
    ((TOTAL_TESTS++))
    if grep -q "v2.1.0" "$SANDBOX/docs/reference/REFCARD-RELEASE.md"; then
        pass "REFCARD-RELEASE.md updated to v2.1.0"
    else
        fail "REFCARD-RELEASE.md updated to v2.1.0" "New version not found"
    fi

    ((TOTAL_TESTS++))
    if grep -q "v2.0.0" "$SANDBOX/docs/reference/REFCARD-RELEASE.md"; then
        fail "Old v2.0.0 removed from REFCARD-RELEASE.md" "Old version still present"
    else
        pass "Old v2.0.0 removed from REFCARD-RELEASE.md"
    fi

    destroy_sandbox
}

test_dry_run_no_modifications() {
    log_test "DRY-RUN" "--dry-run doesn't modify files"
    create_sandbox

    # Add stale ref file with OLD version (2.0.0 — previous of 2.1.0)
    cat > "$SANDBOX/docs/reference/REFCARD-RELEASE.md" <<'STALE'
# Release Reference
Last release: v2.0.0
STALE

    local before_md5
    before_md5=$(md5 -q "$SANDBOX/docs/reference/REFCARD-RELEASE.md")

    local output
    output=$(cd "$SANDBOX" && bash "$SANDBOX/scripts/post-release-sweep.sh" --dry-run --version 2.1.0 2>&1) || true

    local after_md5
    after_md5=$(md5 -q "$SANDBOX/docs/reference/REFCARD-RELEASE.md")

    assert_equals "$before_md5" "$after_md5" "Dry-run doesn't modify files"

    destroy_sandbox
}

test_json_output_valid() {
    log_test "JSON" "--json produces valid JSON"
    create_sandbox

    local output
    output=$(cd "$SANDBOX" && bash "$SANDBOX/scripts/post-release-sweep.sh" --json --version 2.1.0 2>&1)

    # Check it parses as valid JSON
    local json_valid=0
    echo "$output" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null && json_valid=1

    ((TOTAL_TESTS++))
    if [[ $json_valid -eq 1 ]]; then
        pass "JSON output is valid"
    else
        fail "JSON output is valid" "python3 json.load failed"
    fi

    # Check required fields
    assert_contains "$output" '"version"' "JSON has version field"
    assert_contains "$output" '"tier1_issues"' "JSON has tier1_issues field"
    assert_contains "$output" '"clean"' "JSON has clean field"
    assert_contains "$output" '"findings"' "JSON has findings field"

    destroy_sandbox
}

test_clean_sandbox_exits_zero() {
    log_test "CLEAN" "fully consistent sandbox exits 0"
    create_sandbox

    local exit_code=0
    local output
    output=$(cd "$SANDBOX" && bash "$SANDBOX/scripts/post-release-sweep.sh" --version 2.1.0 2>&1) || exit_code=$?

    assert_equals "0" "$exit_code" "Clean sandbox exits with code 0"

    destroy_sandbox
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
}

# ============================================================================
# Main
# ============================================================================

main() {
    local suite="${1:-all}"

    echo -e "${T_BLUE}post-release-sweep.sh Test Suite${T_NC}"
    echo -e "${T_BLUE}═══════════════════════════════════════════════════════════${T_NC}"

    case "$suite" in
        unit)
            run_unit_tests
            ;;
        integration)
            run_integration_tests
            ;;
        all)
            run_unit_tests
            run_integration_tests
            ;;
        *)
            echo "Usage: $0 {unit|integration|all}"
            exit 1
            ;;
    esac

    print_summary

    if [ "$FAILED_TESTS" -gt 0 ]; then
        exit 1
    fi
}

main "$@"
