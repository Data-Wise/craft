#!/bin/bash
# Craft Plugin Installer for Claude Code
# Quick install: curl -fsSL https://raw.githubusercontent.com/Data-Wise/claude-plugins/main/craft/install.sh | bash

set -e

PLUGIN_NAME="craft"
PLUGIN_DIR="${HOME}/.claude/plugins/${PLUGIN_NAME}"
REPO_URL="https://github.com/Data-Wise/claude-plugins.git"
TEMP_DIR=$(mktemp -d)

# Source formatting library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/scripts/formatting.sh"

box_header "Craft Plugin Installer for Claude Code"
box_empty_row
box_row "  📦 Installing: craft v1.17.0 (with workflow)"
box_row "  📍 Location: ~/.claude/plugins/craft"
box_empty_row
box_footer
echo ""

# Check if Claude Code is installed
if ! command -v claude &> /dev/null; then
    echo "⚠️  Claude Code CLI not found."
    echo ""
    echo "Please install Claude Code first:"
    echo "  https://claude.com/claude-code"
    echo ""
    exit 1
fi

# Create plugins directory if it doesn't exist
mkdir -p "${HOME}/.claude/plugins"

# Check if plugin already installed
if [ -d "${PLUGIN_DIR}" ]; then
    echo "📌 Craft plugin already installed at: ${PLUGIN_DIR}"
    echo ""
    read -p "Do you want to reinstall (update)? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "✅ Keeping existing installation"
        exit 0
    fi
    echo "🔄 Removing existing installation..."
    rm -rf "${PLUGIN_DIR}"
fi

# Clone the repository
echo "📥 Cloning craft plugin..."
git clone --depth 1 --filter=blob:none --sparse "${REPO_URL}" "${TEMP_DIR}" > /dev/null 2>&1
cd "${TEMP_DIR}"
git sparse-checkout set craft > /dev/null 2>&1

# Copy to plugins directory
echo "📦 Installing to ~/.claude/plugins/craft..."
cp -r "${TEMP_DIR}/craft" "${PLUGIN_DIR}"

# Cleanup
rm -rf "${TEMP_DIR}"

# Verify installation
if [ -f "${PLUGIN_DIR}/.claude-plugin/plugin.json" ]; then
    VERSION=$(grep '"version"' "${PLUGIN_DIR}/.claude-plugin/plugin.json" | sed 's/.*"\([0-9.]*\)".*/\1/')

    echo ""
    box_header "✅ INSTALLATION COMPLETE"
    box_empty_row
    box_row "  Plugin: craft v${VERSION}"
    box_row "  Location: ~/.claude/plugins/craft"
    box_empty_row
    box_row "  📚 Documentation:"
    box_row "  https://data-wise.github.io/claude-plugins/craft/"
    box_empty_row
    box_row "  🚀 Quick Start:"
    box_row "  • Restart Claude Code to load the plugin"
    box_row "  • Try: /craft:do <task> or /brainstorm"
    box_row "  • Help: /craft:help"
    box_row "  • Hub: /craft:hub"
    box_empty_row
    box_row "  108 commands | 8 agents | 25 skills"
    box_empty_row
    box_footer
    echo ""
else
    echo "❌ Installation verification failed"
    exit 1
fi
