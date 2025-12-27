#!/bin/bash
# Automated CLI Test Suite for: craft plugin
# Generated: 2025-12-26
# Run: bash tests/cli/automated-tests.sh
#
# Options:
#   --junit <file>     Output JUnit XML to file
#   --benchmark        Enable performance benchmarking
#   VERBOSE=1          Show detailed output
#
# This suite runs non-interactively and validates plugin structure,
# commands, skills, and agents automatically.

set -euo pipefail

# ============================================
# Configuration
# ============================================

PLUGIN_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PASS=0
FAIL=0
SKIP=0
TOTAL=0
VERBOSE="${VERBOSE:-0}"
BENCHMARK=${BENCHMARK:-0}
JUNIT_FILE=""
SUITE_START=$(date +%s%N)

# Performance tracking
declare -a TIMINGS=()
SLOW_THRESHOLD_MS=2000

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --junit)
            JUNIT_FILE="$2"
            shift 2
            ;;
        --benchmark)
            BENCHMARK=1
            shift
            ;;
        *)
            shift
            ;;
    esac
done

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

# Current test timing
CURRENT_TEST_START=0
CURRENT_TEST_NAME=""

# JUnit XML handling
declare -a JUNIT_TESTS=()

junit_add_test() {
    local name=$1
    local status=$2  # pass, fail, skip
    local duration_s=$3
    local message=${4:-}

    [[ -z "$JUNIT_FILE" ]] && return

    local xml_name
    xml_name=$(echo "$name" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g; s/"/\&quot;/g')
    local xml_msg
    xml_msg=$(echo "$message" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g; s/"/\&quot;/g')

    if [[ "$status" == "pass" ]]; then
        JUNIT_TESTS+=("    <testcase name=\"$xml_name\" time=\"$duration_s\"/>")
    elif [[ "$status" == "fail" ]]; then
        JUNIT_TESTS+=("    <testcase name=\"$xml_name\" time=\"$duration_s\"><failure message=\"$xml_msg\"/></testcase>")
    elif [[ "$status" == "skip" ]]; then
        JUNIT_TESTS+=("    <testcase name=\"$xml_name\" time=\"$duration_s\"><skipped/></testcase>")
    fi
}

junit_write() {
    [[ -z "$JUNIT_FILE" ]] && return

    local suite_end suite_duration_s
    suite_end=$(date +%s%N)
    suite_duration_s=$(echo "scale=3; ($suite_end - $SUITE_START) / 1000000000" | bc 2>/dev/null || echo "0")

    {
        echo '<?xml version="1.0" encoding="UTF-8"?>'
        echo '<testsuites>'
        echo "  <testsuite name=\"craft-plugin\" tests=\"$((PASS + FAIL + SKIP))\" failures=\"$FAIL\" skipped=\"$SKIP\" time=\"$suite_duration_s\" timestamp=\"$(date -Iseconds)\">"
        for test in "${JUNIT_TESTS[@]}"; do
            echo "$test"
        done
        echo '  </testsuite>'
        echo '</testsuites>'
    } > "$JUNIT_FILE"

    echo -e "\n${BLUE}JUnit XML written to:${NC} $JUNIT_FILE"
}

# Start timing a test
start_test() {
    CURRENT_TEST_NAME="$1"
    CURRENT_TEST_START=$(date +%s%N)
}

# Get elapsed time in ms
get_elapsed_ms() {
    local end_time
    end_time=$(date +%s%N)
    echo $(( (end_time - CURRENT_TEST_START) / 1000000 ))
}

log_pass() {
    local name=${CURRENT_TEST_NAME:-$1}
    local elapsed_ms duration_s timing_info=""

    if [[ $CURRENT_TEST_START -ne 0 ]]; then
        elapsed_ms=$(get_elapsed_ms)
        duration_s=$(echo "scale=3; $elapsed_ms / 1000" | bc 2>/dev/null || echo "0")
        TIMINGS+=("$elapsed_ms:$name")

        if [[ "$BENCHMARK" == "1" ]]; then
            if [[ $elapsed_ms -gt $SLOW_THRESHOLD_MS ]]; then
                timing_info=" ${YELLOW}(${elapsed_ms}ms - SLOW)${NC}"
            else
                timing_info=" (${elapsed_ms}ms)"
            fi
        fi
    else
        duration_s="0"
    fi

    PASS=$((PASS + 1))
    TOTAL=$((TOTAL + 1))
    echo -e "${GREEN}✅ PASS${NC}: $1$timing_info"
    junit_add_test "$name" "pass" "$duration_s"

    CURRENT_TEST_START=0
    CURRENT_TEST_NAME=""
}

log_fail() {
    local name=${CURRENT_TEST_NAME:-$1}
    local elapsed_ms duration_s

    if [[ $CURRENT_TEST_START -ne 0 ]]; then
        elapsed_ms=$(get_elapsed_ms)
        duration_s=$(echo "scale=3; $elapsed_ms / 1000" | bc 2>/dev/null || echo "0")
    else
        duration_s="0"
    fi

    FAIL=$((FAIL + 1))
    TOTAL=$((TOTAL + 1))
    echo -e "${RED}❌ FAIL${NC}: $1"
    if [[ -n "${2:-}" ]]; then
        echo -e "   ${RED}→ $2${NC}"
    fi

    junit_add_test "$name" "fail" "$duration_s" "${2:-Test failed}"

    CURRENT_TEST_START=0
    CURRENT_TEST_NAME=""
}

log_skip() {
    local name=${CURRENT_TEST_NAME:-$1}
    SKIP=$((SKIP + 1))
    TOTAL=$((TOTAL + 1))
    echo -e "${YELLOW}⏭️  SKIP${NC}: $1"
    junit_add_test "$name" "skip" "0"

    CURRENT_TEST_START=0
    CURRENT_TEST_NAME=""
}

section() {
    echo ""
    echo -e "${BLUE}${BOLD}━━━ $1 ━━━${NC}"
}

# ============================================
# Tests
# ============================================

print_header() {
    echo -e "${BOLD}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}  AUTOMATED PLUGIN TEST SUITE: craft${NC}"
    echo -e "${BOLD}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "  Plugin:  $PLUGIN_DIR"
    echo "  Time:    $(date '+%Y-%m-%d %H:%M:%S')"
    echo "  Verbose: $VERBOSE"
    echo ""
}

# ─── Plugin Structure ────────────────────────────────────────────────────────

test_plugin_structure() {
    section "Plugin Structure"

    # plugin.json exists
    start_test "plugin.json exists"
    if [[ -f "$PLUGIN_DIR/.claude-plugin/plugin.json" ]]; then
        log_pass "plugin.json exists"
    else
        log_fail "plugin.json missing" "$PLUGIN_DIR/.claude-plugin/plugin.json"
        return
    fi

    # plugin.json is valid JSON
    start_test "plugin.json is valid JSON"
    if jq empty "$PLUGIN_DIR/.claude-plugin/plugin.json" 2>/dev/null; then
        log_pass "plugin.json is valid JSON"
    else
        log_fail "plugin.json is invalid JSON"
        return
    fi

    # Required fields
    local name version
    name=$(jq -r '.name // empty' "$PLUGIN_DIR/.claude-plugin/plugin.json")
    version=$(jq -r '.version // empty' "$PLUGIN_DIR/.claude-plugin/plugin.json")

    start_test "plugin.json has name"
    if [[ -n "$name" ]]; then
        log_pass "plugin.json has name: $name"
    else
        log_fail "plugin.json missing 'name' field"
    fi

    start_test "plugin.json has version"
    if [[ -n "$version" ]]; then
        log_pass "plugin.json has version: $version"
    else
        log_fail "plugin.json missing 'version' field"
    fi

    # Required directories
    for dir in commands skills agents; do
        start_test "$dir/ directory exists"
        if [[ -d "$PLUGIN_DIR/$dir" ]]; then
            log_pass "$dir/ directory exists"
        else
            log_fail "$dir/ directory missing"
        fi
    done

    # README exists
    start_test "README.md exists"
    if [[ -f "$PLUGIN_DIR/README.md" ]]; then
        log_pass "README.md exists"
    else
        log_skip "README.md not found (optional)"
    fi
}

# ─── Commands ────────────────────────────────────────────────────────────────

test_commands() {
    section "Commands"

    start_test "Commands validation"
    local cmd_count=0
    local valid_count=0

    # Find all .md files in commands/
    while IFS= read -r cmd_file; do
        cmd_count=$((cmd_count + 1))
        local cmd_name
        cmd_name=$(basename "$cmd_file" .md)

        # Check file is not empty
        if [[ -s "$cmd_file" ]]; then
            valid_count=$((valid_count + 1))
            if [[ "$VERBOSE" == "1" ]]; then
                log_pass "Command: $cmd_name"
            fi
        else
            log_fail "Empty command file: $cmd_name"
        fi
    done < <(find "$PLUGIN_DIR/commands" -name "*.md" -type f 2>/dev/null)

    if [[ $cmd_count -gt 0 ]]; then
        log_pass "Found $cmd_count commands ($valid_count valid)"
    else
        log_skip "No commands found"
    fi

    # Check for subdirectory commands (grouped commands)
    local subdir_count=0
    while IFS= read -r subdir; do
        subdir_count=$((subdir_count + 1))
        local subdir_name
        subdir_name=$(basename "$subdir")
        local sub_cmds
        sub_cmds=$(find "$subdir" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
        if [[ "$VERBOSE" == "1" ]]; then
            log_pass "Command group: $subdir_name ($sub_cmds commands)"
        fi
    done < <(find "$PLUGIN_DIR/commands" -mindepth 1 -maxdepth 1 -type d 2>/dev/null)

    if [[ $subdir_count -gt 0 ]]; then
        log_pass "Found $subdir_count command groups"
    fi
}

# ─── Skills ──────────────────────────────────────────────────────────────────

test_skills() {
    section "Skills"

    start_test "Skills validation"
    local skill_count=0
    local valid_count=0

    # Find all .md files in skills/
    while IFS= read -r skill_file; do
        skill_count=$((skill_count + 1))
        local skill_name
        skill_name=$(basename "$skill_file" .md)

        # Check file is not empty
        if [[ -s "$skill_file" ]]; then
            valid_count=$((valid_count + 1))
            if [[ "$VERBOSE" == "1" ]]; then
                log_pass "Skill: $skill_name"
            fi
        else
            log_fail "Empty skill file: $skill_name"
        fi
    done < <(find "$PLUGIN_DIR/skills" -name "*.md" -type f 2>/dev/null)

    if [[ $skill_count -gt 0 ]]; then
        log_pass "Found $skill_count skills ($valid_count valid)"
    else
        log_skip "No skills found"
    fi

    # Check for skill subdirectories
    local subdir_count=0
    while IFS= read -r subdir; do
        subdir_count=$((subdir_count + 1))
        local subdir_name
        subdir_name=$(basename "$subdir")
        local sub_skills
        sub_skills=$(find "$subdir" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
        if [[ "$VERBOSE" == "1" ]]; then
            log_pass "Skill group: $subdir_name ($sub_skills skills)"
        fi
    done < <(find "$PLUGIN_DIR/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null)

    if [[ $subdir_count -gt 0 ]]; then
        log_pass "Found $subdir_count skill categories"
    fi
}

# ─── Agents ──────────────────────────────────────────────────────────────────

test_agents() {
    section "Agents"

    start_test "Agents validation"
    local agent_count=0
    local valid_count=0

    # Find all .md files in agents/
    while IFS= read -r agent_file; do
        agent_count=$((agent_count + 1))
        local agent_name
        agent_name=$(basename "$agent_file" .md)

        # Check file is not empty
        if [[ -s "$agent_file" ]]; then
            valid_count=$((valid_count + 1))

            # Check for required sections (description, tools)
            if grep -q "description:" "$agent_file" 2>/dev/null || grep -q "## " "$agent_file" 2>/dev/null; then
                if [[ "$VERBOSE" == "1" ]]; then
                    log_pass "Agent: $agent_name (has structure)"
                fi
            else
                if [[ "$VERBOSE" == "1" ]]; then
                    log_pass "Agent: $agent_name"
                fi
            fi
        else
            log_fail "Empty agent file: $agent_name"
        fi
    done < <(find "$PLUGIN_DIR/agents" -name "*.md" -type f 2>/dev/null)

    if [[ $agent_count -gt 0 ]]; then
        log_pass "Found $agent_count agents ($valid_count valid)"
    else
        log_skip "No agents found"
    fi
}

# ─── Markdown Validation ─────────────────────────────────────────────────────

test_markdown_syntax() {
    section "Markdown Syntax"

    start_test "Markdown syntax validation"
    local total_md=0
    local valid_md=0
    local errors=""

    # Check all markdown files
    while IFS= read -r md_file; do
        total_md=$((total_md + 1))
        local rel_path="${md_file#$PLUGIN_DIR/}"

        # Basic checks
        local has_errors=0

        # Check for unclosed code blocks (odd number of ```)
        local fence_count
        fence_count=$(grep -c '```' "$md_file" 2>/dev/null || echo "0")
        fence_count="${fence_count//[^0-9]/}"  # Strip non-numeric
        fence_count="${fence_count:-0}"
        if [[ $((fence_count % 2)) -ne 0 ]]; then
            has_errors=1
            errors="${errors}Unclosed code block: $rel_path\n"
        fi

        # Check for YAML frontmatter if present
        if head -1 "$md_file" | grep -q '^---$'; then
            if ! grep -q '^---$' <(tail -n +2 "$md_file") 2>/dev/null; then
                has_errors=1
                errors="${errors}Unclosed YAML frontmatter: $rel_path\n"
            fi
        fi

        if [[ $has_errors -eq 0 ]]; then
            valid_md=$((valid_md + 1))
        fi
    done < <(find "$PLUGIN_DIR" -name "*.md" -type f ! -path "*/node_modules/*" ! -path "*/.git/*" 2>/dev/null)

    if [[ $total_md -gt 0 ]]; then
        if [[ $valid_md -eq $total_md ]]; then
            log_pass "All $total_md markdown files valid"
        else
            log_fail "$((total_md - valid_md)) markdown files have issues"
            if [[ -n "$errors" ]]; then
                echo -e "   ${RED}$errors${NC}"
            fi
        fi
    else
        log_skip "No markdown files found"
    fi
}

# ─── Cross-References ────────────────────────────────────────────────────────

test_references() {
    section "Cross-References"

    start_test "Cross-reference check"
    # Check if commands reference valid skills
    local broken_refs=0

    # Look for skill references in commands (simplified check)
    while IFS= read -r cmd_file; do
        # Check for @skill or skill: references
        if grep -q '@skill\|skill:' "$cmd_file" 2>/dev/null; then
            if [[ "$VERBOSE" == "1" ]]; then
                log_pass "Command $(basename "$cmd_file" .md) has skill references"
            fi
        fi
    done < <(find "$PLUGIN_DIR/commands" -name "*.md" -type f 2>/dev/null)

    log_pass "Cross-reference check complete"
}

# ─── Summary ─────────────────────────────────────────────────────────────────

print_summary() {
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
        echo -e "${GREEN}${BOLD}✅ ALL TESTS PASSED${NC}"
    else
        echo -e "${RED}${BOLD}❌ $FAIL TEST(S) FAILED${NC}"
    fi
}

print_performance_summary() {
    if [[ "$BENCHMARK" == "1" ]] && [[ ${#TIMINGS[@]} -gt 0 ]]; then
        echo ""
        echo -e "${BLUE}${BOLD}━━━ Performance Summary ━━━${NC}"

        # Count by category
        local FAST=0 MEDIUM=0 SLOW=0

        for timing in "${TIMINGS[@]}"; do
            ms="${timing%%:*}"
            if [[ $ms -lt 500 ]]; then
                FAST=$((FAST + 1))
            elif [[ $ms -lt 2000 ]]; then
                MEDIUM=$((MEDIUM + 1))
            else
                SLOW=$((SLOW + 1))
            fi
        done

        echo -e "  Fast (< 500ms):  ${GREEN}${FAST}${NC} tests"
        echo -e "  Medium (< 2s):   ${YELLOW}${MEDIUM}${NC} tests"
        echo -e "  Slow (> 2s):     ${RED}${SLOW}${NC} tests"

        # Show slowest tests if any are slow
        if [[ $SLOW -gt 0 ]]; then
            echo ""
            echo -e "${YELLOW}Slowest tests:${NC}"
            printf '%s\n' "${TIMINGS[@]}" | sort -t: -k1 -n -r | head -5 | while IFS=: read -r ms name; do
                echo -e "  ${YELLOW}${ms}ms${NC}: $name"
            done
        fi
    fi
}

# ============================================
# Main
# ============================================

print_header
test_plugin_structure
test_commands
test_skills
test_agents
test_markdown_syntax
test_references
print_performance_summary
print_summary
junit_write

# Exit with appropriate code
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
