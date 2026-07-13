# Dependency Management for /folio:docs:demo

Complete guide to the dependency management system for demo GIF generation.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Flags Reference](#flags-reference)
- [Methods](#methods)
- [Tool Requirements](#tool-requirements)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)
- [Additional Documentation](#additional-documentation)

## Overview

The `/folio:docs:demo` command includes a comprehensive dependency management system
that automatically detects, validates, and installs required tools for terminal
GIF generation using either asciinema or VHS workflows.

**Key Features:**

- Auto-detection of installed tools
- Health validation and version checking
- Automated installation with user consent
- Batch conversion capabilities
- CI/CD integration with JSON output
- Tool repair functionality
- Session-based caching for performance

## Quick Start

```bash
# Check all dependencies
/folio:docs:demo --check

# Check specific method
/folio:docs:demo --check --method asciinema

# Install missing dependencies
/folio:docs:demo --fix

# Get JSON output for CI/CD
/folio:docs:demo --check --json
```

## Flags Reference

### Dependency Management Flags

| Flag | Description | Example |
|------|-------------|---------|
| `--check` | Validate all dependencies | `/folio:docs:demo --check` |
| `--check --method <method>` | Check specific method (asciinema/vhs) | `/folio:docs:demo --check --method vhs` |
| `--check --json` | JSON output for CI/CD | `/folio:docs:demo --check --json` |
| `--fix` | Auto-install missing dependencies | `/folio:docs:demo --fix` |
| `--fix --method <method>` | Install for specific method | `/folio:docs:demo --fix --method asciinema` |
| `--force` | Overwrite existing files | `/folio:docs:demo --convert demo.cast --force` |

### Conversion Flags

| Flag | Description | Example |
|------|-------------|---------|
| `--convert <cast> [output]` | Convert single .cast to .gif | `/folio:docs:demo --convert demo.cast` |
| `--convert ... --force` | Overwrite existing GIF | `/folio:docs:demo --convert demo.cast --force` |
| `--batch` | Convert all .cast files | `/folio:docs:demo --batch` |
| `--batch --dry-run` | Preview batch conversion | `/folio:docs:demo --batch --dry-run` |
| `--batch --method <method>` | Batch convert with specific method | `/folio:docs:demo --batch --method asciinema` |

## Methods

Two methods are supported for creating terminal GIFs:

### asciinema (Recommended)

**Best for:** Real terminal recordings, authentic output, recording-based workflows

**Tools required:**

- `asciinema` (required) - Record terminal sessions
- `agg` (required) - Convert .cast to .gif
- `gifsicle` (required) - Optimize GIF size
- `fswatch` (optional) - Watch mode for live updates

**Workflow:**

```bash
# 1. Record session
asciinema rec demo.cast

# 2. Convert to GIF
/folio:docs:demo --convert demo.cast

# 3. Batch convert all recordings
/folio:docs:demo --batch
```

**Benefits:**

- Records actual terminal output
- Perfect for showing real commands and results
- Captures timing and pauses naturally
- Easy to edit .cast file if needed

### VHS

**Best for:** Scripted/repeatable demos, consistent output, automated testing

**Tools required:**

- `vhs` (required) - Generate scripted demos
- `gifsicle` (required) - Optimize GIF size
- `ffmpeg` (optional) - Video processing

**Workflow:**

```bash
# 1. Create VHS tape script
cat > demo.tape <<EOF
Output demo.gif
Set FontSize 16
Type "echo 'Hello World'"
Enter
Sleep 2s
EOF

# 2. Generate GIF
vhs demo.tape

# 3. Optimize
gifsicle -O3 demo.gif -o demo.gif
```

**Benefits:**

- Repeatable and scriptable
- Consistent timing and output
- Good for automated demos
- Can be version controlled

## Tool Requirements

### Installation Methods

The dependency manager supports multiple installation strategies with fallback:

| Tool | Method 1 | Method 2 | Method 3 |
|------|----------|----------|----------|
| asciinema | brew install | apt install | Binary download |
| agg | cargo install | Binary download | - |
| gifsicle | brew install | apt install | - |
| vhs | brew install | Binary download | - |
| fswatch | brew install | apt install | - |

### Version Requirements

| Tool | Minimum Version | Recommended | Notes |
|------|----------------|-------------|-------|
| asciinema | 2.0+ | 2.3.0+ | Latest recommended |
| agg | 1.0+ | 1.4.3+ | Rust-based converter |
| gifsicle | 1.90+ | 1.96+ | GIF optimization |
| vhs | 0.6+ | Latest | Scripted demos |
| fswatch | 1.15+ | Latest | File watching |

### Checking Installed Versions

```bash
# Check specific tool version
asciinema --version
agg --version
gifsicle --version

# Check all dependencies and versions
/folio:docs:demo --check
```

## CI/CD Integration

### GitHub Actions Workflow

The project includes a pre-configured GitHub Actions workflow for dependency validation:

**Location:** `.github/workflows/validate-dependencies.yml`

**Triggers:**

- Push to main, dev, or feature/* branches
- Pull requests to main or dev
- Manual workflow dispatch

**What it does:**

1. Checks out code
2. Installs jq for JSON parsing
3. Validates asciinema method dependencies
4. Validates VHS method dependencies (optional)
5. Uploads JSON reports as artifacts
6. Reports status in job summary

**Example workflow run:**

```
✅ asciinema method: ok
⚠️  VHS method: issues
📊 Reports uploaded as artifacts
```

### Auto-Installation in CI

To automatically install dependencies in your CI pipeline:

```yaml
- name: Install demo dependencies
  run: |
    # Install with auto-confirmation
    yes | /folio:docs:demo --fix --method asciinema
```

### JSON Output Format

When using `--check --json`, the output follows this structure:

```json
{
  "status": "ok",
  "method": "asciinema",
  "timestamp": "2026-01-17T16:00:00Z",
  "tools": [
    {
      "name": "asciinema",
      "installed": true,
      "version": "2.3.0",
      "health": "ok",
      "path": "/usr/local/bin/asciinema"
    },
    {
      "name": "agg",
      "installed": false,
      "version": null,
      "health": "n/a",
      "path": null
    }
  ]
}
```

**Status values:**

- `ok` - All required tools installed and healthy
- `issues` - Missing or broken tools detected
- `unknown` - Could not determine status

**Health values:**

- `ok` - Tool installed and working
- `broken` - Tool installed but health check failed
- `outdated` - Tool installed but version is outdated
- `n/a` - Tool not installed

**Exit codes:**

- `0` - All dependencies OK
- `1` - Missing required dependencies or health check failed
- `2` - File exists (batch conversion, use --force)
- `3` - Missing required scripts

### Using JSON Output in Scripts

```bash
# Check and parse JSON output
/folio:docs:demo --check --json > deps.json

# Extract status
status=$(jq -r '.status' deps.json)
echo "Dependency status: $status"

# List missing tools
jq -r '.tools[] | select(.installed == false) | .name' deps.json

# Get tool version
version=$(jq -r '.tools[] | select(.name == "asciinema") | .version' deps.json)
echo "asciinema version: $version"
```

## Troubleshooting

### Common Issues

#### 1. Tool Not Detected (Installed but Shows Missing)

**Symptom:** Tool is installed but `--check` reports it as missing

**Solutions:**

```bash
# Verify tool is in PATH
which asciinema

# Reload shell
exec $SHELL

# Check PATH directly
echo $PATH

# Verify installation location
brew list asciinema  # for brew-installed tools
```

#### 2. Health Check Failing

**Symptom:** Tool installed but health check reports "broken"

**Solutions:**

```bash
# Test tool manually
asciinema --version

# Check for permission issues
ls -la $(which asciinema)

# Repair broken installation
./scripts/repair-tools.sh repair asciinema asciinema

# Reinstall from scratch
brew uninstall asciinema
/folio:docs:demo --fix --method asciinema
```

#### 3. Version Mismatch Warnings

**Symptom:** Tool installed but version is outdated or unsupported

**Solutions:**

```bash
# Check version requirements
./scripts/version-check.sh check asciinema

# Update via package manager
brew upgrade asciinema

# Or use repair tool
./scripts/repair-tools.sh repair asciinema asciinema

# Force installation of specific version
brew uninstall asciinema
brew install asciinema@2.3.0
```

#### 4. Permission Denied During Installation

**Symptom:** `--fix` fails with permission errors

**Solutions:**

```bash
# Use sudo for system-wide installation
sudo /folio:docs:demo --fix

# Or install to user directory
cargo install --root ~/.local agg

# Check /usr/local/bin permissions
ls -ld /usr/local/bin
sudo chown $(whoami):admin /usr/local/bin
```

#### 5. Conversion Fails (File Not Found)

**Symptom:** `--convert` fails because .cast file not found

**Solutions:**

```bash
# Verify .cast file exists
ls -la demo.cast

# Check file is readable
file demo.cast

# Ensure asciinema format
head -c 20 demo.cast  # Should show "{\\"version\\"" for JSON

# Re-record if file is corrupt
asciinema rec demo.cast
```

#### 6. GIF Optimization Issues

**Symptom:** GIF is too large or has quality issues

**Solutions:**

```bash
# Check GIF file
file output.gif
du -h output.gif

# Optimize with gifsicle
gifsicle -O3 output.gif -o output-optimized.gif

# Check gifsicle version
gifsicle --version

# Manual optimization options
gifsicle -O2 --colors 256 output.gif -o output.gif
```

### Debugging Tools

```bash
# Enable debug mode
DEBUG=1 /folio:docs:demo --check

# Check individual components
./scripts/dependency-manager.sh parse_frontmatter
./scripts/tool-detector.sh detect asciinema asciinema
./scripts/health-check.sh check agg
./scripts/version-check.sh check asciinema

# Repair specific tool
./scripts/repair-tools.sh repair agg asciinema

# Detect repair candidates
./scripts/repair-tools.sh detect asciinema

# Test health checks manually
./scripts/health-check.sh test_health_check asciinema asciinema

# Verbose output
./scripts/dependency-manager.sh check_dependencies asciinema --verbose
```

### Getting Help

```bash
# View command help
/folio:docs:demo --help

# Check specific script help
./scripts/dependency-manager.sh help

# Test dependencies with verbose output
/folio:docs:demo --check --verbose

# Generate diagnostic report
./scripts/dependency-manager.sh diagnose
```

## Architecture

### System Components

```
/folio:docs:demo (command entry point)
    │
    ├─ Phase 1: Dependency Checking
    │   ├─ dependency-manager.sh     - Orchestrator, main logic
    │   ├─ tool-detector.sh          - Tool detection logic
    │   ├─ health-check.sh           - Tool health validation
    │   └─ session-cache.sh          - Performance caching
    │
    ├─ Phase 2: Auto-Installation
    │   ├─ installer.sh              - Installation framework
    │   ├─ brew-installer.sh         - Homebrew installer
    │   ├─ cargo-installer.sh        - Rust/cargo installer
    │   └─ binary-installer.sh       - Binary downloader
    │
    ├─ Phase 3: Batch Conversion
    │   ├─ convert-cast.sh           - Single .cast file converter
    │   ├─ batch-convert.sh          - Bulk .cast processor
    │   └─ dry-run-output.sh         - Dry-run preview
    │
    └─ Phase 4: Advanced Features
        ├─ health-check.sh           - Tool health validation
        ├─ version-check.sh          - Version compatibility checking
        └─ repair-tools.sh           - Tool repair/reinstall
```

### Data Flow

```
User runs: /folio:docs:demo --check
    ↓
Parse frontmatter from demo.md command file
    ↓
For each method (asciinema, vhs):
    ├─ Detect installation (tool-detector.sh)
    ├─ Check health (health-check.sh)
    ├─ Verify version (version-check.sh)
    └─ Cache results (session-cache.sh)
    ↓
Generate JSON status output
    ↓
Display table (--check) OR JSON (--check --json)
```

### Dependency Tree

```
asciinema method:
  └─ Required:
     ├─ asciinema (detection: which asciinema)
     ├─ agg (detection: which agg)
     └─ gifsicle (detection: which gifsicle)
     └─ Optional:
        └─ fswatch (detection: which fswatch)

vhs method:
  └─ Required:
     ├─ vhs (detection: which vhs)
     └─ gifsicle (detection: which gifsicle)
     └─ Optional:
        └─ ffmpeg (detection: which ffmpeg)
```

### Key Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `dependency-manager.sh` | Main orchestrator | Called by /folio:docs:demo |
| `tool-detector.sh` | Find installed tools | `detect asciinema asciinema` |
| `health-check.sh` | Validate tool health | `check asciinema` |
| `version-check.sh` | Check tool versions | `check asciinema` |
| `installer.sh` | Framework for installation | Called by --fix |
| `brew-installer.sh` | Homebrew installation | Auto-selected on macOS |
| `cargo-installer.sh` | Cargo/Rust installation | Auto-selected for agg |
| `binary-installer.sh` | Binary download/install | Fallback method |
| `convert-cast.sh` | Single file conversion | `--convert demo.cast` |
| `batch-convert.sh` | Bulk conversion | `--batch` |
| `repair-tools.sh` | Tool repair | Called by diagnostics |

### Exit Codes

| Code | Meaning | When |
|------|---------|------|
| 0 | Success | All dependencies OK, conversions complete |
| 1 | Dependency issues | Missing required dependencies or health check failed |
| 2 | File exists | Batch conversion with existing output, use --force |
| 3 | Missing scripts | Required supporting scripts not found |
| 127 | Command not found | Tool not installed or not in PATH |

### Performance Optimization

**Session Caching:**

- Dependency checks cached per shell session (5-minute TTL)
- Reduces repeated checks during rapid-fire commands
- Cache invalidated on /folio:docs:demo --check with --force
- Cache stored in `$TMPDIR/.craft-demo-cache-*`

**Parallel Operations:**

- Multiple tools checked concurrently where possible
- Batch conversions processed in parallel
- Installation from multiple sources in parallel

## Examples

### Example 1: Check All Dependencies

```bash
$ /folio:docs:demo --check
Checking demo dependencies...

✅ asciinema method
  ✅ asciinema (2.3.0)
  ✅ agg (1.4.3)
  ✅ gifsicle (1.96)
  ⚠️  fswatch (not installed)

⚠️  vhs method
  ❌ vhs (not installed)
  ✅ gifsicle (1.96)

Summary: asciinema method ready, vhs optional
```

### Example 2: Fix Missing Dependencies

```bash
$ /folio:docs:demo --fix
Installing missing dependencies...

Would install:
  - agg (via cargo)
  - vhs (via brew)

Install? (y/n): y

Installing agg via cargo... ✅
Installing vhs via brew... ✅

All dependencies installed. Ready to record!
```

### Example 3: Check Specific Method with JSON

```bash
$ /folio:docs:demo --check --method asciinema --json
{
  "status": "ok",
  "method": "asciinema",
  "timestamp": "2026-01-17T16:00:00Z",
  "tools": [
    {
      "name": "asciinema",
      "installed": true,
      "version": "2.3.0",
      "health": "ok"
    }
  ]
}
```

### Example 4: Batch Convert with Dry-Run

```bash
$ /folio:docs:demo --batch --dry-run
Found 3 .cast files:
  demo1.cast → demo1.gif
  demo2.cast → demo2.gif
  demo3.cast → demo3.gif

Total GIFs to generate: 3
Estimated time: ~45 seconds
Disk space required: ~15 MB

Run with: /folio:docs:demo --batch
```

---

## Additional Documentation

For more detailed information, see:

### 📘 [API Reference](API-REFERENCE.md)

Complete function signatures, parameters, return values, and code examples for all scripts:

- `dependency-manager.sh` - Main orchestrator with 4 commands
- `tool-detector.sh` - Tool detection logic
- `session-cache.sh` - Performance caching (60s TTL)
- `dependency-installer.sh` - Multi-strategy installation
- `consent-prompt.sh` - User consent interface
- `convert-cast.sh` - Single file conversion
- `batch-convert.sh` - Batch processor
- `health-check.sh` - Health validation
- `version-check.sh` - Semantic versioning
- `repair-tools.sh` - Automated repair

**Includes**: JSON schemas, exit codes, integration examples

### 🏗️ [Architecture Diagrams](DEPENDENCY-ARCHITECTURE.md)

Visual architecture with 13 Mermaid diagrams:

- **System Overview**: 4 phases + storage architecture
- **Component Diagrams**: Detection, Installation, Conversion, Repair
- **Sequence Diagrams**: Check, Install, Convert, Repair workflows
- **Data Flow**: Dependency check and installation flows
- **Decision Trees**: Status determination, strategy selection
- **Integration**: CI/CD and command routing
- **Performance**: Caching strategy, parallel processing

**Includes**: Color-coded components, clear data flow visualization

### 👨‍💻 [Developer Guide](DEVELOPER-GUIDE.md)

Complete guide for contributors and maintainers:

- **Getting Started**: Setup, directory structure, quick start
- **Code Structure**: Patterns, naming conventions, error handling
- **Adding Features**: Step-by-step guides for new tools, strategies, checks
- **Testing**: Unit, validation, and E2E test patterns
- **Best Practices**: DOs, DON'Ts, common pitfalls
- **Common Tasks**: Debugging, profiling, documentation updates
- **Code Review**: 11-point checklist
- **Release Process**: Version bumps, tagging, deployment

**Includes**: 50+ code examples, test templates, troubleshooting guides

### 🧪 [Test Suite](https://github.com/Data-Wise/craft/blob/main/tests/test_dependency_management.sh)

Comprehensive test coverage (100% passing):

- **Unit Tests**: 50/50 passing - Script existence, functions, syntax
- **Validation Tests**: 12/12 passing - JSON output, sourcing, flags
- **E2E Tests**: 17/17 passing - Full workflows, integration, documentation

Run tests:

```bash
# All tests
./tests/test_dependency_management.sh all

# Specific suite
./tests/test_dependency_management.sh unit
./tests/test_dependency_management.sh validation
./tests/test_dependency_management.sh e2e
```

---

**Last Updated**: 2026-01-17
**Version**: 1.26.0 (Phase 4 Complete)
**Status**: Production Ready
**Test Coverage**: 100% (79/79 passing)
**Documentation**: Complete (API, Architecture, Developer Guide)
