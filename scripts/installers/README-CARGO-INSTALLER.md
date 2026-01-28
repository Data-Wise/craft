# Cargo Installer - Implementation Documentation

**File:** `scripts/installers/cargo-installer.sh`
**Phase:** 2 (Auto-Installation)
**Status:** ✅ Complete
**Created:** 2026-01-17

---

## Overview

The Cargo installer provides Rust package installation capabilities for the Craft demo dependency management system. It implements two installation strategies:

1. **cargo** - Install from crates.io registry
2. **cargo_git** - Install from git repository

Both strategies compile packages from source, which can take significant time (2-8 minutes typical).

---

## Functions

### `check_cargo_available()`

Verifies that cargo is installed and functional.

**Returns:**

- `0` - Cargo is available
- `1` - Cargo is not available or not functional

**Usage:**

```bash
if check_cargo_available; then
    echo "Cargo is available"
else
    echo "Cargo is not available"
fi
```

---

### `cargo_install_package(tool_name, package)`

Install a Rust package from crates.io.

**Parameters:**

- `tool_name` - Display name of the tool (e.g., "agg")
- `package` - Crate name on crates.io (e.g., "agg")

**Returns:**

- `0` - Installation successful
- `1` - Installation failed

**Output:** JSON to stdout

- Success: `{"success": true}`
- Failure: `{"success": false, "error": "error message"}`

**Side Effects:**

- Displays progress messages to stderr
- Creates log file: `/tmp/cargo-install-$$.log`
- Installs binary to `~/.cargo/bin/`
- Deletes log file on success (keeps on failure)

**Compilation Time:** 2-5 minutes typical

**Usage:**

```bash
# Install agg from crates.io
cargo_install_package "agg" "agg"

# Check result
if [ $? -eq 0 ]; then
    echo "Installation succeeded"
else
    echo "Installation failed"
fi
```

**Example Output (Success):**

```
⏳ Compiling agg from source (this may take 2-5 minutes)...
   This is normal for Rust packages - please be patient
   Updating crates.io index
   Downloading crates dependencies...
   Compiling agg v1.4.3
   Finished release [optimized] target(s) in 3m 42s
✓ Compiled successfully
{"success": true}
```

**Example Output (Failure):**

```
⏳ Compiling agg from source (this may take 2-5 minutes)...
   This is normal for Rust packages - please be patient
   Error: failed to compile `agg v1.4.3`
✗ Compilation failed
See log: /tmp/cargo-install-12345.log
{"success": false, "error": "Compilation failed. See /tmp/cargo-install-12345.log for details."}
```

---

### `cargo_install_from_git(tool_name, repo_url)`

Install a Rust package from a git repository.

**Parameters:**

- `tool_name` - Display name of the tool (e.g., "agg")
- `repo_url` - Git repository URL (e.g., "<https://github.com/asciinema/agg>")

**Returns:**

- `0` - Installation successful
- `1` - Installation failed

**Output:** JSON to stdout

- Success: `{"success": true}`
- Failure: `{"success": false, "error": "error message"}`

**Side Effects:**

- Displays progress messages to stderr
- Creates log file: `/tmp/cargo-git-install-$$.log`
- Clones repository (temporary location)
- Installs binary to `~/.cargo/bin/`
- Deletes log file on success (keeps on failure)

**Compilation Time:** 3-8 minutes typical (includes git clone)

**Requirements:**

- `cargo` must be installed
- `git` must be installed

**Usage:**

```bash
# Install agg from GitHub
cargo_install_from_git "agg" "https://github.com/asciinema/agg"

# Check result
if [ $? -eq 0 ]; then
    echo "Installation succeeded"
else
    echo "Installation failed"
fi
```

**Example Output (Success):**

```
⏳ Compiling agg from git (this may take 3-8 minutes)...
   This is normal for Rust packages - please be patient
   Cloning and building from: https://github.com/asciinema/agg
   Updating git repository `https://github.com/asciinema/agg`
   Downloading crates dependencies...
   Compiling agg v1.4.3
   Finished release [optimized] target(s) in 5m 12s
✓ Compiled successfully from git
{"success": true}
```

**Example Output (Git Not Available):**

```
{"success": false, "error": "Git not installed. Install git first."}
```

---

## Integration with dependency-installer.sh

The cargo installer is sourced by `dependency-installer.sh` and integrated via wrapper functions:

```bash
# Source the installer
source "$SCRIPT_DIR/installers/cargo-installer.sh"

# Wrapper function for cargo install
install_via_cargo() {
    local tool_name="$1"
    local tool_spec="$2"

    # Extract package name from tool spec
    local package
    package=$(echo "$tool_spec" | jq -r '.install.cargo' 2>/dev/null)

    # Call the installer
    if cargo_install_package "$tool_name" "$package"; then
        return 0
    else
        return 1
    fi
}

# Wrapper function for cargo git install
install_via_cargo_git() {
    local tool_name="$1"
    local tool_spec="$2"

    # Extract repo URL from tool spec
    local repo_url
    repo_url=$(echo "$tool_spec" | jq -r '.install.cargo_git' 2>/dev/null)

    # Call the installer
    if cargo_install_from_git "$tool_name" "$repo_url"; then
        return 0
    else
        return 1
    fi
}
```

---

## Error Handling

### Cargo Not Installed

**Detection:**

```bash
if ! command -v cargo &> /dev/null; then
    # Cargo not found
fi
```

**Output:**

```json
{"success": false, "error": "Cargo not installed. Install Rust from https://rustup.rs/"}
```

**User Guidance:**

- Install Rust via rustup: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- Or via Homebrew: `brew install rust`

---

### Git Not Installed (cargo_git only)

**Detection:**

```bash
if ! command -v git &> /dev/null; then
    # Git not found
fi
```

**Output:**

```json
{"success": false, "error": "Git not installed. Install git first."}
```

**User Guidance:**

- Install Git via Homebrew: `brew install git`
- Or via system package manager

---

### Compilation Errors

**Common Causes:**

1. Missing system dependencies (gcc, make, pkg-config)
2. Network errors during dependency download
3. Source code compile errors
4. Incompatible Rust version

**Output:**

```json
{"success": false, "error": "error: failed to compile package..."}
```

**Log File:** `/tmp/cargo-install-$$.log` or `/tmp/cargo-git-install-$$.log`

**Debugging:**

```bash
# View full compilation log
cat /tmp/cargo-install-12345.log

# Check for common issues
grep -i "error" /tmp/cargo-install-12345.log
grep -i "failed" /tmp/cargo-install-12345.log
```

---

### Network Errors

**Common Scenarios:**

1. Cannot reach crates.io registry
2. Cannot clone git repository
3. Dependency download failures

**Example Error:**

```
error: failed to download from `https://crates.io/...`
```

**Resolution:**

- Check internet connection
- Verify firewall/proxy settings
- Retry installation

---

## Performance Characteristics

### Compilation Time

| Strategy | Typical Time | Worst Case |
|----------|--------------|------------|
| `cargo` | 2-5 minutes | 10 minutes |
| `cargo_git` | 3-8 minutes | 15 minutes |

**Factors Affecting Speed:**

- Number of dependencies
- System CPU/RAM
- Network speed (for downloads)
- Rust toolchain version
- Build cache (faster on subsequent installs)

---

### Resource Usage

**CPU:**

- High during compilation (all cores utilized)
- `cargo` runs in release mode (`--release`)

**Memory:**

- Typical: 500MB - 2GB
- Large projects: up to 4GB

**Disk:**

- Build artifacts: 100MB - 1GB temporary
- Final binary: 1MB - 50MB (in `~/.cargo/bin/`)
- Build cache: `~/.cargo/registry/` (persistent)

**Network:**

- Download dependencies from crates.io
- Git clone for `cargo_git` (can be large)

---

## User Experience

### Progress Indicators

Both functions show clear progress messages:

1. **Start Message:**

   ```
   ⏳ Compiling <tool> from source (this may take 2-5 minutes)...
      This is normal for Rust packages - please be patient
   ```

2. **Cargo Output:**
   - Real-time compilation output (shown to stderr)
   - Progress bars for downloads
   - Compiler messages

3. **Completion:**

   ```
   ✓ Compiled successfully
   ```

---

### Installation Location

**Binary Path:** `~/.cargo/bin/<tool_name>`

**PATH Setup:**

```bash
# Add to ~/.zshrc or ~/.bashrc
export PATH="$HOME/.cargo/bin:$PATH"
```

**Verification:**

```bash
# Check if installed
which agg
# Output: /Users/username/.cargo/bin/agg

# Test binary
agg --version
```

---

## Testing

### Self-Test

Run the installer directly to test:

```bash
./scripts/installers/cargo-installer.sh
```

**Output:**

```
Cargo Installer Test
====================

Test 1: Check cargo availability
✓ Cargo is available
cargo 1.92.0 (Homebrew)

Test 2: Test argument parsing
Would install 'agg' via: cargo install agg
Expected output: {"success": true/false, ...}

Test 3: Available functions
  - check_cargo_available()
  - cargo_install_package(tool_name, package)
  - cargo_install_from_git(tool_name, repo_url)

Note: To test actual installation (takes 2-8 minutes):
  source scripts/installers/cargo-installer.sh
  cargo_install_package 'agg' 'agg'
  cargo_install_from_git 'agg' 'https://github.com/asciinema/agg'

Test complete!
```

---

### Manual Testing

```bash
# Source the installer
source scripts/installers/cargo-installer.sh

# Test 1: Check cargo availability
check_cargo_available
echo "Exit code: $?"

# Test 2: Install from crates.io (takes 2-5 minutes)
# cargo_install_package "agg" "agg"

# Test 3: Install from git (takes 3-8 minutes)
# cargo_install_from_git "agg" "https://github.com/asciinema/agg"
```

---

### Integration Testing

```bash
# Test via dependency-installer.sh
source scripts/dependency-installer.sh

# Create test tool spec
test_spec='{
  "install": {
    "cargo": "agg",
    "cargo_git": "https://github.com/asciinema/agg"
  }
}'

# Test cargo strategy
install_via_cargo "agg" "$test_spec"

# Test cargo_git strategy
install_via_cargo_git "agg" "$test_spec"
```

---

## Troubleshooting

### Issue: Cargo not found

**Symptom:** `{"success": false, "error": "Cargo not installed..."}`

**Solution:**

```bash
# Install Rust via rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Or via Homebrew
brew install rust

# Verify installation
cargo --version
```

---

### Issue: Compilation timeout

**Symptom:** Process hangs for > 15 minutes

**Solution:**

1. Check log file for errors: `cat /tmp/cargo-install-*.log`
2. Kill process: `pkill -f "cargo install"`
3. Try binary installation strategy instead
4. Increase system resources (RAM, CPU)

---

### Issue: Binary not in PATH

**Symptom:** `which <tool>` returns nothing after successful install

**Solution:**

```bash
# Add cargo bin to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Make permanent (add to ~/.zshrc)
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc

# Reload shell
source ~/.zshrc
```

---

### Issue: Permission denied

**Symptom:** Error writing to `~/.cargo/bin/`

**Solution:**

```bash
# Fix cargo directory permissions
chmod -R u+w ~/.cargo

# Retry installation
```

---

## Future Enhancements

1. **Progress bars** - Show compilation progress percentage
2. **Parallel builds** - Use `cargo install -j <N>` for faster compilation
3. **Binary caching** - Cache pre-built binaries for common tools
4. **Version pinning** - Install specific versions: `cargo install agg@1.4.3`
5. **Incremental builds** - Reuse build cache for faster recompilation
6. **ARM optimization** - Detect Apple Silicon and optimize flags

---

## Related Files

| File | Purpose |
|------|---------|
| `scripts/dependency-installer.sh` | Main installation orchestrator |
| `scripts/installers/brew-installer.sh` | Homebrew installer (alternative) |
| `scripts/installers/binary-installer.sh` | Binary download installer (alternative) |
| `scripts/tool-detector.sh` | Tool detection and health checks |
| `docs/specs/SPEC-demo-dependency-management-2026-01-17.md` | Architecture specification |

---

## References

- [Cargo Documentation](https://doc.rust-lang.org/cargo/)
- [Cargo Install Command](https://doc.rust-lang.org/cargo/commands/cargo-install.html)
- [Rustup Installation](https://rustup.rs/)
- [Crates.io Registry](https://crates.io/)

---

**Status:** ✅ Implementation complete and tested
**Next Steps:** Integrate with `/craft:docs:demo --fix` workflow
