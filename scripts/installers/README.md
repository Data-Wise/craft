# Installers

Package installation backends for dependency management.

## Overview

Each installer is a self-contained shell script that handles installation via a specific package manager or method.

## Available Installers

### brew-installer.sh

**Purpose:** Install packages via Homebrew (macOS/Linux)

**Functions:**
- `check_brew_available()` - Check if Homebrew is installed and functional
- `brew_search_package(package)` - Verify package exists in Homebrew
- `brew_install_package(tool_name, package)` - Install package via brew
- `get_brew_status()` - Get Homebrew installation status (JSON)

**Output:** JSON format
```json
{
  "success": true|false,
  "error": "error message" (if failed),
  "message": "info message" (if already installed)
}
```

**Example Usage:**
```bash
source scripts/installers/brew-installer.sh

# Check availability
if check_brew_available; then
    echo "Homebrew is available"
fi

# Search for package
if brew_search_package "gifsicle"; then
    echo "Package found"
fi

# Install package
result=$(brew_install_package "gifsicle" "gifsicle")
if echo "$result" | jq -e '.success' > /dev/null; then
    echo "Installation successful"
fi
```

**Platform Support:**
- ✅ macOS (primary)
- ✅ Linux (if Homebrew installed)

**Error Handling:**
- Homebrew not installed
- Package not found
- Installation fails
- Already installed (success)

### cargo-installer.sh

**Purpose:** Install Rust packages via cargo

**Status:** ✅ Implemented (Wave 1)

### Binary Installer (TBD)

**Purpose:** Download and install pre-compiled binaries

**Status:** 🚧 Not yet implemented

## Integration

These installers are sourced by `dependency-installer.sh` which provides:
- Wrapper functions that extract package names from tool specs
- Retry logic (2 attempts)
- Logging to `/tmp/craft-install-$SESSION_ID.log`
- User consent prompts
- Fallback to alternative installation methods

## Testing

Each installer can be tested standalone:

```bash
# Test brew installer
source scripts/installers/brew-installer.sh
get_brew_status | jq .

# Test with real package
brew_install_package "gifsicle" "gifsicle" | jq .
```

## Architecture

```
dependency-installer.sh (orchestrator)
├── Source: brew-installer.sh
├── Source: cargo-installer.sh
├── Source: binary-installer.sh (TBD)
└── Wrappers:
    ├── install_via_brew(tool_name, tool_spec)
    ├── install_via_cargo(tool_name, tool_spec)
    ├── install_via_cargo_git(tool_name, tool_spec)
    └── install_via_binary(tool_name, tool_spec)
```

## Adding New Installers

1. Create `scripts/installers/<manager>-installer.sh`
2. Implement:
   - `check_<manager>_available()` - Availability check
   - `<manager>_search_package(package)` - Package search
   - `<manager>_install_package(tool_name, package)` - Installation
   - `get_<manager>_status()` - Status query (JSON)
3. Return JSON: `{"success": true|false, "error": "..."}`
4. Source in `dependency-installer.sh`
5. Add wrapper function `install_via_<manager>(tool_name, tool_spec)`
6. Add to strategy priority in `INSTALL_PRIORITY` array

## File Locations

```
scripts/
└── installers/
    ├── README.md (this file)
    ├── brew-installer.sh
    ├── cargo-installer.sh
    └── binary-installer.sh (TBD)
```

## Related Documentation

- [INSTALLER-USAGE.md](../INSTALLER-USAGE.md) - High-level usage guide
- [README-PHASE2-INSTALLER.md](../README-PHASE2-INSTALLER.md) - Phase 2 implementation guide
- [Spec](../../docs/specs/SPEC-demo-dependency-management-2026-01-17.md) - Architecture spec
