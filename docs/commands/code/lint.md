# /craft:code:lint

> **Code style and quality checks with mode support**

---

## Synopsis

```bash
/craft:code:lint [mode] [path] [--dry-run|-n]
```

**Quick examples:**

```bash
# Quick style check
/craft:code:lint

# Verbose with fix suggestions
/craft:code:lint debug

# Performance-focused rules
/craft:code:lint optimize

# Comprehensive pre-release check
/craft:code:lint release

# Check specific path
/craft:code:lint debug src/

# Preview commands without execution
/craft:code:lint --dry-run
```

---

## Description

Runs code style and quality checks with configurable depth based on execution mode. Automatically detects project type (Python, JavaScript, TypeScript, R, Go, Rust) and uses the appropriate linter. Supports dry-run mode to preview linting strategy before execution.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `mode` | Execution mode (default\|debug\|optimize\|release) | default |
| `path` | File or directory to lint | Current directory |
| `--dry-run` / `-n` | Preview linting commands without executing | false |

---

## Modes

| Mode | Time | Focus |
|------|------|-------|
| **default** | < 10s | Quick style check (E, W, F rules) |
| **debug** | < 120s | All rules + fix suggestions + source context |
| **optimize** | < 180s | Performance-focused rules (PERF, C4, SIM) |
| **release** | < 300s | Comprehensive + types + security |

---

## Project Type Detection

| Project | Linter | Config Files |
|---------|--------|--------------|
| Python | ruff, flake8, pylint | pyproject.toml, .flake8 |
| JavaScript/TypeScript | ESLint, Prettier | .eslintrc.*, prettier.config.* |
| R | lintr | .lintr |
| Go | golint, staticcheck | - |
| Rust | clippy | - |

---

## Markdown File Handling

When the target path contains `.md` files, `/craft:code:lint` automatically delegates markdown linting to `/craft:docs:lint` and combines results.

---

## See Also

- [/craft:docs:lint](../docs.md) — Markdown-specific linting (category page)
- [/craft:code:ci-local](ci-local.md) — Run full CI suite locally
- [/craft:check](../check.md) — Pre-flight validation
