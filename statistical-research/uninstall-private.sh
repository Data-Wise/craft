#!/bin/bash
# Private uninstallation script for statistical-research plugin

set -e

PLUGIN_NAME="statistical-research"
TARGET_DIR="$HOME/.claude/plugins/$PLUGIN_NAME"

echo "🔬 Uninstalling Statistical Research Plugin"
echo ""

# Check if installed
if [ ! -L "$TARGET_DIR" ] && [ ! -d "$TARGET_DIR" ]; then
    echo "⚠️  Plugin not found at: $TARGET_DIR"
    echo "Nothing to uninstall."
    exit 0
fi

# Check if symlink or directory
if [ -L "$TARGET_DIR" ]; then
    echo "Removing symlink..."
    rm "$TARGET_DIR"
    echo "✅ Symlink removed (development mode installation)"
elif [ -d "$TARGET_DIR" ]; then
    echo "Removing directory..."
    rm -rf "$TARGET_DIR"
    echo "✅ Directory removed (production mode installation)"
fi

echo ""
echo "🎉 Statistical Research Plugin uninstalled successfully!"
echo ""
echo "To reinstall:"
echo "  cd ~/projects/dev-tools/claude-plugins/statistical-research"
echo "  ./install-private.sh"
