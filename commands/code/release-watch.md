---
description: Track Claude Code + Desktop releases and identify plugin-relevant changes
arguments:
  - name: count
    description: Number of Code releases to check
    required: false
    default: 3
  - name: since
    description: Only show releases after this version (e.g., v1.0.25)
    required: false
  - name: format
    description: "Output format: terminal, json, markdown"
    required: false
    default: terminal
  - name: product
    description: "Product to track: all, code, desktop"
    required: false
    default: all
---

# Release Watch v2

Unified tool for monitoring Claude Code and Desktop releases for changes that affect the Craft plugin system.

## Usage

```bash
/craft:code:release-watch [options]
```

## What This Does

1. **Fetches Code releases** from `anthropics/claude-code` via the GitHub API
2. **Parses CHANGELOG.md** for structured categorization (Added, Fixed, etc.)
3. **Fetches Desktop releases** from Anthropic support docs
4. **Scans for plugin-relevant keywords** with word-boundary matching
5. **Categorizes findings** as NEW / DEPRECATED / BREAKING / FIXED
6. **Cross-references craft state** — hardcoded models, agent features, hook patterns
7. **Caches results** for 24 hours to avoid repeated API calls
8. **Proposes auto-fixes** for safe changes (model pattern updates)

## Requirements

- **gh CLI** — must be installed and authenticated (`gh auth login`)
- **curl** — for Desktop release fetching

## Examples

```bash
# Check Code + Desktop (default)
/craft:code:release-watch

# Code only (backward compatible with v1)
/craft:code:release-watch --product code

# Desktop only
/craft:code:release-watch --product desktop

# Check latest 5 Code releases
/craft:code:release-watch --count 5

# JSON v2 output
/craft:code:release-watch --format json

# Force refresh cached data
/craft:code:release-watch --refresh

# Generate auto-fix patch
/craft:code:release-watch --auto-fix
```

## Flags

| Flag | Description |
|------|-------------|
| `--count N` | Number of Code releases to check (default: 3) |
| `--since VERSION` | Only releases after this version |
| `--format FORMAT` | Output: terminal, json, markdown |
| `--product PRODUCT` | all (default), code, desktop |
| `--refresh` | Force refresh all cached data |
| `--no-cache` | Skip cache entirely |
| `--auto-fix` | Generate .patch for safe fixes |

## JSON v2 Schema

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
    "findings": { "new": [], "deprecated": [], "breaking": [], "fixed": [] }
  },
  "craft_state": { "hardcoded_models": [], "agent_features": {}, "hook_events": [] },
  "action_items": []
}
```

## Data Sources

| Source | Product | Caching | Auto-Fix |
|--------|---------|---------|----------|
| GitHub Releases API | Code | 24h | Yes |
| CHANGELOG.md | Code | 24h | Yes |
| Anthropic support docs | Desktop | 24h | Never |

## Integration

Works with:

- `/craft:code:release` — Release preparation
- `/craft:code:desktop-watch` — Redirects to `--product desktop`
- `/craft:code:deps-check` — Dependency auditing
