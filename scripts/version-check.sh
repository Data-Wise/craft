#!/bin/bash
# version-check.sh - Version validation and comparison
# Part of Phase 4: Advanced Features (v1.26.0)
# Usage: source scripts/version-check.sh
#
# Purpose: Provides semantic version parsing, comparison, and validation
#          for dependency management with robust format handling
#
# Functions:
#   extract_version(tool_name, version_cmd)        - Extract version from tool output
#   parse_version(version_string)                  - Parse version into components
#   compare_versions(version1, version2)           - Semantic version comparison
#   check_version_requirement(tool, current, min)  - Validate version requirement
#   validate_all_versions(method)                  - Check all tools for requirements

set -euo pipefail

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Debug mode (set DEBUG=1 to enable verbose output)
DEBUG=${DEBUG:-0}

debug_log() {
    if [ "$DEBUG" = "1" ]; then
        echo -e "${CYAN}[DEBUG]${NC} $*" >&2
    fi
}

#
# Extract version string from tool output
#
# Executes a version command and parses the output to extract a clean
# version string. Handles multiple common formats:
#   - "tool 1.2.3"
#   - "tool version 1.2.3"
#   - "v1.2.3"
#   - "Tool Name 1.2.3"
#   - "version 1.2.3"
#
# Arguments:
#   $1 - tool_name (e.g., "asciinema", for error messages)
#   $2 - version_cmd (e.g., "asciinema --version")
#
# Returns:
#   Clean version string or "unknown" if parsing fails
#   Exit code 0 always
#
extract_version() {
    local tool_name="$1"
    local version_cmd="$2"

    debug_log "Extracting version for $tool_name with: $version_cmd"

    # Execute version command, capture output, suppress errors
    local output
    output=$(eval "$version_cmd" 2>/dev/null || echo "")

    if [ -z "$output" ]; then
        debug_log "No output from version command"
        echo "unknown"
        return 0
    fi

    debug_log "Raw version output: $output"

    # Try multiple parsing patterns (most specific to least specific)

    # Pattern 1: "word v?X.Y.Z" or "word X.Y.Z"
    # Matches: "asciinema 2.3.0", "agg 1.4.3", "vhs version 0.7.2"
    local version
    version=$(echo "$output" | grep -oE 'v?[0-9]+\.[0-9]+(\.[0-9]+)?(-[a-zA-Z0-9\.]+)?(\+[a-zA-Z0-9\.]+)?' | head -1)

    if [ -n "$version" ]; then
        # Clean up: remove leading 'v' if present
        version="${version#v}"
        debug_log "Extracted version: $version"
        echo "$version"
        return 0
    fi

    # Pattern 2: Just a version number with optional patches
    # For cases where output is just "1.2.3" with other text
    version=$(echo "$output" | grep -oE '^[0-9]+\.[0-9]+' | head -1)

    if [ -n "$version" ]; then
        debug_log "Extracted version (fallback): $version"
        echo "$version"
        return 0
    fi

    debug_log "Could not parse version from: $output"
    echo "unknown"
    return 0
}

#
# Parse semantic version string into components
#
# Splits a version string into major.minor.patch components, handling
# pre-release versions and build metadata. Missing components default to 0.
#
# Arguments:
#   $1 - version_string (e.g., "1.2.3", "1.2", "2.0.0-beta", "1.2.3+build")
#
# Returns:
#   JSON object with major, minor, patch, prerelease fields
#   Example: {"major": 1, "minor": 2, "patch": 3, "prerelease": false}
#
# Exit code 0 always
#
parse_version() {
    local version_string="$1"

    debug_log "Parsing version: $version_string"

    # Handle "unknown" or empty input
    if [ "$version_string" = "unknown" ] || [ -z "$version_string" ]; then
        echo '{"major": -1, "minor": -1, "patch": -1, "prerelease": false}'
        return 0
    fi

    # Check if this is a pre-release version
    local prerelease=false
    if [[ "$version_string" =~ - ]]; then
        prerelease=true
    fi

    # Strip pre-release and build metadata
    # Examples: "1.2.3-beta+build" → "1.2.3"
    local base_version
    base_version="${version_string%%-*}"  # Remove -beta, -rc, etc.
    base_version="${base_version%%+*}"    # Remove +build metadata

    debug_log "Base version (metadata stripped): $base_version"

    # Split into major.minor.patch using IFS
    local major=0 minor=0 patch=0

    # Use a subshell to avoid polluting the current environment
    local parts
    parts=$(echo "$base_version" | tr '.' ' ')

    # Parse components
    local -a version_parts=($parts)

    major="${version_parts[0]:-0}"
    minor="${version_parts[1]:-0}"
    patch="${version_parts[2]:-0}"

    # Validate that components are integers
    if ! [[ "$major" =~ ^[0-9]+$ ]]; then major=0; fi
    if ! [[ "$minor" =~ ^[0-9]+$ ]]; then minor=0; fi
    if ! [[ "$patch" =~ ^[0-9]+$ ]]; then patch=0; fi

    debug_log "Parsed: major=$major minor=$minor patch=$patch prerelease=$prerelease"

    # Return as JSON
    printf '{"major": %d, "minor": %d, "patch": %d, "prerelease": %s}' "$major" "$minor" "$patch" "$([ "$prerelease" = true ] && echo 'true' || echo 'false')"
    return 0
}

#
# Compare two semantic versions
#
# Compares two version strings semantically (major.minor.patch).
# Pre-release versions are compared by stripping suffix before comparison.
# Build metadata is ignored.
#
# Arguments:
#   $1 - version1 (e.g., "1.2.3")
#   $2 - version2 (e.g., "1.2.5")
#
# Returns (to stdout):
#   -1 if version1 < version2
#    0 if version1 == version2
#    1 if version1 > version2
#
# Exit code 0 always
#
compare_versions() {
    local version1="$1"
    local version2="$2"

    debug_log "Comparing: $version1 vs $version2"

    # Handle "unknown" versions
    if [ "$version1" = "unknown" ] && [ "$version2" = "unknown" ]; then
        echo 0
        return 0
    fi
    if [ "$version1" = "unknown" ]; then
        echo -1
        return 0
    fi
    if [ "$version2" = "unknown" ]; then
        echo 1
        return 0
    fi

    # Parse both versions into components
    local v1_json v2_json
    v1_json=$(parse_version "$version1")
    v2_json=$(parse_version "$version2")

    # Extract major, minor, patch, prerelease using python3 for JSON parsing
    local v1_major v1_minor v1_patch v1_prerelease v2_major v2_minor v2_patch v2_prerelease
    v1_major=$(echo "$v1_json" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['major'])")
    v1_minor=$(echo "$v1_json" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['minor'])")
    v1_patch=$(echo "$v1_json" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['patch'])")
    v1_prerelease=$(echo "$v1_json" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['prerelease'])")

    v2_major=$(echo "$v2_json" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['major'])")
    v2_minor=$(echo "$v2_json" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['minor'])")
    v2_patch=$(echo "$v2_json" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['patch'])")
    v2_prerelease=$(echo "$v2_json" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['prerelease'])")

    debug_log "Parsed v1: $v1_major.$v1_minor.$v1_patch (prerelease: $v1_prerelease)"
    debug_log "Parsed v2: $v2_major.$v2_minor.$v2_patch (prerelease: $v2_prerelease)"

    # Compare major version
    if [ "$v1_major" -gt "$v2_major" ]; then
        echo 1
        return 0
    elif [ "$v1_major" -lt "$v2_major" ]; then
        echo -1
        return 0
    fi

    # Major equal, compare minor
    if [ "$v1_minor" -gt "$v2_minor" ]; then
        echo 1
        return 0
    elif [ "$v1_minor" -lt "$v2_minor" ]; then
        echo -1
        return 0
    fi

    # Major and minor equal, compare patch
    if [ "$v1_patch" -gt "$v2_patch" ]; then
        echo 1
        return 0
    elif [ "$v1_patch" -lt "$v2_patch" ]; then
        echo -1
        return 0
    fi

    # All numeric components equal, check pre-release
    # Pre-release versions are always less than release versions
    if [ "$v1_prerelease" = "True" ] && [ "$v2_prerelease" = "False" ]; then
        echo -1
        return 0
    elif [ "$v1_prerelease" = "False" ] && [ "$v2_prerelease" = "True" ]; then
        echo 1
        return 0
    fi

    # All components equal (both release or both pre-release)
    echo 0
    return 0
}

#
# Check if tool version meets requirement
#
# Compares current version against minimum required version and returns
# a status along with an appropriate message.
#
# Arguments:
#   $1 - tool_name (e.g., "asciinema")
#   $2 - current_version (e.g., "2.3.0" or "unknown")
#   $3 - min_version (minimum required, e.g., "2.0.0")
#
# Returns (to stdout):
#   JSON object with status, message, current, required fields
#   Example: {"status": "ok", "message": "Version meets requirement", ...}
#
# Exit code 0 always
#
check_version_requirement() {
    local tool_name="$1"
    local current_version="$2"
    local min_version="$3"

    debug_log "Checking $tool_name: current=$current_version, min=$min_version"

    local status message

    # Handle unknown current version
    if [ "$current_version" = "unknown" ]; then
        status="unknown"
        message="Could not determine $tool_name version. Health check may fail."
        debug_log "Status: unknown (could not determine version)"
    else
        # Compare versions
        local cmp_result
        cmp_result=$(compare_versions "$current_version" "$min_version")

        if [ "$cmp_result" -lt 0 ]; then
            # Current is less than minimum
            status="outdated"
            message="Tool $tool_name version $current_version is older than required $min_version. Run /craft:docs:demo --fix to update."
            debug_log "Status: outdated ($current_version < $min_version)"
        elif [ "$cmp_result" -eq 0 ]; then
            # Current equals minimum
            status="ok"
            message="Version meets requirement"
            debug_log "Status: ok ($current_version == $min_version)"
        else
            # Current is greater than minimum
            status="ok"
            message="Version meets requirement"
            debug_log "Status: ok ($current_version > $min_version)"
        fi
    fi

    # Output as JSON
    cat <<EOF
{
  "status": "$status",
  "message": "$message",
  "current": "$current_version",
  "required": "$min_version"
}
EOF

    return 0
}

#
# Validate all tool versions against requirements
#
# Checks all tools configured for a specific demo method (asciinema/vhs)
# and returns a JSON object with validation results for each tool.
#
# Arguments:
#   $1 - method (e.g., "asciinema" or "vhs")
#
# Returns (to stdout):
#   JSON object with per-tool validation results
#   Example: {"asciinema": {...}, "agg": {...}, ...}
#
# Exit code 0 always
#
validate_all_versions() {
    local method="${1:-asciinema}"

    debug_log "Validating all versions for method: $method"

    # Define tool requirements (could be sourced from demo.md in real usage)
    # Format: tool_name|version_cmd|min_version
    local -a tool_specs=(
        "asciinema|asciinema --version|2.0.0"
        "agg|agg --version|1.3.0"
        "gifsicle|gifsicle --version|1.90"
        "ffmpeg|ffmpeg -version|4.2.0"
    )

    local first=true
    echo "{"

    for spec in "${tool_specs[@]}"; do
        local tool_name version_cmd min_version
        IFS='|' read -r tool_name version_cmd min_version <<< "$spec"

        # Extract current version
        local current_version
        current_version=$(extract_version "$tool_name" "$version_cmd")

        # Check requirement
        local check_result
        check_result=$(check_version_requirement "$tool_name" "$current_version" "$min_version")

        # Output with comma handling
        if [ "$first" = true ]; then
            first=false
        else
            echo ","
        fi

        printf '  "%s": %s' "$tool_name" "$check_result"
    done

    echo ""
    echo "}"

    return 0
}

# Provide a friendly test/demo function
version_check_demo() {
    echo "Version Check Functions Available:"
    echo "  extract_version <tool_name> <cmd>   - Extract version from tool output"
    echo "  parse_version <version_string>      - Parse version into components"
    echo "  compare_versions <v1> <v2>          - Compare versions (-1/0/1)"
    echo "  check_version_requirement <t> <c> <m> - Validate requirement"
    echo "  validate_all_versions <method>      - Validate all tools"
    echo ""
    echo "Examples:"
    echo "  extract_version asciinema 'asciinema --version'"
    echo "  parse_version '1.2.3'"
    echo "  compare_versions '1.2.3' '1.2.5'"
    echo "  check_version_requirement asciinema '2.3.0' '2.0.0'"
    echo "  validate_all_versions asciinema"
}
