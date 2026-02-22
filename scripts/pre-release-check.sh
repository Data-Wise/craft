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
#   4. README.md and docs/index.md version references are current
#   5. marketplace.json version consistency (if exists)
#   6. No uncommitted changes
#   7. Badge URL branch validation (main + dev)
#   8. Homebrew formula desc consistency

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
echo -e "${CYAN}[1/8] Plugin version consistency${NC}"

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
echo -e "${CYAN}[2/8] Command/skill/agent counts${NC}"

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
echo -e "${CYAN}[3/8] CLAUDE.md version references${NC}"

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
# Check 4: README.md and docs/index.md version references
# --------------------------------------------------------------------------
echo ""
echo -e "${CYAN}[4/8] README.md and docs/index.md version references${NC}"

STALE_FILES=""

if [ -f "README.md" ]; then
    README_VERSION=$(grep -o 'version-[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*' README.md | head -1 | sed 's/version-//' || echo "")
    if [ -n "$README_VERSION" ] && [ "$README_VERSION" != "$TARGET_VERSION" ]; then
        echo -e "${RED}  ✗ README.md version badge: v${README_VERSION} (target: v${TARGET_VERSION})${NC}"
        STALE_FILES="$STALE_FILES README.md"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}  ✓ README.md version badge OK${NC}"
    fi
fi

if [ -f "docs/index.md" ]; then
    INDEX_VERSION=$(grep -o 'v[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*' docs/index.md | head -1 | sed 's/^v//' || echo "")
    if [ -n "$INDEX_VERSION" ] && [ "$INDEX_VERSION" != "$TARGET_VERSION" ]; then
        echo -e "${RED}  ✗ docs/index.md latest version: v${INDEX_VERSION} (target: v${TARGET_VERSION})${NC}"
        STALE_FILES="$STALE_FILES docs/index.md"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}  ✓ docs/index.md version OK${NC}"
    fi
fi

if [ -n "$STALE_FILES" ]; then
    echo -e "${YELLOW}    Fix: Update version references in:${STALE_FILES}${NC}"
fi

# --------------------------------------------------------------------------
# Check 5: marketplace.json version consistency
# --------------------------------------------------------------------------
echo ""
echo -e "${CYAN}[5/8] Marketplace version consistency${NC}"

MARKETPLACE_JSON=".claude-plugin/marketplace.json"
if [ -f "$MARKETPLACE_JSON" ]; then
    MKT_META_VERSION=$(python3 -c "import json; print(json.load(open('$MARKETPLACE_JSON'))['metadata']['version'])")
    MKT_PLUGIN_VERSION=$(python3 -c "import json; d=json.load(open('$MARKETPLACE_JSON')); print(d['plugins'][0]['version'] if d.get('plugins') else '')" 2>/dev/null || echo "")

    if [ "$MKT_META_VERSION" != "$TARGET_VERSION" ]; then
        echo -e "${RED}  ✗ marketplace.json metadata.version ($MKT_META_VERSION) != target ($TARGET_VERSION)${NC}"
        echo -e "${YELLOW}    Fix: Update .claude-plugin/marketplace.json metadata.version to \"$TARGET_VERSION\"${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}  ✓ marketplace.json metadata.version matches: $MKT_META_VERSION${NC}"
    fi

    if [ -n "$MKT_PLUGIN_VERSION" ] && [ "$MKT_PLUGIN_VERSION" != "$TARGET_VERSION" ]; then
        echo -e "${RED}  ✗ marketplace.json plugins[0].version ($MKT_PLUGIN_VERSION) != target ($TARGET_VERSION)${NC}"
        echo -e "${YELLOW}    Fix: Update .claude-plugin/marketplace.json plugins[0].version to \"$TARGET_VERSION\"${NC}"
        ERRORS=$((ERRORS + 1))
    elif [ -n "$MKT_PLUGIN_VERSION" ]; then
        echo -e "${GREEN}  ✓ marketplace.json plugins[0].version matches: $MKT_PLUGIN_VERSION${NC}"
    fi
else
    echo -e "${YELLOW}  - marketplace.json not found (skipping — not all projects use marketplace)${NC}"
fi

# --------------------------------------------------------------------------
# Check 6: Uncommitted changes
# --------------------------------------------------------------------------
echo ""
echo -e "${CYAN}[6/8] Working tree status${NC}"

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
# Check 7: Badge URL branch validation
# --------------------------------------------------------------------------
echo ""
echo -e "${CYAN}[7/8] Badge URL branch validation${NC}"

BADGE_ERRORS=0
for file in README.md docs/index.md; do
    if [ -f "$file" ]; then
        if ! grep -q 'badge.svg?branch=main' "$file"; then
            echo -e "${RED}  ✗ $file missing main branch badge${NC}"
            BADGE_ERRORS=$((BADGE_ERRORS + 1))
        fi
        if ! grep -q 'badge.svg?branch=dev' "$file"; then
            echo -e "${RED}  ✗ $file missing dev branch badge${NC}"
            BADGE_ERRORS=$((BADGE_ERRORS + 1))
        fi
    fi
done

if [ $BADGE_ERRORS -gt 0 ]; then
    echo -e "${RED}  ✗ $BADGE_ERRORS badge URL issues found${NC}"
    echo -e "${YELLOW}    Fix: Add main and dev badges to README.md and docs/index.md${NC}"
    ERRORS=$((ERRORS + BADGE_ERRORS))
else
    echo -e "${GREEN}  ✓ Both main and dev badges present${NC}"
fi

# --------------------------------------------------------------------------
# Check 8: Homebrew formula desc consistency
# --------------------------------------------------------------------------
echo ""
echo -e "${CYAN}[8/8] Homebrew formula desc consistency${NC}"

FORMULA_PATH=""
for candidate in \
    "$HOME/projects/dev-tools/homebrew-tap/Formula/craft.rb" \
    "$(brew --repository 2>/dev/null)/Library/Taps/data-wise/homebrew-tap/Formula/craft.rb"; do
    if [ -f "$candidate" ]; then
        FORMULA_PATH="$candidate"
        break
    fi
done

if [ -n "$FORMULA_PATH" ]; then
    FORMULA_DESC=$(grep '^  desc ' "$FORMULA_PATH" | head -1 | sed 's/.*desc "\(.*\)"/\1/')
    FORMULA_CMD_COUNT=$(echo "$FORMULA_DESC" | grep -o '[0-9]* commands' | grep -o '[0-9]*' || echo "")
    if [ -n "$FORMULA_CMD_COUNT" ] && [ "$FORMULA_CMD_COUNT" != "$CMD_COUNT" ]; then
        echo -e "${YELLOW}  ! Formula desc says $FORMULA_CMD_COUNT commands, actual is $CMD_COUNT${NC}"
    elif [ -n "$FORMULA_CMD_COUNT" ]; then
        echo -e "${GREEN}  ✓ Formula command count matches: $FORMULA_CMD_COUNT${NC}"
    fi
    echo -e "${GREEN}  ✓ Formula desc: \"$FORMULA_DESC\"${NC}"
else
    echo -e "${YELLOW}  - Homebrew formula not found locally (skipping)${NC}"
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
