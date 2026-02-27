# Tutorial: Release Watch v2

Learn how to track Claude Code and Desktop releases to keep the Craft plugin current.

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth login`)
- `curl` available (for Desktop tracking)
- Internet access

## Step 1: Basic Usage

Run the unified release watch to check both Code and Desktop:

```bash
python3 scripts/release-watch.py
```

You'll see a box-drawn terminal report with:

- **Code releases** — latest 3 from `anthropics/claude-code`
- **Desktop releases** — latest 20 from Anthropic support docs
- **Craft state** — hardcoded model references in your codebase
- **Action items** — what needs attention

## Step 2: Filter by Product

Track only the product you care about:

```bash
# Code releases only (backward compatible with v1)
python3 scripts/release-watch.py --product code

# Desktop releases only
python3 scripts/release-watch.py --product desktop

# Both (default)
python3 scripts/release-watch.py --product all
```

## Step 3: JSON Output for Automation

Get structured output for scripts or CI:

```bash
python3 scripts/release-watch.py --format json | python3 -m json.tool
```

The JSON v2 schema includes:

```json
{
  "version": 2,
  "product": "all",
  "releases_checked": 3,
  "latest_version": "v2.1.59",
  "findings": { "new": [], "deprecated": [], "breaking": [], "fixed": [] },
  "desktop": {
    "entries_checked": 20,
    "latest_date": "February 25, 2026",
    "findings": { ... }
  },
  "craft_state": { "hardcoded_models": [], "agent_features": {}, "hook_events": [] },
  "action_items": []
}
```

## Step 4: Use the Cache

Results are cached for 24 hours at `~/.claude/release-watch-cache.json`.

```bash
# First run — fetches from APIs (slow)
python3 scripts/release-watch.py

# Second run — uses cache (instant)
python3 scripts/release-watch.py

# Force refresh all data
python3 scripts/release-watch.py --refresh

# Skip cache entirely (don't read or write)
python3 scripts/release-watch.py --no-cache
```

## Step 5: Check More Releases

By default, 3 Code releases are checked. Increase the count:

```bash
# Check latest 10 releases
python3 scripts/release-watch.py --count 10

# Only releases after a specific version
python3 scripts/release-watch.py --since v2.1.50
```

## Step 6: Auto-Fix Mode

Generate a patch file for safe fixes (model pattern updates):

```bash
python3 scripts/release-watch.py --auto-fix
```

If safe fixes are found, a `.patch` file is created:

```bash
# Review the patch
cat .claude/release-watch-fixes.patch

# Validate it
git apply --check .claude/release-watch-fixes.patch

# Apply it
git apply .claude/release-watch-fixes.patch
```

Items requiring manual review are listed separately — these need human judgment.

## Step 7: Markdown Reports

Generate a shareable markdown report:

```bash
python3 scripts/release-watch.py --format markdown > release-report.md
```

## Step 8: Use via Craft Commands

The release-watch integrates with Craft's command system:

```bash
# Via slash command
/craft:code:release-watch

# Desktop only
/craft:code:desktop-watch

# Full sync pipeline (audit + release watch + action plan)
/craft:code:sync-features
```

## Understanding Categories

Findings are classified into 4 categories:

| Category | Meaning | Action |
|----------|---------|--------|
| **NEW** | New features or capabilities | Evaluate for adoption |
| **DEPRECATED** | Features being removed | Plan migration |
| **BREAKING** | Changes that break existing behavior | Fix immediately |
| **FIXED** | Bug fixes in upstream | Verify no workarounds to remove |

## Understanding Data Sources

| Source | What It Provides | Caching |
|--------|-----------------|---------|
| GitHub Releases API | Code release notes, version tags | 24h |
| CHANGELOG.md | Structured categorization (Added/Fixed/etc.) | 24h |
| Anthropic Support Docs | Desktop release notes | 24h |

CHANGELOG categories take precedence over keyword scanning for more accurate classification.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `gh: command not found` | Install GitHub CLI: `brew install gh` |
| `gh auth` errors | Run `gh auth login` |
| No Desktop results | Check internet; `curl -sL` must follow redirects |
| Stale data | Use `--refresh` to force fresh fetch |
| Empty findings | Increase `--count` or remove `--since` filter |

## Next Steps

- Read the [architecture docs](../architecture/release-watch-v2.md) for internals
- Check the [refcard](../reference/REFCARD-RELEASE-WATCH.md) for quick reference
- See [cookbook recipes](../cookbook/release-watch-recipes.md) for common patterns
