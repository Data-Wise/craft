#!/bin/bash
# batch-convert.sh - Bulk convert .cast files to optimized .gif
# Part of Phase 3: Batch Conversion (v1.25.0)
# Usage: batch-convert.sh [--search-path <path>] [--force] [--dry-run]
#
# Converts asciinema .cast recordings to optimized .gif files in batch mode
# with progress indicators, size tracking, and error handling.
#
# Functions:
#   find_cast_files() - Recursively find all .cast files
#   filter_existing() - Skip existing .gif unless --force
#   process_batch() - Convert each file with error tracking
#   show_progress() - Display progress bar with ETA
#   show_summary() - Display final statistics

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# Progress tracking variables
declare -a PROCESSED_FILES=()
declare -a FAILED_FILES=()
declare -a SKIPPED_FILES=()
TOTAL_SIZE_BEFORE=0
TOTAL_SIZE_AFTER=0
START_TIME=$(date +%s)

# Command-line defaults
SEARCH_PATHS=("docs/")
FORCE_OVERWRITE=false
DRY_RUN=false
PARALLEL_JOBS=1
VERBOSE=false

#
# Parse command-line arguments
#
parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --search-path)
                SEARCH_PATHS=("$2")
                shift 2
                ;;
            --force)
                FORCE_OVERWRITE=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --parallel)
                PARALLEL_JOBS="$2"
                shift 2
                ;;
            --verbose|-v)
                VERBOSE=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                echo "Error: Unknown option: $1" >&2
                show_help
                exit 1
                ;;
        esac
    done
}

#
# Display help text
#
show_help() {
    cat <<EOF
${BOLD}batch-convert.sh${NC} - Bulk convert .cast files to optimized .gif

${BOLD}USAGE:${NC}
  batch-convert.sh [OPTIONS]

${BOLD}OPTIONS:${NC}
  --search-path <path>   Directory to search for .cast files (default: docs/)
  --force                Overwrite existing .gif files
  --dry-run              Show what would be converted without actual conversion
  --parallel <N>         Number of parallel conversions (default: 1)
  --verbose, -v          Show detailed progress information
  --help, -h             Display this help message

${BOLD}EXAMPLES:${NC}
  # Convert all .cast files in docs/ directory
  batch-convert.sh

  # Search multiple directories
  batch-convert.sh --search-path docs/demos --search-path docs/gifs

  # Overwrite existing GIFs and show details
  batch-convert.sh --force --verbose

  # Preview conversions without processing
  batch-convert.sh --dry-run

${BOLD}EXIT CODES:${NC}
  0  All conversions successful
  1  Some conversions failed
  2  All conversions failed or no files found
  3  Missing convert-cast.sh script

EOF
}

#
# Log message with timestamp (verbose mode)
#
debug_log() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${DIM}[$(date '+%H:%M:%S')]${NC} $*" >&2
    fi
}

#
# Find all .cast files recursively in search paths
#
# Returns: List of .cast file paths (one per line)
#
find_cast_files() {
    local found_any=false
    local temp_file=$(mktemp)
    trap "rm -f '$temp_file'" RETURN

    for search_path in "${SEARCH_PATHS[@]}"; do
        if [ ! -d "$search_path" ]; then
            debug_log "Search path not found: $search_path"
            continue
        fi

        # Find all .cast files recursively
        while IFS= read -r file; do
            echo "$file" >> "$temp_file"
            found_any=true
        done < <(find "$search_path" -type f -name "*.cast" 2>/dev/null | sort)
    done

    if [ "$found_any" = true ]; then
        cat "$temp_file" | sort
    fi
}

#
# Filter out existing .gif files unless --force is set
#
# Arguments:
#   $1 - newline-separated list of .cast files
#   Returns: Filtered list with status
#
filter_existing() {
    local cast_file
    local gif_file
    local count_new=0
    local count_exists=0
    local temp_file=$(mktemp)
    trap "rm -f '$temp_file'" RETURN

    while IFS= read -r cast_file; do
        if [ -z "$cast_file" ]; then
            continue
        fi

        # Calculate expected .gif filename
        gif_file="${cast_file%.cast}.gif"

        if [ -f "$gif_file" ] && [ "$FORCE_OVERWRITE" = false ]; then
            echo "SKIP:$cast_file" >> "$temp_file"
            ((count_exists++)) || true
            debug_log "Skipping existing: $gif_file"
        else
            echo "CONV:$cast_file" >> "$temp_file"
            ((count_new++)) || true
            debug_log "Will convert: $cast_file"
        fi
    done

    cat "$temp_file"
}

#
# Display progress bar with ETA
#
# Arguments:
#   $1 - Current file number (1-based)
#   $2 - Total files
#   $3 - Current filename being processed
#   $4 - Current operation status
#
show_progress() {
    local current=$1
    local total=$2
    local filename=$3
    local status=$4
    local elapsed=$(($(date +%s) - START_TIME))

    # Calculate percentage and bar
    local percent=$(( (current * 100) / total ))
    local bar_filled=$(( (current * 20) / total ))
    local bar_empty=$(( 20 - bar_filled ))

    # Build progress bar
    local bar="["
    for ((i=0; i<bar_filled; i++)); do
        bar+="█"
    done
    for ((i=0; i<bar_empty; i++)); do
        bar+="░"
    done
    bar+="]"

    # Calculate ETA (if we have enough data)
    local eta=""
    if [ $current -gt 0 ] && [ $elapsed -gt 0 ]; then
        local rate=$(echo "scale=2; $elapsed / $current" | bc 2>/dev/null || echo "0")
        local remaining=$(( (total - current) ))
        local eta_seconds=$(echo "$rate * $remaining" | bc 2>/dev/null || echo "0")
        eta=$(format_duration "$eta_seconds")
    fi

    # Clear line and display progress
    printf "\r${CYAN}Processing .cast files...${NC}\n"
    printf "%-50s %3d/%3d (%3d%%)\n" "$bar" "$current" "$total" "$percent"
    printf "\r"
    printf "Current: %-60s\n" "$(basename "$filename")"
    printf "Status: %s\n" "$status"

    if [ -n "$eta" ]; then
        printf "ETA: %s\n" "$eta"
    fi

    # Move cursor back up to overwrite next time
    printf "\033[4A"
}

#
# Format duration in seconds to human-readable string
#
# Arguments:
#   $1 - Duration in seconds
#   Returns: Formatted string (e.g., "2m 35s")
#
format_duration() {
    local seconds=$1
    local hours=$(( seconds / 3600 ))
    local minutes=$(( (seconds % 3600) / 60 ))
    local secs=$(( seconds % 60 ))

    if [ $hours -gt 0 ]; then
        printf "%dh %dm %ds" "$hours" "$minutes" "$secs"
    elif [ $minutes -gt 0 ]; then
        printf "%dm %ds" "$minutes" "$secs"
    else
        printf "%ds" "$secs"
    fi
}

#
# Convert a single .cast file to .gif
#
# Arguments:
#   $1 - .cast file path
#   Returns: JSON result with success/failure and file sizes
#
convert_single() {
    local cast_file="$1"
    local gif_file="${cast_file%.cast}.gif"

    # Check if convert-cast.sh exists
    if [ ! -f "$SCRIPT_DIR/convert-cast.sh" ]; then
        echo "ERROR:convert-cast.sh not found"
        return 1
    fi

    # If dry-run, just report what would happen
    if [ "$DRY_RUN" = true ]; then
        echo "DRY_RUN:$cast_file → $gif_file"
        return 0
    fi

    # Get file size before conversion
    local size_before=0
    if [ -f "$cast_file" ]; then
        size_before=$(stat -f%z "$cast_file" 2>/dev/null || stat -c%s "$cast_file" 2>/dev/null || echo 0)
    fi

    # Source and execute conversion function
    source "$SCRIPT_DIR/convert-cast.sh" 2>/dev/null || {
        echo "ERROR:Failed to source convert-cast.sh"
        return 1
    }

    # Call conversion function (assumes it exists in convert-cast.sh)
    if ! convert_single_file "$cast_file" "$gif_file" 2>/dev/null; then
        echo "ERROR:Conversion failed for $cast_file"
        return 1
    fi

    # Get file size after conversion
    local size_after=0
    if [ -f "$gif_file" ]; then
        size_after=$(stat -f%z "$gif_file" 2>/dev/null || stat -c%s "$gif_file" 2>/dev/null || echo 0)
    fi

    # Calculate compression ratio
    local ratio=0
    if [ $size_before -gt 0 ]; then
        ratio=$(echo "scale=1; 100 - (100 * $size_after / $size_before)" | bc 2>/dev/null || echo "0")
    fi

    echo "SUCCESS:$cast_file:$size_before:$size_after:$ratio"
}

#
# Process batch of .cast files with progress tracking
#
# Arguments:
#   $1 - newline-separated list of files with status prefix
#   Returns: Exit code based on success/failure counts
#
process_batch() {
    local all_files="$1"
    local total_files=0
    local current=0
    local start_time=$(date +%s)

    # Count total files to process
    while IFS= read -r entry; do
        if [ -z "$entry" ]; then
            continue
        fi
        local action="${entry%%:*}"
        if [ "$action" = "CONV" ]; then
            ((total_files++)) || true
        fi
    done <<< "$all_files"

    if [ $total_files -eq 0 ]; then
        return 0
    fi

    echo ""
    echo "Converting $total_files file(s)..."
    echo ""

    # Process each file
    while IFS= read -r entry; do
        if [ -z "$entry" ]; then
            continue
        fi

        local action="${entry%%:*}"
        local file_path="${entry#*:}"

        if [ "$action" = "SKIP" ]; then
            SKIPPED_FILES+=("$file_path")
            debug_log "Skipped: $file_path (already exists)"
            continue
        fi

        if [ "$action" != "CONV" ]; then
            continue
        fi

        ((current++)) || true

        # Update progress display
        show_progress "$current" "$total_files" "$file_path" "Converting..."

        # Perform conversion
        local result
        if ! result=$(convert_single "$file_path" 2>&1); then
            FAILED_FILES+=("$file_path")
            debug_log "Failed: $file_path"
            show_progress "$current" "$total_files" "$file_path" "${RED}Failed${NC}"
            continue
        fi

        # Parse result
        local result_type="${result%%:*}"
        if [ "$result_type" = "ERROR" ] || [ "$result_type" = "DRY_RUN" ]; then
            if [ "$result_type" = "ERROR" ]; then
                FAILED_FILES+=("$file_path")
                debug_log "Failed: $file_path"
                show_progress "$current" "$total_files" "$file_path" "${RED}Failed${NC}"
            else
                PROCESSED_FILES+=("$file_path")
                debug_log "Dry-run: $file_path"
                show_progress "$current" "$total_times" "$file_path" "${YELLOW}Would convert${NC}"
            fi
            continue
        fi

        # Extract metrics from result
        if [ "$result_type" = "SUCCESS" ]; then
            IFS=':' read -r _ _ size_before size_after ratio <<< "$result"
            TOTAL_SIZE_BEFORE=$((TOTAL_SIZE_BEFORE + size_before))
            TOTAL_SIZE_AFTER=$((TOTAL_SIZE_AFTER + size_after))
            PROCESSED_FILES+=("$file_path:$size_after")
            debug_log "Converted: $file_path (${ratio}% reduction)"
            show_progress "$current" "$total_files" "$file_path" "${GREEN}✓ Success${NC}"
        fi
    done <<< "$all_files"

    # Clear progress lines
    printf "\n\n\n\n"

    return 0
}

#
# Display summary statistics
#
# Outputs:
#   Summary table with totals, sizes, compression, and timing
#
show_summary() {
    local elapsed=$(($(date +%s) - START_TIME))
    local success_count=${#PROCESSED_FILES[@]}
    local fail_count=${#FAILED_FILES[@]}
    local skip_count=${#SKIPPED_FILES[@]}
    local total_count=$((success_count + fail_count + skip_count))

    echo ""
    echo "==============================================="
    echo "CONVERSION SUMMARY"
    echo "==============================================="
    echo ""

    # File counts
    if [ $total_count -eq 0 ]; then
        echo "No .cast files found in search paths"
        return 0
    fi

    printf "%-30s: %3d\n" "Files processed" "$success_count"
    printf "%-30s: %3d\n" "Files failed" "$fail_count"
    printf "%-30s: %3d\n" "Files skipped" "$skip_count"
    printf "%-30s: %3d\n" "Total files" "$total_count"
    echo ""

    # Size statistics
    if [ $success_count -gt 0 ] && [ "$TOTAL_SIZE_BEFORE" -gt 0 ]; then
        local size_before_mb=$(echo "scale=2; $TOTAL_SIZE_BEFORE / 1048576" | bc 2>/dev/null || echo "0")
        local size_after_mb=$(echo "scale=2; $TOTAL_SIZE_AFTER / 1048576" | bc 2>/dev/null || echo "0")
        local reduction_ratio=$(echo "scale=1; 100 - (100 * $TOTAL_SIZE_AFTER / $TOTAL_SIZE_BEFORE)" | bc 2>/dev/null || echo "0")

        printf "%-30s: %10s\n" "Total size before" "${size_before_mb} MB"
        printf "%-30s: %10s\n" "Total size after" "${size_after_mb} MB"
        printf "%-30s: %10s %%\n" "Compression ratio" "$reduction_ratio"
        echo ""
    fi

    # Time statistics
    local duration=$(format_duration "$elapsed")
    printf "%-30s: %10s\n" "Total time" "$duration"
    if [ $success_count -gt 0 ]; then
        local avg_time=$(echo "scale=1; $elapsed / $success_count" | bc 2>/dev/null || echo "0")
        printf "%-30s: %10s seconds\n" "Average per file" "$avg_time"
    fi
    echo ""

    # Exit status
    if [ $fail_count -eq 0 ]; then
        echo -e "${GREEN}✓ All conversions successful${NC}"
        return 0
    elif [ $success_count -gt 0 ]; then
        echo -e "${YELLOW}⚠ Some conversions failed${NC}"
        return 1
    else
        echo -e "${RED}✗ All conversions failed${NC}"
        return 2
    fi
}

#
# Trap for cleanup on interrupt
#
trap_cleanup() {
    echo ""
    echo ""
    echo -e "${YELLOW}Conversion interrupted${NC}"
    show_summary || true
    exit 1
}

trap trap_cleanup INT TERM

#
# Main execution
#
main() {
    # Parse command-line arguments
    parse_args "$@"

    # Find all .cast files
    debug_log "Searching for .cast files in: ${SEARCH_PATHS[*]}"
    local all_cast_files
    all_cast_files=$(find_cast_files)

    if [ -z "$all_cast_files" ]; then
        echo "No .cast files found in search paths: ${SEARCH_PATHS[*]}"
        exit 0
    fi

    # Filter out existing files
    debug_log "Filtering existing .gif files (force=$FORCE_OVERWRITE)..."
    local filtered_files
    filtered_files=$(filter_existing <<< "$all_cast_files")

    if [ "$DRY_RUN" = true ]; then
        echo "DRY RUN: Would process the following files:"
        echo ""
        while IFS= read -r entry; do
            local action="${entry%%:*}"
            local file="${entry#*:}"
            case "$action" in
                CONV)
                    echo -e "${GREEN}Convert:${NC} $file"
                    ;;
                SKIP)
                    echo -e "${YELLOW}Skip:${NC} $file (already exists)"
                    ;;
            esac
        done <<< "$filtered_files"
        echo ""
        return 0
    fi

    # Process batch
    process_batch "$filtered_files"

    # Display summary
    show_summary
    local exit_code=$?

    return $exit_code
}

# Execute main function
main "$@"
