# Version Sync Setup Tutorial

## What is Version Sync?

Version sync ensures all version references in your project match. It catches version drift before it causes CI failures or deployment issues.

Three protection layers work together:

1. **PreToolUse hook** — Warns during editing when you're about to change a version file
2. **Git pre-commit hook** — Blocks commits that would introduce version mismatches
3. **/craft:check** — On-demand validation before PRs and releases

When these layers work together, version mismatches are caught early and prevent broken builds.

## Prerequisites

- Claude Code CLI installed
- A project with at least one version file (package.json, pyproject.toml, DESCRIPTION, Cargo.toml, etc.)
- `jq` installed (for JSON parsing, used by version sync scripts)
- Git initialized in your project

## Step 1: Install the Version Sync Script

The version sync script lives in your project at `scripts/version-sync.sh`. It uses convention-based discovery to identify your project type and find all version files automatically.

### Source of Truth Priority

The script checks files in this order and uses the first match as the authoritative version:

1. `.claude-plugin/plugin.json` (Claude Code plugin)
2. `package.json` (Node.js)
3. `pyproject.toml` (Python)
4. `DESCRIPTION` (R package)
5. `Cargo.toml` (Rust)

### Usage Examples

```bash
# Full check with detailed output
./scripts/version-sync.sh

# Exit code only (useful for CI scripts)
./scripts/version-sync.sh --quiet

# Show recommended fix commands without applying them
./scripts/version-sync.sh --fix
```

Each invocation checks all relevant files and reports mismatches with file paths and current values.

## Step 2: Set Up the PreToolUse Hook

The PreToolUse hook runs when you're about to edit a version file. It warns you of any existing mismatches so you know what you're fixing.

**Location:** `~/.claude/hooks/version-sync-hook.sh`

**Registration:** Add to `~/.claude/settings.json` under `PreToolUse` section with matcher `"Edit|Write"`

Example settings entry:

```json
{
  "PreToolUse": [
    {
      "matcher": "Edit|Write",
      "hook": "version-sync-hook.sh",
      "enabled": true
    }
  ]
}
```

This hook is **warning-only** — it displays mismatches but does not block your edit. This gives you the option to fix multiple files in one commit or to proceed if the mismatch is intentional.

## Step 3: Set Up the Pre-Commit Hook

The pre-commit hook is the enforcement layer. It blocks commits that would introduce version mismatches.

**Location:** `scripts/version-sync-precommit.sh`

**Installation:** Create a symlink from `.git/hooks/pre-commit`:

```bash
ln -s ../../scripts/version-sync-precommit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

This hook runs automatically when you run `git commit`. If versions don't match, the commit is blocked and the script shows:

- Which files have mismatches
- What the current values are
- A suggested `--fix` command to resolve the mismatch

## Step 4: Configure /craft:check

Version sync validation is automatically included in `/craft:check` for these scenarios:

- **`/craft:check --for commit`** — Validates before PR creation
- **`/craft:check --for pr`** — Validates before PR review
- **`/craft:check --for release`** — Validates before release (strictest mode)

No additional configuration is needed. The version sync check runs as part of the standard pre-flight validation.

## Testing Your Setup

Test each protection layer to ensure they're working:

### Test 1: PreToolUse Hook

1. Edit a version file with a wrong version number (e.g., change version to `99.0.0` in package.json but leave pyproject.toml at `1.0.0`)
2. The hook should warn about the mismatch when you open the file for editing
3. Save your changes

This confirms the hook is registered and watching.

### Test 2: Pre-Commit Hook

1. Stage the file with the intentional mismatch: `git add package.json`
2. Attempt to commit: `git commit -m "test: version mismatch"`
3. The pre-commit hook should block the commit and show the mismatch
4. Run the suggested `--fix` command to resolve

This confirms the pre-commit hook is installed and enforcing.

### Test 3: /craft:check

1. Create a version mismatch again (same as Test 1)
2. Stage and commit it (bypassing the hook with `--no-verify` for testing only)
3. Run `/craft:check --for commit`
4. The validation should report the mismatch and suggest the fix command

This confirms `/craft:check` is properly configured.

## Project Type Configurations

Version sync automatically detects your project type and checks the appropriate files:

### Node.js Projects

**Source of truth:** `package.json` → `version` field

**Files checked:**

- `package.json`
- `package-lock.json` (if present)
- Any `package.json` files in subdirectories

**Example:**

```json
{
  "name": "my-app",
  "version": "2.1.0"
}
```

### Python Projects

**Source of truth:** `pyproject.toml` → `project.version` field

**Files checked:**

- `pyproject.toml`
- `setup.py` (if present, old-style)
- `__init__.py` files containing version strings

**Example:**

```toml
[project]
name = "my-package"
version = "2.1.0"
```

### R Packages

**Source of truth:** `DESCRIPTION` → `Version` field

**Files checked:**

- `DESCRIPTION`
- Any `VERSION` files

**Example:**

```
Package: MyPackage
Version: 2.1.0
```

### Rust Projects

**Source of truth:** `Cargo.toml` → `package.version` field

**Files checked:**

- `Cargo.toml`
- `Cargo.lock` (if present)

**Example:**

```toml
[package]
name = "my-crate"
version = "2.1.0"
```

### Claude Code Plugins

**Source of truth:** `.claude-plugin/plugin.json` → `version` field

**Files checked:**

- `.claude-plugin/plugin.json`
- Associated `package.json` (if present)
- Associated `pyproject.toml` (if present)

**Example:**

```json
{
  "name": "my-plugin",
  "version": "2.1.0",
  "commands": []
}
```

## Troubleshooting

### jq is Not Installed

**Problem:** The version sync script fails with "jq: command not found"

**Solution:** Install jq using your package manager:

```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq

# CentOS/RHEL
sudo yum install jq
```

### Hook Is Not Registered

**Problem:** You edit a version file but don't see a warning

**Solution:** Verify the hook is registered in `~/.claude/settings.json`:

```json
{
  "PreToolUse": [
    {
      "matcher": "Edit|Write",
      "hook": "version-sync-hook.sh",
      "enabled": true
    }
  ]
}
```

Then restart Claude Code for the settings to take effect.

### Pre-Commit Hook Not Installed

**Problem:** You commit with version mismatches and the commit succeeds

**Solution:** Verify the symlink exists and is executable:

```bash
ls -l .git/hooks/pre-commit
# Should show: .git/hooks/pre-commit -> ../../scripts/version-sync-precommit.sh

chmod +x .git/hooks/pre-commit
```

### Version Intentionally Different (npm Dependencies)

**Problem:** Your `package.json` has a different version than `pyproject.toml`, and this is intentional (e.g., npm package versioning vs. Python package versioning)

**Solution:** Use the `--ignore-files` option in the version sync script:

```bash
./scripts/version-sync.sh --ignore-files package.json
```

Or update `.claude/version-sync-config.json` to exclude specific files:

```json
{
  "ignoredFiles": ["package.json"],
  "strictMode": false
}
```

### macOS grep Compatibility Issue

**Problem:** Scripts fail with "invalid option -- P" (macOS grep doesn't support PCRE by default)

**Solution:** The version sync script uses `-E` (extended regex) instead of `-P` for portability. If you see this error, verify you're using the bundled script and not a custom version.

To check the script:

```bash
grep -n "\-P" scripts/version-sync.sh
# Should return no results

grep -n "\-E" scripts/version-sync.sh
# Should show matches (this is correct)
```

### Mismatches Across Multiple Files

**Problem:** Multiple files have different versions and you're unsure what the correct version should be

**Solution:** Use the `--fix` option to see recommended commands:

```bash
./scripts/version-sync.sh --fix
```

The output will show which file is the source of truth and what commands to run to synchronize the others. Review these commands before running them.
