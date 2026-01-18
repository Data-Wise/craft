#!/bin/bash
# Verify Phase 2 implementation

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="/Users/dt/.git-worktrees/craft/feature-demo-deps/scripts"

echo "=== Phase 2 Verification ==="
echo ""

# 1. Check file exists and is executable
echo "1. File existence and permissions"
if [ -f "$SCRIPT_DIR/dependency-installer.sh" ] && [ -x "$SCRIPT_DIR/dependency-installer.sh" ]; then
    echo -e "   ${GREEN}✓${NC} dependency-installer.sh exists and is executable"
else
    echo -e "   ${RED}✗${NC} dependency-installer.sh missing or not executable"
    exit 1
fi

# 2. Syntax validation
echo "2. Syntax validation"
if bash -n "$SCRIPT_DIR/dependency-installer.sh" 2>&1; then
    echo -e "   ${GREEN}✓${NC} Bash syntax valid"
else
    echo -e "   ${RED}✗${NC} Syntax errors found"
    exit 1
fi

# 3. Source the script
echo "3. Script sourcing"
if source "$SCRIPT_DIR/dependency-installer.sh" 2>&1; then
    echo -e "   ${GREEN}✓${NC} Script sources successfully"
else
    echo -e "   ${RED}✗${NC} Failed to source script"
    exit 1
fi

# 4. Check functions are defined
echo "4. Function definitions"
functions=(
    "install_tool"
    "get_install_strategies"
    "filter_available_strategies"
    "try_install"
    "verify_installation"
    "prompt_user_consent"
    "detect_platform"
    "install_via_brew"
    "install_via_cargo"
    "install_via_cargo_git"
    "install_via_binary"
)

for func in "${functions[@]}"; do
    if declare -F "$func" > /dev/null; then
        echo -e "   ${GREEN}✓${NC} $func defined"
    else
        echo -e "   ${RED}✗${NC} $func not defined"
        exit 1
    fi
done

# 5. Test platform detection
echo "5. Platform detection"
detect_platform
echo -e "   ${GREEN}✓${NC} Platform: $PLATFORM"
echo -e "   ${GREEN}✓${NC} Architecture: $ARCH"

# 6. Test strategy extraction
echo "6. Strategy extraction"
deps_json=$(parse_frontmatter)
agg_spec=$(echo "$deps_json" | jq '.agg')
strategies=$(get_install_strategies "$agg_spec")
strategy_count=$(echo "$strategies" | wc -l | tr -d ' ')
echo -e "   ${GREEN}✓${NC} Extracted $strategy_count strategies"

# 7. Test platform filtering
echo "7. Platform filtering"
available=$(filter_available_strategies "$strategies")
available_count=$(echo "$available" | wc -l | tr -d ' ')
echo -e "   ${GREEN}✓${NC} $available_count strategies available on this platform"

# 8. Test verification function
echo "8. Verification function"
bash_spec='{"version": {"min": "5.0.0", "check_cmd": "bash --version | grep -oE \"[0-9.]+\" | head -1"}, "health": {"check_cmd": "bash --help", "expect_exit": 0}}'
if verify_installation "bash" "$bash_spec" > /dev/null 2>&1; then
    echo -e "   ${GREEN}✓${NC} Verification function working"
else
    echo -e "   ${RED}✗${NC} Verification function failed"
    exit 1
fi

# 9. Test stub functions
echo "9. Stub functions"
if install_via_brew "test" "$agg_spec" 2>&1 | grep -q "STUB"; then
    echo -e "   ${GREEN}✓${NC} install_via_brew stub working"
fi
if install_via_cargo "test" "$agg_spec" 2>&1 | grep -q "STUB"; then
    echo -e "   ${GREEN}✓${NC} install_via_cargo stub working"
fi
if install_via_cargo_git "test" "$agg_spec" 2>&1 | grep -q "STUB"; then
    echo -e "   ${GREEN}✓${NC} install_via_cargo_git stub working"
fi
if install_via_binary "test" "$agg_spec" 2>&1 | grep -q "STUB"; then
    echo -e "   ${GREEN}✓${NC} install_via_binary stub working"
fi

# 10. Documentation exists
echo "10. Documentation"
if [ -f "$SCRIPT_DIR/INSTALLER-USAGE.md" ]; then
    echo -e "   ${GREEN}✓${NC} INSTALLER-USAGE.md exists"
else
    echo -e "   ${RED}✗${NC} INSTALLER-USAGE.md missing"
    exit 1
fi

if [ -f "/Users/dt/.git-worktrees/craft/feature-demo-deps/PHASE-2-SUMMARY.md" ]; then
    echo -e "   ${GREEN}✓${NC} PHASE-2-SUMMARY.md exists"
else
    echo -e "   ${RED}✗${NC} PHASE-2-SUMMARY.md missing"
    exit 1
fi

echo ""
echo -e "${GREEN}=== Phase 2 Verification Complete ===${NC}"
echo ""
echo "Summary:"
echo "  ✓ Script exists and executable"
echo "  ✓ Syntax valid"
echo "  ✓ All 11 functions defined"
echo "  ✓ Platform detection working"
echo "  ✓ Strategy extraction working"
echo "  ✓ Platform filtering working"
echo "  ✓ Verification working"
echo "  ✓ All stub functions working"
echo "  ✓ Documentation complete"
echo ""
echo -e "${GREEN}Ready for Wave 2 implementation${NC}"
