# /craft:docs:help

> **Generate comprehensive help pages for commands using ADHD-friendly templates**

---

## Synopsis

```bash
/craft:docs:help <command> [options]
```

**Quick examples:**

```bash
# Generate help page for /craft:check
/craft:docs:help "check"

# Generate help pages for all docs commands
/craft:docs:help "docs:*"

# Preview in terminal without writing files
/craft:docs:help "check" --format terminal
```

---

## Description

Reads a command definition file, extracts its synopsis, flags, examples, and integration points, then generates a structured help page using the `HELP-PAGE-TEMPLATE.md` template. The output is consistent across all commands: quick examples up front, options in tables, and cross-references at the bottom.

Designed for one-command operation -- no manual template filling required. Supports glob patterns to generate help pages for entire command categories at once.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `<command>` | Command name or glob pattern (e.g., `"check"`, `"docs:*"`) | Required |
| `--output PATH` | Custom output directory | `docs/help/` |
| `--format terminal` | Preview in terminal only (no file written) | - |
| `--format json` | Output as JSON | - |
| `--dry-run` | Show plan without generating | `false` |
| `--verbose` | Detailed output during generation | `false` |
| `--no-nav` | Skip mkdocs.yml navigation update | `false` |

---

## How It Works

1. **Locate** -- finds the command file under `commands/` and reads its definition.
2. **Extract** -- pulls synopsis, description, flags, arguments, examples, and integration points from the source.
3. **Generate** -- fills the `HELP-PAGE-TEMPLATE.md` template with extracted content, producing sections for synopsis, quick examples, options table, detailed examples, troubleshooting, and see-also links.
4. **Validate** -- checks internal links, verifies example syntax, and optionally adds the page to mkdocs.yml navigation.

### Called By

- `/craft:docs:update --with-help`
- `/craft:docs:update` (when help score >= 2)

---

## See Also

- [/craft:docs:quickstart](quickstart.md) -- Quick start guide generator
- [/craft:docs:check](check.md) -- Documentation health check
- [/craft:docs:update](update.md) -- Update documentation
