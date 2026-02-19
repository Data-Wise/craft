#!/usr/bin/env bash
# scripts/stale-ref-scan.sh - Detect stale references after file renames
# Compares current branch against base to find renames, then scans docs
# for references to old file names.
#
# Usage:
#   ./scripts/stale-ref-scan.sh              # Compare against dev
#   ./scripts/stale-ref-scan.sh main         # Compare against main
#   ./scripts/stale-ref-scan.sh --quiet      # Exit code only
#
# Exit codes:
#   0 = no stale references found
#   1 = stale references detected

set -euo pipefail

BASE_BRANCH="${1:-dev}"
QUIET=false

for arg in "$@"; do
    case "$arg" in
        --quiet|-q) QUIET=true ;;
    esac
done

# Colors (only if terminal and not quiet)
if [[ -t 1 ]] && [[ "$QUIET" == false ]]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    GREEN='' RED='' YELLOW='' BOLD='' NC=''
fi

STALE_COUNT=0

# Detect renames between base branch and HEAD
RENAMES=$(git diff --name-status "${BASE_BRANCH}...HEAD" 2>/dev/null | grep '^R' || true)

if [[ -z "$RENAMES" ]]; then
    [[ "$QUIET" == false ]] && echo -e "${GREEN}No renames detected since ${BASE_BRANCH}${NC}"
    exit 0
fi

if [[ "$QUIET" == false ]]; then
    echo -e "${BOLD}Stale Reference Scan${NC}"
    echo "===================="
    echo -e "Renames detected (git diff --name-status ${BASE_BRANCH}...HEAD):"
fi

# Process each rename
while IFS=$'\t' read -r status old_path new_path; do
    # Extract just the filename (without directory) for broader search
    old_basename=$(basename "$old_path")
    old_name="${old_basename%.*}"  # Strip extension

    [[ "$QUIET" == false ]] && echo -e "  ${status}  ${old_path} → ${new_path}"

    # Search docs/, README, tutorials for references to the old name
    # Search in common documentation locations
    SEARCH_DIRS=()
    [[ -d docs/ ]] && SEARCH_DIRS+=("docs/")
    [[ -f README.md ]] && SEARCH_DIRS+=("README.md")
    [[ -f CLAUDE.md ]] && SEARCH_DIRS+=("CLAUDE.md")
    [[ -d tutorials/ ]] && SEARCH_DIRS+=("tutorials/")

    if [[ ${#SEARCH_DIRS[@]} -eq 0 ]]; then
        continue
    fi

    # Search for the old path or old name
    while IFS= read -r ref; do
        ref_file=$(echo "$ref" | cut -d: -f1)
        ref_line=$(echo "$ref" | cut -d: -f2)
        STALE_COUNT=$((STALE_COUNT + 1))
        [[ "$QUIET" == false ]] && echo -e "  ${YELLOW}⚠${NC}  ${ref_file}:${ref_line} — references \"${old_name}\""
    done < <(grep -rnE "(${old_path}|${old_name})" "${SEARCH_DIRS[@]}" 2>/dev/null | grep -v '.git/' || true)

done <<< "$RENAMES"

# Summary
if [[ "$QUIET" == false ]]; then
    echo ""
    if [[ $STALE_COUNT -eq 0 ]]; then
        echo -e "${GREEN}No stale references found${NC}"
    else
        echo -e "${RED}${STALE_COUNT} stale reference(s) found${NC}"
        echo "Fix: Update the files above with new references"
    fi
fi

if [[ $STALE_COUNT -eq 0 ]]; then
    exit 0
else
    exit 1
fi
