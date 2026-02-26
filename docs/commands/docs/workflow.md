# /craft:docs:workflow

> **Workflow documentation generator for multi-step processes**

---

## Synopsis

```bash
/craft:docs:workflow <topic> [options]
```

**Quick examples:**

```bash
# Generate workflow docs from code analysis
/craft:docs:workflow "git"

# Generate from a brainstorm spec (recommended)
/craft:docs:workflow "auth" --from-spec

# Auto-detect workflows in the codebase
/craft:docs:workflow --detect
```

---

## Description

Generates task-focused workflow documentation that walks users through multi-step processes. Analyzes code for command chains, hooks, events, and branch strategies, then produces structured docs using `WORKFLOW-TEMPLATE.md`.

The recommended path is `--from-spec`, which reads brainstorm specs from `docs/specs/SPEC-[topic]-*.md` and maps spec sections (user stories, architecture, acceptance criteria) into workflow sections (when to use, prerequisites, steps, troubleshooting).

Output lands in `docs/workflows/` by default and includes a mermaid flowchart, step-by-step instructions, variation paths, and a quick-reference command table.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `topic` | Workflow topic name | (required unless `--detect`) |
| `--from-spec` | Use brainstorm spec as input source | `false` |
| `--detect` | Auto-detect workflows in codebase | `false` |
| `--from-commits` | Generate from recent commit patterns | `false` |
| `--output PATH` | Custom output directory | `docs/workflows/` |
| `--format terminal` | Preview in terminal only | file output |
| `--dry-run` | Show plan without generating | `false` |
| `--no-diagram` | Skip mermaid diagram | `false` |
| `--no-nav` | Skip mkdocs.yml update | `false` |

---

## How It Works

Runs through four steps:

1. **Analyze Topic** — Detects patterns in the codebase (branch workflows, worktree management, commit conventions, CI/CD files) and identifies related commands
2. **Map Workflow Steps** — Sequences the actions into a primary path and identifies variation paths (e.g., hotfix, quick fix)
3. **Generate Documentation** — Produces the workflow doc with sections: When to Use, Prerequisites, Basic Workflow (with mermaid diagram), Variations, Troubleshooting, and Quick Reference
4. **Validate and Link** — Verifies all referenced commands exist, validates the mermaid diagram, and updates `mkdocs.yml` navigation

When using `--detect`, the generator scans command chains, hook systems, git patterns, CI/CD files, and README sections to find documentable workflows automatically.

---

## See Also

- [/craft:docs:guide](guide.md) — Feature guide generation
- [/craft:docs:tutorial](tutorial.md) — Interactive tutorial generation
- [/craft:docs:check](check.md) — Documentation health check
