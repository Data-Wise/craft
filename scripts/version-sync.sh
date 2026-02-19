#!/usr/bin/env bash
# scripts/version-sync.sh - Version consistency checker
# Checks that all version references in a project match the source of truth.
#
# Usage:
#   ./scripts/version-sync.sh              # Check all version files
#   ./scripts/version-sync.sh --quiet      # Exit code only (for hooks)
#   ./scripts/version-sync.sh --fix        # Show fix commands
#
# Exit codes:
#   0 = all versions match (or no version files found)
#   1 = version mismatch detected
#
# Convention-based discovery: detects project type automatically.
# Source of truth priority:
#   1. .claude-plugin/plugin.json (Claude Code plugin)
#   2. package.json (Node.js)
#   3. pyproject.toml (Python)
#   4. DESCRIPTION (R package)
#   5. Cargo.toml (Rust)

set -euo pipefail

# Options
QUIET=false
SHOW_FIX=false
PROJECT_ROOT="${PROJECT_ROOT:-.}"

for arg in "$@"; do
    case "$arg" in
        --quiet|-q) QUIET=true ;;
        --fix) SHOW_FIX=true ;;
        --root=*) PROJECT_ROOT="${arg#--root=}" ;;
    esac
done

# Colors (only if stdout is a terminal and not quiet)
if [[ -t 1 ]] && [[ "$QUIET" == false ]]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    GREEN='' RED='' YELLOW='' BOLD='' NC=''
fi

# ============================================================================
# Source of Truth Discovery
# ============================================================================

SOT_VERSION=""
SOT_FILE=""

discover_sot() {
    cd "$PROJECT_ROOT"

    # Priority 1: Claude Code plugin
    if [[ -f .claude-plugin/plugin.json ]]; then
        SOT_VERSION=$(jq -r '.version // empty' .claude-plugin/plugin.json 2>/dev/null)
        SOT_FILE=".claude-plugin/plugin.json"
        return
    fi

    # Priority 2: plugin.json (root-level)
    if [[ -f plugin.json ]]; then
        SOT_VERSION=$(jq -r '.version // empty' plugin.json 2>/dev/null)
        SOT_FILE="plugin.json"
        return
    fi

    # Priority 3: package.json (Node.js)
    if [[ -f package.json ]]; then
        SOT_VERSION=$(jq -r '.version // empty' package.json 2>/dev/null)
        SOT_FILE="package.json"
        return
    fi

    # Priority 4: pyproject.toml (Python)
    if [[ -f pyproject.toml ]]; then
        SOT_VERSION=$(grep -m1 '^version' pyproject.toml | sed 's/.*"\(.*\)"/\1/' 2>/dev/null)
        SOT_FILE="pyproject.toml"
        return
    fi

    # Priority 5: DESCRIPTION (R package)
    if [[ -f DESCRIPTION ]]; then
        SOT_VERSION=$(grep -m1 '^Version:' DESCRIPTION | awk '{print $2}' 2>/dev/null)
        SOT_FILE="DESCRIPTION"
        return
    fi

    # Priority 6: Cargo.toml (Rust)
    if [[ -f Cargo.toml ]]; then
        SOT_VERSION=$(grep -m1 '^version' Cargo.toml | sed 's/.*"\(.*\)"/\1/' 2>/dev/null)
        SOT_FILE="Cargo.toml"
        return
    fi
}

# ============================================================================
# Version Extraction from Various File Types
# ============================================================================

ERRORS=0
CHECKED=0
MISMATCHES=()

check_file() {
    local file="$1"
    local description="$2"
    local version=""

    [[ -f "$file" ]] || return 0

    case "$file" in
        *.json)
            version=$(jq -r '.version // empty' "$file" 2>/dev/null)
            ;;
        CLAUDE.md)
            version=$(grep -oE 'Current Version:.*v?[0-9]+\.[0-9]+\.[0-9]+' "$file" 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
            ;;
        DESCRIPTION)
            version=$(grep -m1 '^Version:' "$file" 2>/dev/null | awk '{print $2}')
            ;;
        *.toml)
            version=$(grep -m1 '^version' "$file" 2>/dev/null | sed 's/.*"\(.*\)"/\1/')
            ;;
    esac

    # Skip if no version found (file doesn't contain version info)
    [[ -z "$version" ]] && return 0

    CHECKED=$((CHECKED + 1))

    if [[ "$version" == "$SOT_VERSION" ]]; then
        [[ "$QUIET" == false ]] && echo -e "  ${GREEN}✅${NC} ${file}: v${version}"
    else
        ERRORS=$((ERRORS + 1))
        MISMATCHES+=("$file:$version")
        [[ "$QUIET" == false ]] && echo -e "  ${RED}⚠${NC}  ${file} (v${version}) — ${RED}MISMATCH${NC}"
    fi
}

check_source_constants() {
    # Grep for VERSION = "x.y.z" or __version__ = "x.y.z" in source files
    local patterns='(__version__|VERSION)\s*=\s*["\x27]([0-9]+\.[0-9]+\.[0-9]+)'

    while IFS= read -r match; do
        local file version
        file=$(echo "$match" | cut -d: -f1)
        version=$(echo "$match" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)

        # Skip the SOT file itself
        [[ "$file" == "$SOT_FILE" ]] && continue

        [[ -z "$version" ]] && continue
        CHECKED=$((CHECKED + 1))

        if [[ "$version" == "$SOT_VERSION" ]]; then
            [[ "$QUIET" == false ]] && echo -e "  ${GREEN}✅${NC} ${file}: v${version} (source constant)"
        else
            ERRORS=$((ERRORS + 1))
            MISMATCHES+=("$file:$version")
            [[ "$QUIET" == false ]] && echo -e "  ${RED}⚠${NC}  ${file} (v${version}) — ${RED}MISMATCH${NC} (source constant)"
        fi
    done < <(grep -rnE "$patterns" --include='*.py' --include='*.ts' --include='*.js' --include='*.rb' . 2>/dev/null | grep -v node_modules | grep -v '.git/' || true)
}

check_test_expectations() {
    # Only check tests that explicitly reference the project version constant
    # (e.g., "expected_version", "PROJECT_VERSION", "current_version")
    # Skip test fixtures with arbitrary version strings.
    local patterns='(expected_version|PROJECT_VERSION|current_version|PLUGIN_VERSION).*[0-9]+\.[0-9]+\.[0-9]+'

    while IFS= read -r match; do
        local file version
        file=$(echo "$match" | cut -d: -f1)
        version=$(echo "$match" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)

        [[ -z "$version" ]] && continue
        CHECKED=$((CHECKED + 1))

        if [[ "$version" == "$SOT_VERSION" ]]; then
            [[ "$QUIET" == false ]] && echo -e "  ${GREEN}✅${NC} ${file}: v${version} (test expectation)"
        else
            ERRORS=$((ERRORS + 1))
            MISMATCHES+=("$file:$version")
            [[ "$QUIET" == false ]] && echo -e "  ${RED}⚠${NC}  ${file} (v${version}) — ${RED}MISMATCH${NC} (test expectation)"
        fi
    done < <(grep -rnE "$patterns" --include='*.py' --include='*.ts' --include='*.js' tests/ test/ 2>/dev/null | grep -v node_modules || true)
}

# ============================================================================
# Main
# ============================================================================

discover_sot

if [[ -z "$SOT_VERSION" ]]; then
    [[ "$QUIET" == false ]] && echo "No version source of truth found. Skipping version sync check."
    exit 0
fi

if [[ "$QUIET" == false ]]; then
    echo -e "${BOLD}Version Consistency Check${NC}"
    echo "========================="
    echo -e "Source of truth: ${BOLD}${SOT_FILE}${NC} → v${SOT_VERSION}"
    echo ""
fi

# Check known version files (skip the SOT file itself)
for candidate in \
    package.json \
    plugin.json \
    .claude-plugin/plugin.json \
    pyproject.toml \
    DESCRIPTION \
    Cargo.toml \
    CLAUDE.md \
    .STATUS; do

    [[ "$candidate" == "$SOT_FILE" ]] && continue
    check_file "$candidate" ""
done

# Check source code constants
check_source_constants

# Check test expectations
check_test_expectations

# Summary
if [[ "$QUIET" == false ]]; then
    echo ""
    if [[ $ERRORS -eq 0 ]]; then
        echo -e "${GREEN}All ${CHECKED} version references match v${SOT_VERSION}${NC}"
    else
        echo -e "${RED}${ERRORS} mismatch(es) found${NC} out of ${CHECKED} checked"
        if [[ "$SHOW_FIX" == true ]]; then
            echo ""
            echo "Fix: Update these files to v${SOT_VERSION}:"
            for m in "${MISMATCHES[@]}"; do
                echo "  - ${m%%:*} (currently v${m##*:})"
            done
        fi
    fi
fi

if [[ $ERRORS -eq 0 ]]; then
    exit 0
else
    exit 1
fi
