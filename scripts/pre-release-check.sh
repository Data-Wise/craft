#!/bin/bash
# pre-release-check.sh - Validate release consistency before tagging
#
# Usage:
#   ./scripts/pre-release-check.sh 2.13.0          # Check against specific version
#   ./scripts/pre-release-check.sh                  # Auto-detect from latest git tag
#
# Checks:
#   1. plugin.json version matches intended release
#   2. Actual command/skill/agent counts match plugin.json description
#   3. CLAUDE.md version references are current
#   4. No uncommitted changes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"

# Colors (shared library)
source "$SCRIPT_DIR/formatting.sh"
RED="$FMT_RED"
GREEN="$FMT_GREEN"
YELLOW="$FMT_YELLOW"
CYAN="$FMT_CYAN"
NC="$FMT_NC"

cd "$PLUGIN_DIR"

# Determine target version
if [ -n "$1" ]; then
    TARGET_VERSION="$1"
else
    # Auto-detect from latest git tag
    TARGET_VERSION=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/^v//')
    if [ -z "$TARGET_VERSION" ]; then
        echo -e "${RED}Error: No version argument and no git tags found${NC}"
        echo "Usage: $0 <version>"
        exit 1
    fi
fi

echo -e "${CYAN}Pre-Release Validation for v${TARGET_VERSION}${NC}"
echo "==========================================="
echo ""

ERRORS=0

# --------------------------------------------------------------------------
# Check 1: plugin.json version matches target
# --------------------------------------------------------------------------
echo -e "${CYAN}[1/4] Plugin version consistency${NC}"

PLUGIN_JSON=".claude-plugin/plugin.json"
if [ ! -f "$PLUGIN_JSON" ]; then
    echo -e "${RED}  ✗ plugin.json not found${NC}"
    ERRORS=$((ERRORS + 1))
else
    PLUGIN_VERSION=$(python3 -c "import json; print(json.load(open('$PLUGIN_JSON'))['version'])")
    if [ "$PLUGIN_VERSION" != "$TARGET_VERSION" ]; then
        echo -e "${RED}  ✗ plugin.json version ($PLUGIN_VERSION) != target ($TARGET_VERSION)${NC}"
        echo -e "${YELLOW}    Fix: Update .claude-plugin/plugin.json version to \"$TARGET_VERSION\"${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}  ✓ plugin.json version matches: $PLUGIN_VERSION${NC}"
    fi
fi

# --------------------------------------------------------------------------
# Check 2: Actual counts match plugin.json description
# --------------------------------------------------------------------------
echo ""
echo -e "${CYAN}[2/4] Command/skill/agent counts${NC}"

# Count actual files (same logic as validate-counts.sh)
CMD_COUNT=$(find commands -name "*.md" ! -name "index.md" ! -name "README.md" 2>/dev/null | wc -l | tr -d ' ')
SKILL_COUNT=$(find skills -name "*.md" -o -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
AGENT_COUNT=$(find agents -name "*.md" 2>/dev/null | wc -l | tr -d ' ')

# Extract documented counts from plugin.json description
DESC=$(python3 -c "import json; print(json.load(open('$PLUGIN_JSON'))['description'])")
DOC_CMDS=$(echo "$DESC" | grep -o '[0-9]* commands' | head -1 | grep -o '[0-9]*' || echo "?")
DOC_AGENTS=$(echo "$DESC" | grep -o '[0-9]* agents' | grep -o '[0-9]*' || echo "?")
DOC_SKILLS=$(echo "$DESC" | grep -o '[0-9]* skills' | grep -o '[0-9]*' || echo "?")

if [ "$CMD_COUNT" != "$DOC_CMDS" ]; then
    echo -e "${RED}  ✗ Commands: $CMD_COUNT actual vs $DOC_CMDS in plugin.json${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}  ✓ Commands: $CMD_COUNT${NC}"
fi

if [ "$SKILL_COUNT" != "$DOC_SKILLS" ]; then
    echo -e "${RED}  ✗ Skills: $SKILL_COUNT actual vs $DOC_SKILLS in plugin.json${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}  ✓ Skills: $SKILL_COUNT${NC}"
fi

if [ "$AGENT_COUNT" != "$DOC_AGENTS" ]; then
    echo -e "${RED}  ✗ Agents: $AGENT_COUNT actual vs $DOC_AGENTS in plugin.json${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}  ✓ Agents: $AGENT_COUNT${NC}"
fi

# --------------------------------------------------------------------------
# Check 3: CLAUDE.md version references
# --------------------------------------------------------------------------
echo ""
echo -e "${CYAN}[3/4] CLAUDE.md version references${NC}"

if [ -f "CLAUDE.md" ]; then
    # Check "Current Version" line
    CLAUDE_VERSION=$(grep -o 'Current Version:.*v[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*' CLAUDE.md | grep -o '[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*' | head -1 || echo "")
    if [ -n "$CLAUDE_VERSION" ] && [ "$CLAUDE_VERSION" != "$TARGET_VERSION" ]; then
        echo -e "${YELLOW}  ! CLAUDE.md references v${CLAUDE_VERSION} (target: v${TARGET_VERSION})${NC}"
        echo -e "${YELLOW}    Note: CLAUDE.md is typically updated post-release${NC}"
    else
        echo -e "${GREEN}  ✓ CLAUDE.md version references OK${NC}"
    fi
else
    echo -e "${YELLOW}  ! CLAUDE.md not found (skipping)${NC}"
fi

# --------------------------------------------------------------------------
# Check 4: Uncommitted changes
# --------------------------------------------------------------------------
echo ""
echo -e "${CYAN}[4/4] Working tree status${NC}"

if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
    echo -e "${YELLOW}  ! Uncommitted changes detected${NC}"
    git status --short | head -10 | while read -r line; do
        echo "    $line"
    done
    echo -e "${YELLOW}    Warning: Release tag should be on a clean commit${NC}"
else
    echo -e "${GREEN}  ✓ Working tree clean${NC}"
fi

# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------
echo ""
echo "==========================================="

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}FAILED: $ERRORS error(s) found — fix before releasing v${TARGET_VERSION}${NC}"
    exit 1
else
    echo -e "${GREEN}PASSED: Ready to release v${TARGET_VERSION}${NC}"
    echo ""
    echo "  Counts: $CMD_COUNT commands, $AGENT_COUNT agents, $SKILL_COUNT skills"
fi
