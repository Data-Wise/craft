# /craft:code:command-audit

> **Validate command frontmatter, find deprecated patterns, report health score**

---

## Synopsis

```bash
/craft:code:command-audit [--format fmt] [--fix] [--strict]
```

**Quick examples:**

```bash
# Terminal output (default)
/craft:code:command-audit

# JSON output for CI pipelines
/craft:code:command-audit --format json

# Auto-fix safe issues
/craft:code:command-audit --fix

# Strict mode (warnings become errors)
/craft:code:command-audit --strict
```

---

## Description

Scans all command, skill, and agent files for frontmatter validity, deprecated patterns, hardcoded model names, and orphaned scripts. Reports a health score from 0-100.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--format` | Output format (terminal\|json\|markdown) | terminal |
| `--fix` | Auto-fix safe issues (remove invalid fields, rename `args` to `arguments`) | false |
| `--strict` | Treat warnings as errors (for CI) | false |

---

## Checks

| # | Check | Severity |
|---|-------|----------|
| 1 | Invalid frontmatter fields | ERROR |
| 2 | Missing `description` | ERROR |
| 3 | Deprecated markers | WARNING |
| 4 | Hardcoded model names | WARNING |
| 5 | YAML parse errors | ERROR |
| 6 | Orphaned scripts | WARNING |
| 7 | External tool availability | INFO |
| 8 | Schema compliance | ERROR |

---

## Health Score

| Score | Rating |
|-------|--------|
| 90-100 | Excellent |
| 80-89 | Good |
| 60-79 | Needs attention |
| 0-59 | Critical |

---

## CI Integration

```bash
# Fail on any warnings or errors
bash scripts/command-audit.sh --strict

# Machine-readable output
bash scripts/command-audit.sh --format json | python3 -m json.tool
```

---

## See Also

- [/craft:code:lint](lint.md) -- Code style and quality checks
- [/craft:check](../check.md) -- Pre-flight validation
- [/craft:code:release-watch](release-watch.md) -- Track upstream releases
