# /craft:docs:tutorial

> **Interactive tutorial generator with GIF demos and mermaid diagrams**

---

## Synopsis

```bash
/craft:docs:tutorial <topic> [options]
```

**Quick examples:**

```bash
# Generate a getting-started tutorial
/craft:docs:tutorial "getting-started" --with-gifs --with-diagrams

# Analyze project for tutorial opportunities
/craft:docs:tutorial --analyze

# Preview without writing files
/craft:docs:tutorial "feature-name" --dry-run
```

---

## Description

Creates progressive, step-by-step tutorials organized into difficulty levels. Each tutorial includes interactive command steps, optional GIF demos via VHS tapes, and mermaid learning-path diagrams.

The generator analyzes your project to determine what to teach, designs a step sequence with appropriate complexity, and produces complete tutorial pages ready for the docs site. Tutorials follow a three-level structure: Getting Started (~10 min), Intermediate (~20 min), and Advanced (~35 min).

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `topic` | Tutorial topic or level name | (required) |
| `--list` | Show available tutorial templates | `false` |
| `--analyze` | Analyze project for tutorial content | `false` |
| `--steps N` | Target number of steps | `7-13` |
| `--with-gifs` | Generate VHS tapes for demos | `false` |
| `--with-diagrams` | Include mermaid learning path | `false` |
| `--dry-run` | Preview without writing files | `false` |

---

## How It Works

Runs through six phases:

1. **Analyze** — Scans CLI commands, configuration, integrations, and existing docs to identify tutorial content
2. **Design Steps** — Plans the step sequence, estimates timing, and identifies which steps need GIF demos
3. **Generate Content** — Creates tutorial index and level pages under `docs/tutorials/`
4. **Create VHS Tapes** — Generates `.tape` files for demo recordings (when `--with-gifs`)
5. **Add Mermaid Diagrams** — Creates learning-path flowcharts showing progression across levels (when `--with-diagrams`)
6. **Update Navigation** — Adds tutorial entries to `mkdocs.yml`

Each tutorial step includes a number, title, description, optional command, optional hint, and an interactive flag indicating whether the user needs to take action.

---

## See Also

- [/craft:docs:guide](guide.md) — Feature guide generation
- [/craft:docs:check](check.md) — Documentation health check
- [/craft:docs:sync](sync.md) — Smart documentation detection
