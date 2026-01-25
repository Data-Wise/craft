# GIF Regeneration Guide

**Purpose**: Regenerate all workflow GIFs with accurate output from real `/craft` command execution

**Problem**: Current GIFs show simulated output in bash terminal, not actual Claude Code plugin output

**Solution**: Use asciinema to record real sessions → Convert → Optimize

---

## Quick Start (asciinema method - recommended)

```bash
# 1. Record real session
asciinema rec docs/demos/teaching-workflow.cast

# In Claude Code, run your commands:
# /craft:git:status
# /craft:site:build
# ... etc
# Press Ctrl+D when done

# 2. Convert to GIF (single file)
/craft:docs:demo --convert docs/demos/teaching-workflow.cast

# OR: Batch convert all .cast files
/craft:docs:demo --batch

# 3. Review
open docs/demos/teaching-workflow.gif
```

## Batch Conversion (New in v1.25.0)

**Convert all `.cast` files at once:**

```bash
# Dry run - preview what would be converted
/craft:docs:demo --batch --dry-run

# Convert all new .cast files (skip existing GIFs)
/craft:docs:demo --batch

# Force overwrite all GIFs
/craft:docs:demo --batch --force

# Custom search path
/craft:docs:demo --batch --search-path custom/demos
```

**What batch conversion does:**

- Finds all `.cast` files in `docs/demos/` and `docs/gifs/`
- Skips existing `.gif` files (unless `--force`)
- Shows progress bar with ETA
- Uses optimized settings: `agg` (font-size 16, monokai) + `gifsicle` (optimize=3, 256 colors)
- Reports compression ratios and total size savings

**Progress output:**

```
Processing .cast files...
[████████████░░░░░░░] 8/11 (73%)

Current: docs/demos/install-demo.cast
Status: Converting... (3.2s elapsed)
ETA: 2m 35s

Summary (so far):
  Completed: 8/11
  Failed: 0
  Total size: 2.3 MB → 890 KB (61% reduction)
  Avg time: 3.1s per file
```

## Alternative: VHS Method

If you need scripted/repeatable demos:

```bash
# 1. Update VHS tapes with accurate output
# Edit .tape files in docs/demos/ and docs/gifs/

# 2. Regenerate all GIFs
./scripts/regenerate-gifs.sh

# 3. Review GIFs
open docs/demos/*.gif docs/gifs/*.gif
```

---

## Command Verification (DO THIS FIRST!)

**Before regenerating GIFs, test each `/craft` command in Claude Code to capture real output.**

### GIF 1: Teaching Workflow (`docs/demos/teaching-workflow.tape`)

**Commands to test:**

```bash
/craft:git:status
/craft:site:build
/craft:site:progress
/craft:site:publish --dry-run
/craft:site:publish
```

**What to capture:**

- Exact output format (boxes, icons, text)
- Timing (how long each command takes)
- Color scheme
- Progress indicators

**How to test:**

1. Open Claude Code in terminal
2. Navigate to a teaching project (with `.flow/teach-config.yml`)
3. Run each command above
4. Screenshot or copy-paste the output
5. Note the format and timing

**Update tape with real output:**

- Replace simulated `Type` commands with accurate output
- Match the exact format you saw
- Adjust `Sleep` values to match real timing

---

### GIF 2-11: Workflow Demos (`docs/gifs/workflow-*.tape`)

| GIF | Command | What to Test |
|-----|---------|--------------|
| 01 | `/craft:docs:update` | Output format, file counts, timing |
| 02 | `/craft:site:create --preset adhd-focus --quick` | Interactive prompts, preset output |
| 03 | `/craft:check --for release` | Validation results, checklist format |
| 04 | `/craft:do add user authentication with JWT` | Task breakdown, agent spawning |
| 05 | `/craft:test:run debug` | Test output, pass/fail format |
| 06 | `/craft:code:lint optimize` | Lint results, file list format |
| 07 | `/craft:git:worktree add feature-auth` | Worktree creation, path output |
| 08 | `/craft:dist:homebrew setup` | Setup steps, formula generation |
| 09 | `/craft:check --for commit` | Pre-commit checks, validation |
| 10 | `/craft:orchestrate 'prepare v2.0 release' release` | Orchestrator dashboard, agent status |

**For each command:**

1. Run in Claude Code (not bash!)
2. Capture the exact output
3. Note any interactive elements
4. Time how long it takes
5. Update the corresponding `.tape` file

---

## Recording Workflow

### Method 1: asciinema (Recommended)

**For recording real Claude Code sessions:**

```bash
# 1. Start recording
asciinema rec docs/demos/command-name.cast

# 2. Run commands in Claude Code
/craft:command1
# Wait for output...
/craft:command2
# Wait for output...

# 3. Stop recording
# Press Ctrl+D or type 'exit'

# 4. Preview
asciinema play docs/demos/command-name.cast

# 5. Convert to GIF
agg --cols 100 --rows 30 --font-size 14 --fps 10 \
    docs/demos/command-name.cast \
    docs/demos/command-name.gif

# 6. Optimize
gifsicle -O3 --colors 128 --lossy=80 \
    docs/demos/command-name.gif \
    -o docs/demos/command-name.gif
```

### Method 2: VHS Tape Update (Alternative)

**For scripted/repeatable demos:**

**Example: Updating teaching-workflow.tape**

#### Before (Simulated)

```tape
Type "$ /craft:site:build"
Enter
Sleep 300ms
Type "✓ Built successfully"
```

#### After (Accurate)

```tape
Type "$ /craft:site:build"
Enter
Sleep 500ms
Type "┌─────────────────────────────────────────┐"
Enter
Type "│ 🏗️  Building Site                       │"
Enter
Type "│                                         │"
Enter
Type "│ Course: STAT 545 Fall 2024              │"
Enter
Type "│ Week 8/15 (53%)                         │"
Enter
Type "│                                         │"
Enter
Type "│ ✓ Built successfully                    │"
Enter
Type "│ Output: site/ (450 files, 2.3 MB)       │"
Enter
Type "└─────────────────────────────────────────┘"
Sleep 2s
```

**Key differences:**

- Shows actual box formatting
- Includes course info
- Shows file count and size
- Realistic timing (500ms + 2s)

---

## Regeneration Script

**Location**: `scripts/regenerate-gifs.sh`

**What it does:**

1. Backs up existing GIFs
2. Runs VHS on each `.tape` file
3. Optimizes with gifsicle (`-O3 --colors 128 --lossy=80`)
4. Verifies size is ≤ 2MB
5. Reports results

**Usage:**

```bash
# Regenerate all GIFs
./scripts/regenerate-gifs.sh

# Output:
# 🎬 Craft GIF Regeneration Script
# =================================
#
# Checking dependencies...
# ✅ VHS and gifsicle are installed
#
# Creating backup of existing GIFs...
# ✅ Backup created: .gif-backups-20260117-1400
#
# Regenerating GIFs...
# ====================
#
# 🎬 Generating: teaching-workflow
#    Tape: docs/demos/teaching-workflow.tape
#    Generated: 890K
#    Optimized: 533K
#    ✅ Size OK: 0.52 MB
```

---

## Manual Regeneration (Single GIF)

```bash
# Generate GIF from tape
cd docs/demos
vhs teaching-workflow.tape

# Optimize
gifsicle -O3 --colors 128 --lossy=80 teaching-workflow.gif -o teaching-workflow.gif

# Check size
ls -lh teaching-workflow.gif
```

---

## Quality Checks

After regenerating, verify:

**Technical:**

- [ ] All GIFs under 2MB
- [ ] Optimized with gifsicle
- [ ] Smooth playback

**Accuracy:**

- [ ] Output matches real `/craft` command behavior
- [ ] Formatting is correct (boxes, icons, spacing)
- [ ] Timing feels natural
- [ ] No simulated/fake output

**Readability:**

- [ ] Text is legible
- [ ] Command prompts visible
- [ ] Colors have good contrast
- [ ] Not too fast to read

---

## Troubleshooting

### GIF is too large (> 2MB)

```bash
# Try more aggressive compression
gifsicle -O3 --colors 64 --lossy=100 input.gif -o input.gif

# Or reduce FPS in tape file
Set FPS 8  # Instead of 10 or 15
```

### Text is blurry after optimization

```bash
# Use less lossy compression
gifsicle -O3 --colors 256 --lossy=60 input.gif -o input.gif
```

### VHS tape fails to generate

```bash
# Check VHS version
vhs --version  # Should be 0.10.0 or newer

# Run tape with verbose output
vhs --verbose teaching-workflow.tape
```

---

## Workflow Checklist

For each GIF:

1. **Verify** (CRITICAL)
   - [ ] Test `/craft` command in Claude Code
   - [ ] Capture real output (screenshot/copy)
   - [ ] Note timing and format

2. **Update**
   - [ ] Edit `.tape` file with accurate output
   - [ ] Match exact formatting
   - [ ] Adjust timing values

3. **Generate**
   - [ ] Run `vhs <tape-file>`
   - [ ] Verify GIF created
   - [ ] Check size

4. **Optimize**
   - [ ] Run gifsicle optimization
   - [ ] Verify size ≤ 2MB
   - [ ] Check text readability

5. **Validate**
   - [ ] Open GIF and review
   - [ ] Confirm accuracy
   - [ ] Test on documentation site

---

## Batch Operations

### Regenerate all GIFs

```bash
./scripts/regenerate-gifs.sh
```

### Optimize all existing GIFs

```bash
for gif in docs/demos/*.gif docs/gifs/*.gif; do
    gifsicle -O3 --colors 128 --lossy=80 "$gif" -o "$gif"
    echo "Optimized: $gif ($(ls -lh "$gif" | awk '{print $5}'))"
done
```

### Check all GIF sizes

```bash
ls -lh docs/demos/*.gif docs/gifs/*.gif | \
  awk '{if ($5 ~ /M/) { size=$5; gsub(/M/, "", size);
        if (size+0 > 2.0) print "❌ TOO LARGE:", $9, $5;
        else print "✅ OK:", $9, $5
       } else print "✅ OK:", $9, $5}'
```

---

## Notes

- **DO NOT** run `/craft` commands in bash - they won't work!
- **DO** test commands in Claude Code first
- **DO** update VHS tapes with accurate output
- **DO** optimize all GIFs before committing
- **DO** verify text readability after optimization

---

**Last Updated**: 2026-01-17
**Script Version**: 1.0
