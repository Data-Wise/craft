---
title: "Distribute Plugin via Homebrew"
description: "Set up Homebrew distribution for a Claude Code plugin"
category: "cookbook"
level: "intermediate"
time_estimate: "10 minutes"
related:
  - guide/homebrew-automation.md
  - guide/homebrew-installation.md
  - reference/REFCARD-HOMEBREW.md
---

# Distribute Plugin via Homebrew

Set up Homebrew distribution for a Claude Code plugin using the tap formula generator.

## Problem

You have a Claude Code plugin and want to distribute it via `brew install data-wise/tap/<name>` with automatic symlinks, marketplace registration, and post-install setup.

## Solution

### Step 1: Add to Generator Manifest (2 min)

Edit `generator/manifest.json` in the [homebrew-tap](https://github.com/Data-Wise/homebrew-tap) repo:

```json
{
  "my-plugin": {
    "type": "claude-plugin",
    "desc": "Description for brew info",
    "homepage": "https://github.com/Data-Wise/my-plugin",
    "source": "github",
    "repo": "Data-Wise/my-plugin",
    "version": "1.0.0",
    "sha256": "abc123...",
    "generated": true,
    "features": {
      "schema_cleanup": true,
      "marketplace": true
    },
    "libexec_paths": [".claude-plugin", "dist"],
    "test_paths": [
      {"path": ".claude-plugin/plugin.json", "type": "file"}
    ]
  }
}
```

### Step 2: Handle Nested Directories (if needed)

If your plugin has skills/agents in a subdirectory:

```json
"libexec_copy_map": {
  "my-plugin/skills": "skills",
  "my-plugin/agents": "agents"
}
```

This flattens `my-plugin/skills/` to `libexec/skills/` (what Claude Code expects).

### Step 3: Generate and Validate (2 min)

```bash
cd ~/projects/dev-tools/homebrew-tap
python3 generator/generate.py my-plugin --diff     # Preview
python3 generator/generate.py my-plugin --validate # Check syntax
python3 generator/generate.py my-plugin            # Write formula
```

### Step 4: Test Locally (5 min)

```bash
cp Formula/my-plugin.rb /opt/homebrew/Library/Taps/data-wise/homebrew-tap/Formula/
brew install --build-from-source data-wise/tap/my-plugin
brew test data-wise/tap/my-plugin
brew audit --strict data-wise/tap/my-plugin
```

### Step 5: Set Up Release Automation

Add `.craft/homebrew.json` to your plugin repo:

```json
{
  "formula_name": "my-plugin",
  "tap": "data-wise/tap",
  "source_type": "github"
}
```

Then `/release` will auto-update the formula on each release.

## Explanation

The generator produces a Ruby formula with:

- `libexec.install` for all plugin files
- `libexec_copy_map` for nested directory flattening
- 3-step `post_install`: (1) schema cleanup, (2) install script with 30s timeout, (3) registry sync
- Install/uninstall scripts assembled from composable blocks
- Test block verifying expected files exist

## Variations

### Plugins with npm build step

Add build steps to the manifest:

```json
"dependencies": {"runtime": ["node"]},
"build_steps": ["system \"npm\", \"install\"", "system \"npm\", \"run\", \"build\""]
```

### Head-only plugins (no releases)

```json
"head_only": true,
"head": "https://github.com/Data-Wise/my-plugin.git"
```

## Related

- [Homebrew Automation Guide](../../guide/homebrew-automation.md)
- [Homebrew Installation Guide](../../guide/homebrew-installation.md)
- [Homebrew Quick Reference](../../reference/REFCARD-HOMEBREW.md)
- [Setup Parallel Worktrees](setup-parallel-worktrees.md) -- for editing the tap in a worktree
