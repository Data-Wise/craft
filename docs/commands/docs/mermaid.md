# /craft:docs:mermaid

> **Mermaid diagrams — templates, NL creation, MCP validation, and live preview**

---

## Synopsis

```bash
/craft:docs:mermaid [input] [--validate] [--preview] [--output <file>]
```

**Quick examples:**

```bash
# Show all available templates
/craft:docs:mermaid

# Generate a specific template
/craft:docs:mermaid workflow

# Create diagram from natural language description
/craft:docs:mermaid "show the release pipeline from dev to main"
```

---

## Description

Generates, validates, and previews Mermaid diagrams. Supports six built-in templates (dependency, workflow, architecture, comparison, sequence, state) as well as natural language creation where you describe a diagram in plain English and get validated Mermaid code.

When given a quoted string instead of a template name, the command analyzes the description, selects the best diagram type (flowchart, sequence, state, or ER diagram), and generates Mermaid code following built-in best practices for label length, layout direction, and formatting.

Validation and preview are powered by the `mcp-mermaid` MCP server. Use `--validate` for syntax checking or `--preview` to render to SVG and open in a browser for visual iteration.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `input` | Template type (`dependency`, `workflow`, `architecture`, `comparison`, `sequence`, `state`, `all`) or a quoted natural language description | `all` |
| `--output <file>` | Write output to a file instead of stdout | stdout |
| `--validate` | Validate diagram syntax via mcp-mermaid after generation | `false` |
| `--preview` | Render to SVG and open in browser for visual inspection | `false` |

---

## How It Works

**Template mode** (unquoted keyword): Outputs a production-ready Mermaid template with customization tips. Use `all` to see every template, or specify a type to get just one.

**Natural language mode** (quoted string): Follows a five-step workflow:

1. **Generate** — Analyzes description and creates Mermaid code
2. **Validate** — Checks syntax via mcp-mermaid (if `--validate` or `--preview`)
3. **Preview** — Opens rendered SVG in browser (if `--preview`)
4. **Iterate** — Refine via conversation until satisfied
5. **Save** — Output to specified file or display inline

**Built-in best practices** enforced in all generated diagrams:

- Node labels capped at 15 characters; edge labels at 10
- Markdown string syntax for multi-line text (no `<br/>` tags)
- Vertical layouts (`TD`/`TB`) for complex diagrams, horizontal (`LR`) for relationships

---

## Templates

| Template | Direction | Best For |
|----------|-----------|----------|
| `dependency` | LR | Package/module relationships |
| `workflow` | TD | Process flows with decisions |
| `architecture` | TB | System component diagrams |
| `comparison` | LR | Before/after, option A vs B |
| `sequence` | — | Time-based API interactions |
| `state` | — | State machine transitions |

---

## See Also

- [/craft:docs:check](check.md) — Full documentation health check (includes Mermaid validation)
- [/craft:docs:lint](lint.md) — Markdown quality checks
