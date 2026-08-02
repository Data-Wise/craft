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
# Parallel arrays instead of `declare -A` (bash 4.0+): the shebang is
# /bin/bash, which on macOS is bash 3.2, where the associative-array
# declaration failed outright ("bad array subscript") and `set -e` aborted the
# script before a single command was listed. Names are now walked in the order
# below rather than bash 4's unspecified hash order.
COMMAND_NAMES=(
    "teaching-workflow"
    "workflow-01"
    "workflow-02"
    "workflow-03"
    "workflow-04"
    "workflow-05"
    "workflow-06"
    "workflow-07"
    "workflow-08"
    "workflow-09"
    "workflow-10"
)
COMMAND_LISTS=(
    "/craft:site:build|/craft:site:progress|/craft:site:publish --dry-run|/craft:site:publish"
    "/craft:docs:update"
    "/craft:site:build --preset adhd-focus --quick"
    "/craft:check --for release"
    "/craft:do add user authentication with JWT"
    "/craft:test:run debug"
    "/craft:code:lint optimize"
    "ask Claude to create a worktree (dev/git skill): feature-auth"
    "/craft:dist:homebrew setup"
    "/craft:check --for commit"
    "/craft:orchestrate 'prepare v2.0 release' release"
)

echo "Commands to capture:"
echo "==================="
for (( i=0; i<${#COMMAND_NAMES[@]}; i++ )); do
    echo ""
    echo "📌 ${COMMAND_NAMES[$i]}"
    IFS='|' read -ra CMDS <<< "${COMMAND_LISTS[$i]}"
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
