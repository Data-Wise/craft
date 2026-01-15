# Homebrew Installation Guide

⏱️ **5 minutes** • 🟢 Beginner • ✓ Complete setup

> **TL;DR** (30 seconds)
> - **What:** Install Craft via Homebrew for automatic updates
> - **Why:** Homebrew manages versions and dependencies
> - **How:** `brew install data-wise/tap/craft` → verify with `/craft:hub`
> - **After upgrades:** Run `claude plugin update craft@local-plugins`

---

## Quick Install

```bash
# Add the tap
brew tap data-wise/tap

# Install Craft
brew install craft
```

That's it! The post-install script automatically:
1. Creates symlinks to `~/.claude/plugins/craft`
2. Registers with the `local-plugins` marketplace
3. Enables the plugin in Claude Code settings
4. Syncs the plugin registry with `claude plugin update`

!!! note "Installing while Claude Code is running"
    If Claude Code is running during installation, auto-enable is skipped to avoid file conflicts. You'll see: "Claude Code is running - skipped auto-enable". Just run `claude plugin install craft@local-plugins` after installation.

---

## Verify Installation

```bash
# Check Homebrew installation
brew info craft

# Verify in Claude Code
/craft:hub
```

You should see all 89 commands listed.

---

## How It Works

### Plugin Chain

Homebrew uses a symlink chain to integrate with Claude Code:

```
~/.claude/local-marketplace/craft
    ↓ (symlink)
~/.claude/plugins/craft
    ↓ (symlink)
/opt/homebrew/opt/craft/libexec
    ↓ (actual files)
/opt/homebrew/Cellar/craft/<version>/libexec
```

### Claude Code Plugin System

Claude Code discovers plugins through:

| Component | Purpose |
|-----------|---------|
| **Marketplace** | `local-plugins` registered at `~/.claude/local-marketplace` |
| **Registry** | `~/.claude/plugins/installed_plugins.json` tracks versions |
| **Cache** | `~/.claude/plugins/cache/local-plugins/craft/<version>/` stores loaded files |

---

## Updating After Homebrew Upgrade

When you run `brew upgrade craft`, Homebrew updates the files and the post-install hook automatically syncs the plugin registry.

### Automatic Sync (v1.18.0+)

The formula's `post_install` hook runs:
```bash
claude plugin update craft@local-plugins
```

This happens automatically after each upgrade. Just restart Claude Code to load the new version.

### Manual Sync (if needed)

If automatic sync fails (Claude CLI not available, etc.):

```bash
claude plugin update craft@local-plugins
```

This command:
1. Reads from the symlink (→ new Homebrew version)
2. Copies files to Claude Code cache
3. Updates the registry with new version

### Verify Update

```bash
# Check registry version
cat ~/.claude/plugins/installed_plugins.json | jq '.plugins["craft@local-plugins"][0].version'

# Should match Homebrew version
brew info craft | head -1
```

---

## Troubleshooting

### Auto-Enable Skipped

**Symptom:** Message says "Claude Code is running - skipped auto-enable"

**Cause:** The installer detected Claude Code has `settings.json` open and skipped modification to avoid conflicts.

**Fix:**
```bash
claude plugin install craft@local-plugins
```

This is expected behavior when installing while Claude Code is running.

---

### Installation Hangs (Pre-v1.18.0 only)

**Symptom:** `brew install` or `brew upgrade` hangs during post-install

**Cause:** Older formula versions attempted to modify `settings.json` without checking for Claude.

**Fix (if stuck now):**
```bash
# Find and kill the stuck process
ps aux | grep craft-install
kill <PID>

# Then manually enable
claude plugin install craft@local-plugins
```

**Prevention:** Upgrade to latest formula: `brew update && brew reinstall data-wise/tap/craft`

---

### Plugin Not Loading

**Symptom:** `/craft:hub` not recognized after install

**Fix:**
```bash
# Re-run install script
craft-install

# Or manually create symlink
ln -sf /opt/homebrew/opt/craft/libexec ~/.claude/plugins/craft

# Update registry
claude plugin update craft@local-plugins

# Restart Claude Code
```

### Version Mismatch

**Symptom:** Registry shows old version after `brew upgrade`

**Fix:**
```bash
claude plugin update craft@local-plugins
```

### Symlink Permission Denied

**Symptom:** `ln: failed to create symbolic link`

**Fix:**
```bash
# Remove existing directory/symlink
rm -rf ~/.claude/plugins/craft

# Create fresh symlink
ln -s /opt/homebrew/opt/craft/libexec ~/.claude/plugins/craft
```

### Cache Cleanup

**Symptom:** Multiple old versions accumulating

**Fix:**
```bash
# List cached versions
ls ~/.claude/plugins/cache/local-plugins/craft/

# Remove old versions (keep current)
rm -rf ~/.claude/plugins/cache/local-plugins/craft/1.16.0
rm -rf ~/.claude/plugins/cache/local-plugins/craft/1.6.0-dev
```

---

## Available Commands

After installation, these Homebrew-provided commands are available:

| Command | Description |
|---------|-------------|
| `craft-install` | Create symlinks and register with Claude Code |
| `craft-uninstall` | Remove symlinks |

---

## Uninstallation

```bash
# Remove via Homebrew
brew uninstall craft

# The post-uninstall script automatically removes symlinks
```

To manually clean up:

```bash
# Remove symlinks
rm -f ~/.claude/plugins/craft
rm -f ~/.claude/local-marketplace/craft

# Clear cache
rm -rf ~/.claude/plugins/cache/local-plugins/craft
```

---

## Other Homebrew Plugins

The same pattern applies to other Data-Wise plugins. All use Claude detection to avoid conflicts during installation.

| Plugin | Install Command | Commands |
|--------|-----------------|----------|
| **craft** | `brew install data-wise/tap/craft` | 89 commands |
| **rforge** | `brew install data-wise/tap/rforge` | 15 commands |
| **scholar** | `brew install data-wise/tap/scholar` | 21 commands |

All plugins will show "Claude Code is running - skipped auto-enable" if installed while Claude is running. Just run the enable command shown.

Update all after Homebrew upgrade:
```bash
claude plugin update craft@local-plugins
claude plugin update rforge@local-plugins
claude plugin update scholar@local-plugins
```

---

## See Also

- **Quick Start:** [Getting Started](getting-started.md)
- **Configuration:** [Configuration](../reference/configuration.md)
- **Commands:** [Commands Overview](../commands/overview.md)
