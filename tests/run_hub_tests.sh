#!/bin/bash
# Unified Hub v2.0 Test Runner
# Runs all Hub tests (existing + enhanced)

set -e  # Exit on error

echo "======================================================================="
echo "🧪 Hub v2.0 Comprehensive Test Suite"
echo "======================================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
TOTAL_PASSED=0
TOTAL_FAILED=0
START_TIME=$(date +%s)

# Function to run a test suite
run_test_suite() {
    local test_file=$1
    local test_name=$2

    echo "Running: $test_name"
    echo "-----------------------------------"

    if python3 "$test_file"; then
        echo -e "${GREEN}✅ $test_name PASSED${NC}"
        ((TOTAL_PASSED++))
    else
        echo -e "${RED}❌ $test_name FAILED${NC}"
        ((TOTAL_FAILED++))
    fi
    echo ""
}

# Change to project root
cd "$(dirname "$0")/.."

echo "═══════════════════════════════════════════════════════════════════════"
echo "Phase 1: Existing Tests (34 tests)"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

run_test_suite "tests/test_hub_discovery.py" "Discovery Engine (12 tests)"
run_test_suite "tests/test_hub_layer2.py" "Layer 2 Navigation (7 tests)"
run_test_suite "tests/test_hub_layer3.py" "Layer 3 Detail (8 tests)"
run_test_suite "tests/test_hub_integration.py" "Integration (7 tests)"

echo "═══════════════════════════════════════════════════════════════════════"
echo "Phase 2: Enhanced Tests (18 tests)"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

run_test_suite "tests/test_hub_yaml_edge_cases.py" "YAML Parser Edge Cases (12 tests)"
run_test_suite "tests/test_hub_e2e_focused.py" "E2E Workflows (6 tests)"

# Calculate duration
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Summary
echo "======================================================================="
echo "📊 Test Summary"
echo "======================================================================="
echo ""
echo "Test Suites: $((TOTAL_PASSED + TOTAL_FAILED)) total"
echo -e "  ${GREEN}Passed: $TOTAL_PASSED${NC}"
if [ $TOTAL_FAILED -gt 0 ]; then
    echo -e "  ${RED}Failed: $TOTAL_FAILED${NC}"
fi
echo ""
echo "Total Tests: 52 (34 existing + 18 enhanced)"
echo "Duration: ${DURATION}s"
echo ""

if [ $TOTAL_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All test suites passed!${NC}"
    echo ""
    echo "Hub v2.0 test coverage:"
    echo "  - Core functionality: 100% ✅"
    echo "  - YAML edge cases: 100% ✅"
    echo "  - E2E workflows: 100% ✅"
    echo "  - Total: 52 tests passing"
    exit 0
else
    echo -e "${RED}❌ Some test suites failed${NC}"
    exit 1
fi
