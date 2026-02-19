#!/usr/bin/env bash
# scripts/claude-md-health.sh - CLAUDE.md health check (stub)
# Checks CLAUDE.md for staleness, size, and accuracy.
#
# NOTE: This is a stub that will be filled in when the claude-md-refactor
# feature branch is merged. For now, it performs basic checks only.
#
# Usage:
#   ./scripts/claude-md-health.sh              # Basic health check
#   ./scripts/claude-md-health.sh --quiet      # Exit code only
#
# Exit codes:
#   0 = healthy
#   1 = issues detected

set -euo pipefail

QUIET=false
CLAUDE_MD="${1:-CLAUDE.md}"

for arg in "$@"; do
    case "$arg" in
        --quiet|-q) QUIET=true ;;
    esac
done

# Colors
if [[ -t 1 ]] && [[ "$QUIET" == false ]]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    GREEN='' RED='' YELLOW='' BOLD='' NC=''
fi

ISSUES=0

if [[ ! -f "$CLAUDE_MD" ]]; then
    [[ "$QUIET" == false ]] && echo -e "${YELLOW}No CLAUDE.md found${NC}"
    exit 0
fi

if [[ "$QUIET" == false ]]; then
    echo -e "${BOLD}CLAUDE.md Health Check${NC}"
    echo "======================"
fi

# Check 1: Line count (warn if > 200 lines — gets truncated in system prompt)
LINE_COUNT=$(wc -l < "$CLAUDE_MD" | tr -d ' ')
if [[ $LINE_COUNT -gt 200 ]]; then
    ISSUES=$((ISSUES + 1))
    [[ "$QUIET" == false ]] && echo -e "  ${YELLOW}⚠${NC}  ${LINE_COUNT} lines (>200 — may be truncated in system prompt)"
else
    [[ "$QUIET" == false ]] && echo -e "  ${GREEN}✅${NC} ${LINE_COUNT} lines (within limit)"
fi

# Check 2: Version presence
if grep -qE 'Current Version:|version:' "$CLAUDE_MD" 2>/dev/null; then
    [[ "$QUIET" == false ]] && echo -e "  ${GREEN}✅${NC} Version reference found"
else
    ISSUES=$((ISSUES + 1))
    [[ "$QUIET" == false ]] && echo -e "  ${YELLOW}⚠${NC}  No version reference in CLAUDE.md"
fi

# Check 3: Staleness (last modified vs recent commits)
CLAUDE_MTIME=$(stat -f %m "$CLAUDE_MD" 2>/dev/null || stat -c %Y "$CLAUDE_MD" 2>/dev/null || echo 0)
LATEST_COMMIT=$(git log -1 --format=%ct 2>/dev/null || echo 0)
STALENESS_DAYS=$(( (LATEST_COMMIT - CLAUDE_MTIME) / 86400 ))

if [[ $STALENESS_DAYS -gt 30 ]]; then
    ISSUES=$((ISSUES + 1))
    [[ "$QUIET" == false ]] && echo -e "  ${YELLOW}⚠${NC}  CLAUDE.md is ~${STALENESS_DAYS} days older than latest commit"
elif [[ $STALENESS_DAYS -gt 0 ]]; then
    [[ "$QUIET" == false ]] && echo -e "  ${GREEN}✅${NC} CLAUDE.md updated within ${STALENESS_DAYS} day(s) of latest commit"
else
    [[ "$QUIET" == false ]] && echo -e "  ${GREEN}✅${NC} CLAUDE.md is up to date"
fi

# Check 4: Count accuracy (if claims like "N commands" exist)
CLAIMED_COMMANDS=$(grep -oE '[0-9]+ commands' "$CLAUDE_MD" 2>/dev/null | head -1 | grep -oE '[0-9]+' || echo "")
if [[ -n "$CLAIMED_COMMANDS" ]] && [[ -d commands/ ]]; then
    ACTUAL_COMMANDS=$(find commands/ -name '*.md' -not -path '*/\.*' | wc -l | tr -d ' ')
    if [[ "$CLAIMED_COMMANDS" != "$ACTUAL_COMMANDS" ]]; then
        ISSUES=$((ISSUES + 1))
        [[ "$QUIET" == false ]] && echo -e "  ${YELLOW}⚠${NC}  Claims ${CLAIMED_COMMANDS} commands but found ${ACTUAL_COMMANDS}"
    else
        [[ "$QUIET" == false ]] && echo -e "  ${GREEN}✅${NC} Command count accurate (${ACTUAL_COMMANDS})"
    fi
fi

# Summary
if [[ "$QUIET" == false ]]; then
    echo ""
    if [[ $ISSUES -eq 0 ]]; then
        echo -e "${GREEN}CLAUDE.md is healthy${NC}"
    else
        echo -e "${YELLOW}${ISSUES} issue(s) found${NC}"
        echo "Run /craft:docs:claude-md:sync to fix"
    fi
fi

if [[ $ISSUES -eq 0 ]]; then
    exit 0
else
    exit 1
fi
