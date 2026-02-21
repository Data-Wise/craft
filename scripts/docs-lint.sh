#!/usr/bin/env bash
# scripts/docs-lint.sh - Markdown linting execution layer
# v2.11.0 - Executes markdownlint-cli2 with craft configuration
#            + custom emoji-attribute spacing check
#
# Usage:
#   ./scripts/docs-lint.sh              # Check markdown files
#   ./scripts/docs-lint.sh --fix        # Auto-fix issues
#   ./scripts/docs-lint.sh --fix --dry  # Preview fixes without applying
#
# Environment:
#   CLAUDE_PLUGIN_ROOT: Root of craft plugin (auto-detected)
#   MARKDOWNLINT_CONFIG: Path to config file (default: .markdownlint.json)

set -euo pipefail

# Detect project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Configuration
CONFIG_FILE="${MARKDOWNLINT_CONFIG:-.markdownlint.json}"
TARGET_PATH="${1:-.}"
DRY_RUN=false
FIX_MODE=false

# Parse arguments
for arg in "$@"; do
    case "$arg" in
        --fix)
            FIX_MODE=true
            ;;
        --dry)
            DRY_RUN=true
            ;;
    esac
done

# Detect markdownlint-cli2 installation
detect_linter() {
    if command -v markdownlint-cli2 &>/dev/null; then
        echo "markdownlint-cli2"
    else
        echo "npx markdownlint-cli2"
    fi
}

LINT_CMD=$(detect_linter)

# Handle npx fallback notification
if [[ "$LINT_CMD" == "npx "* ]]; then
    echo "ℹ️  markdownlint-cli2 not found globally" >&2
    echo "   Install with: npm install -g markdownlint-cli2" >&2
    echo "   (Using npx - slower first run)" >&2
fi

# ─── Custom check: emoji-attribute spacing (CRAFT-001) ───
# Detects `:emoji: { .class }` (space before attribute) which breaks
# MkDocs attr_list extension. Correct: `:emoji:{ .class }` (no space).
# Prettier and other formatters may insert this space automatically.
check_emoji_attr_spacing() {
    local target="$1"
    local fix="$2"
    local found=0
    local files_fixed=0

    # Collect markdown files from target
    local md_files=()
    if [ -f "$target" ]; then
        md_files=("$target")
    elif [ -d "$target" ]; then
        while IFS= read -r -d '' f; do
            md_files+=("$f")
        done < <(find "$target" -name '*.md' -type f -not -path '*/node_modules/*' -not -path '*/.pytest_cache/*' -not -path '*/brainstorm/*' -print0)
    fi

    for file in "${md_files[@]}"; do
        # Match :emoji_name: { (space between colon-close and open-brace)
        # Pattern: colon, word chars/hyphens, colon, one or more spaces, open brace
        # Use awk to skip matches inside fenced code blocks
        local matches
        matches=$(awk '/^```/{f=!f;next} !f && /:[a-z][a-z0-9_-]*: +\{/{print NR":"$0}' "$file" 2>/dev/null || true)
        if [ -n "$matches" ]; then
            while IFS= read -r match; do
                local lineno="${match%%:*}"
                local content="${match#*:}"
                # Remove leading line number from content (grep -n gives "NUM:content")
                content="${content#*:}"
                echo "  $file:$lineno CRAFT-001 Emoji-attribute spacing: remove space before {" >&2
                echo "    $content" >&2
                found=$((found + 1))
            done <<< "$matches"

            if [ "$fix" = true ]; then
                # Remove space(s) between :emoji: and { for attribute lists
                if [[ "$OSTYPE" == darwin* ]]; then
                    sed -i '' -E 's/(:[a-z][a-z0-9_-]*:) +(\{)/\1\2/g' "$file"
                else
                    sed -i -E 's/(:[a-z][a-z0-9_-]*:) +(\{)/\1\2/g' "$file"
                fi
                files_fixed=$((files_fixed + 1))
            fi
        fi
    done

    if [ "$found" -gt 0 ]; then
        echo "" >&2
        if [ "$fix" = true ]; then
            echo "CRAFT-001: Fixed $found emoji-attribute spacing issue(s) in $files_fixed file(s)" >&2
        else
            echo "CRAFT-001: Found $found emoji-attribute spacing issue(s)" >&2
            echo "  Fix: remove space between :emoji: and { so attr_list attaches correctly" >&2
            echo "  Run with --fix to auto-fix" >&2
        fi
    fi

    return "$found"
}

# ─── Run markdownlint-cli2 ───
LINT_ARGS=()
LINT_ARGS+=("$TARGET_PATH")
LINT_ARGS+=("--config" "$CONFIG_FILE")

if [ "$FIX_MODE" = true ]; then
    LINT_ARGS+=("--fix")
fi

mdl_exit=0
if [ "$DRY_RUN" = true ] && [ "$FIX_MODE" = true ]; then
    echo "📋 Preview: Files that would be modified" >&2
    echo "" >&2
    $LINT_CMD "${LINT_ARGS[@]}" || mdl_exit=$?
else
    $LINT_CMD "${LINT_ARGS[@]}" || mdl_exit=$?
fi

# ─── Run custom checks ───
echo "" >&2
echo "── Custom checks ──" >&2

craft_exit=0
if [ "$DRY_RUN" = true ] && [ "$FIX_MODE" = true ]; then
    # Dry-run: report only, don't fix
    check_emoji_attr_spacing "$TARGET_PATH" false || craft_exit=$?
else
    check_emoji_attr_spacing "$TARGET_PATH" "$FIX_MODE" || craft_exit=$?
fi

# Exit with failure if either check found issues (and not in fix mode)
if [ "$FIX_MODE" = true ]; then
    exit 0
elif [ "$mdl_exit" -ne 0 ] || [ "$craft_exit" -ne 0 ]; then
    exit 1
else
    exit 0
fi
