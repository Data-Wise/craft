#!/usr/bin/env bash
# scripts/command-audit.sh - Validate command/skill/agent frontmatter against schema
# Usage: ./scripts/command-audit.sh [--format terminal|json|markdown] [--fix] [--strict]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"

if [[ ! -f "$SCRIPT_DIR/formatting.sh" ]]; then
    echo "Error: formatting.sh not found in $SCRIPT_DIR" >&2
    exit 2
fi
source "$SCRIPT_DIR/formatting.sh"

# ============================================================================
# Configuration
# ============================================================================

VALID_FIELDS=(
    name category subcategory description file modes arguments
    tutorial tutorial_level tutorial_file related_commands tags
    project_types common_workflows time_budgets examples
)

SCAN_DIRS=("commands" "skills" "agents")
SKIP_FILES=("_schema.json" "hub.md" "index.md" "README.md")

# Counters
ERRORS=0
WARNINGS=0
SUGGESTIONS=0
FILES_SCANNED=0
FILES_WITH_ISSUES=0
FIXES_APPLIED=0

# Accumulate output for different formats
declare -a ERROR_MSGS=()
declare -a WARNING_MSGS=()
declare -a SUGGESTION_MSGS=()

# ============================================================================
# Argument parsing
# ============================================================================

FORMAT="terminal"
FIX_MODE=0
STRICT_MODE=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --format)
            FORMAT="${2:-terminal}"
            shift 2
            ;;
        --fix)
            FIX_MODE=1
            shift
            ;;
        --strict)
            STRICT_MODE=1
            shift
            ;;
        -h|--help)
            echo "Usage: command-audit.sh [--format terminal|json|markdown] [--fix] [--strict]"
            echo ""
            echo "Options:"
            echo "  --format   Output format: terminal (default), json, markdown"
            echo "  --fix      Auto-fix safe issues (remove invalid fields, rename args -> arguments)"
            echo "  --strict   Treat warnings as errors (for CI)"
            echo ""
            echo "Exit codes: 0 = pass, 1 = warnings only, 2 = errors found"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 2
            ;;
    esac
done

# ============================================================================
# Helper functions
# ============================================================================

# Check if a filename should be skipped
should_skip() {
    local filename
    filename="$(basename "$1")"
    for skip in "${SKIP_FILES[@]}"; do
        if [[ "$filename" == "$skip" ]]; then
            return 0
        fi
    done
    # Skip non-.md files
    if [[ "$filename" != *.md ]]; then
        return 0
    fi
    return 1
}

# Extract frontmatter from a file (text between first --- and second ---)
extract_frontmatter() {
    local file="$1"
    local in_fm=0
    local fm=""
    while IFS= read -r line; do
        if [[ "$line" == "---" ]]; then
            if [[ $in_fm -eq 0 ]]; then
                in_fm=1
                continue
            else
                break
            fi
        fi
        if [[ $in_fm -eq 1 ]]; then
            fm+="$line"$'\n'
        fi
    done < "$file"
    echo "$fm"
}

# Get relative path from plugin dir
relpath() {
    echo "${1#$PLUGIN_DIR/}"
}

add_error() {
    local file="$1" msg="$2"
    ERRORS=$((ERRORS + 1))
    ERROR_MSGS+=("$(relpath "$file"): $msg")
}

add_warning() {
    local file="$1" msg="$2"
    WARNINGS=$((WARNINGS + 1))
    WARNING_MSGS+=("$(relpath "$file"): $msg")
}

add_suggestion() {
    local file="$1" msg="$2"
    SUGGESTIONS=$((SUGGESTIONS + 1))
    SUGGESTION_MSGS+=("$(relpath "$file"): $msg")
}

# ============================================================================
# Check 1: Invalid frontmatter fields
# ============================================================================

check_invalid_fields() {
    local file="$1"
    local fm="$2"

    if [[ -z "$fm" ]]; then
        return
    fi

    # Extract top-level keys from YAML frontmatter
    local keys
    keys=$(echo "$fm" | python3 -c "
import yaml, sys
try:
    data = yaml.safe_load(sys.stdin.read())
    if isinstance(data, dict):
        for k in data.keys():
            print(k)
except:
    pass
" 2>/dev/null || true)

    while IFS= read -r key; do
        [[ -z "$key" ]] && continue
        local valid=0
        for vf in "${VALID_FIELDS[@]}"; do
            if [[ "$key" == "$vf" ]]; then
                valid=1
                break
            fi
        done
        if [[ $valid -eq 0 ]]; then
            # Check if it's a known rename
            if [[ "$key" == "args" && $FIX_MODE -eq 1 ]]; then
                # Auto-fix: rename args -> arguments
                sed -i '' 's/^args:/arguments:/' "$file"
                FIXES_APPLIED=$((FIXES_APPLIED + 1))
                add_suggestion "$file" "auto-fixed: renamed 'args' -> 'arguments'"
            elif [[ "$key" == "args" ]]; then
                add_error "$file" "invalid field 'args' (did you mean 'arguments'?)"
            else
                if [[ $FIX_MODE -eq 1 ]]; then
                    # Auto-fix: remove invalid field (only top-level simple fields)
                    # Pass file and key as sys.argv to avoid shell injection
                    python3 -c "
import sys
filepath, field_key = sys.argv[1], sys.argv[2]
with open(filepath, 'r') as f:
    content = f.read()
lines = content.split('\n')
new_lines = []
in_fm = False
fm_count = 0
skip_indent = False
for line in lines:
    if line.strip() == '---':
        fm_count += 1
        in_fm = (fm_count == 1)
        skip_indent = False
        new_lines.append(line)
        continue
    if in_fm and fm_count == 1:
        if line.startswith(field_key + ':'):
            skip_indent = True
            continue
        if skip_indent and line.startswith('  '):
            continue
        skip_indent = False
    new_lines.append(line)
with open(filepath, 'w') as f:
    f.write('\n'.join(new_lines))
" "$file" "$key" 2>/dev/null && {
                        FIXES_APPLIED=$((FIXES_APPLIED + 1))
                        add_suggestion "$file" "auto-fixed: removed invalid field '$key'"
                    } || {
                        add_error "$file" "invalid field '$key'"
                    }
                else
                    add_error "$file" "invalid field '$key'"
                fi
            fi
        fi
    done <<< "$keys"
}

# ============================================================================
# Check 2: Missing description field
# ============================================================================

check_missing_description() {
    local file="$1"
    local fm="$2"

    if [[ -z "$fm" ]]; then
        add_error "$file" "missing frontmatter entirely"
        return
    fi

    local has_desc
    has_desc=$(echo "$fm" | python3 -c "
import yaml, sys
try:
    data = yaml.safe_load(sys.stdin.read())
    if isinstance(data, dict) and 'description' in data and data['description']:
        print('yes')
    else:
        print('no')
except:
    print('no')
" 2>/dev/null || echo "no")

    if [[ "$has_desc" == "no" ]]; then
        add_error "$file" "missing required field 'description'"
    fi
}

# ============================================================================
# Check 3: Deprecated commands
# ============================================================================

check_deprecated() {
    local file="$1"

    # Only flag if the file has a standalone DEPRECATED marker (not just mentioning
    # the word in documentation). Look for patterns like:
    #   > DEPRECATED
    #   **DEPRECATED**
    #   # DEPRECATED
    #   status: deprecated
    #   deprecated: true
    if grep -qiE '(^>\s*DEPRECATED|^\*\*DEPRECATED|^#.*DEPRECATED|^deprecated:|status:\s*deprecated)' "$file" 2>/dev/null; then
        add_warning "$file" "contains DEPRECATED marker"
    fi
}

# ============================================================================
# Check 4: Hardcoded model names
# ============================================================================

check_hardcoded_models() {
    local file="$1"

    local models=("sonnet 4.5" "opus 4.0" "sonnet 3.5" "opus 3" "haiku 3" "claude-3" "claude-4")
    for model in "${models[@]}"; do
        if grep -qi "$model" "$file" 2>/dev/null; then
            add_warning "$file" "hardcoded model name '$(grep -oi "$model" "$file" | head -1)'"
            break
        fi
    done
}

# ============================================================================
# Check 5: YAML parse errors
# ============================================================================

check_yaml_syntax() {
    local file="$1"
    local fm="$2"

    if [[ -z "$fm" ]]; then
        return  # No frontmatter to parse — handled by check 2
    fi

    local result
    result=$(echo "$fm" | python3 -c "
import yaml, sys
try:
    yaml.safe_load(sys.stdin.read())
    print('ok')
except yaml.YAMLError as e:
    print(f'error: {e}')
" 2>/dev/null || echo "error: python3 failed")

    if [[ "$result" != "ok" ]]; then
        add_error "$file" "YAML parse error: ${result#error: }"
    fi
}

# ============================================================================
# Check 6: Orphaned scripts
# ============================================================================

check_orphaned_scripts() {
    local script_dir="$PLUGIN_DIR/scripts"
    if [[ ! -d "$script_dir" ]]; then
        return
    fi

    # Build a list of all content from command/skill/agent files for reference checking
    local all_content_file
    all_content_file=$(mktemp)
    for dir in "${SCAN_DIRS[@]}"; do
        local scan_path="$PLUGIN_DIR/$dir"
        [[ -d "$scan_path" ]] || continue
        find "$scan_path" -name "*.md" -print0 2>/dev/null | xargs -0 cat 2>/dev/null >> "$all_content_file" || true
    done

    # Also check CLAUDE.md and plugin.json
    for extra in "$PLUGIN_DIR/CLAUDE.md" "$PLUGIN_DIR/.claude-plugin/plugin.json"; do
        [[ -f "$extra" ]] && cat "$extra" >> "$all_content_file" 2>/dev/null || true
    done

    for script in "$script_dir"/*.sh; do
        [[ -f "$script" ]] || continue
        local script_name
        script_name="$(basename "$script")"
        # Skip formatting.sh (it's a library) and this script itself
        if [[ "$script_name" == "formatting.sh" || "$script_name" == "command-audit.sh" ]]; then
            continue
        fi
        if ! grep -q "$script_name" "$all_content_file" 2>/dev/null; then
            add_warning "$script" "script not referenced by any command file"
        fi
    done

    rm -f "$all_content_file"
}

# ============================================================================
# Check 7: External tool availability
# ============================================================================

check_external_tools() {
    local tools=("python3" "ruff" "mkdocs" "gh" "jq")
    for tool in "${tools[@]}"; do
        if command -v "$tool" &>/dev/null; then
            add_suggestion "tools" "$tool: available"
        else
            add_suggestion "tools" "$tool: not found"
        fi
    done
}

# ============================================================================
# Main scan loop
# ============================================================================

scan_files() {
    for dir in "${SCAN_DIRS[@]}"; do
        local scan_path="$PLUGIN_DIR/$dir"
        [[ -d "$scan_path" ]] || continue

        while IFS= read -r -d '' file; do
            should_skip "$file" && continue

            FILES_SCANNED=$((FILES_SCANNED + 1))
            local prev_errors=$ERRORS
            local prev_warnings=$WARNINGS

            # Extract frontmatter
            local fm
            fm=$(extract_frontmatter "$file")

            # Run checks
            check_yaml_syntax "$file" "$fm"       # Check 5 first — if YAML is broken, other checks may fail
            check_missing_description "$file" "$fm" # Check 2
            check_invalid_fields "$file" "$fm"     # Check 1
            check_deprecated "$file"               # Check 3
            check_hardcoded_models "$file"         # Check 4

            if [[ $ERRORS -gt $prev_errors || $WARNINGS -gt $prev_warnings ]]; then
                FILES_WITH_ISSUES=$((FILES_WITH_ISSUES + 1))
            fi
        done < <(find "$scan_path" -name "*.md" -print0 2>/dev/null)
    done

    # Check 6: Orphaned scripts
    check_orphaned_scripts

    # Check 7: External tools
    check_external_tools
}

# ============================================================================
# Health score calculation
# ============================================================================

calculate_score() {
    local score=100
    score=$((score - (ERRORS * 5)))
    score=$((score - (WARNINGS * 2)))
    if [[ $score -lt 0 ]]; then
        score=0
    fi
    echo "$score"
}

# ============================================================================
# Output: Terminal format
# ============================================================================

output_terminal() {
    local score
    score=$(calculate_score)

    box_header "COMMAND AUDIT" "$FMT_CYAN"
    box_empty_row
    box_row "  Scanning commands/, skills/, agents/..."
    box_empty_row

    if [[ $ERRORS -eq 0 && $WARNINGS -eq 0 ]]; then
        box_row "  ${FMT_GREEN}✓${FMT_NC} $FILES_SCANNED files scanned — all clean"
    else
        box_row "  ${FMT_GREEN}✓${FMT_NC} $FILES_SCANNED files scanned"
        if [[ $ERRORS -gt 0 ]]; then
            box_row "  ${FMT_RED}✗${FMT_NC} $ERRORS errors found"
        fi
        if [[ $WARNINGS -gt 0 ]]; then
            box_row "  ${FMT_YELLOW}⚠${FMT_NC} $WARNINGS warnings found"
        fi
    fi

    if [[ $FIX_MODE -eq 1 && $FIXES_APPLIED -gt 0 ]]; then
        box_row "  ${FMT_GREEN}⚡${FMT_NC} $FIXES_APPLIED auto-fixes applied"
    fi

    box_empty_row

    # Errors section
    if [[ ${#ERROR_MSGS[@]} -gt 0 ]]; then
        box_separator
        box_row "  ${FMT_RED}ERRORS${FMT_NC}"
        for msg in "${ERROR_MSGS[@]}"; do
            box_row "  ${FMT_RED}✗${FMT_NC} $msg"
        done
        box_empty_row
    fi

    # Warnings section
    if [[ ${#WARNING_MSGS[@]} -gt 0 ]]; then
        box_separator
        box_row "  ${FMT_YELLOW}WARNINGS${FMT_NC}"
        for msg in "${WARNING_MSGS[@]}"; do
            box_row "  ${FMT_YELLOW}⚠${FMT_NC} $msg"
        done
        box_empty_row
    fi

    # Health score
    box_separator
    local score_color="$FMT_GREEN"
    if [[ $score -lt 80 ]]; then
        score_color="$FMT_YELLOW"
    fi
    if [[ $score -lt 60 ]]; then
        score_color="$FMT_RED"
    fi
    box_row "  Health Score: ${score_color}${score}/100${FMT_NC}"
    box_footer
}

# ============================================================================
# Output: JSON format
# ============================================================================

output_json() {
    local score
    score=$(calculate_score)

    # Write arrays to temp files (one line per entry) for safe Python ingestion
    local tmp_errors tmp_warnings tmp_suggestions
    tmp_errors=$(mktemp)
    tmp_warnings=$(mktemp)
    tmp_suggestions=$(mktemp)

    printf '%s\n' "${ERROR_MSGS[@]+"${ERROR_MSGS[@]}"}" > "$tmp_errors"
    printf '%s\n' "${WARNING_MSGS[@]+"${WARNING_MSGS[@]}"}" > "$tmp_warnings"
    printf '%s\n' "${SUGGESTION_MSGS[@]+"${SUGGESTION_MSGS[@]}"}" > "$tmp_suggestions"

    python3 -c "
import json, sys

def read_lines(path):
    with open(path) as f:
        return [line.rstrip('\n') for line in f if line.strip()]

errors = read_lines(sys.argv[1])
warnings = read_lines(sys.argv[2])
suggestions = read_lines(sys.argv[3])

result = {
    'files_scanned': int(sys.argv[4]),
    'files_with_issues': int(sys.argv[5]),
    'errors': errors,
    'warnings': warnings,
    'suggestions': suggestions,
    'error_count': len(errors),
    'warning_count': len(warnings),
    'suggestion_count': len(suggestions),
    'health_score': int(sys.argv[6]),
    'fixes_applied': int(sys.argv[7])
}
print(json.dumps(result, indent=2))
" "$tmp_errors" "$tmp_warnings" "$tmp_suggestions" \
  "$FILES_SCANNED" "$FILES_WITH_ISSUES" "$score" "$FIXES_APPLIED"

    rm -f "$tmp_errors" "$tmp_warnings" "$tmp_suggestions"
}

# ============================================================================
# Output: Markdown format
# ============================================================================

output_markdown() {
    local score
    score=$(calculate_score)

    echo "# Command Audit Report"
    echo ""
    echo "- **Files scanned:** $FILES_SCANNED"
    echo "- **Errors:** $ERRORS"
    echo "- **Warnings:** $WARNINGS"
    echo "- **Health Score:** $score/100"
    echo ""

    if [[ ${#ERROR_MSGS[@]} -gt 0 ]]; then
        echo "## Errors"
        echo ""
        for msg in "${ERROR_MSGS[@]}"; do
            echo "- $msg"
        done
        echo ""
    fi

    if [[ ${#WARNING_MSGS[@]} -gt 0 ]]; then
        echo "## Warnings"
        echo ""
        for msg in "${WARNING_MSGS[@]}"; do
            echo "- $msg"
        done
        echo ""
    fi

    if [[ $FIX_MODE -eq 1 && $FIXES_APPLIED -gt 0 ]]; then
        echo "## Auto-fixes Applied"
        echo ""
        echo "$FIXES_APPLIED fixes applied."
        echo ""
    fi
}

# ============================================================================
# Run
# ============================================================================

scan_files

case "$FORMAT" in
    terminal) output_terminal ;;
    json)     output_json ;;
    markdown) output_markdown ;;
    *)
        echo "Unknown format: $FORMAT" >&2
        exit 2
        ;;
esac

# Exit code
if [[ $STRICT_MODE -eq 1 ]]; then
    if [[ $ERRORS -gt 0 || $WARNINGS -gt 0 ]]; then
        exit 2
    fi
else
    if [[ $ERRORS -gt 0 ]]; then
        exit 2
    elif [[ $WARNINGS -gt 0 ]]; then
        exit 1
    fi
fi

exit 0
