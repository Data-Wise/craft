# Marketplace Distribution Guide

⏱️ **15 minutes** • 🟡 Intermediate • ✓ Claude Code Plugin Distribution

> **TL;DR** (30 seconds)
>
> - **What:** Distribute your Claude Code plugin via the official marketplace
> - **Why:** One-command install for users on all platforms — no Homebrew, no manual cloning
> - **How:** Create `marketplace.json`, validate with `claude plugin validate .`, publish via git push
> - **Next:** Run `/craft:dist:marketplace validate` to check your listing

---

## Overview

The Claude Code Marketplace is the recommended distribution channel for plugins. Users install with a single command:

```bash
/plugin marketplace add Data-Wise/craft
```

Marketplace distribution is integrated into the Craft release pipeline — version bumps, validation, and publishing happen automatically during `/release`.

---

## Quick Start

### 1. Initialize marketplace.json

```bash
/craft:dist:marketplace init
```

This generates `.claude-plugin/marketplace.json` from your existing `plugin.json`, extracting name, version, description, and author fields.

### 2. Validate

```bash
/craft:dist:marketplace validate
```

Checks: file structure, `claude plugin validate .`, version consistency, owner fields, description length.

### 3. Test Locally

```bash
/craft:dist:marketplace test
```

Runs a full install → verify → uninstall cycle using local paths.

### 4. Publish

```bash
/craft:dist:marketplace publish
```

Validates, checks git state, confirms, and pushes to make the plugin available.

---

## marketplace.json Structure

The marketplace manifest lives at `.claude-plugin/marketplace.json`:

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "data-wise-craft",
  "owner": {
    "name": "Data-Wise",
    "email": "dt@stat-wise.com"
  },
  "metadata": {
    "description": "Full-stack developer toolkit for Claude Code",
    "version": "2.18.0"
  },
  "plugins": [
    {
      "name": "craft",
      "source": { "source": "github", "repo": "Data-Wise/craft" },
      "description": "Full-stack developer toolkit for Claude Code",
      "version": "2.18.0",
      "author": { "name": "Data-Wise", "email": "dt@stat-wise.com" },
      "homepage": "https://data-wise.github.io/craft/",
      "repository": "https://github.com/Data-Wise/craft",
      "license": "MIT",
      "category": "development",
      "tags": ["workflow", "automation", "git", "testing"]
    }
  ]
}
```

### Key Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Kebab-case marketplace identifier (e.g., `data-wise-craft`) |
| `owner.name` | Yes | Organization or author name |
| `metadata.version` | Yes | Must match `plugin.json` version |
| `plugins[].source` | Yes | GitHub source object: `{"source": "github", "repo": "Owner/Repo"}` |
| `plugins[].version` | Yes | Must match `plugin.json` version |
| `plugins[].category` | No | One of: development, productivity, data, etc. |
| `plugins[].tags` | No | Searchable keywords |

### Source Format

For root-level plugins (where `plugin.json` is at the repo root), use the GitHub source object format:

```json
"source": { "source": "github", "repo": "Data-Wise/craft" }
```

For mono-repos with multiple plugins in subdirectories, use relative paths:

```json
"source": "./plugins/my-plugin"
```

---

## Version Consistency

Three files must stay in sync:

| File | Field | Example |
|------|-------|---------|
| `.claude-plugin/plugin.json` | `version` | `"2.18.0"` |
| `.claude-plugin/marketplace.json` | `metadata.version` | `"2.18.0"` |
| `.claude-plugin/marketplace.json` | `plugins[0].version` | `"2.18.0"` |

The `/release` skill handles this automatically. The `pre-release-check.sh` script validates consistency.

---

## Release Pipeline Integration

When you run `/release`, marketplace distribution is handled automatically:

| Step | Action | Description |
|------|--------|-------------|
| **2c** | Marketplace Validation | Runs `claude plugin validate .` and checks version consistency |
| **3** | Version Bump | Updates `metadata.version` and `plugins[0].version` in marketplace.json |
| **8.5** | Tap Auto-Update | Updates Homebrew tap formula with new version and SHA256 |

### Pre-Release Checks

The `pre-release-check.sh` script includes marketplace validation:

```bash
./scripts/pre-release-check.sh 2.18.0
```

Check 5 of 6 validates:

- marketplace.json `metadata.version` matches target version
- marketplace.json `plugins[0].version` matches target version
- Gracefully skips if marketplace.json doesn't exist

---

## Distribution Strategy

| Audience | Channel | Command |
|----------|---------|---------|
| New users (all platforms) | Marketplace | `/plugin marketplace add Owner/Repo` |
| Power users (macOS) | Homebrew | `brew install tap/formula` |
| Contributors | Manual clone | `git clone ... && ln -sf ...` |

The recommended install hierarchy in documentation:

1. **Marketplace** (Recommended) — works everywhere, one command
2. **Homebrew** — macOS power users, auto-updates
3. **Manual** — contributors and developers

---

## Validation Checklist

Before publishing, ensure:

- [ ] `marketplace.json` is valid JSON
- [ ] `name` is kebab-case
- [ ] `owner.name` is populated
- [ ] `metadata.version` matches `plugin.json`
- [ ] `plugins[0].version` matches `plugin.json`
- [ ] `metadata.description` is under 100 characters
- [ ] `source` uses GitHub object format (not relative path)
- [ ] `claude plugin validate .` passes
- [ ] Working tree is clean (no uncommitted changes)

---

## Troubleshooting

### marketplace.json validation fails

**Problem:** `claude plugin validate .` reports errors

**Solution:** Check that `plugin.json` only contains recognized fields: `name`, `version`, `description`, `author`. Remove any extra fields.

### Version mismatch

**Problem:** Pre-release check reports version mismatch

**Solution:** Ensure all three version fields match. The `/release` skill handles this automatically, but if editing manually:

```bash
# Check current versions
jq '.version' .claude-plugin/plugin.json
jq '.metadata.version' .claude-plugin/marketplace.json
jq '.plugins[0].version' .claude-plugin/marketplace.json
```

### Source format rejected

**Problem:** Relative path `"source": "./"` not accepted

**Solution:** Use the GitHub source object format for root-level plugins:

```json
"source": { "source": "github", "repo": "Owner/Repo" }
```

---

## See Also

- [Distribution Commands](../commands/dist.md) — All 4 distribution commands
- [Homebrew Installation Guide](homebrew-installation.md) — Homebrew-specific distribution
- [Release Pipeline Reference](../reference/REFCARD-RELEASE.md) — Full release workflow
- [Release Workflow](../workflows/release-workflow.md) — Step-by-step release process
