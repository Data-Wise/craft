# GIF Creation Guidelines

> **Purpose:** Standards for creating visual demonstrations as GIFs for flow-cli documentation.

---

## Why GIFs?

**Benefits:**
- **Visual learning** — Show, don't just tell
- **Quick understanding** — 5 seconds > 5 paragraphs
- **No hosting needed** — Self-contained files
- **Accessible** — Works without video players

**Use cases:**
- Demonstrating interactive commands (`pick`, `dash -i`)
- Showing TUI interfaces
- Illustrating workflow patterns
- Highlighting new features

---

## ⚠️ CRITICAL: Verify in Claude Code First

**Before generating ANY GIF, you MUST:**

1. **Run commands in Claude Code** - Execute actual commands using Bash tool
2. **Capture real output** - Record the exact output that appears
3. **Check for errors** - Verify commands work without issues
4. **Validate format** - Ensure output matches expected format
5. **THEN generate GIF** - Use verified commands and output

### Why This Matters

| Problem | Example | Solution |
|---------|---------|----------|
| **Broken commands** | GIF shows command that doesn't exist | Run in Claude Code first → catch error |
| **Wrong output** | GIF shows outdated format | Capture real output → use in tape |
| **Missing setup** | Command fails due to prerequisites | Test first → document setup needed |
| **Timing issues** | Output appears slower/faster than GIF | Time real execution → adjust Sleep values |

### Workflow: Verify → Record → Generate

```bash
# ❌ WRONG: Generate GIF without testing
/craft:docs:demo "sessions" --generate    # May show broken commands!

# ✅ CORRECT: Test in Claude Code first
# Step 1: Verify commands work
ait sessions live                          # Test command
ait sessions current                       # Test command
ait sessions conflicts                     # Test command

# Step 2: Capture actual output and timing
# - Note how long output takes to appear
# - Record exact text format
# - Check for any errors

# Step 3: Generate GIF with verified commands
/craft:docs:demo "sessions" --generate     # Now using verified commands
```

### Testing Checklist

Before recording, verify:

- [ ] All commands execute without errors in Claude Code
- [ ] Output format matches what GIF will show
- [ ] Timing is realistic (not too fast/slow)
- [ ] All prerequisites are met (files exist, setup done)
- [ ] Commands work in the environment shown in GIF

**Remember:** GIFs are documentation. They must show real, working functionality.

### Special Case: Plugin Commands

**For Craft plugin commands (e.g., `/craft:site:build`):**

These commands only work within Claude Code's plugin system and **cannot** be executed in bash. For plugin command GIFs:

1. **Verify command exists** - Check the command file in `commands/`
2. **Test command manually** - Invoke the command in a Claude Code session
3. **Capture real output** - Screenshot or copy the actual output format
4. **Create accurate simulation** - Use `Type` in VHS tape to replicate the exact output
5. **Validate with user** - Confirm the simulated output matches real behavior

```bash
# ✅ CORRECT workflow for plugin commands:
# 1. Verify command exists
ls commands/site/build.md

# 2. Test in Claude Code session (manually)
# Run: /craft:site:build
# Capture output format and timing

# 3. Create VHS tape with accurate simulation
# Use Type to replicate the exact output seen
Type "$ /craft:site:build"
Sleep 300ms
Type "✓ Built successfully"  # ← Must match real output

# 4. Validate GIF matches actual command behavior
```

**Key Difference:**
- **Regular CLI tools** → MUST execute in bash first
- **Plugin commands** → MUST test in Claude Code, then simulate accurately in VHS

---

## Technical Standards

### File Specifications

| Property | Standard | Notes |
|----------|----------|-------|
| **Duration** | 5-15 seconds | Shorter is better |
| **File Size** | ≤ 2MB | Optimize with gifsicle |
| **FPS** | 10-15 | Smooth but efficient |
| **Resolution** | 1200px width max | Readable on all devices |
| **Format** | .gif | Not .mp4, .webm, etc. |
| **Colors** | ≤ 128 | Balance quality/size |

### Technical Requirements

```bash
# Minimum quality threshold
Width: 800-1200px
Height: Auto (maintain aspect ratio)
FPS: 10-15 (not 30+)
Colors: 64-128 palette
Loop: Infinite
```

---

## Naming Convention

### Format

```
<feature>-<action>-<variant>.gif
```

### Examples

**Good names:**
- `pick-basic-usage.gif`
- `cc-dispatcher-opus-mode.gif`
- `dash-interactive-tui.gif`
- `worktree-create-branch.gif`
- `win-tracking-streak.gif`

**Bad names:**
- `demo.gif` (not descriptive)
- `screen-recording-2026-01-07.gif` (includes date)
- `my-test.gif` (not professional)
- `PICK_DEMO_FINAL_V2.gif` (version in filename)

### Naming Components

| Component | Purpose | Examples |
|-----------|---------|----------|
| **Feature** | What tool/command | `pick`, `cc`, `dash`, `worktree` |
| **Action** | What it does | `usage`, `mode`, `tui`, `create` |
| **Variant** | Specific case | `opus`, `streak`, `branch` (optional) |

---

## Storage Location

### Directory Structure

```
docs/
├── assets/
│   └── gifs/
│       ├── commands/          # Command demos
│       │   ├── pick-*.gif
│       │   ├── dash-*.gif
│       │   └── work-*.gif
│       ├── dispatchers/       # Dispatcher demos
│       │   ├── cc-*.gif
│       │   ├── g-*.gif
│       │   └── r-*.gif
│       ├── features/          # Feature demos
│       │   ├── dopamine-*.gif
│       │   └── worktree-*.gif
│       └── tutorials/         # Tutorial companion GIFs
│           ├── 01-*.gif
│           └── 10-*.gif
```

### Linking in Docs

```markdown
<!-- Relative path from doc location -->
![Pick basic usage](../../assets/gifs/commands/pick-basic-usage.gif)

*Using `pick` to navigate between projects*
```

---

## Recording Workflow

### Tools

**Recommended:**
- **QuickTime Player** (Mac) — Built-in, simple
- **Kap** (Mac) — Lightweight, GIF-optimized
- **peek** (Linux) — Designed for GIFs

**Conversion:**
- **gifsicle** — Optimize existing GIFs
- **ffmpeg** — Convert video to GIF

### Recording Setup

```bash
# 1. Clean terminal environment
clear
export PS1="$ "  # Simple prompt

# 2. Set terminal size
# iTerm2: Preferences → Profiles → Window → Columns=100, Rows=30

# 3. Use readable font size
# iTerm2: Preferences → Profiles → Text → 14-16pt

# 4. Choose high-contrast theme
# Recommended: Solarized Light (better GIF compression)
```

### Recording Process

**Before recording:**
1. ✅ Practice the workflow 2-3 times
2. ✅ Clear terminal (`clear`)
3. ✅ Set simple PS1 prompt
4. ✅ Close unnecessary tabs/panes
5. ✅ Disable notifications

**During recording:**
1. **Count 2 seconds** before starting
2. **Type at normal pace** (not too fast)
3. **Pause 1 second** after important output
4. **Count 2 seconds** after completion

**After recording:**
1. Trim unnecessary frames
2. Optimize file size
3. Test on documentation page
4. Verify accessibility

---

## Optimization (REQUIRED)

**⚠️ MANDATORY: All GIFs MUST be optimized before committing**

Optimization reduces file size by 30-70% while maintaining quality, improving page load times and reducing bandwidth.

### Recommended Tool: gifsicle

Install gifsicle (required for GIF creation):
```bash
# macOS
brew install gifsicle

# Linux
sudo apt install gifsicle
```

### Standard Optimization Workflow

```bash
# STEP 1: Generate GIF (e.g., with VHS)
vhs demo.tape

# STEP 2: Optimize (REQUIRED - choose one)

# Option A: Recommended (balanced quality/size)
gifsicle -O3 --colors 128 --lossy=80 demo.gif -o demo.gif

# Option B: Maximum compression (for large GIFs)
gifsicle -O3 --colors 64 --lossy=100 demo.gif -o demo.gif

# Option C: High quality (for detailed UIs)
gifsicle -O3 --colors 256 demo.gif -o demo.gif

# STEP 3: Verify readability (see Readability Check below)
open demo.gif  # Check text is readable, timing is natural
```

### Batch Optimization

```bash
# Optimize all GIFs in directory (RECOMMENDED)
for gif in docs/demos/*.gif docs/gifs/*.gif; do
    gifsicle -O3 --colors 128 --lossy=80 "$gif" -o "$gif"
    echo "Optimized: $gif ($(ls -lh "$gif" | awk '{print $5}'))"
done
```

### Before/After Size Check

```bash
# Check sizes before optimization
ls -lh docs/demos/*.gif docs/gifs/*.gif | awk '{print $9, $5}'

# After optimization, verify all GIFs ≤ 2MB
ls -lh docs/demos/*.gif docs/gifs/*.gif | awk '{if ($5 ~ /M/) { size=$5; gsub(/M/, "", size); if (size+0 > 2.0) print "❌ TOO LARGE:", $9, $5; else print "✅ OK:", $9, $5 } else print "✅ OK:", $9, $5}'
```

### Using ffmpeg

```bash
# Convert video to GIF
ffmpeg -i input.mov -vf "fps=10,scale=1200:-1:flags=lanczos" \
  -c:v gif output.gif

# Add palette for better quality
ffmpeg -i input.mov -vf \
  "fps=10,scale=1200:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  output.gif
```

### Optimization Targets

| Before | After | Method |
|--------|-------|--------|
| 5MB | < 2MB | Color reduction (256 → 128) |
| 3MB | < 1MB | FPS reduction (30 → 10) |
| 2MB | < 500KB | Lossy optimization |

### Readability Check (REQUIRED)

**After optimization, ALWAYS verify:**

```bash
# 1. Open GIF in viewer
open demo.gif

# 2. Check readability (ALL must be YES)
# ✓ Can you read all text at normal viewing size?
# ✓ Are command prompts clearly visible?
# ✓ Is output legible without zooming?
# ✓ Do colors have sufficient contrast?
# ✓ Is timing natural (not too fast/slow)?
# ✓ Does the loop feel smooth?
```

**Readability Issues:**

| Problem | Cause | Fix |
|---------|-------|-----|
| **Text too blurry** | Too much lossy compression | Reduce `--lossy` value (80 → 60) |
| **Colors washed out** | Too few colors | Increase `--colors` (128 → 256) |
| **Text hard to read** | Font too small in recording | Re-record with larger font (14pt → 16pt) |
| **Timing too fast** | Sleep values too short | Increase Sleep in VHS tape (1s → 2s) |
| **File too large** | Not optimized | Run gifsicle with --lossy=80 |

**Quality-Size Trade-offs:**

```bash
# If text becomes unreadable after optimization:
# 1. Try less aggressive compression
gifsicle -O3 --colors 256 --lossy=60 demo.gif -o demo.gif

# 2. If still too large, reduce resolution instead
# Re-record at 800px width instead of 1200px

# 3. If still too large, reduce FPS in VHS tape
Set FPS 10  # Instead of 15
```

**Acceptance Criteria:**
- ✅ File size ≤ 2MB
- ✅ All text readable without zooming
- ✅ Command prompts clearly visible
- ✅ Natural timing (not rushed)
- ✅ Smooth playback

---

## Content Guidelines

### What to Show

**Do show:**
- ✅ Complete workflows (start to finish)
- ✅ Interactive UI (fzf pickers, TUI dashboards)
- ✅ Successful outcomes
- ✅ Real project names (not fake data)
- ✅ Actual command output

**Don't show:**
- ❌ Error states (unless troubleshooting GIF)
- ❌ Personal information (API keys, paths with username)
- ❌ Incomplete workflows
- ❌ Multiple unrelated commands
- ❌ Long pauses or waiting

### Timing Guidelines

| Duration | Use For |
|----------|---------|
| **3-5 sec** | Single command demo |
| **5-10 sec** | Short workflow (2-3 commands) |
| **10-15 sec** | Complete workflow |
| **15+ sec** | Complex tutorial (split into multiple GIFs) |

**ADHD-Friendly:**
- Shorter is better
- One concept per GIF
- Loop should feel natural

---

## Accessibility

### Visual Clarity

**Terminal settings:**
- Font size: 14-16pt (readable in GIF)
- Contrast: High (Solarized Light/Dark)
- Colors: Limited palette (< 8 colors)
- Width: 80-100 columns (fits in docs)

**Recording settings:**
- No transparency effects
- No blinking cursors (distracting)
- No animations in PS1 prompt
- Clean, simple output

### Caption Requirements

Every GIF must have:

1. **Alt text** (for screen readers)
2. **Caption** (brief description)
3. **Text explanation** (in documentation)

```markdown
![Pick basic usage showing project selection](../../assets/gifs/pick-basic-usage.gif)

*Using `pick` to navigate between projects with fzf interface*

The GIF demonstrates:
1. Launching `pick` command
2. Filtering projects by typing
3. Selecting with Enter key
4. Changing directory to selected project
```

---

## GIF Types

### Demo GIF

**Purpose:** Show feature in action

**Structure:**
1. Start state (clear terminal)
2. Command execution
3. Expected output
4. End state

**Example:** `pick-basic-usage.gif`

### Tutorial GIF

**Purpose:** Accompany tutorial steps

**Structure:**
1. Step N from tutorial
2. Command from tutorial
3. Output from tutorial
4. Verification (checkpoint)

**Example:** `tutorial-01-first-session.gif`

### Feature Highlight GIF

**Purpose:** Showcase new feature

**Structure:**
1. Before state (old behavior)
2. New command/feature
3. After state (improvement)

**Example:** `cc-unified-grammar.gif` (shows both orders work)

### Comparison GIF

**Purpose:** Show differences between approaches

**Structure:**
1. Approach A
2. Split or fade transition
3. Approach B
4. Highlight difference

**Example:** `pick-vs-direct-jump.gif`

---

## Quality Checklist

Before adding GIF to documentation:

**Verification (REQUIRED FIRST):**
- [ ] **Commands tested in Claude Code** (or bash for CLI tools)
- [ ] **Real output captured** (screenshots/copy-paste)
- [ ] **No errors** during testing
- [ ] **Timing observed** (how long output takes to appear)

**Technical (REQUIRED):**
- [ ] **Optimized with gifsicle** (`-O3 --colors 128 --lossy=80`)
- [ ] **File size ≤ 2MB** (check with `ls -lh`)
- [ ] **Resolution 800-1200px width**
- [ ] **FPS 10-15** (not 30+)
- [ ] **Loops infinitely**
- [ ] **No audio track**

**Readability (REQUIRED):**
- [ ] **All text readable** without zooming at normal viewing size
- [ ] **Command prompts clearly visible** ($ or > visible)
- [ ] **Output legible** (14-16pt font minimum in recording)
- [ ] **Colors have sufficient contrast** (Solarized/Dracula themes work well)
- [ ] **Timing natural** (not too fast to read, not too slow)
- [ ] **Smooth playback** (no jarring jumps)

**Content:**
- [ ] Shows complete workflow
- [ ] No sensitive information visible
- [ ] Demonstrates one clear concept
- [ ] Matches actual command behavior

**Accessibility:**
- [ ] Alt text provided
- [ ] Caption written
- [ ] Text explanation in docs
- [ ] High contrast terminal

**Naming & Organization:**
- [ ] Follows naming convention (`<feature>-<action>-<variant>.gif`)
- [ ] Stored in correct directory (`docs/demos/` or `docs/gifs/`)
- [ ] Referenced correctly in docs
- [ ] Markdown image syntax correct

---

## Examples

### Example 1: Pick Basic Usage

**File:** `docs/assets/gifs/commands/pick-basic-usage.gif`

**Recording:**
```bash
# Setup
clear
export PS1="$ "

# Record this workflow
pick
# [Type "flow"]
# [Press Enter]
pwd
# Shows: /Users/dt/projects/dev-tools/flow-cli
```

**In documentation:**
```markdown
### Using Pick to Navigate Projects

![Pick basic usage](../../assets/gifs/commands/pick-basic-usage.gif)

*Using `pick` to filter and navigate to flow-cli project*

The `pick` command provides an interactive FZF interface for navigating
between projects. Type to filter, use arrow keys to select, and press
Enter to navigate.
```

### Example 2: CC Unified Grammar

**File:** `docs/assets/gifs/dispatchers/cc-unified-grammar.gif`

**Recording:**
```bash
# Show both orders work
clear

# Mode-first (traditional)
echo "$ cc opus pick"
cc opus pick
# [Select project]
# [Close Claude window]

# Target-first (new!)
echo "$ cc pick opus"
cc pick opus
# [Select same project]
# [Shows identical behavior]
```

**In documentation:**
```markdown
### Unified Grammar (v4.8.0)

![CC unified grammar](../../assets/gifs/dispatchers/cc-unified-grammar.gif)

*Both `cc opus pick` and `cc pick opus` work identically*

The CC dispatcher now supports flexible command ordering. Whether you
specify the mode first or the target first, the result is the same.
```

---

## Maintenance

### Updating GIFs

**When to update:**
- UI changes significantly
- Command syntax changes
- Feature behavior changes
- Brand new feature added

**Update process:**
1. Create new GIF with updated workflow
2. Optimize new GIF
3. Replace old GIF (keep same filename)
4. Git commit with message: "docs: update GIF for [feature]"
5. Verify docs render correctly

### Archiving Old GIFs

```bash
# If replacing significantly different GIF
mv docs/assets/gifs/pick-old-ui.gif \
   docs/assets/gifs/archive/pick-old-ui-v1.0.gif

# Document in git commit
git add .
git commit -m "docs: update pick GIF for v4.8 UI changes

- New GIF reflects unified grammar
- Old GIF archived for reference"
```

---

## Future Enhancements

### Video Alternatives

**When GIFs aren't enough:**
- Complex workflows > 15 seconds
- Workflows requiring audio explanation
- Multi-pane terminal workflows

**Options:**
- **asciinema** — Terminal session recordings
- **YouTube** — Hosted video tutorials
- **Vimeo** — Higher quality, no ads

**Embedding asciinema:**
```markdown
<script id="asciicast-123456"
  src="https://asciinema.org/a/123456.js"
  async>
</script>
```

### Interactive Demos

**Future consideration:**
- **ttyrec/ttygif** — Terminal recordings
- **Carbon** — Beautiful code screenshots
- **termtosvg** — SVG terminal recordings (smaller than GIF)

---

## Tools Installation

### macOS

```bash
# Install gifsicle for optimization
brew install gifsicle

# Install ffmpeg for video conversion
brew install ffmpeg

# Install Kap for recording (optional)
brew install --cask kap

# Install peek alternative (optional)
brew install --cask licecap
```

### Linux

```bash
# Install gifsicle
sudo apt install gifsicle

# Install ffmpeg
sudo apt install ffmpeg

# Install peek
sudo apt install peek
```

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────┐
│  GIF CREATION QUICK REFERENCE                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  SPECIFICATIONS                                         │
│  Duration:      5-15 seconds                            │
│  Size:          ≤ 2MB                                   │
│  Resolution:    800-1200px width                        │
│  FPS:           10-15                                   │
│  Colors:        ≤ 128                                   │
│                                                         │
│  NAMING                                                 │
│  Format:        <feature>-<action>-<variant>.gif        │
│  Example:       pick-basic-usage.gif                    │
│                                                         │
│  OPTIMIZATION                                           │
│  gifsicle -O3 --colors 128 input.gif -o output.gif      │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  WORKFLOW: record → trim → optimize → embed → verify    │
└─────────────────────────────────────────────────────────┘
```

---

## Related Resources

- **QUICK-START-TEMPLATE.md** — For text-based quick starts
- **TUTORIAL-TEMPLATE.md** — For step-by-step tutorials with GIFs
- **WORKFLOW-TEMPLATE.md** — For workflow documentation with GIFs
- **REFCARD-TEMPLATE.md** — For reference cards (no GIFs)

---

**Last Updated:** 2026-01-07
**Guidelines Version:** 1.0
