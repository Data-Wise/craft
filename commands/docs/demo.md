---
description: Terminal Recording & GIF Generator with dependency management
dependencies:
  asciinema:
    required: true
    purpose: "Record real terminal sessions"
    methods: ["asciinema"]
    install:
      brew: "asciinema"
      apt: "asciinema"
      yum: "asciinema"
    version:
      min: "2.0.0"
      check_cmd: "asciinema --version | grep -oE '[0-9.]+' | head -1"
    health:
      check_cmd: "asciinema --help"
      expect_exit: 0

  agg:
    required: true
    purpose: "Convert .cast to .gif"
    methods: ["asciinema"]
    install:
      cargo: "agg"
      cargo_git: "https://github.com/asciinema/agg"
      binary:
        url: "https://github.com/asciinema/agg/releases/latest/download/agg-{{arch}}-apple-darwin"
        arch_map:
          x86_64: "x86_64"
          arm64: "aarch64"
        target: "/usr/local/bin/agg"
    version:
      min: "1.4.0"
      check_cmd: "agg --version 2>&1 | grep -oE '[0-9.]+' | head -1"
    health:
      check_cmd: "agg --help"
      expect_exit: 0

  gifsicle:
    required: true
    purpose: "Optimize GIF file size"
    methods: ["asciinema", "vhs"]
    install:
      brew: "gifsicle"
      apt: "gifsicle"
      yum: "gifsicle"
    version:
      min: "1.90"
      check_cmd: "gifsicle --version | grep -oE '[0-9.]+' | head -1"
    health:
      check_cmd: "gifsicle --help"
      expect_exit: 0

  vhs:
    required: false
    purpose: "Generate scripted demos (alternative to asciinema)"
    methods: ["vhs"]
    install:
      brew: "charmbracelet/tap/vhs"
    version:
      min: "0.7.0"
      check_cmd: "vhs --version | grep -oE '[0-9.]+' | head -1"
    health:
      check_cmd: "vhs --help"
      expect_exit: 0

  fswatch:
    required: false
    purpose: "Watch mode for iterative development"
    methods: ["asciinema", "vhs"]
    install:
      brew: "fswatch"
      apt: "fswatch"
    version:
      min: "1.14.0"
      check_cmd: "fswatch --version | grep -oE '[0-9.]+' | head -1"
    health:
      check_cmd: "fswatch --help"
      expect_exit: 0

  python3:
    required: true
    purpose: "Parse YAML frontmatter in dependency-manager.sh"
    methods: ["asciinema", "vhs"]
    install:
      brew: "python3"
      apt: "python3"
      yum: "python3"
    version:
      min: "3.7.0"
      check_cmd: "python3 --version | grep -oE '[0-9.]+' | head -1"
    health:
      check_cmd: "python3 --version"
      expect_exit: 0

  pyyaml:
    required: true
    purpose: "Parse YAML frontmatter (Python library)"
    methods: ["asciinema", "vhs"]
    install_cmd: "pip3 install pyyaml"
    version:
      min: "5.1"
      check_cmd: "python3 -c 'import yaml; print(yaml.__version__)' 2>/dev/null"
    health:
      check_cmd: "python3 -c 'import yaml' 2>/dev/null"
      expect_exit: 0
---

# /craft:docs:demo - Terminal Recording & GIF Generator

You are a terminal demo creator. Record real terminal sessions or generate scripted demos for documentation.

## Purpose

**Create GIF demos of CLI features:**
- Record real terminal sessions with asciinema (default)
- Generate VHS tape files for scripted demos (optional)
- Auto-detect commands from feature
- Convert recordings to optimized GIFs

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
/craft:docs:demo "sessions"                    # Record real session with asciinema (default)
/craft:docs:demo "sessions" --method vhs       # Generate VHS tape (scripted)
/craft:docs:demo "sessions" --template workflow # Use specific template
/craft:docs:demo --list-templates              # Show available templates
/craft:docs:demo --preview                     # Show recording guide without starting
/craft:docs:demo "sessions" --watch            # Watch mode: auto-regenerate on changes
/craft:docs:demo "sessions" --generate         # Record/generate AND convert to GIF immediately
/craft:docs:demo --check                       # Validate all dependencies
/craft:docs:demo --check --method asciinema    # Check asciinema-specific deps
/craft:docs:demo --fix                         # Auto-install missing dependencies
/craft:docs:demo --fix --method asciinema      # Install missing deps for specific method
/craft:docs:demo --convert recording.cast      # Convert single .cast file to .gif
/craft:docs:demo --convert file.cast out.gif   # Convert with custom output name
/craft:docs:demo --batch                       # Convert all .cast files in docs/
/craft:docs:demo --batch --force               # Overwrite existing GIF files
```

## Dependency Management

The demo command includes built-in dependency checking for all required tools.

### Check Dependencies

```bash
/craft:docs:demo --check                     # Check all dependencies
/craft:docs:demo --check --method asciinema  # Check for specific method
/craft:docs:demo --check --json              # Get JSON output for CI/CD
```

Shows a status table with:
- Tool name and purpose
- Installation status (✅ OK, ❌ MISSING, ⚠️  OPTIONAL)
- Installed version
- Health check result
- Install command if missing

#### JSON Output

Get machine-readable dependency status for CI/CD pipelines:

```bash
/craft:docs:demo --check --json
/craft:docs:demo --check --method asciinema --json
/craft:docs:demo --check --method vhs --json
```

**Output format:**
```json
{
  "status": "ok",
  "method": "asciinema",
  "tools": [
    {"name": "asciinema", "installed": true, "version": "2.3.0", "health": "ok"},
    {"name": "agg", "installed": true, "version": "1.4.3", "health": "ok"},
    {"name": "gifsicle", "installed": true, "version": "1.96", "health": "ok"}
  ]
}
```

**Status values:**
- `ok` - All required tools installed and healthy
- `issues` - Missing or broken tools detected

**Exit codes:**
- `0` - All required dependencies OK
- `1` - Missing required dependencies or health check failed

### Auto-Installation

The `--fix` flag automatically installs missing dependencies with your consent.

```bash
/craft:docs:demo --fix                       # Install all missing dependencies
/craft:docs:demo --fix --method asciinema    # Install for asciinema method only
```

**How it works:**
1. Checks for missing dependencies
2. Prompts for consent before each installation
3. Tries multiple installation methods (brew → cargo → binary)
4. Verifies installation success
5. Shows summary of installed/skipped/failed tools

**Installation Strategies:**
- **Homebrew** (~30 seconds) - macOS package manager
- **Cargo** (~2-5 minutes) - Rust compilation
- **Binary** (~10 seconds) - Direct download from GitHub

**User Consent:**
- You approve each tool individually
- Choose 'Y' to install, 'N' to skip, 'S' to skip all
- Installation requires sudo for system paths

### Required Tools by Method

**asciinema method:**
- asciinema (record sessions)
- agg (convert .cast to .gif)
- gifsicle (optimize GIF size)
- fswatch (optional, for watch mode)

**vhs method:**
- vhs (scripted demos)
- gifsicle (optimize GIF size)
- fswatch (optional, for watch mode)

### Batch Conversion

Convert existing `.cast` recordings to optimized `.gif` files.

**Convert single file:**
```bash
/craft:docs:demo --convert recording.cast              # Auto-generate recording.gif
/craft:docs:demo --convert demo.cast output.gif        # Custom output name
/craft:docs:demo --convert file.cast --force           # Overwrite existing
```

**Batch convert all files:**
```bash
/craft:docs:demo --batch                               # Convert all .cast in docs/
/craft:docs:demo --batch --force                       # Overwrite existing GIFs
/craft:docs:demo --batch --search-path custom/path     # Custom search directory
/craft:docs:demo --batch --dry-run                     # Preview without converting
```

**Features:**
- Automatically finds all `.cast` files in `docs/demos/` and `docs/gifs/`
- Skips existing `.gif` files (unless `--force`)
- Shows progress bar with ETA
- Reports compression ratios and file sizes
- Cross-platform (macOS/Linux)

**Output format:**
- Input: `recording.cast` (45 KB)
- Processing with `agg` (font-size 16, monokai theme)
- Optimizing with `gifsicle` (--optimize=3 --colors 256)
- Output: `recording.gif` (235 KB, 5.2x compression)

## Recording Methods

| Method | Best For | Recording Type |
|--------|----------|----------------|
| **asciinema** (default) | All commands - works everywhere | Real recording |
| **VHS** | Repeatable scripted demos | Simulated (Type commands) |

### When to Use Each Method

**Use asciinema (default) for:**
- Claude Code plugin commands (e.g., `/craft:site:build`)
- Bash CLI tools with real output
- When you want to record actual execution
- When accuracy is critical

**Use VHS for:**
- Scripted, repeatable demos
- When you need exact control over timing
- Automated demo generation in CI/CD

## When Invoked

### Implementation: Dependency Checking

When `--check` flag is provided:

1. Source the dependency manager:
   ```bash
   source scripts/dependency-manager.sh
   ```

2. Determine method and output format:
   ```bash
   method="${args_method:-asciinema}"  # Default to asciinema
   json_mode="${args_json:-false}"     # JSON output if --json flag present
   ```

3. Check dependencies and capture status:
   ```bash
   status_json=$(check_dependencies "$method")
   exit_code=$?
   ```

4. Display status based on output mode:
   ```bash
   if [ "$json_mode" = "true" ]; then
       # Machine-readable JSON output
       display_status_json "$method" "$status_json"
   else
       # Human-readable table format
       display_status_table "$method" "$status_json"
   fi
   exit $exit_code
   ```

#### Exit Codes

- `0` - All required dependencies OK
- `1` - Missing required dependencies or health check failed

#### JSON Output Details

The `display_status_json` function:
1. Analyzes the status JSON from `check_dependencies`
2. Counts missing and broken required tools
3. Sets overall status to "ok" if all OK, "issues" if any problems
4. Outputs formatted JSON with:
   - `status` - Overall status ("ok" or "issues")
   - `method` - The method checked (asciinema, vhs, all)
   - `tools` - Array of tool objects with name, installed, version, health

### Implementation: Auto-Installation (--fix)

When `--fix` flag is provided:

1. Source the installation utilities:
   ```bash
   source scripts/dependency-installer.sh
   source scripts/consent-prompt.sh
   ```

2. Determine method and check dependencies:
   ```bash
   method="${args_method:-asciinema}"
   status=$(check_dependencies "$method")
   ```

3. Get list of missing tools:
   ```bash
   missing_tools=$(parse_missing_tools "$status")
   ```

4. For each missing tool:
   ```bash
   for tool in $missing_tools; do
       tool_spec=$(get_tool_spec "$tool")
       install_tool "$tool" "$tool_spec"
   done
   ```

5. Display installation summary:
   ```bash
   show_installation_summary "$installed" "$skipped" "$failed"
   ```

6. Re-check dependencies and display final status:
   ```bash
   display_status_table "$method"
   ```

#### Exit Codes (--fix mode)

- `0` - All required dependencies installed or already OK
- `1` - Some required dependencies still missing after installation
- `2` - User skipped all installations

#### Integration with Normal Workflow

Before recording or generating demos, optionally validate dependencies:

```bash
# Early validation (optional in normal workflow)
if [ "${args_check_dependencies:-false}" = "true" ]; then
    source scripts/dependency-manager.sh
    method="${args_method:-asciinema}"

    if ! check_dependencies "$method" > /dev/null 2>&1; then
        echo "⚠️  Missing dependencies. Run: /craft:docs:demo --check"
        echo "   Or install with: /craft:docs:demo --fix"
        exit 1
    fi
fi
```

### Implementation: Batch Conversion (--convert, --batch)

#### Convert Single File (--convert)

When `--convert` flag is provided:

1. Source the conversion utility:
   ```bash
   source scripts/convert-cast.sh
   ```

2. Parse arguments:
   ```bash
   cast_file="$1"
   output_gif="${2:-}"  # Optional custom output
   force_flag="${args_force:-false}"
   ```

3. Validate and convert:
   ```bash
   if ! validate_cast_file "$cast_file"; then
       echo "Error: Invalid .cast file"
       exit 1
   fi

   convert_single "$cast_file" "$output_gif" "$force_flag"
   exit $?
   ```

#### Batch Convert (--batch)

When `--batch` flag is provided:

1. Source the batch converter:
   ```bash
   source scripts/batch-convert.sh
   ```

2. Parse batch options:
   ```bash
   search_paths="${args_search_path:-docs/demos docs/gifs}"
   force_flag="${args_force:-false}"
   dry_run="${args_dry_run:-false}"
   ```

3. Find and filter files:
   ```bash
   cast_files=$(find_cast_files "$search_paths")
   filtered_files=$(filter_existing "$cast_files" "$force_flag")
   ```

4. Process batch with progress:
   ```bash
   if [ "$dry_run" = "true" ]; then
       echo "Dry run - would convert:"
       echo "$filtered_files"
       exit 0
   fi

   process_batch "$filtered_files"
   show_summary
   exit $?
   ```

#### Exit Codes (Conversion)

- `0` - All conversions successful (or no files found)
- `1` - Some conversions failed
- `2` - All conversions failed or file exists without --force
- `3` - Missing convert-cast.sh script

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

## Asciinema Recording Workflow (--method asciinema)

When `--method asciinema` is specified, the workflow changes to real terminal recording:

### Step 1: Prepare Recording Script

Create a recording guide (not executed, just instructions):

```bash
# Recording guide saved to: docs/demos/[feature-name]-recording-guide.md
#
# Commands to run:
# 1. /craft:site:build
# 2. /craft:site:progress
# 3. /craft:site:publish --dry-run
#
# Total estimated time: ~45 seconds
```

### Step 2: Start Recording

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:demo "sessions" --method asciinema               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 🎙️  ASCIINEMA RECORDING MODE                                │
│                                                              │
│ Preparation:                                                 │
│   ✓ Created recording guide                                  │
│   ✓ Verified asciinema installed                             │
│   ✓ Verified agg installed                                   │
│                                                              │
│ ──────────────────────────────────────────────────────────── │
│                                                              │
│ NEXT: Start recording manually                               │
│                                                              │
│ 1. Start recording:                                          │
│    asciinema rec docs/demos/sessions.cast                    │
│                                                              │
│ 2. Run commands from guide:                                  │
│    See: docs/demos/sessions-recording-guide.md               │
│                                                              │
│ 3. Stop recording:                                           │
│    Press Ctrl+D or type 'exit'                               │
│                                                              │
│ 4. Preview recording:                                        │
│    asciinema play docs/demos/sessions.cast                   │
│                                                              │
│ 5. Convert to GIF:                                           │
│    agg --cols 100 --rows 30 --font-size 14 \                 │
│        docs/demos/sessions.cast \                            │
│        docs/demos/sessions.gif                               │
│                                                              │
│ 6. Optimize:                                                 │
│    gifsicle -O3 --colors 128 --lossy=80 \                    │
│        docs/demos/sessions.gif \                             │
│        -o docs/demos/sessions.gif                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: Recording Guide Format

```markdown
# Recording Guide: [Feature Name]

**Commands to run in this order:**

1. `/craft:command1`
   - Expected output: [brief description]
   - Wait for: [what to look for]

2. `/craft:command2 --arg`
   - Expected output: [brief description]
   - Wait for: [what to look for]

3. `/craft:command3`
   - Expected output: [brief description]
   - Wait for: [what to look for]

**Recording tips:**
- Let each command complete fully before the next
- Pause 2-3 seconds between commands
- Total estimated time: ~45 seconds

**After recording:**
1. Preview: `asciinema play docs/demos/[name].cast`
2. If mistakes, re-record from scratch
3. Convert and optimize (see commands above)
```

### asciinema + agg Settings

Default settings for Claude Code recordings:

| Setting | Value | Purpose |
|---------|-------|---------|
| `--cols` | 100 | Terminal width |
| `--rows` | 30 | Terminal height |
| `--font-size` | 14 | Readable in docs |
| `--theme` | dracula | Good contrast |
| `--fps` | 10 | Frame rate (lower = smaller file) |
| `--quality` | 100 | GIF quality (1-100) |

### Installation Check

When `--method asciinema` is used, verify tools are installed:

```bash
# Check for asciinema
if ! command -v asciinema &> /dev/null; then
  echo "❌ asciinema not installed"
  echo "   Install: brew install asciinema"
  exit 1
fi

# Check for agg
if ! command -v agg &> /dev/null; then
  echo "❌ agg not installed"
  echo "   Install: cargo install --git https://github.com/asciinema/agg"
  exit 1
fi

# Check for gifsicle
if ! command -v gifsicle &> /dev/null; then
  echo "❌ gifsicle not installed"
  echo "   Install: brew install gifsicle"
  exit 1
fi
```

### Complete asciinema Workflow Example

```bash
# 1. Generate recording guide
/craft:docs:demo "teaching-workflow" --method asciinema

# 2. Start recording
asciinema rec docs/demos/teaching-workflow.cast

# In Claude Code, run:
# /craft:git:status
# /craft:site:build
# /craft:site:progress
# /craft:site:publish --dry-run
# /craft:site:publish
# Ctrl+D to stop

# 3. Preview
asciinema play docs/demos/teaching-workflow.cast

# 4. Convert to GIF
agg --cols 100 --rows 30 --font-size 14 --theme dracula --fps 10 \
    docs/demos/teaching-workflow.cast \
    docs/demos/teaching-workflow.gif

# 5. Optimize
gifsicle -O3 --colors 128 --lossy=80 \
    docs/demos/teaching-workflow.gif \
    -o docs/demos/teaching-workflow.gif

# 6. Check size
ls -lh docs/demos/teaching-workflow.gif
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

### asciinema Method (default)

```bash
# Install asciinema (terminal recorder)
brew install asciinema

# Install agg (asciinema → GIF converter)
cargo install --git https://github.com/asciinema/agg

# Or download prebuilt binary
curl -LO https://github.com/asciinema/agg/releases/latest/download/agg-$(uname -m)-apple-darwin
chmod +x agg-$(uname -m)-apple-darwin
mv agg-$(uname -m)-apple-darwin /usr/local/bin/agg

# Install gifsicle for optimization
brew install gifsicle

# Verify
asciinema --version
agg --version
gifsicle --version
```

### VHS Method (--method vhs)

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
