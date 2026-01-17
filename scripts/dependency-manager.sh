#!/bin/bash
# Dependency Management Orchestrator for Craft Demo
# Part of: feature/demo-dependency-management
# Phase: 1 (Core Dependency Checking)
#
# Purpose: Orchestrates dependency checking by parsing demo.md frontmatter,
#          using tool-detector.sh for detection, and session-cache.sh for performance
#
# Functions:
#   parse_frontmatter() - Extract dependencies from demo.md
#   check_dependencies(method) - Check deps for specific method (asciinema/vhs)
#   check_all_dependencies() - Check all deps regardless of method
#   display_status_table(status_json) - Format status as ASCII table
#   get_install_command(tool_name, install_spec) - Get platform-specific install cmd

set -e

# Source utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/tool-detector.sh"
source "$SCRIPT_DIR/session-cache.sh"

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
BOLD='\033[1m'
NC='\033[0m'

# Demo.md location
DEMO_MD="$SCRIPT_DIR/../commands/docs/demo.md"

# Debug mode
DEBUG=${DEBUG:-0}

debug_log() {
    if [ "$DEBUG" = "1" ]; then
        echo -e "${CYAN}[DEBUG]${NC} $*" >&2
    fi
}

#
# Parse frontmatter from demo.md and extract dependency specifications
#
# Extracts the YAML frontmatter between '---' markers and converts
# the dependencies section into a bash associative array structure.
#
# Returns:
#   Prints dependency specifications as JSON to stdout
#   Exit code 0 on success, 1 on failure
#
parse_frontmatter() {
    if [ ! -f "$DEMO_MD" ]; then
        echo "ERROR: demo.md not found at $DEMO_MD" >&2
        return 1
    fi

    # Extract YAML frontmatter (between first --- and second ---)
    # Then extract just the dependencies section and convert to JSON
    python3 - "$DEMO_MD" <<'PYTHON'
import sys
import yaml
import json

demo_md_path = sys.argv[1]

try:
    with open(demo_md_path, 'r') as f:
        content = f.read()

    # Extract frontmatter between --- markers
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter_yaml = parts[1]
            frontmatter = yaml.safe_load(frontmatter_yaml)

            # Extract dependencies section
            dependencies = frontmatter.get('dependencies', {})

            # Output as JSON
            print(json.dumps(dependencies, indent=2))
        else:
            print("{}", file=sys.stderr)
            sys.exit(1)
    else:
        print("{}", file=sys.stderr)
        sys.exit(1)

except Exception as e:
    print(f"ERROR: Failed to parse frontmatter: {e}", file=sys.stderr)
    print("{}", file=sys.stderr)
    sys.exit(1)
PYTHON
}

#
# Get platform-specific install command for a tool
#
# Args:
#   $1 - tool_name (e.g., "asciinema")
#   $2 - install_spec (JSON with install methods)
#
# Returns:
#   Prints install command to stdout
#
get_install_command() {
    local tool_name="$1"
    local install_spec="$2"

    # Detect platform
    local os_type
    if [[ "$OSTYPE" == "darwin"* ]]; then
        os_type="brew"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            os_type="apt"
        elif command -v yum &> /dev/null; then
            os_type="yum"
        else
            os_type="unknown"
        fi
    else
        os_type="unknown"
    fi

    # Extract install command for this platform
    local install_cmd
    install_cmd=$(echo "$install_spec" | python3 -c "
import sys, json
try:
    spec = json.load(sys.stdin)
    install = spec.get('install', {})

    # Try platform-specific first
    os_type = '$os_type'
    if os_type in install:
        pkg = install[os_type]
        if os_type == 'brew':
            print(f'brew install {pkg}')
        elif os_type == 'apt':
            print(f'sudo apt-get install {pkg}')
        elif os_type == 'yum':
            print(f'sudo yum install {pkg}')
    elif 'cargo' in install:
        pkg = install['cargo']
        print(f'cargo install {pkg}')
    elif 'cargo_git' in install:
        url = install['cargo_git']
        print(f'cargo install --git {url}')
    elif 'binary' in install:
        print('(binary download - see docs)')
    else:
        print('(see documentation)')
except:
    print('(unknown)')
" 2>/dev/null || echo "(unknown)")

    echo "$install_cmd"
}

#
# Check dependencies for a specific method (asciinema or vhs)
#
# Args:
#   $1 - method ("asciinema", "vhs", or "all")
#
# Returns:
#   Prints JSON array with status for each dependency
#   Exit code: 0 if all OK, 1 if any missing/broken
#
check_dependencies() {
    local method="$1"

    debug_log "Checking dependencies for method: $method"

    # Initialize cache if not already done
    if [ -z "$CRAFT_CACHE_DIR" ]; then
        init_cache > /dev/null
    fi

    # Parse dependencies from frontmatter
    local deps_json
    if ! deps_json=$(parse_frontmatter); then
        echo "ERROR: Failed to parse dependencies" >&2
        return 1
    fi

    debug_log "Parsed dependencies JSON"

    # Process each dependency
    local results=()
    local all_ok=true

    # Get list of tool names
    local tool_names
    tool_names=$(echo "$deps_json" | jq -r 'keys[]' 2>/dev/null)

    for tool_name in $tool_names; do
        debug_log "Processing tool: $tool_name"

        # Extract tool spec from deps_json
        local tool_spec
        tool_spec=$(echo "$deps_json" | jq ".\"$tool_name\"" 2>/dev/null)

        # Check if tool is relevant for this method
        local tool_methods
        tool_methods=$(echo "$tool_spec" | jq -r '.methods[]' 2>/dev/null || echo "")

        if [ "$method" != "all" ]; then
            # Filter by method
            if ! echo "$tool_methods" | grep -q "^${method}$"; then
                debug_log "Skipping $tool_name (not used by $method)"
                continue
            fi
        fi

        # Check if tool is required or optional
        local is_required
        is_required=$(echo "$tool_spec" | jq -r '.required' 2>/dev/null || echo "true")

        # Check cache first
        local status_json
        if status_json=$(get_cached_status "$tool_name"); then
            debug_log "Cache hit for $tool_name"
        else
            debug_log "Cache miss for $tool_name, detecting..."
            # Run detection
            status_json=$(detect_tool "$tool_name" "$tool_spec")
            # Store in cache
            store_cache "$tool_name" "$status_json"
        fi

        # Extract status fields
        local installed
        local version
        local version_ok
        local health
        installed=$(echo "$status_json" | jq -r '.installed' 2>/dev/null || echo "false")
        version=$(echo "$status_json" | jq -r '.version' 2>/dev/null || echo "unknown")
        version_ok=$(echo "$status_json" | jq -r '.version_ok' 2>/dev/null || echo "false")
        health=$(echo "$status_json" | jq -r '.health' 2>/dev/null || echo "unknown")

        # Get install command
        local install_cmd
        install_cmd=$(get_install_command "$tool_name" "$tool_spec")

        # Build result object
        local result
        # Handle version_ok which can be boolean or "n/a"
        if [ "$version_ok" = "true" ] || [ "$version_ok" = "false" ]; then
            result=$(jq -n \
                --arg name "$tool_name" \
                --argjson installed "$installed" \
                --arg version "$version" \
                --argjson version_ok "$version_ok" \
                --arg health "$health" \
                --argjson required "$is_required" \
                --arg install "$install_cmd" \
                '{name: $name, installed: $installed, version: $version, version_ok: $version_ok, health: $health, required: $required, install_cmd: $install}')
        else
            # version_ok is "n/a" or other string
            result=$(jq -n \
                --arg name "$tool_name" \
                --argjson installed "$installed" \
                --arg version "$version" \
                --arg version_ok "$version_ok" \
                --arg health "$health" \
                --argjson required "$is_required" \
                --arg install "$install_cmd" \
                '{name: $name, installed: $installed, version: $version, version_ok: $version_ok, health: $health, required: $required, install_cmd: $install}')
        fi

        results+=("$result")

        # Update all_ok status
        if [ "$is_required" = "true" ]; then
            if [ "$installed" != "true" ] || [ "$health" = "broken" ]; then
                all_ok=false
            fi
        fi
    done

    # Combine results into JSON array
    local results_json
    results_json=$(printf '%s\n' "${results[@]}" | jq -s '.')

    # Print results
    echo "$results_json"

    # Return exit code
    if [ "$all_ok" = "true" ]; then
        return 0
    else
        return 1
    fi
}

#
# Check all dependencies regardless of method
#
# Returns:
#   Prints JSON array with status for all dependencies
#   Exit code: 0 if all OK, 1 if any missing/broken
#
check_all_dependencies() {
    check_dependencies "all"
}

#
# Display status table for dependencies
#
# Args:
#   $1 - method (for title)
#   $2 - status_json (JSON array from check_dependencies)
#
# Output:
#   Formatted ASCII table with dependency status
#
display_status_table() {
    local method="$1"
    local status_json="$2"

    # Count tools by status
    local total_count
    local missing_count
    local broken_count
    local optional_count

    total_count=$(echo "$status_json" | jq 'length' 2>/dev/null || echo "0")
    missing_count=$(echo "$status_json" | jq '[.[] | select(.installed == false and .required == true)] | length' 2>/dev/null || echo "0")
    broken_count=$(echo "$status_json" | jq '[.[] | select(.health == "broken" and .required == true)] | length' 2>/dev/null || echo "0")
    optional_count=$(echo "$status_json" | jq '[.[] | select(.required == false)] | length' 2>/dev/null || echo "0")

    # Print header
    echo ""
    echo "┌─────────────────────────────────────────────────────────────┐"
    echo -e "│ 🔍 ${BOLD}DEPENDENCY STATUS: ${method} method${NC}                      │"
    echo "├─────────────────────────────────────────────────────────────┤"
    printf "│ %-12s │ %-10s │ %-8s │ %-7s │ %-15s │\n" "Tool" "Status" "Version" "Health" "Install"
    echo "├──────────────┼────────────┼──────────┼─────────┼─────────────────┤"

    # Print each tool
    echo "$status_json" | jq -r '.[] | @json' | while IFS= read -r tool_json; do
        local name
        local installed
        local version
        local health
        local required
        local install_cmd

        name=$(echo "$tool_json" | jq -r '.name')
        installed=$(echo "$tool_json" | jq -r '.installed')
        version=$(echo "$tool_json" | jq -r '.version')
        health=$(echo "$tool_json" | jq -r '.health')
        required=$(echo "$tool_json" | jq -r '.required')
        install_cmd=$(echo "$tool_json" | jq -r '.install_cmd')

        # Format status
        local status_str
        local health_str
        if [ "$installed" = "true" ]; then
            status_str="${GREEN}✅ OK${NC}"
            if [ "$health" = "ok" ]; then
                health_str="${GREEN}✅ OK${NC}"
            elif [ "$health" = "broken" ]; then
                health_str="${RED}❌ FAIL${NC}"
            else
                health_str="${YELLOW}❓${NC}"
            fi
        else
            if [ "$required" = "true" ]; then
                status_str="${RED}❌ MISSING${NC}"
            else
                status_str="${YELLOW}⚠️  OPTIONAL${NC}"
            fi
            health_str="-"
            version="-"
        fi

        # Truncate install command for display
        local install_display
        if [ "$installed" = "true" ]; then
            install_display="-"
        else
            install_display=$(echo "$install_cmd" | cut -c1-15)
            if [ ${#install_cmd} -gt 15 ]; then
                install_display="${install_display}..."
            fi
        fi

        # Print row with proper color escaping
        # Calculate visible lengths (without ANSI codes)
        local status_visible
        local health_visible
        if [ "$installed" = "true" ]; then
            status_visible="✅ OK"
            if [ "$health" = "ok" ]; then
                health_visible="✅ OK"
            elif [ "$health" = "broken" ]; then
                health_visible="❌ FAIL"
            else
                health_visible="❓"
            fi
        else
            if [ "$required" = "true" ]; then
                status_visible="❌ MISSING"
            else
                status_visible="⚠️  OPTIONAL"
            fi
            health_visible="-"
        fi

        # Print row
        printf "│ %-12s │ " "$name"
        printf "%b" "$status_str"
        printf "%$((10 - ${#status_visible}))s │ %-8s │ " "" "$version"
        printf "%b" "$health_str"
        printf "%$((7 - ${#health_visible}))s │ %-15s │\n" "" "$install_display"
    done

    echo "└──────────────┴────────────┴──────────┴─────────┴─────────────────┘"
    echo ""

    # Print summary
    local issues=$((missing_count + broken_count))
    if [ "$issues" -gt 0 ]; then
        echo -e "${RED}Summary: $missing_count missing, $broken_count broken${NC}"
        echo ""
        echo "Run: /craft:docs:demo --fix"
    else
        echo -e "${GREEN}Summary: All required tools installed and healthy${NC}"
        if [ "$optional_count" -gt 0 ]; then
            echo -e "${YELLOW}Note: $optional_count optional tools not installed${NC}"
        fi
    fi
    echo ""
}

# Main execution when script is run directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    # Parse command line arguments
    command="${1:-check_dependencies}"
    arg1="${2:-asciinema}"

    case "$command" in
        parse_frontmatter)
            parse_frontmatter
            ;;

        check_dependencies)
            method="$arg1"
            check_dependencies "$method"
            exit $?
            ;;

        check_all_dependencies)
            check_all_dependencies
            exit $?
            ;;

        display_status_table)
            method="${arg1:-asciinema}"
            # Check dependencies and display table
            if status_json=$(check_dependencies "$method"); then
                display_status_table "$method" "$status_json"
                exit 0
            else
                display_status_table "$method" "$status_json"
                exit 1
            fi
            ;;

        *)
            echo "Usage: $0 {parse_frontmatter|check_dependencies|check_all_dependencies|display_status_table} [method]"
            echo ""
            echo "Commands:"
            echo "  parse_frontmatter          - Extract dependencies from demo.md"
            echo "  check_dependencies METHOD  - Check deps for method (asciinema|vhs|all)"
            echo "  check_all_dependencies     - Check all deps"
            echo "  display_status_table METHOD - Check and display formatted table"
            echo ""
            echo "Examples:"
            echo "  $0 parse_frontmatter"
            echo "  $0 check_dependencies asciinema"
            echo "  $0 display_status_table asciinema"
            exit 1
            ;;
    esac
fi
