# /craft:docs:demo - VHS Tape Generator

You are a terminal demo creator. Generate VHS tape files for GIF demos of CLI features.

## Purpose

**Generate VHS tape files for terminal recordings:**
- Create `.tape` files for VHS (github.com/charmbracelet/vhs)
- Three templates: command-showcase, workflow, before-after
- Auto-detect commands from feature
- Proper timing for readability

## ⚠️ CRITICAL: Verify Commands First

**Before generating demo tapes, you MUST:**

1. **Test commands in Claude Code** - Run actual commands using Bash tool
2. **Capture real output** - Record exactly what appears
3. **Verify no errors** - Ensure commands execute correctly
4. **Note timing** - Observe how long output takes to appear
5. **THEN generate tape** - Use verified commands in VHS tape

```bash
# ❌ WRONG: Generate demo without testing
/craft:docs:demo "feature" --generate

# ✅ CORRECT: Test commands first
# 1. Run commands in Claude Code
ait command1
ait command2
ait command3

# 2. Verify output format and timing
# 3. Note any prerequisites needed
# 4. Generate tape with verified commands
/craft:docs:demo "feature" --generate
```

**Why this matters:**
- GIFs must show **real, working** commands
- Output must match **actual** format
- Timing must be **realistic** (not guessed)
- Prerequisites must be **documented**

See: `templates/docs/GIF-GUIDELINES.md` for full workflow.

## Usage

```bash
/craft:docs:demo "sessions"                    # Generate demo for feature
/craft:docs:demo "sessions" --template workflow # Use specific template
/craft:docs:demo --list-templates              # Show available templates
/craft:docs:demo --preview                     # Show tape without writing
/craft:docs:demo "sessions" --watch            # Watch mode: auto-regenerate on changes
/craft:docs:demo "sessions" --generate         # Generate tape AND run VHS immediately
```

## When Invoked

### Step 1: Determine Feature Commands

```bash
# If feature name given, find related commands
ait --help | grep -i "sessions"

# Or from recent changes
git log --oneline -10 | grep -i "sessions"
git diff HEAD~10 --name-only | xargs grep -l "sessions"
```

### Step 2: Select Template

Choose template based on feature type:

| Template | Best For | Duration |
|----------|----------|----------|
| `command-showcase` | Show 3-5 CLI commands | 20-30s |
| `workflow` | Multi-step process | 30-45s |
| `before-after` | Compare old vs new | 25-35s |

### Step 3: Generate Tape File

#### Template 1: Command Showcase (Default)

```tape
# [Feature Name] Demo
# Shows: [brief description]

Output [feature-name].gif

Set Shell "zsh"
Set FontSize 18
Set Width 900
Set Height 550
Set Theme "Dracula"
Set Padding 15
Set TypingSpeed 40ms

# Command 1: [description]
Type "[command1]"
Enter
Sleep 2.5s

# Command 2: [description]
Type "[command2]"
Enter
Sleep 2.5s

# Command 3: [description]
Type "[command3]"
Enter
Sleep 2.5s

# Command 4: [description]
Type "[command4]"
Enter
Sleep 3s

```

**Timing Guidelines:**
- `Sleep 2.5s` - Standard command output
- `Sleep 3s` - Complex output to read
- `Sleep 1.5s` - Simple/expected output
- `TypingSpeed 40ms` - Readable but not slow

#### Template 2: Workflow Demo

```tape
# [Feature Name] Workflow Demo
# Shows: Complete workflow from start to finish

Output [feature-name]-workflow.gif

Set Shell "zsh"
Set FontSize 18
Set Width 900
Set Height 550
Set Theme "Dracula"
Set Padding 15
Set TypingSpeed 40ms

# === SETUP ===
# [Describe initial state]
Type "[setup-command]"
Enter
Sleep 2s

# === ACTION ===
# [Main workflow steps]
Type "[action-command-1]"
Enter
Sleep 2.5s

Type "[action-command-2]"
Enter
Sleep 2.5s

# === VERIFY ===
# [Show result]
Type "[verify-command]"
Enter
Sleep 3s

# === COMPLETE ===
# [Optional cleanup]
Type "[cleanup-command]"
Enter
Sleep 2s

```

#### Template 3: Before/After Comparison

```tape
# [Feature Name] Before/After Demo
# Shows: Old way vs new way

Output [feature-name]-comparison.gif

Set Shell "zsh"
Set FontSize 18
Set Width 900
Set Height 550
Set Theme "Dracula"
Set Padding 15
Set TypingSpeed 40ms

# === BEFORE (Old Way) ===
Type "# Old approach..."
Enter
Sleep 1s

Type "[old-command-1]"
Enter
Sleep 2s

Type "[old-command-2]"
Enter
Sleep 2s

# === AFTER (New Way) ===
Type "# With [feature]..."
Enter
Sleep 1s

Type "[new-command]"
Enter
Sleep 3s

```

### Step 4: Write Tape File

Write to `docs/demos/[feature-name].tape`:

```bash
# Default location
docs/demos/sessions.tape

# Verify demos directory exists
mkdir -p docs/demos
```

### Step 5: Output Summary

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:demo "sessions"                                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ ✅ VHS TAPE CREATED                                          │
│                                                              │
│ File: docs/demos/sessions.tape                               │
│ Template: command-showcase                                   │
│ Commands: 4                                                  │
│ Est. duration: ~25 seconds                                   │
│                                                              │
│ ──────────────────────────────────────────────────────────── │
│                                                              │
│ NEXT STEPS:                                                  │
│                                                              │
│ 1. Generate GIF:                                             │
│    cd docs/demos && vhs sessions.tape                        │
│                                                              │
│ 2. Optimize GIF (recommended):                               │
│    gifsicle -O3 --lossy=80 sessions.gif -o sessions-opt.gif  │
│    mv sessions-opt.gif sessions.gif                          │
│                                                              │
│ 3. Preview before commit:                                    │
│    open sessions.gif                                         │
│                                                              │
│ 4. Add to guide:                                             │
│    ![Sessions Demo](../demos/sessions.gif)                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Template Reference

### Command Showcase Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| `Width` | 900 | Wide enough for output |
| `Height` | 550 | Tall enough for multiple lines |
| `FontSize` | 18 | Readable in docs |
| `Theme` | Dracula | Good contrast |
| `TypingSpeed` | 40ms | Natural but fast |
| `Padding` | 15 | Clean borders |

### Timing Calculations

```
Duration = (commands × avg_output_time) + (commands × typing_time)

command_showcase (4 commands):
  = 4 × 2.5s + 4 × 0.5s = 12s output + 2s typing = ~14s
  + buffer = ~20-25s

workflow (6 commands):
  = 6 × 2.5s + 6 × 0.5s = 15s + 3s = ~18s
  + transitions = ~30s

before_after (5 commands):
  = 5 × 2s + 5 × 0.5s = 10s + 2.5s = ~12.5s
  + comments = ~25s
```

## Customization Options

### Adjust for Output Length

```tape
# Short output (1-2 lines)
Sleep 1.5s

# Medium output (3-10 lines)
Sleep 2.5s

# Long output (10+ lines)
Sleep 3.5s

# Interactive display (needs reading)
Sleep 4s
```

### Handle Errors Gracefully

```tape
# Show error and recovery
Type "ait sessions current"
Enter
Sleep 2s
# May show "No active session" - that's okay for demo
```

### Add Context Comments

```tape
# Show what we're about to do (NOT typed, just comment in tape)
# This comment won't appear in GIF

# To show text in GIF, use typed comment:
Type "# Check active sessions..."
Enter
Sleep 0.5s
```

## Integration

**Related commands:**
- `/craft:docs:analyze` - Recommends when GIF is needed
- `/craft:docs:guide` - Embeds GIF in generated guides
- `/craft:docs:mermaid` - Complementary visual docs

**CI Integration:**
- `.github/workflows/demos.yml` auto-generates GIFs
- Optimizes with gifsicle (`-O3 --lossy=80`)
- Posts PR comments with sizes

## Watch Mode (--watch)

Iterative development mode for refining demos:

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:demo "sessions" --watch                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 👀 WATCH MODE ACTIVE                                         │
│                                                              │
│ Watching: docs/demos/sessions.tape                           │
│                                                              │
│ Commands:                                                    │
│   [r] Regenerate GIF now                                     │
│   [o] Open GIF in viewer                                     │
│   [e] Edit tape file                                         │
│   [q] Quit watch mode                                        │
│                                                              │
│ Auto-regenerate on file save: ✓ enabled                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Watch Mode Workflow

```bash
# 1. Start watch mode
/craft:docs:demo "sessions" --watch

# 2. Edit the tape file (in another terminal/editor)
vim docs/demos/sessions.tape

# 3. On save, watch mode automatically:
#    - Runs: vhs sessions.tape
#    - Runs: gifsicle -O3 --lossy=80 sessions.gif
#    - Opens: sessions.gif (optional)

# 4. Iterate until satisfied
# 5. Press 'q' to exit watch mode
```

### Implementation (for terminal)

```bash
# Watch for changes using fswatch
fswatch -o docs/demos/sessions.tape | while read; do
  echo "Change detected, regenerating..."
  cd docs/demos && vhs sessions.tape
  gifsicle -O3 --lossy=80 sessions.gif -o sessions.gif
  echo "Done! Size: $(ls -lh sessions.gif | awk '{print $5}')"
done
```

### Quick Iteration Tips

1. **Start small** - Begin with 2-3 commands
2. **Check timing** - Are pauses long enough to read?
3. **Verify output** - Does the demo show expected results?
4. **Optimize last** - Get content right before size optimization

## Best Practices

1. **Keep under 30 seconds** - Attention spans are short
2. **Show realistic output** - Don't fake results
3. **Include context** - Show what you're about to do
4. **Test locally first** - `vhs --preview [tape]`
5. **Optimize size** - Use gifsicle for ~30% smaller files
6. **Use watch mode** - Iterate quickly on timing and content

## Generate Mode (--generate)

Skip the manual steps - generate tape AND create GIF in one command:

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:demo "sessions" --generate                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ ✅ DEMO GENERATED                                            │
│                                                              │
│ 1. ✓ Created: docs/demos/sessions.tape                       │
│ 2. ✓ Running: vhs sessions.tape                              │
│ 3. ✓ Optimizing: gifsicle -O3 --lossy=80                     │
│ 4. ✓ Created: docs/demos/sessions.gif (245KB)                │
│                                                              │
│ Preview: open docs/demos/sessions.gif                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**What --generate does:**
1. Creates the `.tape` file
2. Runs `vhs` to generate the GIF
3. Optimizes with `gifsicle`
4. Reports final file size

**Use when:** You want the complete workflow without manual steps.

## Requirements

```bash
# Install VHS
brew install charmbracelet/tap/vhs

# Install gifsicle for optimization
brew install gifsicle

# Install fswatch for watch mode (optional)
brew install fswatch

# Verify
vhs --version
gifsicle --version
```
