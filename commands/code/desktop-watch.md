---
description: Track Claude Desktop releases and identify plugin integration opportunities
arguments:
  - name: format
    description: "Output format: terminal, markdown"
    required: false
    default: terminal
---

# /craft:code:desktop-watch - Desktop Release Watch

Monitor Claude Desktop releases for features relevant to plugin development and distribution.

## How It Works

This is an instruction-driven command — Claude performs the research directly using web tools. No external script is required.

## Execution Steps

When invoked, perform these steps in order:

1. **WebSearch** for "Claude Desktop release notes 2026" and "Anthropic Claude Desktop changelog"
2. **WebFetch** the Anthropic support/changelog pages found in search results
3. **Parse** for developer-relevant features:
   - MCP server support and changes
   - Extension/plugin capabilities
   - File system access changes
   - API or protocol updates
   - New integrations or tools
4. **Compare** against craft's current distribution channels and capabilities
5. **Output** a report with integration opportunities

## Output Format

### Terminal (default)

```text
╔═════════════════════════════════════════════════════════════╗
║  DESKTOP WATCH — Claude Desktop                             ║
╠═════════════════════════════════════════════════════════════╣
║                                                             ║
║  Source: Anthropic support pages + web search                ║
║  Last checked: 2026-02-21                                   ║
║                                                             ║
╠═════════════════════════════════════════════════════════════╣
║  DEVELOPER-RELEVANT FEATURES                                ║
║                                                             ║
║  MCP                                                        ║
║  - MCP server support added in Desktop v1.x                 ║
║  - New transport protocols supported                        ║
║                                                             ║
║  INTEGRATION OPPORTUNITIES                                  ║
║                                                             ║
║  - Craft could register as MCP server for Desktop           ║
║  - Desktop file access enables local plugin workflows       ║
║                                                             ║
╚═════════════════════════════════════════════════════════════╝
```

### Markdown

Human-readable report with sections and action items, suitable for saving to a file.

## Usage

```bash
/craft:code:desktop-watch                    # Terminal output
/craft:code:desktop-watch --format markdown  # Markdown report
```

## Notes

- Results depend on publicly available information at time of execution
- Web search results may vary between runs
- For Claude Code (CLI) releases, use `/craft:code:release-watch` instead

## Integration

Works with:

- `/craft:code:release-watch` - Claude Code CLI release tracking
- `/craft:code:sync-features` - Combined feature sync wizard
