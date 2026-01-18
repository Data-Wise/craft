# Dependency Management Advanced Guide

⏱️ **20 minutes** • 🟠 Intermediate • ✓ Complete guide

> **TL;DR** (30 seconds)
> - **What:** Craft's dependency system automatically detects, validates, and installs tools needed for commands
> - **Why:** Ensure demos and commands work reliably without manual setup
> - **How:** System checks dependencies, shows status, and installs missing tools
> - **Next:** Read about [Integration Testing](integration-testing.md) or [Orchestrator](orchestrator.md)

The dependency management system ensures that tools required by commands (like `asciinema` for the demo command) are installed and working correctly.

## Quick Start

!!! abstract "Check Dependencies"
    ```bash
    # Check status of all dependencies
    /craft:docs:demo --check

    # Fix missing or broken dependencies
    /craft:docs:demo --fix
    ```

## System Architecture

### High-Level Flow

The dependency system works in three phases:

```
Phase 1: Parse
  ↓
demo.md frontmatter → Tool specifications (JSON)
  ↓

Phase 2: Detect
  ↓
Tool detection (PATH, homebrew, npm, cargo) → Status JSON
  ↓
Session cache (60s TTL) for performance
  ↓

Phase 3: Install (if needed)
  ↓
Fallback chain: brew → cargo → binary → consent prompt
  ↓
Atomic installation with logging and rollback
```

### Component Architecture

```
┌─────────────────────────────────────────────────────┐
│           commands/docs/demo.md                      │
│    (contains tool specs in YAML frontmatter)        │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        ↓                             ↓
   dependency-manager.sh       dependency-installer.sh
   (check & detect)            (install & repair)
        ↓                             ↓
   ┌────┴──────────┐         ┌───────┴──────────┐
   ↓               ↓         ↓                   ↓
tool-detector  session-cache brew-installer  cargo-installer
  (detects)     (caches)      (installs)      (installs)
   ↓               ↓         ↓                   ↓
version-check  health-check  repair-tools    binary-installer
 (validates)   (validates)   (fixes)         (fallback)
```

## Components Explained

### 1. Tool Specifications (in demo.md)

Dependencies are declared in the frontmatter of commands. Example from `commands/docs/demo.md`:

```yaml
---
name: demo
description: Generate GIF demos
dependencies:
  asciinema:
    required: true
    purpose: "Record real terminal sessions"
    methods: ["asciinema", "vhs"]
    install:
      brew: "asciinema"
      apt: "asciinema"
      cargo: "asciinema"
    version:
      min: "2.0.0"
      check_cmd: "asciinema --version | grep -oE '[0-9.]+' | head -1"
    health:
      check_cmd: "asciinema --help"
      expect_exit: 0

  agg:
    required: true
    purpose: "Optimize GIF files"
    methods: ["asciinema"]
    install:
      brew: "agg"
      cargo: "agg"
    version:
      min: "1.5.0"
      check_cmd: "agg --version"
    health:
      check_cmd: "agg --help"
      expect_exit: 0
---
```

**Fields Explained:**
- `required` - Boolean. If true, command fails without this tool
- `purpose` - Description of what the tool does
- `methods` - Array of demo methods that use this tool (asciinema, vhs)
- `install` - Platform-specific install commands (brew, apt, cargo, etc.)
- `version.min` - Minimum required version
- `version.check_cmd` - Command that outputs the tool's version
- `health.check_cmd` - Command to verify tool works
- `health.expect_exit` - Expected exit code (usually 0)

### 2. Tool Detection (tool-detector.sh)

Detects whether tools are installed using 4 methods:

**Detection Methods (in order):**

1. **PATH Search** - Look for executable in PATH
   ```bash
   which asciinema
   ```

2. **Homebrew** - Check Homebrew installation
   ```bash
   brew list asciinema
   ```

3. **NPM** - Check global npm packages
   ```bash
   npm list -g asciinema
   ```

4. **Cargo** - Check Rust toolchain
   ```bash
   cargo install --list | grep asciinema
   ```

**Output:** JSON detection result

```json
{
  "name": "asciinema",
  "installed": true,
  "version": "2.3.0",
  "version_ok": true,
  "health": "ok",
  "path": "/usr/local/bin/asciinema",
  "method": "brew"
}
```

### 3. Session Caching (session-cache.sh)

Caches detection results for performance:

**Cache Behavior:**
- **Location:** `/tmp/craft-deps-{SESSION_ID}/`
- **TTL:** 60 seconds
- **Scope:** Session-specific (no cross-session pollution)
- **Format:** JSON files per tool

**Benefits:**
- First check: ~500ms (5 tools)
- Cached check: ~50ms (90% faster)
- Automatic cleanup after 60s

**Example:**
```bash
# First check - detects and caches
/craft:docs:demo --check    # ~500ms

# Second check within 60s - uses cache
/craft:docs:demo --check    # ~50ms (10x faster!)

# After 60s - cache expires, re-detects
/craft:docs:demo --check    # ~500ms
```

### 4. Version Management (version-check.sh)

Validates tool versions using semantic versioning:

**Supported Formats:**
- `2.3.0` - Semantic versioning (major.minor.patch)
- `2.3` - Short version (auto-pad to X.Y.0)
- `2` - Major only (auto-pad to X.0.0)

**Comparison Logic:**
```
Requires: 2.0.0
Installed: 2.3.0
Result: OK (2.3.0 >= 2.0.0)

Installed: 1.9.0
Result: BROKEN (1.9.0 < 2.0.0) - needs upgrade
```

### 5. Health Checks (health-check.sh)

Verifies installed tools actually work:

```bash
# Test command
asciinema --help

# Expected exit code
0

# Result
OK if exit code matches
BROKEN if unexpected exit code
```

## Workflows

### Workflow 1: Check Dependencies

**Command:** `/craft:docs:demo --check`

**Steps:**
1. Parse `demo.md` frontmatter → Tool specs
2. For each tool:
   - Check cache (60s TTL)
   - If cache miss → Run detection (4 methods)
   - Store result in cache
3. Display results in formatted table

**Output Example:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 DEPENDENCY STATUS: asciinema method                      │
├─────────────────────────────────────────────────────────────┤
│ Tool         │ Status     │ Version  │ Health  │ Install     │
├──────────────┼────────────┼──────────┼─────────┼─────────────┤
│ asciinema    │ ✅ OK       │ 2.3.0    │ ✅ OK    │ -           │
│ agg          │ ❌ MISSING  │ -        │ -       │ cargo i ... │
│ gifsicle     │ ✅ OK       │ 1.96     │ ✅ OK    │ -           │
└──────────────┴────────────┴──────────┴─────────┴─────────────┘

Summary: 1 missing, 0 broken
Run: /craft:docs:demo --fix
```

**Exit Codes:**
- `0` - All required tools OK
- `1` - Missing or broken required tools

### Workflow 2: Install Missing Dependencies

**Command:** `/craft:docs:demo --fix`

**Steps:**
1. Check dependencies (same as Workflow 1)
2. Identify missing/broken tools
3. For each missing tool:
   - Try install methods in priority order: brew → cargo → binary
   - First success → use that method
   - First failure → try next method
4. Verify installation with health check
5. Report results

**Install Priority:**
```
1. Homebrew (macOS primary)
   └─ brew install asciinema

2. Cargo (Rust packages)
   └─ cargo install agg

3. Binary Download (fallback)
   └─ Download pre-compiled binary

4. User Consent Prompt (last resort)
   └─ Ask user permission for other methods
```

**Output Example:**
```
Installing missing dependencies...

agg (required for asciinema method):
  Trying: brew install agg ... NOT FOUND
  Trying: cargo install agg ... ✅ SUCCESS
  Verified: agg 1.7.0 ✅

gifsicle (optional for asciinema method):
  Skipped (optional tool)

Installation complete!
```

### Workflow 3: Repair Broken Dependencies

**Command:** `/craft:docs:demo --repair` (or automatic with --fix)

**Steps:**
1. Detect broken tools (health check failed)
2. For each broken tool:
   - Determine install method (from detection)
   - Uninstall current version (if safe)
   - Reinstall latest compatible version
   - Verify with health check

**Example - Broken Installation:**
```
gifsicle health check FAILED
  Current version: 1.88
  Required minimum: 1.90

Repair strategy:
  1. Uninstall: brew uninstall gifsicle
  2. Reinstall: brew install gifsicle
  3. Verify: gifsicle --version

Result: ✅ gifsicle 1.96 now healthy
```

### Workflow 4: Batch Installation

For commands with many dependencies, batch mode:
1. Collect all missing tools
2. Show installation plan
3. Install all tools sequentially
4. Report summary
5. Optionally run integration tests

**Example:**
```bash
# Check 5 tools
asciinema   ✅ OK
agg         ❌ MISSING
gifsicle    ✅ OK
ffmpeg      ❌ MISSING
imagemagick ✅ OK

# Batch fix
Installing: agg, ffmpeg (2 tools)
  agg       ✅ (via cargo)
  ffmpeg    ✅ (via brew)

Result: 2/2 installed successfully
```

## Scripts Reference

### dependency-manager.sh (476 lines)

**Main orchestrator for checking and detecting tools.**

**Key Functions:**

| Function | Purpose | Example |
|----------|---------|---------|
| `parse_frontmatter` | Extract tool specs from demo.md | Returns JSON of all dependencies |
| `check_dependencies METHOD` | Check specific method (asciinema/vhs) | Returns status JSON |
| `check_all_dependencies` | Check all tools regardless of method | Returns status JSON |
| `display_status_table METHOD` | Format status as ASCII table | Outputs formatted table |
| `get_install_command TOOL SPEC` | Get platform-specific install cmd | Returns brew/cargo/apt command |

**Usage:**
```bash
# Check dependencies for asciinema method
bash scripts/dependency-manager.sh check_dependencies asciinema

# Display formatted status table
bash scripts/dependency-manager.sh display_status_table asciinema

# Get install command for a tool
bash scripts/dependency-manager.sh get_install_command agg '{"brew":"agg","cargo":"agg"}'
```

**Output Formats:**
- **JSON:** For programmatic use
- **Table:** For human readability
- **Exit codes:** 0 (OK), 1 (missing/broken)

### dependency-installer.sh (476 lines)

**Orchestrator for installing and repairing tools.**

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `install_missing_tools` | Install all missing required tools |
| `repair_broken_tools` | Fix tools with failed health checks |
| `install_via_brew TOOL SPEC` | Install via Homebrew |
| `install_via_cargo TOOL SPEC` | Install via Cargo |
| `install_via_binary TOOL SPEC` | Download pre-compiled binary |
| `prompt_user_consent TOOL` | Ask user permission to install |

**Usage:**
```bash
# Install missing tools
bash scripts/dependency-installer.sh install_missing_tools

# Repair broken tools
bash scripts/dependency-installer.sh repair_broken_tools

# Dry-run to preview what would happen
bash scripts/dependency-installer.sh --dry-run install_missing_tools
```

### tool-detector.sh (297 lines)

**Low-level tool detection using 4 methods.**

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `detect_tool TOOL SPEC` | Main detection routine |
| `extract_version TOOL CMD` | Extract version from command output |
| `compare_version CURRENT MIN` | Validate version meets minimum |
| `run_health_check CMD EXPECT_EXIT` | Verify tool works |

**Usage:**
```bash
# Detect if bash is installed
bash scripts/tool-detector.sh bash

# Import functions and use directly
source scripts/tool-detector.sh
detect_tool "asciinema" '{"min":"2.0.0"}'
```

### session-cache.sh (211 lines)

**Session-scoped caching layer for performance.**

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `init_cache` | Create cache directory |
| `get_cached_status TOOL` | Retrieve cached detection result |
| `store_cache TOOL JSON` | Store detection result (60s TTL) |
| `clear_cache TOOL` | Invalidate single tool |
| `cleanup_cache` | Remove entire cache directory |

**Cache Structure:**
```
/tmp/craft-deps-SESSION_ID/
├── asciinema.json     # {"installed": true, "version": "2.3.0", ...}
├── agg.json            # {"installed": false, ...}
└── gifsicle.json
```

**Cache Expiration:**
- Manual: `clear_cache asciinema`
- Automatic: 60 seconds TTL
- Cleanup: `cleanup_cache` removes entire directory

### version-check.sh (365 lines)

**Semantic version comparison and validation.**

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `compare_versions CURRENT MINIMUM` | Check if current >= minimum |
| `parse_version_string STRING` | Extract version components |
| `validate_version_format VERSION` | Check format is valid |

**Supported Formats:**
```
2.3.0    → [major=2, minor=3, patch=0]
2.3      → [major=2, minor=3, patch=0] (auto-pad)
2        → [major=2, minor=0, patch=0] (auto-pad)
v2.3.0   → [major=2, minor=3, patch=0] (strip 'v')
```

### health-check.sh (287 lines)

**Tool validation and health assessment.**

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `run_health_check TOOL CMD EXPECT_EXIT` | Test tool functionality |
| `diagnose_tool_failure TOOL` | Troubleshoot broken tools |
| `suggest_fixes TOOL ERROR` | Recommend fixes |

**Health Check Output:**
```json
{
  "name": "asciinema",
  "health": "ok",
  "exit_code": 0,
  "output": "asciinema 2.3.0\nRecord and share your terminal session...",
  "timestamp": "2026-01-18T14:30:00Z"
}
```

### repair-tools.sh (485 lines)

**Advanced repair and recovery for broken dependencies.**

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `diagnose_broken_tool TOOL` | Identify why tool is broken |
| `repair_via_reinstall TOOL` | Uninstall and reinstall |
| `repair_via_update TOOL` | Update to latest version |
| `repair_via_downgrade TOOL` | Downgrade if needed |
| `repair_via_alternative TOOL` | Try alternative tool |

**Repair Strategies:**
1. **Update** - Upgrade to latest version
2. **Reinstall** - Remove and reinstall
3. **Downgrade** - Go to previous stable version
4. **Alternative** - Use different tool with same purpose
5. **Manual** - Ask user to fix manually

## Installers

### brew-installer.sh (156 lines)

**Homebrew package installation.**

**Functions:**
```bash
check_brew_available()      # Check if brew is installed
brew_search_package PKG     # Verify package exists
brew_install_package TOOL PKG  # Install package
get_brew_status            # Status JSON
```

**Output:**
```json
{"success": true, "message": "Successfully installed agg via brew"}
{"success": false, "error": "Package not found in Homebrew"}
```

### cargo-installer.sh (234 lines)

**Rust package installation via Cargo.**

**Functions:**
```bash
check_cargo_available()        # Check if cargo installed
cargo_search_package PKG       # Verify package exists
cargo_install_package TOOL PKG # Install package
get_cargo_status               # Status JSON
```

**Output:**
```json
{"success": true, "message": "Successfully installed agg v1.7.0"}
{"success": false, "error": "Package not found in crates.io"}
```

### binary-installer.sh (312 lines)

**Direct binary download and installation.**

**Functions:**
```bash
get_download_url TOOL VERSION           # Construct download URL
download_binary TOOL URL DESTINATION    # Download and verify
install_binary_from_archive TOOL PATH   # Extract and install
get_binary_status                       # Status JSON
```

**Supported Formats:**
- `.tar.gz` - Gzip archive
- `.zip` - Zip archive
- Single binary files

### consent-prompt.sh (98 lines)

**Interactive user approval for sensitive operations.**

**Functions:**
```bash
prompt_user_consent TOOL MESSAGE        # Ask user permission
format_consent_prompt TOOL REASON       # Format prompt text
parse_user_response RESPONSE            # Validate user input
```

**Example:**
```
agg needs to be installed. Install now? [y/N]
> y
✅ Installing agg via cargo...
```

## Error Handling

### Graceful Degradation

The system gracefully handles common errors:

| Error | Behavior |
|-------|----------|
| Tool not found | `installed: false` (continue) |
| Version unparseable | `version: "unparseable"` (continue) |
| Health check failed | `health: "broken"` (warn) |
| Installer unavailable | Try next installer method |
| All installers fail | `installed: false` (require manual install) |
| Invalid frontmatter | Error to stderr, exit 1 |

### Retry Logic

Installation retries with exponential backoff:
```
Attempt 1: brew install agg
  └─ Failed

Wait 2 seconds

Attempt 2: brew install agg
  └─ Failed

Try next method: cargo install agg
  └─ Success!
```

### Logging

All operations logged to:
```
/tmp/craft-install-SESSION_ID.log
```

**Log Format:**
```
2026-01-18 14:30:00 [INFO] Starting dependency check
2026-01-18 14:30:00 [DEBUG] Checking asciinema...
2026-01-18 14:30:01 [DEBUG] Found via PATH: /usr/local/bin/asciinema
2026-01-18 14:30:01 [DEBUG] Version 2.3.0 >= 2.0.0: OK
2026-01-18 14:30:01 [DEBUG] Health check: OK
2026-01-18 14:30:02 [INFO] Dependency check complete: 1 OK, 0 missing, 0 broken
```

## Performance Characteristics

### Benchmark Results

| Operation | Time (first) | Time (cached) | Speedup |
|-----------|--------------|---------------|---------|
| Check 1 tool | 100ms | 5ms | 20x |
| Check 5 tools | 500ms | 25ms | 20x |
| Check 10 tools | 1000ms | 50ms | 20x |
| Install 1 tool | 2-5s | - | - |
| Install 5 tools | 8-15s | - | - |

### Session Cache Impact

- **First check per session:** ~500ms (5 tools)
- **Subsequent checks (< 60s):** ~50ms (cache hits)
- **After 60s:** ~500ms (cache expired, fresh detection)

### Optimization Tips

1. **Reuse commands** - Use `/craft:docs:demo --check` twice within 60s
2. **Batch installs** - Install multiple tools at once (faster than individual)
3. **Avoid network calls** - cache.sh stores results locally
4. **CI/CD** - Pre-cache dependencies in CI step for speed

## Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Check dependencies
  run: /craft:docs:demo --check

- name: Install missing tools
  run: /craft:docs:demo --fix

- name: Run command
  run: /craft:docs:demo asciinema
```

### GitLab CI Example

```yaml
check-dependencies:
  script:
    - /craft:docs:demo --check
    - /craft:docs:demo --fix
```

## Troubleshooting

### Issue: Tool shows as "MISSING" but is actually installed

**Diagnosis:**
1. Check if tool is in PATH: `which toolname`
2. Check if tool is in homebrew: `brew list toolname`
3. Check if tool is in cargo: `cargo install --list | grep toolname`

**Solution:**
- Add to PATH: `export PATH="/path/to/tool:$PATH"`
- Reinstall via correct method
- Clear cache: `rm -rf /tmp/craft-deps-*`

### Issue: Version validation fails

**Diagnosis:**
1. Check actual version: `toolname --version`
2. Verify minimum required version in tool spec
3. Check version extraction command in health check

**Solution:**
```bash
# Test version extraction
asciinema --version | grep -oE '[0-9.]+'

# Update version extraction command in demo.md
check_cmd: "asciinema --version | grep -oE '[0-9.]+' | head -1"
```

### Issue: Installation fails with "installer not available"

**Diagnosis:**
- Homebrew not installed on macOS
- Cargo not installed for Rust tools
- Internet connection required for downloads

**Solution:**
1. Install Homebrew: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2. Install Rust: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
3. Check internet connection

### Issue: Health check fails after installation

**Diagnosis:**
- Tool installed but not in PATH
- Tool has unusual health check requirements
- Tool requires additional configuration

**Solution:**
1. Check if installed: `which toolname`
2. Verify health check command: `toolname --help`
3. Modify health check in tool spec if needed

## Next Steps

1. **Run check:** `/craft:docs:demo --check`
2. **Install missing:** `/craft:docs:demo --fix`
3. **Run demo:** `/craft:docs:demo asciinema`
4. **Read integration tests:** [Integration Testing Guide](integration-testing.md)
5. **Explore orchestration:** [Orchestrator Guide](orchestrator.md)

## Summary

The dependency management system provides:

- **Automatic detection** - Finds tools using 4 methods
- **Smart caching** - 20x performance improvement
- **Intelligent installation** - Fallback chain (brew → cargo → binary)
- **Health validation** - Ensures tools work correctly
- **Session isolation** - No cross-session pollution
- **CI/CD ready** - Works in automated environments
- **ADHD-friendly** - Simple commands: check, fix, repair

All operations are atomic, logged, and reversible.
