---
description: Track Claude Desktop releases and identify plugin integration opportunities
category: code
arguments:
  - name: format
    description: "Output format: terminal, json, markdown"
    required: false
    default: terminal
---

# Desktop Watch

Monitor Claude Desktop releases for features relevant to plugin development.

**This command now uses the unified release-watch tool.**

## Usage

```bash
/craft:code:desktop-watch                    # Terminal output
/craft:code:desktop-watch --format markdown  # Markdown report
```

## Execution

When invoked, run the unified release-watch with `--product desktop`:

```bash
python3 scripts/release-watch.py --product desktop --format <format>
```

This fetches Desktop release notes from Anthropic support docs, scans for plugin-relevant changes, and presents findings in the same format as the Code release watch.

## See Also

- `/craft:code:release-watch` — Full unified release tracking (Code + Desktop)
- `/craft:code:release-watch --product desktop` — Direct Desktop tracking
- `/craft:code:ci-fix` - Fix CI Failures
- `/craft:code:command-audit` - Validate command frontmatter, find deprecated patterns, report health score
- `/craft:code:coverage` - Test Coverage Report
- `/craft:code:deps-check` - Dependency Check
- `/craft:code:lint` - Code style and quality checks with mode support
