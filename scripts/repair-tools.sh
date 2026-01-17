#!/usr/bin/env bash
# repair-tools.sh - Tool repair and reinstallation utility
# Part of Phase 4: Advanced Features (v1.26.0) - Wave 2: Tool Repair
#
# Purpose: Detects broken/outdated tools and repairs them using existing
#          installer framework. Uses health-check.sh and version-check.sh
#          to identify repair candidates, then reinstalls via installer.sh
#
# Usage:
#   # Repair single tool
#   ./scripts/repair-tools.sh repair asciinema asciinema
#   ./scripts/repair-tools.sh repair agg asciinema --json
#
#   # Detect candidates for repair
#   ./scripts/repair-tools.sh detect asciinema
#   ./scripts/repair-tools.sh detect vhs --json
#
#   # Repair all broken/outdated tools
#   ./scripts/repair-tools.sh repair-all asciinema
#   ./scripts/repair-tools.sh repair-all asciinema --auto-confirm --json
#
# Exit Codes:
#   0: All repairs successful or no repairs needed
#   1: Some repairs failed
#   2: All repairs failed
#   3: Missing required dependencies (health-check.sh, installer.sh, etc.)

set -euo pipefail

# ============================================================================
# Configuration and Setup
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HEALTH_CHECK="$SCRIPT_DIR/health-check.sh"
VERSION_CHECK="$SCRIPT_DIR/version-check.sh"
TOOL_DETECTOR="$SCRIPT_DIR/tool-detector.sh"
DEPENDENCY_MANAGER="$SCRIPT_DIR/dependency-manager.sh"

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Debug mode
DEBUG=${DEBUG:-0}

# Global flags
JSON_OUTPUT=0
AUTO_CONFIRM=0

debug_log() {
    if [ "$DEBUG" = "1" ]; then
        echo -e "${CYAN}[DEBUG]${NC} $*" >&2
    fi
}

# ============================================================================
# Dependency Verification
# ============================================================================

check_dependencies() {
    debug_log "Checking dependencies..."

    local missing_deps=0

    # Check if required scripts exist
    for script in "$HEALTH_CHECK" "$VERSION_CHECK" "$TOOL_DETECTOR" "$DEPENDENCY_MANAGER"; do
        if [ ! -f "$script" ]; then
            echo -e "${RED}✗ Missing required script: $script${NC}" >&2
            missing_deps=1
        elif [ ! -x "$script" ]; then
            chmod +x "$script"
            debug_log "Made executable: $script"
        fi
    done

    if [ "$missing_deps" = "1" ]; then
        echo -e "${RED}Error: Missing required dependencies for Phase 4 Wave 1${NC}" >&2
        echo "Please ensure health-check.sh, version-check.sh, and tool-detector.sh exist" >&2
        return 3
    fi

    debug_log "All dependencies verified"
    return 0
}

# ============================================================================
# Tool Specification Retrieval
# ============================================================================

get_tool_spec() {
    local tool_name="$1"

    debug_log "Getting tool spec for: $tool_name"

    # Parse frontmatter and extract spec for this tool
    source "$DEPENDENCY_MANAGER"
    local all_deps
    all_deps=$(parse_frontmatter 2>/dev/null || echo "{}")

    # Extract specific tool spec from JSON
    echo "$all_deps" | python3 -c "
import sys, json
try:
    all_deps = json.load(sys.stdin)
    tool_spec = all_deps.get('$tool_name', {})
    print(json.dumps(tool_spec))
except:
    print('{}')
"
}

# ============================================================================
# Health and Version Detection
# ============================================================================

check_tool_health() {
    local tool_name="$1"
    local tool_spec="$2"

    debug_log "Checking health for: $tool_name"

    # Extract health check command from tool spec
    local health_check_cmd
    health_check_cmd=$(echo "$tool_spec" | python3 -c "
import sys, json
try:
    spec = json.load(sys.stdin)
    health = spec.get('health', {})
    cmd = health.get('check_cmd', '')
    print(cmd)
except:
    print('')
" 2>/dev/null || echo "")

    if [ -z "$health_check_cmd" ]; then
        debug_log "No health check command for $tool_name"
        echo "ok"
        return 0
    fi

    # Run health check
    source "$HEALTH_CHECK"
    local health_result
    health_result=$(eval "$health_check_cmd" &>/dev/null && echo "ok" || echo "broken")

    echo "$health_result"
}

check_tool_version() {
    local tool_name="$1"
    local tool_spec="$2"

    debug_log "Checking version for: $tool_name"

    # Extract version check command
    local version_check_cmd
    version_check_cmd=$(echo "$tool_spec" | python3 -c "
import sys, json
try:
    spec = json.load(sys.stdin)
    version = spec.get('version', {})
    cmd = version.get('check_cmd', '')
    print(cmd)
except:
    print('')
" 2>/dev/null || echo "")

    if [ -z "$version_check_cmd" ]; then
        debug_log "No version check command for $tool_name"
        echo "unknown"
        return 0
    fi

    # Get current version
    source "$VERSION_CHECK"
    local current_version
    current_version=$(extract_version "$tool_name" "$version_check_cmd" 2>/dev/null || echo "unknown")

    # Get minimum required version
    local min_version
    min_version=$(echo "$tool_spec" | python3 -c "
import sys, json
try:
    spec = json.load(sys.stdin)
    version = spec.get('version', {})
    min_ver = version.get('min', '')
    print(min_ver)
except:
    print('')
" 2>/dev/null || echo "")

    if [ -z "$min_version" ]; then
        echo "$current_version"
        return 0
    fi

    # Compare versions
    source "$VERSION_CHECK"
    local comparison
    comparison=$(compare_versions "$current_version" "$min_version" 2>/dev/null || echo "-1")

    if [ "$comparison" -lt 0 ]; then
        echo "outdated:$current_version:$min_version"
    else
        echo "$current_version"
    fi
}

# ============================================================================
# Repair Detection
# ============================================================================

detect_repair_candidates() {
    local method="$1"
    local json_mode="${2:-0}"

    debug_log "Detecting repair candidates for method: $method"

    # Parse all tools
    source "$DEPENDENCY_MANAGER"
    local all_deps
    all_deps=$(parse_frontmatter 2>/dev/null || echo "{}")

    local candidates_json="[]"
    local has_candidates=0

    # Iterate through all tools
    echo "$all_deps" | python3 -c "
import sys, json
try:
    all_deps = json.load(sys.stdin)
    tools = list(all_deps.keys())
    print('\n'.join(tools))
except:
    pass
" | while read -r tool_name; do
        [ -z "$tool_name" ] && continue

        # Get tool spec
        local tool_spec
        tool_spec=$(get_tool_spec "$tool_name")

        # Check if tool is required for this method
        local is_required_for_method
        is_required_for_method=$(echo "$tool_spec" | python3 -c "
import sys, json
try:
    spec = json.load(sys.stdin)
    methods = spec.get('methods', [])
    print('yes' if '$method' in methods else 'no')
except:
    print('no')
" 2>/dev/null || echo "no")

        if [ "$is_required_for_method" != "yes" ]; then
            debug_log "Tool $tool_name not required for method $method, skipping"
            continue
        fi

        # Check if tool is installed
        if ! command -v "$tool_name" &>/dev/null; then
            debug_log "$tool_name not installed"
            echo "{\"tool\": \"$tool_name\", \"status\": \"not_installed\", \"reason\": \"Tool not found in PATH\"}"
            has_candidates=1
            continue
        fi

        # Check health
        local health
        health=$(check_tool_health "$tool_name" "$tool_spec")

        if [ "$health" = "broken" ]; then
            debug_log "$tool_name is broken"
            echo "{\"tool\": \"$tool_name\", \"status\": \"broken\", \"reason\": \"Health check failed\"}"
            has_candidates=1
            continue
        fi

        # Check version
        local version_status
        version_status=$(check_tool_version "$tool_name" "$tool_spec")

        if [[ "$version_status" == outdated:* ]]; then
            debug_log "$tool_name is outdated: $version_status"
            echo "{\"tool\": \"$tool_name\", \"status\": \"outdated\", \"reason\": \"$version_status\"}"
            has_candidates=1
            continue
        fi

        debug_log "$tool_name is healthy"
    done

    if [ "$has_candidates" = "0" ] && [ "$json_mode" = "0" ]; then
        echo -e "${GREEN}✓ No repair candidates found${NC}"
    fi
}

# ============================================================================
# Tool Repair
# ============================================================================

repair_tool() {
    local tool_name="$1"
    local method="$2"
    local json_mode="${3:-0}"

    debug_log "Starting repair for tool: $tool_name (method: $method)"

    # Get tool spec
    local tool_spec
    tool_spec=$(get_tool_spec "$tool_name")

    if [ -z "$tool_spec" ] || [ "$tool_spec" = "{}" ]; then
        if [ "$json_mode" = "1" ]; then
            echo "{\"tool\": \"$tool_name\", \"method\": \"$method\", \"status\": \"error\", \"message\": \"Tool not found in spec\"}"
        else
            echo -e "${RED}✗ Tool not found in spec: $tool_name${NC}"
        fi
        return 1
    fi

    if [ "$json_mode" = "0" ]; then
        echo -e "${BOLD}🔧 Repairing: $tool_name${NC}"
    fi

    # Check if tool exists
    if ! command -v "$tool_name" &>/dev/null; then
        if [ "$json_mode" = "0" ]; then
            echo -e "  ${YELLOW}├─ Detecting current install: not installed${NC}"
        fi
        # Skip uninstall for non-installed tools
    else
        if [ "$json_mode" = "0" ]; then
            echo -e "  ${YELLOW}├─ Tool is installed${NC}"
        fi
    fi

    # Attempt reinstallation via installer
    if [ "$json_mode" = "0" ]; then
        echo -e "  ${YELLOW}├─ Reinstalling via installer${NC}"
    fi

    # Source and call installer function
    source "$DEPENDENCY_MANAGER"

    # Try to reinstall - for now we'll simulate by reinstalling via brew
    local install_method
    install_method=$(echo "$tool_spec" | python3 -c "
import sys, json
try:
    spec = json.load(sys.stdin)
    install = spec.get('install', {})
    # Prefer brew on macOS
    if 'brew' in install:
        print('brew')
    elif 'cargo' in install:
        print('cargo')
    elif 'binary' in install:
        print('binary')
    else:
        print('unknown')
except:
    print('unknown')
" 2>/dev/null || echo "unknown")

    local reinstall_success=0

    case "$install_method" in
        brew)
            local pkg_name
            pkg_name=$(echo "$tool_spec" | python3 -c "
import sys, json
try:
    spec = json.load(sys.stdin)
    install = spec.get('install', {})
    print(install.get('brew', ''))
except:
    print('')
" 2>/dev/null)

            if [ -n "$pkg_name" ]; then
                if brew install "$pkg_name" &>/dev/null; then
                    reinstall_success=1
                else
                    if [ "$json_mode" = "0" ]; then
                        echo -e "  ${RED}│  (brew install failed, trying update)${NC}"
                    fi
                    brew upgrade "$pkg_name" &>/dev/null && reinstall_success=1
                fi
            fi
            ;;

        cargo)
            local cargo_pkg
            cargo_pkg=$(echo "$tool_spec" | python3 -c "
import sys, json
try:
    spec = json.load(sys.stdin)
    install = spec.get('install', {})
    print(install.get('cargo', ''))
except:
    print('')
" 2>/dev/null)

            if [ -n "$cargo_pkg" ]; then
                if cargo install "$cargo_pkg" &>/dev/null; then
                    reinstall_success=1
                fi
            fi
            ;;
    esac

    if [ "$reinstall_success" = "0" ]; then
        if [ "$json_mode" = "0" ]; then
            echo -e "  ${RED}│  Reinstallation failed${NC}"
            echo -e "  ${RED}└─ Repair: ✗ FAILED${NC}"
        else
            echo "{\"tool\": \"$tool_name\", \"method\": \"$method\", \"status\": \"failed\", \"message\": \"Reinstallation failed\"}"
        fi
        return 1
    fi

    # Validate repair
    if [ "$json_mode" = "0" ]; then
        echo -e "  ${YELLOW}├─ Health check: validating${NC}"
    fi

    local health_after
    health_after=$(check_tool_health "$tool_name" "$tool_spec")

    if [ "$health_after" != "ok" ]; then
        if [ "$json_mode" = "0" ]; then
            echo -e "  ${RED}│  Health check still failing${NC}"
            echo -e "  ${RED}└─ Repair: ✗ FAILED${NC}"
        else
            echo "{\"tool\": \"$tool_name\", \"method\": \"$method\", \"status\": \"failed\", \"message\": \"Health check still failing after repair\"}"
        fi
        return 1
    fi

    # Verify version
    if [ "$json_mode" = "0" ]; then
        echo -e "  ${YELLOW}└─ Version check: validating${NC}"
    fi

    local version_after
    version_after=$(check_tool_version "$tool_name" "$tool_spec")

    if [ "$json_mode" = "0" ]; then
        echo -e "  ${GREEN}  ✅ Version: $version_after${NC}"
        echo -e "${GREEN}✓ Repair successful${NC}"
    else
        # Extract clean version for JSON
        local clean_version
        clean_version=$(echo "$version_after" | cut -d: -f2)
        [ -z "$clean_version" ] && clean_version="$version_after"

        echo "{\"tool\": \"$tool_name\", \"method\": \"$method\", \"status\": \"repaired\", \"health\": \"ok\", \"version\": \"$clean_version\"}"
    fi

    return 0
}

# ============================================================================
# Batch Repair
# ============================================================================

repair_all() {
    local method="$1"
    local auto_confirm="${2:-0}"
    local json_mode="${3:-0}"

    debug_log "Starting batch repair for method: $method"

    # Detect candidates first
    if [ "$json_mode" = "0" ]; then
        echo -e "${BOLD}Detecting repair candidates...${NC}"
    fi

    local candidates
    candidates=$(detect_repair_candidates "$method" 1)

    # Parse candidates and repair
    local failed_count=0
    local success_count=0
    local results_json="[]"

    echo "$candidates" | python3 -c "
import sys, json
candidates_json = sys.stdin.read().strip()
if candidates_json:
    for line in candidates_json.strip().split('\n'):
        if line:
            try:
                print(json.dumps(json.loads(line)))
            except:
                pass
" | while read -r candidate_json; do
        [ -z "$candidate_json" ] && continue

        local tool_name
        tool_name=$(echo "$candidate_json" | python3 -c "
import sys, json
try:
    candidate = json.load(sys.stdin)
    print(candidate.get('tool', ''))
except:
    print('')
")

        [ -z "$tool_name" ] && continue

        if [ "$json_mode" = "0" ] && [ "$auto_confirm" = "0" ]; then
            echo -e "${YELLOW}Candidate: $tool_name${NC}"
            read -p "Repair this tool? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                debug_log "Skipping $tool_name (user declined)"
                continue
            fi
        fi

        # Repair the tool
        if repair_tool "$tool_name" "$method" "$json_mode"; then
            ((success_count++))
        else
            ((failed_count++))
        fi
    done

    # Report results
    if [ "$json_mode" = "0" ]; then
        echo ""
        echo -e "${BOLD}Repair Summary:${NC}"
        echo -e "  ${GREEN}✓ Successful: $success_count${NC}"
        if [ "$failed_count" -gt 0 ]; then
            echo -e "  ${RED}✗ Failed: $failed_count${NC}"
        fi

        if [ "$failed_count" -gt 0 ]; then
            return 1
        fi
    fi

    return 0
}

# ============================================================================
# Help and Usage
# ============================================================================

show_usage() {
    cat <<'EOF'
repair-tools.sh - Tool repair and reinstallation utility

USAGE:
    ./scripts/repair-tools.sh <command> <method> [options]

COMMANDS:
    repair <tool_name> <method>      Repair a specific tool
    detect <method>                  Detect tools needing repair
    repair-all <method>              Repair all candidates for a method

METHODS:
    asciinema                        GIF recording method
    vhs                              Alternative GIF method

OPTIONS:
    --json                           Output results as JSON
    --auto-confirm                   Skip confirmation prompts

EXAMPLES:
    # Repair single tool
    ./scripts/repair-tools.sh repair asciinema asciinema
    ./scripts/repair-tools.sh repair agg asciinema --json

    # Detect candidates
    ./scripts/repair-tools.sh detect asciinema
    ./scripts/repair-tools.sh detect vhs --json

    # Repair all
    ./scripts/repair-tools.sh repair-all asciinema
    ./scripts/repair-tools.sh repair-all asciinema --auto-confirm --json

EXIT CODES:
    0   All repairs successful or no repairs needed
    1   Some repairs failed
    2   All repairs failed
    3   Missing required dependencies

EOF
}

# ============================================================================
# Main Entry Point
# ============================================================================

main() {
    local command="${1:-}"
    local method="${2:-}"
    local arg3="${3:-}"
    local arg4="${4:-}"

    # Check for help
    if [ -z "$command" ] || [ "$command" = "--help" ] || [ "$command" = "-h" ]; then
        show_usage
        exit 0
    fi

    # Parse global options
    for arg in "$arg3" "$arg4"; do
        case "$arg" in
            --json) JSON_OUTPUT=1 ;;
            --auto-confirm) AUTO_CONFIRM=1 ;;
        esac
    done

    # Verify dependencies
    if ! check_dependencies; then
        exit 3
    fi

    # Route to appropriate function
    case "$command" in
        repair)
            if [ -z "$method" ]; then
                echo -e "${RED}Error: tool_name and method required for repair${NC}" >&2
                show_usage
                exit 1
            fi
            repair_tool "$method" "$arg3" "$JSON_OUTPUT"
            exit $?
            ;;
        detect)
            if [ -z "$method" ]; then
                echo -e "${RED}Error: method required for detect${NC}" >&2
                show_usage
                exit 1
            fi
            detect_repair_candidates "$method" "$JSON_OUTPUT"
            exit $?
            ;;
        repair-all)
            if [ -z "$method" ]; then
                echo -e "${RED}Error: method required for repair-all${NC}" >&2
                show_usage
                exit 1
            fi
            repair_all "$method" "$AUTO_CONFIRM" "$JSON_OUTPUT"
            exit $?
            ;;
        *)
            echo -e "${RED}Error: Unknown command: $command${NC}" >&2
            show_usage
            exit 1
            ;;
    esac
}

# Run main function if not being sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
