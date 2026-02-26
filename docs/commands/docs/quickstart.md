# /craft:docs:quickstart

> **Generate a 5-minute quickstart guide for any project**

---

## Synopsis

```bash
/craft:docs:quickstart [options]
```

**Quick examples:**

```bash
# Auto-detect project and generate quickstart
/craft:docs:quickstart

# Write to a custom path
/craft:docs:quickstart --output docs/QUICK-START.md

# Insert as a section in an existing README
/craft:docs:quickstart --output README.md --section
```

---

## Description

Detects the project type (Node.js, Python, R, Go, Rust, Claude plugin, MkDocs site), extracts setup steps from README, package files, and CI configuration, then generates a copy-paste ready quickstart guide using the `QUICK-START-TEMPLATE.md` template.

The output includes a TL;DR, 30-second setup commands, a common-tasks table, a project-layout table, and current status. Everything is designed to get a new user running in under 5 minutes with zero decision-making.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--output PATH` | Custom output path | `docs/QUICK-START.md` |
| `--section` | Insert as section in an existing file (use with `--output`) | `false` |
| `--format terminal` | Preview in terminal only (no file written) | - |
| `--dry-run` | Show plan without generating | `false` |
| `--no-status` | Skip the current-status section | `false` |
| `--verbose` | Detailed output during generation | `false` |

---

## How It Works

1. **Detect project type** — checks for `package.json`, `pyproject.toml`, `DESCRIPTION`, `go.mod`, `Cargo.toml`, `.claude-plugin/`, or `mkdocs.yml`.
2. **Extract setup steps** — reads README, CLAUDE.md, package manifests, and CI workflows to find install and verify commands.
3. **Generate quickstart** — fills the `QUICK-START-TEMPLATE.md` template with TL;DR, 30-second setup, common tasks, project layout, and status sections.
4. **Validate** — verifies that all listed commands are runnable and all paths exist.

### Called By

- `/craft:docs:update --with-quickstart`
- `/craft:docs:update` (when quickstart score >= 3)

---

## See Also

- [/craft:docs:help](help.md) — Help page generator
- [/craft:docs:check](check.md) — Documentation health check
- [/craft:docs:update](update.md) — Update documentation
