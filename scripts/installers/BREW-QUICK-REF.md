# Brew Installer Quick Reference

## Functions

| Function | Args | Returns | Description |
|----------|------|---------|-------------|
| `check_brew_available()` | - | 0/1 | Check if Homebrew is installed and functional |
| `brew_search_package(package)` | package name | 0/1 | Verify package exists in Homebrew |
| `brew_install_package(tool, pkg)` | tool name, package | JSON | Install package via Homebrew |
| `get_brew_status()` | - | JSON | Get Homebrew installation status |

## JSON Output

**Success:**

```json
{"success": true}
{"success": true, "message": "Package already installed"}
```

**Failure:**

```json
{"success": false, "error": "Homebrew not installed or not functional"}
{"success": false, "error": "Package 'xyz' not found in Homebrew"}
{"success": false, "error": "Installation failed: ..."}
```

## Usage Examples

### Check Availability

```bash
source scripts/installers/brew-installer.sh

if check_brew_available; then
    echo "Homebrew is ready"
fi
```

### Search for Package

```bash
if brew_search_package "gifsicle"; then
    echo "Package found"
else
    echo "Package not found"
fi
```

### Install Package

```bash
result=$(brew_install_package "gifsicle" "gifsicle")
success=$(echo "$result" | jq -r '.success')

if [ "$success" = "true" ]; then
    echo "Installation successful"
else
    error=$(echo "$result" | jq -r '.error')
    echo "Installation failed: $error"
fi
```

### Get Status

```bash
get_brew_status | jq .
# Output:
# {
#   "status": "available",
#   "version": "5.0.10",
#   "path": "/opt/homebrew/bin/brew"
# }
```

## Integration with dependency-installer.sh

The `install_via_brew()` wrapper function:

1. Extracts package name from tool_spec JSON
2. Calls `brew_install_package()`
3. Parses JSON result
4. Returns 0 (success) or 1 (failure)

**Example:**

```bash
tool_spec='{"install": {"brew": "gifsicle"}}'
if install_via_brew "gifsicle" "$tool_spec"; then
    echo "Installation successful"
fi
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|-----------|
| "Homebrew not installed" | brew command not found | Install Homebrew |
| "Homebrew not functional" | brew --version fails | Reinstall/repair Homebrew |
| "Package not found" | Package doesn't exist | Check package name, try different source |
| "Installation failed" | brew install error | Check logs, verify permissions |

## Temp Files

Installation output logged to: `/tmp/brew-install-$$.log`

- Automatically cleaned up on success
- Retained on failure for debugging

## Platform Support

- ✅ macOS (ARM/Intel)
- ✅ Linux (with Homebrew)
- ❌ Windows (use WSL with Homebrew)

## Related

- [README.md](README.md) - Complete installer documentation
- [../INSTALLER-USAGE.md](../INSTALLER-USAGE.md) - User guide
- [../dependency-installer.sh](../dependency-installer.sh) - Orchestrator
