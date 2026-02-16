#!/usr/bin/env bash
#
# E2E Tests for Homebrew Refactor (Phases 1, 2, 6)
# Tests: Command structure, subcommand consolidation, workflow hardening,
#        formula name mapping, .craft/homebrew.json, cross-references.
#
# Usage:
#   bash tests/test_homebrew_refactor_e2e.sh
#
# Requirements:
#   - Craft plugin installed (commands/dist/homebrew.md exists)
#   - git and python3 available

set -uo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRAFT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOMEBREW_CMD="$CRAFT_ROOT/commands/dist/homebrew.md"
CI_GENERATE_CMD="$CRAFT_ROOT/commands/ci/generate.md"
RELEASE_SKILL="$CRAFT_ROOT/skills/release/SKILL.md"
HOMEBREW_JSON="$CRAFT_ROOT/.craft/homebrew.json"
WORKFLOW_YML="$CRAFT_ROOT/.github/workflows/homebrew-release.yml"

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

# ============================================================================
# Helpers
# ============================================================================

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
# Preflight
# ============================================================================

echo ""
echo -e "${T_BOLD}Homebrew Refactor E2E Tests${T_NC}"
echo -e "${T_BOLD}==========================${T_NC}"
echo ""

if [[ ! -f "$HOMEBREW_CMD" ]]; then
    echo -e "${T_RED}ERROR${T_NC}: commands/dist/homebrew.md not found"
    exit 1
fi

# ============================================================================
# Group 1: Subcommand Consolidation (8 → 6)
# ============================================================================

echo -e "${T_BLUE}--- Group 1: Subcommand Consolidation (8 → 6) ---${T_NC}"

CONTENT=$(cat "$HOMEBREW_CMD")

# Test: Exactly 6 subcommands in the first table (## Subcommands section)
# Extract only the first table after "## Subcommands" header
SUBCMD_COUNT=$(sed -n '/^## Subcommands/,/^## /p' "$HOMEBREW_CMD" | grep -c '| `[a-z-]*` |')
if [[ "$SUBCMD_COUNT" -eq 6 ]]; then
    assert_pass "exactly_6_subcommands"
else
    assert_fail "exactly_6_subcommands" "Expected 6, found $SUBCMD_COUNT"
fi

# Test: validate renamed to audit
if echo "$CONTENT" | grep -q '| `audit`'; then
    assert_pass "validate_renamed_to_audit"
else
    assert_fail "validate_renamed_to_audit" "audit subcommand not in table"
fi

# Test: No validate subcommand remains
if ! echo "$CONTENT" | grep -q '| `validate`'; then
    assert_pass "no_validate_subcommand"
else
    assert_fail "no_validate_subcommand" "validate still in subcommand table"
fi

# Test: No token subcommand remains
if ! echo "$CONTENT" | grep -q '| `token`'; then
    assert_pass "no_token_subcommand"
else
    assert_fail "no_token_subcommand" "token still in subcommand table"
fi

# Test: No release-batch subcommand remains
if ! echo "$CONTENT" | grep -q '| `release-batch`'; then
    assert_pass "no_release_batch_subcommand"
else
    assert_fail "no_release_batch_subcommand" "release-batch still in subcommand table"
fi

# Test: All 6 expected subcommands present
EXPECTED_SUBS=("formula" "workflow" "audit" "setup" "update-resources" "deps")
ALL_PRESENT=true
MISSING=""
for sub in "${EXPECTED_SUBS[@]}"; do
    if ! echo "$CONTENT" | grep -q "| \`$sub\`"; then
        ALL_PRESENT=false
        MISSING="$MISSING $sub"
    fi
done
if $ALL_PRESENT; then
    assert_pass "all_6_subcommands_present"
else
    assert_fail "all_6_subcommands_present" "Missing:$MISSING"
fi

# Test: Frontmatter subcommand description updated
if grep -q 'audit.*setup.*update-resources.*deps\|formula.*workflow.*audit' "$HOMEBREW_CMD"; then
    assert_pass "frontmatter_subcommands_updated"
else
    assert_fail "frontmatter_subcommands_updated" "Frontmatter description not updated"
fi

echo ""

# ============================================================================
# Group 2: Audit Subcommand (renamed from validate)
# ============================================================================

echo -e "${T_BLUE}--- Group 2: Audit Subcommand ---${T_NC}"

# Test: Audit section header exists
if echo "$CONTENT" | grep -q "## /craft:dist:homebrew audit"; then
    assert_pass "audit_section_exists"
else
    assert_fail "audit_section_exists" "No audit section header"
fi

# Test: --build flag documented
if echo "$CONTENT" | grep -q "\-\-build"; then
    assert_pass "build_flag_documented"
else
    assert_fail "build_flag_documented" "--build flag not documented"
fi

# Test: --build explains brew install --build-from-source
if echo "$CONTENT" | grep -q "build-from-source"; then
    assert_pass "build_from_source_explained"
else
    assert_fail "build_from_source_explained" "build-from-source not mentioned"
fi

# Test: Auto-fix patterns section exists
if echo "$CONTENT" | grep -q "Auto-Fix Patterns"; then
    assert_pass "auto_fix_patterns_exist"
else
    assert_fail "auto_fix_patterns_exist" "Auto-Fix Patterns section missing"
fi

# Test: No stale 'validate' references in tips/integration
STALE_COUNT=$(echo "$CONTENT" | grep -c "validate" || true)
if [[ "$STALE_COUNT" -eq 0 ]]; then
    assert_pass "no_stale_validate_refs"
else
    assert_fail "no_stale_validate_refs" "Found $STALE_COUNT 'validate' references in homebrew.md"
fi

echo ""

# ============================================================================
# Group 3: Token Folded into Setup
# ============================================================================

echo -e "${T_BLUE}--- Group 3: Token Folded into Setup ---${T_NC}"

# Test: No standalone token section
if ! echo "$CONTENT" | grep -q "## /craft:dist:homebrew token"; then
    assert_pass "no_standalone_token_section"
else
    assert_fail "no_standalone_token_section" "Standalone token section still exists"
fi

# Test: Setup step 4 mentions token
SETUP_SECTION=$(echo "$CONTENT" | sed -n '/## \/craft:dist:homebrew setup/,/## \/craft:dist:homebrew/p')
if echo "$SETUP_SECTION" | grep -qi "token"; then
    assert_pass "setup_step4_has_token"
else
    assert_fail "setup_step4_has_token" "Setup wizard doesn't mention token"
fi

# Test: Setup mentions Fine-Grained PAT
if echo "$SETUP_SECTION" | grep -qi "fine-grained\|PAT"; then
    assert_pass "setup_mentions_pat"
else
    assert_fail "setup_mentions_pat" "Setup doesn't mention Fine-Grained PAT"
fi

# Test: Setup mentions HOMEBREW_TAP_GITHUB_TOKEN
if echo "$SETUP_SECTION" | grep -q "HOMEBREW_TAP_GITHUB_TOKEN"; then
    assert_pass "setup_mentions_token_name"
else
    assert_fail "setup_mentions_token_name" "Setup doesn't mention HOMEBREW_TAP_GITHUB_TOKEN"
fi

echo ""

# ============================================================================
# Group 4: Deps Subcommand (expanded)
# ============================================================================

echo -e "${T_BLUE}--- Group 4: Deps Subcommand ---${T_NC}"

# Test: deps section exists
if echo "$CONTENT" | grep -q "## /craft:dist:homebrew deps"; then
    assert_pass "deps_section_exists"
else
    assert_fail "deps_section_exists" "No deps section header"
fi

# Test: Inter-formula dependency graph documented
if echo "$CONTENT" | grep -qi "inter-formula"; then
    assert_pass "inter_formula_graph_documented"
else
    assert_fail "inter_formula_graph_documented" "No inter-formula dependency graph"
fi

# Test: System dependencies matrix documented
if echo "$CONTENT" | grep -qi "system dep"; then
    assert_pass "system_deps_matrix_documented"
else
    assert_fail "system_deps_matrix_documented" "No system dependencies matrix"
fi

# Test: --system flag documented
if echo "$CONTENT" | grep -q "\-\-system"; then
    assert_pass "system_flag_documented"
else
    assert_fail "system_flag_documented" "--system flag not documented"
fi

# Test: --dot flag for Graphviz
if echo "$CONTENT" | grep -q "\-\-dot"; then
    assert_pass "dot_flag_documented"
else
    assert_fail "dot_flag_documented" "--dot flag not documented"
fi

echo ""

# ============================================================================
# Group 5: Workflow Hardening
# ============================================================================

echo -e "${T_BLUE}--- Group 5: Workflow Hardening ---${T_NC}"

# Test: Workflow YAML exists
if [[ -f "$WORKFLOW_YML" ]]; then
    assert_pass "workflow_yml_exists"
else
    assert_fail "workflow_yml_exists" ".github/workflows/homebrew-release.yml not found"
fi

if [[ -f "$WORKFLOW_YML" ]]; then
    WF_CONTENT=$(cat "$WORKFLOW_YML")

    # Test: Uses env indirection (no direct ${{ github.event_name }} in run blocks)
    # Check that EVENT_NAME is defined in env
    if echo "$WF_CONTENT" | grep -q 'EVENT_NAME:'; then
        assert_pass "workflow_env_indirection"
    else
        assert_fail "workflow_env_indirection" "No EVENT_NAME env var for script injection prevention"
    fi

    # Test: Uses sha256sum (not shasum)
    if echo "$WF_CONTENT" | grep -q "sha256sum"; then
        assert_pass "workflow_sha256sum"
    else
        assert_fail "workflow_sha256sum" "Still using shasum instead of sha256sum"
    fi

    # Test: Has retry on curl
    if echo "$WF_CONTENT" | grep -q "\-\-retry"; then
        assert_pass "workflow_curl_retry"
    else
        assert_fail "workflow_curl_retry" "No --retry on curl command"
    fi

    # Test: Has SHA validation guard
    if echo "$WF_CONTENT" | grep -q '${#SHA256}'; then
        assert_pass "workflow_sha_guard"
    else
        assert_fail "workflow_sha_guard" "No SHA256 length validation guard"
    fi
fi

# Test: Workflow template in homebrew.md also hardened
if echo "$CONTENT" | grep -q "sha256sum"; then
    assert_pass "template_uses_sha256sum"
else
    assert_fail "template_uses_sha256sum" "Template in homebrew.md still uses shasum"
fi

if echo "$CONTENT" | grep -q "env indirection\|script injection"; then
    assert_pass "template_documents_security"
else
    assert_fail "template_documents_security" "Template doesn't document security features"
fi

echo ""

# ============================================================================
# Group 6: .craft/homebrew.json Config
# ============================================================================

echo -e "${T_BLUE}--- Group 6: .craft/homebrew.json Config ---${T_NC}"

# Test: Config file exists
if [[ -f "$HOMEBREW_JSON" ]]; then
    assert_pass "homebrew_json_exists"
else
    assert_fail "homebrew_json_exists" ".craft/homebrew.json not found"
fi

if [[ -f "$HOMEBREW_JSON" ]]; then
    # Test: Valid JSON
    if python3 -m json.tool "$HOMEBREW_JSON" >/dev/null 2>&1; then
        assert_pass "homebrew_json_valid"
    else
        assert_fail "homebrew_json_valid" "Invalid JSON"
    fi

    # Test: Has formula_name field
    if python3 -c "import json; d=json.load(open('$HOMEBREW_JSON')); assert 'formula_name' in d" 2>/dev/null; then
        assert_pass "homebrew_json_has_formula_name"
    else
        assert_fail "homebrew_json_has_formula_name" "Missing formula_name field"
    fi

    # Test: Has tap field
    if python3 -c "import json; d=json.load(open('$HOMEBREW_JSON')); assert 'tap' in d" 2>/dev/null; then
        assert_pass "homebrew_json_has_tap"
    else
        assert_fail "homebrew_json_has_tap" "Missing tap field"
    fi

    # Test: formula_name is "craft"
    FNAME=$(python3 -c "import json; print(json.load(open('$HOMEBREW_JSON'))['formula_name'])" 2>/dev/null)
    if [[ "$FNAME" == "craft" ]]; then
        assert_pass "homebrew_json_formula_name_correct"
    else
        assert_fail "homebrew_json_formula_name_correct" "Expected 'craft', got '$FNAME'"
    fi

    # Test: tap is "data-wise/tap"
    TAP=$(python3 -c "import json; print(json.load(open('$HOMEBREW_JSON'))['tap'])" 2>/dev/null)
    if [[ "$TAP" == "data-wise/tap" ]]; then
        assert_pass "homebrew_json_tap_correct"
    else
        assert_fail "homebrew_json_tap_correct" "Expected 'data-wise/tap', got '$TAP'"
    fi
fi

echo ""

# ============================================================================
# Group 7: Release Skill Step 8.5 Updates
# ============================================================================

echo -e "${T_BLUE}--- Group 7: Release Skill Step 8.5 ---${T_NC}"

SKILL_CONTENT=$(cat "$RELEASE_SKILL")

# Test: Step 8.5 exists
if echo "$SKILL_CONTENT" | grep -q "Step 8.5"; then
    assert_pass "step_8_5_exists"
else
    assert_fail "step_8_5_exists" "Step 8.5 not found in SKILL.md"
fi

# Test: basename $PWD is not the primary formula name lookup
# It can exist as a fallback (3rd priority), but config should come first
CONFIG_LINE=$(echo "$SKILL_CONTENT" | grep -n ".craft/homebrew.json" | head -1 | cut -d: -f1)
BASENAME_LINE=$(echo "$SKILL_CONTENT" | grep -n 'basename' | head -1 | cut -d: -f1)
if [[ -n "$CONFIG_LINE" && -n "$BASENAME_LINE" ]] && [[ "$CONFIG_LINE" -lt "$BASENAME_LINE" ]]; then
    assert_pass "config_before_basename"
else
    assert_fail "config_before_basename" "Config lookup should appear before basename fallback"
fi

# Test: Uses .craft/homebrew.json lookup
if echo "$SKILL_CONTENT" | grep -q ".craft/homebrew.json"; then
    assert_pass "uses_homebrew_json_config"
else
    assert_fail "uses_homebrew_json_config" "Doesn't reference .craft/homebrew.json"
fi

# Test: Has git remote fallback
if echo "$SKILL_CONTENT" | grep -q "git remote"; then
    assert_pass "has_git_remote_fallback"
else
    assert_fail "has_git_remote_fallback" "No git remote fallback in lookup chain"
fi

# Test: Has basename fallback (3rd priority)
if echo "$SKILL_CONTENT" | grep -q "basename.*fallback\|Basename fallback"; then
    assert_pass "has_basename_fallback"
else
    assert_fail "has_basename_fallback" "No basename fallback documented"
fi

# Test: Uses sha256sum (not shasum)
STEP85=$(echo "$SKILL_CONTENT" | sed -n '/Step 8.5/,/Step 9/p')
if echo "$STEP85" | grep -q "sha256sum"; then
    assert_pass "step85_uses_sha256sum"
else
    assert_fail "step85_uses_sha256sum" "Step 8.5 still uses shasum"
fi

# Test: Has ruby -c syntax check
if echo "$STEP85" | grep -q "ruby -c"; then
    assert_pass "step85_has_ruby_syntax_check"
else
    assert_fail "step85_has_ruby_syntax_check" "No ruby -c syntax check after sed update"
fi

# Test: Has SHA validation guard
if echo "$STEP85" | grep -q '${#SHA256}'; then
    assert_pass "step85_has_sha_guard"
else
    assert_fail "step85_has_sha_guard" "No SHA256 validation guard in Step 8.5"
fi

# Test: Has curl retry
if echo "$STEP85" | grep -q "\-\-retry"; then
    assert_pass "step85_has_curl_retry"
else
    assert_fail "step85_has_curl_retry" "No --retry on curl in Step 8.5"
fi

echo ""

# ============================================================================
# Group 8: Cross-References
# ============================================================================

echo -e "${T_BLUE}--- Group 8: Cross-References ---${T_NC}"

# Test: ci:generate references dist:homebrew workflow
if grep -q "dist:homebrew workflow" "$CI_GENERATE_CMD"; then
    assert_pass "ci_generate_xref_homebrew"
else
    assert_fail "ci_generate_xref_homebrew" "ci:generate.md doesn't reference dist:homebrew workflow"
fi

# Test: No stale validate references in skills
STALE_SKILLS=$(grep -rl "dist:homebrew validate" "$CRAFT_ROOT/skills/" 2>/dev/null | wc -l | tr -d ' ')
if [[ "$STALE_SKILLS" -eq 0 ]]; then
    assert_pass "no_stale_validate_in_skills"
else
    assert_fail "no_stale_validate_in_skills" "Found $STALE_SKILLS skill files with stale validate ref"
fi

# Test: No stale validate references in docs
STALE_DOCS=$(grep -rl "dist:homebrew validate" "$CRAFT_ROOT/docs/" 2>/dev/null | wc -l | tr -d ' ')
if [[ "$STALE_DOCS" -eq 0 ]]; then
    assert_pass "no_stale_validate_in_docs"
else
    assert_fail "no_stale_validate_in_docs" "Found $STALE_DOCS doc files with stale validate ref"
fi

# Test: No stale token subcommand references
STALE_TOKEN=$(grep -rl "dist:homebrew token" "$CRAFT_ROOT/skills/" "$CRAFT_ROOT/docs/" "$CRAFT_ROOT/commands/" 2>/dev/null | wc -l | tr -d ' ')
if [[ "$STALE_TOKEN" -eq 0 ]]; then
    assert_pass "no_stale_token_refs"
else
    assert_fail "no_stale_token_refs" "Found $STALE_TOKEN files with stale token subcommand ref"
fi

echo ""

# ============================================================================
# Summary
# ============================================================================

echo -e "${T_BOLD}=======================================${T_NC}"
echo -e "${T_BOLD}  Homebrew Refactor E2E Summary${T_NC}"
echo -e "${T_BOLD}=======================================${T_NC}"
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
