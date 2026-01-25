#!/usr/bin/env bash
# scripts/docs-lint.sh - Markdown linting execution layer
# v2.8.0 - Executes markdownlint-cli2 with craft configuration
#
# Usage:
#   ./scripts/docs-lint.sh              # Check markdown files
#   ./scripts/docs-lint.sh --fix        # Auto-fix issues
#   ./scripts/docs-lint.sh --fix --dry  # Preview fixes without applying
#
# Environment:
#   CRAFT_PLUGIN_ROOT: Root of craft plugin (auto-detected)
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

# Build lint command
LINT_ARGS=()
LINT_ARGS+=("$TARGET_PATH")
LINT_ARGS+=("--config" "$CONFIG_FILE")

if [ "$FIX_MODE" = true ]; then
    LINT_ARGS+=("--fix")
fi

# Execute linting
if [ "$DRY_RUN" = true ] && [ "$FIX_MODE" = true ]; then
    # Dry-run: show what would be fixed
    echo "📋 Preview: Files that would be modified" >&2
    echo "" >&2
    $LINT_CMD "${LINT_ARGS[@]}" || true
else
    # Normal execution
    $LINT_CMD "${LINT_ARGS[@]}"
fi
