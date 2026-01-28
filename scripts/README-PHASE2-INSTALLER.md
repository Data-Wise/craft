# Phase 2: Dependency Installer Framework

**Status:** ✅ Complete
**Agent:** code-5
**Duration:** 2 hours
**Branch:** feature/demo-dependency-management

---

## Overview

Phase 2 implements the **installation orchestration framework** that manages multi-strategy tool installation with user consent, automatic fallbacks, and comprehensive verification.

### What This Provides

- **Multi-strategy installation** - Try brew → cargo_git → cargo → binary automatically
- **User consent** - Clear prompts showing what will be installed and how
- **Automatic fallbacks** - If one method fails, try the next
- **Retry logic** - 2 attempts per strategy before moving on
- **Installation verification** - Confirm tools work after installation
- **Comprehensive logging** - Track all installation attempts

---

## Quick Start

### Test the Framework

```bash
# Run built-in test
./scripts/dependency-installer.sh

# Test with debug output
DEBUG=1 ./scripts/dependency-installer.sh

# Run comprehensive verification
./scripts/verify-phase2.sh
```

### Use in Scripts

```bash
source scripts/dependency-installer.sh

# Parse frontmatter and install a tool
deps_json=$(parse_frontmatter)
tool_spec=$(echo "$deps_json" | jq '.asciinema')
install_tool "asciinema" "$tool_spec"
```

---

## Architecture

### Installation Flow

```
┌─────────────────────────────────────────────────────────────┐
│ User calls: install_tool("agg", tool_spec)                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
            ┌───────────▼────────────┐
            │ Extract purpose from   │
            │ tool_spec for consent  │
            └───────────┬────────────┘
                        │
            ┌───────────▼────────────┐
            │ get_install_strategies │
            │ → [brew, cargo_git,    │
            │    cargo, binary]      │
            └───────────┬────────────┘
                        │
            ┌───────────▼────────────┐
            │ filter_available       │
            │ → [cargo_git, cargo,   │
            │    binary] (no brew)   │
            └───────────┬────────────┘
                        │
            ┌───────────▼────────────┐
            │ prompt_user_consent    │
            │ Show strategies & time │
            │ [Y/n/s]                │
            └───────────┬────────────┘
                        │
                ┌───────┴────────┐
                │ User approved? │
                └───┬────────┬───┘
                    │        │
                 Yes│        │No → Return 1
                    │        │
        ┌───────────▼────────────┐
        │ Loop through each      │
        │ available strategy:    │
        │                        │
        │ 1. try_install()       │
        │    - Attempt 1         │
        │    - Wait 2s           │
        │    - Attempt 2         │
        │                        │
        │ 2. verify_installation│
        │    - detect_tool()     │
        │    - Check health      │
        │                        │
        │ Success → Return 0     │
        │ Failure → Next strategy│
        └────────────────────────┘
```

### Function Relationships

```
install_tool()
  ├─ Uses: parse_frontmatter() [from dependency-manager.sh]
  ├─ Calls: get_install_strategies()
  ├─ Calls: filter_available_strategies()
  ├─ Calls: prompt_user_consent()
  ├─ Calls: try_install()
  │   └─ Calls: install_via_*() [4 stub functions]
  └─ Calls: verify_installation()
      └─ Uses: detect_tool() [from tool-detector.sh]
```

---

## Strategy Priority

Installation attempts strategies in this priority order:

### 1. Homebrew (brew)

- **Platform:** macOS, Linux (if installed)
- **Speed:** ~30 seconds
- **Reliability:** High
- **Command:** `brew install <package>`
- **Status:** Stub (Wave 2)

### 2. Cargo Git (cargo_git)

- **Platform:** Any with Rust installed
- **Speed:** ~2-5 minutes (compile from source)
- **Reliability:** High
- **Command:** `cargo install --git <repo_url>`
- **Status:** Stub (Wave 2)

### 3. Cargo (cargo)

- **Platform:** Any with Rust installed
- **Speed:** ~2-5 minutes (compile from crates.io)
- **Reliability:** High
- **Command:** `cargo install <package>`
- **Status:** Stub (Wave 2)

### 4. Binary Download (binary)

- **Platform:** Any with curl
- **Speed:** ~10 seconds
- **Reliability:** Medium (depends on GitHub releases)
- **Command:** Download from URL, install to target
- **Status:** Stub (Wave 2)

**Platform Filtering:** Unavailable strategies are automatically removed based on:

- Platform detection (macOS vs Linux)
- Available tools (brew, cargo, curl)
- Architecture (arm64 vs x86_64 for binaries)

---

## User Consent Interface

When `install_tool()` is called, the user sees:

```
┌─────────────────────────────────────────────────────────────┐
│ 🔧 INSTALLATION REQUIRED                                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Tool: agg
│ Purpose: Convert .cast to .gif
│                                                              │
│ Installation will try (in order):                            │
│   1. cargo_git       (~2-5min)                               │
│   2. cargo           (~2-5min)                               │
│   3. binary          (~10s)                                  │
│                                                              │
│ Install agg now?                                             │
│   [Y] Yes, install                                           │
│   [N] No, skip this tool                                     │
│   [S] Skip all missing tools                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### User Options

- **Y (default):** Proceed with installation, try strategies in order
- **N:** Skip this tool only, continue with other tools
- **S:** Set `SKIP_ALL=true`, skip all remaining tools without prompting

---

## Error Handling & Retry Logic

### Retry Mechanism

Each strategy gets **2 attempts** before moving to the next:

```bash
max_attempts=2
attempt=1

while [ $attempt -le $max_attempts ]; do
    # Try installation
    result=$(install_via_strategy 2>&1)

    if [ $? -eq 0 ]; then
        return 0  # Success
    fi

    if [ $attempt -lt $max_attempts ]; then
        echo "Retry attempt $((attempt + 1))..."
        sleep 2  # Brief delay
    fi

    ((attempt++))
done

return 1  # All attempts failed
```

### Fallback Chain

1. **Try strategy #1** (2 attempts)
   - On success: Verify installation
     - If verification passes: Return 0
     - If verification fails: Continue to strategy #2
   - On failure: Continue to strategy #2

2. **Try strategy #2** (2 attempts)
   - Same verification flow
   - On any failure: Continue to strategy #3

3. **Try strategy #3** (2 attempts)
   - Same verification flow
   - On any failure: Return 1 (all strategies exhausted)

### Verification After Install

After each successful installation attempt:

```bash
verify_installation()
  ├─ Invalidate cache for this tool
  ├─ Run detect_tool() from tool-detector.sh
  ├─ Extract: installed, health
  ├─ Check: installed == true && health == "ok"
  └─ Return: 0 (verified) or 1 (failed)
```

If verification fails, the installer continues to the next strategy rather than failing immediately.

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `DEBUG` | 0 | Enable verbose debug output to stderr |
| `SKIP_ALL` | false | Skip all installations (set by user choosing 'S') |
| `INSTALL_LOG` | /tmp/craft-install-$$.log | Path to installation log file |

### Usage Examples

```bash
# Enable debug output
DEBUG=1 ./scripts/dependency-installer.sh

# Skip all installations (non-interactive)
SKIP_ALL=true source scripts/dependency-installer.sh

# Custom log location
INSTALL_LOG=/tmp/my-install.log ./scripts/dependency-installer.sh
```

---

## Logging

### Log Location

`/tmp/craft-install-$$.log` (unique per process ID)

### Log Format

```
[YYYY-MM-DD HH:MM:SS] Message
```

### Log Entries

- Session markers (`=== Starting installation: tool ===`)
- User consent decisions
- Installation attempt starts
- Installation failures with error messages
- Verification results
- Session end markers

### Example Log

```
[2026-01-17 15:00:00] === Starting installation: agg ===
[2026-01-17 15:00:01] User approved installation of agg
[2026-01-17 15:00:01] Attempting cargo_git installation for agg
[2026-01-17 15:00:03] Installation failed via cargo_git on attempt 1: compilation error
[2026-01-17 15:00:05] Installation failed via cargo_git on attempt 2: compilation error
[2026-01-17 15:00:05] All attempts failed for cargo_git
[2026-01-17 15:00:05] Attempting cargo installation for agg
[2026-01-17 15:02:30] Installation successful via cargo on attempt 1
[2026-01-17 15:02:31] Verification successful: agg installed and healthy
[2026-01-17 15:02:31] === Installation complete: agg via cargo ===
```

---

## Function Reference

### Core Functions

#### `install_tool(tool_name, tool_spec)`

Main installation orchestrator.

**Arguments:**

- `tool_name` - Tool command name (e.g., "asciinema")
- `tool_spec` - JSON tool specification from frontmatter

**Returns:**

- `0` - Successful installation and verification
- `1` - User declined or all strategies failed

**Example:**

```bash
deps_json=$(parse_frontmatter)
agg_spec=$(echo "$deps_json" | jq '.agg')
install_tool "agg" "$agg_spec"
```

---

#### `get_install_strategies(tool_spec)`

Extract installation methods from tool spec in priority order.

**Arguments:**

- `tool_spec` - JSON tool specification

**Returns:**

- Newline-separated list of strategy names

**Example:**

```bash
strategies=$(get_install_strategies "$tool_spec")
# Output:
# brew
# cargo_git
# cargo
# binary
```

---

#### `filter_available_strategies(strategies)`

Filter strategies by platform availability.

**Arguments:**

- `strategies` - Newline-separated list of strategy names

**Returns:**

- Newline-separated list of available strategies

**Checks:**

- `brew` - Requires `command -v brew`
- `cargo`/`cargo_git` - Requires `command -v cargo`
- `binary` - Requires `command -v curl`

**Example:**

```bash
available=$(filter_available_strategies "$strategies")
# On macOS without brew:
# cargo_git
# cargo
# binary
```

---

#### `try_install(tool_name, strategy, tool_spec)`

Attempt installation with retry logic.

**Arguments:**

- `tool_name` - Tool command name
- `strategy` - Strategy name (brew, cargo, cargo_git, binary)
- `tool_spec` - JSON tool specification

**Returns:**

- `0` - Installation succeeded
- `1` - Installation failed after 2 attempts

**Behavior:**

- Tries installation up to 2 times
- 2-second delay between retries
- Logs all attempts to INSTALL_LOG

---

#### `verify_installation(tool_name, tool_spec)`

Verify tool installed and healthy.

**Arguments:**

- `tool_name` - Tool command name
- `tool_spec` - JSON tool specification

**Returns:**

- `0` - Tool installed and healthy
- `1` - Tool missing or broken

**Behavior:**

- Invalidates cache for this tool
- Uses `detect_tool()` from tool-detector.sh
- Checks both installation and health status

---

#### `prompt_user_consent(tool_name, purpose, strategies)`

Get user approval for installation.

**Arguments:**

- `tool_name` - Tool command name
- `purpose` - User-facing description
- `strategies` - Newline-separated list of strategies

**Returns:**

- `0` - User approved
- `1` - User declined or SKIP_ALL is set

---

#### `detect_platform()`

Detect operating system and architecture.

**No arguments**

**Sets global variables:**

- `PLATFORM` - "macos", "linux", or "unknown"
- `ARCH` - "arm64", "x86_64", etc. (from `uname -m`)

---

### Stub Functions (Wave 2 Implementation)

These functions are currently stubs that return failure (exit code 1) and print stub messages. They will be implemented in Wave 2.

#### `install_via_brew(tool_name, tool_spec)`

**Current:** Stub returning 1
**Wave 2:** Will run `brew install <package>`

---

#### `install_via_cargo(tool_name, tool_spec)`

**Current:** Stub returning 1
**Wave 2:** Will run `cargo install <package>`

---

#### `install_via_cargo_git(tool_name, tool_spec)`

**Current:** Stub returning 1
**Wave 2:** Will run `cargo install --git <repo_url>`

---

#### `install_via_binary(tool_name, tool_spec)`

**Current:** Stub returning 1
**Wave 2:** Will download binary from URL, handle architecture templating, install to target

---

## Integration with Phase 1

### Dependencies

```bash
source "$SCRIPT_DIR/dependency-manager.sh"
source "$SCRIPT_DIR/tool-detector.sh"
source "$SCRIPT_DIR/session-cache.sh"
```

### Uses from dependency-manager.sh

- `parse_frontmatter()` - Extract tool specifications from demo.md

### Uses from tool-detector.sh

- `detect_tool()` - Verify tool installation and health

### Uses from session-cache.sh

- Cache invalidation after install
- Cache storage after verification

---

## Testing

### Built-in Test Suite

```bash
./scripts/dependency-installer.sh
```

**Tests:**

- Parse asciinema tool spec from frontmatter
- Extract installation strategies
- Filter by platform availability
- Verify all functions defined

### Comprehensive Verification

```bash
./scripts/verify-phase2.sh
```

**Verifies:**

- File existence and permissions
- Bash syntax validity
- Script sourcing
- All 11 functions defined
- Platform detection
- Strategy extraction and filtering
- Verification function
- All stub functions
- Documentation files

### Integration Tests

Created test scripts in `/tmp/`:

- `test-stub-installers.sh` - Test all 4 stub functions
- `test-full-workflow.sh` - End-to-end workflow test
- `test-installer-integration.sh` - Integration with Phase 1

**All tests passing:** ✅

---

## Platform Support

### Detected Platforms

| OS | PLATFORM | ARCH |
|----|----------|------|
| macOS | macos | arm64, x86_64 |
| Linux | linux | x86_64, arm64, etc. |
| Other | unknown | (from uname -m) |

### Strategy Availability

| Platform | brew | cargo | cargo_git | binary |
|----------|------|-------|-----------|--------|
| macOS (brew installed) | ✅ | ✅ | ✅ | ✅ |
| macOS (no brew) | ❌ | ✅ | ✅ | ✅ |
| Linux (apt) | ✅ | ✅ | ✅ | ✅ |
| Linux (no package manager) | ❌ | ✅ | ✅ | ✅ |

---

## Files & Documentation

### Implementation

- **scripts/dependency-installer.sh** (549 lines, 16KB)
  - Main installer framework
  - 11 functions (7 core + 4 stubs)

### Documentation

- **scripts/INSTALLER-USAGE.md** (8.8KB)
  - Complete usage guide
  - Function reference
  - Testing instructions

- **PHASE-2-SUMMARY.md** (13KB)
  - Implementation summary
  - Success metrics
  - Handoff notes

- **scripts/README-PHASE2-INSTALLER.md** (this file)
  - Comprehensive overview
  - Architecture diagrams
  - Complete reference

### Testing

- **scripts/verify-phase2.sh** (executable)
  - Comprehensive verification
  - Tests all functions
  - Platform detection validation

---

## Next Steps (Wave 2)

### Implement Actual Installers

1. **Brew installer** (`install_via_brew`)
   - Run `brew install <package>`
   - Handle "already installed" gracefully
   - Capture and log errors

2. **Cargo installer** (`install_via_cargo`)
   - Run `cargo install <package>`
   - Show progress for long compiles
   - Handle compilation errors

3. **Cargo git installer** (`install_via_cargo_git`)
   - Run `cargo install --git <url>`
   - Show clone progress
   - Handle network errors

4. **Binary installer** (`install_via_binary`)
   - Download from URL
   - Handle `{{arch}}` templating
   - Verify checksums (if available)
   - Set executable permissions
   - Install to target directory

### Additional Features

- Progress indicators for long-running installs
- Checksum verification for binary downloads
- Binary architecture selection (arm64 vs x86_64)
- Better error messages with suggestions
- Post-install configuration checks

**Estimated Wave 2 effort:** 6-8 hours

---

## Success Metrics

✅ All core functions implemented (7)
✅ All stub functions defined (4)
✅ Platform detection working (macOS, Linux)
✅ Strategy prioritization correct
✅ User consent interface complete
✅ Retry logic functional (2 attempts per strategy)
✅ Verification integration working
✅ Logging infrastructure complete
✅ All tests passing
✅ Documentation complete
✅ Ready for Wave 2 implementation

---

## Timeline

- **Start:** 2 hours ago
- **Development:** 1.5 hours
- **Testing:** 0.3 hours
- **Documentation:** 0.2 hours
- **Total:** 2 hours (on target)

---

**Status:** ✅ Phase 2 Complete
**Next:** Wave 2 (Actual Installer Implementation)
