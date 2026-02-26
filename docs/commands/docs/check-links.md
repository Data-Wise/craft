# /craft:docs:check-links

> **Internal link validation for documentation**

---

## Synopsis

```bash
/craft:docs:check-links [mode] [path] [options]
```

**Quick examples:**

```bash
# Quick check of all docs
/craft:docs:check-links

# Comprehensive validation with anchor checks
/craft:docs:check-links release

# Check a specific directory
/craft:docs:check-links docs/guide/

# Preview what will be checked
/craft:docs:check-links --dry-run
```

---

## Description

Validates internal links in markdown files to prevent broken references before deployment. Scans for relative links, absolute repo links, and reference-style links, then resolves each target path and reports any files not found.

Supports a `.linkcheck-ignore` file in the project root to document expected broken links (test files, gitignored references). Only critical broken links cause a non-zero exit code, so CI pipelines stay clean.

Philosophy: "Find broken links before they break production."

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `mode` | Execution mode: `default`, `debug`, `optimize`, `release` | `default` |
| `path` | Specific file or directory to check | All docs |
| `--dry-run`, `-n` | Preview checks without executing them | `false` |

---

## Modes

| Mode | Time | Focus |
|------|------|-------|
| **default** | < 10s | Internal file links only |
| **debug** | < 120s | Verbose output with context and suggestions |
| **optimize** | < 180s | Parallel processing for large doc sets |
| **release** | < 300s | Internal links + anchor validation + consistency |

---

## How It Works

1. **Load ignore rules** from `.linkcheck-ignore` (if present)
2. **Detect scope** — target path or all `docs/` and root markdown files
3. **Parse links** — extracts inline links, reference links, and link definitions
4. **Validate targets** — resolves relative and absolute paths, checks file existence
5. **Categorize results** — critical (must fix) vs. expected (documented in `.linkcheck-ignore`)
6. **Report** — VS Code-clickable `file:line:col` format with summary

In **release** mode, an additional anchor validation phase checks that `file.md#heading` targets resolve to actual headings in the target file.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All links valid, or only expected broken links |
| `1` | Critical broken links found |
| `2` | Validation error |

---

## See Also

- [/craft:docs:check](check.md) — Full documentation health check
- [/craft:docs:lint](lint.md) — Markdown style and quality checks
- [/craft:docs:update](update.md) — Update documentation
