#!/usr/bin/env bash
# scripts/docs-lint-emoji.sh - Standalone CRAFT-001 emoji-attribute spacing check
# Extracted from docs-lint.sh for use as a pre-commit hook.
#
# Detects `:emoji: { .class }` (space before attribute) which breaks
# MkDocs attr_list extension. Correct: `:emoji:{ .class }` (no space).
# Prettier and other formatters may insert this space automatically.
#
# Usage:
#   ./scripts/docs-lint-emoji.sh          # Check all markdown files
#   ./scripts/docs-lint-emoji.sh --fix    # Auto-fix issues

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

FIX_MODE=false
for arg in "$@"; do
    case "$arg" in
        --fix) FIX_MODE=true ;;
    esac
done

found=0
files_fixed=0

while IFS= read -r -d '' file; do
    # Use awk to skip matches inside fenced code blocks
    matches=$(awk '/^```/{f=!f;next} !f && /:[a-z][a-z0-9_-]*: +\{/{print NR":"$0}' "$file" 2>/dev/null || true)
    if [ -n "$matches" ]; then
        while IFS= read -r match; do
            lineno="${match%%:*}"
            content="${match#*:}"
            content="${content#*:}"
            echo "  $file:$lineno CRAFT-001 Emoji-attribute spacing: remove space before {" >&2
            echo "    $content" >&2
            found=$((found + 1))
        done <<< "$matches"

        if [ "$FIX_MODE" = true ]; then
            if [[ "$OSTYPE" == darwin* ]]; then
                sed -i '' -E 's/(:[a-z][a-z0-9_-]*:) +(\{)/\1\2/g' "$file"
            else
                sed -i -E 's/(:[a-z][a-z0-9_-]*:) +(\{)/\1\2/g' "$file"
            fi
            files_fixed=$((files_fixed + 1))
        fi
    fi
done < <(find "$PROJECT_ROOT" -name '*.md' -type f \
    -not -path '*/node_modules/*' \
    -not -path '*/.pytest_cache/*' \
    -not -path '*/brainstorm/*' \
    -not -path '*/fixtures/*' \
    -print0)

if [ "$found" -gt 0 ]; then
    echo "" >&2
    if [ "$FIX_MODE" = true ]; then
        echo "CRAFT-001: Fixed $found emoji-attribute spacing issue(s) in $files_fixed file(s)" >&2
    else
        echo "CRAFT-001: Found $found emoji-attribute spacing issue(s)" >&2
        echo "  Fix: remove space between :emoji: and { so attr_list attaches correctly" >&2
        echo "  Run with --fix to auto-fix" >&2
        exit 1
    fi
fi

exit 0
