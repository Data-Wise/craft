# /craft:test:template

> **Manage Jinja2 templates for test generation**

---

## Synopsis

```bash
/craft:test:template <action> [template] [--type TYPE] [--output PATH]
```

**Quick examples:**

```bash
/craft:test:template list                       # List all templates
/craft:test:template list --type plugin         # Plugin templates only
/craft:test:template show plugin/test_structure  # Show template source
/craft:test:template validate                    # Check all templates
/craft:test:template render plugin/test_structure --output preview.py
```

---

## Description

Manages the Jinja2 templates that power `/craft:test:gen`. Provides lifecycle operations for listing, inspecting, validating, rendering, creating, editing, and deleting templates.

---

## Actions

| Action | Description |
|--------|-------------|
| `list` | Show available templates (filterable by type) |
| `show` | Display raw Jinja2 template source |
| `validate` | Check syntax, variables, and rendered output |
| `render` | Preview rendered output with sample variables |
| `create` | Add a new template with boilerplate |
| `edit` | Modify existing template (re-validates after save) |
| `delete` | Remove template and registry entry |

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `action` | Action to perform (required) | - |
| `template` | Template path (e.g., `plugin/test_structure`) | - |
| `--type TYPE` | Filter: `plugin`, `zsh`, `cli`, `mcp`, `_base` | All |
| `--output PATH` | Output path for `render` action | stdout |

---

## See Also

- [/craft:test:gen](gen.md) — Generate test suites
- [/craft:test](../test.md) — Unified test runner
- [Test Architecture Guide](../../guide/test-architecture.md) — Template system details
