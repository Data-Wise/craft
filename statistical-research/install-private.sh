#!/bin/bash
# Private installation script for statistical-research plugin
# For personal use only - not published to package managers

set -e

PLUGIN_NAME="statistical-research"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$HOME/.claude/plugins/$PLUGIN_NAME"

echo "🔬 Installing Statistical Research Plugin (Private)"
echo ""

# Parse flags
DEV_MODE=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            DEV_MODE=true
            shift
            ;;
        --force|-f)
            FORCE=true
            shift
            ;;
        --help|-h)
            echo "Usage: ./install-private.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dev         Install in development mode (symlink)"
            echo "  --force, -f   Force reinstall (remove existing)"
            echo "  --help, -h    Show this help message"
            echo ""
            echo "Development mode creates a symlink to this directory,"
            echo "allowing you to edit files without reinstalling."
            echo ""
            echo "Production mode copies files to ~/.claude/plugins/"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if already installed
if [ -L "$TARGET_DIR" ] || [ -d "$TARGET_DIR" ]; then
    if [ "$FORCE" = false ]; then
        echo "⚠️  Plugin already installed at: $TARGET_DIR"
        echo ""
        read -p "Reinstall? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Installation cancelled."
            exit 0
        fi
    fi

    # Remove existing installation
    echo "Removing existing installation..."
    rm -rf "$TARGET_DIR"
fi

# Create plugins directory if needed
mkdir -p "$HOME/.claude/plugins"

# Install
if [ "$DEV_MODE" = true ]; then
    echo "📝 Installing in DEVELOPMENT mode (symlink)..."
    ln -s "$SCRIPT_DIR" "$TARGET_DIR"
    echo "✅ Symlink created: $TARGET_DIR -> $SCRIPT_DIR"
    echo ""
    echo "ℹ️  Changes to files in $SCRIPT_DIR will be immediately reflected"
else
    echo "📦 Installing in PRODUCTION mode (copy)..."
    cp -r "$SCRIPT_DIR" "$TARGET_DIR"
    echo "✅ Files copied to: $TARGET_DIR"
fi

echo ""
echo "🎉 Statistical Research Plugin installed successfully!"
echo ""
echo "Available slash commands:"
echo "  Literature:"
echo "    /lit:arxiv     - Search arXiv papers"
echo "    /lit:doi       - Lookup paper by DOI"
echo "    /lit:bib-add   - Add citation to BibTeX"
echo "    /lit:bib-search - Search BibTeX library"
echo ""
echo "  Manuscript:"
echo "    /ms:methods    - Write methods section"
echo "    /ms:results    - Write results section"
echo "    /ms:proof      - Write mathematical proof"
echo "    /ms:reviewer   - Respond to reviewers"
echo ""
echo "  Simulation:"
echo "    /sim:design    - Design simulation study"
echo "    /sim:analysis  - Analyze simulation results"
echo ""
echo "  Research:"
echo "    /research:hypothesis    - Formulate hypotheses"
echo "    /research:analysis-plan - Create analysis plan"
echo "    /research:lit-gap       - Find literature gaps"
echo ""
echo "Plus 17 A-grade auto-activating skills!"
echo ""

if [ "$DEV_MODE" = true ]; then
    echo "📝 Development mode: Edit files in:"
    echo "   $SCRIPT_DIR"
    echo ""
    echo "   Changes take effect immediately (no reinstall needed)"
else
    echo "To update, run: ./install-private.sh --force"
fi

echo ""
echo "To uninstall: rm -rf $TARGET_DIR"
