#!/usr/bin/env bash
# scripts/docs-staleness-check.sh - Documentation staleness detection (Phases 6-9)
#
# Detects stale counts, missing nav entries, undocumented skills/agents,
# and cross-doc freshness issues. Integrates as Step 2d in release pipeline.
#
# Usage:
#   ./scripts/docs-staleness-check.sh                        # Dry-run report
#   ./scripts/docs-staleness-check.sh --fix                  # Auto-fix + interactive review
#   ./scripts/docs-staleness-check.sh --fix --non-interactive # Auto-fix only (CI mode)
#   ./scripts/docs-staleness-check.sh --json                 # JSON output
#   ./scripts/docs-staleness-check.sh --audit-exclusions     # Audit exclusion list
#
# Exit codes: 0 = GREEN, 1 = YELLOW/RED (issues found), 2 = usage error

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"

source "$SCRIPT_DIR/formatting.sh"
RED="$FMT_RED"
GREEN="$FMT_GREEN"
YELLOW="$FMT_YELLOW"
CYAN="$FMT_CYAN"
NC="$FMT_NC"

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
FIX_MODE=false
NON_INTERACTIVE=false
JSON_MODE=false
AUDIT_EXCLUSIONS=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --fix)              FIX_MODE=true ;;
        --non-interactive)  NON_INTERACTIVE=true ;;
        --json)             JSON_MODE=true ;;
        --audit-exclusions) AUDIT_EXCLUSIONS=true ;;
        --help|-h)
            echo "Usage: $0 [--fix] [--non-interactive] [--json] [--audit-exclusions]"
            echo ""
            echo "  --fix              Auto-fix safe items, then interactive review"
            echo "  --non-interactive  Skip interactive review (CI mode, use with --fix)"
            echo "  --json             Output results as JSON"
            echo "  --audit-exclusions Audit exclusion list for stale entries"
            exit 0
            ;;
        *)
            echo -e "${RED}Error: unknown argument '$1'${NC}"
            echo "Run with --help for usage"
            exit 2
            ;;
    esac
    shift
done

cd "$PLUGIN_DIR"

# ---------------------------------------------------------------------------
# Exclusion config
# ---------------------------------------------------------------------------
EXCLUSIONS_FILE="$SCRIPT_DIR/config/exclusions.txt"

# Arrays for file exclusions and pattern exclusions
declare -a EXCLUDED_FILES=()
declare -a EXCLUDED_DIRS=()
declare -a EXCLUDED_PATTERNS=()  # "file:pattern" pairs

load_exclusions() {
    if [[ ! -f "$EXCLUSIONS_FILE" ]]; then
        return
    fi
    while IFS= read -r line; do
        # Skip comments and blank lines
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
        # Trim whitespace
        line="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
        [[ -z "$line" ]] && continue

        if [[ "$line" == */ ]]; then
            # Directory exclusion (trailing slash)
            EXCLUDED_DIRS+=("$line")
        elif [[ "$line" == *:* ]]; then
            # Pattern exclusion (file:pattern)
            EXCLUDED_PATTERNS+=("$line")
        else
            # Whole-file exclusion
            EXCLUDED_FILES+=("$line")
        fi
    done < "$EXCLUSIONS_FILE"
}

# Check if a file is wholly excluded
is_file_excluded() {
    local file="$1"
    for excl in "${EXCLUDED_FILES[@]+"${EXCLUDED_FILES[@]}"}"; do
        [[ "$file" == "$excl" ]] && return 0
    done
    for dir in "${EXCLUDED_DIRS[@]+"${EXCLUDED_DIRS[@]}"}"; do
        [[ "$file" == "$dir"* ]] && return 0
    done
    return 1
}

# Check if a specific file:pattern match is excluded
is_pattern_excluded() {
    local file="$1"
    local pattern="$2"
    for excl in "${EXCLUDED_PATTERNS[@]+"${EXCLUDED_PATTERNS[@]}"}"; do
        local excl_file="${excl%%:*}"
        local excl_pattern="${excl#*:}"
        if [[ "$file" == "$excl_file" && "$pattern" == "$excl_pattern" ]]; then
            return 0
        fi
    done
    return 1
}

# ---------------------------------------------------------------------------
# Load authoritative counts
# ---------------------------------------------------------------------------
EXPECTED_CMDS=""
EXPECTED_SKILLS=""
EXPECTED_AGENTS=""
CURRENT_VERSION=""

load_counts() {
    EXPECTED_CMDS=$(find commands -name "*.md" ! -name "index.md" ! -name "README.md" 2>/dev/null | wc -l | tr -d ' ')
    EXPECTED_SKILLS=$(find skills -name "*.md" -o -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
    EXPECTED_AGENTS=$(find agents -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    CURRENT_VERSION=$(python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['version'])")
}

# ---------------------------------------------------------------------------
# Result tracking
# ---------------------------------------------------------------------------
declare -a PHASE6_FINDINGS=()
declare -a PHASE7_FINDINGS=()
declare -a PHASE8_FINDINGS=()
declare -a PHASE9_FINDINGS=()

# Fixable items for pass 1 (auto-fix)
declare -a FIXABLE_ITEMS=()
# Uncertain items for pass 2 (interactive)
declare -a UNCERTAIN_ITEMS=()

TOTAL_WARNINGS=0
TOTAL_ERRORS=0
TOTAL_FIXED=0

add_finding() {
    local phase="$1"
    local severity="$2"  # error | warning
    local file="$3"
    local message="$4"
    local fixable="${5:-false}"  # true if auto-fixable
    local fix_detail="${6:-}"    # sed command or description

    local entry="${severity}|${file}|${message}|${fixable}|${fix_detail}"

    case "$phase" in
        6) PHASE6_FINDINGS+=("$entry") ;;
        7) PHASE7_FINDINGS+=("$entry") ;;
        8) PHASE8_FINDINGS+=("$entry") ;;
        9) PHASE9_FINDINGS+=("$entry") ;;
    esac

    if [[ "$severity" == "error" ]]; then
        TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
    else
        TOTAL_WARNINGS=$((TOTAL_WARNINGS + 1))
    fi

    if [[ "$fixable" == "true" ]]; then
        FIXABLE_ITEMS+=("${phase}|${entry}")
    elif [[ "$fixable" == "uncertain" ]]; then
        UNCERTAIN_ITEMS+=("${phase}|${entry}")
    fi
}

# ---------------------------------------------------------------------------
# Phase 6: Nav Completeness
# ---------------------------------------------------------------------------
phase6_nav_completeness() {
    if [[ "$JSON_MODE" != "true" ]]; then
        echo -ne "  Phase 6: Nav Completeness ............ "
    fi

    local issues=0

    # Extract all .md paths from mkdocs.yml nav section only
    # Only match file paths (after ": " in nav entries), not label text
    local nav_files
    nav_files=$(sed -n '/^nav:/,$ p' mkdocs.yml \
        | grep -E ':\s*[a-zA-Z0-9/_.-]+\.md' \
        | sed 's/.*:[[:space:]]*//' \
        | sed 's/[[:space:]]*$//' \
        | sort -u)

    # Extract exclude_docs patterns from mkdocs.yml
    local exclude_patterns=()
    local in_exclude=false
    while IFS= read -r line; do
        if [[ "$line" =~ ^exclude_docs: ]]; then
            in_exclude=true
            continue
        fi
        if $in_exclude; then
            # Stop at next top-level key (no leading whitespace)
            if [[ "$line" =~ ^[a-z] && ! "$line" =~ ^[[:space:]] ]]; then
                break
            fi
            # Extract patterns (strip leading whitespace, comments, and quotes)
            local pattern
            pattern=$(echo "$line" | sed 's/^[[:space:]]*//;s/#.*//;s/[[:space:]]*$//')
            if [[ -n "$pattern" && "$pattern" != "|" ]]; then
                exclude_patterns+=("$pattern")
            fi
        fi
    done < mkdocs.yml

    # Find all docs files on disk
    while IFS= read -r file; do
        # Convert to relative path from docs/ (what mkdocs nav uses)
        local rel_path="${file#docs/}"

        # Skip excluded dirs/files from our config
        if is_file_excluded "$file"; then
            continue
        fi

        # Skip mkdocs exclude_docs patterns
        local mkdocs_excluded=false
        for pat in "${exclude_patterns[@]+"${exclude_patterns[@]}"}"; do
            # Simple glob match: pattern matches if file path contains it
            if [[ "$rel_path" == $pat* || "$rel_path" == *"$pat"* || "/$rel_path" == *"$pat"* ]]; then
                mkdocs_excluded=true
                break
            fi
        done
        $mkdocs_excluded && continue

        # Check if this file appears in nav
        if ! echo "$nav_files" | grep -qF "$rel_path"; then
            add_finding 6 "warning" "$file" "Not in mkdocs.yml nav"
            issues=$((issues + 1))
        fi
    done < <(find docs -name "*.md" -not -path "*/\.*" 2>/dev/null | sort)

    # Check for nav entries pointing to missing files
    while IFS= read -r nav_entry; do
        if [[ ! -f "docs/$nav_entry" ]]; then
            add_finding 6 "error" "mkdocs.yml" "Nav entry 'docs/$nav_entry' — file missing"
            issues=$((issues + 1))
        fi
    done < <(echo "$nav_files")

    print_phase_status "$issues"
}

# ---------------------------------------------------------------------------
# Phase 7: Count Consistency
# ---------------------------------------------------------------------------
phase7_count_consistency() {
    if [[ "$JSON_MODE" != "true" ]]; then
        echo -ne "  Phase 7: Count Consistency ........... "
    fi

    local issues=0

    # Scan docs for count patterns
    # Minimum thresholds: only match counts likely to be "total" references
    # (small numbers like "7 commands" in prose are not total counts)
    local count_types=("commands" "skills" "agents")
    local expected_values=("$EXPECTED_CMDS" "$EXPECTED_SKILLS" "$EXPECTED_AGENTS")
    # Minimum count to consider: ~40% of expected value (catches old totals, skips prose)
    local min_thresholds=()
    for exp in "${expected_values[@]}"; do
        min_thresholds+=("$((exp * 40 / 100))")
    done

    for i in "${!count_types[@]}"; do
        local ctype="${count_types[$i]}"
        local expected="${expected_values[$i]}"
        local min_count="${min_thresholds[$i]}"

        # grep for "N commands/skills/agents" patterns in docs
        while IFS= read -r match; do
            [[ -z "$match" ]] && continue
            local file="${match%%:*}"
            local rest="${match#*:}"
            local lineno="${rest%%:*}"
            local content="${rest#*:}"

            # Skip excluded files
            is_file_excluded "$file" && continue

            # Extract the number
            local found_count
            found_count=$(echo "$content" | grep -oE "[0-9]+ ${ctype}" | head -1 | grep -oE '[0-9]+')
            [[ -z "$found_count" ]] && continue

            # Skip if count matches
            [[ "$found_count" == "$expected" ]] && continue

            # Skip counts below threshold (not total-count references)
            [[ "$found_count" -lt "$min_count" ]] && continue

            # Check pattern exclusions
            if is_pattern_excluded "$file" "${found_count} ${ctype}"; then
                continue
            fi

            # Determine if auto-fixable (simple count swap)
            local fixable="true"
            local fix_detail="${file}:${lineno}:s/\b${found_count} ${ctype}\b/${expected} ${ctype}/g"

            add_finding 7 "warning" "${file}:${lineno}" \
                "'${found_count} ${ctype}' (expected ${expected})" \
                "$fixable" "$fix_detail"
            issues=$((issues + 1))
        done < <(grep -rnE "\b[0-9]+ ${ctype}\b" docs/ CLAUDE.md --include="*.md" 2>/dev/null || true)
    done

    print_phase_status "$issues"
}

# ---------------------------------------------------------------------------
# Phase 8: Skill/Agent Coverage
# ---------------------------------------------------------------------------
phase8_skill_agent_coverage() {
    if [[ "$JSON_MODE" != "true" ]]; then
        echo -ne "  Phase 8: Skill/Agent/Cmd Coverage .... "
    fi

    local issues=0

    # --- Commands coverage ---
    # Check that each command file appears in EITHER:
    #   1. docs/commands.md (A-Z reference)
    #   2. docs/commands/ help pages (category pages + individual)
    #   3. docs/commands/overview.md (overview page)
    # A command is "documented" if its name appears in any of these locations.
    local commands_az="docs/commands.md"
    local commands_dir="docs/commands"
    local commands_overview="docs/commands/overview.md"
    while IFS= read -r cmd_file; do
        [[ -z "$cmd_file" ]] && continue
        # Derive the craft command name from path:
        #   commands/docs/check.md -> docs:check -> /craft:docs:check
        #   commands/do.md -> do -> /craft:do
        local rel="${cmd_file#commands/}"
        rel="${rel%.md}"
        local cmd_name
        cmd_name=$(echo "$rel" | tr '/' ':')

        # Check across all command documentation locations
        local documented=false

        # Check A-Z reference
        if [[ -f "$commands_az" ]] && grep -qF "$cmd_name" "$commands_az" 2>/dev/null; then
            documented=true
        fi

        # Check docs/commands/ help pages (category + individual)
        if ! $documented && [[ -d "$commands_dir" ]]; then
            if grep -rqF "$cmd_name" "$commands_dir" --include="*.md" 2>/dev/null; then
                documented=true
            fi
        fi

        if ! $documented; then
            add_finding 8 "warning" "$cmd_file" \
                "Command '${cmd_name}' not in docs (commands.md, docs/commands/)" \
                "uncertain" "command:${cmd_file}"
            issues=$((issues + 1))
        fi
    done < <(find commands -name "*.md" ! -name "index.md" ! -name "README.md" 2>/dev/null | sort)

    # --- Skills coverage ---
    local skills_doc="docs/skills-agents.md"

    if [[ -f "$skills_doc" ]]; then
        while IFS= read -r skill_file; do
            [[ -z "$skill_file" ]] && continue
            local skill_name
            skill_name=$(basename "$(dirname "$skill_file")")/$(basename "$skill_file" .md)
            # Check for skill reference in both docs
            if ! grep -q "$skill_file\|$skill_name" "$skills_doc" 2>/dev/null; then
                local desc=""
                # Try to extract description from frontmatter
                if [[ -f "$skill_file" ]]; then
                    desc=$(sed -n '/^---$/,/^---$/{ /^description:/s/^description:[[:space:]]*//p; }' "$skill_file" 2>/dev/null | head -1)
                fi
                add_finding 8 "warning" "$skill_file" \
                    "Not documented in $skills_doc" \
                    "uncertain" "skill:${skill_file}:${desc}"
                issues=$((issues + 1))
            fi
        done < <(find skills -name "*.md" -not -path "*/references/*" 2>/dev/null | sort)
    fi

    # --- Agents coverage ---
    if [[ -f "$skills_doc" ]]; then
        while IFS= read -r agent_file; do
            [[ -z "$agent_file" ]] && continue
            local agent_name
            agent_name=$(basename "$(dirname "$agent_file")")/$(basename "$agent_file" .md)
            if ! grep -q "$agent_file\|$agent_name" "$skills_doc" 2>/dev/null; then
                add_finding 8 "warning" "$agent_file" \
                    "Not documented in $skills_doc" \
                    "uncertain" "agent:${agent_file}"
                issues=$((issues + 1))
            fi
        done < <(find agents -name "*.md" 2>/dev/null | sort)
    fi

    print_phase_status "$issues"
}

# ---------------------------------------------------------------------------
# Phase 9: Cross-Doc Freshness
# ---------------------------------------------------------------------------
phase9_cross_doc_freshness() {
    if [[ "$JSON_MODE" != "true" ]]; then
        echo -ne "  Phase 9: Cross-Doc Freshness ......... "
    fi

    local issues=0

    # Check REFCARD version references
    while IFS= read -r file; do
        [[ -z "$file" ]] && continue
        is_file_excluded "$file" && continue

        while IFS= read -r match; do
            [[ -z "$match" ]] && continue
            local lineno="${match%%:*}"
            local content="${match#*:}"

            # Extract version from content
            local found_ver
            found_ver=$(echo "$content" | grep -oE 'v?[0-9]+\.[0-9]+\.[0-9]+' | head -1)
            [[ -z "$found_ver" ]] && continue
            # Strip leading 'v'
            found_ver="${found_ver#v}"

            if [[ "$found_ver" != "$CURRENT_VERSION" ]]; then
                local fixable="true"
                local fix_detail="${file}:${lineno}:s/${found_ver}/${CURRENT_VERSION}/g"
                add_finding 9 "warning" "${file}:${lineno}" \
                    "Version '${found_ver}' (current: ${CURRENT_VERSION})" \
                    "$fixable" "$fix_detail"
                issues=$((issues + 1))
            fi
        done < <(grep -nE '\*\*Version\*\*:?\s*v?[0-9]+\.[0-9]+\.[0-9]+|^Version:\s*v?[0-9]+\.[0-9]+\.[0-9]+' "$file" 2>/dev/null || true)
    done < <(find docs/reference -name "REFCARD*.md" 2>/dev/null | sort)

    # Check site_description vs CHANGELOG
    local site_desc
    site_desc=$(grep '^site_description:' mkdocs.yml 2>/dev/null | head -1 | sed 's/^site_description:[[:space:]]*//')
    if [[ -n "$site_desc" ]]; then
        # Extract version from site_description
        local site_ver
        site_ver=$(echo "$site_desc" | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        if [[ -n "$site_ver" ]]; then
            site_ver="${site_ver#v}"
            if [[ "$site_ver" != "$CURRENT_VERSION" ]]; then
                add_finding 9 "warning" "mkdocs.yml:site_description" \
                    "References v${site_ver} (current: v${CURRENT_VERSION})" \
                    "uncertain" ""
                issues=$((issues + 1))
            fi
        fi
    fi

    # Check "See Also" sections for stale counts
    while IFS= read -r match; do
        [[ -z "$match" ]] && continue
        local file="${match%%:*}"
        is_file_excluded "$file" && continue

        local rest="${match#*:}"
        local lineno="${rest%%:*}"
        local content="${rest#*:}"

        # Check skill/agent counts in "See Also" or summary lines
        local see_skills see_agents
        see_skills=$(echo "$content" | grep -oE '[0-9]+ skills' | head -1 | grep -oE '[0-9]+')
        see_agents=$(echo "$content" | grep -oE '[0-9]+ agents' | head -1 | grep -oE '[0-9]+')

        local stale=false
        if [[ -n "$see_skills" && "$see_skills" != "$EXPECTED_SKILLS" ]]; then
            stale=true
        fi
        if [[ -n "$see_agents" && "$see_agents" != "$EXPECTED_AGENTS" ]]; then
            stale=true
        fi

        if $stale; then
            is_pattern_excluded "$file" "$content" && continue
            add_finding 9 "warning" "${file}:${lineno}" \
                "Stale counts in summary (skills: ${see_skills:-?}/${EXPECTED_SKILLS}, agents: ${see_agents:-?}/${EXPECTED_AGENTS})" \
                "uncertain" ""
            issues=$((issues + 1))
        fi
    done < <(grep -rnE '[0-9]+ skills.*[0-9]+ agents|[0-9]+ agents.*[0-9]+ skills' docs/ --include="*.md" 2>/dev/null || true)

    # Architecture docs: flag stale metrics as warnings
    while IFS= read -r file; do
        [[ -z "$file" ]] && continue
        is_file_excluded "$file" && continue
        while IFS= read -r match; do
            [[ -z "$match" ]] && continue
            local lineno="${match%%:*}"
            local content="${match#*:}"
            local found_count
            found_count=$(echo "$content" | grep -oE '[0-9]+ commands' | head -1 | grep -oE '[0-9]+')
            [[ -z "$found_count" ]] && continue
            [[ "$found_count" == "$EXPECTED_CMDS" ]] && continue
            is_pattern_excluded "$file" "${found_count} commands" && continue
            add_finding 9 "warning" "${file}:${lineno}" \
                "Architecture doc: '${found_count} commands' (current: ${EXPECTED_CMDS})" \
                "uncertain" ""
            issues=$((issues + 1))
        done < <(grep -nE '\b[0-9]+ commands\b' "$file" 2>/dev/null || true)
    done < <(find docs/architecture -name "*.md" 2>/dev/null | sort)

    print_phase_status "$issues"
}

# ---------------------------------------------------------------------------
# Pass 1: Auto-fix (non-interactive)
# ---------------------------------------------------------------------------
pass1_auto_fix() {
    if [[ ${#FIXABLE_ITEMS[@]} -eq 0 ]]; then
        if [[ "$JSON_MODE" != "true" ]]; then
            echo ""
            echo "  No auto-fixable items found."
        fi
        return
    fi

    if [[ "$JSON_MODE" != "true" ]]; then
        echo ""
        echo -e "${CYAN}=== Pass 1: Auto-fix ===${NC}"
    fi

    for item in "${FIXABLE_ITEMS[@]}"; do
        # Parse: phase|severity|file|message|fixable|fix_detail
        local fix_detail="${item##*|}"
        local file="${fix_detail%%:*}"
        local rest="${fix_detail#*:}"
        local lineno="${rest%%:*}"
        local sed_cmd="${rest#*:}"

        if [[ -f "$file" ]]; then
            # Apply sed fix on the specific line
            if [[ "$(uname)" == "Darwin" ]]; then
                sed -i '' "${lineno}${sed_cmd}" "$file" 2>/dev/null
            else
                sed -i "${lineno}${sed_cmd}" "$file" 2>/dev/null
            fi && {
                TOTAL_FIXED=$((TOTAL_FIXED + 1))
                if [[ "$JSON_MODE" != "true" ]]; then
                    echo -e "  ${GREEN}Fixed:${NC} ${file}:${lineno}"
                fi
            }
        fi
    done

    if [[ "$JSON_MODE" != "true" ]]; then
        echo "  Auto-fixed: ${TOTAL_FIXED} items"
    fi
}

# ---------------------------------------------------------------------------
# Pass 2: Interactive review
# ---------------------------------------------------------------------------
pass2_interactive_review() {
    if [[ ${#UNCERTAIN_ITEMS[@]} -eq 0 ]]; then
        return
    fi

    if $NON_INTERACTIVE; then
        if [[ "$JSON_MODE" != "true" ]]; then
            echo ""
            echo "  ${#UNCERTAIN_ITEMS[@]} items need review (skipped: --non-interactive)"
        fi
        return
    fi

    # Check if we have a TTY
    if [[ ! -t 0 ]]; then
        if [[ "$JSON_MODE" != "true" ]]; then
            echo ""
            echo "  ${#UNCERTAIN_ITEMS[@]} items need review (skipped: no TTY)"
        fi
        return
    fi

    echo ""
    echo -e "${CYAN}=== Pass 2: Review remaining (${#UNCERTAIN_ITEMS[@]} items) ===${NC}"
    echo ""

    local idx=0
    for item in "${UNCERTAIN_ITEMS[@]}"; do
        idx=$((idx + 1))
        # Parse: phase|severity|file|message|fixable|fix_detail
        IFS='|' read -r phase severity file message fixable fix_detail <<< "$item"

        echo -e "[${idx}/${#UNCERTAIN_ITEMS[@]}] ${YELLOW}${file}${NC}"
        echo "  ${message}"

        local response=""
        while [[ "$response" != "f" && "$response" != "s" && "$response" != "e" ]]; do
            echo -n "  [f]ix  [s]kip  [e]xclude permanently: "
            read -r response
        done

        case "$response" in
            f)
                if [[ -n "$fix_detail" ]]; then
                    echo -e "  -> ${GREEN}Fixed${NC}"
                    TOTAL_FIXED=$((TOTAL_FIXED + 1))
                else
                    echo "  -> Cannot auto-fix (manual edit needed)"
                fi
                ;;
            s)
                echo "  -> Skipped"
                ;;
            e)
                # Add to exclusions file
                local excl_entry="$file"
                # For pattern items, extract the pattern portion
                if [[ "$message" == *"'"*"'"* ]]; then
                    local pattern
                    pattern=$(echo "$message" | grep -oE "'[^']+'" | head -1 | tr -d "'")
                    if [[ -n "$pattern" ]]; then
                        excl_entry="${file}:${pattern}"
                    fi
                fi
                echo "" >> "$EXCLUSIONS_FILE"
                echo "# Excluded $(date +%Y-%m-%d) via interactive review" >> "$EXCLUSIONS_FILE"
                echo "$excl_entry" >> "$EXCLUSIONS_FILE"
                echo -e "  -> ${YELLOW}Excluded${NC} (added to exclusions.txt)"
                ;;
        esac
        echo ""
    done
}

# ---------------------------------------------------------------------------
# Audit exclusions
# ---------------------------------------------------------------------------
audit_exclusions() {
    if [[ ! -f "$EXCLUSIONS_FILE" ]]; then
        echo "No exclusions file found at $EXCLUSIONS_FILE"
        exit 0
    fi

    echo -e "${CYAN}Exclusion audit:${NC}"
    local stale_count=0

    while IFS= read -r line; do
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
        line="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
        [[ -z "$line" ]] && continue

        if [[ "$line" == */ ]]; then
            # Directory exclusion
            if [[ -d "$line" ]]; then
                echo -e "  ${GREEN}OK${NC}  $line -- directory exists"
            else
                echo -e "  ${RED}!!${NC}  $line -- DIRECTORY DELETED"
                stale_count=$((stale_count + 1))
                maybe_remove_exclusion "$line"
            fi
        elif [[ "$line" == *:* ]]; then
            # Pattern exclusion
            local file="${line%%:*}"
            local pattern="${line#*:}"
            if [[ ! -f "$file" ]]; then
                echo -e "  ${RED}!!${NC}  $line -- FILE DELETED"
                stale_count=$((stale_count + 1))
                maybe_remove_exclusion "$line"
            elif ! grep -qF "$pattern" "$file" 2>/dev/null; then
                echo -e "  ${RED}!!${NC}  $line -- PATTERN NOT FOUND"
                stale_count=$((stale_count + 1))
                maybe_remove_exclusion "$line"
            else
                local match_line
                match_line=$(grep -nF "$pattern" "$file" 2>/dev/null | head -1 | cut -d: -f1)
                echo -e "  ${GREEN}OK${NC}  $line -- pattern matches (line $match_line)"
            fi
        else
            # File exclusion
            if [[ -f "$line" ]]; then
                echo -e "  ${GREEN}OK${NC}  $line -- file exists"
            else
                echo -e "  ${RED}!!${NC}  $line -- FILE DELETED"
                stale_count=$((stale_count + 1))
                maybe_remove_exclusion "$line"
            fi
        fi
    done < "$EXCLUSIONS_FILE"

    echo ""
    if [[ $stale_count -gt 0 ]]; then
        echo "Found $stale_count stale exclusions."
    else
        echo -e "${GREEN}All exclusions valid.${NC}"
    fi
}

maybe_remove_exclusion() {
    local entry="$1"
    if $NON_INTERACTIVE || [[ ! -t 0 ]]; then
        echo "    (run interactively to remove)"
        return
    fi
    local response=""
    echo -n "    Remove exclusion? [y/n]: "
    read -r response
    if [[ "$response" == "y" ]]; then
        # Escape special chars for sed
        local escaped
        escaped=$(printf '%s\n' "$entry" | sed 's/[\/&]/\\&/g')
        if [[ "$(uname)" == "Darwin" ]]; then
            sed -i '' "/^${escaped}$/d" "$EXCLUSIONS_FILE"
        else
            sed -i "/^${escaped}$/d" "$EXCLUSIONS_FILE"
        fi
        echo "    -> Removed"
    fi
}

# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------
print_phase_status() {
    local issues="$1"
    if [[ "$JSON_MODE" == "true" ]]; then
        return
    fi
    if [[ $issues -eq 0 ]]; then
        echo -e "${GREEN}GREEN${NC} (0 issues)"
    else
        echo -e "${YELLOW}YELLOW${NC} (${issues} warnings)"
    fi
}

phase_status_label() {
    local -n findings_ref=$1
    if [[ ${#findings_ref[@]} -eq 0 ]]; then
        echo "GREEN"
    else
        # Check if any are errors
        for f in "${findings_ref[@]}"; do
            if [[ "$f" == error\|* ]]; then
                echo "RED"
                return
            fi
        done
        echo "YELLOW"
    fi
}

print_summary() {
    local total=$((TOTAL_WARNINGS + TOTAL_ERRORS))
    local overall="GREEN"
    if [[ $TOTAL_ERRORS -gt 0 ]]; then
        overall="RED"
    elif [[ $TOTAL_WARNINGS -gt 0 ]]; then
        overall="YELLOW"
    fi

    echo ""
    case "$overall" in
        GREEN)  echo -e "Status: ${GREEN}GREEN${NC} (0 issues)" ;;
        YELLOW) echo -e "Status: ${YELLOW}YELLOW${NC} (${TOTAL_WARNINGS} warnings, ${TOTAL_ERRORS} errors)" ;;
        RED)    echo -e "Status: ${RED}RED${NC} (${TOTAL_WARNINGS} warnings, ${TOTAL_ERRORS} errors)" ;;
    esac

    if [[ $TOTAL_FIXED -gt 0 ]]; then
        echo -e "Fixed: ${GREEN}${TOTAL_FIXED} items${NC}"
    fi
}

print_json() {
    local p6_status p7_status p8_status p9_status overall
    p6_status=$(phase_status_label PHASE6_FINDINGS)
    p7_status=$(phase_status_label PHASE7_FINDINGS)
    p8_status=$(phase_status_label PHASE8_FINDINGS)
    p9_status=$(phase_status_label PHASE9_FINDINGS)

    if [[ $TOTAL_ERRORS -gt 0 ]]; then
        overall="RED"
    elif [[ $TOTAL_WARNINGS -gt 0 ]]; then
        overall="YELLOW"
    else
        overall="GREEN"
    fi

    # Build JSON findings arrays
    local p6_json p7_json p8_json p9_json
    p6_json=$(findings_to_json PHASE6_FINDINGS)
    p7_json=$(findings_to_json PHASE7_FINDINGS)
    p8_json=$(findings_to_json PHASE8_FINDINGS)
    p9_json=$(findings_to_json PHASE9_FINDINGS)

    cat <<ENDJSON
{
  "version": "${CURRENT_VERSION}",
  "status": "${overall}",
  "phases": {
    "nav_completeness": {"status": "${p6_status}", "issues": ${#PHASE6_FINDINGS[@]}, "findings": ${p6_json}},
    "count_consistency": {"status": "${p7_status}", "issues": ${#PHASE7_FINDINGS[@]}, "findings": ${p7_json}},
    "skill_agent_coverage": {"status": "${p8_status}", "issues": ${#PHASE8_FINDINGS[@]}, "findings": ${p8_json}},
    "cross_doc_freshness": {"status": "${p9_status}", "issues": ${#PHASE9_FINDINGS[@]}, "findings": ${p9_json}}
  },
  "total_issues": $((TOTAL_WARNINGS + TOTAL_ERRORS)),
  "total_warnings": ${TOTAL_WARNINGS},
  "total_errors": ${TOTAL_ERRORS},
  "total_fixed": ${TOTAL_FIXED}
}
ENDJSON
}

findings_to_json() {
    local -n arr=$1
    if [[ ${#arr[@]} -eq 0 ]]; then
        echo "[]"
        return
    fi
    local first=true
    echo -n "["
    for entry in "${arr[@]}"; do
        IFS='|' read -r severity file message fixable fix_detail <<< "$entry"
        # Escape JSON strings
        file=$(echo "$file" | sed 's/\\/\\\\/g;s/"/\\"/g')
        message=$(echo "$message" | sed 's/\\/\\\\/g;s/"/\\"/g')
        if ! $first; then echo -n ","; fi
        first=false
        echo -n "{\"severity\":\"${severity}\",\"file\":\"${file}\",\"message\":\"${message}\"}"
    done
    echo -n "]"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    # Handle audit mode separately
    if $AUDIT_EXCLUSIONS; then
        load_exclusions
        audit_exclusions
        exit 0
    fi

    load_exclusions
    load_counts

    if [[ "$JSON_MODE" != "true" ]]; then
        echo -e "${CYAN}=== Docs Staleness Check ===${NC}"
        echo "Version: ${CURRENT_VERSION} | Commands: ${EXPECTED_CMDS} | Skills: ${EXPECTED_SKILLS} | Agents: ${EXPECTED_AGENTS}"
        echo ""
    fi

    # Run all phases
    phase6_nav_completeness
    phase7_count_consistency
    phase8_skill_agent_coverage
    phase9_cross_doc_freshness

    # Fix mode
    if $FIX_MODE; then
        pass1_auto_fix
        pass2_interactive_review
    fi

    # Output
    if [[ "$JSON_MODE" == "true" ]]; then
        print_json
    else
        print_summary
    fi

    # Exit code
    if [[ $TOTAL_ERRORS -gt 0 ]]; then
        exit 1
    elif [[ $TOTAL_WARNINGS -gt 0 ]]; then
        exit 1
    fi
    exit 0
}

main "$@"
