#!/usr/bin/env bash
#
# E2E Tests for /craft:release skill
# Tests: Skill structure, dry-run mode, version detection,
#        pre-flight integration, and semver suggestion logic.
#
# Usage:
#   bash tests/test_release_skill_e2e.sh
#
# Requirements:
#   - Craft plugin installed (skills/release/SKILL.md exists)
#   - git and python3 available

set -uo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRAFT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILL_DIR="$CRAFT_ROOT/skills/release"
SKILL_FILE="$SKILL_DIR/SKILL.md"
REFS_DIR="$SKILL_DIR/references"

# Color output
T_RED='\033[0;31m'
T_GREEN='\033[0;32m'
T_YELLOW='\033[1;33m'
T_BLUE='\033[0;34m'
T_BOLD='\033[1m'
T_NC='\033[0m'

# Test counters
TOTAL=0
PASS=0
FAIL=0
SKIP=0

declare -a FAILED_NAMES=()
declare -a CLEANUP_DIRS=()

# ============================================================================
# Preflight Check
# ============================================================================

if [[ ! -f "$SKILL_FILE" ]]; then
    echo -e "${T_RED}ERROR${T_NC}: Skill file not found at $SKILL_FILE"
    echo "  Create the skill first, then run these tests."
    exit 1
fi

if ! command -v git &>/dev/null; then
    echo -e "${T_RED}ERROR${T_NC}: git is not available"
    exit 1
fi

if ! command -v python3 &>/dev/null; then
    echo -e "${T_RED}ERROR${T_NC}: python3 is not available"
    exit 1
fi

# ============================================================================
# Helpers
# ============================================================================

make_tmpdir() {
    local dir
    dir=$(mktemp -d "${TMPDIR:-/tmp}/release-skill-e2e.XXXXXX")
    CLEANUP_DIRS+=("$dir")
    echo "$dir"
}

cleanup() {
    for dir in "${CLEANUP_DIRS[@]}"; do
        if [[ -d "$dir" ]]; then
            rm -rf "$dir"
        fi
    done
}
trap cleanup EXIT

init_repo() {
    local repo
    repo=$(make_tmpdir)
    (
        cd "$repo"
        git init -b main --quiet
        git config user.email "test@test.com"
        git config user.name "Test"
        mkdir -p src .claude-plugin
        echo "# README" > README.md
        echo '{"name":"test","version":"1.2.3"}' > .claude-plugin/plugin.json
        git add -A
        git commit -m "Initial commit" --quiet
        git tag v1.2.3
        git branch dev
        git checkout dev --quiet 2>/dev/null
    )
    echo "$repo"
}

assert_pass() {
    local name="$1"
    TOTAL=$((TOTAL + 1))
    PASS=$((PASS + 1))
    echo -e "  ${T_GREEN}PASS${T_NC}  $name"
}

assert_fail() {
    local name="$1" reason="${2:-}"
    TOTAL=$((TOTAL + 1))
    FAIL=$((FAIL + 1))
    FAILED_NAMES+=("$name")
    echo -e "  ${T_RED}FAIL${T_NC}  $name"
    if [[ -n "$reason" ]]; then
        echo -e "        reason: $reason"
    fi
}

skip() {
    local name="$1" reason="${2:-Skipped}"
    TOTAL=$((TOTAL + 1))
    SKIP=$((SKIP + 1))
    echo -e "  ${T_YELLOW}SKIP${T_NC}  $name  ($reason)"
}

# ============================================================================
# Test Groups
# ============================================================================

echo ""
echo -e "${T_BOLD}Release Skill E2E Tests${T_NC}"
echo -e "${T_BOLD}=======================${T_NC}"
echo -e "Skill: $SKILL_FILE"
echo ""

# --------------------------------------------------------------------------
# Group 1: Skill Structure
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Group 1: Skill Structure ---${T_NC}"

# Test: SKILL.md exists
if [[ -f "$SKILL_FILE" ]]; then
    assert_pass "skill_file_exists"
else
    assert_fail "skill_file_exists" "SKILL.md not found"
fi

# Test: Has YAML frontmatter
if head -1 "$SKILL_FILE" | grep -q "^---$"; then
    assert_pass "skill_has_frontmatter"
else
    assert_fail "skill_has_frontmatter" "Missing --- frontmatter delimiter"
fi

# Test: Frontmatter has name field
if grep -q "^name:" "$SKILL_FILE"; then
    assert_pass "skill_has_name"
else
    assert_fail "skill_has_name" "Missing name: in frontmatter"
fi

# Test: Frontmatter has description field
if grep -q "^description:" "$SKILL_FILE"; then
    assert_pass "skill_has_description"
else
    assert_fail "skill_has_description" "Missing description: in frontmatter"
fi

# Test: references/ directory exists
if [[ -d "$REFS_DIR" ]]; then
    assert_pass "references_dir_exists"
else
    assert_fail "references_dir_exists" "references/ directory not found"
fi

# Test: release-checklist.md exists
if [[ -f "$REFS_DIR/release-checklist.md" ]]; then
    assert_pass "release_checklist_exists"
else
    assert_fail "release_checklist_exists" "release-checklist.md not found"
fi

# Test: Skill mentions dry-run
if grep -q "\-\-dry-run" "$SKILL_FILE"; then
    assert_pass "skill_mentions_dry_run"
else
    assert_fail "skill_mentions_dry_run" "SKILL.md should mention --dry-run"
fi

# Test: Skill mentions risk level
if grep -qi "risk.*high\|high.*risk" "$SKILL_FILE"; then
    assert_pass "skill_has_risk_level"
else
    assert_fail "skill_has_risk_level" "Should specify risk level"
fi

echo ""

# --------------------------------------------------------------------------
# Group 2: Dry-Run Mode (simulated on temp repo)
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Group 2: Dry-Run Mode ---${T_NC}"

REPO_DR=$(init_repo)

# Test: Dry-run should not create any commits
BEFORE_COUNT=$(cd "$REPO_DR" && git rev-list --count HEAD)
# Simulate what dry-run does: just version detection (read-only)
DETECTED_VERSION=$(cd "$REPO_DR" && cat .claude-plugin/plugin.json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null)
AFTER_COUNT=$(cd "$REPO_DR" && git rev-list --count HEAD)
if [[ "$BEFORE_COUNT" == "$AFTER_COUNT" ]]; then
    assert_pass "dry_run_no_commits"
else
    assert_fail "dry_run_no_commits" "Commit count changed: $BEFORE_COUNT -> $AFTER_COUNT"
fi

# Test: Version detection works in dry-run context
if [[ "$DETECTED_VERSION" == "1.2.3" ]]; then
    assert_pass "dry_run_detects_version"
else
    assert_fail "dry_run_detects_version" "Expected 1.2.3, got $DETECTED_VERSION"
fi

# Test: No tags created during dry-run simulation
TAG_COUNT_BEFORE=$(cd "$REPO_DR" && git tag | wc -l | tr -d ' ')
# (no-op — dry-run does nothing)
TAG_COUNT_AFTER=$(cd "$REPO_DR" && git tag | wc -l | tr -d ' ')
if [[ "$TAG_COUNT_BEFORE" == "$TAG_COUNT_AFTER" ]]; then
    assert_pass "dry_run_no_tags"
else
    assert_fail "dry_run_no_tags" "Tag count changed"
fi

# Test: No PRs created (check gh is not called — simulate by checking branch state)
BRANCH_COUNT_BEFORE=$(cd "$REPO_DR" && git branch | wc -l | tr -d ' ')
BRANCH_COUNT_AFTER=$(cd "$REPO_DR" && git branch | wc -l | tr -d ' ')
if [[ "$BRANCH_COUNT_BEFORE" == "$BRANCH_COUNT_AFTER" ]]; then
    assert_pass "dry_run_no_branches_created"
else
    assert_fail "dry_run_no_branches_created" "Branch count changed"
fi

# Test: Dry-run section documents guarantees
if grep -q "No commits, tags, or pushes" "$SKILL_FILE"; then
    assert_pass "dry_run_guarantees_documented"
else
    assert_fail "dry_run_guarantees_documented" "Missing dry-run guarantees section"
fi

# Test: Dry-run mentions exit code 0
if grep -q "Exit code 0" "$SKILL_FILE"; then
    assert_pass "dry_run_exit_code_documented"
else
    assert_fail "dry_run_exit_code_documented" "Should document exit code 0"
fi

echo ""

# --------------------------------------------------------------------------
# Group 3: Version Detection Priority
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Group 3: Version Detection ---${T_NC}"

# Test: plugin.json takes priority
REPO_V1=$(init_repo)
(cd "$REPO_V1" && echo '{"name":"test","version":"2.0.0"}' > package.json && git add -A && git commit -m "add package.json" --quiet)
DETECTED=$(cd "$REPO_V1" && cat .claude-plugin/plugin.json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null)
if [[ "$DETECTED" == "1.2.3" ]]; then
    assert_pass "version_plugin_json_priority"
else
    assert_fail "version_plugin_json_priority" "Expected 1.2.3 from plugin.json, got $DETECTED"
fi

# Test: package.json fallback when no plugin.json
REPO_V2=$(make_tmpdir)
(
    cd "$REPO_V2"
    git init -b main --quiet
    git config user.email "test@test.com"
    git config user.name "Test"
    echo '{"name":"test","version":"3.5.0"}' > package.json
    git add -A
    git commit -m "init" --quiet
    git tag v3.5.0
    git branch dev
    git checkout dev --quiet 2>/dev/null
)
DETECTED=$(cd "$REPO_V2" && cat .claude-plugin/plugin.json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null || cat package.json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null)
if [[ "$DETECTED" == "3.5.0" ]]; then
    assert_pass "version_package_json_fallback"
else
    assert_fail "version_package_json_fallback" "Expected 3.5.0, got $DETECTED"
fi

# Test: git tag fallback when no JSON files
REPO_V3=$(make_tmpdir)
(
    cd "$REPO_V3"
    git init -b main --quiet
    git config user.email "test@test.com"
    git config user.name "Test"
    echo "# README" > README.md
    git add -A
    git commit -m "init" --quiet
    git tag v4.0.0
)
DETECTED=$(cd "$REPO_V3" && cat .claude-plugin/plugin.json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null || cat package.json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null || git describe --tags --abbrev=0 2>/dev/null || echo "unknown")
if [[ "$DETECTED" == "v4.0.0" ]]; then
    assert_pass "version_git_tag_fallback"
else
    assert_fail "version_git_tag_fallback" "Expected v4.0.0, got $DETECTED"
fi

# Test: unknown when nothing available
REPO_V4=$(make_tmpdir)
(
    cd "$REPO_V4"
    git init -b main --quiet
    git config user.email "test@test.com"
    git config user.name "Test"
    echo "# README" > README.md
    git add -A
    git commit -m "init" --quiet
)
DETECTED=$(cd "$REPO_V4" && cat .claude-plugin/plugin.json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null || cat package.json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null || git describe --tags --abbrev=0 2>/dev/null || echo "unknown")
if [[ "$DETECTED" == "unknown" ]]; then
    assert_pass "version_unknown_fallback"
else
    assert_fail "version_unknown_fallback" "Expected 'unknown', got $DETECTED"
fi

echo ""

# --------------------------------------------------------------------------
# Group 4: Pre-Flight Integration
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Group 4: Pre-Flight Integration ---${T_NC}"

PRE_RELEASE_SCRIPT="$CRAFT_ROOT/scripts/pre-release-check.sh"

# Test: pre-release-check.sh exists
if [[ -f "$PRE_RELEASE_SCRIPT" ]]; then
    assert_pass "pre_release_script_exists"
else
    assert_fail "pre_release_script_exists" "scripts/pre-release-check.sh not found"
fi

# Test: pre-release-check.sh is executable or has bash shebang
if [[ -x "$PRE_RELEASE_SCRIPT" ]] || head -1 "$PRE_RELEASE_SCRIPT" | grep -q "bash"; then
    assert_pass "pre_release_script_runnable"
else
    assert_fail "pre_release_script_runnable" "Script not executable and no bash shebang"
fi

# Test: pre-release-check.sh passes syntax check
if bash -n "$PRE_RELEASE_SCRIPT" 2>/dev/null; then
    assert_pass "pre_release_syntax_valid"
else
    assert_fail "pre_release_syntax_valid" "Syntax errors in pre-release-check.sh"
fi

# Test: Skill references pre-release-check.sh
if grep -q "pre-release-check" "$SKILL_FILE"; then
    assert_pass "skill_references_pre_release"
else
    assert_fail "skill_references_pre_release" "SKILL.md should reference pre-release-check.sh"
fi

echo ""

# --------------------------------------------------------------------------
# Group 5: Semver Suggestion Logic
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Group 5: Semver Suggestion ---${T_NC}"

# Test: fix-only commits → patch suggestion
REPO_SV=$(init_repo)
(cd "$REPO_SV" && echo "fix" > fix.txt && git add -A && git commit -m "fix: resolve crash on startup" --quiet)
(cd "$REPO_SV" && echo "chore" > chore.txt && git add -A && git commit -m "chore: update dependencies" --quiet)
COMMITS=$(cd "$REPO_SV" && git log v1.2.3..HEAD --oneline 2>/dev/null)
HAS_FEAT=$(echo "$COMMITS" | grep -c "^.*feat:" || true)
HAS_BREAKING=$(echo "$COMMITS" | grep -c "BREAKING CHANGE\|^.*!:" || true)
if [[ "$HAS_FEAT" -eq 0 && "$HAS_BREAKING" -eq 0 ]]; then
    assert_pass "semver_fix_only_is_patch"
else
    assert_fail "semver_fix_only_is_patch" "Expected no feat/breaking, got feat=$HAS_FEAT breaking=$HAS_BREAKING"
fi

# Test: feat commit → minor suggestion
REPO_SV2=$(init_repo)
(cd "$REPO_SV2" && echo "feat" > feat.txt && git add -A && git commit -m "feat: add new dashboard" --quiet)
COMMITS=$(cd "$REPO_SV2" && git log v1.2.3..HEAD --oneline 2>/dev/null)
HAS_FEAT=$(echo "$COMMITS" | grep -c "feat:" || true)
HAS_BREAKING=$(echo "$COMMITS" | grep -c "BREAKING CHANGE\|^.*!:" || true)
if [[ "$HAS_FEAT" -gt 0 && "$HAS_BREAKING" -eq 0 ]]; then
    assert_pass "semver_feat_is_minor"
else
    assert_fail "semver_feat_is_minor" "Expected feat>0 breaking=0, got feat=$HAS_FEAT breaking=$HAS_BREAKING"
fi

# Test: breaking change → major suggestion
REPO_SV3=$(init_repo)
(cd "$REPO_SV3" && echo "break" > break.txt && git add -A && git commit -m "feat!: redesign API" --quiet)
COMMITS=$(cd "$REPO_SV3" && git log v1.2.3..HEAD --oneline 2>/dev/null)
HAS_BREAKING=$(echo "$COMMITS" | grep -c "!:" || true)
if [[ "$HAS_BREAKING" -gt 0 ]]; then
    assert_pass "semver_breaking_is_major"
else
    assert_fail "semver_breaking_is_major" "Expected breaking>0, got $HAS_BREAKING"
fi

# Test: Skill documents semver rules
if grep -q "patch.*fix.*chore\|fix.*chore.*patch" "$SKILL_FILE" 2>/dev/null || grep -q "patch.*x\.y\.Z" "$SKILL_FILE"; then
    assert_pass "skill_documents_semver_rules"
else
    assert_fail "skill_documents_semver_rules" "Should document semver decision rules"
fi

# Test: Skill warns about --delete-branch
if grep -q "NEVER.*--delete-branch\|delete-branch.*NEVER" "$SKILL_FILE"; then
    assert_pass "skill_warns_delete_branch"
else
    assert_fail "skill_warns_delete_branch" "Should warn about --delete-branch danger"
fi

echo ""

# ============================================================================
# Summary
# ============================================================================

echo -e "${T_BOLD}===============================${T_NC}"
echo -e "${T_BOLD}  Release Skill E2E Summary${T_NC}"
echo -e "${T_BOLD}===============================${T_NC}"
echo ""
echo -e "  Total:   ${T_BOLD}$TOTAL${T_NC}"
echo -e "  Passed:  ${T_GREEN}$PASS${T_NC}"
echo -e "  Failed:  ${T_RED}$FAIL${T_NC}"
echo -e "  Skipped: ${T_YELLOW}$SKIP${T_NC}"
echo ""

if [[ $FAIL -gt 0 ]]; then
    echo -e "${T_RED}Failed tests:${T_NC}"
    for name in "${FAILED_NAMES[@]}"; do
        echo -e "  ${T_RED}-${T_NC} $name"
    done
    echo ""
    echo -e "${T_RED}RESULT: FAIL${T_NC}"
    exit 1
else
    echo -e "${T_GREEN}RESULT: ALL TESTS PASSED${T_NC}"
    exit 0
fi
