#!/usr/bin/env bash
# scripts/formatting.sh - Unified formatting library for Craft
# v2.14.0 - Box-drawing, colors, tables, and ANSI-aware padding
#
# Usage:
#   source "$(dirname "${BASH_SOURCE[0]}")/formatting.sh"
#   box_header "Title"
#   box_row "Content with ${FMT_GREEN}color${FMT_NC}"
#   box_footer
#
# All boxes default to 63 visible characters wide.

# Source guard — prevent double-loading
[[ -n "${_FMT_LOADED:-}" ]] && return 0
_FMT_LOADED=1

# ============================================================================
# Color Constants (FMT_ prefix avoids collisions with script-local vars)
# ============================================================================

FMT_RED='\033[0;31m'
FMT_GREEN='\033[0;32m'
FMT_YELLOW='\033[1;33m'
FMT_CYAN='\033[1;36m'
FMT_BLUE='\033[0;34m'
FMT_BOLD='\033[1m'
FMT_DIM='\033[2m'
FMT_NC='\033[0m'

# ============================================================================
# Configuration
# ============================================================================

_FMT_WIDTH=63
_FMT_STYLE=""  # "double" or "single" — set by box_header/box_single

# Box characters — double line
_FMT_D_TL='╔' _FMT_D_TR='╗' _FMT_D_BL='╚' _FMT_D_BR='╝'
_FMT_D_H='═'  _FMT_D_V='║'  _FMT_D_ML='╠' _FMT_D_MR='╣'

# Box characters — single line
_FMT_S_TL='┌' _FMT_S_TR='┐' _FMT_S_BL='└' _FMT_S_BR='┘'
_FMT_S_H='─'  _FMT_S_V='│'  _FMT_S_ML='├' _FMT_S_MR='┤'

# ============================================================================
# Internal Utilities
# ============================================================================

# Strip ANSI escape codes from text for width calculation
_fmt_strip_ansi() {
    local text="$1"
    printf '%b' "$text" | sed $'s/\033\[[0-9;]*m//g'
}

# Calculate visible length of text (excluding ANSI codes)
_fmt_visible_len() {
    local stripped
    stripped=$(_fmt_strip_ansi "$1")
    echo ${#stripped}
}

# Repeat a character N times
_fmt_repeat() {
    local char="$1" count="$2"
    if (( count <= 0 )); then
        return
    fi
    printf '%0.s'"$char" $(seq 1 "$count")
}

# Get current box characters based on active style
_fmt_get_v() {
    if [[ "$_FMT_STYLE" == "double" ]]; then
        echo "$_FMT_D_V"
    else
        echo "$_FMT_S_V"
    fi
}

# ============================================================================
# Public API
# ============================================================================

# Set custom width (default: 63)
fmt_set_width() {
    _FMT_WIDTH="${1:-63}"
}

# Print a standalone divider line (no box context needed)
# Usage: fmt_divider [char] [width]
fmt_divider() {
    local char="${1:-═}" width="${2:-$_FMT_WIDTH}"
    _fmt_repeat "$char" "$width"
    echo
}

# --- Box Opening Functions ---

# Open a double-line box with title
# Usage: box_header "Title" [color]
box_header() {
    local title="$1"
    local color="${2:-}"
    _FMT_STYLE="double"

    local inner=$(( _FMT_WIDTH - 2 ))  # inside the two border chars

    # Top border: ╔═══...═══╗
    printf '%s' "$_FMT_D_TL"
    _fmt_repeat "$_FMT_D_H" "$inner"
    printf '%s\n' "$_FMT_D_TR"

    # Title row
    local display_title="$title"
    if [[ -n "$color" ]]; then
        display_title="${color}${title}${FMT_NC}"
    fi
    box_row "  $display_title"

    # Separator: ╠═══...═══╣
    printf '%s' "$_FMT_D_ML"
    _fmt_repeat "$_FMT_D_H" "$inner"
    printf '%s\n' "$_FMT_D_MR"
}

# Open a single-line box with title
# Usage: box_single "Title" [color]
box_single() {
    local title="$1"
    local color="${2:-}"
    _FMT_STYLE="single"

    local inner=$(( _FMT_WIDTH - 2 ))

    # Top border: ┌───...───┐
    printf '%s' "$_FMT_S_TL"
    _fmt_repeat "$_FMT_S_H" "$inner"
    printf '%s\n' "$_FMT_S_TR"

    # Title row
    local display_title="$title"
    if [[ -n "$color" ]]; then
        display_title="${color}${title}${FMT_NC}"
    fi
    box_row "  $display_title"

    # Separator: ├───...───┤
    printf '%s' "$_FMT_S_ML"
    _fmt_repeat "$_FMT_S_H" "$inner"
    printf '%s\n' "$_FMT_S_MR"
}

# --- Box Content Functions ---

# Print a content row with side borders and ANSI-aware right-padding
# Usage: box_row "text" [color]
box_row() {
    local text="$1"
    local color="${2:-}"
    local v
    v=$(_fmt_get_v)

    local inner=$(( _FMT_WIDTH - 2 ))

    if [[ -n "$color" ]]; then
        text="${color}${text}${FMT_NC}"
    fi

    local visible_len
    visible_len=$(_fmt_visible_len "$text")
    local pad=$(( inner - visible_len ))

    if (( pad < 0 )); then
        pad=0
    fi

    printf '%s' "$v"
    printf '%b' "$text"
    printf '%*s' "$pad" ""
    printf '%s\n' "$v"
}

# Print an empty bordered row
box_empty_row() {
    local v
    v=$(_fmt_get_v)
    local inner=$(( _FMT_WIDTH - 2 ))

    printf '%s' "$v"
    printf '%*s' "$inner" ""
    printf '%s\n' "$v"
}

# Print a mid-box separator (matches current style)
box_separator() {
    local inner=$(( _FMT_WIDTH - 2 ))

    if [[ "$_FMT_STYLE" == "double" ]]; then
        printf '%s' "$_FMT_D_ML"
        _fmt_repeat "$_FMT_D_H" "$inner"
        printf '%s\n' "$_FMT_D_MR"
    else
        printf '%s' "$_FMT_S_ML"
        _fmt_repeat "$_FMT_S_H" "$inner"
        printf '%s\n' "$_FMT_S_MR"
    fi
}

# Close the box (matches current style, resets state)
box_footer() {
    local inner=$(( _FMT_WIDTH - 2 ))

    if [[ "$_FMT_STYLE" == "double" ]]; then
        printf '%s' "$_FMT_D_BL"
        _fmt_repeat "$_FMT_D_H" "$inner"
        printf '%s\n' "$_FMT_D_BR"
    else
        printf '%s' "$_FMT_S_BL"
        _fmt_repeat "$_FMT_S_H" "$inner"
        printf '%s\n' "$_FMT_S_BR"
    fi

    _FMT_STYLE=""
}

# --- Table Functions ---

# Print table rows with pipe-delimited columns
# Usage: box_table "Col1|Col2|Col3" "val1|val2|val3" ...
# First argument is the header, rest are data rows
box_table() {
    local header="$1"
    shift

    local v
    v=$(_fmt_get_v)
    local inner=$(( _FMT_WIDTH - 2 ))

    # Parse header into columns and calculate widths
    IFS='|' read -ra cols <<< "$header"
    local num_cols=${#cols[@]}

    # Calculate equal column widths
    # Account for spacing: each col gets " content " with "|" separators
    # Total inner = col1 + " | " + col2 + " | " + col3 ...
    # separators = (num_cols - 1) * 3
    local separators_width=$(( (num_cols - 1) * 3 ))
    local available=$(( inner - 2 - separators_width ))  # -2 for leading/trailing space
    local col_width=$(( available / num_cols ))

    # Print header row
    printf '%s ' "$v"
    for (( i=0; i<num_cols; i++ )); do
        local col_text="${cols[$i]}"
        local vis_len
        vis_len=$(_fmt_visible_len "$col_text")
        local cpad=$(( col_width - vis_len ))
        if (( cpad < 0 )); then cpad=0; fi

        printf '%b%*s' "$col_text" "$cpad" ""
        if (( i < num_cols - 1 )); then
            printf ' | '
        fi
    done
    # Right-pad to fill the row
    local row_text
    row_text=$(printf ' ')
    for (( i=0; i<num_cols; i++ )); do
        local col_text="${cols[$i]}"
        local vis_len
        vis_len=$(_fmt_visible_len "$col_text")
        local cpad=$(( col_width - vis_len ))
        if (( cpad < 0 )); then cpad=0; fi
        row_text+=$(printf '%s%*s' "$col_text" "$cpad" "")
        if (( i < num_cols - 1 )); then
            row_text+=" | "
        fi
    done
    local row_vis_len=${#row_text}
    local rpad=$(( inner - row_vis_len ))
    if (( rpad > 0 )); then
        printf '%*s' "$rpad" ""
    fi
    printf '%s\n' "$v"

    # Print data rows
    for row in "$@"; do
        IFS='|' read -ra vals <<< "$row"

        printf '%s ' "$v"
        row_text=" "
        for (( i=0; i<num_cols; i++ )); do
            local val="${vals[$i]:-}"
            local vis_len
            vis_len=$(_fmt_visible_len "$val")
            local cpad=$(( col_width - vis_len ))
            if (( cpad < 0 )); then cpad=0; fi

            printf '%b%*s' "$val" "$cpad" ""
            row_text+=$(printf '%s%*s' "$(_fmt_strip_ansi "$val")" "$cpad" "")
            if (( i < num_cols - 1 )); then
                printf ' | '
                row_text+=" | "
            fi
        done
        row_vis_len=${#row_text}
        rpad=$(( inner - row_vis_len ))
        if (( rpad > 0 )); then
            printf '%*s' "$rpad" ""
        fi
        printf '%s\n' "$v"
    done
}
