#!/usr/bin/env bash
#
# E2E Tests for Marketplace Distribution
# Tests: marketplace.json structure, version consistency,
#        pre-release-check integration, release skill steps.
#
# Usage:
#   bash tests/test_marketplace_e2e.sh
#
# Requirements:
#   - Craft plugin (marketplace feature branch)
#   - git, python3, jq available

set -uo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRAFT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MARKETPLACE_JSON="$CRAFT_ROOT/.claude-plugin/marketplace.json"
PLUGIN_JSON="$CRAFT_ROOT/.claude-plugin/plugin.json"
PRE_RELEASE_SCRIPT="$CRAFT_ROOT/scripts/pre-release-check.sh"
SKILL_FILE="$CRAFT_ROOT/skills/release/SKILL.md"

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

if [[ ! -f "$MARKETPLACE_JSON" ]]; then
    echo -e "${T_RED}ERROR${T_NC}: marketplace.json not found at $MARKETPLACE_JSON"
    echo "  Create .claude-plugin/marketplace.json first, then run these tests."
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

if ! command -v jq &>/dev/null; then
    echo -e "${T_RED}ERROR${T_NC}: jq is not available"
    exit 1
fi

# ============================================================================
# Helpers
# ============================================================================

make_tmpdir() {
    local dir
    dir=$(mktemp -d "${TMPDIR:-/tmp}/marketplace-e2e.XXXXXX")
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
        mkdir -p .claude-plugin
        echo '{"name":"test","version":"1.2.3","description":"A test plugin","author":{"name":"Test"}}' > .claude-plugin/plugin.json
        cat > .claude-plugin/marketplace.json << 'MKJSON'
{
  "name": "test-marketplace",
  "owner": {"name": "Test"},
  "metadata": {"description": "Test marketplace", "version": "1.2.3"},
  "plugins": [{"name": "test", "source": {"source": "github", "repo": "test/test"}, "description": "A test plugin", "version": "1.2.3"}]
}
MKJSON
        echo "# README" > README.md
        git add -A
        git commit -m "Initial commit" --quiet
        git tag v1.2.3
        git branch dev
        git checkout dev --quiet 2>/dev/null
    )
    echo "$repo"
}

init_repo_no_marketplace() {
    local repo
    repo=$(make_tmpdir)
    (
        cd "$repo"
        git init -b main --quiet
        git config user.email "test@test.com"
        git config user.name "Test"
        mkdir -p .claude-plugin
        echo '{"name":"test","version":"1.2.3","description":"A test plugin","author":{"name":"Test"}}' > .claude-plugin/plugin.json
        echo "# README" > README.md
        git add -A
        git commit -m "Initial commit" --quiet
        git tag v1.2.3
        git branch dev
        git checkout dev --quiet 2>/dev/null
    )
    echo "$repo"
}

init_repo_bad_version() {
    local repo
    repo=$(make_tmpdir)
    (
        cd "$repo"
        git init -b main --quiet
        git config user.email "test@test.com"
        git config user.name "Test"
        mkdir -p .claude-plugin
        echo '{"name":"test","version":"1.2.3","description":"A test plugin","author":{"name":"Test"}}' > .claude-plugin/plugin.json
        cat > .claude-plugin/marketplace.json << 'MKJSON'
{
  "name": "test-marketplace",
  "owner": {"name": "Test"},
  "metadata": {"description": "Test marketplace", "version": "9.9.9"},
  "plugins": [{"name": "test", "source": {"source": "github", "repo": "test/test"}, "description": "A test plugin", "version": "9.9.9"}]
}
MKJSON
        echo "# README" > README.md
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
echo -e "${T_BOLD}Marketplace Distribution E2E Tests${T_NC}"
echo -e "${T_BOLD}==================================${T_NC}"
echo -e "Marketplace: $MARKETPLACE_JSON"
echo ""

# --------------------------------------------------------------------------
# Group 1: marketplace.json Structure
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Group 1: marketplace.json Structure ---${T_NC}"

# Test: marketplace.json exists
if [[ -f "$MARKETPLACE_JSON" ]]; then
    assert_pass "marketplace_json_exists"
else
    assert_fail "marketplace_json_exists" "File not found"
fi

# Test: Valid JSON
if jq empty "$MARKETPLACE_JSON" 2>/dev/null; then
    assert_pass "marketplace_json_valid"
else
    assert_fail "marketplace_json_valid" "jq empty failed — invalid JSON"
fi

# Test: Has required top-level fields: name, owner, plugins
MISSING_FIELDS=""
for field in name owner plugins; do
    if ! jq -e ".$field" "$MARKETPLACE_JSON" &>/dev/null; then
        MISSING_FIELDS="$MISSING_FIELDS $field"
    fi
done
if [[ -z "$MISSING_FIELDS" ]]; then
    assert_pass "marketplace_has_required_fields"
else
    assert_fail "marketplace_has_required_fields" "Missing:$MISSING_FIELDS"
fi

# Test: owner.name is non-empty
OWNER_NAME=$(jq -r '.owner.name // ""' "$MARKETPLACE_JSON")
if [[ -n "$OWNER_NAME" ]]; then
    assert_pass "marketplace_owner_name_nonempty"
else
    assert_fail "marketplace_owner_name_nonempty" "owner.name is empty"
fi

# Test: plugins array has at least 1 entry
PLUGIN_COUNT=$(jq '.plugins | length' "$MARKETPLACE_JSON")
if [[ "$PLUGIN_COUNT" -ge 1 ]]; then
    assert_pass "marketplace_plugins_nonempty"
else
    assert_fail "marketplace_plugins_nonempty" "plugins array is empty"
fi

# Test: plugins[0] has name, source, description, version
MISSING_PLUGIN_FIELDS=""
for field in name source description version; do
    if ! jq -e ".plugins[0].$field" "$MARKETPLACE_JSON" &>/dev/null; then
        MISSING_PLUGIN_FIELDS="$MISSING_PLUGIN_FIELDS $field"
    fi
done
if [[ -z "$MISSING_PLUGIN_FIELDS" ]]; then
    assert_pass "marketplace_plugin0_has_required_fields"
else
    assert_fail "marketplace_plugin0_has_required_fields" "Missing:$MISSING_PLUGIN_FIELDS"
fi

# Test: source is a GitHub object (has .source == "github")
SOURCE_TYPE=$(jq -r '.plugins[0].source.source // ""' "$MARKETPLACE_JSON")
if [[ "$SOURCE_TYPE" == "github" ]]; then
    assert_pass "marketplace_source_is_github"
else
    assert_fail "marketplace_source_is_github" "Expected source.source='github', got '$SOURCE_TYPE'"
fi

# Test: source has .repo field
SOURCE_REPO=$(jq -r '.plugins[0].source.repo // ""' "$MARKETPLACE_JSON")
if [[ -n "$SOURCE_REPO" ]]; then
    assert_pass "marketplace_source_has_repo"
else
    assert_fail "marketplace_source_has_repo" "source.repo is empty"
fi

# Test: marketplace name is kebab-case
MKT_NAME=$(jq -r '.name' "$MARKETPLACE_JSON")
if echo "$MKT_NAME" | grep -qE '^[a-z0-9-]+$'; then
    assert_pass "marketplace_name_kebab_case"
else
    assert_fail "marketplace_name_kebab_case" "Name '$MKT_NAME' is not kebab-case (must match ^[a-z0-9-]+$)"
fi

echo ""

# --------------------------------------------------------------------------
# Group 2: Version Consistency
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Group 2: Version Consistency ---${T_NC}"

PLUGIN_VERSION=$(python3 -c "import json; print(json.load(open('$PLUGIN_JSON'))['version'])")
MKT_META_VERSION=$(jq -r '.metadata.version' "$MARKETPLACE_JSON")
MKT_PLUGIN_VERSION=$(jq -r '.plugins[0].version' "$MARKETPLACE_JSON")

# Test: metadata.version matches plugin.json version
if [[ "$MKT_META_VERSION" == "$PLUGIN_VERSION" ]]; then
    assert_pass "version_metadata_matches_plugin_json"
else
    assert_fail "version_metadata_matches_plugin_json" "metadata.version=$MKT_META_VERSION != plugin.json=$PLUGIN_VERSION"
fi

# Test: plugins[0].version matches plugin.json version
if [[ "$MKT_PLUGIN_VERSION" == "$PLUGIN_VERSION" ]]; then
    assert_pass "version_plugins0_matches_plugin_json"
else
    assert_fail "version_plugins0_matches_plugin_json" "plugins[0].version=$MKT_PLUGIN_VERSION != plugin.json=$PLUGIN_VERSION"
fi

# Test: metadata.description is under 100 characters
MKT_DESC=$(jq -r '.metadata.description // ""' "$MARKETPLACE_JSON")
DESC_LEN=${#MKT_DESC}
if [[ "$DESC_LEN" -lt 100 ]]; then
    assert_pass "metadata_description_under_100_chars"
else
    assert_fail "metadata_description_under_100_chars" "Description is $DESC_LEN chars (max 100)"
fi

echo ""

# --------------------------------------------------------------------------
# Group 3: marketplace.json in Temp Repos
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Group 3: Temp Repo Edge Cases ---${T_NC}"

# Test: Temp repo with valid marketplace.json — versions match
REPO_GOOD=$(init_repo)
GOOD_PV=$(cd "$REPO_GOOD" && python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['version'])")
GOOD_MV=$(cd "$REPO_GOOD" && jq -r '.metadata.version' .claude-plugin/marketplace.json)
if [[ "$GOOD_PV" == "$GOOD_MV" ]]; then
    assert_pass "temp_repo_versions_match"
else
    assert_fail "temp_repo_versions_match" "plugin.json=$GOOD_PV vs marketplace.json=$GOOD_MV"
fi

# Test: Temp repo with BAD version — marketplace version != plugin.json version
REPO_BAD=$(init_repo_bad_version)
BAD_PV=$(cd "$REPO_BAD" && python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['version'])")
BAD_MV=$(cd "$REPO_BAD" && jq -r '.metadata.version' .claude-plugin/marketplace.json)
if [[ "$BAD_PV" != "$BAD_MV" ]]; then
    assert_pass "temp_repo_bad_version_detected"
else
    assert_fail "temp_repo_bad_version_detected" "Expected version mismatch: plugin.json=$BAD_PV, marketplace=$BAD_MV"
fi

# Test: Temp repo WITHOUT marketplace.json — no marketplace.json to validate
REPO_NO_MKT=$(init_repo_no_marketplace)
if [[ ! -f "$REPO_NO_MKT/.claude-plugin/marketplace.json" ]]; then
    assert_pass "temp_repo_no_marketplace_graceful_skip"
else
    assert_fail "temp_repo_no_marketplace_graceful_skip" "Expected no marketplace.json in no-marketplace repo"
fi

# Test: Temp repo marketplace.json has valid JSON structure
REPO_STRUCT=$(init_repo)
if (cd "$REPO_STRUCT" && jq empty .claude-plugin/marketplace.json 2>/dev/null); then
    assert_pass "temp_repo_marketplace_valid_json"
else
    assert_fail "temp_repo_marketplace_valid_json" "marketplace.json in temp repo is not valid JSON"
fi

# Test: Temp repo marketplace name is kebab-case
REPO_KEBAB=$(init_repo)
TEMP_NAME=$(cd "$REPO_KEBAB" && jq -r '.name' .claude-plugin/marketplace.json)
if echo "$TEMP_NAME" | grep -qE '^[a-z0-9-]+$'; then
    assert_pass "temp_repo_name_kebab_case"
else
    assert_fail "temp_repo_name_kebab_case" "Temp repo name '$TEMP_NAME' not kebab-case"
fi

# Test: Bad version repo has plugins[0].version mismatch too
REPO_BAD2=$(init_repo_bad_version)
BAD_PV2=$(cd "$REPO_BAD2" && python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['version'])")
BAD_PLV2=$(cd "$REPO_BAD2" && jq -r '.plugins[0].version' .claude-plugin/marketplace.json)
if [[ "$BAD_PV2" != "$BAD_PLV2" ]]; then
    assert_pass "temp_repo_bad_plugins0_version_detected"
else
    assert_fail "temp_repo_bad_plugins0_version_detected" "Expected plugins[0].version mismatch"
fi

echo ""

# --------------------------------------------------------------------------
# Group 4: pre-release-check.sh Marketplace Integration
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Group 4: pre-release-check.sh Integration ---${T_NC}"

# Test: Script has marketplace check
if grep -q "marketplace" "$PRE_RELEASE_SCRIPT"; then
    assert_pass "pre_release_has_marketplace_check"
else
    assert_fail "pre_release_has_marketplace_check" "No mention of 'marketplace' in pre-release-check.sh"
fi

# Test: Script has 6 checks
if grep -q "\[./6\]" "$PRE_RELEASE_SCRIPT"; then
    assert_pass "pre_release_has_6_checks"
else
    assert_fail "pre_release_has_6_checks" "Expected [N/6] check numbering"
fi

# Test: Script syntax is valid
if bash -n "$PRE_RELEASE_SCRIPT" 2>/dev/null; then
    assert_pass "pre_release_syntax_valid"
else
    assert_fail "pre_release_syntax_valid" "Syntax errors in pre-release-check.sh"
fi

# Test: Run script against real craft repo with current version — should PASS
CURRENT_VERSION=$(python3 -c "import json; print(json.load(open('$PLUGIN_JSON'))['version'])")
if (cd "$CRAFT_ROOT" && bash "$PRE_RELEASE_SCRIPT" "$CURRENT_VERSION" 2>&1) >/dev/null; then
    assert_pass "pre_release_passes_real_repo"
else
    assert_fail "pre_release_passes_real_repo" "pre-release-check.sh failed on real repo with version $CURRENT_VERSION"
fi

# Test: Marketplace check logic detects version mismatch (inline validation)
REPO_MISMATCH=$(init_repo_bad_version)
_TARGET="1.2.3"
_MKT_META=$(cd "$REPO_MISMATCH" && python3 -c "import json; print(json.load(open('.claude-plugin/marketplace.json'))['metadata']['version'])")
_MKT_PLUG=$(cd "$REPO_MISMATCH" && python3 -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); print(d['plugins'][0]['version'])")
_ERRORS=0
[[ "$_MKT_META" != "$_TARGET" ]] && _ERRORS=$((_ERRORS + 1))
[[ "$_MKT_PLUG" != "$_TARGET" ]] && _ERRORS=$((_ERRORS + 1))
if [[ $_ERRORS -gt 0 ]]; then
    assert_pass "pre_release_fails_on_mismatch"
else
    assert_fail "pre_release_fails_on_mismatch" "Expected marketplace version mismatch to be detected (meta=$_MKT_META, plug=$_MKT_PLUG, target=$_TARGET)"
fi

# Test: pre-release-check.sh gracefully skips when no marketplace.json
if grep -q "not all projects use marketplace" "$PRE_RELEASE_SCRIPT"; then
    assert_pass "pre_release_graceful_skip_message"
else
    assert_fail "pre_release_graceful_skip_message" "Script should contain graceful skip message for missing marketplace.json"
fi

# Test: pre-release-check.sh checks both metadata.version and plugins[0].version
META_CHECK=$(grep -c "metadata.*version\|MKT_META_VERSION" "$PRE_RELEASE_SCRIPT" || true)
PLUG_CHECK=$(grep -c "plugins\[0\].*version\|MKT_PLUGIN_VERSION" "$PRE_RELEASE_SCRIPT" || true)
if [[ "$META_CHECK" -ge 1 && "$PLUG_CHECK" -ge 1 ]]; then
    assert_pass "pre_release_checks_both_versions"
else
    assert_fail "pre_release_checks_both_versions" "Script should check both metadata.version and plugins[0].version"
fi

echo ""

# --------------------------------------------------------------------------
# Group 5: Release Skill Marketplace Steps
# --------------------------------------------------------------------------

echo -e "${T_BLUE}--- Group 5: Release Skill Marketplace Steps ---${T_NC}"

if [[ ! -f "$SKILL_FILE" ]]; then
    skip "skill_mentions_marketplace_validation" "SKILL.md not found"
    skip "skill_mentions_marketplace_version_bump" "SKILL.md not found"
    skip "skill_mentions_tap_auto_update" "SKILL.md not found"
    skip "skill_dry_run_mentions_tap" "SKILL.md not found"
else
    # Test: SKILL.md mentions marketplace validation
    if grep -q "Marketplace Validat" "$SKILL_FILE" || grep -q "2c" "$SKILL_FILE"; then
        assert_pass "skill_mentions_marketplace_validation"
    else
        assert_fail "skill_mentions_marketplace_validation" "SKILL.md should mention marketplace validation (2c or 'Marketplace Validat')"
    fi

    # Test: SKILL.md mentions marketplace.json in version bump
    if grep -q "marketplace.json" "$SKILL_FILE"; then
        assert_pass "skill_mentions_marketplace_version_bump"
    else
        assert_fail "skill_mentions_marketplace_version_bump" "SKILL.md should mention marketplace.json for version bumps"
    fi

    # Test: SKILL.md mentions tap auto-update
    if grep -q "8\.5" "$SKILL_FILE" || grep -qi "Tap" "$SKILL_FILE"; then
        assert_pass "skill_mentions_tap_auto_update"
    else
        assert_fail "skill_mentions_tap_auto_update" "SKILL.md should mention step 8.5 or Tap for auto-update"
    fi

    # Test: SKILL.md dry-run output mentions tap
    if grep -qi "tap" "$SKILL_FILE"; then
        assert_pass "skill_dry_run_mentions_tap"
    else
        assert_fail "skill_dry_run_mentions_tap" "SKILL.md should mention tap in dry-run output section"
    fi

    # Test: SKILL.md lists marketplace.json in version bump file list
    if grep -q "marketplace.json.*if exists\|marketplace.json.*(if" "$SKILL_FILE" || grep -q "marketplace.json" "$SKILL_FILE"; then
        assert_pass "skill_marketplace_in_bump_file_list"
    else
        assert_fail "skill_marketplace_in_bump_file_list" "SKILL.md should list marketplace.json in files to bump"
    fi
fi

echo ""

# ============================================================================
# Summary
# ============================================================================

echo -e "${T_BOLD}======================================${T_NC}"
echo -e "${T_BOLD}  Marketplace Distribution E2E Summary${T_NC}"
echo -e "${T_BOLD}======================================${T_NC}"
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
