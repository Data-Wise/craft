#!/usr/bin/env bash
#
# Test Suite for scripts/bump-version.sh
# Tests: Unit (dry-run, verify, CLI), Integration (sandbox bump)
#
# Usage:
#   ./tests/test_bump_version.sh              # Run all tests
#   ./tests/test_bump_version.sh unit         # Run unit tests only
#   ./tests/test_bump_version.sh integration  # Run integration tests only

# Note: Not using 'set -e' because we want tests to continue after failures
set -uo pipefail

# Test configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUMP_SCRIPT="$PROJECT_ROOT/scripts/bump-version.sh"

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

# Sandbox directory for integration tests
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

# Strip ANSI codes from text
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
    mkdir -p "$SANDBOX/commands/test"
    mkdir -p "$SANDBOX/skills/test"
    mkdir -p "$SANDBOX/agents"
    mkdir -p "$SANDBOX/docs/specs"

    # Copy scripts
    cp "$PROJECT_ROOT/scripts/bump-version.sh" "$SANDBOX/scripts/"
    cp "$PROJECT_ROOT/scripts/bump-version-helper.py" "$SANDBOX/scripts/"
    cp "$PROJECT_ROOT/scripts/formatting.sh" "$SANDBOX/scripts/"

    # Create mock command/skill/agent files for count detection
    echo "---" > "$SANDBOX/commands/test/cmd1.md"
    echo "---" > "$SANDBOX/skills/test/SKILL.md"
    echo "---" > "$SANDBOX/agents/agent1.md"
    echo "---" > "$SANDBOX/docs/specs/SPEC-test-2026.md"

    # Create mock plugin.json
    cat > "$SANDBOX/.claude-plugin/plugin.json" <<'PJSON'
{
  "name": "test-plugin",
  "version": "1.0.0",
  "description": "Test plugin with 1 commands, 1 agents, 1 skills"
}
PJSON

    # Create mock marketplace.json
    cat > "$SANDBOX/.claude-plugin/marketplace.json" <<'MJSON'
{
  "metadata": {
    "version": "1.0.0"
  },
  "plugins": [
    {
      "version": "1.0.0"
    }
  ]
}
MJSON

    # Create mock package.json
    cat > "$SANDBOX/package.json" <<'PKG'
{
  "name": "test-plugin",
  "version": "1.0.0"
}
PKG

    # Create mock CLAUDE.md
    cat > "$SANDBOX/CLAUDE.md" <<'CMD'
# Test Plugin

**Current Version:** v1.0.0 | **Tests:** 100 passing

**1 commands** · **1 skills** · **1 agents**
CMD

    # Create mock README.md
    cat > "$SANDBOX/README.md" <<'RMD'
# Test Plugin

![version](https://img.shields.io/badge/version-1.0.0-blue)

**1 commands** · **1 skills** · **1 agents**

1 commands, 1 agents, 1 skills
RMD

    # Create mock docs/index.md
    cat > "$SANDBOX/docs/index.md" <<'IDX'
# Test Plugin

![version](https://img.shields.io/badge/version-1.0.0-blue)

Current version: v1.0.0

1 commands, 1 AI agents, and 1 auto-triggered skills

1 commands, 1 agents, 1 skills

!!! info "Latest: v1.0.0 — Test Release"
    Some content here
IDX

    # Create mock docs/REFCARD.md
    cat > "$SANDBOX/docs/REFCARD.md" <<'REF'
# Quick Reference

```
┌─────────────────────────────────────────────────────────────┐
│  TEST PLUGIN QUICK REFERENCE                                │
├─────────────────────────────────────────────────────────────┤
│  Version: 1.0.0 (released 2026-01-01)                      │
│  Commands: 1 | Agents: 1 | Skills: 1                       │
│  Documentation: 99% complete | Tests: ~100 passing          │
│  Docs: https://example.com                                  │
│  v1.0.0: Test release title                                 │
└─────────────────────────────────────────────────────────────┘
```
REF

    # Create mock docs/DEPENDENCY-ARCHITECTURE.md
    cat > "$SANDBOX/docs/DEPENDENCY-ARCHITECTURE.md" <<'DEP'
# Architecture

Some content here.

**Version**: 1.0.0
DEP

    # Create mock docs/reference/configuration.md
    cat > "$SANDBOX/docs/reference/configuration.md" <<'CFG'
# Configuration

## Version Sync

Version is managed across 13 files atomically using `bump-version.sh`:

```bash
./scripts/bump-version.sh 1.0.0        # Full bump
./scripts/bump-version.sh --verify       # Check for drift
```
CFG

    # Create mock mkdocs.yml
    cat > "$SANDBOX/mkdocs.yml" <<'MKD'
site_name: Test
site_description: >-
  Test plugin with 1 commands, 1 agents, 1 skills.
  v1.0.0 adds new features.
MKD

    # Create mock .STATUS
    cat > "$SANDBOX/.STATUS" <<'STS'
version: 1.0.0
counts: 1 commands, 1 skills, 1 agents
STS
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
    test_cli_conflicting_flags
    test_dry_run_lists_all_files
    test_verify_passes_on_clean
    test_verify_file_count
}

test_cli_help() {
    log_test "CLI" "help flag"
    local output
    output=$(cd "$PROJECT_ROOT" && bash "$BUMP_SCRIPT" --help 2>&1)

    assert_contains "$output" "VERSION" "Help shows VERSION parameter"
    assert_contains "$output" "--dry-run" "Help shows --dry-run flag"
    assert_contains "$output" "--verify" "Help shows --verify flag"
    assert_contains "$output" "--counts-only" "Help shows --counts-only flag"
}

test_cli_bad_args() {
    log_test "CLI" "bad arguments"

    local output exit_code
    output=$(cd "$PROJECT_ROOT" && bash "$BUMP_SCRIPT" --bad-flag 2>&1) || exit_code=$?
    assert_equals "2" "$exit_code" "Bad flag exits with code 2"

    output=$(cd "$PROJECT_ROOT" && bash "$BUMP_SCRIPT" not-a-version 2>&1) || exit_code=$?
    assert_equals "2" "$exit_code" "Non-version string exits with code 2"
}

test_cli_conflicting_flags() {
    log_test "CLI" "conflicting flags"

    local output exit_code
    output=$(cd "$PROJECT_ROOT" && bash "$BUMP_SCRIPT" 1.0.0 --counts-only 2>&1) || exit_code=$?
    assert_equals "2" "$exit_code" "Version + --counts-only exits with code 2"

    output=$(cd "$PROJECT_ROOT" && bash "$BUMP_SCRIPT" 1.0.0 --verify 2>&1) || exit_code=$?
    assert_equals "2" "$exit_code" "Version + --verify exits with code 2"
}

test_dry_run_lists_all_files() {
    log_test "DRY-RUN" "lists all 13 files"
    local output
    output=$(cd "$PROJECT_ROOT" && bash "$BUMP_SCRIPT" 99.99.99 --dry-run 2>&1)
    local stripped
    stripped=$(strip_ansi "$output")

    # JSON files
    assert_contains "$stripped" "plugin.json" "Dry-run lists plugin.json"
    assert_contains "$stripped" "marketplace.json" "Dry-run lists marketplace.json"
    assert_contains "$stripped" "package.json" "Dry-run lists package.json"

    # Original text files
    assert_contains "$stripped" "CLAUDE.md" "Dry-run lists CLAUDE.md"
    assert_contains "$stripped" "README.md" "Dry-run lists README.md"
    assert_contains "$stripped" "docs/index.md" "Dry-run lists docs/index.md"
    assert_contains "$stripped" "docs/REFCARD.md" "Dry-run lists docs/REFCARD.md"
    assert_contains "$stripped" "mkdocs.yml" "Dry-run lists mkdocs.yml"
    assert_contains "$stripped" ".STATUS" "Dry-run lists .STATUS"

    # New files (added in bump-version-docs feature)
    assert_contains "$stripped" "docs/DEPENDENCY-ARCHITECTURE.md" "Dry-run lists DEPENDENCY-ARCHITECTURE.md"
    assert_contains "$stripped" "docs/reference/configuration.md" "Dry-run lists configuration.md"

    # Verify dry-run doesn't modify
    assert_contains "$stripped" "DRY RUN" "Dry-run shows DRY RUN message"
    assert_contains "$stripped" "no files were modified" "Dry-run confirms no modifications"
}

test_verify_passes_on_clean() {
    log_test "VERIFY" "passes on clean project"
    local exit_code=0
    local output
    output=$(cd "$PROJECT_ROOT" && bash "$BUMP_SCRIPT" --verify 2>&1) || exit_code=$?

    assert_equals "0" "$exit_code" "Verify exits 0 on clean project"
    local stripped
    stripped=$(strip_ansi "$output")
    assert_contains "$stripped" "ALL CONSISTENT" "Verify shows ALL CONSISTENT"
}

test_verify_file_count() {
    log_test "VERIFY" "checks all 13 files"
    # Verify mode checks: 3 JSON loop + CLAUDE.md + README.md + mkdocs.yml + .STATUS
    #   + DEPENDENCY-ARCHITECTURE.md + configuration.md + REFCARD.md + index.md
    #   + commands/hub.md + docs/commands/hub.md = 13
    # We can't easily count checks from output on a clean project,
    # but we can verify the script contains all the grep patterns
    local script_content
    script_content=$(cat "$BUMP_SCRIPT")

    assert_contains "$script_content" "DEPENDENCY-ARCHITECTURE.md" "Script checks DEPENDENCY-ARCHITECTURE.md"
    assert_contains "$script_content" "configuration.md" "Script checks configuration.md"
    assert_contains "$script_content" 'Version: ${CURRENT_VERSION}' "Script checks REFCARD box version"
    assert_contains "$script_content" 'Latest: v${CURRENT_VERSION}' "Script checks index.md info box"
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

    test_full_bump_updates_all_files
    test_verify_catches_drift
    test_counts_only_mode
    test_refcard_box_interior_updated
    test_index_info_box_updated
    test_dependency_arch_footer_updated
    test_configuration_example_updated
}

test_full_bump_updates_all_files() {
    log_test "BUMP" "full bump updates all files"
    create_sandbox

    local output
    output=$(cd "$SANDBOX" && bash "$SANDBOX/scripts/bump-version.sh" 2.0.0 2>&1)
    local stripped
    stripped=$(strip_ansi "$output")

    # Verify version was updated in JSON files
    local pj_ver
    pj_ver=$(python3 -c "import json; print(json.load(open('$SANDBOX/.claude-plugin/plugin.json'))['version'])")
    assert_equals "2.0.0" "$pj_ver" "plugin.json version updated to 2.0.0"

    local mj_ver
    mj_ver=$(python3 -c "import json; print(json.load(open('$SANDBOX/.claude-plugin/marketplace.json'))['metadata']['version'])")
    assert_equals "2.0.0" "$mj_ver" "marketplace.json version updated to 2.0.0"

    local pkg_ver
    pkg_ver=$(python3 -c "import json; print(json.load(open('$SANDBOX/package.json'))['version'])")
    assert_equals "2.0.0" "$pkg_ver" "package.json version updated to 2.0.0"

    # Verify text file updates
    ((TOTAL_TESTS++))
    if grep -q "v2.0.0" "$SANDBOX/CLAUDE.md"; then
        pass "CLAUDE.md contains v2.0.0"
    else
        fail "CLAUDE.md contains v2.0.0" "Version not found"
    fi

    ((TOTAL_TESTS++))
    if grep -q "version-2.0.0" "$SANDBOX/README.md"; then
        pass "README.md badge updated to 2.0.0"
    else
        fail "README.md badge updated to 2.0.0" "Badge version not found"
    fi

    ((TOTAL_TESTS++))
    if grep -q "version: 2.0.0" "$SANDBOX/.STATUS"; then
        pass ".STATUS version updated to 2.0.0"
    else
        fail ".STATUS version updated to 2.0.0" "Version not found"
    fi

    destroy_sandbox
}

test_verify_catches_drift() {
    log_test "VERIFY" "catches version drift"
    create_sandbox

    # Introduce drift: change plugin.json version but not others
    python3 -c "
import json
with open('$SANDBOX/.claude-plugin/plugin.json', 'r') as f:
    data = json.load(f)
data['version'] = '9.9.9'
with open('$SANDBOX/.claude-plugin/plugin.json', 'w') as f:
    json.dump(data, f, indent=2)
"

    local exit_code=0
    local output
    output=$(cd "$SANDBOX" && bash "$SANDBOX/scripts/bump-version.sh" --verify 2>&1) || exit_code=$?

    assert_equals "1" "$exit_code" "Verify exits 1 when drift detected"
    local stripped
    stripped=$(strip_ansi "$output")
    assert_contains "$stripped" "DRIFT DETECTED" "Output shows DRIFT DETECTED"

    destroy_sandbox
}

test_counts_only_mode() {
    log_test "COUNTS" "counts-only updates counts without version"
    create_sandbox

    local output
    output=$(cd "$SANDBOX" && bash "$SANDBOX/scripts/bump-version.sh" --counts-only 2>&1)

    # Version should remain 1.0.0
    local pj_ver
    pj_ver=$(python3 -c "import json; print(json.load(open('$SANDBOX/.claude-plugin/plugin.json'))['version'])")
    assert_equals "1.0.0" "$pj_ver" "Version unchanged in counts-only mode"

    destroy_sandbox
}

test_refcard_box_interior_updated() {
    log_test "REFCARD" "box interior lines updated"
    create_sandbox

    cd "$SANDBOX" && bash "$SANDBOX/scripts/bump-version.sh" 2.0.0 > /dev/null 2>&1

    # Line ~7: "Version: X.Y.Z"
    ((TOTAL_TESTS++))
    if grep -q "Version: 2.0.0" "$SANDBOX/docs/REFCARD.md"; then
        pass "REFCARD box 'Version: 2.0.0' updated"
    else
        fail "REFCARD box 'Version: 2.0.0' updated" "Pattern not found"
    fi

    # Line ~11: "vX.Y.Z: ..."
    ((TOTAL_TESTS++))
    if grep -q "v2.0.0:" "$SANDBOX/docs/REFCARD.md"; then
        pass "REFCARD box 'v2.0.0:' summary updated"
    else
        fail "REFCARD box 'v2.0.0:' summary updated" "Pattern not found"
    fi

    # Should NOT contain old version in box
    ((TOTAL_TESTS++))
    if grep -q "Version: 1.0.0" "$SANDBOX/docs/REFCARD.md"; then
        fail "REFCARD old 'Version: 1.0.0' removed" "Old version still present"
    else
        pass "REFCARD old 'Version: 1.0.0' removed"
    fi

    destroy_sandbox
}

test_index_info_box_updated() {
    log_test "INDEX" "info box version updated"
    create_sandbox

    cd "$SANDBOX" && bash "$SANDBOX/scripts/bump-version.sh" 2.0.0 > /dev/null 2>&1

    ((TOTAL_TESTS++))
    if grep -q 'Latest: v2.0.0' "$SANDBOX/docs/index.md"; then
        pass "index.md info box 'Latest: v2.0.0' updated"
    else
        fail "index.md info box 'Latest: v2.0.0' updated" "Pattern not found"
    fi

    # Old version should be gone from info box
    ((TOTAL_TESTS++))
    if grep -q 'Latest: v1.0.0' "$SANDBOX/docs/index.md"; then
        fail "index.md old 'Latest: v1.0.0' removed" "Old version still present"
    else
        pass "index.md old 'Latest: v1.0.0' removed"
    fi

    destroy_sandbox
}

test_dependency_arch_footer_updated() {
    log_test "DEP-ARCH" "footer version updated"
    create_sandbox

    cd "$SANDBOX" && bash "$SANDBOX/scripts/bump-version.sh" 2.0.0 > /dev/null 2>&1

    ((TOTAL_TESTS++))
    if grep -qF '**Version**: 2.0.0' "$SANDBOX/docs/DEPENDENCY-ARCHITECTURE.md"; then
        pass "DEPENDENCY-ARCHITECTURE.md footer updated to 2.0.0"
    else
        fail "DEPENDENCY-ARCHITECTURE.md footer updated to 2.0.0" "Pattern not found"
    fi

    ((TOTAL_TESTS++))
    if grep -qF '**Version**: 1.0.0' "$SANDBOX/docs/DEPENDENCY-ARCHITECTURE.md"; then
        fail "DEPENDENCY-ARCHITECTURE.md old version removed" "Old version still present"
    else
        pass "DEPENDENCY-ARCHITECTURE.md old version removed"
    fi

    destroy_sandbox
}

test_configuration_example_updated() {
    log_test "CONFIG" "example version + file count updated"
    create_sandbox

    cd "$SANDBOX" && bash "$SANDBOX/scripts/bump-version.sh" 2.0.0 > /dev/null 2>&1

    ((TOTAL_TESTS++))
    if grep -q 'bump-version.sh 2.0.0' "$SANDBOX/docs/reference/configuration.md"; then
        pass "configuration.md example version updated to 2.0.0"
    else
        fail "configuration.md example version updated to 2.0.0" "Pattern not found"
    fi

    ((TOTAL_TESTS++))
    if grep -q 'across 13 files' "$SANDBOX/docs/reference/configuration.md"; then
        pass "configuration.md file count is 13"
    else
        fail "configuration.md file count is 13" "File count not found or wrong"
    fi

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

    echo -e "${T_BLUE}bump-version.sh Test Suite${T_NC}"
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
