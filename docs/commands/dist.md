# Distribution Commands

⏱️ **10 minutes** • 🟡 Intermediate • ✓ Multi-platform packaging

> **TL;DR** (30 seconds)
>
> - **What:** 4 commands for packaging and distributing your project (Marketplace, Homebrew, PyPI, curl installer)
> - **Why:** Automate release workflows and make your project easy to install across platforms
> - **How:** Use `/craft:dist:marketplace` for Claude Code plugins, `/craft:dist:homebrew setup` for macOS
> - **Next:** Try `/craft:dist:marketplace validate` or `/craft:dist:homebrew audit` to validate your distribution

Craft's distribution commands automate packaging and distribution across Claude Code Marketplace, Homebrew, PyPI, and curl installers.

---

## Commands Overview

| Command | Purpose | Platforms |
|---------|---------|-----------|
| `/craft:dist:marketplace` | Claude Code marketplace distribution | All platforms |
| `/craft:dist:homebrew` | Homebrew formula automation | macOS, Linux |
| `/craft:dist:pypi` | PyPI package publishing | Python (all platforms) |
| `/craft:dist:curl-install` | Curl-based installer script | All platforms |

---

## `/craft:dist:marketplace` - Marketplace Distribution

Manage Claude Code marketplace listings — generate, validate, test, and publish.

### Quick Start

```bash
# Validate marketplace config (default)
/craft:dist:marketplace

# Initialize marketplace.json for first time
/craft:dist:marketplace init

# Test local install/uninstall cycle
/craft:dist:marketplace test

# Publish to marketplace
/craft:dist:marketplace publish
```

### Subcommands

| Subcommand | Purpose |
|------------|---------|
| `init` | Generate `marketplace.json` from `plugin.json` |
| `validate` | Validate marketplace config and version consistency (default) |
| `test` | Local install/uninstall cycle verification |
| `publish` | Push to GitHub for marketplace availability |

### Init: Generate marketplace.json

Creates `.claude-plugin/marketplace.json` from existing `plugin.json`:

```bash
/craft:dist:marketplace init
```

**Output:**

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:dist:marketplace init                                │
├─────────────────────────────────────────────────────────────┤
│ Plugin: craft v2.18.0                                       │
│ Author: Data-Wise <dt@stat-wise.com>                        │
│ Marketplace: data-wise-craft                                │
├─────────────────────────────────────────────────────────────┤
│ Created: .claude-plugin/marketplace.json                    │
│ Validated: claude plugin validate . ... PASSED              │
├─────────────────────────────────────────────────────────────┤
│ Install with:                                               │
│   /plugin marketplace add Data-Wise/craft                   │
└─────────────────────────────────────────────────────────────┘
```

### Validate: Check Configuration

Validates marketplace.json structure and version consistency:

```bash
/craft:dist:marketplace validate
```

**Checks performed:**

| Check | Severity | Description |
|-------|----------|-------------|
| marketplace.json exists | Error | File must be present |
| `claude plugin validate .` | Error/Warning | Plugin structure validation |
| Version consistency | Error | marketplace.json versions must match plugin.json |
| Owner fields | Warning | name and email should be populated |
| Description length | Warning | Should be concise (< 100 chars) |

### Test: Local Install Cycle

Runs a full install/uninstall cycle to verify the plugin works:

```bash
/craft:dist:marketplace test
```

Steps: validate → install locally → verify plugin visible → verify commands → uninstall → verify cleanup.

### Publish: Push to Marketplace

Push to GitHub to make the plugin available via marketplace:

```bash
/craft:dist:marketplace publish
```

Checks: validate → clean working tree → correct branch → confirm → push → show install instructions.

### Release Pipeline Integration

The `/release` skill handles marketplace automatically:

- **Step 2c:** Runs `claude plugin validate .` if marketplace.json exists
- **Step 3:** Updates `metadata.version` and `plugins[0].version` in marketplace.json
- **Step 8.5:** Updates Homebrew tap formula with new version and SHA256

---

## `/craft:dist:homebrew` - Homebrew Automation

Complete Homebrew formula management with automated GitHub Actions workflows, security-hardened release automation, and dependency analysis.

### Quick Start

```bash
# Full setup wizard (recommended)
/craft:dist:homebrew setup

# Generate formula only
/craft:dist:homebrew formula

# Generate GitHub Actions workflow
/craft:dist:homebrew workflow

# Audit formula (replaces old validate)
/craft:dist:homebrew audit

# Analyze formula dependencies
/craft:dist:homebrew deps
```

### Subcommands

| Subcommand | Purpose |
|------------|---------|
| `formula` | Generate or update Homebrew formula |
| `workflow` | Create security-hardened GitHub Actions release automation |
| `audit` | Run `brew audit` validation with auto-fix and `--build` support |
| `setup` | Full wizard (formula + workflow + token in 4 steps) |
| `update-resources` | Fix stale PyPI resource URLs |
| `deps` | Analyze inter-formula and system dependency graphs |

### Configuration: `.craft/homebrew.json`

Each project can define its Homebrew config in `.craft/homebrew.json`:

```json
{
  "formula_name": "craft",
  "tap": "data-wise/tap",
  "source_type": "github"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `formula_name` | Yes | Name of the Homebrew formula (e.g., `craft`, `aiterm`) |
| `tap` | Yes | Tap in `org/name` format (e.g., `data-wise/tap`) |
| `source_type` | No | `github` (default) or `pypi` |

This config is used by the `/release` skill (Step 8.5) for formula name lookup, avoiding reliance on `basename $PWD`.

### Example: Full Setup

```bash
/craft:dist:homebrew setup
```

**Output:**

```
╔═══════════════════════════════════════════════════════════╗
║       HOMEBREW AUTOMATION SETUP WIZARD                     ║
╠═══════════════════════════════════════════════════════════╣
║  Step 1: Detect project type                              ║
║    ✓ Detected: Python (pyproject.toml)                    ║
║    ✓ Name: aiterm | Version: 0.6.0                       ║
║                                                           ║
║  Step 2: Generate formula                                 ║
║    ✓ Created: Formula/aiterm.rb                          ║
║    ✓ Validated: brew audit passed                        ║
║                                                           ║
║  Step 3: Generate workflow                                ║
║    ✓ Created: .github/workflows/homebrew-release.yml     ║
║    ✓ Security: env indirection, sha256sum, --retry       ║
║                                                           ║
║  Step 4: Token configuration                              ║
║    ⚠ HOMEBREW_TAP_GITHUB_TOKEN not found                 ║
║    Run: gh secret set HOMEBREW_TAP_GITHUB_TOKEN          ║
╚═══════════════════════════════════════════════════════════╝
```

### Supported Project Types

| Type | Detection | Formula Pattern |
|------|-----------|-----------------|
| Python | `pyproject.toml` | `Language::Python::Virtualenv` |
| Node.js | `package.json` | npm install |
| Go | `go.mod` | go build |
| Rust | `Cargo.toml` | cargo install |
| Shell | `*.sh` scripts | bin.install |

### Audit Subcommand

Runs `brew audit` validation with auto-fix patterns and optional build-from-source testing:

```bash
# Standard audit
/craft:dist:homebrew audit

# Build from source (catches runtime issues)
/craft:dist:homebrew audit --build

# Strict + online checks
/craft:dist:homebrew audit --strict --online

# Report issues without fixing
/craft:dist:homebrew audit --check-only
```

**Auto-Fix Patterns** (applied automatically):

| Pattern | Fix |
|---------|-----|
| `Array#include?` deprecation | Replace with `.include?` |
| `assert_equal path` | Use `assert_path_exists` |
| `rescue StandardError` | Use bare `rescue` |
| Caveats after test block | Move caveats before test |
| Description too long | Truncate to 80 chars |

### Deps Subcommand

Analyze inter-formula and system dependencies:

```bash
# Show inter-formula dependency graph
/craft:dist:homebrew deps

# Show system dependencies matrix
/craft:dist:homebrew deps --system

# Generate Graphviz DOT output
/craft:dist:homebrew deps --dot
```

**Inter-Formula Graph** shows which formulas depend on others within your tap. **System Dependencies Matrix** maps each formula to its system-level requirements (python, node, ruby, etc.).

### Automated Workflow (Hardened)

Creates `.github/workflows/homebrew-release.yml` with security hardening:

| Feature | Description |
|---------|-------------|
| **Env indirection** | GitHub context values go through `env:` block (prevents script injection) |
| **`sha256sum`** | Uses `sha256sum` (not `shasum -a 256`) for Ubuntu CI runners |
| **`--retry`** | `curl --retry 3 --retry-delay 2` for resilient downloads |
| **SHA guard** | Validates SHA256 is exactly 64 hex characters before proceeding |
| **Ruby syntax check** | `ruby -c` validates formula after sed updates |

- **Triggers:** On GitHub release published or manual dispatch
- **Auto-merge:** Optional PR auto-merge
- **Multi-source:** Supports GitHub releases or PyPI packages
- **Token-based:** Uses fine-grained GitHub token

### Update Stale Resources (Python)

PyPI occasionally changes URLs for packages. Fix automatically:

```bash
/craft:dist:homebrew update-resources aiterm
```

**Output:**

```
Checking 5 resources...
  ✓ click: 8.0.0 → 8.1.7 (URL updated)
  ✓ rich: 13.0.0 → 13.7.0 (URL updated)
  - typer: 0.9.0 (no changes)

Updated 2 resources in Formula/aiterm.rb
Running brew audit... ✓ passed
```

---

## `/craft:dist:pypi` - PyPI Publishing

Publish Python packages to PyPI with automated workflows and trusted publishing.

### Quick Start

```bash
# Full PyPI setup
/craft:dist:pypi setup

# Publish current version
/craft:dist:pypi publish

# Check PyPI status
/craft:dist:pypi status

# Generate GitHub Actions workflow
/craft:dist:pypi workflow
```

### Subcommands

| Subcommand | Purpose |
|------------|---------|
| `setup` | Configure PyPI publishing (pyproject.toml, workflows) |
| `publish` | Build and upload to PyPI |
| `status` | Check package status on PyPI |
| `workflow` | Generate GitHub Actions for trusted publishing |
| `validate` | Validate package metadata |

### Trusted Publishing (Recommended)

Uses OpenID Connect (OIDC) for secure, token-free publishing:

**Setup:**

1. **Add pending publisher on PyPI:**
   - Go to: <https://pypi.org/manage/account/publishing/>
   - Project: `your-package`
   - Owner: `your-org`
   - Repository: `your-repo`
   - Workflow: `publish.yml`
   - Environment: `pypi`

2. **Generate workflow:**

   ```bash
   /craft:dist:pypi workflow
   ```

3. **Create release:**

   ```bash
   gh release create v1.0.0
   ```

### Example Workflow

Creates `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi  # Required for trusted publishing
    permissions:
      id-token: write  # Required for OIDC
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - name: Build package
        run: |
          python -m pip install build
          python -m build
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

### Validation

```bash
/craft:dist:pypi validate
```

**Checks:**

- `pyproject.toml` completeness
- Version format (SemVer)
- README presence
- License file
- Classifiers validity
- Build configuration

---

## `/craft:dist:curl-install` - Universal Installer

Create a curl-based installer script for easy one-line installation.

### Quick Start

```bash
# Generate installer
/craft:dist:curl-install

# Generate with custom URL
/craft:dist:curl-install --repo user/repo

# Add to README
/craft:dist:curl-install --add-readme
```

### What It Creates

Generates `install.sh`:

```bash
#!/bin/bash
# Quick installer for myapp

set -e

# Detect platform
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS - use Homebrew
  brew install user/tap/myapp
elif command -v pip &> /dev/null; then
  # Python available - use PyPI
  pip install myapp
else
  # Fallback - download binary
  curl -sSL https://github.com/user/repo/releases/latest/download/myapp > /usr/local/bin/myapp
  chmod +x /usr/local/bin/myapp
fi
```

### Features

- **Platform detection:** macOS (Homebrew) / Linux (PyPI or binary)
- **Fallback chain:** Homebrew → PyPI → Direct download
- **Error handling:** Checks for dependencies
- **Version pinning:** Optional specific version

### Usage in README

```bash
# Quick install (auto-detects best method)
curl -fsSL https://raw.githubusercontent.com/user/repo/main/install.sh | bash

# Install specific version
curl -fsSL https://raw.githubusercontent.com/user/repo/main/install.sh | bash -s -- v1.0.0
```

### Options

```bash
/craft:dist:curl-install --methods homebrew,pypi    # Specify methods
/craft:dist:curl-install --add-readme               # Append to README
/craft:dist:curl-install --verify-sig               # Add GPG signature verification
```

---

## Common Workflows

### Workflow 1: New Project Distribution Setup

```bash
# Step 1: Set up all distribution channels
/craft:dist:homebrew setup
/craft:dist:pypi setup
/craft:dist:curl-install --add-readme

# Step 2: Validate everything
/craft:dist:homebrew audit
/craft:dist:pypi validate

# Step 3: Create first release
git tag -a v1.0.0 -m "Initial release"
git push --tags

# Step 4: Verify automation
gh run list --workflow homebrew-release
gh run list --workflow publish
```

### Workflow 2: Update Existing Distribution

```bash
# Update version in code
# Commit changes

# Create new release
gh release create v1.1.0 --generate-notes

# Monitor automation
gh run watch
```

### Workflow 3: Fix Stale Homebrew Resources

```bash
# Fix PyPI resource URLs
/craft:dist:homebrew update-resources myapp

# Validate
/craft:dist:homebrew audit --strict --online

# Analyze dependencies
/craft:dist:homebrew deps --system

# Commit and push to tap
cd ~/homebrew-tap
git add Formula/myapp.rb
git commit -m "fix(myapp): update PyPI resource URLs"
git push
```

---

## Integration with Other Commands

| Command | Use Case |
|---------|----------|
| `/craft:check --for release` | Pre-release validation before distribution |
| `/craft:git:recap` | Create version tags for releases |
| `/craft:docs:changelog` | Generate changelog for release notes |
| `/craft:ci:generate` | Full CI/CD setup including distribution |
| `/craft:code:release` | Complete release checklist |

---

## Skills Used

- `distribution-strategist` - Multi-channel distribution planning
- `homebrew-formula-expert` - Homebrew formula syntax
- `homebrew-workflow-expert` - GitHub Actions automation
- `homebrew-setup-wizard` - Setup wizard implementation

---

## Tips

!!! tip "Start with Setup Wizards"
    Use `/craft:dist:homebrew setup` and `/craft:dist:pypi setup` for guided configuration.

!!! success "Use Trusted Publishing"
    PyPI's trusted publishing (OIDC) is more secure than API tokens - no secrets to manage!

!!! tip "Test Locally First"
    Test Homebrew formulas before release: `brew install --build-from-source ./Formula/myapp.rb`

!!! warning "Token Rotation"
    Set a 90-day reminder to rotate Homebrew tap tokens.

---

## Troubleshooting

### Homebrew Formula Issues

**Problem:** `brew audit` fails with "Description too long"
**Solution:** Keep description under 80 characters, no "A/An" prefix

**Problem:** SHA256 mismatch
**Solution:** Recalculate: `curl -sL <url> | shasum -a 256 | cut -d' ' -f1`

**Problem:** Stale PyPI resource URLs
**Solution:** Run `/craft:dist:homebrew update-resources`

### PyPI Publishing Issues

**Problem:** `invalid-publisher` error
**Solution:** Verify workflow name matches exactly in PyPI config

**Problem:** Missing `environment: pypi`
**Solution:** Add environment to workflow job

**Problem:** Permission denied
**Solution:** Ensure `id-token: write` permission in workflow

### Curl Installer Issues

**Problem:** Installer fails on Linux
**Solution:** Add Python/binary fallback for non-macOS platforms

---

## Learn More

- [Architecture Commands](arch.md) - System design for distribution
- [CI Commands](git.md#ci-commands-3) - Automated testing before release
- [Visual Workflows](../workflows/index.md) - See distribution in action
