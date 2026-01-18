#!/bin/bash
# Cargo Installer for Craft Demo Dependency Management
# Part of: feature/demo-dependency-management
# Phase: 2 (Auto-Installation)
#
# Purpose: Install tools using Rust's cargo package manager
#
# Functions:
#   install_via_cargo(tool_name, package) - Install via cargo from crates.io
#   install_via_cargo_git(tool_name, repo_url) - Install via cargo from git repo
#   check_cargo_available() - Check if cargo is installed and functional
#
# Installation characteristics:
#   - Cargo compilation is SLOW (2-8 minutes typical)
#   - Requires internet connection
#   - Requires build dependencies (gcc, make, etc.)
#   - Compiles from source (architecture-independent)
#   - Output goes to ~/.cargo/bin/ (user installation)
#
# Error handling:
#   - Cargo not installed
#   - Git not installed (for cargo_git)
#   - Compilation errors
#   - Network errors
#   - Missing system dependencies (gcc, pkg-config, etc.)
#
# Output format: JSON
#   Success: {"success": true}
#   Failure: {"success": false, "error": "message"}

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
BOLD='\033[1m'
NC='\033[0m'

# Debug mode
DEBUG=${DEBUG:-0}

debug_log() {
    if [ "$DEBUG" = "1" ]; then
        echo -e "${CYAN}[DEBUG]${NC} $*" >&2
    fi
}

#
# Check if cargo is available and functional
#
# Returns:
#   0 if cargo is available, 1 otherwise
#
check_cargo_available() {
    debug_log "Checking cargo availability"

    # Check if cargo command exists
    if ! command -v cargo &> /dev/null; then
        debug_log "  cargo command not found"
        return 1
    fi

    # Check if cargo is functional
    if ! cargo --version &> /dev/null; then
        debug_log "  cargo --version failed"
        return 1
    fi

    debug_log "  cargo is available: $(cargo --version)"
    return 0
}

#
# Install tool via cargo from crates.io
#
# Args:
#   $1 - tool_name (for display purposes)
#   $2 - package (crate name on crates.io)
#
# Returns:
#   0 on success, 1 on failure
#   Prints JSON to stdout
#
cargo_install_package() {
    local tool_name="$1"
    local package="$2"

    debug_log "Installing $tool_name via cargo install $package"

    # Check if cargo is available
    if ! check_cargo_available; then
        echo '{"success": false, "error": "Cargo not installed. Install Rust from https://rustup.rs/"}'
        return 1
    fi

    # Create temp log file
    local log_file="/tmp/cargo-install-$$.log"
    debug_log "  Log file: $log_file"

    # Show progress message
    echo -e "${CYAN}⏳ Compiling $tool_name from source (this may take 2-5 minutes)...${NC}" >&2
    echo -e "${YELLOW}   This is normal for Rust packages - please be patient${NC}" >&2

    # Attempt installation
    if cargo install "$package" > "$log_file" 2>&1; then
        debug_log "  Installation successful"

        # Check if binary was installed
        if [ -f "$HOME/.cargo/bin/$tool_name" ]; then
            echo -e "${GREEN}✓ Compiled successfully${NC}" >&2
            echo '{"success": true}'
            rm -f "$log_file"
            return 0
        else
            # Binary might have different name than tool_name
            echo -e "${YELLOW}⚠ Compiled but binary name may differ from tool name${NC}" >&2
            echo '{"success": true}'
            rm -f "$log_file"
            return 0
        fi
    else
        # Extract error details from log
        local error_msg
        error_msg=$(tail -20 "$log_file" | grep -i "error\|failed" | head -3 | tr '\n' ' ' | sed 's/"/\\"/g')

        if [ -z "$error_msg" ]; then
            error_msg="Compilation failed. See $log_file for details."
        fi

        debug_log "  Installation failed: $error_msg"
        echo -e "${RED}✗ Compilation failed${NC}" >&2
        echo -e "${YELLOW}See log: $log_file${NC}" >&2

        echo "{\"success\": false, \"error\": \"$error_msg\"}"
        return 1
    fi
}

#
# Install tool via cargo from git repository
#
# Args:
#   $1 - tool_name (for display purposes)
#   $2 - repo_url (git repository URL)
#
# Returns:
#   0 on success, 1 on failure
#   Prints JSON to stdout
#
cargo_install_from_git() {
    local tool_name="$1"
    local repo_url="$2"

    debug_log "Installing $tool_name via cargo install --git $repo_url"

    # Check if cargo is available
    if ! check_cargo_available; then
        echo '{"success": false, "error": "Cargo not installed. Install Rust from https://rustup.rs/"}'
        return 1
    fi

    # Check if git is available (required for cargo install --git)
    if ! command -v git &> /dev/null; then
        echo '{"success": false, "error": "Git not installed. Install git first."}'
        return 1
    fi

    # Create temp log file
    local log_file="/tmp/cargo-git-install-$$.log"
    debug_log "  Log file: $log_file"

    # Show progress message
    echo -e "${CYAN}⏳ Compiling $tool_name from git (this may take 3-8 minutes)...${NC}" >&2
    echo -e "${YELLOW}   This is normal for Rust packages - please be patient${NC}" >&2
    echo -e "${YELLOW}   Cloning and building from: $repo_url${NC}" >&2

    # Attempt installation
    if cargo install --git "$repo_url" > "$log_file" 2>&1; then
        debug_log "  Installation successful"

        # Check if binary was installed
        if [ -f "$HOME/.cargo/bin/$tool_name" ]; then
            echo -e "${GREEN}✓ Compiled successfully from git${NC}" >&2
            echo '{"success": true}'
            rm -f "$log_file"
            return 0
        else
            # Binary might have different name than tool_name
            echo -e "${YELLOW}⚠ Compiled but binary name may differ from tool name${NC}" >&2
            echo '{"success": true}'
            rm -f "$log_file"
            return 0
        fi
    else
        # Extract error details from log
        local error_msg
        error_msg=$(tail -20 "$log_file" | grep -i "error\|failed" | head -3 | tr '\n' ' ' | sed 's/"/\\"/g')

        if [ -z "$error_msg" ]; then
            error_msg="Compilation failed. See $log_file for details."
        fi

        debug_log "  Installation failed: $error_msg"
        echo -e "${RED}✗ Compilation failed${NC}" >&2
        echo -e "${YELLOW}See log: $log_file${NC}" >&2

        echo "{\"success\": false, \"error\": \"$error_msg\"}"
        return 1
    fi
}

# Main execution when script is run directly (for testing)
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    echo -e "${CYAN}Cargo Installer Test${NC}"
    echo "===================="
    echo ""

    # Test 1: Check cargo availability
    echo -e "${CYAN}Test 1: Check cargo availability${NC}"
    if check_cargo_available; then
        echo -e "${GREEN}✓ Cargo is available${NC}"
        cargo --version
    else
        echo -e "${RED}✗ Cargo is not available${NC}"
    fi
    echo ""

    # Test 2: Dry-run test (parse arguments)
    echo -e "${CYAN}Test 2: Test argument parsing${NC}"
    echo "Would install 'agg' via: cargo install agg"
    echo "Expected output: {\"success\": true/false, ...}"
    echo ""

    # Test 3: Show function signatures
    echo -e "${CYAN}Test 3: Available functions${NC}"
    echo "  - check_cargo_available()"
    echo "  - cargo_install_package(tool_name, package)"
    echo "  - cargo_install_from_git(tool_name, repo_url)"
    echo ""

    # Note about actual testing
    echo -e "${YELLOW}Note: To test actual installation (takes 2-8 minutes):${NC}"
    echo "  source scripts/installers/cargo-installer.sh"
    echo "  cargo_install_package 'agg' 'agg'"
    echo "  cargo_install_from_git 'agg' 'https://github.com/asciinema/agg'"
    echo ""

    echo -e "${GREEN}Test complete!${NC}"
fi
