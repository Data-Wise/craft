# /craft:test:gen

> **Generate test suites with project-type auto-detection**

---

## Synopsis

```bash
/craft:test:gen [project-type] [--tier TIER] [--output DIR]
               [--force] [--diff] [--dry-run]
```

**Quick examples:**

```bash
/craft:test:gen                     # Auto-detect and generate all
/craft:test:gen plugin              # Force plugin type
/craft:test:gen --tier unit         # Unit tests only
/craft:test:gen --diff              # Preview changes
/craft:test:gen --dry-run           # Preview plan
```

---

## Description

Generates test suites by auto-detecting the project type and rendering Jinja2 templates. Supports 4 project types: Claude Code plugin, ZSH plugin, Python/Node CLI, and MCP server.

Replaces the old `/craft:test:cli-gen` and `/craft:test:generate` commands.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `project-type` | Force type: `plugin`, `zsh`, `cli`, `mcp` | Auto-detect |
| `--tier TIER` | Filter: `smoke`, `unit`, `integration`, `e2e`, `all` | `all` |
| `--output DIR` | Output directory | `tests/` |
| `--force` | Overwrite existing test files | `false` |
| `--diff` | Show diff preview without writing | `false` |
| `--dry-run`, `-n` | Preview generation plan | `false` |

---

## See Also

- [/craft:test](../test.md) — Unified test runner
- [/craft:test:template](template.md) — Manage templates
- [Test Architecture Guide](../../guide/test-architecture.md) — Template system details
