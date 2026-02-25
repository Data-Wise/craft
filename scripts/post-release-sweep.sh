#!/usr/bin/env bash
# scripts/post-release-sweep.sh - Post-release drift detection for Tier 2+ references
#
# Catches secondary version references, stale dates/counts, and content
# staleness that bump-version.sh doesn't cover.
#
# Usage:
#   ./scripts/post-release-sweep.sh                    # Dry-run (default)
#   ./scripts/post-release-sweep.sh --fix              # Auto-fix mechanical items
#   ./scripts/post-release-sweep.sh --version 2.27.0   # Check against specific version
#   ./scripts/post-release-sweep.sh --json             # JSON output
#   ./scripts/post-release-sweep.sh --dry-run          # Explicit dry-run
#
# Exit codes: 0 = clean, 1 = drift found, 2 = usage error

# Note: no `set -e` — script uses explicit exit code checks (|| exit_code=$?)
# for controlled flow through each phase rather than failing on first error.
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
DRY_RUN=true
JSON_MODE=false
TARGET_VERSION=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --fix)       FIX_MODE=true; DRY_RUN=false ;;
        --dry-run|-n) DRY_RUN=true; FIX_MODE=false ;;
        --json)      JSON_MODE=true ;;
        --version)
            if [[ $# -lt 2 ]] || [[ ! "$2" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
                echo -e "${RED}Error: --version requires a version argument (X.Y.Z)${NC}"
                exit 2
            fi
            TARGET_VERSION="$2"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--fix] [--dry-run] [--version X.Y.Z] [--json]"
            echo ""
            echo "  --fix         Auto-fix mechanical items (Tier 2 version refs)"
            echo "  --dry-run     Report only, no changes (default)"
            echo "  --version     Check against specific version (default: from plugin.json)"
            echo "  --json        Output results as JSON"
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown argument '$1'${NC}"
            echo "Usage: $0 [--fix] [--dry-run] [--version X.Y.Z] [--json]"
            exit 2
            ;;
    esac
    shift
done

cd "$PLUGIN_DIR"

# Read current version from plugin.json
CURRENT_VERSION=$(python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['version'])" 2>/dev/null || echo "unknown")

if [[ -n "$TARGET_VERSION" ]]; then
    CHECK_VERSION="$TARGET_VERSION"
else
    CHECK_VERSION="$CURRENT_VERSION"
fi

if [[ "$CHECK_VERSION" == "unknown" ]]; then
    echo -e "${RED}Error: Cannot determine version from plugin.json${NC}"
    exit 2
fi

# Derive previous version for stale-ref detection (decrement patch)
MAJOR=$(echo "$CHECK_VERSION" | cut -d. -f1)
MINOR=$(echo "$CHECK_VERSION" | cut -d. -f2)
PATCH=$(echo "$CHECK_VERSION" | cut -d. -f3)

if (( PATCH > 0 )); then
    PREV_VERSION="${MAJOR}.${MINOR}.$((PATCH - 1))"
else
    # If patch is 0, check previous minor
    if (( MINOR > 0 )); then
        PREV_VERSION="${MAJOR}.$((MINOR - 1)).0"
    else
        PREV_VERSION=""
    fi
fi

# ---------------------------------------------------------------------------
# Result tracking
# ---------------------------------------------------------------------------
TIER1_ISSUES=0
TIER2_ISSUES=0
TIER2_FIXED=0
TIER3_ISSUES=0
declare -a FINDINGS=()

add_finding() {
    local tier="$1" file="$2" detail="$3" fixable="$4"
    FINDINGS+=("${tier}|${file}|${detail}|${fixable}")
}

# ---------------------------------------------------------------------------
# Phase 1: Tier 1 — bump-version.sh --verify
# ---------------------------------------------------------------------------
if [[ "$JSON_MODE" != true ]]; then
    echo -e "${CYAN}Post-Release Sweep${NC} (v${CHECK_VERSION})"
    echo "=============================="
    if [[ "$FIX_MODE" == true ]]; then
        echo -e "  Mode: ${YELLOW}fix${NC}"
    else
        echo -e "  Mode: ${CYAN}dry-run${NC}"
    fi
    echo ""
    echo -e "${CYAN}Phase 1: Tier 1 (bump-version.sh --verify)${NC}"
fi

TIER1_OUTPUT=""
TIER1_EXIT=0
TIER1_OUTPUT=$("$SCRIPT_DIR/bump-version.sh" --verify 2>&1) || TIER1_EXIT=$?

if [[ $TIER1_EXIT -ne 0 ]]; then
    TIER1_ISSUES=1
    add_finding "1" "bump-version.sh" "Tier 1 drift detected (run bump-version.sh --verify for details)" "auto"
    if [[ "$JSON_MODE" != true ]]; then
        echo -e "  ${RED}DRIFT${NC} — Tier 1 inconsistency found"
        echo -e "  Fix: ./scripts/bump-version.sh ${CHECK_VERSION}"
    fi
else
    if [[ "$JSON_MODE" != true ]]; then
        echo -e "  ${GREEN}CLEAN${NC} — all Tier 1 files consistent"
    fi
fi

# ---------------------------------------------------------------------------
# Phase 2: Tier 2 — version refs in secondary files
# ---------------------------------------------------------------------------
if [[ "$JSON_MODE" != true ]]; then
    echo ""
    echo -e "${CYAN}Phase 2: Tier 2 version refs (secondary files)${NC}"
fi

# Files NOT managed by bump-version.sh that commonly have version references
TIER2_VERSION_FILES=(
    "docs/reference/REFCARD-RELEASE.md"
    "docs/reference/REFCARD-HOMEBREW.md"
    "docs/reference/REFCARD-BUMP-VERSION.md"
    "docs/reference/REFCARD-CHECK.md"
    "docs/reference/REFCARD-TESTING.md"
    "docs/guide/badge-management.md"
    "docs/guide/homebrew-automation.md"
    "docs/guide/homebrew-installation.md"
    "docs/guide/getting-started.md"
    "docs/guide/marketplace-distribution.md"
    # Note: docs/VERSION-HISTORY.md excluded — it legitimately lists all past versions
    "docs/testing-quickstart.md"
)

if [[ -n "$PREV_VERSION" ]]; then
    for file in "${TIER2_VERSION_FILES[@]}"; do
        [[ -f "$file" ]] || continue

        # Search for old version strings (vX.Y.Z or X.Y.Z)
        STALE_LINES=""
        STALE_LINES=$(grep -n "v${PREV_VERSION}\b\|\"${PREV_VERSION}\"\| ${PREV_VERSION} \|${PREV_VERSION}$\|version-${PREV_VERSION}" "$file" 2>/dev/null || true)

        if [[ -n "$STALE_LINES" ]]; then
            STALE_COUNT=$(echo "$STALE_LINES" | wc -l | tr -d ' ')
            TIER2_ISSUES=$((TIER2_ISSUES + STALE_COUNT))

            if [[ "$FIX_MODE" == true ]]; then
                # Auto-fix: replace old version with current in known patterns
                sed -i '' "s|v${PREV_VERSION}|v${CHECK_VERSION}|g" "$file"
                sed -i '' "s|version-${PREV_VERSION}|version-${CHECK_VERSION}|g" "$file"
                sed -i '' "s|\"${PREV_VERSION}\"|\"${CHECK_VERSION}\"|g" "$file"
                TIER2_FIXED=$((TIER2_FIXED + STALE_COUNT))
                add_finding "2" "$file" "${STALE_COUNT} stale v${PREV_VERSION} ref(s) — FIXED" "auto"
                if [[ "$JSON_MODE" != true ]]; then
                    echo -e "  ${GREEN}FIXED${NC} $file (${STALE_COUNT} ref(s))"
                fi
            else
                add_finding "2" "$file" "${STALE_COUNT} stale v${PREV_VERSION} ref(s)" "auto"
                if [[ "$JSON_MODE" != true ]]; then
                    echo -e "  ${YELLOW}STALE${NC} $file (${STALE_COUNT} ref(s) to v${PREV_VERSION})"
                    # Show first few lines for context
                    echo "$STALE_LINES" | head -3 | while IFS= read -r line; do
                        echo -e "    ${line}"
                    done
                fi
            fi
        fi
    done

    if [[ $TIER2_ISSUES -eq 0 ]] && [[ "$JSON_MODE" != true ]]; then
        echo -e "  ${GREEN}CLEAN${NC} — no stale v${PREV_VERSION} refs in secondary files"
    fi
else
    if [[ "$JSON_MODE" != true ]]; then
        echo -e "  ${YELLOW}SKIP${NC} — cannot derive previous version (patch=0, minor=0)"
    fi
fi

# ---------------------------------------------------------------------------
# Phase 3: Tier 2 — date/count staleness
# ---------------------------------------------------------------------------
if [[ "$JSON_MODE" != true ]]; then
    echo ""
    echo -e "${CYAN}Phase 3: Tier 2 date/count refs${NC}"
fi

PHASE3_ISSUES=0

# Check for stale test counts in docs (compare against actual test count from CLAUDE.md)
CLAUDE_TEST_COUNT=""
if [[ -f "CLAUDE.md" ]]; then
    CLAUDE_TEST_COUNT=$(grep -o '[0-9]* tests passing' CLAUDE.md | head -1 | grep -o '[0-9]*' || true)
fi

# Check docs that mention test counts
TEST_COUNT_FILES=(
    "docs/testing-quickstart.md"
    "docs/guide/test-architecture.md"
    "docs/guide/integration-testing.md"
)

for file in "${TEST_COUNT_FILES[@]}"; do
    [[ -f "$file" ]] || continue
    FILE_TEST_COUNTS=$(grep -on '[0-9]* tests\? passing' "$file" 2>/dev/null || true)
    if [[ -n "$FILE_TEST_COUNTS" ]] && [[ -n "$CLAUDE_TEST_COUNT" ]]; then
        while IFS= read -r match; do
            FILE_COUNT=$(echo "$match" | grep -o '[0-9]* tests' | grep -o '[0-9]*')
            if [[ -n "$FILE_COUNT" ]] && [[ "$FILE_COUNT" != "$CLAUDE_TEST_COUNT" ]]; then
                LINE_NUM=$(echo "$match" | cut -d: -f1)
                PHASE3_ISSUES=$((PHASE3_ISSUES + 1))
                TIER2_ISSUES=$((TIER2_ISSUES + 1))
                add_finding "2" "${file}:${LINE_NUM}" "test count ${FILE_COUNT} != ${CLAUDE_TEST_COUNT} (CLAUDE.md)" "manual"
                if [[ "$JSON_MODE" != true ]]; then
                    echo -e "  ${YELLOW}STALE${NC} ${file}:${LINE_NUM} — ${FILE_COUNT} tests (expected ${CLAUDE_TEST_COUNT})"
                fi
            fi
        done <<< "$FILE_TEST_COUNTS"
    fi
done

# Check for stale command/skill/agent counts in docs
CMD_COUNT=$(find commands -name "*.md" ! -name "index.md" ! -name "README.md" 2>/dev/null | wc -l | tr -d ' ')
SKILL_COUNT=$(find skills -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
AGENT_COUNT=$(find agents -name "*.md" 2>/dev/null | wc -l | tr -d ' ')

COUNT_CHECK_FILES=(
    "docs/testing-quickstart.md"
    "docs/guide/getting-started.md"
)

for file in "${COUNT_CHECK_FILES[@]}"; do
    [[ -f "$file" ]] || continue
    # Check for "N commands" patterns that don't match actual count
    FILE_CMD_COUNTS=$(grep -on '[0-9]* commands' "$file" 2>/dev/null || true)
    if [[ -n "$FILE_CMD_COUNTS" ]]; then
        while IFS= read -r match; do
            [[ -z "$match" ]] && continue
            FC=$(echo "$match" | grep -o '[0-9]* commands' | grep -o '[0-9]*')
            if [[ -n "$FC" ]] && [[ "$FC" != "$CMD_COUNT" ]]; then
                LINE_NUM=$(echo "$match" | cut -d: -f1)
                PHASE3_ISSUES=$((PHASE3_ISSUES + 1))
                TIER2_ISSUES=$((TIER2_ISSUES + 1))
                add_finding "2" "${file}:${LINE_NUM}" "command count ${FC} != ${CMD_COUNT} actual" "manual"
                if [[ "$JSON_MODE" != true ]]; then
                    echo -e "  ${YELLOW}STALE${NC} ${file}:${LINE_NUM} — ${FC} commands (expected ${CMD_COUNT})"
                fi
            fi
        done <<< "$FILE_CMD_COUNTS"
    fi
done

if [[ $PHASE3_ISSUES -eq 0 ]] && [[ "$JSON_MODE" != true ]]; then
    echo -e "  ${GREEN}CLEAN${NC} — date/count refs look current"
fi

# ---------------------------------------------------------------------------
# Phase 4: Tier 3 — content staleness (report only, never auto-fix)
# ---------------------------------------------------------------------------
if [[ "$JSON_MODE" != true ]]; then
    echo ""
    echo -e "${CYAN}Phase 4: Tier 3 content staleness (review only)${NC}"
fi

# Compare docs/index.md info box against CHANGELOG latest version
if [[ -f "docs/index.md" ]] && [[ -f "CHANGELOG.md" ]]; then
    CHANGELOG_VER=$(grep -m1 '^\#\# \[' CHANGELOG.md | grep -o '[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*' || true)
    INDEX_VER=$(grep -o 'Latest: v[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*' docs/index.md | head -1 | grep -o '[0-9].*' || true)

    if [[ -n "$CHANGELOG_VER" ]] && [[ -n "$INDEX_VER" ]] && [[ "$CHANGELOG_VER" != "$INDEX_VER" ]]; then
        TIER3_ISSUES=$((TIER3_ISSUES + 1))
        add_finding "3" "docs/index.md" "info box v${INDEX_VER} != CHANGELOG v${CHANGELOG_VER}" "manual"
        if [[ "$JSON_MODE" != true ]]; then
            echo -e "  ${YELLOW}REVIEW${NC} docs/index.md info box (v${INDEX_VER}) vs CHANGELOG (v${CHANGELOG_VER})"
        fi
    fi
fi

# Check if README feature list is stale (compare feature count keywords)
if [[ -f "README.md" ]] && [[ -f "CHANGELOG.md" ]]; then
    # Simple heuristic: check if CHANGELOG mentions features not in README
    CHANGELOG_FEATURES=$(grep -c '^\- \*\*' CHANGELOG.md 2>/dev/null || true)
    CHANGELOG_FEATURES="${CHANGELOG_FEATURES:-0}"
    README_FEATURES=$(grep -c '^\- :' README.md 2>/dev/null || true)
    README_FEATURES="${README_FEATURES:-0}"
    if (( CHANGELOG_FEATURES > 0 )) && (( README_FEATURES > 0 )); then
        # Just report — this always needs human judgment
        if [[ "$JSON_MODE" != true ]]; then
            echo -e "  ${CYAN}INFO${NC}  README.md has ${README_FEATURES} feature items; CHANGELOG has ${CHANGELOG_FEATURES} feature entries"
        fi
    fi
fi

if [[ $TIER3_ISSUES -eq 0 ]] && [[ "$JSON_MODE" != true ]]; then
    echo -e "  ${GREEN}CLEAN${NC} — no obvious content staleness"
fi

# ---------------------------------------------------------------------------
# Phase 5: Summary
# ---------------------------------------------------------------------------
TOTAL_ISSUES=$((TIER1_ISSUES + TIER2_ISSUES + TIER3_ISSUES))

if [[ "$JSON_MODE" == true ]]; then
    # JSON output
    echo "{"
    echo "  \"version\": \"${CHECK_VERSION}\","
    echo "  \"previous_version\": \"${PREV_VERSION}\","
    echo "  \"mode\": \"$(if [[ "$FIX_MODE" == true ]]; then echo "fix"; else echo "dry-run"; fi)\","
    echo "  \"tier1_issues\": ${TIER1_ISSUES},"
    echo "  \"tier2_issues\": ${TIER2_ISSUES},"
    echo "  \"tier2_fixed\": ${TIER2_FIXED},"
    echo "  \"tier3_issues\": ${TIER3_ISSUES},"
    echo "  \"total_issues\": ${TOTAL_ISSUES},"
    echo "  \"findings\": ["
    FIRST_FINDING=true
    for finding in "${FINDINGS[@]:-}"; do
        [[ -z "$finding" ]] && continue
        IFS='|' read -r tier file detail fixable <<< "$finding"
        if [[ "$FIRST_FINDING" == true ]]; then
            FIRST_FINDING=false
        else
            printf ',\n'
        fi
        # Escape double quotes in fields to produce valid JSON
        file="${file//\"/\\\"}"
        detail="${detail//\"/\\\"}"
        printf '    {"tier": %s, "file": "%s", "detail": "%s", "fixable": "%s"}' "$tier" "$file" "$detail" "$fixable"
    done
    [[ "$FIRST_FINDING" == false ]] && echo ""
    echo "  ],"
    echo "  \"clean\": $(if [[ $TOTAL_ISSUES -eq 0 ]]; then echo "true"; else echo "false"; fi)"
    echo "}"
else
    echo ""
    echo "=============================="
    if [[ $TOTAL_ISSUES -eq 0 ]]; then
        echo -e "${GREEN}ALL CLEAN${NC} — no post-release drift detected"
    else
        echo -e "${YELLOW}Summary:${NC}"
        [[ $TIER1_ISSUES -gt 0 ]] && echo -e "  Tier 1 (core):    ${RED}${TIER1_ISSUES} issue(s)${NC}"
        [[ $TIER2_ISSUES -gt 0 ]] && echo -e "  Tier 2 (secondary): ${YELLOW}${TIER2_ISSUES} issue(s)${NC} (${TIER2_FIXED} auto-fixed)"
        [[ $TIER3_ISSUES -gt 0 ]] && echo -e "  Tier 3 (content): ${CYAN}${TIER3_ISSUES} item(s)${NC} (needs review)"
        echo ""
        if [[ $FIX_MODE == true ]] && [[ $TIER2_FIXED -gt 0 ]]; then
            echo -e "${GREEN}Auto-fixed ${TIER2_FIXED} item(s).${NC} Remaining issues need manual review."
        elif [[ $TOTAL_ISSUES -gt 0 ]]; then
            echo -e "Run with ${CYAN}--fix${NC} to auto-correct Tier 2 version refs."
        fi
    fi
fi

if [[ $TOTAL_ISSUES -eq 0 ]]; then
    exit 0
else
    exit 1
fi
