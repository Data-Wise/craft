#!/bin/bash
# Craft Plugin Uninstaller
# Removes craft plugin from Claude Code

set -e

PLUGIN_NAME="craft"
PLUGIN_DIR="$HOME/.claude/plugins/$PLUGIN_NAME"
MARKETPLACE_LINK="$HOME/.claude/local-marketplace/$PLUGIN_NAME"

echo "Uninstalling Craft plugin..."

# Remove plugin directory/symlink
if [ -L "$PLUGIN_DIR" ] || [ -d "$PLUGIN_DIR" ]; then
    rm -rf "$PLUGIN_DIR"
    echo "✅ Removed $PLUGIN_DIR"
else
    echo "⚠️  Plugin not found at $PLUGIN_DIR"
fi

# Remove marketplace link
if [ -L "$MARKETPLACE_LINK" ]; then
    rm -f "$MARKETPLACE_LINK"
    echo "✅ Removed marketplace link"
fi

echo ""
echo "Craft plugin uninstalled."
echo "To reinstall: brew install data-wise/tap/craft"
