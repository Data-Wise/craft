# /craft:test:cli-run

> **CLI test suite runner with interactive and automated modes**

---

## Synopsis

```bash
/craft:test:cli-run [mode] [--path PATH] [--dry-run]
```

**Quick examples:**

```bash
# Interactive guided mode
/craft:test:cli-run

# CI-ready automated mode
/craft:test:cli-run automated

# Auto-detect from test files
/craft:test:cli-run auto --path tests/cli/
```

---

## Description

Runs CLI test suites with mode-specific execution strategies. Interactive mode provides guided test selection and real-time feedback. Automated mode runs all tests with CI-friendly exit codes (0 for success, 1 for failure). Auto mode detects execution context from test file patterns.

Designed for command-line tool testing with support for subprocess execution, stdin/stdout validation, and exit code verification.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `mode` | Execution mode: `interactive`, `automated`, `auto` | `interactive` |
| `--path PATH` | CLI test file or directory | `tests/cli/` |
| `--dry-run`, `-n` | Preview test execution plan | `false` |

---

## Modes

| Mode | Behavior | Exit Codes | Use Case |
|------|----------|------------|----------|
| `interactive` | Guided test selection with real-time feedback | Always 0 | Local development |
| `automated` | Run all tests, fail fast on errors | 0/1 | CI/CD pipelines |
| `auto` | Detect mode from test file patterns | Context-dependent | Mixed workflows |

---

## Examples

```bash
# Interactive mode for local development
/craft:test:cli-run

# Automated mode for CI
/craft:test:cli-run automated

# Test specific CLI command
/craft:test:cli-run --path tests/cli/test_deploy.sh

# Preview automated run
/craft:test:cli-run automated --dry-run
```

---

## See Also

- [/craft:test:run](run.md) — Unified test runner
- [/craft:ci:generate](../ci/generate.md) — CI workflow generation
- [Code & Testing Commands](../code.md) — All testing commands
