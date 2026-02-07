---
title: "Tutorial: Migrate Your Script to the Formatting Library"
description: "Step-by-step guide to eliminating duplicated color definitions and hand-coded box drawing from bash scripts"
category: tutorial
level: intermediate
time: 15 minutes
prerequisites:
  - Basic bash scripting
  - Familiarity with ANSI escape codes
tags:
  - formatting
  - migration
  - refactoring
  - bash
related:
  - ../guide/bash-formatting-library.md
  - ../reference/REFCARD-FORMATTING.md
  - ../specs/_archive/SPEC-styled-output-v2.14.0-2026-02-05.md
version: 2.14.0
last_updated: 2026-02-05
---

# Tutorial: Migrate Your Script to the Formatting Library

> Eliminate duplicated color definitions and hand-coded box drawing from your bash scripts in under 15 minutes.

**Level:** Intermediate | **Time:** 15 minutes | **Prerequisites:** Basic bash scripting

---

## What You'll Learn

1. How to source `formatting.sh` from any script location
2. Replace duplicated color variables with shared `FMT_` constants
3. Replace hand-coded box-drawing with library functions
4. Test your migration for width consistency

---

## Part 1: Assess Your Script

Before migrating, identify what your script uses:

**Color definitions** (replace with `FMT_` constants):

```bash
# Look for patterns like these:
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'
```

**Box-drawing characters** (replace with library functions):

```bash
# Look for echo/printf with box chars:
echo "╔═══════════════════════════╗"
echo "║  Title                   ║"
echo "╚═══════════════════════════╝"
```

**Divider lines** (replace with `fmt_divider`):

```bash
echo "=========================================="
echo "──────────────────────────────────────────"
```

---

## Part 2: Source the Library

The source path depends on where your script lives:

### Scripts in `scripts/`

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/formatting.sh"
```

### Scripts in `scripts/installers/` or `scripts/hooks/`

```bash
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/formatting.sh"
```

### Root-level scripts (`install.sh`)

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/scripts/formatting.sh"
```

---

## Part 3: Replace Color Definitions

### Before

```bash
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${GREEN}Success${NC}"
```

### After (if you want to keep short names)

```bash
source "$SCRIPT_DIR/formatting.sh"
RED="$FMT_RED" GREEN="$FMT_GREEN" YELLOW="$FMT_YELLOW"
CYAN="$FMT_CYAN" BOLD="$FMT_BOLD" NC="$FMT_NC"

echo -e "${GREEN}Success${NC}"  # Works identically
```

### After (using FMT_ directly)

```bash
source "$SCRIPT_DIR/formatting.sh"

echo -e "${FMT_GREEN}Success${FMT_NC}"
```

---

## Part 4: Replace Box-Drawing

### Example: Double-Line Box

**Before (27 lines):**

```bash
echo "╔═════════════════════════════════════════════════════════════╗"
echo "║  Craft Plugin Installer for Claude Code                   ║"
echo "╠═════════════════════════════════════════════════════════════╣"
echo "║                                                           ║"
echo "║  📦 Installing: craft v2.14.0                             ║"
echo "║  📍 Location: ~/.claude/plugins/craft                     ║"
echo "║                                                           ║"
echo "╚═════════════════════════════════════════════════════════════╝"
```

**After (7 lines):**

```bash
box_header "Craft Plugin Installer for Claude Code"
box_empty_row
box_row "  📦 Installing: craft v${VERSION}"
box_row "  📍 Location: ~/.claude/plugins/craft"
box_empty_row
box_footer
```

Benefits:

- Dynamic variables (`$VERSION`) automatically padded
- Width always 63 visible characters
- No manual alignment needed

### Example: Single-Line Box with Colors

**Before:**

```bash
printf '┌─────────────────────────────────────────────────────────────┐\n'
printf '│  %-57s  │\n' "INSTALLATION REQUIRED"
printf '├─────────────────────────────────────────────────────────────┤\n'
printf '│  Tool: %-51s  │\n' "$tool_name"
printf '└─────────────────────────────────────────────────────────────┘\n'
```

**After:**

```bash
box_single "INSTALLATION REQUIRED" "$FMT_BOLD"
box_row "Tool: $tool_name"
box_footer
```

### Example: Colored Content Rows

**Before:**

```bash
printf '║ %-55s ║\n' "$(echo -e "Status: ${GREEN}OK${NC}")"
# Manual visible-length calculation needed!
```

**After:**

```bash
box_row "Status: ${FMT_GREEN}OK${FMT_NC}"
# ANSI-aware padding handles alignment automatically
```

---

## Part 5: Replace Dividers

**Before:**

```bash
echo "==========================================="
echo "──────────────────────────────────────────"
```

**After:**

```bash
fmt_divider "=" 43
fmt_divider "─" 42
```

---

## Part 6: Test Your Migration

### 1. Run syntax check

```bash
bash -n your-script.sh
```

### 2. Run the formatting test suite

```bash
bash tests/test_formatting.sh
```

### 3. Visual check

Run your script and verify boxes look correct.

### 4. Width verification

```bash
your-script.sh 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | while IFS= read -r line; do
  if [[ "$line" == *"║"* || "$line" == *"│"* ]]; then
    echo "${#line}: $line"
  fi
done
```

All box lines should be exactly 63 characters.

### 5. Color leak check

```bash
your-script.sh | cat
# Should see no raw ANSI escape codes after box output
```

---

## Checklist

- [ ] Source `formatting.sh` with correct path for your script location
- [ ] Replace all local color definitions with `FMT_` constants (or aliases)
- [ ] Replace echo/printf box-drawing with `box_header`/`box_single`/`box_row`/`box_footer`
- [ ] Replace divider lines with `fmt_divider`
- [ ] Test: syntax check passes (`bash -n`)
- [ ] Test: visual output looks correct
- [ ] Test: all box lines are 63 visible chars
- [ ] Test: no color leaks (`| cat`)

---

## Common Migration Patterns

### Pattern 1: Simple Status Box

**Before:**

```bash
echo "╔════════════════════════════╗"
echo "║ Status: OK                 ║"
echo "╚════════════════════════════╝"
```

**After:**

```bash
box_single "Status: OK"
```

### Pattern 2: Multi-Section Box

**Before:**

```bash
echo "╔════════════════════════════╗"
echo "║ Section 1                  ║"
echo "╠════════════════════════════╣"
echo "║ Section 2                  ║"
echo "╚════════════════════════════╝"
```

**After:**

```bash
box_header "Section 1"
box_divider
box_row "Section 2"
box_footer
```

### Pattern 3: Colored Headers

**Before:**

```bash
echo -e "╔════════════════════════════╗"
echo -e "║ ${GREEN}Success${NC}                 ║"
echo -e "╚════════════════════════════╝"
```

**After:**

```bash
box_single "Success" "$FMT_GREEN"
```

---

## Troubleshooting

### Box width looks wrong

**Problem:** Lines don't align or width varies

**Solution:** Verify you're using ANSI-aware padding:

```bash
# Wrong - uses visible length including ANSI codes
printf '║ %-59s ║\n' "${GREEN}text${NC}"

# Right - strips ANSI before calculating padding
box_row "${FMT_GREEN}text${FMT_NC}"
```

### Colors bleed into next line

**Problem:** Text after box is still colored

**Solution:** Ensure `box_footer` is called (it includes `$FMT_NC`):

```bash
box_header "Title"
box_row "Content"
box_footer  # REQUIRED - resets color
```

### Source path not found

**Problem:** `formatting.sh: No such file or directory`

**Solution:** Check your script's location and adjust the relative path:

```bash
# Debug: print resolved path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Script dir: $SCRIPT_DIR"
echo "Looking for: $SCRIPT_DIR/formatting.sh"
```

---

## See Also

- [Formatting Library Guide](../guide/bash-formatting-library.md) — Full API documentation
- [Quick Reference Card](../reference/REFCARD-FORMATTING.md) — Function cheat sheet
- [Spec](../specs/_archive/SPEC-styled-output-v2.14.0-2026-02-05.md) — Design specification
- Test Suite: `tests/test_formatting.sh` — 74 validation tests

---

**Next Steps:**

1. Migrate your first script using this tutorial
2. Run the test suite to validate formatting
3. Review the [Formatting Library Guide](../guide/bash-formatting-library.md) for advanced features
4. Contribute improvements to the library
