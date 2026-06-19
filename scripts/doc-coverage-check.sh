#!/usr/bin/env bash
# doc-coverage-check.sh — verify doc surfaces exist for every active command
# Exit 0: all blocking surfaces present. Exit 1: blocking gaps found.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${SCRIPT_DIR}/.."
JSON_MODE=false
SINCE_REF=""

usage() {
    echo "Usage: $0 [--root DIR] [--since GIT_REF] [--json]"
    echo "  --root DIR      Project root (default: script's parent)"
    echo "  --since REF     Only check commands changed since git ref"
    echo "  --json          Output JSON array of findings"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --root) ROOT="$2"; shift 2 ;;
        --since) SINCE_REF="$2"; shift 2 ;;
        --json) JSON_MODE=true; shift ;;
        -h|--help) usage ;;
        *) echo "Unknown arg: $1"; usage ;;
    esac
done

COMMANDS_DIR="$ROOT/commands"
REFCARD="$ROOT/docs/REFCARD.md"
MKDOCS="$ROOT/mkdocs.yml"

blocking_gaps=0
warn_gaps=0
json_findings=()

# Parse a frontmatter field from a markdown file
# Usage: get_field FILE FIELD
get_field() {
    local file="$1" field="$2"
    { sed -n '/^---$/,/^---$/{ /^'"$field"':/s/^'"$field"':[[:space:]]*//p; }' "$file" 2>/dev/null || true; } | head -1 | tr -d '"'"'"
}

# Emit a finding
finding() {
    local cmd="$1" surface="$2" severity="$3" message="$4"
    if [[ "$JSON_MODE" == "true" ]]; then
        json_findings+=("{\"cmd\":\"$cmd\",\"surface\":\"$surface\",\"severity\":\"$severity\",\"message\":\"$message\"}")
    else
        local icon="[BLOCK]"
        [[ "$severity" == "warn" ]] && icon="[WARN]"
        echo "  $icon $cmd — $message"
    fi
    if [[ "$severity" == "block" ]]; then blocking_gaps=$((blocking_gaps + 1)); fi
    if [[ "$severity" == "warn" ]];  then warn_gaps=$((warn_gaps + 1));     fi
}

# Build list of command files to check
if [[ -n "$SINCE_REF" ]]; then
    mapfile -t cmd_files < <(
        git -C "$ROOT" diff --name-only "$SINCE_REF"..HEAD -- 'commands/*.md' 'commands/**/*.md' 2>/dev/null \
        | grep -v -E '(index|README)\.md$' || true
    )
    # Also include untracked new files
    mapfile -t untracked < <(
        git -C "$ROOT" ls-files --others --exclude-standard -- 'commands/*.md' 'commands/**/*.md' 2>/dev/null || true
    )
    cmd_files+=("${untracked[@]}")
else
    mapfile -t cmd_files < <(
        find "$COMMANDS_DIR" -name "*.md" \
            ! -name "index.md" ! -name "README.md" \
            2>/dev/null | sort
    )
fi

[[ "${#cmd_files[@]}" -eq 0 ]] && { echo "No command files to check."; exit 0; }

[[ "$JSON_MODE" != "true" ]] && echo "Doc Coverage Check (${#cmd_files[@]} commands)"

for cmd_file in "${cmd_files[@]}"; do
    [[ -z "$cmd_file" ]] && continue
    # Use absolute path for field parsing
    local_file="$cmd_file"
    [[ "$cmd_file" != /* ]] && local_file="$ROOT/$cmd_file"
    [[ -f "$local_file" ]] || continue

    # Skip deprecated and internal
    deprecated=$(get_field "$local_file" "deprecated")
    internal=$(get_field "$local_file" "internal")
    [[ "$deprecated" == "true" ]] && continue
    [[ "$internal"   == "true" ]] && continue

    # Derive command name: commands/ci/watch.md → ci:watch
    rel="${local_file#"$COMMANDS_DIR/"}"
    rel="${rel%.md}"
    cmd_name=$(echo "$rel" | tr '/' ':')

    # Check 1: REFCARD row (blocking)
    if [[ -f "$REFCARD" ]]; then
        if ! grep -qF "/craft:${cmd_name}" "$REFCARD" 2>/dev/null; then
            finding "$cmd_name" "refcard" "block" "Missing REFCARD row in docs/REFCARD.md"
        fi
    fi

    # Check 2: mkdocs.yml nav entry (blocking)
    if [[ -f "$MKDOCS" ]]; then
        # Look for the command file path in nav section
        rel_path="${local_file#"$ROOT/"}"
        if ! grep -qF "$rel_path" "$MKDOCS" 2>/dev/null; then
            finding "$cmd_name" "nav" "block" "Missing mkdocs.yml nav entry for $rel_path"
        fi
    fi

    # Check 3: Tutorial (warn only — required if arguments: present)
    has_args=$(get_field "$local_file" "arguments")
    if [[ -n "$has_args" ]]; then
        # Look for tutorial file referencing this command in docs/tutorials/
        tut_dir="$ROOT/docs/tutorials"
        safe_name="${cmd_name//:/-}"
        found_tut=false
        if [[ -d "$tut_dir" ]] && ls "$tut_dir/"*"${safe_name}"* 2>/dev/null | grep -q .; then
            found_tut=true
        fi
        if [[ "$found_tut" == "false" ]]; then
            finding "$cmd_name" "tutorial" "warn" "Has arguments: but no tutorial in docs/tutorials/"
        fi
    fi
done

# Output JSON
if [[ "$JSON_MODE" == "true" ]]; then
    echo "["
    for i in "${!json_findings[@]}"; do
        if [[ $i -lt $((${#json_findings[@]} - 1)) ]]; then
            echo "  ${json_findings[$i]},"
        else
            echo "  ${json_findings[$i]}"
        fi
    done
    echo "]"
    exit $(( blocking_gaps > 0 ? 1 : 0 ))
fi

# Human summary
echo ""
echo "Blocking gaps:  $blocking_gaps"
echo "Warnings:       $warn_gaps"
if [[ "$blocking_gaps" -gt 0 ]]; then
    echo "Status: FAIL"
else
    echo "Status: PASS"
fi
exit $(( blocking_gaps > 0 ? 1 : 0 ))
