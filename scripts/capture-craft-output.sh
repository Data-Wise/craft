#!/bin/bash
# Craft Command Output Capture Script
# Runs /craft commands in Claude Code and captures real output for VHS tapes

set -e

echo "🎯 Craft Command Output Capture"
echo "================================"
echo ""
echo "This script helps capture real /craft command output for VHS tape generation."
echo ""
echo "⚠️  NOTE: This script provides the FRAMEWORK."
echo "    Actual command execution must be done IN Claude Code using the Skill tool."
echo ""

# Output directory for captured results
OUTPUT_DIR="docs/demos/captured-output"
mkdir -p "$OUTPUT_DIR"

echo "Output directory: $OUTPUT_DIR"
echo ""

# Commands to capture
declare -A COMMANDS=(
    ["teaching-workflow"]="/craft:git:status|/craft:site:build|/craft:site:progress|/craft:site:publish --dry-run|/craft:site:publish"
    ["workflow-01"]="/craft:docs:update"
    ["workflow-02"]="/craft:site:create --preset adhd-focus --quick"
    ["workflow-03"]="/craft:check --for release"
    ["workflow-04"]="/craft:do add user authentication with JWT"
    ["workflow-05"]="/craft:test:run debug"
    ["workflow-06"]="/craft:code:lint optimize"
    ["workflow-07"]="/craft:git:worktree add feature-auth"
    ["workflow-08"]="/craft:dist:homebrew setup"
    ["workflow-09"]="/craft:check --for commit"
    ["workflow-10"]="/craft:orchestrate 'prepare v2.0 release' release"
)

echo "Commands to capture:"
echo "==================="
for name in "${!COMMANDS[@]}"; do
    echo ""
    echo "📌 $name"
    IFS='|' read -ra CMDS <<< "${COMMANDS[$name]}"
    for cmd in "${CMDS[@]}"; do
        echo "   - $cmd"
    done
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. In Claude Code, run each command listed above"
echo "2. Copy the output (including formatting, boxes, icons)"
echo "3. Save to: $OUTPUT_DIR/<name>-output.txt"
echo ""
echo "Example:"
echo "  /craft:site:build"
echo "  # Copy output → save to: $OUTPUT_DIR/workflow-01-output.txt"
echo ""
echo "Then run: ./scripts/update-vhs-tapes.sh"
echo ""
