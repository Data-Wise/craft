#!/bin/bash
# health-check.sh - Validate tool functionality
# Part of Phase 4: Advanced Features (v1.26.0)
# Usage: source scripts/health-check.sh

set -euo pipefail

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Debug mode
DEBUG=${DEBUG:-0}

debug_log() {
    if [ "$DEBUG" = "1" ]; then
        echo -e "${CYAN}[DEBUG]${NC} $*" >&2
    fi
}

#
# Run health check for a specific tool
#
# Args:
#   $1 - tool_name (e.g., "asciinema")
#   $2 - check_cmd (command to verify tool health)
#   $3 - expected_exit (expected exit code, defaults to 0)
#
# Returns:
#   JSON object with health status
#   Exit code: 0 if health check passes, 1 if fails
#
run_health_check() {
    local tool_name="$1"
    local check_cmd="$2"
    local expected_exit="${3:-0}"

    debug_log "Running health check for $tool_name: $check_cmd"

    if [ -z "$check_cmd" ]; then
        # No health check specified
        echo '{"status": "ok", "message": "No health check required"}'
        return 0
    fi

    # Execute health check command and capture exit code
    local actual_exit
    eval "$check_cmd" &> /dev/null
    actual_exit=$?

    debug_log "Health check exit code for $tool_name: $actual_exit (expected: $expected_exit)"

    # Compare exit codes
    if [ "$actual_exit" -eq "$expected_exit" ]; then
        # Health check passed
        echo "{\"status\": \"ok\", \"message\": \"Health check passed\", \"exit_code\": $actual_exit}"
        return 0
    else
        # Health check failed - exit code mismatch
        echo "{\"status\": \"broken\", \"message\": \"Exit code mismatch\", \"expected\": $expected_exit, \"actual\": $actual_exit}"
        return 1
    fi
}

#
# Health check for asciinema
#
# Returns:
#   JSON object with health status
#
health_check_asciinema() {
    debug_log "Checking asciinema health..."

    if ! command -v asciinema &> /dev/null; then
        echo '{"status": "broken", "message": "asciinema not found in PATH"}'
        return 1
    fi

    run_health_check "asciinema" "asciinema --help" 0
}

#
# Health check for agg
#
# Returns:
#   JSON object with health status
#
health_check_agg() {
    debug_log "Checking agg health..."

    if ! command -v agg &> /dev/null; then
        echo '{"status": "broken", "message": "agg not found in PATH"}'
        return 1
    fi

    run_health_check "agg" "agg --help" 0
}

#
# Health check for gifsicle
#
# Returns:
#   JSON object with health status
#
health_check_gifsicle() {
    debug_log "Checking gifsicle health..."

    if ! command -v gifsicle &> /dev/null; then
        echo '{"status": "broken", "message": "gifsicle not found in PATH"}'
        return 1
    fi

    run_health_check "gifsicle" "gifsicle --help" 0
}

#
# Health check for vhs
#
# Returns:
#   JSON object with health status
#
health_check_vhs() {
    debug_log "Checking vhs health..."

    if ! command -v vhs &> /dev/null; then
        echo '{"status": "broken", "message": "vhs not found in PATH"}'
        return 1
    fi

    run_health_check "vhs" "vhs --help" 0
}

#
# Health check for fswatch
#
# Returns:
#   JSON object with health status
#
health_check_fswatch() {
    debug_log "Checking fswatch health..."

    if ! command -v fswatch &> /dev/null; then
        echo '{"status": "broken", "message": "fswatch not found in PATH"}'
        return 1
    fi

    run_health_check "fswatch" "fswatch --help" 0
}

#
# Validate all dependencies required by a specific method
#
# Args:
#   $1 - method ("asciinema", "vhs", or "all")
#   $2 - deps_json (optional, dependency specifications from frontmatter)
#
# Returns:
#   JSON object with health status for each tool
#   {
#     "asciinema": {"status": "ok", ...},
#     "agg": {"status": "broken", ...}
#   }
#
validate_all_health() {
    local method="${1:-asciinema}"
    local deps_json="${2:-}"

    debug_log "Validating all health checks for method: $method"

    # Initialize results object
    local results='{'
    local first=true

    # Define tools by method
    local asciinema_tools=("asciinema" "agg" "gifsicle")
    local vhs_tools=("vhs" "gifsicle")
    local all_tools=("asciinema" "agg" "gifsicle" "vhs" "fswatch")

    # Select tools based on method
    local tools_to_check=()
    case "$method" in
        asciinema)
            tools_to_check=("${asciinema_tools[@]}")
            ;;
        vhs)
            tools_to_check=("${vhs_tools[@]}")
            ;;
        all)
            tools_to_check=("${all_tools[@]}")
            ;;
        *)
            echo '{"error": "Invalid method. Use asciinema, vhs, or all"}' >&2
            return 1
            ;;
    esac

    # Run health check for each tool
    for tool in "${tools_to_check[@]}"; do
        debug_log "Running health check for: $tool"

        # Get health check result
        local health_result
        case "$tool" in
            asciinema)
                health_result=$(health_check_asciinema || true)
                ;;
            agg)
                health_result=$(health_check_agg || true)
                ;;
            gifsicle)
                health_result=$(health_check_gifsicle || true)
                ;;
            vhs)
                health_result=$(health_check_vhs || true)
                ;;
            fswatch)
                health_result=$(health_check_fswatch || true)
                ;;
            *)
                health_result='{"status": "unknown", "message": "Unknown tool"}'
                ;;
        esac

        # Add to results (avoiding leading comma)
        if [ "$first" = true ]; then
            results="${results}\"${tool}\": ${health_result}"
            first=false
        else
            results="${results}, \"${tool}\": ${health_result}"
        fi
    done

    # Close JSON object
    results="${results}}"

    # Output results
    echo "$results"

    # Determine exit code: 0 if all ok, 1 if any broken
    local all_ok=true
    echo "$results" | jq -r '.[] | .status' 2>/dev/null | while read -r status; do
        if [ "$status" = "broken" ]; then
            all_ok=false
        fi
    done

    # Note: Exit code in subshell doesn't affect parent, but we return success here
    # Caller should parse JSON to determine failure
    return 0
}

#
# Parse health checks from tool specification JSON
#
# Args:
#   $1 - tool_name
#   $2 - tool_spec (JSON)
#
# Returns:
#   JSON with health check command and expected exit code
#
parse_health_spec() {
    local tool_name="$1"
    local tool_spec="$2"

    echo "$tool_spec" | python3 <<'PYTHON'
import sys, json

try:
    spec = json.load(sys.stdin)
    health = spec.get('health', {})
    check_cmd = health.get('check_cmd', '')
    expect_exit = health.get('expect_exit', 0)

    result = {
        'check_cmd': check_cmd,
        'expect_exit': expect_exit
    }
    print(json.dumps(result))
except:
    print('{"check_cmd": "", "expect_exit": 0}')
PYTHON
}

#
# Generate comprehensive health report
#
# Returns:
#   Formatted health report with status for all tools
#
generate_health_report() {
    debug_log "Generating comprehensive health report..."

    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║             TOOL HEALTH CHECK REPORT                       ║"
    echo "╠════════════════════════════════════════════════════════════╣"

    # Check each tool with verbose output
    local all_ok=true

    # Asciinema
    echo "│ asciinema: $(check_tool_health_verbose asciinema)"
    if [ $? -ne 0 ]; then all_ok=false; fi

    # Agg
    echo "│ agg:       $(check_tool_health_verbose agg)"
    if [ $? -ne 0 ]; then all_ok=false; fi

    # Gifsicle
    echo "│ gifsicle:  $(check_tool_health_verbose gifsicle)"
    if [ $? -ne 0 ]; then all_ok=false; fi

    # VHS (optional)
    echo "│ vhs:       $(check_tool_health_verbose vhs) (optional)"
    # Don't mark all_ok=false for optional tools

    # FSWatch (optional)
    echo "│ fswatch:   $(check_tool_health_verbose fswatch) (optional)"
    # Don't mark all_ok=false for optional tools

    echo "╠════════════════════════════════════════════════════════════╣"

    if [ "$all_ok" = true ]; then
        echo "║ ${GREEN}✅ All required tools are healthy${NC}                 ║"
    else
        echo "║ ${RED}❌ Some required tools are broken${NC}                  ║"
    fi

    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""

    [ "$all_ok" = true ]
}

#
# Helper: Check and report health status for a tool
#
# Args:
#   $1 - tool_name
#
# Returns:
#   Formatted status string
#
check_tool_health_verbose() {
    local tool="$1"

    if ! command -v "$tool" &> /dev/null; then
        echo -e "${RED}❌ NOT INSTALLED${NC}"
        return 1
    fi

    # Run appropriate health check
    local health_result
    case "$tool" in
        asciinema)
            health_result=$(health_check_asciinema 2>/dev/null || echo '{"status": "broken"}')
            ;;
        agg)
            health_result=$(health_check_agg 2>/dev/null || echo '{"status": "broken"}')
            ;;
        gifsicle)
            health_result=$(health_check_gifsicle 2>/dev/null || echo '{"status": "broken"}')
            ;;
        vhs)
            health_result=$(health_check_vhs 2>/dev/null || echo '{"status": "broken"}')
            ;;
        fswatch)
            health_result=$(health_check_fswatch 2>/dev/null || echo '{"status": "broken"}')
            ;;
        *)
            echo -e "${YELLOW}❓ UNKNOWN${NC}"
            return 1
            ;;
    esac

    # Parse status
    local status
    status=$(echo "$health_result" | jq -r '.status' 2>/dev/null || echo "unknown")

    case "$status" in
        ok)
            echo -e "${GREEN}✅ OK${NC}"
            return 0
            ;;
        broken)
            echo -e "${RED}❌ BROKEN${NC}"
            return 1
            ;;
        *)
            echo -e "${YELLOW}❓ UNKNOWN${NC}"
            return 1
            ;;
    esac
}

# Main execution when script is run directly
if [[ -n "${BASH_SOURCE[0]:-}" && "${BASH_SOURCE[0]}" == "${0}" ]]; then
    command="${1:-all}"

    case "$command" in
        asciinema)
            health_check_asciinema
            ;;

        agg)
            health_check_agg
            ;;

        gifsicle)
            health_check_gifsicle
            ;;

        vhs)
            health_check_vhs
            ;;

        fswatch)
            health_check_fswatch
            ;;

        validate)
            method="${2:-all}"
            validate_all_health "$method"
            ;;

        report)
            generate_health_report
            ;;

        all)
            # Run all health checks and display report
            generate_health_report
            exit $?
            ;;

        *)
            echo "Usage: $0 {asciinema|agg|gifsicle|vhs|fswatch|validate|report|all} [method]"
            echo ""
            echo "Commands:"
            echo "  asciinema     - Check asciinema health"
            echo "  agg           - Check agg health"
            echo "  gifsicle      - Check gifsicle health"
            echo "  vhs           - Check vhs health"
            echo "  fswatch       - Check fswatch health"
            echo "  validate      - Validate all health checks for method (asciinema|vhs|all)"
            echo "  report        - Generate comprehensive health report"
            echo "  all           - Run all checks and display report (default)"
            echo ""
            echo "Examples:"
            echo "  $0 asciinema"
            echo "  $0 validate asciinema"
            echo "  $0 validate all"
            echo "  $0 report"
            exit 1
            ;;
    esac
fi
