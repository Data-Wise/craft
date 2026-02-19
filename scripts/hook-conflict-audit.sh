#!/usr/bin/env bash
# scripts/hook-conflict-audit.sh - Audit git hooks for potential conflicts
# Checks .githooks/, .husky/, and .git/hooks/ for rules that might block
# Claude Code operations (push, commit, branch guard, etc.)
#
# Usage:
#   ./scripts/hook-conflict-audit.sh              # Full audit
#   ./scripts/hook-conflict-audit.sh --quiet      # Exit code only
#   ./scripts/hook-conflict-audit.sh --for pr     # PR-specific audit
#   ./scripts/hook-conflict-audit.sh --for release # Release-specific audit
#
# Exit codes:
#   0 = no conflicts detected
#   1 = potential conflicts found

set -euo pipefail

QUIET=false
CONTEXT="general"

for arg in "$@"; do
    case "$arg" in
        --quiet|-q) QUIET=true ;;
        --for) shift_next=true ;;
        pr|release|commit)
            if [[ "${shift_next:-false}" == true ]]; then
                CONTEXT="$arg"
                shift_next=false
            fi
            ;;
    esac
done

# Handle --for with next arg
while [[ $# -gt 0 ]]; do
    case "$1" in
        --for) CONTEXT="${2:-general}"; shift 2 || break ;;
        *) shift ;;
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

CONFLICTS=0
WARNINGS=0

check_hook_file() {
    local file="$1"
    local hook_type="$2"

    [[ -f "$file" ]] || return 0

    local content
    content=$(cat "$file")

    # Check for branch guard patterns
    if echo "$content" | grep -qiE '(main|master|dev|develop).*protect|branch.*guard|branch.*block'; then
        WARNINGS=$((WARNINGS + 1))
        [[ "$QUIET" == false ]] && echo -e "  ${YELLOW}⚠${NC}  ${file}: Branch protection rule detected"

        # For PR/release context, this is a potential conflict
        if [[ "$CONTEXT" == "pr" ]] || [[ "$CONTEXT" == "release" ]]; then
            if echo "$content" | grep -qiE 'push.*block|push.*prevent|reject.*push'; then
                CONFLICTS=$((CONFLICTS + 1))
                [[ "$QUIET" == false ]] && echo -e "  ${RED}❌${NC}  ${file}: May block push to target branch"
            fi
        fi
    fi

    # Check for pre-commit hooks that might reject staged changes
    if [[ "$hook_type" == "pre-commit" ]]; then
        if echo "$content" | grep -qiE '(lint-staged|prettier|eslint|ruff).*--strict|exit 1'; then
            WARNINGS=$((WARNINGS + 1))
            [[ "$QUIET" == false ]] && echo -e "  ${YELLOW}⚠${NC}  ${file}: Strict linting in pre-commit (may reject auto-generated changes)"
        fi
    fi

    # Check for pre-push hooks
    if [[ "$hook_type" == "pre-push" ]]; then
        if echo "$content" | grep -qiE 'test|pytest|jest|npm test'; then
            WARNINGS=$((WARNINGS + 1))
            [[ "$QUIET" == false ]] && echo -e "  ${YELLOW}⚠${NC}  ${file}: Test suite in pre-push hook (may slow down or block push)"
        fi
    fi

    # Check for commit-msg hooks with strict format requirements
    if [[ "$hook_type" == "commit-msg" ]]; then
        if echo "$content" | grep -qiE 'conventional|commitlint|commit-msg.*reject'; then
            WARNINGS=$((WARNINGS + 1))
            [[ "$QUIET" == false ]] && echo -e "  ${YELLOW}⚠${NC}  ${file}: Commit message format enforcement detected"
        fi
    fi
}

scan_hook_directory() {
    local dir="$1"
    local label="$2"

    [[ -d "$dir" ]] || return 0

    [[ "$QUIET" == false ]] && echo -e "  Scanning ${BOLD}${label}${NC} (${dir})..."

    for hook_file in "$dir"/*; do
        [[ -f "$hook_file" ]] || continue
        local hook_name
        hook_name=$(basename "$hook_file")
        check_hook_file "$hook_file" "$hook_name"
    done
}

# ============================================================================
# Main
# ============================================================================

if [[ "$QUIET" == false ]]; then
    echo -e "${BOLD}Hook Conflict Audit${NC}"
    echo "==================="
    echo -e "Context: ${BOLD}${CONTEXT}${NC}"
    echo ""
fi

# Scan all known hook locations
scan_hook_directory ".githooks" ".githooks/"
scan_hook_directory ".husky" ".husky/"
scan_hook_directory ".git/hooks" ".git/hooks/"

# Check for husky configuration in package.json
if [[ -f package.json ]]; then
    if jq -e '.husky // empty' package.json &>/dev/null; then
        WARNINGS=$((WARNINGS + 1))
        [[ "$QUIET" == false ]] && echo -e "  ${YELLOW}⚠${NC}  package.json: Husky configuration detected"
    fi
fi

# Check for lint-staged configuration
if [[ -f .lintstagedrc ]] || [[ -f .lintstagedrc.json ]] || [[ -f .lintstagedrc.js ]]; then
    WARNINGS=$((WARNINGS + 1))
    [[ "$QUIET" == false ]] && echo -e "  ${YELLOW}⚠${NC}  lint-staged config detected (may reject auto-formatted files)"
fi

# Summary
if [[ "$QUIET" == false ]]; then
    echo ""
    if [[ $CONFLICTS -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
        echo -e "${GREEN}No hook conflicts detected${NC}"
    elif [[ $CONFLICTS -gt 0 ]]; then
        echo -e "${RED}${CONFLICTS} potential conflict(s), ${WARNINGS} warning(s)${NC}"
        echo "Review the hooks above before proceeding with ${CONTEXT}"
    else
        echo -e "${YELLOW}${WARNINGS} warning(s) (no blocking conflicts)${NC}"
    fi
fi

if [[ $CONFLICTS -eq 0 ]]; then
    exit 0
else
    exit 1
fi
