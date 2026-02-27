# REFCARD: Release Watch v2

Quick reference for `scripts/release-watch.py` — unified Claude Code + Desktop release tracking.

## CLI Flags

```text
python3 scripts/release-watch.py [FLAGS]

--count N, -c N      Code releases to check (default: 3)
--since VER, -s VER  Only after this version (e.g., v2.1.50)
--format FMT, -f FMT Output: terminal | json | markdown
--product P, -p P    Track: all | code | desktop
--refresh            Force refresh all cached data
--no-cache           Skip cache entirely
--auto-fix           Generate .patch for safe fixes
```

## Common Patterns

```bash
# Quick check (uses cache)
python3 scripts/release-watch.py

# Code only, JSON
python3 scripts/release-watch.py -p code -f json

# Desktop only
python3 scripts/release-watch.py -p desktop

# Deep scan (10 releases, fresh)
python3 scripts/release-watch.py -c 10 --refresh

# Since a version
python3 scripts/release-watch.py --since v2.1.50

# Auto-fix + review
python3 scripts/release-watch.py --auto-fix

# Markdown report
python3 scripts/release-watch.py -f markdown > report.md
```

## Craft Commands

```bash
/craft:code:release-watch              # Full unified check
/craft:code:desktop-watch              # Desktop only (alias)
/craft:code:sync-features              # Audit + release watch + action plan
```

## Finding Categories

| Category | Icon | Meaning |
|----------|------|---------|
| NEW | | New features/capabilities to adopt |
| DEPRECATED | | Features being removed — plan migration |
| BREAKING | | Breaks existing behavior — fix now |
| FIXED | | Bug fixes — remove workarounds |

## Data Sources

| Source | Product | Cache Key | TTL |
|--------|---------|-----------|-----|
| GitHub Releases API | Code | `releases` | 24h |
| CHANGELOG.md | Code | `changelog` | 24h |
| Anthropic Support Docs | Desktop | `desktop_releases` | 24h |

## Cache

```text
Location: ~/.claude/release-watch-cache.json
TTL:      24 hours (per source, independent)
Fallback: Stale data used when fetch fails
Perms:    0o700 dir, 0o600 file
```

## JSON v2 Schema (top-level keys)

```text
version            2
product            "all" | "code" | "desktop"
releases_checked   int
latest_version     "vX.Y.Z"
findings           {new, deprecated, breaking, fixed}
desktop            {entries_checked, latest_date, findings}
craft_state        {hardcoded_models, agent_features, hook_events}
action_items       [{type, message}]
```

## Auto-Fix Rules

| Item Type | Classification | Action |
|-----------|---------------|--------|
| New model pattern (GitHub) | Safe | Generates `.patch` |
| Breaking change | Review | Listed for manual fix |
| Deprecated feature | Review | Listed for manual fix |
| Desktop findings | Excluded | Never in patch |

## Security

- Auto-fix generates `.patch` only — never modifies files directly
- Desktop data never used for auto-fix (source-tagged boundary)
- All subprocess calls use list-form (no shell injection)
- Timeouts: 30s GitHub, 10s Desktop

## Keyword Matching

Uses `\b` word-boundary regex:

- `"new feature"` matches keyword `new`
- `"renewable"` does NOT match keyword `new`
- CHANGELOG prefix categories override keyword scan
