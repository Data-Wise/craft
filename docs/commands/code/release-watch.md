# /craft:code:release-watch

> **Track Claude Code releases and identify plugin-relevant changes**

---

## Synopsis

```bash
/craft:code:release-watch [--count N] [--since vX.Y.Z] [--format fmt]
```

**Quick examples:**

```bash
# Check latest 3 releases (default)
/craft:code:release-watch

# Check latest 5 releases
/craft:code:release-watch --count 5

# Only releases after a specific version
/craft:code:release-watch --since v1.0.25

# JSON output for CI
/craft:code:release-watch --format json
```

---

## Description

Fetches releases from `anthropics/claude-code` via the GitHub API, scans release notes for plugin-relevant keywords, categorizes findings, cross-references craft state, and generates action items.

---

## Requirements

- **gh CLI** must be installed and authenticated (`gh auth login`)

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--count` | Number of releases to check | 3 |
| `--since` | Only show releases after this version | - |
| `--format` | Output format (terminal\|json\|markdown) | terminal |

---

## Keyword Categories

| Category | Keywords Scanned |
|----------|-----------------|
| Plugin system | `plugin`, `skill`, `command`, `agent`, `hook`, `frontmatter` |
| Schema | `schema`, `field`, `property`, `validation` |
| Deprecation | `deprecated`, `removed`, `breaking`, `migration` |
| New features | `new`, `added`, `support`, `feature`, `capability` |
| Models | `sonnet`, `opus`, `haiku`, `model` |
| Environment | `environment`, `variable`, `CLAUDE_` |

---

## Output Example (JSON)

```json
{
  "releases_checked": 3,
  "latest_version": "v1.0.30",
  "findings": { "new": [], "deprecated": [], "breaking": [], "fixed": [] },
  "craft_state": { "hardcoded_models": [], "agent_features": {}, "hook_events": [] },
  "action_items": []
}
```

---

## See Also

- [/craft:code:desktop-watch](desktop-watch.md) -- Claude Desktop release tracking
- [/craft:code:command-audit](command-audit.md) -- Frontmatter validation
- [/craft:code:deps-audit](deps-audit.md) -- Security vulnerability scan
