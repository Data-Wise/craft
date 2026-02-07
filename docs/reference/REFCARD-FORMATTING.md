# Quick Reference: Formatting Library

**One library for all terminal output styling** — Box-drawing, colors, ANSI-aware padding, standardized at 63 characters.

**Version:** 2.14.0 | **Location:** `scripts/formatting.sh` | **Tests:** 74 passing

---

## Quick Start

```bash
# Source in your script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/formatting.sh"

# Draw a box
box_header "MY TITLE"
box_row "Content line"
box_row "Colored" "$FMT_GREEN"
box_footer
```

---

## Function Reference

| Function | Signature | Purpose |
|----------|-----------|---------|
| `box_header` | `box_header "title" [color]` | Double-line box top with title |
| `box_single` | `box_single "title" [color]` | Single-line box top with title |
| `box_row` | `box_row "text" [color]` | Content row, ANSI-aware padding |
| `box_empty_row` | `box_empty_row` | Empty bordered row |
| `box_separator` | `box_separator` | Mid-box divider (matches style) |
| `box_footer` | `box_footer` | Close box, reset state |
| `box_table` | `box_table "H1\|H2" "v1\|v2"` | Pipe-delimited table row |
| `fmt_set_width` | `fmt_set_width N` | Override default width |
| `fmt_divider` | `fmt_divider [char] [width]` | Standalone divider line |

---

## Color Constants

| Constant | Value | Preview |
|----------|-------|---------|
| `$FMT_RED` | `\033[0;31m` | Error text |
| `$FMT_GREEN` | `\033[0;32m` | Success text |
| `$FMT_YELLOW` | `\033[1;33m` | Warning text |
| `$FMT_CYAN` | `\033[1;36m` | Info/headers |
| `$FMT_BLUE` | `\033[0;34m` | Accents |
| `$FMT_BOLD` | `\033[1m` | Emphasis |
| `$FMT_DIM` | `\033[2m` | Muted text |
| `$FMT_NC` | `\033[0m` | Reset (No Color) |

---

## Box Styles

### Double-Line (headers, reports)

```
╔═════════════════════════════════════════════════════════════╗
║  Title                                                      ║
╠═════════════════════════════════════════════════════════════╣
║ Content                                                     ║
╚═════════════════════════════════════════════════════════════╝
```

### Single-Line (prompts, secondary)

```
┌─────────────────────────────────────────────────────────────┐
│  Title                                                      │
├─────────────────────────────────────────────────────────────┤
│ Content                                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Common Patterns

### Report Box

```bash
box_header "HEALTH CHECK REPORT"
box_row "Tool A: ${FMT_GREEN}OK${FMT_NC}"
box_row "Tool B: ${FMT_RED}FAIL${FMT_NC}"
box_separator
box_row "1 issue found" "$FMT_YELLOW"
box_footer
```

### Consent Prompt

```bash
box_single "INSTALLATION REQUIRED" "$FMT_BOLD"
box_empty_row
box_row " Tool: ffmpeg"
box_row " Size: ~50MB"
box_empty_row
box_footer
```

### Redirect to stderr

```bash
{
    box_single "Warning" "$FMT_YELLOW"
    box_row "Something happened"
    box_footer
} >&2
```

### Custom Width

```bash
fmt_set_width 80
box_header "Wide Box"
box_row "Content in 80-char box"
box_footer  # Resets to 63
```

---

## Source Paths

| Script Location | Source Pattern |
|----------------|---------------|
| `scripts/*.sh` | `source "$SCRIPT_DIR/formatting.sh"` |
| `scripts/installers/*.sh` | `source "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/formatting.sh"` |
| `scripts/hooks/*.sh` | `source "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/formatting.sh"` |
| `install.sh` (root) | `source "$SCRIPT_DIR/scripts/formatting.sh"` |

---

## Internal Functions

| Function | Purpose |
|----------|---------|
| `_fmt_strip_ansi "text"` | Remove ANSI escape codes |
| `_fmt_visible_len "text"` | Count visible characters |
| `_fmt_repeat "char" N` | Repeat character N times |

---

## Quick Troubleshooting

| Symptom | Fix |
|---------|-----|
| Width wrong after custom box | `box_footer` resets width; check call order |
| Colors bleed past box | Ensure `box_footer` is called; check `$FMT_NC` |
| Double-sourcing warnings | None — source guard (`_FMT_LOADED`) prevents this |
| Borders misaligned with emoji | Emoji are 2 display-chars; count carefully |

---

## See Also

- [Full Guide](../guide/bash-formatting-library.md)
- [Spec](../specs/_archive/SPEC-styled-output-v2.14.0-2026-02-05.md)
- 74 Tests: `tests/test_formatting.sh`
