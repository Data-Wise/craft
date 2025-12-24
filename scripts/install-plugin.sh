#!/usr/bin/env bash
#
# Plugin Installation Manager for Claude Code
#
# Usage:
#   ./install-plugin.sh <plugin-name>          # Install plugin
#   ./install-plugin.sh <plugin-name> --force  # Force reinstall
#   ./install-plugin.sh --list                 # List available plugins
#   ./install-plugin.sh --validate             # Validate before install
#
# Examples:
#   ./install-plugin.sh rforge-orchestrator
#   ./install-plugin.sh workflow --force
#

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
CLAUDE_PLUGINS_DIR="$HOME/.claude/plugins"
BACKUP_DIR="$HOME/.claude/plugins/.backups"

# Available plugins
PLUGINS=("rforge-orchestrator" "statistical-research" "workflow")

# Functions
print_header() {
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${BLUE}  $1${NC}"
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

list_plugins() {
    print_header "Available Plugins"
    echo ""
    for plugin in "${PLUGINS[@]}"; do
        if [ -d "$REPO_ROOT/$plugin" ]; then
            # Check if installed
            if [ -d "$CLAUDE_PLUGINS_DIR/$plugin" ]; then
                echo -e "  ${GREEN}✅ $plugin${NC} (installed)"
            else
                echo -e "  ${BLUE}📦 $plugin${NC} (not installed)"
            fi

            # Show version if package.json exists
            if [ -f "$REPO_ROOT/$plugin/package.json" ]; then
                version=$(python3 -c "import json; print(json.load(open('$REPO_ROOT/$plugin/package.json'))['version'])" 2>/dev/null || echo "unknown")
                echo -e "     Version: $version"
            fi
        else
            print_error "Plugin directory not found: $plugin"
        fi
        echo ""
    done
}

validate_plugin() {
    local plugin=$1
    local plugin_path="$REPO_ROOT/$plugin"

    print_info "Validating $plugin..."

    # Check required files
    local required_files=("package.json" ".claude-plugin/plugin.json" "README.md" "LICENSE")
    for file in "${required_files[@]}"; do
        if [ ! -f "$plugin_path/$file" ]; then
            print_error "Missing required file: $file"
            return 1
        fi
    done

    # Validate JSON files
    if ! python3 -m json.tool "$plugin_path/package.json" > /dev/null 2>&1; then
        print_error "Invalid JSON in package.json"
        return 1
    fi

    if ! python3 -m json.tool "$plugin_path/.claude-plugin/plugin.json" > /dev/null 2>&1; then
        print_error "Invalid JSON in plugin.json"
        return 1
    fi

    print_success "Plugin structure validated"
    return 0
}

backup_existing() {
    local plugin=$1

    if [ -d "$CLAUDE_PLUGINS_DIR/$plugin" ]; then
        print_info "Backing up existing installation..."

        # Create backup directory
        mkdir -p "$BACKUP_DIR"

        # Backup with timestamp
        local timestamp=$(date +%Y%m%d-%H%M%S)
        local backup_path="$BACKUP_DIR/${plugin}-${timestamp}"

        cp -r "$CLAUDE_PLUGINS_DIR/$plugin" "$backup_path"
        print_success "Backup created: $backup_path"
    fi
}

install_plugin() {
    local plugin=$1
    local force=${2:-false}
    local plugin_path="$REPO_ROOT/$plugin"

    print_header "Installing: $plugin"
    echo ""

    # Check if plugin exists in repo
    if [ ! -d "$plugin_path" ]; then
        print_error "Plugin not found: $plugin"
        print_info "Available plugins: ${PLUGINS[*]}"
        return 1
    fi

    # Validate plugin structure
    if ! validate_plugin "$plugin"; then
        print_error "Plugin validation failed"
        return 1
    fi

    # Check if already installed
    if [ -d "$CLAUDE_PLUGINS_DIR/$plugin" ] && [ "$force" != "true" ]; then
        print_warning "Plugin already installed: $plugin"
        print_info "Use --force to reinstall"
        return 1
    fi

    # Backup existing installation
    if [ -d "$CLAUDE_PLUGINS_DIR/$plugin" ]; then
        backup_existing "$plugin"
        rm -rf "$CLAUDE_PLUGINS_DIR/$plugin"
    fi

    # Create plugins directory if needed
    mkdir -p "$CLAUDE_PLUGINS_DIR"

    # Copy plugin to ~/.claude/plugins/
    print_info "Installing plugin..."
    cp -r "$plugin_path" "$CLAUDE_PLUGINS_DIR/$plugin"

    # Verify installation
    if [ -d "$CLAUDE_PLUGINS_DIR/$plugin" ]; then
        print_success "Plugin installed successfully"

        # Show plugin info
        echo ""
        print_info "Installation location: $CLAUDE_PLUGINS_DIR/$plugin"

        if [ -f "$CLAUDE_PLUGINS_DIR/$plugin/package.json" ]; then
            version=$(python3 -c "import json; print(json.load(open('$CLAUDE_PLUGINS_DIR/$plugin/package.json'))['version'])" 2>/dev/null || echo "unknown")
            print_info "Version: $version"
        fi

        # Count commands
        if [ -d "$CLAUDE_PLUGINS_DIR/$plugin/commands" ]; then
            cmd_count=$(find "$CLAUDE_PLUGINS_DIR/$plugin/commands" -name "*.md" | wc -l)
            print_info "Commands: $cmd_count"
        fi

        echo ""
        print_warning "IMPORTANT: Restart Claude Code to load the plugin"
        echo ""

        return 0
    else
        print_error "Installation failed"
        return 1
    fi
}

show_usage() {
    cat << EOF
${BOLD}Plugin Installation Manager for Claude Code${NC}

${BOLD}USAGE:${NC}
    $0 <plugin-name>          Install plugin
    $0 <plugin-name> --force  Force reinstall
    $0 --list                 List available plugins
    $0 --help                 Show this help

${BOLD}AVAILABLE PLUGINS:${NC}
    ${PLUGINS[@]}

${BOLD}EXAMPLES:${NC}
    $0 rforge-orchestrator              # Install rforge-orchestrator
    $0 workflow --force                 # Force reinstall workflow
    $0 --list                           # List all plugins

${BOLD}NOTES:${NC}
    - Plugins are installed to: $CLAUDE_PLUGINS_DIR
    - Backups are stored in: $BACKUP_DIR
    - You must restart Claude Code after installation

EOF
}

# Main script
main() {
    if [ $# -eq 0 ]; then
        show_usage
        exit 0
    fi

    case "$1" in
        --list)
            list_plugins
            ;;
        --help|-h)
            show_usage
            ;;
        --validate)
            if [ -z "$2" ]; then
                print_error "Please specify a plugin to validate"
                exit 1
            fi
            validate_plugin "$2"
            ;;
        *)
            local plugin=$1
            local force=false

            if [ "$2" == "--force" ]; then
                force=true
            fi

            install_plugin "$plugin" "$force"
            ;;
    esac
}

main "$@"
