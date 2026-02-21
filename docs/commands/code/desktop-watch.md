# /craft:code:desktop-watch

> **Track Claude Desktop releases and identify plugin integration opportunities**

---

## Synopsis

```bash
/craft:code:desktop-watch [--format fmt]
```

**Quick examples:**

```bash
# Terminal output (default)
/craft:code:desktop-watch

# Markdown report
/craft:code:desktop-watch --format markdown
```

---

## Description

Monitors Claude Desktop releases for features relevant to plugin development and distribution. This is an instruction-driven command -- Claude performs the research directly using web tools; no external script is required.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--format` | Output format (terminal\|markdown) | terminal |

---

## How It Works

When invoked, Claude performs these steps:

1. **WebSearch** for Claude Desktop release notes and changelog
2. **WebFetch** the Anthropic support/changelog pages found in results
3. **Parse** for developer-relevant features (MCP support, extension capabilities, file system access, API updates)
4. **Compare** against craft's current distribution channels
5. **Output** a report with integration opportunities

---

## Output Example

```text
DESKTOP WATCH -- Claude Desktop

Source: Anthropic support pages + web search
Last checked: 2026-02-21

DEVELOPER-RELEVANT FEATURES
  MCP
  - MCP server support added in Desktop v1.x
  - New transport protocols supported

INTEGRATION OPPORTUNITIES
  - Craft could register as MCP server for Desktop
  - Desktop file access enables local plugin workflows
```

---

## Notes

- Results depend on publicly available information at time of execution
- Web search results may vary between runs
- For Claude Code (CLI) releases, use `/craft:code:release-watch` instead

---

## See Also

- [/craft:code:release-watch](release-watch.md) -- Claude Code CLI release tracking
- [/craft:code:command-audit](command-audit.md) -- Frontmatter validation
