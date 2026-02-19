---
description: Complete PyPI automation - build, publish, and workflow generation
arguments:
  - name: subcommand
    description: "Subcommand: publish|workflow|validate|setup|check"
    required: false
    default: publish
  - name: version
    description: "Specific version to publish (default: from pyproject.toml)"
    required: false
  - name: dry-run
    description: Preview actions without executing (build, publish, file creation)
    required: false
    default: false
    alias: -n
---

# /craft:dist:pypi - PyPI Automation Hub

Complete PyPI publishing automation with GitHub Actions workflows.

## Subcommands

| Command | Purpose |
|---------|---------|
| `publish` | Build and publish to PyPI (default) |
| `workflow` | Generate GitHub Actions release workflow |
| `validate` | Check package structure and metadata |
| `setup` | Full setup wizard (workflow + trusted publishing) |
| `check` | Pre-flight checks before publishing |

## Quick Start

```bash
# Validate package before publishing
/craft:dist:pypi validate

# Full automated setup (recommended for new projects)
/craft:dist:pypi setup

# Generate release workflow
/craft:dist:pypi workflow

# Pre-flight checks
/craft:dist:pypi check

# Preview any subcommand with --dry-run
/craft:dist:pypi workflow --dry-run
/craft:dist:pypi publish --dry-run
```

## Dry-Run Mode

Preview PyPI operations without executing them:

### Workflow Generation Dry-Run

```bash
/craft:dist:pypi workflow --dry-run
```

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: PyPI Workflow Generation                          │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Project Analysis:                                           │
│   - Package: aiterm                                           │
│   - Version: 0.6.1 (from pyproject.toml)                      │
│   - Build tool: uv                                            │
│   - License: MIT                                              │
│                                                               │
│ ✓ Files to Create:                                            │
│   - .github/workflows/pypi-release.yml (~140 lines)           │
│                                                               │
│ ✓ Workflow Configuration:                                     │
│   - Trigger: GitHub Release published                         │
│   - Environment: pypi (for trusted publishing)                │
│   - Permissions: id-token write                               │
│   - Python version: 3.12                                      │
│   - Build command: uv build                                   │
│   - Publish action: pypa/gh-action-pypi-publish@release/v1    │
│                                                               │
│ ✓ Post-Creation Steps:                                        │
│   1. Configure PyPI trusted publishing:                       │
│      https://pypi.org/manage/account/publishing/              │
│      - Project: aiterm                                        │
│      - Owner: Data-Wise                                       │
│      - Workflow: pypi-release.yml                             │
│      - Environment: pypi                                      │
│                                                               │
│   2. Create GitHub release to trigger:                        │
│      gh release create v0.6.1 --generate-notes                │
│                                                               │
│ ⚠ Notes:                                                      │
│   • Trusted publishing requires PyPI configuration            │
│   • Environment name must match workflow (pypi)               │
│   • First release must be manual to establish publisher       │
│                                                               │
│ 📊 Summary: 1 workflow file, 2 setup steps                    │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

### Publish Dry-Run

```bash
/craft:dist:pypi publish --dry-run
```

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: PyPI Package Publishing                           │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Pre-Flight Checks:                                          │
│   1. Validate pyproject.toml metadata                         │
│   2. Check version not already published                      │
│   3. Verify clean git repository                              │
│   4. Run tests (pytest)                                       │
│   5. Test build (uv build --no-publish)                       │
│                                                               │
│ ✓ Build Operations:                                           │
│   - Command: uv build                                         │
│   - Output: dist/aiterm-0.6.1.tar.gz                          │
│   - Output: dist/aiterm-0.6.1-py3-none-any.whl               │
│   - Size estimate: ~45 KB (tarball), ~38 KB (wheel)          │
│                                                               │
│ ✓ Publish Operations:                                         │
│   - Target: PyPI (https://pypi.org)                           │
│   - Method: Trusted publishing (no token required)            │
│   - Package: aiterm                                           │
│   - Version: 0.6.1                                            │
│                                                               │
│ ✓ Post-Publish Actions:                                       │
│   - Create git tag: v0.6.1                                    │
│   - Push tag to origin                                        │
│   - Verify package on PyPI: https://pypi.org/project/aiterm/  │
│                                                               │
│ ⚠ Critical Warnings:                                          │
│   • Publishing to PyPI is IRREVERSIBLE                        │
│   • Cannot delete or modify published versions                │
│   • Version 0.6.1 will be permanently claimed                 │
│   • Ensure all tests pass before publishing                   │
│                                                               │
│ 📊 Summary: 5 pre-flight checks, 2 build artifacts            │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

### Setup Dry-Run

```bash
/craft:dist:pypi setup --dry-run
```

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: PyPI Full Setup Wizard                            │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Setup Workflow (4 phases):                                  │
│                                                               │
│   Phase 1: Package Validation                                 │
│   - Check pyproject.toml structure                            │
│   - Verify version and metadata                               │
│   - Test build (uv build --no-publish)                        │
│   - Validate dependencies                                     │
│                                                               │
│   Phase 2: Workflow Generation                                │
│   - Create .github/workflows/pypi-release.yml                 │
│   - Configure trusted publishing settings                     │
│   - Set up environment: pypi                                  │
│                                                               │
│   Phase 3: PyPI Configuration Guide                           │
│   - Display PyPI trusted publishing instructions              │
│   - Show required settings and values                         │
│   - Provide verification checklist                            │
│                                                               │
│   Phase 4: First Release (optional)                           │
│   - Create git tag for current version                        │
│   - Generate GitHub release                                   │
│   - Trigger workflow for initial publish                      │
│                                                               │
│ ✓ Interactive Prompts:                                        │
│   - Confirm package name and version                          │
│   - Choose to include TestPyPI step                           │
│   - Decide whether to create first release now                │
│                                                               │
│ 📊 Summary: 4 setup phases, 3 user prompts                    │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

**Note**: Dry-run shows the complete setup/build/publish plan without creating files or publishing packages. Use this to understand what will happen before executing CRITICAL publishing operations.

---

## /craft:dist:pypi publish

Build and publish package to PyPI.

### Usage

```bash
/craft:dist:pypi publish                    # Publish current version
/craft:dist:pypi publish --version 1.2.3    # Publish specific version
```

### Requirements

- `pyproject.toml` with valid metadata
- PyPI account with trusted publishing configured
- Version must match tag for workflow publishing

### Manual Publishing (Development)

```bash
# Build package
uv build

# Publish to TestPyPI first
uv publish --repository testpypi

# Publish to PyPI
uv publish
```

---

## /craft:dist:pypi workflow

Generate GitHub Actions workflow for automated PyPI releases.

### Usage

```bash
/craft:dist:pypi workflow                   # Generate workflow
/craft:dist:pypi workflow --test           # Include TestPyPI step
```

### Output Files

```
.github/workflows/pypi-release.yml
```

### Workflow Template

```yaml
name: PyPI Release

on:
  release:
    types: [published]
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to publish (must match pyproject.toml)'
        required: true
        type: string

jobs:
  publish:
    name: Build and Publish to PyPI
    runs-on: ubuntu-latest
    environment: pypi  # Must match PyPI trusted publisher config
    permissions:
      id-token: write  # For trusted publishing
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync

      - name: Build package
        run: uv build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          skip-existing: true
```

### Features

- **Triggered by**: GitHub Release publish or manual dispatch
- **Build tool**: uv (fast, reliable)
- **Publishing**: Trusted publishing (no API tokens needed)
- **Safety**: `skip-existing: true` prevents accidental overwrites

---

## /craft:dist:pypi validate

Validate package structure and metadata before publishing.

### Usage

```bash
/craft:dist:pypi validate
```

### Checks Performed

| Check | Description |
|-------|-------------|
| `pyproject.toml` | Valid TOML, required fields present |
| `version` | Matches expected format (PEP 440) |
| `readme` | README file exists and is referenced |
| `license` | License file or classifier present |
| `classifiers` | Valid PyPI classifiers |
| `dependencies` | All dependencies are valid |
| `build` | Package builds successfully |

### Example Output

```
╭─────────────────────────────────────────────────────────────╮
│ PyPI Package Validation                                     │
├─────────────────────────────────────────────────────────────┤
│ ✓ pyproject.toml valid                                     │
│ ✓ Version: 0.6.1 (PEP 440 compliant)                       │
│ ✓ README.md found and referenced                           │
│ ✓ License: MIT                                             │
│ ✓ 4 classifiers valid                                      │
│ ✓ 4 dependencies valid                                     │
│ ✓ Build successful                                         │
├─────────────────────────────────────────────────────────────┤
│ ✅ Ready to publish                                         │
╰─────────────────────────────────────────────────────────────╯
```

---

## /craft:dist:pypi setup

Full setup wizard for new PyPI publishing.

### Usage

```bash
/craft:dist:pypi setup
```

### Steps Performed

1. **Validate Package**
   - Check pyproject.toml
   - Verify version and metadata
   - Test build

2. **Generate Workflow**
   - Create `.github/workflows/pypi-release.yml`
   - Configure for trusted publishing

3. **Guide Trusted Publishing Setup**
   - Instructions for PyPI settings
   - Environment configuration

4. **Create First Release** (optional)
   - Tag current version
   - Create GitHub release
   - Trigger workflow

### Trusted Publishing Setup

After running setup, configure PyPI:

1. Go to <https://pypi.org/manage/account/publishing/>
2. Add new pending publisher:
   - **Owner**: Your GitHub username/org
   - **Repository**: Your repo name
   - **Workflow**: `pypi-release.yml`
   - **Environment**: `pypi`

---

## /craft:dist:pypi check

Pre-flight checks before publishing.

### Usage

```bash
/craft:dist:pypi check
```

### Checks

| Check | Description |
|-------|-------------|
| **Version Sync** | pyproject.toml == __init__.py == git tag |
| **Clean Repo** | No uncommitted changes |
| **Tests Pass** | pytest returns 0 |
| **Build Works** | uv build succeeds |
| **Not Published** | Version not already on PyPI |

### Example Output

```
╭─────────────────────────────────────────────────────────────╮
│ PyPI Pre-Flight Checks                                      │
├─────────────────────────────────────────────────────────────┤
│ ✓ Version sync: 0.6.1 (pyproject.toml, __init__.py, tag)   │
│ ✓ Repository clean                                          │
│ ✓ Tests passing (135 passed)                                │
│ ✓ Build successful                                          │
│ ✓ Version 0.6.1 not on PyPI                                │
├─────────────────────────────────────────────────────────────┤
│ ✅ Ready to publish                                         │
│                                                             │
│ Next: Create GitHub release to trigger workflow             │
│   gh release create v0.6.1 --title "v0.6.1" --generate-notes│
╰─────────────────────────────────────────────────────────────╯
```

---

## When to Use

### Use `/craft:dist:pypi workflow` When

You want to automate PyPI publishing via GitHub Actions. This is the recommended approach for consistent, secure releases.

### Use `/craft:dist:pypi validate` When

Before any release, to catch issues early. Run this as part of your pre-release checklist.

### Use `/craft:dist:pypi check` When

You're about to create a release and want to ensure everything is in order.

### Use `/craft:dist:pypi setup` When

Setting up a new project for PyPI publishing for the first time.

---

## Related Commands

- `/craft:dist:homebrew` - Homebrew formula automation
- `/craft:dist:curl-install` - curl installer generation
- `/craft:check --for release` - Release readiness check
- `/craft:git:tag` - Create release tags

---

## Implementation Notes

### When `/craft:dist:pypi` is Invoked

1. **Detect subcommand** from first argument (default: `publish`)
2. **Read pyproject.toml** for package metadata
3. **Execute appropriate action**:
   - `publish`: Build and guide through publishing
   - `workflow`: Generate GitHub Actions workflow
   - `validate`: Run all validation checks
   - `setup`: Full wizard flow
   - `check`: Pre-flight checks

### Version Synchronization

Ensure these match before publishing:

- `pyproject.toml` → `version = "X.Y.Z"`
- `src/package/__init__.py` → `__version__ = "X.Y.Z"`
- Git tag → `vX.Y.Z`

### Trusted Publishing Benefits

- No API tokens to manage
- Automatic rotation
- Audit trail
- Works with branch protection
