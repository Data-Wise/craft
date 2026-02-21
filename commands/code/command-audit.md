---
description: Validate command frontmatter, find deprecated patterns, report health score
arguments:
  - name: format
    description: "Output format: terminal, json, markdown"
    required: false
    default: terminal
  - name: fix
    description: Auto-fix safe issues
    required: false
    default: false
    alias: --fix
  - name: strict
    description: Treat warnings as errors (for CI)
    required: false
    default: false
    alias: --strict
---

# /craft:code:command-audit - Command Audit

Validate all command, skill, and agent frontmatter against the schema. Reports errors, warnings, and a health score.

## What It Checks

| # | Check | Severity | Description |
|---|-------|----------|-------------|
| 1 | Invalid frontmatter fields | ERROR | Keys not in `_schema.json` |
| 2 | Missing `description` | ERROR | Required field per schema |
| 3 | Deprecated markers | WARNING | Files containing `DEPRECATED` |
| 4 | Hardcoded model names | WARNING | References to specific model versions |
| 5 | YAML parse errors | ERROR | Malformed frontmatter YAML |
| 6 | Orphaned scripts | WARNING | Scripts in `scripts/` not referenced by any command |
| 7 | External tool availability | INFO | Checks for ruff, mkdocs, python3, gh, etc. |
| 8 | Schema compliance | ERROR | Required fields present and valid |

## Usage

```bash
/craft:code:command-audit                    # Terminal output (default)
/craft:code:command-audit --format json      # JSON output
/craft:code:command-audit --format markdown  # Markdown report
/craft:code:command-audit --fix              # Auto-fix safe issues
/craft:code:command-audit --strict           # Treat warnings as errors
```

## Auto-Fix Mode

When `--fix` is passed, the script will:

- Remove invalid frontmatter fields
- Rename `args` to `arguments`

Other issues require manual intervention.

## CI Integration

Use `--strict` to fail on any warnings (useful in CI pipelines):

```bash
bash scripts/command-audit.sh --strict
# Exit code 0 = clean, 2 = errors or warnings
```

Use `--format json` for machine-readable output:

```bash
bash scripts/command-audit.sh --format json | python3 -m json.tool
```

## Health Score

The health score is calculated as:

```text
score = 100 - (errors * 5) - (warnings * 2)
score = max(0, score)
```

| Score | Rating |
|-------|--------|
| 90-100 | Excellent |
| 80-89 | Good |
| 60-79 | Needs attention |
| 0-59 | Critical |

## Output Example

```text
╔═════════════════════════════════════════════════════════════╗
║  COMMAND AUDIT                                             ║
╠═════════════════════════════════════════════════════════════╣
║                                                            ║
║  Scanning commands/, skills/, agents/...                   ║
║                                                            ║
║  ✓ 104 files scanned                                      ║
║  ✗ 2 errors found                                         ║
║  ⚠ 3 warnings found                                       ║
║                                                            ║
╠═════════════════════════════════════════════════════════════╣
║  ERRORS                                                    ║
║  ✗ commands/foo/bar.md: invalid field 'trigger'            ║
╠═════════════════════════════════════════════════════════════╣
║  Health Score: 90/100                                      ║
╚═════════════════════════════════════════════════════════════╝
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | Warnings found (no errors) |
| 2 | Errors found |

In `--strict` mode, warnings also cause exit code 2.

## Integration

Works with:

- `/craft:code:lint` - Code quality checks
- `/craft:check` - Pre-flight validation
- `/craft:code:release` - Release validation
