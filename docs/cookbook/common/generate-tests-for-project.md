---
title: "Generate Tests for a Project"
description: "Auto-detect project type and generate a full test suite with /craft:test:gen"
category: "cookbook"
level: "beginner"
time_estimate: "5 minutes"
related:
  - guide/test-commands.md
  - guide/test-architecture.md
  - tutorials/testing-quickstart.md
---

# Generate Tests for a Project

## Problem

You have a project (plugin, CLI tool, ZSH plugin, or MCP server) and want a comprehensive test suite generated automatically.

## Solution

### 1. Auto-detect and generate

```bash
/craft:test:gen
```

The generator detects your project type from indicator files and renders Jinja2 templates into test files.

### 2. Preview first (recommended)

```bash
/craft:test:gen --dry-run
```

Output:

```text
Test Generation Plan
Project: my-plugin (plugin)
Template: templates/plugin/
Output: tests/

Files to generate:
  [new]    tests/test_structure.py     (7 tests)
  [new]    tests/test_commands.py      (24 tests)
  [new]    tests/test_skills.py        (5 tests)
  [skip]   tests/conftest.py           (already exists)
```

### 3. Run generated tests

```bash
/craft:test unit
```

## Explanation

The generator works in 4 steps:

1. **Detect** — Checks for indicator files (`.claude-plugin/plugin.json`, `*.plugin.zsh`, etc.)
2. **Gather** — Scans the project for variables (command names, skills, entry points)
3. **Render** — Applies Jinja2 templates with gathered variables
4. **Write** — Creates test files in `tests/` (skips existing files unless `--force`)

## Variations

### Force a project type

```bash
/craft:test:gen plugin
/craft:test:gen cli
/craft:test:gen mcp
```

### Generate only unit tests

```bash
/craft:test:gen --tier unit
```

### Overwrite existing tests

```bash
/craft:test:gen --force
```

### Generate to a different directory

```bash
/craft:test:gen --output my-tests/
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Could not detect project type" | Use `--type` to force detection |
| "Template render error" | Run `/craft:test:template validate` |
| Tests fail after generation | Generated tests check real structure — fix the issues they find |
| `jinja2` not installed | `pip install jinja2` |

## Related

- [Testing Quickstart](../../tutorials/testing-quickstart.md) — Full step-by-step tutorial
- [Test Architecture](../../guide/test-architecture.md) — How the template system works
- [Test Commands Reference](../../guide/test-commands.md) — All options and flags
