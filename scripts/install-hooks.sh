#!/usr/bin/env bash
#
# Install Git hooks for Craft development
#
# This script sets up pre-commit hooks to ensure code quality:
#   - Markdownlint list spacing enforcement (MD030, MD004, MD032)
#
# Usage:
#   ./scripts/install-hooks.sh

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Installing Git hooks for Craft...${NC}"
echo ""

# Check if we're in a git repository
if [ ! -d .git ]; then
  echo -e "${YELLOW}⚠️  Not in a git repository root${NC}"
  echo "Please run this script from the repository root:"
  echo "  cd /path/to/craft"
  echo "  ./scripts/install-hooks.sh"
  exit 1
fi

# Install pre-commit hook
echo "Installing pre-commit hook..."
HOOK_SRC="scripts/hooks/pre-commit-markdownlint.sh"
HOOK_DEST=".git/hooks/pre-commit"

if [ ! -f "$HOOK_SRC" ]; then
  echo -e "${YELLOW}⚠️  Hook source not found: $HOOK_SRC${NC}"
  exit 1
fi

# Backup existing hook if present
if [ -f "$HOOK_DEST" ]; then
  echo "  ℹ️  Backing up existing pre-commit hook..."
  cp "$HOOK_DEST" "$HOOK_DEST.backup.$(date +%Y%m%d-%H%M%S)"
fi

# Create symlink
ln -sf "../../$HOOK_SRC" "$HOOK_DEST"

echo -e "${GREEN}✓${NC} Pre-commit hook installed"
echo ""

# Verify installation
if [ -x "$HOOK_DEST" ]; then
  echo -e "${GREEN}✅ Installation complete!${NC}"
  echo ""
  echo "The following hooks are now active:"
  echo "  • Pre-commit: Markdownlint list spacing"
  echo ""
  echo "Hooks will run automatically on 'git commit'."
  echo "To bypass (not recommended): git commit --no-verify"
else
  echo -e "${YELLOW}⚠️  Hook installed but may not be executable${NC}"
  echo "Try: chmod +x $HOOK_DEST"
  exit 1
fi
