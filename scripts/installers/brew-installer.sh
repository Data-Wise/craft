#!/bin/bash
# Homebrew Installer for Craft Demo Dependency Management
# Part of: feature/demo-dependency-management
# Phase: 2 (Auto-Installation)

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

#
# Check if Homebrew is available and functional
#
# Returns:
#   0 if Homebrew is available and working
#   1 if Homebrew is not available or broken
#
check_brew_available() {
    # Check if brew command exists
    if ! command -v brew &> /dev/null; then
        return 1
    fi

    # Check if brew is functional (can run --version)
    if ! brew --version &> /dev/null; then
        return 1
    fi

    return 0
}

#
# Search for a package in Homebrew
#
# Args:
#   $1 - package name
#
# Returns:
#   0 if package found
#   1 if package not found or error
#
brew_search_package() {
    local package="$1"

    if [ -z "$package" ]; then
        return 1
    fi

    # Use brew info to check if package exists
    # This is more reliable than brew search for exact matches
    if brew info "$package" &> /dev/null; then
        return 0
    fi

    return 1
}

#
# Install a tool via Homebrew
#
# Args:
#   $1 - tool_name (e.g., "asciinema")
#   $2 - package name (e.g., "asciinema" or "charmbracelet/tap/vhs")
#
# Returns:
#   0 on success
#   1 on failure
#   Prints JSON result to stdout
#
brew_install_package() {
    local tool_name="$1"
    local package="$2"
    local temp_log="/tmp/brew-install-$$.log"

    # Validate inputs
    if [ -z "$tool_name" ] || [ -z "$package" ]; then
        echo '{"success": false, "error": "Missing tool_name or package"}'
        return 1
    fi

    # Check if Homebrew is available
    if ! check_brew_available; then
        echo '{"success": false, "error": "Homebrew not installed or not functional"}'
        return 1
    fi

    # Check if package exists in Homebrew
    if ! brew_search_package "$package"; then
        echo "{\"success\": false, \"error\": \"Package '$package' not found in Homebrew\"}"
        return 1
    fi

    # Check if already installed
    if brew list "$package" &> /dev/null; then
        echo '{"success": true, "message": "Package already installed"}'
        return 0
    fi

    # Attempt installation
    echo -e "${CYAN}Installing $tool_name via Homebrew...${NC}" >&2

    # Run brew install and capture output
    if brew install "$package" > "$temp_log" 2>&1; then
        # Success
        rm -f "$temp_log"
        echo '{"success": true}'
        return 0
    else
        # Failure - extract error message
        local error_msg
        error_msg=$(tail -10 "$temp_log" | tr '\n' ' ' | sed 's/"/\\"/g')

        # Clean up
        rm -f "$temp_log"

        echo "{\"success\": false, \"error\": \"Installation failed: $error_msg\"}"
        return 1
    fi
}

#
# Get Homebrew installation status
#
# Returns:
#   JSON object with brew status
#
get_brew_status() {
    local status="unavailable"
    local version=""
    local path=""

    if check_brew_available; then
        status="available"
        version=$(brew --version 2>/dev/null | head -1 | grep -oE '[0-9.]+' | head -1 || echo "unknown")
        path=$(command -v brew)
    fi

    cat <<EOF
{
  "status": "$status",
  "version": "$version",
  "path": "$path"
}
EOF
}

# Main execution when script is sourced (for testing)
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    cat <<'EOF'
Homebrew Installer Test
========================

This script is meant to be sourced, not executed directly.

Usage:
  source scripts/installers/brew-installer.sh
  brew_install_package "gifsicle" "gifsicle"

Functions available:
  - check_brew_available
  - brew_search_package <package>
  - brew_install_package <tool_name> <package>
  - get_brew_status

EOF

    echo "Testing Homebrew availability:"
    get_brew_status | jq .
fi
