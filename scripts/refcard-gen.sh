#!/usr/bin/env bash
# refcard-gen.sh — generate REFCARD table rows from command frontmatter
# Usage:
#   refcard-gen.sh [--root DIR] [--category CAT] [--check]
#
# --root DIR      : project root (default: parent of this script)
# --category CAT  : only emit rows for this category
# --check         : exit 1 if generated output differs from docs/REFCARD.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${SCRIPT_DIR}/.."
CATEGORY_FILTER=""
CHECK_MODE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --root)     ROOT="$2"; shift 2 ;;
        --category) CATEGORY_FILTER="$2"; shift 2 ;;
        --check)    CHECK_MODE=true; shift ;;
        *) echo "Unknown argument: $1" >&2; exit 1 ;;
    esac
done

COMMANDS_DIR="$ROOT/commands"
REFCARD="$ROOT/docs/REFCARD.md"

# Extract a single frontmatter field value from a command file.
# Works with BSD sed (macOS) and GNU sed.
get_field() {
    local file="$1" field="$2"
    sed -n '/^---$/,/^---$/{
        /^'"$field"':/s/^'"$field"':[[:space:]]*//p
    }' "$file" 2>/dev/null | head -1 | tr -d "\"'"
}

# Collect rows per category
declare -A cat_rows

while IFS= read -r cmd_file; do
    [[ -f "$cmd_file" ]] || continue

    deprecated=$(get_field "$cmd_file" "deprecated")
    internal=$(get_field  "$cmd_file" "internal")
    [[ "$deprecated" == "true" ]] && continue
    [[ "$internal"   == "true" ]] && continue

    category=$(get_field "$cmd_file" "category")
    [[ -z "$category" ]] && continue
    [[ -n "$CATEGORY_FILTER" && "$category" != "$CATEGORY_FILTER" ]] && continue

    description=$(get_field "$cmd_file" "description")

    # Derive command name from path: commands/ci/watch.md -> ci:watch
    rel="${cmd_file#"$COMMANDS_DIR/"}"
    rel="${rel%.md}"
    cmd_name="${rel//\//:}"

    row="| \`/craft:${cmd_name}\` | ${category} | ${description} |"
    cat_rows["$category"]+="${row}"$'\n'
done < <(find "$COMMANDS_DIR" -name "*.md" \
    ! -name "index.md" ! -name "README.md" | sort)

# Build generated output: one sentinel-wrapped block per category
generated=""
for cat in $(printf '%s\n' "${!cat_rows[@]}" | sort); do
    block="<!-- REFCARD:GENERATED:START:${cat} -->"$'\n'
    block+="${cat_rows[$cat]}"
    block+="<!-- REFCARD:GENERATED:END:${cat} -->"
    generated+="${block}"$'\n'
done

if [[ "$CHECK_MODE" == "true" ]]; then
    # --check is not supported: docs/REFCARD.md uses heading-based sections (### /craft:cmd),
    # not <!-- REFCARD:GENERATED:START/END --> sentinels. This script is a scaffolding helper
    # that prints rows to stdout for human use. Use scripts/doc-coverage-check.sh to verify
    # REFCARD row presence programmatically.
    echo "⚠️  --check is not supported: docs/REFCARD.md does not use generated sentinels." >&2
    echo "   Use scripts/doc-coverage-check.sh to verify REFCARD row presence." >&2
    exit 1
fi

printf '%s' "$generated"
