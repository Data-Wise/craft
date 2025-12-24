#!/usr/bin/env bash
#
# Git pre-commit hook for Claude Code plugins
#
# Install: ln -sf ../../scripts/pre-commit-hook.sh .git/hooks/pre-commit
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Running pre-commit validation..."
echo ""

# Get staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

# Check if any plugin files are staged
PLUGIN_FILES=$(echo "$STAGED_FILES" | grep -E '(rforge-orchestrator|statistical-research|workflow)/' || true)

if [ -z "$PLUGIN_FILES" ]; then
    echo -e "${GREEN}✅ No plugin files changed${NC}"
    exit 0
fi

# Validate JSON files
echo "Checking JSON files..."
JSON_FILES=$(echo "$STAGED_FILES" | grep '\.json$' || true)

if [ -n "$JSON_FILES" ]; then
    for file in $JSON_FILES; do
        if [ -f "$file" ]; then
            if ! python3 -m json.tool "$file" > /dev/null 2>&1; then
                echo -e "${RED}❌ Invalid JSON: $file${NC}"
                exit 1
            fi
        fi
    done
    echo -e "${GREEN}✅ All JSON files valid${NC}"
fi

# Check command frontmatter
echo "Checking command frontmatter..."
CMD_FILES=$(echo "$STAGED_FILES" | grep 'commands/.*\.md$' || true)

if [ -n "$CMD_FILES" ]; then
    for file in $CMD_FILES; do
        if [ -f "$file" ]; then
            if ! head -n 5 "$file" | grep -q "^name:"; then
                echo -e "${RED}❌ Missing 'name:' field in frontmatter: $file${NC}"
                echo -e "${YELLOW}   Add YAML frontmatter with 'name:' field${NC}"
                exit 1
            fi
        fi
    done
    echo -e "${GREEN}✅ All command files have proper frontmatter${NC}"
fi

# Run comprehensive validation if Python script exists
if [ -f "scripts/validate-all-plugins.py" ]; then
    echo ""
    echo "Running comprehensive validation..."
    if python3 scripts/validate-all-plugins.py; then
        echo ""
        echo -e "${GREEN}✅ All pre-commit checks passed${NC}"
        exit 0
    else
        echo ""
        echo -e "${RED}❌ Validation failed${NC}"
        echo -e "${YELLOW}Fix errors and try again${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Basic checks passed${NC}"
    exit 0
fi
