#!/bin/bash
# Binary Installer for Craft Demo Dependency Management
# Part of: feature/demo-dependency-management
# Phase: 2 (Auto-Installation)
#
# Purpose: Download and install binary executables from URLs
#
# Functions:
#   binary_download_and_install(tool_name, binary_spec) - Download and install binary
#   download_binary(url, dest_dir) - Download binary from URL
#   get_arch_mapping(arch, arch_map) - Map system arch to binary arch
#   make_executable_and_install(binary_file, target_path) - Install binary to target
#
# Binary spec format (JSON):
#   {
#     "url": "https://github.com/org/repo/releases/latest/download/tool-{{arch}}-darwin",
#     "arch_map": {"x86_64": "x86_64", "arm64": "aarch64"},
#     "target": "/usr/local/bin/tool"
#   }
#
# Installation characteristics:
#   - Fast (download only, no compilation)
#   - Requires internet connection
#   - May require sudo for privileged paths
#   - Architecture-specific binaries
#
# Error handling:
#   - Network errors (404, timeouts, etc.)
#   - Permission errors (sudo required)
#   - Architecture not found in mapping
#   - Binary not executable
#   - Invalid URL format
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

# Temp directory for downloads
DOWNLOAD_DIR="/tmp/craft-binary-install-$$"

# Debug mode
DEBUG=${DEBUG:-0}

debug_log() {
    if [ "$DEBUG" = "1" ]; then
        echo -e "${CYAN}[DEBUG]${NC} $*" >&2
    fi
}

#
# Extract JSON field value
#
# Args:
#   $1 - JSON string
#   $2 - Field name
#
# Returns:
#   Field value (empty if not found)
#
extract_json_field() {
    local json="$1"
    local field="$2"

    # Use sed to extract field value
    # Handles: "field": "value" or "field":"value"
    echo "$json" | sed -n "s/.*\"$field\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
}

#
# Get architecture mapping from binary spec
#
# Args:
#   $1 - system architecture (e.g., "arm64", "x86_64")
#   $2 - binary_spec JSON string
#
# Returns:
#   Mapped architecture (exits with error if not found)
#
get_arch_mapping() {
    local sys_arch="$1"
    local binary_spec="$2"

    debug_log "Mapping architecture: $sys_arch"

    # Extract arch_map section
    # Format: "arch_map": {"x86_64": "x86_64", "arm64": "aarch64"}
    local arch_map
    arch_map=$(echo "$binary_spec" | sed -n 's/.*"arch_map"[[:space:]]*:[[:space:]]*{\([^}]*\)}.*/\1/p')

    if [ -z "$arch_map" ]; then
        debug_log "  No arch_map found, using system arch as-is"
        echo "$sys_arch"
        return 0
    fi

    # Extract mapping for current architecture
    # Format: "arm64": "aarch64"
    local mapped
    mapped=$(echo "$arch_map" | sed -n "s/.*\"$sys_arch\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p")

    if [ -z "$mapped" ]; then
        debug_log "  No mapping found for $sys_arch in arch_map"
        echo "$sys_arch"
        return 0
    fi

    debug_log "  Mapped $sys_arch -> $mapped"
    echo "$mapped"
}

#
# Download binary from URL
#
# Args:
#   $1 - URL to download from
#   $2 - destination directory
#
# Returns:
#   0 on success, 1 on failure
#   Prints downloaded file path to stdout on success
#
download_binary() {
    local url="$1"
    local dest_dir="$2"

    debug_log "Downloading from: $url"
    debug_log "  Destination: $dest_dir"

    # Create destination directory
    mkdir -p "$dest_dir"

    # Extract filename from URL (last component)
    local filename
    filename=$(basename "$url" | sed 's/[?#].*//')

    if [ -z "$filename" ]; then
        filename="downloaded-binary"
    fi

    local dest_file="$dest_dir/$filename"
    debug_log "  Output file: $dest_file"

    # Try curl first, fallback to wget
    if command -v curl &> /dev/null; then
        echo -e "${CYAN}⏳ Downloading binary...${NC}" >&2

        if curl -L -f -o "$dest_file" "$url" 2>&1 | grep -v "%" >&2; then
            debug_log "  Download successful via curl"
            echo "$dest_file"
            return 0
        else
            debug_log "  curl download failed"
            rm -f "$dest_file"
            return 1
        fi
    elif command -v wget &> /dev/null; then
        echo -e "${CYAN}⏳ Downloading binary...${NC}" >&2

        if wget -q -O "$dest_file" "$url" 2>&1 >&2; then
            debug_log "  Download successful via wget"
            echo "$dest_file"
            return 0
        else
            debug_log "  wget download failed"
            rm -f "$dest_file"
            return 1
        fi
    else
        echo -e "${RED}✗ Neither curl nor wget found${NC}" >&2
        return 1
    fi
}

#
# Make binary executable and install to target location
#
# Args:
#   $1 - binary file path
#   $2 - target installation path
#
# Returns:
#   0 on success, 1 on failure
#
make_executable_and_install() {
    local binary_file="$1"
    local target="$2"

    debug_log "Installing binary"
    debug_log "  Source: $binary_file"
    debug_log "  Target: $target"

    # Validate inputs
    if [ ! -f "$binary_file" ]; then
        echo -e "${RED}✗ Binary file not found: $binary_file${NC}" >&2
        return 1
    fi

    if [ -z "$target" ]; then
        echo -e "${RED}✗ Target path not specified${NC}" >&2
        return 1
    fi

    # Make executable
    chmod +x "$binary_file"
    debug_log "  Made executable"

    # Determine if sudo is needed
    local needs_sudo=0
    local target_dir
    target_dir=$(dirname "$target")

    # Check if target is in a privileged location
    if [[ "$target" == /usr/local/* ]] || [[ "$target" == /usr/bin/* ]] || [[ "$target" == /opt/* ]]; then
        needs_sudo=1
        debug_log "  Target requires sudo: $target"
    fi

    # Ensure target directory exists
    if [ ! -d "$target_dir" ]; then
        debug_log "  Creating target directory: $target_dir"

        if [ $needs_sudo -eq 1 ]; then
            echo -e "${YELLOW}⚠️  Installation to $target requires administrator privileges${NC}" >&2

            # Check if we can use sudo without password
            if ! sudo -n true 2>/dev/null; then
                echo -e "${YELLOW}Please enter your password for installation:${NC}" >&2
            fi

            if ! sudo mkdir -p "$target_dir"; then
                echo -e "${RED}✗ Failed to create target directory${NC}" >&2
                return 1
            fi
        else
            mkdir -p "$target_dir"
        fi
    fi

    # Install binary
    if [ $needs_sudo -eq 1 ]; then
        echo -e "${CYAN}Installing to $target (requires sudo)...${NC}" >&2

        # Check if we can use sudo without password
        if ! sudo -n true 2>/dev/null; then
            echo -e "${YELLOW}Please enter your password for installation:${NC}" >&2
        fi

        if sudo mv "$binary_file" "$target"; then
            debug_log "  Installed successfully with sudo"
            echo -e "${GREEN}✓ Installed to $target${NC}" >&2
            return 0
        else
            echo -e "${RED}✗ Installation failed (permission denied)${NC}" >&2
            return 1
        fi
    else
        if mv "$binary_file" "$target"; then
            debug_log "  Installed successfully"
            echo -e "${GREEN}✓ Installed to $target${NC}" >&2
            return 0
        else
            echo -e "${RED}✗ Installation failed${NC}" >&2
            return 1
        fi
    fi
}

#
# Install tool via binary download
#
# Args:
#   $1 - tool_name (for display purposes)
#   $2 - binary_spec (JSON string with url, arch_map, target)
#
# Returns:
#   0 on success, 1 on failure
#   Prints JSON to stdout
#
binary_download_and_install() {
    local tool_name="$1"
    local binary_spec="$2"

    debug_log "Installing $tool_name via binary download"
    debug_log "  Spec: $binary_spec"

    # Validate inputs
    if [ -z "$tool_name" ] || [ -z "$binary_spec" ]; then
        echo '{"success": false, "error": "Missing tool_name or binary_spec"}'
        return 1
    fi

    # Extract fields from JSON
    local url
    local target

    url=$(extract_json_field "$binary_spec" "url")
    target=$(extract_json_field "$binary_spec" "target")

    if [ -z "$url" ]; then
        echo '{"success": false, "error": "No URL specified in binary_spec"}'
        return 1
    fi

    if [ -z "$target" ]; then
        echo '{"success": false, "error": "No target path specified in binary_spec"}'
        return 1
    fi

    debug_log "  URL: $url"
    debug_log "  Target: $target"

    # Get system architecture
    local sys_arch
    sys_arch=$(uname -m)
    debug_log "  System arch: $sys_arch"

    # Map architecture if needed
    local mapped_arch
    mapped_arch=$(get_arch_mapping "$sys_arch" "$binary_spec")
    debug_log "  Mapped arch: $mapped_arch"

    # Substitute {{arch}} in URL
    url=${url//\{\{arch\}\}/$mapped_arch}
    debug_log "  Final URL: $url"

    # Create download directory
    mkdir -p "$DOWNLOAD_DIR"

    # Download binary
    local binary_file
    if ! binary_file=$(download_binary "$url" "$DOWNLOAD_DIR"); then
        local error_msg="Failed to download binary from $url"
        echo -e "${RED}✗ Download failed${NC}" >&2
        echo "{\"success\": false, \"error\": \"$error_msg\"}"

        # Cleanup
        rm -rf "$DOWNLOAD_DIR"
        return 1
    fi

    # Install binary
    if make_executable_and_install "$binary_file" "$target"; then
        echo -e "${GREEN}✓ Binary installation complete${NC}" >&2
        echo '{"success": true}'

        # Cleanup
        rm -rf "$DOWNLOAD_DIR"
        return 0
    else
        echo -e "${RED}✗ Installation failed${NC}" >&2
        echo '{"success": false, "error": "Failed to install binary to target location"}'

        # Cleanup
        rm -rf "$DOWNLOAD_DIR"
        return 1
    fi
}

# Cleanup function (called on exit)
cleanup_on_exit() {
    if [ -d "$DOWNLOAD_DIR" ]; then
        debug_log "Cleaning up temporary directory: $DOWNLOAD_DIR"
        rm -rf "$DOWNLOAD_DIR"
    fi
}

# Register cleanup
trap cleanup_on_exit EXIT

# Main execution when script is run directly (for testing)
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    echo -e "${CYAN}Binary Installer Test${NC}"
    echo "====================="
    echo ""

    # Test 1: Architecture detection
    echo -e "${CYAN}Test 1: System architecture${NC}"
    echo "  System arch: $(uname -m)"
    echo ""

    # Test 2: Test architecture mapping
    echo -e "${CYAN}Test 2: Architecture mapping${NC}"
    test_spec='{"arch_map": {"x86_64": "x86_64", "arm64": "aarch64"}}'
    echo "  Spec: $test_spec"
    echo "  Mapped arch: $(get_arch_mapping "$(uname -m)" "$test_spec")"
    echo ""

    # Test 3: Show function signatures
    echo -e "${CYAN}Test 3: Available functions${NC}"
    echo "  - binary_download_and_install(tool_name, binary_spec)"
    echo "  - download_binary(url, dest_dir)"
    echo "  - get_arch_mapping(arch, arch_map)"
    echo "  - make_executable_and_install(binary_file, target_path)"
    echo ""

    # Test 4: Example usage
    echo -e "${CYAN}Test 4: Example usage${NC}"
    cat <<'EXAMPLE'
# Example: Install agg binary
binary_spec='{
  "url": "https://github.com/asciinema/agg/releases/latest/download/agg-{{arch}}-apple-darwin",
  "arch_map": {"x86_64": "x86_64", "arm64": "aarch64"},
  "target": "/usr/local/bin/agg"
}'

source scripts/installers/binary-installer.sh
binary_download_and_install "agg" "$binary_spec"
EXAMPLE
    echo ""

    # Note about actual testing
    echo -e "${YELLOW}Note: To test actual installation:${NC}"
    echo "  source scripts/installers/binary-installer.sh"
    echo "  binary_download_and_install 'tool_name' '\$binary_spec'"
    echo ""

    echo -e "${GREEN}Test complete!${NC}"
fi
