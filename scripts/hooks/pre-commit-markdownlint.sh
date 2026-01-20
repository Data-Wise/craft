#!/usr/bin/env bash
#
# Pre-commit hook for markdownlint list spacing enforcement
#
# Checks staged markdown files for MD030, MD004, and MD032 violations.
# Offers interactive auto-fix if violations found.
#
# Installation:
#   ./scripts/install-hooks.sh
#
# Manual installation:
#   ln -sf ../../scripts/hooks/pre-commit-markdownlint.sh .git/hooks/pre-commit
#
# Bypass (not recommended):
#   git commit --no-verify

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get staged markdown files
STAGED_MD_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.md$' || true)

if [ -z "$STAGED_MD_FILES" ]; then
  echo -e "${GREEN}✓${NC} No markdown files staged"
  exit 0
fi

echo -e "${BLUE}🔍${NC} Checking markdown list spacing..."

# Run markdownlint on staged files
if npx -y markdownlint-cli2 $STAGED_MD_FILES 2>&1 | grep -E "(MD030|MD004|MD032)"; then
  echo ""
  echo -e "${RED}❌${NC} Markdown list spacing violations found"
  echo ""
  echo "Violations detected:"
  echo "  • MD030: Extra spaces after list markers"
  echo "  • MD004: Inconsistent list marker style"
  echo "  • MD032: Missing blank lines around lists"
  echo ""

  # Offer auto-fix
  read -p "Auto-fix these issues? (y/n) " -n 1 -r
  echo ""

  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}🔧${NC} Auto-fixing..."
    npx -y markdownlint-cli2 --fix $STAGED_MD_FILES

    echo ""
    echo -e "${GREEN}✅${NC} Auto-fix complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Review the changes: git diff"
    echo "  2. Stage the fixes: git add $STAGED_MD_FILES"
    echo "  3. Commit again: git commit"
    echo ""
    exit 1  # Block commit, require re-staging
  else
    echo ""
    echo -e "${YELLOW}⚠️${NC}  Commit blocked. Fix manually with:"
    echo "  npx -y markdownlint-cli2 --fix $STAGED_MD_FILES"
    echo ""
    echo "Or bypass this hook (not recommended):"
    echo "  git commit --no-verify"
    echo ""
    exit 1
  fi
else
  echo -e "${GREEN}✓${NC} All markdown files pass list spacing checks"
  exit 0
fi
