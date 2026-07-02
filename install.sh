#!/bin/bash
# Craft Plugin Installer for Claude Code
# Quick install: curl -fsSL https://raw.githubusercontent.com/Data-Wise/craft/main/install.sh | bash
#
# Installs the CURRENT craft plugin by cloning Data-Wise/craft directly.
# (Previously cloned a frozen mirror in Data-Wise/claude-plugins that was
# permanently stuck at v1.16.0 — see docs/specs/SPEC-dist-surface-hardening-2026-07-01.md D1.)

set -e

PLUGIN_NAME="craft"
PLUGIN_DIR="${HOME}/.claude/plugins/${PLUGIN_NAME}"
REPO_URL="https://github.com/Data-Wise/craft.git"

# --- Formatting: source the repo library when available, else inline fallback.
# Under `curl | bash` there is no script file on disk, so BASH_SOURCE-relative
# sourcing fails — the fallback keeps the installer runnable when piped.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-.}")" 2>/dev/null && pwd || echo ".")"
if [ -f "${SCRIPT_DIR}/scripts/formatting.sh" ]; then
    # shellcheck source=scripts/formatting.sh
    source "${SCRIPT_DIR}/scripts/formatting.sh"
else
    box_header() { echo "==== $1 ===="; }
    box_row()    { echo "$1"; }
    box_empty_row() { echo ""; }
    box_footer() { echo "============"; }
fi

box_header "Craft Plugin Installer for Claude Code"
box_empty_row
box_row "  📦 Installing: craft (latest from main)"
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

# Check if plugin already installed.
# Under `curl | bash` stdin is the script stream, so `read` must come from the
# terminal; without a TTY (CI), default to reinstall — running the installer
# again IS the update intent.
if [ -d "${PLUGIN_DIR}" ]; then
    echo "📌 Craft plugin already installed at: ${PLUGIN_DIR}"
    echo ""
    REPLY="y"
    if [ -t 0 ]; then
        read -p "Do you want to reinstall (update)? (y/N): " -n 1 -r || REPLY="y"
        echo ""
    elif [ -r /dev/tty ] && read -p "Do you want to reinstall (update)? (y/N): " -n 1 -r < /dev/tty; then
        echo ""
    else
        # No usable terminal (CI, curl|bash without tty) — running the
        # installer again IS the update intent.
        REPLY="y"
        echo "🔄 Non-interactive session — updating existing installation."
    fi
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "✅ Keeping existing installation"
        exit 0
    fi
    echo "🔄 Removing existing installation..."
    rm -rf "${PLUGIN_DIR}"
fi

# Clone the craft repository (current main, shallow) straight into place.
# git writes symlinks as symlinks — `cp -r` follows them and dies on the
# intentionally-broken governance test fixtures (macOS BSD cp).
echo "📥 Installing craft plugin (current main)..."
git clone --depth 1 "${REPO_URL}" "${PLUGIN_DIR}" > /dev/null 2>&1
rm -rf "${PLUGIN_DIR}/.git"

# Verify installation
if [ -f "${PLUGIN_DIR}/.claude-plugin/plugin.json" ]; then
    VERSION=$(grep '"version"' "${PLUGIN_DIR}/.claude-plugin/plugin.json" | sed 's/.*"\([0-9.]*\)".*/\1/')

    # Live counts from the installed tree — never hardcode (drift-prone).
    # Skills count uses the canonical SKILL.md marker, not *.md.
    CMD_COUNT=$(find "${PLUGIN_DIR}/commands" -name "*.md" ! -name "index.md" ! -name "README.md" 2>/dev/null | wc -l | tr -d ' ')
    AGENT_COUNT=$(find "${PLUGIN_DIR}/agents" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    SKILL_COUNT=$(find "${PLUGIN_DIR}/skills" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')

    echo ""
    box_header "✅ INSTALLATION COMPLETE"
    box_empty_row
    box_row "  Plugin: craft v${VERSION}"
    box_row "  Location: ~/.claude/plugins/craft"
    box_empty_row
    box_row "  📚 Documentation:"
    box_row "  https://data-wise.github.io/craft/"
    box_empty_row
    box_row "  🚀 Quick Start:"
    box_row "  • Restart Claude Code to load the plugin"
    box_row "  • Try: /craft:do <task> or /brainstorm"
    box_row "  • Help: /craft:help"
    box_row "  • Hub: /craft:hub"
    box_empty_row
    box_row "  ${CMD_COUNT} commands | ${AGENT_COUNT} agents | ${SKILL_COUNT} skills"
    box_empty_row
    box_footer
    echo ""
else
    echo "❌ Installation verification failed"
    exit 1
fi
