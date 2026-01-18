#!/bin/bash
# Dependency Installation Framework for Craft Demo
# Part of: feature/demo-dependency-management
# Phase: 2 (Auto-Installation)
#
# Purpose: Orchestrates multi-strategy installation with user consent and fallbacks
#
# Functions:
#   install_tool(tool_name, tool_spec) - Main installation orchestrator
#   get_install_strategies(tool_spec) - Extract and prioritize install methods
#   filter_available_strategies(strategies) - Filter by platform availability
#   try_install(tool_name, strategy, tool_spec) - Attempt installation with retry
#   verify_installation(tool_name, tool_spec) - Verify successful installation
#   prompt_user_consent(tool_name, purpose, strategies) - Get user approval

set -e

# Source utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/dependency-manager.sh"
source "$SCRIPT_DIR/tool-detector.sh"
source "$SCRIPT_DIR/session-cache.sh"
source "$SCRIPT_DIR/installers/brew-installer.sh"
source "$SCRIPT_DIR/installers/cargo-installer.sh"
source "$SCRIPT_DIR/installers/binary-installer.sh"

# Installation methods priority (can be overridden)
INSTALL_PRIORITY=("brew" "cargo_git" "cargo" "binary")

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
BOLD='\033[1m'
NC='\033[0m'

# Debug mode
DEBUG=${DEBUG:-0}

# Global skip flag (set by user consent)
SKIP_ALL=${SKIP_ALL:-false}

# Installation log (for debugging)
INSTALL_LOG="${INSTALL_LOG:-/tmp/craft-install-$$.log}"

debug_log() {
    if [ "$DEBUG" = "1" ]; then
        echo -e "${CYAN}[DEBUG]${NC} $*" >&2
    fi
}

log_install() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$INSTALL_LOG"
}

# Platform detection
detect_platform() {
    local os_type
    OS="$(uname -s)"
    case "$OS" in
        Darwin*) PLATFORM="macos" ;;
        Linux*)  PLATFORM="linux" ;;
        *)       PLATFORM="unknown" ;;
    esac

    ARCH="$(uname -m)"

    debug_log "Platform: $PLATFORM, Architecture: $ARCH"
}

# Initialize platform detection
detect_platform

#
# Get installation strategies from tool spec in priority order
#
# Args:
#   $1 - tool_spec (JSON string)
#
# Returns:
#   Newline-separated list of strategy names
#
get_install_strategies() {
    local tool_spec="$1"

    debug_log "Extracting install strategies from tool spec"

    # Extract all available install methods from spec
    python3 - <<PYTHON "$tool_spec"
import sys
import json

tool_spec = json.loads(sys.argv[1])
install = tool_spec.get('install', {})

# Priority order (defined globally)
priority = ["brew", "cargo_git", "cargo", "binary"]

# Filter to only methods that exist in spec
available = [method for method in priority if method in install]

# Print each on a new line
for method in available:
    print(method)
PYTHON
}

#
# Filter strategies by platform availability
#
# Args:
#   $1 - strategies (newline-separated list)
#
# Returns:
#   Newline-separated list of available strategies
#
filter_available_strategies() {
    local strategies="$1"
    local available=()

    debug_log "Filtering strategies by platform availability"

    while IFS= read -r strategy; do
        case "$strategy" in
            brew)
                if command -v brew &> /dev/null; then
                    debug_log "  ✓ brew available"
                    available+=("$strategy")
                else
                    debug_log "  ✗ brew not available"
                fi
                ;;

            cargo|cargo_git)
                if command -v cargo &> /dev/null; then
                    debug_log "  ✓ cargo available"
                    available+=("$strategy")
                else
                    debug_log "  ✗ cargo not available"
                fi
                ;;

            binary)
                # Binary download always available (requires curl)
                if command -v curl &> /dev/null; then
                    debug_log "  ✓ binary (curl) available"
                    available+=("$strategy")
                else
                    debug_log "  ✗ binary (curl) not available"
                fi
                ;;

            *)
                debug_log "  ? unknown strategy: $strategy"
                ;;
        esac
    done <<< "$strategies"

    # Print available strategies
    printf '%s\n' "${available[@]}"
}

#
# Prompt user for installation consent
#
# Args:
#   $1 - tool_name
#   $2 - purpose (user-facing description)
#   $3 - strategies (newline-separated list)
#
# Returns:
#   0 if user consents, 1 if user declines
#
prompt_user_consent() {
    local tool_name="$1"
    local purpose="$2"
    local strategies="$3"

    # Check global skip flag
    if [ "$SKIP_ALL" = "true" ]; then
        echo -e "${YELLOW}Skipping $tool_name (--skip-all)${NC}" >&2
        return 1
    fi

    # Display consent prompt
    cat >&2 <<EOF

┌─────────────────────────────────────────────────────────────┐
│ 🔧 ${BOLD}INSTALLATION REQUIRED${NC}                                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Tool: $tool_name
│ Purpose: $purpose
│                                                              │
│ Installation will try (in order):                            │
EOF

    local i=1
    while IFS= read -r strategy; do
        local time_estimate
        case "$strategy" in
            brew) time_estimate="~30s" ;;
            cargo) time_estimate="~2-5min" ;;
            cargo_git) time_estimate="~2-5min" ;;
            binary) time_estimate="~10s" ;;
            *) time_estimate="unknown" ;;
        esac

        printf "│   %d. %-15s (%s)%*s│\n" "$i" "$strategy" "$time_estimate" $((33 - ${#strategy} - ${#time_estimate})) "" >&2
        ((i++))
    done <<< "$strategies"

    cat >&2 <<EOF
│                                                              │
│ Install $tool_name now?                                      │
│   [Y] Yes, install                                           │
│   [N] No, skip this tool                                     │
│   [S] Skip all missing tools                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
EOF

    # Get user input
    read -p "Your choice [Y/n/s]: " choice
    case "$choice" in
        Y|y|"")
            log_install "User approved installation of $tool_name"
            return 0
            ;;
        S|s)
            SKIP_ALL=true
            log_install "User chose to skip all installations"
            return 1
            ;;
        *)
            log_install "User declined installation of $tool_name"
            return 1
            ;;
    esac
}

#
# Attempt installation with a specific strategy
#
# Args:
#   $1 - tool_name
#   $2 - strategy (brew, cargo, cargo_git, binary)
#   $3 - tool_spec (JSON string)
#
# Returns:
#   0 on success, 1 on failure
#   Prints error message to stderr on failure
#
try_install() {
    local tool_name="$1"
    local strategy="$2"
    local tool_spec="$3"

    debug_log "Attempting $strategy installation for $tool_name"
    log_install "Attempting $strategy installation for $tool_name"

    # Retry logic (2 attempts)
    local max_attempts=2
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        debug_log "  Attempt $attempt of $max_attempts"

        local install_result
        case "$strategy" in
            brew)
                install_result=$(install_via_brew "$tool_name" "$tool_spec" 2>&1)
                ;;

            cargo)
                install_result=$(install_via_cargo "$tool_name" "$tool_spec" 2>&1)
                ;;

            cargo_git)
                install_result=$(install_via_cargo_git "$tool_name" "$tool_spec" 2>&1)
                ;;

            binary)
                install_result=$(install_via_binary "$tool_name" "$tool_spec" 2>&1)
                ;;

            *)
                echo "ERROR: Unknown strategy: $strategy" >&2
                log_install "ERROR: Unknown strategy: $strategy"
                return 1
                ;;
        esac

        local exit_code=$?

        if [ $exit_code -eq 0 ]; then
            debug_log "  Installation successful"
            log_install "Installation successful via $strategy on attempt $attempt"
            return 0
        else
            debug_log "  Installation failed (exit: $exit_code)"
            log_install "Installation failed via $strategy on attempt $attempt: $install_result"

            if [ $attempt -lt $max_attempts ]; then
                echo -e "${YELLOW}Retry attempt $((attempt + 1))...${NC}" >&2
                sleep 2  # Brief delay before retry
            fi
        fi

        ((attempt++))
    done

    # All attempts failed
    echo -e "${RED}❌ $strategy failed after $max_attempts attempts${NC}" >&2
    log_install "All attempts failed for $strategy"
    return 1
}

#
# Verify installation succeeded
#
# Args:
#   $1 - tool_name
#   $2 - tool_spec (JSON string)
#
# Returns:
#   0 if installed and healthy, 1 otherwise
#
verify_installation() {
    local tool_name="$1"
    local tool_spec="$2"

    debug_log "Verifying installation of $tool_name"

    # Invalidate cache (tool was just installed)
    if [ -n "$CRAFT_CACHE_DIR" ]; then
        rm -f "$CRAFT_CACHE_DIR/${tool_name}.json" 2>/dev/null || true
    fi

    # Use tool-detector to verify
    local status_json
    status_json=$(detect_tool "$tool_name" "$tool_spec")

    # Extract status fields
    local installed
    local health
    installed=$(echo "$status_json" | jq -r '.installed' 2>/dev/null || echo "false")
    health=$(echo "$status_json" | jq -r '.health' 2>/dev/null || echo "unknown")

    debug_log "Verification result: installed=$installed, health=$health"

    if [ "$installed" = "true" ] && [ "$health" = "ok" ]; then
        log_install "Verification successful: $tool_name installed and healthy"
        return 0
    else
        log_install "Verification failed: installed=$installed, health=$health"
        return 1
    fi
}

#
# Main installation orchestrator
#
# Args:
#   $1 - tool_name
#   $2 - tool_spec (JSON string)
#
# Returns:
#   0 on success, 1 on failure
#
install_tool() {
    local tool_name="$1"
    local tool_spec="$2"

    debug_log "Installing tool: $tool_name"
    log_install "=== Starting installation: $tool_name ==="

    # Extract purpose for consent prompt
    local purpose
    purpose=$(echo "$tool_spec" | jq -r '.purpose' 2>/dev/null || echo "Required for demo functionality")

    # 1. Get installation strategies in priority order
    local strategies
    strategies=$(get_install_strategies "$tool_spec")

    if [ -z "$strategies" ]; then
        echo -e "${RED}ERROR: No installation methods available for $tool_name${NC}" >&2
        log_install "ERROR: No installation methods available"
        return 1
    fi

    debug_log "Available strategies: $(echo "$strategies" | tr '\n' ' ')"

    # 2. Filter strategies by platform
    local available_strategies
    available_strategies=$(filter_available_strategies "$strategies")

    if [ -z "$available_strategies" ]; then
        echo -e "${RED}ERROR: No installation methods available on this platform${NC}" >&2
        log_install "ERROR: No installation methods available on this platform"
        return 1
    fi

    debug_log "Platform-filtered strategies: $(echo "$available_strategies" | tr '\n' ' ')"

    # 3. Prompt user for consent
    if ! prompt_user_consent "$tool_name" "$purpose" "$available_strategies"; then
        echo -e "${YELLOW}Skipped $tool_name installation${NC}" >&2
        return 1
    fi

    # 4. Try each strategy with fallback
    while IFS= read -r strategy; do
        echo -e "${CYAN}Attempting: $strategy installation for $tool_name...${NC}" >&2

        if try_install "$tool_name" "$strategy" "$tool_spec"; then
            # 5. Verify installation
            if verify_installation "$tool_name" "$tool_spec"; then
                echo -e "${GREEN}✅ $tool_name installed successfully via $strategy${NC}" >&2
                log_install "=== Installation complete: $tool_name via $strategy ==="
                return 0
            else
                echo -e "${YELLOW}⚠️  $tool_name installed but health check failed${NC}" >&2
                log_install "Health check failed after $strategy installation, trying next strategy"
                # Continue to next strategy
            fi
        fi
        # Strategy failed, try next one
    done <<< "$available_strategies"

    # 6. All strategies failed
    echo -e "${RED}❌ Failed to install $tool_name via all methods${NC}" >&2
    log_install "=== Installation failed: $tool_name (all strategies exhausted) ==="
    return 1
}

#
# Stub installation functions (to be implemented in Wave 2)
#
# These functions are called by try_install() but not yet implemented.
# They should return 0 on success, 1 on failure, and print errors to stderr.
#

install_via_brew() {
    local tool_name="$1"
    local tool_spec="$2"

    # Extract brew package name from tool_spec
    local package
    package=$(echo "$tool_spec" | jq -r '.install.brew' 2>/dev/null)

    if [ -z "$package" ] || [ "$package" = "null" ]; then
        echo "ERROR: No brew package specified" >&2
        return 1
    fi

    debug_log "Installing $tool_name via brew (package: $package)"

    # Call the brew installer (from brew-installer.sh)
    # Note: This returns JSON to stdout, we need to parse it
    local result
    result=$(brew_install_package "$tool_name" "$package" 2>&1)
    local exit_code=$?

    # Parse result
    local success
    success=$(echo "$result" | jq -r '.success' 2>/dev/null || echo "false")

    if [ "$success" = "true" ]; then
        debug_log "Brew installation successful"
        return 0
    else
        local error
        error=$(echo "$result" | jq -r '.error' 2>/dev/null || echo "Unknown error")
        echo "ERROR: $error" >&2
        return 1
    fi
}

install_via_cargo() {
    local tool_name="$1"
    local tool_spec="$2"

    # Extract cargo package name from tool_spec
    local package
    package=$(echo "$tool_spec" | jq -r '.install.cargo' 2>/dev/null)

    if [ -z "$package" ] || [ "$package" = "null" ]; then
        echo "ERROR: No cargo package specified" >&2
        return 1
    fi

    debug_log "Installing via cargo: $package"

    # Call cargo installer function (from cargo-installer.sh)
    # The cargo_install_package function handles all output to stderr
    # and returns JSON to stdout for result parsing
    if cargo_install_package "$tool_name" "$package"; then
        return 0
    else
        return 1
    fi
}

install_via_cargo_git() {
    local tool_name="$1"
    local tool_spec="$2"

    # Extract git URL from tool_spec
    local repo_url
    repo_url=$(echo "$tool_spec" | jq -r '.install.cargo_git' 2>/dev/null)

    if [ -z "$repo_url" ] || [ "$repo_url" = "null" ]; then
        echo "ERROR: No cargo_git repo specified" >&2
        return 1
    fi

    debug_log "Installing via cargo git: $repo_url"

    # Call cargo installer function (from cargo-installer.sh)
    # The cargo_install_from_git function handles all output to stderr
    # and returns JSON to stdout for result parsing
    if cargo_install_from_git "$tool_name" "$repo_url"; then
        return 0
    else
        return 1
    fi
}

install_via_binary() {
    local tool_name="$1"
    local tool_spec="$2"

    debug_log "Installing $tool_name via binary download"

    # Extract binary spec from tool_spec
    # Frontmatter format: install.binary = { url, arch_map, target }
    local binary_spec
    binary_spec=$(echo "$tool_spec" | jq -c '.install.binary' 2>/dev/null)

    if [ -z "$binary_spec" ] || [ "$binary_spec" = "null" ]; then
        echo "ERROR: No binary spec in install config" >&2
        return 1
    fi

    # Call the binary installer (from binary-installer.sh)
    # Note: This returns JSON to stdout, progress messages to stderr
    # We only capture stdout for JSON parsing, let stderr pass through
    local result
    result=$(binary_download_and_install "$tool_name" "$binary_spec")
    local exit_code=$?

    # Parse result (JSON from stdout)
    local success
    success=$(echo "$result" | jq -r '.success' 2>/dev/null || echo "false")

    if [ "$success" = "true" ]; then
        debug_log "Binary installation successful"
        return 0
    else
        local error
        error=$(echo "$result" | jq -r '.error' 2>/dev/null || echo "Unknown error")
        echo "ERROR: $error" >&2
        return 1
    fi
}

# Main execution when script is run directly (for testing)
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    echo -e "${CYAN}Dependency Installer Test${NC}"
    echo "=========================="
    echo ""

    # Test: Install asciinema (using demo.md frontmatter)
    echo -e "${CYAN}Test: Install asciinema${NC}"

    # Parse frontmatter to get tool spec
    deps_json=$(parse_frontmatter)
    asciinema_spec=$(echo "$deps_json" | jq '.asciinema')

    echo "Tool spec:"
    echo "$asciinema_spec" | jq .
    echo ""

    # Test get_install_strategies
    echo "Strategies:"
    strategies=$(get_install_strategies "$asciinema_spec")
    echo "$strategies"
    echo ""

    # Test filter_available_strategies
    echo "Available strategies:"
    available=$(filter_available_strategies "$strategies")
    echo "$available"
    echo ""

    # Uncomment to test full installation (will prompt user)
    # install_tool "asciinema" "$asciinema_spec"

    echo -e "${GREEN}Test complete!${NC}"
    echo ""
    echo "Installation log: $INSTALL_LOG"
fi
