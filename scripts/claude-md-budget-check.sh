#!/usr/bin/env bash
# scripts/claude-md-budget-check.sh - CLAUDE.md budget enforcement
# Checks that CLAUDE.md files don't exceed the configured line budget.
# Default budget: 150 lines. Override in .claude-plugin/plugin.json:
#   { "claude_md_budget": 200 }
#
# Usage:
#   bash scripts/claude-md-budget-check.sh          # Check staged CLAUDE.md files
#   bash scripts/claude-md-budget-check.sh --all    # Check all CLAUDE.md files in repo

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

DEFAULT_BUDGET=150
ERRORS=0

# Read budget from plugin.json if available
read_budget() {
    local config=".claude-plugin/plugin.json"
    if [[ -f "$config" ]]; then
        local budget
        budget=$(python3 -c "import json; d=json.load(open('$config')); print(d.get('claude_md_budget', $DEFAULT_BUDGET))" 2>/dev/null || echo "$DEFAULT_BUDGET")
        echo "$budget"
    else
        echo "$DEFAULT_BUDGET"
    fi
}

BUDGET=$(read_budget)

# Find CLAUDE.md files to check
if [[ "${1:-}" == "--all" ]]; then
    # Check all CLAUDE.md files
    FILES=$(find "$PROJECT_ROOT" -name "CLAUDE.md" -type f \
        -not -path '*/.git/*' \
        -not -path '*/node_modules/*' \
        -not -path '*/.pytest_cache/*' \
        2>/dev/null || true)
else
    # Check only staged CLAUDE.md files
    FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null | grep -i 'CLAUDE\.md$' || true)
fi

if [[ -z "$FILES" ]]; then
    exit 0
fi

for file in $FILES; do
    if [[ -f "$file" ]]; then
        LINES=$(wc -l < "$file" | tr -d ' ')
        if [[ "$LINES" -gt "$BUDGET" ]]; then
            echo "  $file: $LINES lines (budget: $BUDGET)" >&2
            ERRORS=$((ERRORS + 1))
        fi
    fi
done

if [[ "$ERRORS" -gt 0 ]]; then
    echo "" >&2
    echo "CLAUDE.md budget exceeded in $ERRORS file(s)." >&2
    echo "  Budget: $BUDGET lines (configure in .claude-plugin/plugin.json)" >&2
    echo "  Run: /craft:docs:claude-md:sync --optimize" >&2
    exit 1
fi

exit 0
