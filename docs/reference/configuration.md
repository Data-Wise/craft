# Configuration

Craft plugin configuration and customization.

## Plugin Location

```text
~/.claude/plugins/craft/
```

## Configuration Files

| File | Purpose | Created By |
|------|---------|-----------|
| `.craft/site-design.yaml` | Site design preferences | `/craft:site:create` |
| `.craft/homebrew.json` | Homebrew formula name and tap | Manual |
| `.claude-plugin/plugin.json` | Plugin manifest (version, name) | Plugin init |
| `.claude-plugin/marketplace.json` | Marketplace distribution metadata | `/craft:dist:marketplace init` |
| `.claude-plugin/config.json` | Plugin custom config (budget, etc.) | Manual |
| `.claude/release-config.json` | Release pipeline + version sync config | Manual |
| `package.json` | Version source (Node projects) | `npm init` |

### .craft/site-design.yaml

Created by `/craft:site:create`, stores site design preferences:

```yaml
preset: "data-wise"

branding:
  name: "Your Project"
  tagline: "Description"
  logo: null

colors:
  primary: "#1a73e8"
  accent: "#ff6b35"
  scheme: "auto"

navigation:
  style: "tabs"
  max_depth: 3

features:
  search: true
  dark_mode: true
  code_copy: true
  edit_on_github: true
```

### .craft/homebrew.json

Maps project to Homebrew formula and tap:

```json
{
  "formula_name": "craft",
  "tap": "data-wise/tap",
  "source_type": "github"
}
```

### .claude/release-config.json

Controls version sync and CI monitoring behavior:

```json
{
  "version_sync": {
    "enabled": true,
    "source_of_truth": "auto"
  },
  "ci_timeout": 600,
  "ci_max_retries": 3,
  "ci_poll_interval": 30
}
```

See [Version Sync Architecture](../architecture/version-sync.md) for full schema.

## Mode Configuration

Execution modes can be customized per project.

**Default mode settings:**

| Mode | Timeout | Use Case |
|------|---------|----------|
| default | 10s | Quick checks |
| debug | 120s | Verbose output |
| optimize | 180s | Parallel execution |
| release | 300s | Comprehensive audit |

## Version Sync

Version is managed across 13 files atomically using `bump-version.sh`:

```bash
./scripts/bump-version.sh 2.27.0        # Full bump
./scripts/bump-version.sh --verify       # Check for drift
./scripts/bump-version.sh --counts-only  # Sync counts only
```

See [Bump Version Reference](REFCARD-BUMP-VERSION.md) for details.

## ADHD Score Thresholds

Website enhancement scoring:

| Grade | Score Range | Description |
|-------|-------------|-------------|
| A | 90-100 | Excellent ADHD-friendliness |
| B | 80-89 | Good |
| C | 70-79 | Acceptable |
| D | 60-69 | Needs improvement |
| F | <60 | Poor |

**Target:** Achieve C (70+) minimum for production docs.

## Environment Variables

Currently, craft uses Claude Code's built-in configuration. No additional environment variables required.

## Next Steps

- [Presets Reference](presets.md) - Design preset details
- [Quick Reference](../REFCARD.md) - Command cheat sheet
- [Bump Version Reference](REFCARD-BUMP-VERSION.md) - Version management
- [Version Sync Architecture](../architecture/version-sync.md) - Three-layer drift prevention
