#!/bin/bash
#
# Wave 1 Implementation Test Suite
#

set -e

echo "🧪 Testing Wave 1 Implementations..."
echo ""

# Test 1: Hook script exists and is executable
echo "Test 1: Hook script setup..."
if [ -x ".claude-plugin/hooks/orchestrate-hooks.sh" ]; then
    echo "✅ Hook script is executable"
else
    echo "❌ Hook script not executable"
    exit 1
fi

# Test 2: Validation skills exist
echo ""
echo "Test 2: Validation skills..."
VALIDATORS=(
    ".claude-plugin/skills/validation/test-coverage.md"
    ".claude-plugin/skills/validation/broken-links.md"
    ".claude-plugin/skills/validation/lint-check.md"
)

for validator in "${VALIDATORS[@]}"; do
    if [ -f "$validator" ]; then
        echo "✅ Found: $validator"
    else
        echo "❌ Missing: $validator"
        exit 1
    fi
done

# Test 3: Complexity scoring in do.md
echo ""
echo "Test 3: Complexity scoring documentation..."
if grep -q "Complexity Analysis (NEW in v1.23.0)" commands/do.md; then
    echo "✅ Complexity analysis section added"
else
    echo "❌ Complexity analysis section missing"
    exit 1
fi

if grep -q "Routing Decision Flow" commands/do.md; then
    echo "✅ Routing decision flow documented"
else
    echo "❌ Routing decision flow missing"
    exit 1
fi

# Test 4: Hook execution (PreToolUse)
echo ""
echo "Test 4: PreToolUse hook execution..."
HOOK_EVENT=PreToolUse TOOL_NAME=test-agent CRAFT_MODE=default \
    bash .claude-plugin/hooks/orchestrate-hooks.sh

if [ -f ".craft/logs/orchestration.log" ]; then
    echo "✅ Log file created"
    if grep -q "Starting agent: test-agent" .craft/logs/orchestration.log; then
        echo "✅ Agent start logged"
    else
        echo "❌ Agent start not logged"
        exit 1
    fi
else
    echo "❌ Log file not created"
    exit 1
fi

if [ -f ".craft/cache/agent-test-agent.status" ]; then
    echo "✅ Agent status file created"
else
    echo "❌ Agent status file not created"
    exit 1
fi

# Test 5: Hook execution (PostToolUse)
echo ""
echo "Test 5: PostToolUse hook execution..."
HOOK_EVENT=PostToolUse TOOL_NAME=test-agent DURATION=42 \
    bash .claude-plugin/hooks/orchestrate-hooks.sh

if grep -q "Completed agent: test-agent" .craft/logs/orchestration.log; then
    echo "✅ Agent completion logged"
else
    echo "❌ Agent completion not logged"
    exit 1
fi

if grep -q "test-agent:success" .craft/cache/agent-results.cache; then
    echo "✅ Result cached"
else
    echo "❌ Result not cached"
    exit 1
fi

# Test 6: Hook execution (Stop)
echo ""
echo "Test 6: Stop hook execution..."
HOOK_EVENT=Stop AGENT_COUNT=1 \
    bash .claude-plugin/hooks/orchestrate-hooks.sh

if [ -f ".craft/cache/last-orchestration.json" ]; then
    echo "✅ Session file created"

    if command -v jq &> /dev/null; then
        TOTAL_AGENTS=$(jq -r '.total_agents' .craft/cache/last-orchestration.json)
        if [ "$TOTAL_AGENTS" == "1" ]; then
            echo "✅ Session summary correct"
        else
            echo "❌ Session summary incorrect (expected 1 agent, got $TOTAL_AGENTS)"
            exit 1
        fi
    else
        echo "⚠️  jq not installed, skipping JSON validation"
    fi
else
    echo "❌ Session file not created"
    exit 1
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ALL TESTS PASSED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Wave 1 Implementation: VERIFIED ✓"
echo ""
echo "Files created:"
echo "  - 1 modified: commands/do.md"
echo "  - 3 validators: .claude-plugin/skills/validation/"
echo "  - 2 hooks: .claude-plugin/hooks/"
echo "  - 1 summary: WAVE1-IMPLEMENTATION-SUMMARY.md"
echo ""
echo "Artifacts generated:"
echo "  - .craft/logs/orchestration.log"
echo "  - .craft/cache/agent-*.status"
echo "  - .craft/cache/agent-results.cache"
echo "  - .craft/cache/last-orchestration.json"
echo ""
