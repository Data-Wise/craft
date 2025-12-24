#!/bin/bash

# Workflow Plugin - Structure Tests
# Tests plugin structure, JSON validity, and file integrity

set -e  # Exit on first error

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PLUGIN_DIR"

echo "🧪 Testing Workflow Plugin Structure..."
echo "Plugin directory: $PLUGIN_DIR"
echo ""

# Test counter
TESTS_RUN=0
TESTS_PASSED=0

# Helper functions
pass() {
    TESTS_RUN=$((TESTS_RUN + 1))
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo "✅ PASS: $1"
}

fail() {
    TESTS_RUN=$((TESTS_RUN + 1))
    echo "❌ FAIL: $1"
    exit 1
}

# Test 1: Check required files exist
echo "Test 1: Required files..."
test -f .claude-plugin/plugin.json || fail "plugin.json missing"
test -f package.json || fail "package.json missing"
test -f README.md || fail "README.md missing"
test -f LICENSE || fail "LICENSE missing"
pass "All required files exist"

# Test 2: Validate JSON files
echo "Test 2: JSON validity..."
if ! jq empty .claude-plugin/plugin.json 2>/dev/null; then
    fail "plugin.json is invalid JSON"
fi
if ! jq empty package.json 2>/dev/null; then
    fail "package.json is invalid JSON"
fi
pass "All JSON files are valid"

# Test 3: Check plugin.json structure
echo "Test 3: plugin.json structure..."
NAME=$(jq -r '.name' .claude-plugin/plugin.json)
VERSION=$(jq -r '.version' .claude-plugin/plugin.json)
DESCRIPTION=$(jq -r '.description' .claude-plugin/plugin.json)

if [ "$NAME" != "workflow" ]; then
    fail "plugin.json name is '$NAME', expected 'workflow'"
fi

if [ -z "$VERSION" ] || [ "$VERSION" = "null" ]; then
    fail "plugin.json version is missing or null"
fi

if [ -z "$DESCRIPTION" ] || [ "$DESCRIPTION" = "null" ]; then
    fail "plugin.json description is missing or null"
fi

pass "plugin.json structure is valid"

# Test 4: Commands structure
echo "Test 4: Commands structure..."
test -d commands || fail "commands/ directory missing"

COMMAND_COUNT=$(find commands/ -name "*.md" -type f | wc -l | tr -d ' ')
EXPECTED_COMMANDS=1  # brainstorm.md

if [ "$COMMAND_COUNT" -ne "$EXPECTED_COMMANDS" ]; then
    fail "Expected $EXPECTED_COMMANDS commands, found $COMMAND_COUNT"
fi

# Check brainstorm command exists
test -f commands/brainstorm.md || fail "commands/brainstorm.md missing"

pass "Commands structure is valid ($COMMAND_COUNT commands)"

# Test 5: Skills structure
echo "Test 5: Skills structure..."
test -d skills || fail "skills/ directory missing"
test -d skills/design || fail "skills/design/ directory missing"

SKILL_COUNT=$(find skills/ -name "*.md" -type f | wc -l | tr -d ' ')
EXPECTED_SKILLS=3  # backend-designer, frontend-designer, devops-helper

if [ "$SKILL_COUNT" -ne "$EXPECTED_SKILLS" ]; then
    fail "Expected $EXPECTED_SKILLS skills, found $SKILL_COUNT"
fi

# Check individual skills exist
test -f skills/design/backend-designer.md || fail "backend-designer skill missing"
test -f skills/design/frontend-designer.md || fail "frontend-designer skill missing"
test -f skills/design/devops-helper.md || fail "devops-helper skill missing"

pass "Skills structure is valid ($SKILL_COUNT skills)"

# Test 6: Agents structure
echo "Test 6: Agents structure..."
test -d agents || fail "agents/ directory missing"

AGENT_COUNT=$(find agents/ -name "*.md" -type f | wc -l | tr -d ' ')
EXPECTED_AGENTS=1  # orchestrator.md

if [ "$AGENT_COUNT" -ne "$EXPECTED_AGENTS" ]; then
    fail "Expected $EXPECTED_AGENTS agent, found $AGENT_COUNT"
fi

# Check orchestrator agent exists
test -f agents/orchestrator.md || fail "agents/orchestrator.md missing"

pass "Agents structure is valid ($AGENT_COUNT agent)"

# Test 7: Documentation structure
echo "Test 7: Documentation structure..."
test -d docs || fail "docs/ directory missing"
test -f docs/README.md || fail "docs/README.md missing"
test -f docs/QUICK-START.md || fail "docs/QUICK-START.md missing"
test -f docs/REFCARD.md || fail "docs/REFCARD.md missing"

pass "Documentation structure is valid"

# Test 8: Skill frontmatter validation
echo "Test 8: Skill frontmatter..."

for skill_file in skills/design/*.md; do
    if ! head -n 20 "$skill_file" | grep -q "^name:"; then
        fail "Skill $(basename $skill_file) missing 'name:' in frontmatter"
    fi
    if ! head -n 20 "$skill_file" | grep -q "^description:"; then
        fail "Skill $(basename $skill_file) missing 'description:' in frontmatter"
    fi
    if ! head -n 20 "$skill_file" | grep -q "^triggers:"; then
        fail "Skill $(basename $skill_file) missing 'triggers:' in frontmatter"
    fi
done

pass "All skills have valid frontmatter"

# Test 9: Command frontmatter validation
echo "Test 9: Command frontmatter..."

if ! head -n 20 commands/brainstorm.md | grep -q "^name:"; then
    fail "brainstorm command missing 'name:' in frontmatter"
fi

if ! head -n 20 commands/brainstorm.md | grep -q "^description:"; then
    fail "brainstorm command missing 'description:' in frontmatter"
fi

pass "brainstorm command has valid frontmatter"

# Test 10: Agent frontmatter validation
echo "Test 10: Agent frontmatter..."

if ! head -n 20 agents/orchestrator.md | grep -q "^name:"; then
    fail "orchestrator agent missing 'name:' in frontmatter"
fi

if ! head -n 20 agents/orchestrator.md | grep -q "^description:"; then
    fail "orchestrator agent missing 'description:' in frontmatter"
fi

if ! head -n 20 agents/orchestrator.md | grep -q "^tools:"; then
    fail "orchestrator agent missing 'tools:' in frontmatter"
fi

pass "orchestrator agent has valid frontmatter"

# Test 11: No hardcoded paths
echo "Test 11: No hardcoded paths..."

# Check for /Users/dt or similar absolute paths (exclude tests, docs, comments)
if grep -r "/Users/dt" --include="*.md" commands/ skills/ agents/ 2>/dev/null | grep -v "^#" | grep -v "Example:" > /dev/null; then
    fail "Found hardcoded /Users/dt paths in plugin files"
fi

pass "No hardcoded paths found"

# Test 12: Repository URL correctness
echo "Test 12: Repository URL..."

REPO_URL=$(jq -r '.repository.url' .claude-plugin/plugin.json)
EXPECTED_REPO="https://github.com/Data-Wise/claude-plugins.git"

if [ "$REPO_URL" != "$EXPECTED_REPO" ]; then
    fail "plugin.json repository URL is '$REPO_URL', expected '$EXPECTED_REPO'"
fi

PACKAGE_REPO=$(jq -r '.repository.url' package.json)
if [ "$PACKAGE_REPO" != "$EXPECTED_REPO" ]; then
    fail "package.json repository URL is '$PACKAGE_REPO', expected '$EXPECTED_REPO'"
fi

pass "Repository URLs are correct"

# Test 13: README quality checks
echo "Test 13: README quality..."

if ! grep -q "## Installation" README.md; then
    fail "README.md missing Installation section"
fi

if ! grep -q "## Features" README.md; then
    fail "README.md missing Features section"
fi

if ! grep -q "MIT" README.md; then
    fail "README.md missing license information"
fi

pass "README.md has required sections"

# Test 14: Skill trigger keywords validation
echo "Test 14: Skill trigger keywords..."

# backend-designer should have API/database/auth triggers
if ! grep -A 10 "^triggers:" skills/design/backend-designer.md | grep -q "API design"; then
    fail "backend-designer missing 'API design' trigger"
fi

# frontend-designer should have UI/UX triggers
if ! grep -A 10 "^triggers:" skills/design/frontend-designer.md | grep -q "UI design"; then
    fail "frontend-designer missing 'UI design' trigger"
fi

# devops-helper should have CI/CD/deployment triggers
if ! grep -A 10 "^triggers:" skills/design/devops-helper.md | grep -q "CI/CD"; then
    fail "devops-helper missing 'CI/CD' trigger"
fi

pass "All skills have appropriate trigger keywords"

# Test 15: Documentation cross-references
echo "Test 15: Documentation cross-references..."

# Check QUICK-START references REFCARD
if ! grep -q "REFCARD.md" docs/QUICK-START.md; then
    fail "QUICK-START.md doesn't reference REFCARD.md"
fi

# Check docs/README references both guides
if ! grep -q "QUICK-START.md" docs/README.md; then
    fail "docs/README.md doesn't reference QUICK-START.md"
fi

if ! grep -q "REFCARD.md" docs/README.md; then
    fail "docs/README.md doesn't reference REFCARD.md"
fi

pass "Documentation cross-references are valid"

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Test Results:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Tests run: $TESTS_RUN"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $((TESTS_RUN - TESTS_PASSED))"
echo ""

if [ "$TESTS_RUN" -eq "$TESTS_PASSED" ]; then
    echo "✅ All tests passed!"
    echo ""
    echo "Plugin structure validated:"
    echo "  • $COMMAND_COUNT command (brainstorm)"
    echo "  • $SKILL_COUNT skills (backend, frontend, devops)"
    echo "  • $AGENT_COUNT agent (orchestrator)"
    echo "  • JSON files valid"
    echo "  • Documentation complete"
    echo "  • No hardcoded paths"
    echo ""
    exit 0
else
    echo "❌ Some tests failed"
    exit 1
fi
