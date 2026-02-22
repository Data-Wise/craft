# Homebrew Automation Guide

> **TL;DR** (30 seconds)
>
> - **What:** Complete Homebrew formula lifecycle — generate, audit, release, and dependency analysis
> - **Why:** Automate formula updates on every release with security-hardened workflows
> - **How:** `/craft:dist:homebrew setup` for first-time, then `/release` handles everything
> - **Config:** `.craft/homebrew.json` maps your project to its formula and tap

---

## Overview

The `/craft:dist:homebrew` command manages the full Homebrew formula lifecycle with 6 subcommands:

| Subcommand | Purpose | When to Use |
|------------|---------|-------------|
| `setup` | 4-step wizard (formula + workflow + token) | First time setting up Homebrew distribution |
| `formula` | Generate or update Ruby formula | Adding new formula or changing install method |
| `workflow` | Create hardened GitHub Actions automation | Setting up CI-based formula updates |
| `audit` | Run `brew audit` with auto-fix and `--build` | Before releasing, after formula changes |
| `deps` | Inter-formula and system dependency analysis | Understanding formula relationships |
| `update-resources` | Fix stale PyPI resource URLs | When `brew audit` reports URL mismatches |

---

## Configuration

### `.craft/homebrew.json`

Every project that distributes via Homebrew should have a `.craft/homebrew.json` in the project root:

```json
{
  "formula_name": "craft",
  "tap": "data-wise/tap",
  "source_type": "github"
}
```

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `formula_name` | Yes | Homebrew formula name (lowercase) | `craft`, `aiterm`, `scholar` |
| `tap` | Yes | Tap in `org/name` format | `data-wise/tap` |
| `source_type` | No | `github` (default) or `pypi` | `github` |

### Why This Matters

The `/release` skill (Step 10) uses a 3-priority lookup chain to find the formula name:

1. **`.craft/homebrew.json`** — most reliable, explicit config
2. **Git remote URL** — extracted from `origin`, works for most repos
3. **Directory basename** — fallback, least reliable (fails in worktrees)

Without this file, formula updates during release may target the wrong formula name — especially in git worktrees where `basename $PWD` returns the worktree name, not the project name.

---

## Setup Wizard

The setup wizard walks through 4 steps:

```bash
/craft:dist:homebrew setup
```

### Step 1: Project Detection

Detects project type from manifest files:

| Type | Detection File | Formula Pattern |
|------|---------------|-----------------|
| Python | `pyproject.toml` | `Language::Python::Virtualenv` |
| Node.js | `package.json` | npm install |
| Go | `go.mod` | go build |
| Rust | `Cargo.toml` | cargo install |
| Shell | `*.sh` scripts | bin.install |

### Step 2: Formula Generation

Generates a Ruby formula file with:

- Correct `url` and `sha256` for the latest release
- Dependency declarations from project manifest
- Install method matching project type
- Test block with basic smoke tests

### Step 3: Workflow Generation

Creates `.github/workflows/homebrew-release.yml` with security hardening (see [Workflow Hardening](#workflow-hardening) below).

### Step 4: Token Configuration

Guides setting up `HOMEBREW_TAP_GITHUB_TOKEN`:

```bash
# Create fine-grained token at github.com/settings/tokens
# Scope: Contents (read/write) on your tap repo

# Set as repository secret
gh secret set HOMEBREW_TAP_GITHUB_TOKEN
```

---

## Audit Subcommand

The `audit` subcommand replaces the old `validate` command with expanded capabilities:

```bash
# Standard audit
/craft:dist:homebrew audit

# Build from source (catches runtime issues)
/craft:dist:homebrew audit --build

# Strict + online checks
/craft:dist:homebrew audit --strict --online

# Report only (no auto-fix)
/craft:dist:homebrew audit --check-only
```

### `--build` Flag

Runs `brew install --build-from-source` to catch issues that static analysis misses:

- Missing build dependencies
- Compilation errors
- Runtime path issues
- Post-install script failures

### Auto-Fix Patterns

Common `brew audit` failures are fixed automatically:

| Pattern | Fix Applied |
|---------|------------|
| `Array#include?` deprecation | Replace with `.include?` |
| `assert_equal path` | Use `assert_path_exists` |
| `rescue StandardError` | Use bare `rescue` (Homebrew style) |
| Caveats after test block | Move `def caveats` before `test do` |
| Description starts with "A/An" | Remove article prefix |
| Description too long | Truncate to 80 characters |

---

## Deps Subcommand

Analyze dependencies across your tap's formulas:

```bash
# Inter-formula dependency graph
/craft:dist:homebrew deps

# System dependencies matrix
/craft:dist:homebrew deps --system

# Graphviz DOT output (for visualization)
/craft:dist:homebrew deps --dot | dot -Tpng -o deps.png
```

### Inter-Formula Graph

Shows which formulas in your tap depend on each other. Useful for understanding update order — if formula A depends on formula B, update B first.

### System Dependencies Matrix

Maps each formula to its system-level requirements:

```
Formula       | python | node | ruby | go | rust
------------- | ------ | ---- | ---- | -- | ----
aiterm        |   ✓    |      |      |    |
atlas         |        |  ✓   |      |    |
craft         |        |      |      |    |
flow-cli      |        |      |      |    |
himalaya-mcp  |   ✓    |      |      |    |
nexus-cli     |   ✓    |      |      |    |
scholar       |        |      |      |    |
```

---

## Workflow Hardening

The generated workflow includes security features to prevent common CI attack vectors:

### Env Indirection (Script Injection Prevention)

GitHub context values like `${{ github.event.inputs.version }}` in `run:` blocks are vulnerable to script injection. The workflow uses `env:` blocks instead:

```yaml
# UNSAFE - attacker-controlled input in run block
- run: echo "Version: ${{ github.event.inputs.version }}"

# SAFE - env indirection
- env:
    INPUT_VERSION: ${{ github.event.inputs.version }}
  run: echo "Version: $INPUT_VERSION"
```

### SHA256 Validation

```bash
# Uses sha256sum (not shasum) — standard on Ubuntu CI runners
SHA256=$(curl -sL --retry 3 --retry-delay 2 "$URL" | sha256sum | cut -d' ' -f1)

# Guard: validate 64 hex characters
if [ -z "$SHA256" ] || [ ${#SHA256} -ne 64 ]; then
    echo "ERROR: SHA256 calculation failed"
    exit 1
fi
```

### Ruby Syntax Check

After `sed` updates the formula, validate it hasn't been corrupted:

```bash
ruby -c "$FORMULA" || { echo "ERROR: Formula syntax error"; exit 1; }
```

### Security Features Summary

| Feature | Prevents |
|---------|----------|
| Env indirection | Script injection via PR titles or input parameters |
| `sha256sum` | Incorrect hash tool on Ubuntu runners |
| `--retry 3` | Transient download failures during release |
| 64-char SHA guard | Empty or truncated hash values |
| `ruby -c` check | Corrupted formula after sed replacement |

---

## Release Integration

The `/release` skill Step 10 automatically updates your Homebrew tap formula:

1. Looks up formula name via `.craft/homebrew.json` > git remote > basename
2. Locates the tap directory (local checkout or brew tap cache)
3. Downloads the release tarball and calculates SHA256
4. Updates `url` and `sha256` in the Ruby formula via `sed`
5. Validates with `ruby -c`
6. Commits and pushes to the tap repo

If no local tap is found, the CI workflow handles it automatically on release publish.

---

## Formula Description Consistency (Check 8)

The `pre-release-check.sh` script includes **Check 8: Homebrew formula desc consistency**, which validates that the `desc` field in your Homebrew formula stays in sync with the actual command counts in the project.

### What It Checks

The check extracts the command count from the formula's `desc` string (e.g., `"Full-stack developer toolkit for Claude Code with 107 commands"`) and compares it against the actual count detected by `validate-counts.sh`. If they differ, a warning is raised.

```bash
# Run Check 8 standalone
./scripts/pre-release-check.sh v2.26.0
# Look for: [8/8] Homebrew formula desc consistency
```

### Formula Lookup Chain

Check 8 searches for the formula file in this order:

1. Local Homebrew tap checkout (e.g., `$(brew --repository)/Library/Taps/<tap>/Formula/<name>.rb`)
2. Common worktree/clone locations for the tap repo
3. Falls back with a skip message if no formula is found locally

### Keeping Desc in Sync

When adding new commands to the plugin, update the formula description to reflect the new count:

```ruby
# In your formula .rb file
class Craft < Formula
  desc "Full-stack developer toolkit for Claude Code with 107 commands"
  #                                                      ^^^ update this
```

The release pipeline will warn you if this number drifts. To fix:

1. Run `./scripts/validate-counts.sh` to get the actual command count
2. Update the `desc` line in your formula file
3. Commit and push to the tap repo

### Why This Matters

Homebrew formula descriptions are user-facing -- they appear in `brew search`, `brew info`, and the Homebrew Formulae website. Stale command counts erode trust and confuse users who see a different number in the formula vs. the documentation site.

---

## Common Workflows

### New Project Setup

```bash
# 1. Create config
echo '{"formula_name": "myapp", "tap": "my-org/tap", "source_type": "github"}' > .craft/homebrew.json

# 2. Run setup wizard
/craft:dist:homebrew setup

# 3. Audit the generated formula
/craft:dist:homebrew audit --build

# 4. Create first release — workflow handles tap update
/release
```

### Pre-Release Validation

```bash
# Audit all formulas in tap
/craft:dist:homebrew audit --strict --online

# Check dependency graph for conflicts
/craft:dist:homebrew deps

# Build from source to catch runtime issues
/craft:dist:homebrew audit --build
```

### Fix Stale PyPI Resources

```bash
# Update resource URLs for Python formula
/craft:dist:homebrew update-resources aiterm

# Verify fix
/craft:dist:homebrew audit
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `brew audit` fails with "Description too long" | Keep description under 80 characters, no "A/An" prefix |
| SHA256 mismatch | Recalculate: `curl -sL <url> \| shasum -a 256 \| cut -d' ' -f1` |
| Wrong formula name in worktree | Add `.craft/homebrew.json` with explicit `formula_name` |
| `rescue StandardError` style warning | Use bare `rescue` (Homebrew convention) |
| Stale PyPI resource URLs | Run `/craft:dist:homebrew update-resources` |
| Workflow fails with script injection | Check for unquoted `${{ }}` in `run:` blocks — use `env:` instead |

---

## See Also

- [Homebrew Installation Guide](homebrew-installation.md) — End-user install instructions
- [Distribution Commands](../commands/dist.md) — All distribution commands
- [Release Pipeline Tutorial](../tutorials/TUTORIAL-release-pipeline.md) — End-to-end release workflow
- [Homebrew Quick Reference](../reference/REFCARD-HOMEBREW.md) — Cheat sheet
- [Homebrew Setup Tutorial](../tutorials/TUTORIAL-homebrew-setup.md) — Step-by-step first setup
