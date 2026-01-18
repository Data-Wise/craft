#!/bin/bash

# User Consent Prompts for Dependency Installation
# Part of: feature/demo-dependency-management
# Phase: 2 (Auto-Installation)

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
NC='\033[0m'

# Global flag for skip-all mode
SKIP_ALL=false

################################################################################
# prompt_user_consent
#
# Display formatted consent prompt and get user choice
#
# Arguments:
#   $1: tool_name    - Name of tool to install
#   $2: purpose      - Human-readable purpose
#   $3: strategies   - Space-separated list of strategies (e.g. "brew cargo binary")
#
# Returns:
#   0 - User approved installation
#   1 - User declined this tool
#   2 - User selected skip-all mode
#
################################################################################
prompt_user_consent() {
    local tool_name="$1"
    local purpose="$2"
    local strategies="$3"

    # If skip-all is active, skip without prompting
    if [[ "$SKIP_ALL" == true ]]; then
        return 1
    fi

    # Count strategies to format properly
    local strategy_array=($strategies)
    local strategy_count=${#strategy_array[@]}
    local max_width=57

    # Display consent prompt box
    echo ""
    echo "┌─────────────────────────────────────────────────────────────┐"
    echo -e "│ ${CYAN}🔧 INSTALLATION REQUIRED${NC}                                     │"
    echo "├─────────────────────────────────────────────────────────────┤"
    echo "│                                                              │"
    printf "│ Tool: %-54s│\n" "$tool_name"
    printf "│ Purpose: %-50s│\n" "$purpose"
    echo "│                                                              │"
    echo "│ Installation will try (in order):                            │"

    # List each strategy with time estimate
    local i=1
    for strategy in "${strategy_array[@]}"; do
        local time_est=$(get_time_estimate "$strategy")
        printf "│   %d. %-51s│\n" "$i" "$strategy ($time_est)"
        ((i++))
    done

    echo "│                                                              │"
    echo "│ Install $tool_name now?                                      │"
    echo "│   [Y] Yes, install                                           │"
    echo "│   [N] No, skip this tool                                     │"
    echo "│   [S] Skip all missing tools                                 │"
    echo "│                                                              │"
    echo "└─────────────────────────────────────────────────────────────┘"
    echo ""

    # Get user input with validation
    local choice
    local max_attempts=3
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        read -p "Your choice [Y/n/s]: " choice

        # Validate input (only allow alphanumeric single character)
        if [[ ! "$choice" =~ ^[YyNnSs]?$ ]]; then
            echo -e "${RED}Invalid input. Please enter 'Y', 'n', or 's' (or press Enter for Yes)${NC}"
            ((attempt++))
            continue
        fi

        # Valid input - process choice
        case "$choice" in
            Y|y|"")
                return 0  # Yes, install
                ;;
            S|s)
                SKIP_ALL=true
                return 2  # Skip all mode activated
                ;;
            N|n)
                return 1  # No, skip this tool
                ;;
        esac
    done

    # Max attempts exceeded - default to skip
    echo -e "${YELLOW}Maximum attempts exceeded. Skipping this tool.${NC}"
    return 1
}

################################################################################
# get_time_estimate
#
# Return human-readable time estimate for installation strategy
#
# Arguments:
#   $1: strategy - Installation method (brew, cargo, cargo_git, binary)
#
# Returns:
#   Prints time estimate string to stdout
#
################################################################################
get_time_estimate() {
    local strategy="$1"

    case "$strategy" in
        brew)
            echo "~30 seconds"
            ;;
        cargo)
            echo "~2-5 minutes (compilation)"
            ;;
        cargo_git)
            echo "~3-8 minutes (compilation)"
            ;;
        binary)
            echo "~10 seconds"
            ;;
        apt|yum|pacman)
            echo "~30 seconds"
            ;;
        *)
            echo "~1-5 minutes"
            ;;
    esac
}

################################################################################
# show_installation_summary
#
# Display summary of installation results with categorized outcomes
#
# Arguments:
#   $1: installed_json - JSON array of successful installations
#       Format: [{"name": "asciinema", "via": "brew"}, ...]
#   $2: skipped_json   - JSON array of skipped tools
#       Format: [{"name": "vhs", "reason": "optional"}, ...]
#   $3: failed_json    - JSON array of failed installations
#       Format: [{"name": "agg", "errors": ["brew: not found", "cargo: build error"]}, ...]
#
# Returns:
#   None (displays formatted summary)
#
################################################################################
show_installation_summary() {
    local installed_json="$1"
    local skipped_json="$2"
    local failed_json="$3"

    echo ""
    echo "┌─────────────────────────────────────────────────────────────┐"
    echo -e "│ ${CYAN}📊 INSTALLATION SUMMARY${NC}                                      │"
    echo "├─────────────────────────────────────────────────────────────┤"
    echo "│                                                              │"

    # Helper function to extract JSON field value
    _extract_json_field() {
        local json_obj="$1"
        local field="$2"
        echo "$json_obj" | sed -n "s/.*\"$field\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
    }

    # Parse JSON and display installed tools
    if [[ -n "$installed_json" && "$installed_json" != "[]" ]]; then
        echo -e "│ ${GREEN}✅ Installed (count)${NC}:                                      │"

        # Parse JSON array manually by finding object boundaries
        local json_clean=$(echo "$installed_json" | sed 's/\[//g; s/\]//g; s/}, /}\n/g')
        while IFS= read -r item; do
            if [[ -n "$item" ]] && [[ "$item" == *"name"* ]]; then
                local name=$(_extract_json_field "$item" "name")
                local via=$(_extract_json_field "$item" "via")
                if [[ -n "$name" ]]; then
                    printf "│    ${GREEN}•${NC} %-50s│\n" "$name (via $via)"
                fi
            fi
        done < <(echo "$json_clean")
    fi

    # Display skipped tools
    if [[ -n "$skipped_json" && "$skipped_json" != "[]" ]]; then
        echo "│                                                              │"
        echo -e "│ ${YELLOW}⏭️  Skipped (count)${NC}:                                       │"

        local json_clean=$(echo "$skipped_json" | sed 's/\[//g; s/\]//g; s/}, /}\n/g')
        while IFS= read -r item; do
            if [[ -n "$item" ]] && [[ "$item" == *"name"* ]]; then
                local name=$(_extract_json_field "$item" "name")
                if [[ -n "$name" ]]; then
                    printf "│    ${YELLOW}•${NC} %-50s│\n" "$name"
                fi
            fi
        done < <(echo "$json_clean")
    fi

    # Display failed tools
    if [[ -n "$failed_json" && "$failed_json" != "[]" ]]; then
        echo "│                                                              │"
        echo -e "│ ${RED}❌ Failed (count)${NC}:                                         │"

        local json_clean=$(echo "$failed_json" | sed 's/\[//g; s/\]//g; s/}, /}\n/g')
        while IFS= read -r item; do
            if [[ -n "$item" ]] && [[ "$item" == *"name"* ]]; then
                local name=$(_extract_json_field "$item" "name")
                if [[ -n "$name" ]]; then
                    printf "│    ${RED}•${NC} %-50s│\n" "$name (all methods failed)"
                fi
            fi
        done < <(echo "$json_clean")
    fi

    echo "│                                                              │"
    echo "│ Next: Run /craft:docs:demo --check to verify                │"
    echo "│                                                              │"
    echo "└─────────────────────────────────────────────────────────────┘"
    echo ""
}

################################################################################
# Helper: Reset skip-all mode
# (Useful for testing and session resets)
################################################################################
reset_skip_all() {
    SKIP_ALL=false
}

################################################################################
# Helper: Get current skip-all status
################################################################################
is_skip_all_active() {
    [[ "$SKIP_ALL" == true ]]
}

# Export functions for use in other scripts
export -f prompt_user_consent
export -f get_time_estimate
export -f show_installation_summary
export -f reset_skip_all
export -f is_skip_all_active
