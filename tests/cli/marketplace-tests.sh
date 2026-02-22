#!/bin/bash
# Marketplace Distribution Test Suite for: craft plugin
# Generated: 2026-02-14
# Run: bash tests/cli/marketplace-tests.sh
#
# Tests the marketplace distribution feature added in v2.18.0:
#   1. marketplace.json structure and validity
#   2. Version consistency across plugin.json, marketplace.json, and docs
#   3. dist:marketplace command file structure
#   4. Homebrew auto-detection table
#   5. Release skill marketplace integration
#   6. Pre-release check marketplace validation
#   7. Documentation install hierarchy

set -euo pipefail

# ============================================
# Configuration
# ============================================

PLUGIN_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PASS=0
FAIL=0
SKIP=0
TOTAL=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# ============================================
# Helpers
# ============================================

log_pass() {
    PASS=$((PASS + 1))
    TOTAL=$((TOTAL + 1))
    echo -e "${GREEN}  ✓${NC} $1"
}

log_fail() {
    FAIL=$((FAIL + 1))
    TOTAL=$((TOTAL + 1))
    echo -e "${RED}  ✗${NC} $1"
    if [[ -n "${2:-}" ]]; then
        echo -e "    ${RED}→ $2${NC}"
    fi
}

log_skip() {
    SKIP=$((SKIP + 1))
    TOTAL=$((TOTAL + 1))
    echo -e "${YELLOW}  - ${NC} $1"
}

section() {
    echo ""
    echo -e "${BLUE}${BOLD}━━━ $1 ━━━${NC}"
}

# ============================================
# Tests
# ============================================

echo -e "${BOLD}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}  MARKETPLACE DISTRIBUTION TEST SUITE${NC}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "  Plugin: $PLUGIN_DIR"
echo "  Time:   $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

cd "$PLUGIN_DIR"

# ─── 1. marketplace.json Structure ──────────────────────────────────────────

section "1. marketplace.json Structure"

MKT_JSON=".claude-plugin/marketplace.json"

if [[ -f "$MKT_JSON" ]]; then
    log_pass "marketplace.json exists"
else
    log_fail "marketplace.json missing" "Expected at $MKT_JSON"
fi

# Valid JSON
if jq empty "$MKT_JSON" 2>/dev/null; then
    log_pass "marketplace.json is valid JSON"
else
    log_fail "marketplace.json is invalid JSON"
fi

# Required top-level fields
for field in name owner plugins; do
    if jq -e ".$field" "$MKT_JSON" >/dev/null 2>&1; then
        log_pass "Has required field: $field"
    else
        log_fail "Missing required field: $field"
    fi
done

# Owner has name
if jq -e '.owner.name' "$MKT_JSON" >/dev/null 2>&1; then
    log_pass "owner.name present: $(jq -r '.owner.name' "$MKT_JSON")"
else
    log_fail "owner.name missing"
fi

# Metadata fields
for field in description version; do
    if jq -e ".metadata.$field" "$MKT_JSON" >/dev/null 2>&1; then
        log_pass "metadata.$field present"
    else
        log_fail "metadata.$field missing"
    fi
done

# Plugin entry
if [[ $(jq '.plugins | length' "$MKT_JSON") -ge 1 ]]; then
    log_pass "plugins array has at least 1 entry"
else
    log_fail "plugins array is empty"
fi

# Plugin entry required fields
for field in name source description version; do
    if jq -e ".plugins[0].$field" "$MKT_JSON" >/dev/null 2>&1; then
        log_pass "plugins[0].$field present"
    else
        log_fail "plugins[0].$field missing"
    fi
done

# Source is GitHub object (not relative path)
SOURCE_TYPE=$(jq -r '.plugins[0].source.source // "string"' "$MKT_JSON" 2>/dev/null)
if [[ "$SOURCE_TYPE" == "github" ]]; then
    log_pass "source uses GitHub object format"
    REPO=$(jq -r '.plugins[0].source.repo' "$MKT_JSON" 2>/dev/null)
    if [[ -n "$REPO" && "$REPO" != "null" ]]; then
        log_pass "source.repo present: $REPO"
    else
        log_fail "source.repo missing from GitHub source"
    fi
elif [[ "$SOURCE_TYPE" == "string" ]]; then
    SOURCE_VAL=$(jq -r '.plugins[0].source' "$MKT_JSON" 2>/dev/null)
    log_fail "source is relative path '$SOURCE_VAL'" "Should be GitHub object for root-level plugins"
else
    log_skip "source type: $SOURCE_TYPE (not validated)"
fi

# Optional marketplace fields
for field in homepage repository license category keywords; do
    if jq -e ".plugins[0].$field" "$MKT_JSON" >/dev/null 2>&1; then
        log_pass "plugins[0].$field present"
    else
        log_skip "plugins[0].$field not set (optional)"
    fi
done

# Name format (kebab-case)
MKT_NAME=$(jq -r '.name' "$MKT_JSON")
if [[ "$MKT_NAME" =~ ^[a-z0-9-]+$ ]]; then
    log_pass "marketplace name is kebab-case: $MKT_NAME"
else
    log_fail "marketplace name not kebab-case: $MKT_NAME"
fi

# ─── 2. Version Consistency ─────────────────────────────────────────────────

section "2. Version Consistency"

PLUGIN_VERSION=$(jq -r '.version' ".claude-plugin/plugin.json" 2>/dev/null)
MKT_META_VERSION=$(jq -r '.metadata.version' "$MKT_JSON" 2>/dev/null)
MKT_PLUGIN_VERSION=$(jq -r '.plugins[0].version' "$MKT_JSON" 2>/dev/null)

if [[ "$MKT_META_VERSION" == "$PLUGIN_VERSION" ]]; then
    log_pass "metadata.version ($MKT_META_VERSION) == plugin.json ($PLUGIN_VERSION)"
else
    log_fail "metadata.version ($MKT_META_VERSION) != plugin.json ($PLUGIN_VERSION)"
fi

if [[ "$MKT_PLUGIN_VERSION" == "$PLUGIN_VERSION" ]]; then
    log_pass "plugins[0].version ($MKT_PLUGIN_VERSION) == plugin.json ($PLUGIN_VERSION)"
else
    log_fail "plugins[0].version ($MKT_PLUGIN_VERSION) != plugin.json ($PLUGIN_VERSION)"
fi

# Description consistency (marketplace desc should be shorter/derived from plugin.json)
MKT_DESC_LEN=$(jq -r '.metadata.description | length' "$MKT_JSON" 2>/dev/null)
if [[ "$MKT_DESC_LEN" -le 100 ]]; then
    log_pass "metadata.description is concise ($MKT_DESC_LEN chars)"
else
    log_fail "metadata.description too long ($MKT_DESC_LEN chars)" "Should be under 100 chars"
fi

# ─── 3. dist:marketplace Command ────────────────────────────────────────────

section "3. dist:marketplace Command"

MKT_CMD="commands/dist/marketplace.md"

if [[ -f "$MKT_CMD" ]]; then
    log_pass "marketplace.md command file exists"
else
    log_fail "marketplace.md command file missing" "Expected at $MKT_CMD"
fi

# Has YAML frontmatter
if head -1 "$MKT_CMD" | grep -q '^---$'; then
    log_pass "Has YAML frontmatter"
else
    log_fail "Missing YAML frontmatter"
fi

# Has description in frontmatter
if grep -q '^description:' "$MKT_CMD"; then
    log_pass "Frontmatter has description"
else
    log_fail "Frontmatter missing description"
fi

# Has arguments in frontmatter
if grep -q 'arguments:' "$MKT_CMD"; then
    log_pass "Frontmatter has arguments"
else
    log_fail "Frontmatter missing arguments"
fi

# All 4 subcommands documented
for subcmd in init validate test publish; do
    if grep -qi "## .*$subcmd\|### .*$subcmd\|subcommand.*$subcmd\|\`$subcmd\`" "$MKT_CMD"; then
        log_pass "Subcommand documented: $subcmd"
    else
        log_fail "Subcommand not documented: $subcmd"
    fi
done

# Has box-drawing output examples
if grep -q '┌\|└\|├\|│' "$MKT_CMD"; then
    log_pass "Has box-drawing output format"
else
    log_skip "No box-drawing output examples"
fi

# References integration commands
for ref in "dist:homebrew" "check" "release"; do
    if grep -qi "$ref" "$MKT_CMD"; then
        log_pass "References: $ref"
    else
        log_skip "No reference to: $ref"
    fi
done

# ─── 4. Homebrew Auto-Detection ─────────────────────────────────────────────

section "4. Homebrew Auto-Detection"

HB_CMD="commands/dist/homebrew.md"

# Claude Code Plugin in auto-detect table
if grep -q 'Claude Code Plugin' "$HB_CMD"; then
    log_pass "Claude Code Plugin in auto-detect table"
else
    log_fail "Claude Code Plugin missing from auto-detect table"
fi

# Plugin detection uses .claude-plugin/plugin.json
if grep -q '\.claude-plugin/plugin\.json' "$HB_CMD"; then
    log_pass "Detection uses .claude-plugin/plugin.json"
else
    log_fail "Detection doesn't reference .claude-plugin/plugin.json"
fi

# Detection priority note
if grep -qi 'detection priority\|priority.*Plugin.*Python' "$HB_CMD"; then
    log_pass "Detection priority documented"
else
    log_skip "No detection priority note"
fi

# Plugin formula template exists
if grep -q 'libexec.install' "$HB_CMD"; then
    log_pass "Plugin formula template present (libexec.install)"
else
    log_fail "Plugin formula template missing"
fi

# brew audit compliance patterns
for pattern in "Array#include\|%w\[" "assert_path_exists" "caveats.*before.*test\|caveats.*test"; do
    if grep -qP "$pattern" "$HB_CMD" 2>/dev/null || grep -q "$pattern" "$HB_CMD" 2>/dev/null; then
        log_pass "brew audit pattern present: $(echo "$pattern" | head -c 30)"
    else
        log_skip "brew audit pattern not found: $(echo "$pattern" | head -c 30)"
    fi
done

# ─── 5. Release Skill Integration ──────────────────────────────────────────

section "5. Release Skill Integration"

RELEASE_SKILL="skills/release/SKILL.md"

# Step 2c: Marketplace validation
if grep -q '2c\|[Mm]arketplace [Vv]alidat' "$RELEASE_SKILL"; then
    log_pass "Step 2c: marketplace validation present"
else
    log_fail "Step 2c: marketplace validation missing"
fi

# Step 3: marketplace.json in version bump
if grep -q 'marketplace\.json' "$RELEASE_SKILL"; then
    log_pass "marketplace.json referenced in release skill"
else
    log_fail "marketplace.json not referenced in release skill"
fi

# Step 8.5: Tap auto-update
if grep -q '8\.5\|[Tt]ap.*[Uu]pdate\|[Hh]omebrew.*[Tt]ap' "$RELEASE_SKILL"; then
    log_pass "Step 8.5: tap auto-update present"
else
    log_fail "Step 8.5: tap auto-update missing"
fi

# Dry-run output includes tap update
if grep -q 'tap\|Homebrew' <(sed -n '/dry.*run\|DRY.*RUN/,/└/p' "$RELEASE_SKILL") 2>/dev/null; then
    log_pass "Dry-run output includes tap update"
else
    log_skip "Could not verify dry-run output"
fi

# marketplace.json bump mentions both metadata.version and plugins[0].version
if grep -q 'metadata\.version\|plugins\[0\]\.version' "$RELEASE_SKILL"; then
    log_pass "Version bump mentions marketplace.json fields"
else
    log_skip "No explicit marketplace.json field references"
fi

# ─── 6. Pre-Release Check ──────────────────────────────────────────────────

section "6. Pre-Release Check Script"

PRE_CHECK="scripts/pre-release-check.sh"

# Has marketplace check
if grep -q 'marketplace' "$PRE_CHECK"; then
    log_pass "pre-release-check.sh has marketplace check"
else
    log_fail "pre-release-check.sh missing marketplace check"
fi

# Check count is 8
if grep -q '\[.\+/8\]' "$PRE_CHECK"; then
    log_pass "Check count is /8 (includes badge + formula checks)"
else
    log_fail "Check count not /8" "Expected 8 checks including badge + formula"
fi

# Validates metadata.version
if grep -q 'metadata.*version\|MKT_META_VERSION' "$PRE_CHECK"; then
    log_pass "Validates metadata.version"
else
    log_fail "Does not validate metadata.version"
fi

# Validates plugins[0].version
if grep -q 'plugins.*version\|MKT_PLUGIN_VERSION' "$PRE_CHECK"; then
    log_pass "Validates plugins[0].version"
else
    log_fail "Does not validate plugins[0].version"
fi

# Graceful skip when marketplace.json missing
if grep -q 'not found\|skipping\|not all projects' "$PRE_CHECK"; then
    log_pass "Graceful skip when marketplace.json absent"
else
    log_fail "No graceful skip for missing marketplace.json"
fi

# ─── 7. Documentation Install Hierarchy ────────────────────────────────────

section "7. Documentation Install Hierarchy"

# README: marketplace is Option 1
if head -30 README.md | grep -q 'Marketplace.*Recommended\|Option 1.*Marketplace'; then
    log_pass "README: marketplace is Option 1 (Recommended)"
else
    log_fail "README: marketplace not first/recommended install option"
fi

# README: Homebrew is Option 2
if grep -q 'Option 2.*Homebrew\|Option 2.*macOS' README.md; then
    log_pass "README: Homebrew is Option 2"
else
    log_skip "README: Homebrew option numbering unclear"
fi

# README: install command present
if grep -q 'claude plugin add\|plugin marketplace add' README.md; then
    log_pass "README: marketplace install command present"
else
    log_fail "README: marketplace install command missing"
fi

# Homebrew guide: marketplace alternative section
if grep -qi 'Marketplace.*Recommended\|Alternative.*Marketplace' "docs/guide/homebrew-installation.md" 2>/dev/null; then
    log_pass "Homebrew guide: marketplace alternative section present"
else
    log_skip "Homebrew guide: marketplace section not found"
fi

# ============================================
# Summary
# ============================================

echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}  RESULTS${NC}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════════${NC}"
echo -e "  Passed:  ${GREEN}$PASS${NC}"
echo -e "  Failed:  ${RED}$FAIL${NC}"
echo -e "  Skipped: ${YELLOW}$SKIP${NC}"
echo -e "  Total:   $TOTAL"
echo ""

if [[ $FAIL -eq 0 ]]; then
    echo -e "${GREEN}${BOLD}  ALL MARKETPLACE TESTS PASSED${NC}"
else
    echo -e "${RED}${BOLD}  $FAIL TEST(S) FAILED${NC}"
fi

echo ""
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
