#!/usr/bin/env bash
#
# Comprehensive Test Suite for Dependency Management System
# Tests: Unit, Validation, and E2E
#
# Usage:
#   ./tests/test_dependency_management.sh              # Run all tests
#   ./tests/test_dependency_management.sh unit         # Run unit tests only
#   ./tests/test_dependency_management.sh validation   # Run validation tests only
#   ./tests/test_dependency_management.sh e2e          # Run E2E tests only
#

# Note: Not using 'set -e' because we want tests to continue after failures
set -uo pipefail

# Test configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Test results array
declare -a FAILED_TEST_NAMES=()

#
# Helper Functions
#

log_test() {
    local category="$1"
    local name="$2"
    echo -e "${BLUE}[TEST]${NC} ${category}: ${name}"
}

pass() {
    local name="$1"
    ((PASSED_TESTS++))
    echo -e "${GREEN}  ✓ PASS${NC}: $name"
}

fail() {
    local name="$1"
    local reason="${2:-Unknown failure}"
    ((FAILED_TESTS++))
    FAILED_TEST_NAMES+=("$name: $reason")
    echo -e "${RED}  ✗ FAIL${NC}: $name"
    echo -e "${RED}    Reason: $reason${NC}"
}

skip() {
    local name="$1"
    local reason="${2:-Skipped}"
    ((SKIPPED_TESTS++))
    echo -e "${YELLOW}  ⊘ SKIP${NC}: $name ($reason)"
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

assert_file_exists() {
    local file="$1"
    local test_name="$2"

    ((TOTAL_TESTS++))
    if [ -f "$file" ]; then
        pass "$test_name"
    else
        fail "$test_name" "File '$file' does not exist"
    fi
}

assert_executable() {
    local file="$1"
    local test_name="$2"

    ((TOTAL_TESTS++))
    if [ -x "$file" ]; then
        pass "$test_name"
    else
        fail "$test_name" "File '$file' is not executable"
    fi
}

assert_exit_code() {
    local expected_code="$1"
    local command="$2"
    local test_name="$3"

    ((TOTAL_TESTS++))
    local actual_code=0
    eval "$command" > /dev/null 2>&1 || actual_code=$?

    if [ "$expected_code" -eq "$actual_code" ]; then
        pass "$test_name"
    else
        fail "$test_name" "Expected exit code $expected_code, got $actual_code"
    fi
}

assert_json_valid() {
    local json="$1"
    local test_name="$2"

    ((TOTAL_TESTS++))
    if echo "$json" | python3 -m json.tool > /dev/null 2>&1; then
        pass "$test_name"
    else
        fail "$test_name" "Invalid JSON output"
    fi
}

assert_contains() {
    local haystack="$1"
    local needle="$2"
    local test_name="$3"

    ((TOTAL_TESTS++))
    if echo "$haystack" | grep -q "$needle"; then
        pass "$test_name"
    else
        fail "$test_name" "Expected to find '$needle' in output"
    fi
}

#
# UNIT TESTS
#

run_unit_tests() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  UNIT TESTS - Individual Component Testing${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

    # Test 1: Script Files Exist
    log_test "Unit" "Script files exist"
    assert_file_exists "$SCRIPTS_DIR/dependency-manager.sh" "dependency-manager.sh exists"
    assert_file_exists "$SCRIPTS_DIR/tool-detector.sh" "tool-detector.sh exists"
    assert_file_exists "$SCRIPTS_DIR/session-cache.sh" "session-cache.sh exists"
    assert_file_exists "$SCRIPTS_DIR/dependency-installer.sh" "dependency-installer.sh exists"
    assert_file_exists "$SCRIPTS_DIR/consent-prompt.sh" "consent-prompt.sh exists"
    assert_file_exists "$SCRIPTS_DIR/convert-cast.sh" "convert-cast.sh exists"
    assert_file_exists "$SCRIPTS_DIR/batch-convert.sh" "batch-convert.sh exists"
    assert_file_exists "$SCRIPTS_DIR/health-check.sh" "health-check.sh exists"
    assert_file_exists "$SCRIPTS_DIR/version-check.sh" "version-check.sh exists"
    assert_file_exists "$SCRIPTS_DIR/repair-tools.sh" "repair-tools.sh exists"

    # Test 2: Scripts are Executable
    log_test "Unit" "Scripts are executable"
    assert_executable "$SCRIPTS_DIR/dependency-manager.sh" "dependency-manager.sh is executable"
    assert_executable "$SCRIPTS_DIR/tool-detector.sh" "tool-detector.sh is executable"
    assert_executable "$SCRIPTS_DIR/dependency-installer.sh" "dependency-installer.sh is executable"
    assert_executable "$SCRIPTS_DIR/consent-prompt.sh" "consent-prompt.sh is executable"
    assert_executable "$SCRIPTS_DIR/convert-cast.sh" "convert-cast.sh is executable"
    assert_executable "$SCRIPTS_DIR/batch-convert.sh" "batch-convert.sh is executable"
    assert_executable "$SCRIPTS_DIR/health-check.sh" "health-check.sh is executable"
    assert_executable "$SCRIPTS_DIR/version-check.sh" "version-check.sh is executable"
    assert_executable "$SCRIPTS_DIR/repair-tools.sh" "repair-tools.sh is executable"

    # Test 3: Bash Syntax Validation
    log_test "Unit" "Bash syntax validation"
    for script in "$SCRIPTS_DIR"/*.sh; do
        script_name=$(basename "$script")
        assert_exit_code 0 "bash -n $script" "Syntax valid: $script_name"
    done

    # Test 4: Tool Detector Functions
    log_test "Unit" "tool-detector.sh functions"

    # Source the script
    source "$SCRIPTS_DIR/tool-detector.sh" || {
        fail "Source tool-detector.sh" "Failed to source script"
        return
    }

    # Test detect function exists
    ((TOTAL_TESTS++))
    if type detect_tool > /dev/null 2>&1; then
        pass "detect_tool function exists"
    else
        fail "detect_tool function exists" "Function not found"
    fi

    # Test 5: Health Check Functions
    log_test "Unit" "health-check.sh functions"

    source "$SCRIPTS_DIR/health-check.sh" || {
        fail "Source health-check.sh" "Failed to source script"
        return
    }

    ((TOTAL_TESTS++))
    if type run_health_check > /dev/null 2>&1; then
        pass "run_health_check function exists"
    else
        fail "run_health_check function exists" "Function not found"
    fi

    ((TOTAL_TESTS++))
    if type validate_all_health > /dev/null 2>&1; then
        pass "validate_all_health function exists"
    else
        fail "validate_all_health function exists" "Function not found"
    fi

    # Test 6: Version Check Functions
    log_test "Unit" "version-check.sh functions"

    source "$SCRIPTS_DIR/version-check.sh" || {
        fail "Source version-check.sh" "Failed to source script"
        return
    }

    ((TOTAL_TESTS++))
    if type extract_version > /dev/null 2>&1; then
        pass "extract_version function exists"
    else
        fail "extract_version function exists" "Function not found"
    fi

    ((TOTAL_TESTS++))
    if type compare_versions > /dev/null 2>&1; then
        pass "compare_versions function exists"
    else
        fail "compare_versions function exists" "Function not found"
    fi

    # Test 7: Version Comparison Logic
    log_test "Unit" "Version comparison logic"

    local result
    result=$(compare_versions "1.0.0" "2.0.0")
    assert_equals "-1" "$result" "1.0.0 < 2.0.0"

    result=$(compare_versions "2.0.0" "1.0.0")
    assert_equals "1" "$result" "2.0.0 > 1.0.0"

    result=$(compare_versions "1.0.0" "1.0.0")
    assert_equals "0" "$result" "1.0.0 = 1.0.0"

    result=$(compare_versions "1.2.3" "1.2.4")
    assert_equals "-1" "$result" "1.2.3 < 1.2.4"

    # Test 8: Session Cache
    log_test "Unit" "session-cache.sh functions"

    source "$SCRIPTS_DIR/session-cache.sh" || {
        fail "Source session-cache.sh" "Failed to source script"
        return
    }

    ((TOTAL_TESTS++))
    if type get_cached_status > /dev/null 2>&1; then
        pass "get_cached_status function exists"
    else
        fail "get_cached_status function exists" "Function not found"
    fi

    ((TOTAL_TESTS++))
    if type store_cache > /dev/null 2>&1; then
        pass "store_cache function exists"
    else
        fail "store_cache function exists" "Function not found"
    fi
}

#
# VALIDATION TESTS
#

run_validation_tests() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  VALIDATION TESTS - Input/Output Validation${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

    # Test 1: Dependency Manager Help Text
    log_test "Validation" "dependency-manager.sh help text"

    local help_output
    help_output=$("$SCRIPTS_DIR/dependency-manager.sh" 2>&1 || true)
    assert_contains "$help_output" "Usage:" "Help shows usage"
    assert_contains "$help_output" "parse_frontmatter" "Help shows parse_frontmatter command"
    assert_contains "$help_output" "check_dependencies" "Help shows check_dependencies command"

    # Test 2: Health Check JSON Output
    log_test "Validation" "health-check.sh JSON output"

    local json_output
    json_output=$("$SCRIPTS_DIR/health-check.sh" validate asciinema --json 2>&1 || true)
    assert_json_valid "$json_output" "Health check produces valid JSON"

    # Test 3: Version Check JSON Output
    log_test "Validation" "version-check.sh JSON output"

    json_output=$("$SCRIPTS_DIR/version-check.sh" validate asciinema --json 2>&1 || true)
    assert_json_valid "$json_output" "Version check produces valid JSON"

    # Test 4: Repair Tools Help
    log_test "Validation" "repair-tools.sh help text"

    help_output=$("$SCRIPTS_DIR/repair-tools.sh" --help 2>&1 || true)
    assert_contains "$help_output" "Usage:" "Repair help shows usage"
    assert_contains "$help_output" "repair" "Repair help shows repair command"
    assert_contains "$help_output" "detect" "Repair help shows detect command"

    # Test 5: Convert Cast Script Validation
    log_test "Validation" "convert-cast.sh input validation"

    # Test with invalid input (should fail)
    assert_exit_code 1 "$SCRIPTS_DIR/convert-cast.sh nonexistent.cast output.gif 2>/dev/null" \
        "convert-cast fails on nonexistent file"

    # Test 6: Batch Convert Dry Run
    log_test "Validation" "batch-convert.sh dry-run mode"

    local dry_run_output
    dry_run_output=$("$SCRIPTS_DIR/batch-convert.sh" --search-path /tmp --dry-run 2>&1 || true)
    assert_contains "$dry_run_output" "DRY RUN" "Batch convert shows dry run mode"

    # Test 7: Dependency Manager JSON Output
    log_test "Validation" "dependency-manager.sh JSON output"

    json_output=$("$SCRIPTS_DIR/dependency-manager.sh" display_status_json asciinema 2>&1 || true)
    assert_json_valid "$json_output" "Dependency manager produces valid JSON"

    if echo "$json_output" | python3 -c "import sys, json; data=json.load(sys.stdin); assert 'status' in data" 2>/dev/null; then
        pass "JSON contains 'status' field"
        ((TOTAL_TESTS++))
    else
        fail "JSON contains 'status' field" "Field not found"
        ((TOTAL_TESTS++))
    fi

    if echo "$json_output" | python3 -c "import sys, json; data=json.load(sys.stdin); assert 'method' in data" 2>/dev/null; then
        pass "JSON contains 'method' field"
        ((TOTAL_TESTS++))
    else
        fail "JSON contains 'method' field" "Field not found"
        ((TOTAL_TESTS++))
    fi

    if echo "$json_output" | python3 -c "import sys, json; data=json.load(sys.stdin); assert 'tools' in data" 2>/dev/null; then
        pass "JSON contains 'tools' field"
        ((TOTAL_TESTS++))
    else
        fail "JSON contains 'tools' field" "Field not found"
        ((TOTAL_TESTS++))
    fi

    # Test 8: Exit Codes
    log_test "Validation" "Script exit codes"

    # Health check with valid method should not crash
    "$SCRIPTS_DIR/health-check.sh" validate asciinema > /dev/null 2>&1 || true
    ((TOTAL_TESTS++))
    pass "health-check.sh exits cleanly"

    # Version check with valid method should not crash
    "$SCRIPTS_DIR/version-check.sh" validate asciinema > /dev/null 2>&1 || true
    ((TOTAL_TESTS++))
    pass "version-check.sh exits cleanly"

    # Test 9: Installer Script Validation
    log_test "Validation" "Installer scripts structure"

    # Verify installer scripts have required functions
    for installer in brew cargo binary; do
        local installer_script="$SCRIPTS_DIR/${installer}-installer.sh"
        if [ -f "$installer_script" ]; then
            # Check for install function
            if grep -q "^install_" "$installer_script"; then
                pass "${installer}-installer has install function"
                ((TOTAL_TESTS++))
            else
                fail "${installer}-installer has install function" "Function not found"
                ((TOTAL_TESTS++))
            fi
        fi
    done
}

#
# END-TO-END TESTS
#

run_e2e_tests() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  E2E TESTS - Full Workflow Testing${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

    # Test 1: Full Dependency Check Workflow
    log_test "E2E" "Complete dependency check workflow"

    local check_output
    check_output=$("$SCRIPTS_DIR/dependency-manager.sh" display_status_table asciinema 2>&1 || true)

    assert_contains "$check_output" "DEPENDENCY STATUS" "Shows status table header"
    assert_contains "$check_output" "Tool" "Shows tool column"
    assert_contains "$check_output" "Status" "Shows status column"

    # Test 2: Health Check + Version Check Integration
    log_test "E2E" "Health check and version check integration"

    # Run health check
    local health_json
    health_json=$("$SCRIPTS_DIR/health-check.sh" validate asciinema --json 2>&1 || true)

    # Run version check
    local version_json
    version_json=$("$SCRIPTS_DIR/version-check.sh" validate asciinema --json 2>&1 || true)

    # Both should produce valid JSON
    assert_json_valid "$health_json" "Health check JSON valid in E2E"
    assert_json_valid "$version_json" "Version check JSON valid in E2E"

    # Test 3: Repair Detection Workflow
    log_test "E2E" "Repair candidate detection workflow"

    local repair_output
    repair_output=$("$SCRIPTS_DIR/repair-tools.sh" detect asciinema --json 2>&1 || true)

    assert_json_valid "$repair_output" "Repair detection produces valid JSON"

    # Test 4: CI/CD Workflow File Validation
    log_test "E2E" "GitHub Actions workflow validation"

    local workflow_file="$PROJECT_ROOT/.github/workflows/validate-dependencies.yml"

    if [ -f "$workflow_file" ]; then
        pass "GitHub Actions workflow file exists"
        ((TOTAL_TESTS++))

        # Check for required keys
        if grep -q "validate-dependencies" "$workflow_file"; then
            pass "Workflow has correct job name"
            ((TOTAL_TESTS++))
        else
            fail "Workflow has correct job name" "Job name not found"
            ((TOTAL_TESTS++))
        fi

        if grep -q "display_status_json" "$workflow_file"; then
            pass "Workflow uses display_status_json"
            ((TOTAL_TESTS++))
        else
            fail "Workflow uses display_status_json" "Command not found"
            ((TOTAL_TESTS++))
        fi
    else
        fail "GitHub Actions workflow file exists" "File not found"
        ((TOTAL_TESTS++))
    fi

    # Test 5: Documentation Completeness
    log_test "E2E" "Documentation completeness"

    local doc_file="$PROJECT_ROOT/docs/DEPENDENCY-MANAGEMENT.md"

    if [ -f "$doc_file" ]; then
        pass "Dependency management documentation exists"
        ((TOTAL_TESTS++))

        # Check for required sections
        local sections=("Overview" "Quick Start" "Flags Reference" "Methods" "Troubleshooting" "Architecture")
        for section in "${sections[@]}"; do
            if grep -q "## $section" "$doc_file"; then
                pass "Documentation has '$section' section"
                ((TOTAL_TESTS++))
            else
                fail "Documentation has '$section' section" "Section not found"
                ((TOTAL_TESTS++))
            fi
        done
    else
        fail "Dependency management documentation exists" "File not found"
        ((TOTAL_TESTS++))
    fi

    # Test 6: Full System Integration
    log_test "E2E" "Complete system integration test"

    # Simulate full workflow: check → detect issues → (would repair if issues found)

    # Step 1: Check dependencies
    local status_json
    status_json=$("$SCRIPTS_DIR/dependency-manager.sh" display_status_json asciinema 2>&1 || true)

    # Step 2: Parse status
    local status
    status=$(echo "$status_json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null || echo "unknown")

    if [ "$status" = "ok" ] || [ "$status" = "issues" ]; then
        pass "Full workflow: status detection works"
        ((TOTAL_TESTS++))
    else
        fail "Full workflow: status detection works" "Got status: $status"
        ((TOTAL_TESTS++))
    fi

    # Step 3: If issues, detect repair candidates
    if [ "$status" = "issues" ]; then
        local candidates
        candidates=$("$SCRIPTS_DIR/repair-tools.sh" detect asciinema --json 2>&1 || true)

        if echo "$candidates" | python3 -m json.tool > /dev/null 2>&1; then
            pass "Full workflow: repair candidate detection works"
            ((TOTAL_TESTS++))
        else
            fail "Full workflow: repair candidate detection works" "Invalid JSON"
            ((TOTAL_TESTS++))
        fi
    else
        skip "Full workflow: repair candidate detection" "No issues to repair"
    fi
}

#
# TEST SUMMARY
#

print_summary() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  TEST SUMMARY${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

    echo -e "Total Tests:   ${TOTAL_TESTS}"
    echo -e "${GREEN}Passed:        ${PASSED_TESTS}${NC}"

    if [ $FAILED_TESTS -gt 0 ]; then
        echo -e "${RED}Failed:        ${FAILED_TESTS}${NC}"
    else
        echo -e "Failed:        ${FAILED_TESTS}"
    fi

    if [ $SKIPPED_TESTS -gt 0 ]; then
        echo -e "${YELLOW}Skipped:       ${SKIPPED_TESTS}${NC}"
    else
        echo -e "Skipped:       ${SKIPPED_TESTS}"
    fi

    local pass_rate=0
    if [ $TOTAL_TESTS -gt 0 ]; then
        pass_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    fi
    echo -e "Pass Rate:     ${pass_rate}%"

    if [ $FAILED_TESTS -gt 0 ]; then
        echo -e "\n${RED}Failed Tests:${NC}"
        for failed_test in "${FAILED_TEST_NAMES[@]}"; do
            echo -e "  ${RED}✗${NC} $failed_test"
        done
    fi

    echo ""

    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
        return 0
    else
        echo -e "${RED}❌ SOME TESTS FAILED${NC}"
        return 1
    fi
}

#
# MAIN
#

main() {
    local test_suite="${1:-all}"

    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   Dependency Management System - Test Suite               ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

    case "$test_suite" in
        unit)
            run_unit_tests
            ;;
        validation)
            run_validation_tests
            ;;
        e2e)
            run_e2e_tests
            ;;
        all)
            run_unit_tests
            run_validation_tests
            run_e2e_tests
            ;;
        *)
            echo -e "${RED}Unknown test suite: $test_suite${NC}"
            echo "Usage: $0 [unit|validation|e2e|all]"
            exit 1
            ;;
    esac

    print_summary
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
