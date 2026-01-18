# API Reference - Dependency Management System

Complete reference for all scripts, functions, and interfaces in the dependency management system.

---

## Table of Contents

- [Core Scripts](#core-scripts)
  - [dependency-manager.sh](#dependency-managersh)
  - [tool-detector.sh](#tool-detectorsh)
  - [session-cache.sh](#session-cachesh)
- [Installation Scripts](#installation-scripts)
  - [dependency-installer.sh](#dependency-installersh)
  - [consent-prompt.sh](#consent-promptsh)
- [Conversion Scripts](#conversion-scripts)
  - [convert-cast.sh](#convert-castsh)
  - [batch-convert.sh](#batch-convertsh)
- [Advanced Features](#advanced-features)
  - [health-check.sh](#health-checksh)
  - [version-check.sh](#version-checksh)
  - [repair-tools.sh](#repair-toolssh)
- [Data Formats](#data-formats)
- [Exit Codes](#exit-codes)

---

## Core Scripts

### dependency-manager.sh

**Purpose**: Main orchestrator for dependency checking and management

**Usage**:
```bash
# Source for function access
source scripts/dependency-manager.sh

# Direct execution
./scripts/dependency-manager.sh <command> [method]
```

**Commands**:

#### `parse_frontmatter`
Extracts dependency metadata from YAML frontmatter.

**Signature**:
```bash
parse_frontmatter() -> JSON
```

**Returns**:
```json
{
  "asciinema": {
    "required": true,
    "purpose": "Record real terminal sessions",
    "install": {...},
    "version": {...},
    "health": {...}
  }
}
```

**Example**:
```bash
source scripts/dependency-manager.sh
metadata=$(parse_frontmatter)
echo "$metadata" | jq '.asciinema.required'
# Output: true
```

---

#### `check_dependencies`
Checks installation status, health, and versions for a method.

**Signature**:
```bash
check_dependencies <method> -> JSON
```

**Parameters**:
- `method` (string): Method name (`asciinema` or `vhs`)

**Returns**:
```json
[
  {
    "name": "asciinema",
    "installed": true,
    "version": "2.3.0",
    "version_ok": true,
    "health": "ok",
    "required": true,
    "install_cmd": "brew install asciinema"
  }
]
```

**Example**:
```bash
./scripts/dependency-manager.sh check_dependencies asciinema
```

---

#### `display_status_table`
Displays dependencies as formatted table.

**Signature**:
```bash
display_status_table <method> <status_json>
```

**Parameters**:
- `method` (string): Method name
- `status_json` (string): JSON from `check_dependencies`

**Output**:
```
╔════════════════════════════════════════════════════╗
║  DEPENDENCY STATUS - asciinema method              ║
╚════════════════════════════════════════════════════╝

Tool         Status    Version    Health    Required
──────────────────────────────────────────────────────
asciinema    ✅        2.3.0      ok        yes
agg          ❌        -          n/a       yes
gifsicle     ✅        1.96       ok        yes
```

---

#### `display_status_json`
Outputs dependency status as JSON for CI/CD.

**Signature**:
```bash
display_status_json <method> [status_json] -> JSON
```

**Parameters**:
- `method` (string): Method name
- `status_json` (string, optional): Pre-computed status

**Returns**:
```json
{
  "status": "ok",
  "method": "asciinema",
  "timestamp": "2026-01-17T16:00:00Z",
  "tools": [...]
}
```

**Status Values**:
- `ok`: All required tools installed and healthy
- `issues`: Missing or broken tools
- `unknown`: Could not determine status

**Example**:
```bash
./scripts/dependency-manager.sh display_status_json asciinema > status.json
```

---

### tool-detector.sh

**Purpose**: Detect installed tools and their paths

**Usage**:
```bash
source scripts/tool-detector.sh
```

**Functions**:

#### `detect_tool`
Detects if a tool is installed and returns its path.

**Signature**:
```bash
detect_tool <tool_name> <search_cmd> -> string
```

**Parameters**:
- `tool_name` (string): Name of the tool
- `search_cmd` (string): Command to locate tool (e.g., `which asciinema`)

**Returns**:
- Tool path if found (e.g., `/usr/local/bin/asciinema`)
- Empty string if not found

**Example**:
```bash
source scripts/tool-detector.sh
path=$(detect_tool "asciinema" "which asciinema")
if [ -n "$path" ]; then
    echo "Found at: $path"
fi
```

---

### session-cache.sh

**Purpose**: Performance caching for dependency checks

**Usage**:
```bash
source scripts/session-cache.sh
```

**Configuration**:
- Cache TTL: 60 seconds
- Cache location: `$TMPDIR/.craft-demo-cache-$$`

**Functions**:

#### `init_cache`
Initializes cache for current session.

**Signature**:
```bash
init_cache()
```

**Example**:
```bash
source scripts/session-cache.sh
init_cache
```

---

#### `get_cached_status`
Retrieves cached dependency status if valid.

**Signature**:
```bash
get_cached_status <method> -> JSON | empty
```

**Parameters**:
- `method` (string): Method name

**Returns**:
- Cached JSON if valid and not expired
- Empty string if cache miss or expired

**Example**:
```bash
source scripts/session-cache.sh
cached=$(get_cached_status "asciinema")
if [ -n "$cached" ]; then
    echo "Cache hit!"
fi
```

---

#### `store_cache`
Stores dependency status in cache.

**Signature**:
```bash
store_cache <method> <status_json>
```

**Parameters**:
- `method` (string): Method name
- `status_json` (string): Status to cache

**Example**:
```bash
source scripts/session-cache.sh
store_cache "asciinema" "$status_json"
```

---

## Installation Scripts

### dependency-installer.sh

**Purpose**: Multi-strategy installation framework

**Usage**:
```bash
source scripts/dependency-installer.sh
```

**Functions**:

#### `install_tool`
Attempts to install a tool using available strategies.

**Signature**:
```bash
install_tool <tool_name> <install_spec> -> exit_code
```

**Parameters**:
- `tool_name` (string): Name of tool to install
- `install_spec` (JSON): Installation specification from frontmatter

**Installation Strategies** (tried in order):
1. **Homebrew** (`brew install`)
2. **Cargo** (`cargo install`)
3. **Binary download** (GitHub releases)
4. **APT** (`apt install`) - Linux only
5. **YUM** (`yum install`) - Linux only

**Exit Codes**:
- `0`: Installation successful
- `1`: Installation failed (all strategies exhausted)

**Example**:
```bash
source scripts/dependency-installer.sh
install_spec='{"brew":"asciinema","apt":"asciinema"}'
install_tool "asciinema" "$install_spec"
```

---

### consent-prompt.sh

**Purpose**: Interactive consent for installations

**Usage**:
```bash
source scripts/consent-prompt.sh
```

**Functions**:

#### `prompt_consent`
Prompts user for installation consent.

**Signature**:
```bash
prompt_consent <tool_name> <install_cmd> -> boolean
```

**Parameters**:
- `tool_name` (string): Name of tool
- `install_cmd` (string): Command that will be executed

**Returns**:
- `0`: User consented (yes)
- `1`: User declined (no)

**Example**:
```bash
source scripts/consent-prompt.sh
if prompt_consent "agg" "cargo install agg"; then
    echo "Installing agg..."
fi
```

---

## Conversion Scripts

### convert-cast.sh

**Purpose**: Convert single .cast file to .gif

**Usage**:
```bash
./scripts/convert-cast.sh <input.cast> [output.gif]
```

**Parameters**:
- `input.cast` (required): Path to .cast file
- `output.gif` (optional): Output path (default: same name as input)

**Process**:
1. Validate .cast file exists and is readable
2. Convert using `agg` with optimized settings
3. Optimize with `gifsicle -O3 --colors 256`
4. Report file size and conversion time

**agg Settings**:
```bash
agg --font-size 16 \
    --line-height 1.4 \
    --theme monokai \
    input.cast output.gif
```

**Example**:
```bash
# Basic usage
./scripts/convert-cast.sh demo.cast

# Custom output
./scripts/convert-cast.sh demo.cast docs/demo.gif

# Check exit code
if ./scripts/convert-cast.sh demo.cast; then
    echo "Conversion successful"
fi
```

**Exit Codes**:
- `0`: Conversion successful
- `1`: File not found or conversion failed

---

### batch-convert.sh

**Purpose**: Bulk conversion of .cast files

**Usage**:
```bash
./scripts/batch-convert.sh [options]
```

**Options**:
- `--search-path <path>`: Directory to search (default: `docs/`)
- `--dry-run`: Preview without converting
- `--force`: Overwrite existing GIFs
- `--method <method>`: Conversion method (default: `asciinema`)

**Process**:
1. Find all .cast files in search path(s)
2. Filter out files with existing .gif (unless `--force`)
3. Convert each file with progress tracking
4. Display summary statistics

**Output**:
```
Found 5 .cast files
Converting: demo1.cast → demo1.gif... ✓ (2.3s, 145KB)
Converting: demo2.cast → demo2.gif... ✓ (1.8s, 98KB)
...
Summary: 5/5 converted, 0 failed
Total time: 12.4s
Total size: 567KB
```

**Example**:
```bash
# Dry run
./scripts/batch-convert.sh --dry-run

# Convert all in docs/
./scripts/batch-convert.sh

# Convert specific directory
./scripts/batch-convert.sh --search-path examples/

# Force overwrite
./scripts/batch-convert.sh --force
```

**Exit Codes**:
- `0`: All conversions successful
- `1`: One or more conversions failed
- `2`: File exists (use `--force` to overwrite)

---

## Advanced Features

### health-check.sh

**Purpose**: Validate tool health and functionality

**Usage**:
```bash
source scripts/health-check.sh
```

**Functions**:

#### `run_health_check`
Executes health check command and validates exit code.

**Signature**:
```bash
run_health_check <tool_name> <check_cmd> <expected_exit> -> JSON
```

**Parameters**:
- `tool_name` (string): Name of tool
- `check_cmd` (string): Command to execute
- `expected_exit` (integer): Expected exit code (usually 0)

**Returns**:
```json
{
  "tool": "asciinema",
  "health": "ok",
  "exit_code": 0,
  "message": "Health check passed"
}
```

**Health States**:
- `ok`: Tool responds correctly
- `broken`: Tool installed but fails health check
- `n/a`: Tool not installed

**Example**:
```bash
source scripts/health-check.sh
result=$(run_health_check "asciinema" "asciinema --help" 0)
echo "$result" | jq '.health'
```

---

#### `validate_all_health`
Validates health for all tools in a method.

**Signature**:
```bash
validate_all_health <method> -> JSON
```

**Parameters**:
- `method` (string): Method name

**Returns**:
```json
{
  "asciinema": {"health": "ok", "exit_code": 0},
  "agg": {"health": "ok", "exit_code": 0},
  "gifsicle": {"health": "ok", "exit_code": 0}
}
```

---

### version-check.sh

**Purpose**: Semantic version comparison and validation

**Usage**:
```bash
source scripts/version-check.sh
```

**Functions**:

#### `extract_version`
Extracts version number from tool output.

**Signature**:
```bash
extract_version <tool_name> <version_cmd> -> string
```

**Parameters**:
- `tool_name` (string): Name of tool
- `version_cmd` (string): Command to get version

**Returns**:
- Version string (e.g., `2.3.0`)
- `null` if not found

**Example**:
```bash
source scripts/version-check.sh
version=$(extract_version "asciinema" "asciinema --version")
echo "$version"  # Output: 2.3.0
```

---

#### `parse_version`
Parses version string into major.minor.patch components.

**Signature**:
```bash
parse_version <version_string> -> array
```

**Parameters**:
- `version_string` (string): Version like `1.2.3`

**Returns**:
- Space-separated string: `major minor patch`

**Example**:
```bash
source scripts/version-check.sh
read major minor patch <<< $(parse_version "2.3.0")
echo "Major: $major, Minor: $minor, Patch: $patch"
```

---

#### `compare_versions`
Compares two semantic versions.

**Signature**:
```bash
compare_versions <version1> <version2> -> integer
```

**Parameters**:
- `version1` (string): First version
- `version2` (string): Second version

**Returns**:
- `-1`: version1 < version2
- `0`: version1 = version2
- `1`: version1 > version2

**Example**:
```bash
source scripts/version-check.sh
result=$(compare_versions "1.2.3" "1.2.5")
if [ "$result" = "-1" ]; then
    echo "Upgrade needed"
fi
```

---

#### `check_version_requirement`
Validates version meets minimum requirement.

**Signature**:
```bash
check_version_requirement <tool> <current> <min> -> JSON
```

**Parameters**:
- `tool` (string): Tool name
- `current` (string): Current version
- `min` (string): Minimum required version

**Returns**:
```json
{
  "tool": "asciinema",
  "current": "2.3.0",
  "required": "2.0.0",
  "satisfied": true
}
```

---

### repair-tools.sh

**Purpose**: Automated tool repair and reinstallation

**Usage**:
```bash
source scripts/repair-tools.sh
```

**Functions**:

#### `detect_repair_candidates`
Identifies tools that need repair.

**Signature**:
```bash
detect_repair_candidates <method> -> JSON
```

**Parameters**:
- `method` (string): Method name

**Returns**:
```json
{
  "candidates": [
    {
      "tool": "agg",
      "issue": "not_installed",
      "recommendation": "Install via: cargo install agg"
    },
    {
      "tool": "gifsicle",
      "issue": "outdated",
      "current": "1.88",
      "required": "1.90",
      "recommendation": "Upgrade via: brew upgrade gifsicle"
    }
  ]
}
```

**Issue Types**:
- `not_installed`: Tool missing
- `broken`: Health check fails
- `outdated`: Version below minimum

---

#### `repair_tool`
Attempts to repair a single tool.

**Signature**:
```bash
repair_tool <tool_name> <method> -> exit_code
```

**Parameters**:
- `tool_name` (string): Tool to repair
- `method` (string): Method name

**Process**:
1. Detect issue type
2. Uninstall if needed
3. Reinstall using dependency-installer
4. Validate installation

**Exit Codes**:
- `0`: Repair successful
- `1`: Repair failed

---

## Data Formats

### Dependency Metadata (YAML)

```yaml
tool_name:
  required: boolean          # Is this tool required?
  purpose: string            # Human-readable description
  methods: [string]          # Applicable methods
  install:
    brew: string             # Homebrew formula
    cargo: string            # Cargo crate
    apt: string              # APT package
    binary:
      url: string            # Binary download URL
      target: string         # Install location
  version:
    min: string              # Minimum version (semver)
    check_cmd: string        # Command to get version
  health:
    check_cmd: string        # Command for health check
    expect_exit: integer     # Expected exit code
```

### Tool Status (JSON)

```json
{
  "name": "string",           // Tool name
  "installed": boolean,       // Is installed?
  "version": "string|null",   // Current version
  "version_ok": boolean,      // Meets minimum?
  "health": "ok|broken|n/a",  // Health status
  "required": boolean,        // Is required?
  "install_cmd": "string"     // Installation command
}
```

### Dependency Check Response (JSON)

```json
{
  "status": "ok|issues|unknown",
  "method": "string",
  "timestamp": "ISO8601",
  "tools": [
    // Array of Tool Status objects
  ]
}
```

---

## Exit Codes

Standard exit codes across all scripts:

| Code | Meaning | Usage |
|------|---------|-------|
| `0` | Success | All operations completed successfully |
| `1` | Dependency Issues | Missing required dependencies or health check failed |
| `2` | File Exists | Batch conversion blocked by existing files (use `--force`) |
| `3` | Missing Scripts | Required supporting scripts not found |
| `127` | Command Not Found | Tool not installed or not in PATH |

---

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `TMPDIR` | Cache directory location | System default |
| `DEBUG` | Enable debug output | `false` |
| `NO_COLOR` | Disable colored output | `false` |

---

## Error Handling

All scripts follow this error handling pattern:

```bash
set -uo pipefail  # Strict mode (no set -e for tests)

# Function-level error handling
function_name() {
    local result
    result=$(some_command) || {
        log_error "Command failed"
        return 1
    }
    echo "$result"
}
```

**Error Propagation**:
- Functions return non-zero on error
- Main scripts exit with appropriate code
- JSON responses include error details

---

## Integration Examples

### CI/CD Integration

```bash
#!/bin/bash
# .github/workflows/validate-deps.sh

set -euo pipefail

# Check dependencies
status_json=$(./scripts/dependency-manager.sh display_status_json asciinema)

# Parse status
status=$(echo "$status_json" | jq -r '.status')

if [ "$status" = "issues" ]; then
    echo "::error::Missing dependencies detected"
    echo "$status_json" | jq '.tools[] | select(.installed == false)'
    exit 1
fi

echo "::notice::All dependencies satisfied"
exit 0
```

### Custom Workflow Integration

```bash
#!/bin/bash
# my-workflow.sh

source scripts/dependency-manager.sh
source scripts/repair-tools.sh

# Check dependencies
if ! check_dependencies "asciinema" > /dev/null; then
    echo "Issues detected. Attempting repair..."

    # Detect candidates
    candidates=$(detect_repair_candidates "asciinema")

    # Repair each
    echo "$candidates" | jq -r '.candidates[].tool' | while read -r tool; do
        echo "Repairing $tool..."
        repair_tool "$tool" "asciinema"
    done
fi

# Proceed with main workflow
echo "All dependencies ready!"
```

---

**Last Updated**: 2026-01-17
**Version**: 1.26.0
**Status**: Production Ready
