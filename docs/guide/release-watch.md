# Release Watch — User Guide

Release Watch v2 is craft's unified tool for monitoring Claude Code and Desktop releases. It detects upstream changes that affect the plugin system and proposes fixes.

## Why Release Watch?

Claude Code and Desktop ship frequent updates. Some introduce new features craft should adopt, others deprecate patterns craft uses, and occasionally breaking changes require immediate fixes. Release Watch automates the detection so you don't have to manually read every release note.

## How It Works

```text
GitHub Releases ─┐
CHANGELOG.md ────┼── Cache (24h) ── Analyze ── Categorize ── Report
Anthropic Docs ──┘                                            │
                                                              ├── Terminal
                                                              ├── JSON v2
                                                              └── Markdown
```

1. **Fetches** Code releases from GitHub and Desktop releases from Anthropic docs
2. **Parses** CHANGELOG.md for structured categories (Added, Fixed, Breaking, etc.)
3. **Scans** release notes for plugin-relevant keywords using word-boundary regex
4. **Cross-references** findings against craft's current state (hardcoded models, agents, hooks)
5. **Caches** everything for 24 hours to avoid repeated API calls
6. **Reports** findings in your preferred format

## Getting Started

```bash
# Basic check — Code + Desktop, terminal output
python3 scripts/release-watch.py

# Via craft command
/craft:code:release-watch
```

## Product Filtering

The `--product` flag controls which releases to track:

| Value | What's Tracked |
|-------|---------------|
| `all` (default) | Code + Desktop |
| `code` | Code only (backward compatible with v1) |
| `desktop` | Desktop only |

```bash
python3 scripts/release-watch.py --product code      # Code only
python3 scripts/release-watch.py --product desktop   # Desktop only
```

## Output Formats

### Terminal (default)

Box-drawn report with sections for Code findings, Desktop findings, craft state, and action items. Best for interactive use.

### JSON

Machine-readable v2 schema. Ideal for scripting and CI integration.

```bash
python3 scripts/release-watch.py --format json | python3 -m json.tool
```

### Markdown

Shareable report with headers and tables. Good for documentation or team communication.

```bash
python3 scripts/release-watch.py --format markdown > report.md
```

## Caching

All API responses are cached at `~/.claude/release-watch-cache.json` with 24-hour TTL per source. This means:

- **First run:** fetches live data (~5 seconds)
- **Subsequent runs:** uses cache (~instant)
- **After 24h:** automatically fetches fresh data

### Cache Control

| Flag | Behavior |
|------|----------|
| (none) | Use cache if fresh, fetch if stale |
| `--refresh` | Treat all cached data as stale |
| `--no-cache` | Don't read or write cache at all |

### Stale Fallback

If a live fetch fails (network error, API down) and stale cached data exists, the stale data is used with a warning. This ensures you always get results even when offline.

## Finding Categories

Release notes are categorized by relevance to craft:

| Category | Source | What It Means |
|----------|--------|---------------|
| **NEW** | Added features, new capabilities | Evaluate for adoption in craft |
| **DEPRECATED** | Removed/deprecated features | Plan migration away from usage |
| **BREAKING** | Breaking changes, migrations | Fix immediately — may break craft |
| **FIXED** | Bug fixes, patches | Check if craft has workarounds to remove |

### How Categories Are Assigned

1. **CHANGELOG prefix** (highest priority): If CHANGELOG.md has structured entries like "Added: ...", "Fixed: ...", these map directly to categories
2. **Keyword scan** (fallback): Word-boundary regex matches keywords like "deprecated", "breaking", "new" in release note text

## Auto-Fix

The `--auto-fix` flag generates a `.patch` file for changes that can be safely automated:

```bash
python3 scripts/release-watch.py --auto-fix
```

### Safe vs Review

| Classification | What Happens | Example |
|---------------|-------------|---------|
| **Safe** | Generates a `.patch` file | New model pattern to add to MODEL_PATTERNS |
| **Review** | Listed for manual attention | Breaking API change, deprecated feature |

### Security Rules

- Auto-fix **never modifies files directly** — it only creates a `.patch` file
- Desktop release data is **never used for auto-fix** — only GitHub data is trusted
- You review and apply the patch manually: `git apply .claude/release-watch-fixes.patch`

## Integration with Craft

Release Watch integrates with the broader craft workflow:

| Command | What It Does |
|---------|-------------|
| `/craft:code:release-watch` | Full unified check |
| `/craft:code:desktop-watch` | Desktop only (alias) |
| `/craft:code:sync-features` | Audit + release watch + interactive action plan |
| `/craft:do "check for updates"` | Routes to release-watch automatically |

The **sync-features** skill chains command-audit with release-watch to give you a complete picture of craft's health and upstream changes in one pass.

## See Also

- [Architecture](../architecture/release-watch-v2.md) — Internal design and data flow
- [Refcard](../reference/REFCARD-RELEASE-WATCH.md) — Quick flag reference
- [Cookbook](../cookbook/release-watch-recipes.md) — Common recipes and patterns
- [Tutorial](../tutorials/TUTORIAL-release-watch-v2.md) — Step-by-step walkthrough
