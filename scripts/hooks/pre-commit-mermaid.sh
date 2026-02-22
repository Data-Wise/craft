#!/usr/bin/env bash
#
# Pre-commit hook for Mermaid diagram validation
#
# Validates mermaid blocks in staged .md files using local regex
# pre-checks only (no MCP dependency — fast).
#
# Rules checked (error-level only):
#   - [/text] leading slash detection (parallelogram misparse)
#   - [end] lowercase end keyword (keyword conflict)
#
# Installation:
#   Included via .pre-commit-config.yaml (local hook)
#
# Manual run:
#   python3 scripts/mermaid-validate.py <files> --errors-only

set -e

# Resolve script directory (works through symlinks)
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}" 2>/dev/null || realpath "${BASH_SOURCE[0]}" 2>/dev/null || echo "${BASH_SOURCE[0]}")")" && cd .. && pwd)"
source "$SCRIPT_DIR/formatting.sh"

# Get staged markdown files
STAGED_MD_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.md$' || true)

if [ -z "$STAGED_MD_FILES" ]; then
    exit 0
fi

# Check if any staged files contain mermaid blocks
HAS_MERMAID=false
for file in $STAGED_MD_FILES; do
    if grep -q '```mermaid' "$file" 2>/dev/null; then
        HAS_MERMAID=true
        break
    fi
done

if [ "$HAS_MERMAID" = false ]; then
    exit 0
fi

# Run mermaid validation (errors only — fast local regex)
# shellcheck disable=SC2086
OUTPUT=$(python3 scripts/mermaid-validate.py $STAGED_MD_FILES --errors-only 2>&1) || {
    echo ""
    echo -e "${FMT_RED}❌${FMT_NC} Mermaid validation errors found:"
    echo "$OUTPUT"
    echo ""
    echo "Fix the issues above, then re-stage and commit."
    echo "See: python3 scripts/mermaid-validate.py <file> for details"
    echo ""
    exit 1
}

exit 0
