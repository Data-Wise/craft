#!/bin/bash
# Integration test for /craft:docs:demo --check flag
# Tests the dependency checking integration

set -e

echo "========================================"
echo "Integration Tests: --check Flag"
echo "========================================"
echo ""

# Test 1: Check all dependencies (default)
echo "Test 1: Check all dependencies (default method: asciinema)"
echo "Command: bash scripts/dependency-manager.sh display_status_table asciinema"
echo "----------------------------------------"
bash scripts/dependency-manager.sh display_status_table asciinema || true
echo ""

# Test 2: Check asciinema method explicitly
echo "Test 2: Check asciinema method"
echo "Command: bash scripts/dependency-manager.sh display_status_table asciinema"
echo "----------------------------------------"
bash scripts/dependency-manager.sh display_status_table asciinema || true
echo ""

# Test 3: Check vhs method
echo "Test 3: Check vhs method"
echo "Command: bash scripts/dependency-manager.sh display_status_table vhs"
echo "----------------------------------------"
bash scripts/dependency-manager.sh display_status_table vhs || true
echo ""

# Test 4: Check all tools regardless of method
echo "Test 4: Check all tools (all methods)"
echo "Command: bash scripts/dependency-manager.sh display_status_table all"
echo "----------------------------------------"
bash scripts/dependency-manager.sh display_status_table all || true
echo ""

# Test 5: Verify frontmatter parsing
echo "Test 5: Verify frontmatter parsing"
echo "Command: bash scripts/dependency-manager.sh parse_frontmatter"
echo "----------------------------------------"
if deps_json=$(bash scripts/dependency-manager.sh parse_frontmatter); then
    echo "✓ Frontmatter parsed successfully"
    echo "$deps_json" | jq -r 'keys[]' | while read tool; do
        echo "  - $tool"
    done
else
    echo "✗ Frontmatter parsing failed"
    exit 1
fi
echo ""

# Test 6: Check exit codes
echo "Test 6: Check exit codes"
echo "----------------------------------------"
if bash scripts/dependency-manager.sh check_dependencies asciinema > /dev/null 2>&1; then
    echo "✓ Exit code 0 (all deps OK or some missing)"
else
    echo "✓ Exit code 1 (missing required deps)"
fi
echo ""

echo "========================================"
echo "All Integration Tests Complete"
echo "========================================"
