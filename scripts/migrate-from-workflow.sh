#!/bin/bash
# Migration script for users upgrading from standalone workflow plugin to craft v1.17.0
# This script safely migrates from workflow plugin to craft with integrated workflow features

set -e

WORKFLOW_DIR="${HOME}/.claude/plugins/workflow"
CRAFT_DIR="${HOME}/.claude/plugins/craft"
BACKUP_DIR="${HOME}/.claude/plugins/.backup-workflow-$(date +%Y%m%d-%H%M%S)"

# Source formatting library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/formatting.sh"

box_header "Workflow → Craft Migration Tool"
box_empty_row
box_row "  This script will:"
box_row "  1. Backup your existing workflow plugin"
box_row "  2. Check if craft v1.17.0+ is installed"
box_row "  3. Remove the old workflow plugin"
box_row "  4. Confirm workflow commands work in craft"
box_empty_row
box_footer
echo ""

# Check if workflow plugin is installed
if [ ! -d "${WORKFLOW_DIR}" ]; then
    echo "✅ Workflow plugin not found - no migration needed"
    echo ""
    echo "If you want to use workflow features:"
    echo "  Install craft v1.17.0+ which includes all workflow commands"
    exit 0
fi

echo "📍 Found workflow plugin at: ${WORKFLOW_DIR}"
echo ""

# Check if craft is installed
if [ ! -d "${CRAFT_DIR}" ]; then
    echo "❌ Craft plugin not found"
    echo ""
    echo "Please install craft v1.17.0+ first:"
    echo "  curl -fsSL https://raw.githubusercontent.com/Data-Wise/claude-plugins/main/craft/install.sh | bash"
    echo ""
    exit 1
fi

# Check craft version
if [ -f "${CRAFT_DIR}/.claude-plugin/plugin.json" ]; then
    CRAFT_VERSION=$(grep '"version"' "${CRAFT_DIR}/.claude-plugin/plugin.json" | sed 's/.*"\([0-9.]*\)".*/\1/')
    echo "📦 Found craft version: ${CRAFT_VERSION}"

    # Version comparison (requires v1.17.0+)
    MAJOR=$(echo ${CRAFT_VERSION} | cut -d. -f1)
    MINOR=$(echo ${CRAFT_VERSION} | cut -d. -f2)

    if [ "${MAJOR}" -lt 1 ] || ([ "${MAJOR}" -eq 1 ] && [ "${MINOR}" -lt 17 ]); then
        echo "❌ Craft version ${CRAFT_VERSION} is too old"
        echo ""
        echo "Please update craft to v1.17.0+ first:"
        echo "  cd ~/projects/dev-tools/claude-plugins/craft"
        echo "  ./install.sh"
        echo ""
        exit 1
    fi
else
    echo "⚠️  Could not detect craft version"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
box_header "Migration Plan"
box_empty_row
box_row "  Source: ${WORKFLOW_DIR}"
box_row "  Backup: ${BACKUP_DIR}"
box_row "  Target: craft v${CRAFT_VERSION}"
box_empty_row
box_row "  Workflow commands will work identically in craft:"
box_row "  • /brainstorm, /spec-review, /focus, /next, /done"
box_row "  • /recap, /stuck, /refine, /task-*"
box_row "  • /adhd-guide"
box_empty_row
box_footer
echo ""

read -p "Proceed with migration? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Migration cancelled"
    exit 0
fi

echo ""
echo "🔄 Starting migration..."
echo ""

# Step 1: Create backup
echo "📦 Creating backup..."
mkdir -p "${BACKUP_DIR}"
cp -r "${WORKFLOW_DIR}" "${BACKUP_DIR}/"
echo "   ✅ Backup created: ${BACKUP_DIR}/workflow"

# Step 2: Remove workflow plugin
echo "🗑️  Removing workflow plugin..."
rm -rf "${WORKFLOW_DIR}"
echo "   ✅ Workflow plugin removed"

# Step 3: Verify craft has workflow commands
echo "✅ Verifying craft includes workflow commands..."
WORKFLOW_CMD_COUNT=$(find "${CRAFT_DIR}/commands/workflow" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')

if [ "${WORKFLOW_CMD_COUNT}" -lt 12 ]; then
    echo "   ⚠️  Warning: Expected 12 workflow commands, found ${WORKFLOW_CMD_COUNT}"
    echo ""
    echo "Restoring backup..."
    cp -r "${BACKUP_DIR}/workflow" "${HOME}/.claude/plugins/"
    echo "❌ Migration failed - backup restored"
    exit 1
fi

echo "   ✅ Found ${WORKFLOW_CMD_COUNT} workflow commands in craft"

echo ""
box_header "✅ MIGRATION COMPLETE"
box_empty_row
box_row "  Workflow plugin has been replaced with craft v${CRAFT_VERSION}"
box_empty_row
box_row "  All workflow commands now work through craft:"
box_row "  • /brainstorm [depth] [focus] [action]"
box_row "  • /spec-review <file>"
box_row "  • /focus [task]"
box_row "  • /next, /done, /recap, /stuck"
box_row "  • /task-status, /task-output, /task-cancel"
box_row "  • /adhd-guide"
box_empty_row
box_row "  📚 Documentation:"
box_row "  https://data-wise.github.io/claude-plugins/craft/"
box_empty_row
box_row "  🗂️  Backup Location:"
box_row "  ${BACKUP_DIR}"
box_empty_row
box_row "  🚀 Next Steps:"
box_row "  • Restart Claude Code to load updated plugin"
box_row "  • Try: /brainstorm or /craft:do"
box_row "  • Help: /craft:help"
box_empty_row
box_footer
echo ""
