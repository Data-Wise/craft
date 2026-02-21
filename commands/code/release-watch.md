---
description: Track Claude Code releases and identify plugin-relevant changes
arguments:
  - name: count
    description: Number of releases to check
    required: false
    default: 3
  - name: since
    description: Only show releases after this version (e.g., v1.0.25)
    required: false
  - name: format
    description: "Output format: terminal, json, markdown"
    required: false
    default: terminal
---

# Release Watch

Monitor Claude Code releases for changes that affect the Craft plugin system.

## Usage

```bash
/craft:code:release-watch [options]
```

## What This Does

1. **Fetches releases** from `anthropics/claude-code` via the GitHub API
2. **Scans release notes** for plugin-relevant keywords (plugin, schema, deprecation, model changes, environment variables)
3. **Categorizes findings** as NEW / DEPRECATED / BREAKING / FIXED
4. **Cross-references craft state** — checks agents for special frontmatter fields, scans for hardcoded model names, audits hook patterns
5. **Generates action items** when attention is needed

## Requirements

- **gh CLI** — must be installed and authenticated (`gh auth login`)

## Keyword Categories

| Category | Keywords Scanned |
|----------|-----------------|
| Plugin system | `plugin`, `skill`, `command`, `agent`, `hook`, `frontmatter` |
| Schema | `schema`, `field`, `property`, `validation` |
| Deprecation | `deprecated`, `removed`, `breaking`, `migration` |
| New features | `new`, `added`, `support`, `feature`, `capability` |
| Models | `sonnet`, `opus`, `haiku`, `model` |
| Environment | `environment`, `variable`, `CLAUDE_` |

## Examples

```bash
# Check latest 3 releases (default)
/craft:code:release-watch

# Check latest 5 releases
/craft:code:release-watch --count 5

# Only releases after a specific version
/craft:code:release-watch --since v1.0.25

# JSON output (for CI or piping)
/craft:code:release-watch --format json

# Markdown output (for reports)
/craft:code:release-watch --format markdown
```

## Output Formats

### Terminal (default)

Box-drawing display with sections for release summary, plugin-relevant changes, craft state analysis, and action items.

### JSON

Structured output suitable for CI pipelines and automation:

```json
{
  "releases_checked": 3,
  "latest_version": "v1.0.30",
  "findings": { "new": [], "deprecated": [], "breaking": [], "fixed": [] },
  "craft_state": { "hardcoded_models": [], "agent_features": {}, "hook_events": [] },
  "action_items": []
}
```

### Markdown

Human-readable report with checkboxes for action items.

## Craft State Analysis

The tool inspects the current codebase for potential compatibility issues:

- **Hardcoded models** — scans for model name strings (e.g., `claude-3-opus`, `claude-sonnet-4`) across all project files
- **Agent features** — reads agent frontmatter for `memory`, `isolation`, `background` fields that may be affected by upstream changes
- **Hook patterns** — checks command files for `hooks`, `trigger`, `event` fields

## CI Usage

```bash
# Run in CI and fail if breaking changes detected
output=$(python3 scripts/release-watch.py --format json --count 5)
breaking=$(echo "$output" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['findings']['breaking']))")
if [ "$breaking" -gt 0 ]; then
  echo "Breaking changes detected in Claude Code releases"
  echo "$output" | python3 -m json.tool
  exit 1
fi
```

## Integration

Works with:

- `/craft:code:release` — Release preparation
- `/craft:code:deps-check` — Dependency auditing
