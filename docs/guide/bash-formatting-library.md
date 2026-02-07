# Bash Formatting Library: `scripts/formatting.sh`

> **TL;DR:**
>
> - **What:** Shared bash library for box-drawing, color constants, and ANSI-aware padding
> - **Why:** Eliminates duplication across 20+ scripts — one source of truth for visual output
> - **How:** `source "$SCRIPT_DIR/formatting.sh"` then use `box_header`, `box_row`, `box_footer`
> - **Applies to:** All scripts in `scripts/`, `scripts/installers/`, `scripts/hooks/`

## Overview

The formatting library (`scripts/formatting.sh`) provides a unified API for terminal output styling. Before v2.14.0, each script defined its own color variables and hand-coded box-drawing characters, leading to:

- Inconsistent box widths (61, 62, 63 chars across scripts)
- Duplicated color definitions in 20+ scripts
- Manual ANSI-aware padding calculations
- Fragile alignment that broke when content changed

The library standardizes on 63 visible characters width, provides both double-line (╔═╗) and single-line (┌─┐) box styles, and handles ANSI escape code stripping automatically.

## Color Constants

All color constants use the `FMT_` prefix to avoid collisions:

```bash
FMT_RED='\033[0;31m'    FMT_GREEN='\033[0;32m'
FMT_YELLOW='\033[1;33m' FMT_CYAN='\033[1;36m'
FMT_BLUE='\033[0;34m'   FMT_BOLD='\033[1m'
FMT_DIM='\033[2m'       FMT_NC='\033[0m'
```

For backward compatibility, scripts can alias:

```bash
source "$SCRIPT_DIR/formatting.sh"
RED="$FMT_RED" GREEN="$FMT_GREEN" NC="$FMT_NC"
```

## Box-Drawing API

### Double-Line Box (`box_header`)

Used for main headers, important notices:

```bash
box_header "TOOL HEALTH CHECK REPORT"
box_row "asciinema: OK"
box_row "agg: OK"
box_separator
box_row "All required tools are healthy" "$FMT_GREEN"
box_footer
```

Output:

```text
╔═══════════════════════════════════════════════════════════════╗
║  TOOL HEALTH CHECK REPORT                                     ║
╠═══════════════════════════════════════════════════════════════╣
║ asciinema: OK                                                 ║
║ agg: OK                                                       ║
╠═══════════════════════════════════════════════════════════════╣
║ All required tools are healthy                                ║
╚═══════════════════════════════════════════════════════════════╝
```

### Single-Line Box (`box_single`)

Used for secondary content, prompts:

```bash
box_single "INSTALLATION REQUIRED" "$FMT_BOLD"
box_empty_row
box_row " Tool: ffmpeg"
box_row " Method: brew install ffmpeg"
box_footer
```

### Key Functions

| Function                         | Purpose                                 | Example                               |
| -------------------------------- | --------------------------------------- | ------------------------------------- |
| `box_header "title" [color]`     | Double-line top + title + separator     | `box_header "REPORT"`                 |
| `box_single "title" [color]`     | Single-line top + title + separator     | `box_single "PROMPT" "$FMT_BOLD"`     |
| `box_row "text" [color]`         | Content row with ANSI-aware padding     | `box_row "Status: OK" "$FMT_GREEN"`   |
| `box_empty_row`                  | Empty bordered row for spacing          | `box_empty_row`                       |
| `box_separator`                  | Mid-box divider (matches current style) | `box_separator`                       |
| `box_footer`                     | Close box and reset state               | `box_footer`                          |
| `box_table "H1\|H2" "v1\|v2"`    | Pipe-delimited table rows               | `box_table "Name\|Version"`           |
| `fmt_set_width N`                | Override default width (63)             | `fmt_set_width 80`                    |
| `fmt_divider [char] [width]`     | Standalone divider line                 | `fmt_divider "=" 40`                  |

## ANSI-Aware Padding

The library automatically strips ANSI escape codes when calculating visible width. This means colored content aligns correctly:

```bash
box_row "Status: ${FMT_GREEN}OK${FMT_NC}"     # "OK" in green, border at col 63
box_row "Status: ${FMT_RED}FAIL${FMT_NC}"     # "FAIL" in red, border at col 63
```

Internal functions:

- `_fmt_strip_ansi "text"` — Removes all `\033[...m` sequences
- `_fmt_visible_len "text"` — Returns visible character count (excluding ANSI)

## Source Guard

The library uses a source guard to prevent double-loading:

```bash
[[ -n "${_FMT_LOADED:-}" ]] && return 0; _FMT_LOADED=1
```

Safe to source multiple times — second source is a no-op.

## Custom Width

Default is 63 visible characters. Override with:

```bash
source "$SCRIPT_DIR/formatting.sh"
fmt_set_width 80
box_header "Wide Box"
box_row "Content"
box_footer
# Width resets to 63 after box_footer
```

Note: `box_footer` resets width to the default (63).

## Migrating Your Script

### Step 1: Source the library

For scripts in `scripts/`:

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/formatting.sh"
```

For scripts in `scripts/installers/` or `scripts/hooks/`:

```bash
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/formatting.sh"
```

### Step 2: Replace color definitions

Before:

```bash
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'
```

After:

```bash
source "$SCRIPT_DIR/formatting.sh"
RED="$FMT_RED" GREEN="$FMT_GREEN" NC="$FMT_NC"
```

### Step 3: Replace box-drawing echo blocks

Before:

```bash
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  MY REPORT                                              ║"
echo "╠═══════════════════════════════════════════════════════════╣"
echo "║ Some content                                            ║"
echo "╚═══════════════════════════════════════════════════════════╝"
```

After:

```bash
box_header "MY REPORT"
box_row "Some content"
box_footer
```

### Step 4: Test

```bash
bash tests/test_formatting.sh   # 74 library tests
bash your-script.sh             # Visual check
your-script.sh | cat            # Verify no color leaks
```

## Troubleshooting

| Issue              | Fix                                                                           |
| ------------------ | ----------------------------------------------------------------------------- |
| Box width wrong    | Check `fmt_set_width` calls; `box_footer` resets to 63                        |
| Colors not showing | Ensure terminal supports ANSI; check `FMT_NC` reset                           |
| Double borders     | Check source guard: `_FMT_LOADED` should prevent double-source                |
| Content overflows  | `box_row` truncation is not automatic; keep content under width-2 chars       |
| Emoji width off    | Emoji are 2-char wide in some terminals; library counts them as visible chars |

## Related

- [Formatting Library Spec](../specs/_archive/SPEC-styled-output-v2.14.0-2026-02-05.md)
- [Quick Reference Card](../reference/REFCARD-FORMATTING.md)
- [Changelog](../CHANGELOG.md)
