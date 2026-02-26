# /craft:docs:guide

> **Orchestrated guide generator with mermaid diagrams, GIF demos, and refcards**

---

## Synopsis

```bash
/craft:docs:guide <feature> [options]
```

**Quick examples:**

```bash
# Generate complete feature guide with all artifacts
/craft:docs:guide "session tracking"

# Generate guide without GIF demo
/craft:docs:guide "sessions" --no-demo

# Only generate the refcard
/craft:docs:guide "sessions" --refcard-only
```

---

## Description

One command to generate complete feature documentation: a structured guide, VHS tape for a GIF demo, mermaid diagrams, a domain refcard (for features with 3+ commands), and navigation updates. Smart defaults mean it works without options; flags let you skip individual artifacts.

The generated guide follows a consistent template with sections for Overview, Quick Start, How It Works (with embedded mermaid diagram), Commands, Configuration, and Troubleshooting. Diagram type is chosen automatically based on the feature: workflow diagrams for hook-based features, architecture diagrams for modules, and sequence diagrams for multi-step processes.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `feature` | Feature name or topic | (required) |
| `--no-demo` | Skip VHS tape generation | `false` |
| `--no-mermaid` | Skip diagram generation | `false` |
| `--no-refcard` | Skip refcard generation | `false` |
| `--no-nav` | Skip mkdocs.yml update | `false` |
| `--refcard-only` | Only generate refcard | `false` |
| `--dry-run` | Preview without writing files | `false` |
| `--template TYPE` | Guide template: default, api, cli | `default` |
| `--output PATH` | Custom output path | `docs/guide/` |

---

## How It Works

Runs through seven phases:

1. **Analyze** — Runs `/craft:docs:analyze` internally to classify the feature, find CLI commands, hooks, and modules
2. **Show Plan** — Presents what will be created (guide, VHS tape, diagram, refcard, nav update) and waits for confirmation
3. **Generate Guide** — Writes the guide document with all template sections populated from analysis
4. **Generate VHS Tape** — Creates a `.tape` file showcasing key commands (skipped with `--no-demo`)
5. **Generate Refcard** — Produces a one-page quick reference with essential commands, common workflows, and troubleshooting shortcuts (skipped with `--no-refcard`)
6. **Update Navigation** — Adds guide and refcard entries to `mkdocs.yml` (skipped with `--no-nav`)
7. **Summary** — Reports all created files and provides next steps (generate GIF, optimize, preview, commit)

---

## See Also

- [/craft:docs:tutorial](tutorial.md) — Interactive tutorial generation
- [/craft:docs:workflow](workflow.md) — Workflow documentation generation
- [/craft:docs:check](check.md) — Documentation health check
- [/craft:docs:sync](sync.md) — Smart documentation detection
