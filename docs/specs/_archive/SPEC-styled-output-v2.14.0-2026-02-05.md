# SPEC: Unified Bash Formatting Library — v2.14.0

**Date:** 2026-02-05
**Status:** In Progress
**Branch:** `feature/styled-output`

## Problem

20+ scripts duplicate color definitions (RED, GREEN, YELLOW, CYAN, BOLD, NC). Eight scripts implement box-drawing with inconsistent widths (61-63 chars), styles (echo, printf, heredoc), and broken alignment when ANSI codes or dynamic variables are present.

## Solution

Create `scripts/formatting.sh` — a shared bash library providing:

1. **Color constants** with `FMT_` prefix (avoids collisions with existing vars)
2. **Box-drawing functions** (double-line and single-line styles)
3. **ANSI-aware width calculation** for correct padding with colored text
4. **Table formatting** for structured data display
5. **Source guard** to prevent double-loading

## API

| Function | Purpose |
|----------|---------|
| `box_header "Title" [color]` | Double-line top + title + separator |
| `box_single "Title" [color]` | Single-line top + title + separator |
| `box_row "text" [color]` | Content row with side borders, ANSI-aware padding |
| `box_separator` | Mid-box divider (auto-matches current style) |
| `box_footer` | Close box (auto-matches style, resets state) |
| `box_table "Col1\|Col2" "val1\|val2"` | Column-padded table rows |
| `box_empty_row` | Empty bordered row |
| `fmt_set_width N` | Override default width (63) |
| `fmt_divider [char] [width]` | Standalone divider line |
| `_fmt_strip_ansi "text"` | Internal: strip ANSI for width calc |

## Standard Width

All boxes standardized to **63 visible characters** (width 61 → 63 for older scripts).

## Migration Order

1. Library + tests
2. Static double-line boxes (install.sh, migrate-from-workflow.sh, convert-cast.sh)
3. Health-check with colors
4. Consent-prompt (single-line + printf)
5. Dependency-installer (heredoc)
6. Dependency-manager (complex table)
7. Plain-text scripts (colors only)
8. Sub-scripts (installers, hooks, utilities)

## Verification

- All 55+ formatting tests pass
- Each migrated script renders correctly
- All box lines exactly 63 visible chars
- Existing test suites still pass (1174 tests)
