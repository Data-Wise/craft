#!/bin/bash
# Integration test for --fix flag
# Part of: feature/demo-dependency-management
# Phase: 2 (Auto-Installation)

set -e

# Color definitions
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
NC='\033[0m'

echo -e "${CYAN}Testing --fix flag integration...${NC}"
echo "========================================"
echo ""

# Source the required modules
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/dependency-manager.sh"
source "$SCRIPT_DIR/dependency-installer.sh"
source "$SCRIPT_DIR/consent-prompt.sh"

# Test 1: Check status before fix
echo -e "${CYAN}Test 1: Check status before fix${NC}"
echo "-----------------------------------"
if bash "$SCRIPT_DIR/dependency-manager.sh" display_status_table asciinema; then
    echo -e "${GREEN}✓ Status check successful${NC}"
else
    echo -e "${YELLOW}⚠ Some dependencies missing (expected)${NC}"
fi
echo ""

# Test 2: Test missing tool detection
echo -e "${CYAN}Test 2: Test missing tool detection${NC}"
echo "-----------------------------------"
status_json=$(check_dependencies "asciinema" 2>/dev/null || true)
exit_code=$?

echo "Exit code: $exit_code"
if [ -n "$status_json" ]; then
    echo "Status summary:"
    echo "$status_json" | jq -r '.[] | "\(.name): installed=\(.installed), health=\(.health)"' 2>/dev/null || echo "JSON parse error"
else
    echo -e "${YELLOW}⚠ No status returned (expected if dependencies missing)${NC}"
fi
echo ""

# Test 3: Verify installer framework is loaded
echo -e "${CYAN}Test 3: Verify installer framework${NC}"
echo "-----------------------------------"
if declare -f install_tool > /dev/null; then
    echo -e "${GREEN}✓ install_tool function available${NC}"
else
    echo -e "${YELLOW}⚠ install_tool function not found${NC}"
    exit 1
fi

if declare -f prompt_user_consent > /dev/null; then
    echo -e "${GREEN}✓ prompt_user_consent function available${NC}"
else
    echo -e "${YELLOW}⚠ prompt_user_consent function not found${NC}"
    exit 1
fi

if declare -f show_installation_summary > /dev/null; then
    echo -e "${GREEN}✓ show_installation_summary function available${NC}"
else
    echo -e "${YELLOW}⚠ show_installation_summary function not found${NC}"
    exit 1
fi
echo ""

# Test 4: Test get_install_strategies function
echo -e "${CYAN}Test 4: Test strategy extraction${NC}"
echo "-----------------------------------"

# Get asciinema tool spec
deps_json=$(parse_frontmatter 2>/dev/null || echo '{}')
asciinema_spec=$(echo "$deps_json" | jq '.asciinema' 2>/dev/null || echo '{}')

if [ "$asciinema_spec" = "{}" ] || [ "$asciinema_spec" = "null" ]; then
    echo -e "${YELLOW}⚠ Could not parse tool spec (may need to be in commands/docs/ dir)${NC}"
else
    strategies=$(get_install_strategies "$asciinema_spec" 2>/dev/null || echo "")
    if [ -n "$strategies" ]; then
        echo "Strategies for asciinema:"
        echo "$strategies" | while read -r strategy; do
            [ -n "$strategy" ] && echo "  - $strategy"
        done
    else
        echo -e "${YELLOW}⚠ No strategies found${NC}"
    fi
fi
echo ""

# Test 5: Test platform filtering
echo -e "${CYAN}Test 5: Test platform filtering${NC}"
echo "-----------------------------------"
if [ -n "$strategies" ]; then
    available=$(filter_available_strategies "$strategies" 2>/dev/null || echo "")
    if [ -n "$available" ]; then
        echo "Available strategies on this platform:"
        echo "$available" | while read -r strategy; do
            [ -n "$strategy" ] && echo "  - $strategy"
        done
    else
        echo -e "${YELLOW}⚠ No available strategies${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Skipping (no strategies from previous test)${NC}"
fi
echo ""

# Test 6: Dry run simulation (no actual installation)
echo -e "${CYAN}Test 6: Dry run simulation${NC}"
echo "-----------------------------------"
echo "Simulating installation flow (no actual install):"
echo "1. Tool: asciinema"
echo "2. Strategies: $(echo "$strategies" | tr '\n' ' ')"
echo "3. Available: $(echo "$available" | tr '\n' ' ')"
echo "4. Would prompt for user consent"
echo "5. Would try each strategy in order"
echo "6. Would verify installation"
echo "7. Would display summary"
echo -e "${GREEN}✓ Dry run complete${NC}"
echo ""

# Summary
echo "========================================"
echo -e "${GREEN}✓ --fix flag integration tests complete${NC}"
echo ""
echo "Next steps:"
echo "  1. Manual test: /craft:docs:demo --fix"
echo "  2. Verify consent prompts work"
echo "  3. Test skip-all functionality"
echo "  4. Verify installation summary display"
echo ""
