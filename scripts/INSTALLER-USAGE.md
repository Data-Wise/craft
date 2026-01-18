# Dependency Installer Framework - Usage Guide

## Overview

The `dependency-installer.sh` script orchestrates multi-strategy tool installation with:
- User consent prompts
- Automatic fallback strategies
- Retry logic (2 attempts per strategy)
- Installation verification
- Comprehensive logging

## Architecture

```
install_tool()
  ├─ get_install_strategies()      # Extract from frontmatter
  ├─ filter_available_strategies() # Check platform availability
  ├─ prompt_user_consent()         # Get user approval
  └─ [for each strategy]
      ├─ try_install()              # Attempt installation (2 tries)
      │   ├─ install_via_brew()
      │   ├─ install_via_cargo()
      │   ├─ install_via_cargo_git()
      │   └─ install_via_binary()
      └─ verify_installation()      # Check with tool-detector.sh
```

## Strategy Priority

1. **brew** - Homebrew (macOS/Linux) - ~30s install
2. **cargo_git** - Cargo from Git repo - ~2-5min compile
3. **cargo** - Cargo from crates.io - ~2-5min compile
4. **binary** - Direct binary download - ~10s

Platform filtering automatically removes unavailable methods.

## Usage

### From Shell Scripts

```bash
source scripts/dependency-installer.sh

# Install a tool
deps_json=$(parse_frontmatter)
tool_spec=$(echo "$deps_json" | jq '.asciinema')
install_tool "asciinema" "$tool_spec"
```

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `DEBUG` | 0 | Enable verbose logging (set to 1) |
| `SKIP_ALL` | false | Skip all installations without prompting |
| `INSTALL_LOG` | /tmp/craft-install-$$.log | Installation log path |

### User Consent Flow

When `install_tool()` is called:

```
┌─────────────────────────────────────────────────────────────┐
│ 🔧 INSTALLATION REQUIRED                                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Tool: asciinema
│ Purpose: Record real terminal sessions
│                                                              │
│ Installation will try (in order):                            │
│   1. brew            (~30s)                                  │
│   2. binary          (~10s)                                  │
│                                                              │
│ Install asciinema now?                                       │
│   [Y] Yes, install                                           │
│   [N] No, skip this tool                                     │
│   [S] Skip all missing tools                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

User choices:
- **Y** (default): Proceed with installation
- **N**: Skip this tool only
- **S**: Skip all tools (sets SKIP_ALL=true)

## Function Reference

### `install_tool(tool_name, tool_spec)`

Main installation orchestrator.

**Arguments:**
- `tool_name` - Tool command name (e.g., "asciinema")
- `tool_spec` - JSON tool specification from frontmatter

**Returns:**
- `0` on successful installation and verification
- `1` if user declined or all strategies failed

**Example:**
```bash
install_tool "agg" "$agg_spec"
```

---

### `get_install_strategies(tool_spec)`

Extract installation methods from tool spec in priority order.

**Arguments:**
- `tool_spec` - JSON tool specification

**Returns:**
- Newline-separated list of strategy names

**Example:**
```bash
strategies=$(get_install_strategies "$tool_spec")
# Output: brew\ncargo_git\nbinary
```

---

### `filter_available_strategies(strategies)`

Filter strategies by platform availability.

**Arguments:**
- `strategies` - Newline-separated list of strategy names

**Returns:**
- Newline-separated list of available strategies

**Checks:**
- `brew` - Requires `brew` command
- `cargo`/`cargo_git` - Requires `cargo` command
- `binary` - Requires `curl` command

**Example:**
```bash
available=$(filter_available_strategies "$strategies")
```

---

### `try_install(tool_name, strategy, tool_spec)`

Attempt installation with retry logic.

**Arguments:**
- `tool_name` - Tool command name
- `strategy` - Strategy name (brew, cargo, cargo_git, binary)
- `tool_spec` - JSON tool specification

**Returns:**
- `0` on success
- `1` on failure after 2 attempts

**Behavior:**
- Tries installation up to 2 times
- 2-second delay between retries
- Logs all attempts to INSTALL_LOG

**Example:**
```bash
if try_install "asciinema" "brew" "$spec"; then
    echo "Installation succeeded"
fi
```

---

### `verify_installation(tool_name, tool_spec)`

Verify tool installed and healthy.

**Arguments:**
- `tool_name` - Tool command name
- `tool_spec` - JSON tool specification

**Returns:**
- `0` if tool installed and healthy
- `1` otherwise

**Behavior:**
- Invalidates cache for this tool
- Uses `detect_tool()` from tool-detector.sh
- Checks both installation and health status

**Example:**
```bash
if verify_installation "asciinema" "$spec"; then
    echo "Tool verified"
fi
```

---

### `prompt_user_consent(tool_name, purpose, strategies)`

Get user approval for installation.

**Arguments:**
- `tool_name` - Tool command name
- `purpose` - User-facing description
- `strategies` - Newline-separated list of strategies

**Returns:**
- `0` if user approves
- `1` if user declines or SKIP_ALL is set

**Example:**
```bash
if prompt_user_consent "agg" "Convert .cast to .gif" "$strategies"; then
    # User approved
fi
```

## Stub Functions (Wave 2 Implementation)

The following functions are currently stubs that return failure:

### `install_via_brew(tool_name, tool_spec)`

Install using Homebrew.

**Current:** Stub returning 1
**Wave 2:** Will run `brew install <package>`

---

### `install_via_cargo(tool_name, tool_spec)`

Install using Cargo from crates.io.

**Current:** Stub returning 1
**Wave 2:** Will run `cargo install <package>`

---

### `install_via_cargo_git(tool_name, tool_spec)`

Install using Cargo from Git repository.

**Current:** Stub returning 1
**Wave 2:** Will run `cargo install --git <repo_url>`

---

### `install_via_binary(tool_name, tool_spec)`

Install by downloading binary.

**Current:** Stub returning 1
**Wave 2:** Will download from URL, verify checksum, install to target

## Testing

### Run Built-in Test
```bash
./scripts/dependency-installer.sh
```

### Test with Debug Output
```bash
DEBUG=1 ./scripts/dependency-installer.sh
```

### Integration Test
```bash
# Parse frontmatter
deps_json=$(source scripts/dependency-manager.sh && parse_frontmatter)

# Get tool spec
agg_spec=$(echo "$deps_json" | jq '.agg')

# Test strategy extraction
source scripts/dependency-installer.sh
strategies=$(get_install_strategies "$agg_spec")
echo "Strategies: $strategies"

# Test filtering
available=$(filter_available_strategies "$strategies")
echo "Available: $available"
```

## Installation Log

All installation attempts are logged to `$INSTALL_LOG` (default: `/tmp/craft-install-$$.log`).

**Log entries include:**
- Timestamp
- User consent decisions
- Installation attempts and results
- Verification outcomes

**Example log:**
```
[2026-01-17 15:00:00] === Starting installation: agg ===
[2026-01-17 15:00:01] User approved installation of agg
[2026-01-17 15:00:01] Attempting cargo_git installation for agg
[2026-01-17 15:00:03] Installation failed via cargo_git on attempt 1: [error details]
[2026-01-17 15:00:05] Installation failed via cargo_git on attempt 2: [error details]
[2026-01-17 15:00:05] All attempts failed for cargo_git
[2026-01-17 15:00:05] === Installation failed: agg (all strategies exhausted) ===
```

## Next Steps (Wave 2)

1. Implement `install_via_brew()` - Run brew install commands
2. Implement `install_via_cargo()` - Run cargo install from crates.io
3. Implement `install_via_cargo_git()` - Run cargo install from git
4. Implement `install_via_binary()` - Download and install binaries
5. Add checksum verification for binary downloads
6. Add platform-specific binary selection (macOS vs Linux, x86_64 vs arm64)
7. Add progress indicators for long-running installs

## Dependencies

- `dependency-manager.sh` - Frontmatter parsing
- `tool-detector.sh` - Tool detection and verification
- `session-cache.sh` - Cache management
- `jq` - JSON parsing
- `python3` - YAML/JSON processing

## Platform Support

- **macOS** (arm64/x86_64) - Full support (brew, cargo, binary)
- **Linux** (x86_64) - Full support (apt/yum, cargo, binary)
- **Other platforms** - Binary download only (if available)
