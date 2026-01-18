#!/bin/bash
# Tool Detection Utilities for Craft Demo Dependency Management
# Part of: feature/demo-dependency-management
# Phase: 1 (Core Dependency Checking)
#
# Purpose: Detect tool availability, version, and health status
# Usage: Source this file to access detection functions
#
# Functions:
#   detect_tool(tool_name, tool_spec_json)     - Main detection routine
#   extract_version(tool_name, check_cmd)      - Extract version string
#   compare_version(current, minimum)          - Compare version strings
#   run_health_check(check_cmd, expected_exit) - Validate tool health

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Debug mode (set DEBUG=1 to enable verbose output)
DEBUG=${DEBUG:-0}

debug_log() {
    if [ "$DEBUG" = "1" ]; then
        echo -e "${CYAN}[DEBUG]${NC} $*" >&2
    fi
}

# Main tool detection function
# Args:
#   $1 - tool_name (e.g., "asciinema")
#   $2 - tool_spec (JSON string with version/health requirements)
# Returns:
#   JSON string with detection results
detect_tool() {
    local tool_name="$1"
    local tool_spec="$2"

    debug_log "Detecting tool: $tool_name"

    # 1. Check if command exists in PATH
    if ! command -v "$tool_name" &> /dev/null; then
        debug_log "Tool not found in PATH: $tool_name"
        echo '{"installed": false, "version": null, "version_ok": false, "health": "n/a", "path": null}'
        return 0
    fi

    local tool_path
    tool_path=$(command -v "$tool_name")
    debug_log "Tool found at: $tool_path"

    # 2. Extract version (if check_cmd provided)
    local version="unknown"
    local version_ok=false

    if [ -n "$tool_spec" ] && [ "$tool_spec" != "{}" ]; then
        # Extract version check command from JSON spec (if exists)
        local version_check_cmd
        version_check_cmd=$(echo "$tool_spec" | python3 -c "
import sys, json
try:
    spec = json.load(sys.stdin)
    cmd = spec.get('version', {}).get('check_cmd', '')
    print(cmd)
except:
    print('')
" 2>/dev/null || echo "")

        if [ -n "$version_check_cmd" ]; then
            debug_log "Running version check: $version_check_cmd"
            version=$(extract_version "$tool_name" "$version_check_cmd")
            debug_log "Extracted version: $version"

            # Compare with minimum version (if specified)
            local min_version
            min_version=$(echo "$tool_spec" | python3 -c "
import sys, json
try:
    spec = json.load(sys.stdin)
    min_ver = spec.get('version', {}).get('min', '')
    print(min_ver)
except:
    print('')
" 2>/dev/null || echo "")

            if [ -n "$min_version" ] && [ "$version" != "unparseable" ]; then
                debug_log "Comparing version $version against minimum $min_version"
                if compare_version "$version" "$min_version"; then
                    version_ok=true
                    debug_log "Version check passed"
                else
                    version_ok=false
                    debug_log "Version check failed"
                fi
            else
                # No minimum version specified or version unparseable
                version_ok="n/a"
            fi
        fi
    fi

    # 3. Run health check (if check_cmd provided)
    local health="unknown"

    if [ -n "$tool_spec" ] && [ "$tool_spec" != "{}" ]; then
        local health_check_cmd
        local expected_exit

        health_check_cmd=$(echo "$tool_spec" | python3 -c "
import sys, json
try:
    spec = json.load(sys.stdin)
    cmd = spec.get('health', {}).get('check_cmd', '')
    print(cmd)
except:
    print('')
" 2>/dev/null || echo "")

        expected_exit=$(echo "$tool_spec" | python3 -c "
import sys, json
try:
    spec = json.load(sys.stdin)
    exit_code = spec.get('health', {}).get('expect_exit', 0)
    print(exit_code)
except:
    print('0')
" 2>/dev/null || echo "0")

        if [ -n "$health_check_cmd" ]; then
            debug_log "Running health check: $health_check_cmd (expect exit: $expected_exit)"
            if run_health_check "$health_check_cmd" "$expected_exit"; then
                health="ok"
                debug_log "Health check passed"
            else
                health="broken"
                debug_log "Health check failed"
            fi
        else
            health="n/a"
        fi
    fi

    # 4. Return structured result as JSON
    cat <<EOF
{"installed": true, "version": "$version", "version_ok": $version_ok, "health": "$health", "path": "$tool_path"}
EOF
}

# Extract version string from tool
# Args:
#   $1 - tool_name (for context)
#   $2 - check_cmd (command to extract version)
# Returns:
#   Version string or "unparseable"
extract_version() {
    local tool_name="$1"
    local check_cmd="$2"

    if [ -z "$check_cmd" ]; then
        echo "unknown"
        return 0
    fi

    # Run version check command with error handling
    local version_output
    if version_output=$(eval "$check_cmd" 2>&1); then
        # Check if output is non-empty
        if [ -n "$version_output" ]; then
            echo "$version_output"
        else
            echo "unparseable"
        fi
    else
        echo "unparseable"
    fi
}

# Compare version strings using sort -V
# Args:
#   $1 - current version
#   $2 - minimum required version
# Returns:
#   0 (true) if current >= minimum, 1 (false) otherwise
compare_version() {
    local current="$1"
    local minimum="$2"

    # Handle unparseable versions
    if [ "$current" = "unparseable" ] || [ "$current" = "unknown" ]; then
        return 1  # Cannot verify, assume failure
    fi

    if [ -z "$minimum" ]; then
        return 0  # No minimum specified, any version is OK
    fi

    # Use sort -V to compare versions
    # If current is greater or equal, it will be sorted last
    local sorted_first
    sorted_first=$(printf "%s\n%s\n" "$minimum" "$current" | sort -V | head -n1)

    if [ "$sorted_first" = "$minimum" ]; then
        return 0  # current >= minimum
    else
        return 1  # current < minimum
    fi
}

# Run health check command
# Args:
#   $1 - check_cmd (command to run)
#   $2 - expected_exit (expected exit code)
# Returns:
#   0 (true) if exit code matches expected, 1 (false) otherwise
run_health_check() {
    local check_cmd="$1"
    local expected_exit="${2:-0}"

    if [ -z "$check_cmd" ]; then
        return 0  # No health check specified, assume healthy
    fi

    # Run health check command and capture exit code
    local actual_exit
    eval "$check_cmd" &> /dev/null
    actual_exit=$?

    debug_log "Health check exit code: $actual_exit (expected: $expected_exit)"

    if [ "$actual_exit" -eq "$expected_exit" ]; then
        return 0  # Health check passed
    else
        return 1  # Health check failed
    fi
}

# If script is run directly (not sourced), run tests
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    echo -e "${CYAN}Tool Detector Test Suite${NC}"
    echo "========================"
    echo ""

    # Test 1: Detect existing tool (bash)
    echo -e "${CYAN}Test 1: Detect bash${NC}"
    bash_spec='{"version": {"min": "5.0.0", "check_cmd": "bash --version | grep -oE \"[0-9.]+\" | head -1"}, "health": {"check_cmd": "bash --help", "expect_exit": 0}}'
    result=$(detect_tool "bash" "$bash_spec")
    echo "Result: $result"
    echo ""

    # Test 2: Detect missing tool
    echo -e "${CYAN}Test 2: Detect nonexistent tool${NC}"
    result=$(detect_tool "nonexistent-tool-12345" "{}")
    echo "Result: $result"
    echo ""

    # Test 3: Detect tool with no spec
    echo -e "${CYAN}Test 3: Detect ls (no spec)${NC}"
    result=$(detect_tool "ls" "{}")
    echo "Result: $result"
    echo ""

    # Test 4: Version comparison
    echo -e "${CYAN}Test 4: Version comparison${NC}"
    if compare_version "2.3.0" "2.0.0"; then
        echo -e "${GREEN}✓ 2.3.0 >= 2.0.0${NC}"
    else
        echo -e "${RED}✗ 2.3.0 >= 2.0.0 (failed)${NC}"
    fi

    if compare_version "1.9.0" "2.0.0"; then
        echo -e "${RED}✗ 1.9.0 >= 2.0.0 (should fail)${NC}"
    else
        echo -e "${GREEN}✓ 1.9.0 < 2.0.0${NC}"
    fi
    echo ""

    # Test 5: Health check
    echo -e "${CYAN}Test 5: Health check${NC}"
    if run_health_check "bash --help" 0; then
        echo -e "${GREEN}✓ bash --help (exit 0)${NC}"
    else
        echo -e "${RED}✗ bash --help failed${NC}"
    fi

    if run_health_check "bash --invalid-flag-xyz" 0; then
        echo -e "${RED}✗ bash --invalid-flag-xyz should fail${NC}"
    else
        echo -e "${GREEN}✓ bash --invalid-flag-xyz (exit != 0)${NC}"
    fi

    echo ""
    echo -e "${GREEN}All tests complete!${NC}"
fi
