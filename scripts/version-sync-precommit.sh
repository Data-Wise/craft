#!/usr/bin/env bash
# scripts/version-sync-precommit.sh — Git pre-commit hook
# BLOCKS commits with version mismatches.
#
# Installation:
#   ln -sf ../../scripts/version-sync-precommit.sh .git/hooks/pre-commit
#   # Or add to .husky/pre-commit or .githooks/pre-commit
#
# This hook checks staged files for version references that don't match
# the project's source of truth. It prevents version drift from reaching
# the repository.

set -euo pipefail

# Find source of truth version
SOT="" SOT_FILE=""

if [[ -f .claude-plugin/plugin.json ]]; then
    SOT=$(jq -r '.version // empty' .claude-plugin/plugin.json 2>/dev/null)
    SOT_FILE=".claude-plugin/plugin.json"
elif [[ -f package.json ]]; then
    SOT=$(jq -r '.version // empty' package.json 2>/dev/null)
    SOT_FILE="package.json"
elif [[ -f pyproject.toml ]]; then
    SOT=$(grep -m1 '^version' pyproject.toml | sed 's/.*"\(.*\)"/\1/' 2>/dev/null)
    SOT_FILE="pyproject.toml"
elif [[ -f DESCRIPTION ]]; then
    SOT=$(grep -m1 '^Version:' DESCRIPTION | awk '{print $2}' 2>/dev/null)
    SOT_FILE="DESCRIPTION"
elif [[ -f Cargo.toml ]]; then
    SOT=$(grep -m1 '^version' Cargo.toml | sed 's/.*"\(.*\)"/\1/' 2>/dev/null)
    SOT_FILE="Cargo.toml"
else
    exit 0  # No version file, skip
fi

[[ -z "$SOT" ]] && exit 0

ERRORS=0

# Check staged files for version mismatches
while IFS= read -r FILE; do
    FILE_VER=""

    case "$FILE" in
        *.json)
            FILE_VER=$(git show ":$FILE" 2>/dev/null | jq -r '.version // empty' 2>/dev/null)
            ;;
        CLAUDE.md)
            FILE_VER=$(git show ":$FILE" 2>/dev/null | grep -E 'Current Version:' | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
            ;;
        *.py)
            FILE_VER=$(git show ":$FILE" 2>/dev/null | grep -E '(__version__|VERSION)\s*=' | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
            ;;
        *.ts|*.js)
            FILE_VER=$(git show ":$FILE" 2>/dev/null | grep -E 'VERSION\s*=' | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
            ;;
        DESCRIPTION)
            FILE_VER=$(git show ":$FILE" 2>/dev/null | grep -m1 '^Version:' | awk '{print $2}')
            ;;
        *.toml)
            FILE_VER=$(git show ":$FILE" 2>/dev/null | grep -m1 '^version' | sed 's/.*"\(.*\)"/\1/')
            ;;
        .STATUS)
            FILE_VER=$(git show ":$FILE" 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
            ;;
        *)
            continue
            ;;
    esac

    # Skip the SOT file itself, and skip if no version found
    [[ "$FILE" == "$SOT_FILE" ]] && continue
    [[ -z "$FILE_VER" ]] && continue

    if [[ "$FILE_VER" != "$SOT" ]]; then
        echo "❌ Version mismatch: $FILE has v$FILE_VER (expected v$SOT from $SOT_FILE)"
        ERRORS=$((ERRORS + 1))
    fi
done < <(git diff --cached --name-only)

if [[ $ERRORS -gt 0 ]]; then
    echo ""
    echo "Fix: Update the $ERRORS file(s) above to v$SOT"
    echo "Or update $SOT_FILE if the version should change."
    exit 1
fi

exit 0
