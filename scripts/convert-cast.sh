#!/bin/bash
# convert-cast.sh - Convert single .cast file to optimized .gif
# Part of Phase 3: Batch Conversion (v1.25.0)
#
# Converts asciinema recordings (.cast files) to optimized animated GIFs
# using agg for rendering and gifsicle for compression.
#
# Usage: convert-cast.sh <input.cast> [output.gif] [--force]
#
# Examples:
#   convert-cast.sh recording.cast                          # Auto-generate output.gif
#   convert-cast.sh demo.cast demo-output.gif               # Specify output name
#   convert-cast.sh recording.cast --force                  # Overwrite existing .gif
#   convert-cast.sh demo.cast output.gif --force            # Both output name and force flag
#
# Exit codes:
#   0 = Success
#   1 = Error (missing dependencies, invalid input, file errors)
#   2 = File exists, need --force flag

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

# agg rendering settings
AGG_FONT_SIZE=16
AGG_LINE_HEIGHT=1.4
AGG_THEME="monokai"

# gifsicle optimization settings
GIFSICLE_OPTIMIZE=3
GIFSICLE_COLORS=256

# ============================================================================
# Utility Functions
# ============================================================================

# Print error message to stderr and exit
error() {
    echo "❌ ERROR: $1" >&2
    exit 1
}

# Print warning message to stderr
warn() {
    echo "⚠️  WARNING: $1" >&2
}

# Print info message to stdout
info() {
    echo "ℹ️  $1"
}

# Print success message to stdout
success() {
    echo "✅ $1"
}

# Format bytes as human-readable size
format_bytes() {
    local bytes=$1
    if [ "$bytes" -lt 1024 ]; then
        echo "${bytes}B"
    elif [ "$bytes" -lt 1048576 ]; then
        echo "$(echo "scale=2; $bytes / 1024" | bc)KB"
    else
        echo "$(echo "scale=2; $bytes / 1048576" | bc)MB"
    fi
}

# Get file size in bytes (cross-platform)
get_file_size() {
    local file=$1
    if command -v stat &>/dev/null; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            stat -f%z "$file" 2>/dev/null || echo "0"
        else
            stat -c%s "$file" 2>/dev/null || echo "0"
        fi
    else
        ls -lh "$file" | awk '{print $5}'
    fi
}

# ============================================================================
# Validation Functions
# ============================================================================

# Check if required commands are available
check_dependencies() {
    local missing_deps=()

    if ! command -v agg &>/dev/null; then
        missing_deps+=("agg")
    fi

    if ! command -v gifsicle &>/dev/null; then
        missing_deps+=("gifsicle")
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo "❌ Missing required dependencies: ${missing_deps[*]}" >&2
        echo "" >&2
        echo "Install with:" >&2
        echo "  brew install asciinema-agg gifsicle" >&2
        exit 1
    fi
}

# Validate that input file exists and is readable
validate_cast_file() {
    local cast_file=$1

    if [ ! -f "$cast_file" ]; then
        error "Input file does not exist: $cast_file"
    fi

    if [ ! -r "$cast_file" ]; then
        error "Input file is not readable: $cast_file"
    fi

    # Check file extension
    if [[ "$cast_file" != *.cast ]]; then
        error "Input file must have .cast extension: $cast_file"
    fi

    # Basic format validation: check if it's valid JSON
    if ! jq empty "$cast_file" 2>/dev/null; then
        error "Input file is not valid JSON (required for .cast format): $cast_file"
    fi
}

# Determine output path from input or use provided output
get_output_path() {
    local cast_file=$1
    local output_gif=$2
    local force_flag=$3

    # Use provided output path or derive from input
    local final_output="$output_gif"
    if [ -z "$final_output" ]; then
        final_output="${cast_file%.cast}.gif"
    fi

    # Check if output file already exists
    if [ -f "$final_output" ] && [ "$force_flag" != "true" ]; then
        echo "2"  # Special exit code for file exists
        return
    fi

    echo "$final_output"
}

# ============================================================================
# Conversion Functions
# ============================================================================

# Convert .cast file to .gif using agg
render_with_agg() {
    local cast_file=$1
    local temp_gif=$2

    info "Rendering with agg..."
    info "  Font size: ${AGG_FONT_SIZE}px"
    info "  Line height: ${AGG_LINE_HEIGHT}"
    info "  Theme: ${AGG_THEME}"

    if ! agg \
        --font-size "$AGG_FONT_SIZE" \
        --line-height "$AGG_LINE_HEIGHT" \
        --theme "$AGG_THEME" \
        "$cast_file" \
        "$temp_gif" 2>/dev/null; then
        error "agg rendering failed for: $cast_file"
    fi

    if [ ! -f "$temp_gif" ]; then
        error "agg did not produce output file: $temp_gif"
    fi

    success "Rendering complete"
}

# Optimize .gif file with gifsicle
optimize_with_gifsicle() {
    local input_gif=$1
    local output_gif=$2

    info "Optimizing with gifsicle..."
    info "  Optimization level: ${GIFSICLE_OPTIMIZE}"
    info "  Color palette: ${GIFSICLE_COLORS} colors"

    # Use in-place optimization or create new file if different
    if [ "$input_gif" = "$output_gif" ]; then
        if ! gifsicle \
            -O"${GIFSICLE_OPTIMIZE}" \
            --colors "${GIFSICLE_COLORS}" \
            "$input_gif" -o "$input_gif"; then
            error "gifsicle optimization failed"
        fi
    else
        if ! gifsicle \
            -O"${GIFSICLE_OPTIMIZE}" \
            --colors "${GIFSICLE_COLORS}" \
            "$input_gif" -o "$output_gif"; then
            error "gifsicle optimization failed"
        fi
    fi

    success "Optimization complete"
}

# ============================================================================
# Reporting Functions
# ============================================================================

# Report conversion statistics
report_conversion() {
    local cast_file=$1
    local output_gif=$2
    local start_time=$3

    local input_size=$(get_file_size "$cast_file")
    local output_size=$(get_file_size "$output_gif")
    local duration=$(($(date +%s) - start_time))

    # Calculate compression ratio (if output is smaller)
    local compression_ratio=0
    if [ "$output_size" -gt 0 ]; then
        compression_ratio=$(echo "scale=2; $input_size / $output_size" | bc)
    fi

    # Format human-readable sizes
    local input_size_human=$(format_bytes "$input_size")
    local output_size_human=$(format_bytes "$output_size")

    # Print summary
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "Conversion Summary"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "Input file:        $cast_file"
    echo "Output file:       $output_gif"
    echo ""
    echo "Input size:        $input_size_human ($input_size bytes)"
    echo "Output size:       $output_size_human ($output_size bytes)"
    echo "Compression ratio: ${compression_ratio}x"
    echo "Time elapsed:      ${duration}s"
    echo ""

    # Output JSON for automation
    cat << EOF
{
  "status": "success",
  "input_file": "$cast_file",
  "output_file": "$output_gif",
  "input_size_bytes": $input_size,
  "output_size_bytes": $output_size,
  "compression_ratio": $compression_ratio,
  "time_elapsed_seconds": $duration
}
EOF

    echo ""
}

# ============================================================================
# Main Conversion Function
# ============================================================================

convert_single() {
    local cast_file=$1
    local output_gif=${2:-}
    local force_flag=${3:-false}

    # Check for --force flag
    if [ "$force_flag" = "--force" ]; then
        force_flag="true"
    fi

    local start_time=$(date +%s)

    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║  .cast to .gif Converter (Phase 3)                      ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""

    # Validate input
    info "Validating input..."
    validate_cast_file "$cast_file"
    success "Input validation passed"
    echo ""

    # Determine output path
    info "Determining output path..."
    local output_result=$(get_output_path "$cast_file" "$output_gif" "$force_flag")

    # Check if file exists (special exit code 2)
    if [ "$output_result" = "2" ]; then
        local derived_output="${cast_file%.cast}.gif"
        if [ -n "$output_gif" ]; then
            derived_output="$output_gif"
        fi

        echo "❌ ERROR: Output file already exists: $derived_output" >&2
        echo "Use --force flag to overwrite" >&2
        exit 2
    fi

    local final_output="$output_result"
    success "Output path: $final_output"
    echo ""

    # Create temporary file for rendering
    local temp_gif=$(mktemp /tmp/cast-render-XXXXXX.gif)
    trap "rm -f '$temp_gif'" EXIT

    # Render with agg
    render_with_agg "$cast_file" "$temp_gif"
    echo ""

    # Optimize with gifsicle
    optimize_with_gifsicle "$temp_gif" "$final_output"
    echo ""

    # Report results
    report_conversion "$cast_file" "$final_output" "$start_time"

    success "Conversion complete!"
}

# ============================================================================
# Usage Information
# ============================================================================

show_usage() {
    cat << 'EOF'
Usage: convert-cast.sh <input.cast> [output.gif] [--force]

Arguments:
  input.cast      Path to .cast file (asciinema recording)
  output.gif      Output path for .gif file (optional, auto-derived if not provided)
  --force         Overwrite existing output file if it exists

Examples:
  # Auto-generate output filename
  convert-cast.sh recording.cast

  # Specify output filename
  convert-cast.sh demo.cast demo-output.gif

  # Overwrite existing file
  convert-cast.sh recording.cast --force

  # Specify output and force overwrite
  convert-cast.sh demo.cast output.gif --force

Exit codes:
  0   Success
  1   Error (missing dependencies, invalid input, conversion failed)
  2   File exists (use --force to overwrite)

Configuration:
  Font size:     16px
  Line height:   1.4
  Theme:         monokai
  GIF colors:    256
  Optimization:  Level 3 (maximum)

Dependencies:
  agg            - Asciinema GIF renderer
  gifsicle       - GIF optimization tool

Install with:
  brew install asciinema-agg gifsicle
EOF
}

# ============================================================================
# Entry Point
# ============================================================================

main() {
    # Check for help flag
    if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_usage
        exit 0
    fi

    # Validate arguments
    if [ $# -lt 1 ]; then
        error "Missing required argument: input.cast"
    fi

    local cast_file="$1"
    local output_gif="${2:-}"
    local force_flag="${3:-}"

    # Handle case where --force is second argument
    if [ "$output_gif" = "--force" ]; then
        force_flag="--force"
        output_gif=""
    fi

    # Check dependencies
    check_dependencies

    # Perform conversion
    convert_single "$cast_file" "$output_gif" "$force_flag"
}

# Run main function with all arguments
main "$@"
