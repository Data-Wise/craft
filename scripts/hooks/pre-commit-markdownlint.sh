#!/usr/bin/env bash
#
# Pre-commit hook for comprehensive markdownlint enforcement
#
# Checks staged markdown files for 24 markdown quality rules.
# Offers interactive auto-fix if violations found.
#
# Rules enforced:
#   Lists: MD004, MD005, MD007, MD029, MD030, MD031, MD032
#   Headings: MD003, MD022, MD023, MD036
#   Code: MD040, MD046, MD048
#   Links/Images: MD042, MD045, MD052, MD056
#   Whitespace: MD009, MD010, MD012
#   Inline: MD034, MD049, MD050
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

# Markdown rules to check (24 rules)
MD_RULES="MD003|MD004|MD005|MD007|MD009|MD010|MD012|MD022|MD023|MD029|MD030|MD031|MD032|MD034|MD036|MD040|MD042|MD045|MD046|MD048|MD049|MD050|MD052|MD056"

# Get staged markdown files
STAGED_MD_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.md$' || true)

if [ -z "$STAGED_MD_FILES" ]; then
  echo -e "${GREEN}✓${NC} No markdown files staged"
  exit 0
fi

echo -e "${BLUE}🔍${NC} Checking markdown quality (24 rules)..."

# Run markdownlint on staged files
VIOLATIONS=$(npx -y markdownlint-cli2 $STAGED_MD_FILES 2>&1 || true)

if echo "$VIOLATIONS" | grep -E "($MD_RULES)"; then
  echo ""
  echo -e "${RED}❌${NC} Markdown quality violations found"
  echo ""
  echo "Common violations:"
  echo "  Lists: MD004 (marker style), MD030 (spaces), MD032 (blank lines)"
  echo "  Headings: MD003 (style), MD022 (blank lines), MD036 (no emphasis)"
  echo "  Code: MD040 (language required), MD046/MD048 (consistent style)"
  echo "  Links: MD042 (empty links), MD045 (alt text), MD052 (references)"
  echo "  Whitespace: MD009 (trailing), MD010 (tabs), MD012 (multiple blanks)"
  echo "  Inline: MD034 (bare URLs), MD049/MD050 (emphasis style)"
  echo ""
  echo "See full list: npx markdownlint-cli2 --help | grep MD0"
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
  echo -e "${GREEN}✓${NC} All markdown files pass quality checks (24 rules)"
  exit 0
fi
