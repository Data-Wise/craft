# /craft:test:run

> **Unified test runner with mode-based execution strategies**

---

## Synopsis

```bash
/craft:test:run [mode] [--filter PATTERN] [--path PATH] [--dry-run]
```

**Quick examples:**

```bash
# Quick smoke tests (< 30s)
/craft:test:run

# Verbose debugging (< 120s)
/craft:test:run debug

# Full release validation (< 300s)
/craft:test:run release --filter auth
```

---

## Description

Runs project test suites with intelligent mode selection for different scenarios. Supports Python (pytest, unittest), JavaScript (jest, vitest), and shell scripts. Automatically detects test frameworks and applies mode-specific timeouts, parallelization, and verbosity settings.

Modes are optimized for different workflows: quick feedback during development (default), deep debugging (debug), performance optimization (optimize), and thorough pre-release validation (release).

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `mode` | Execution mode: `default`, `debug`, `optimize`, `release` | `default` |
| `--filter PATTERN` | Run only tests matching pattern | All tests |
| `--path PATH` | Test file or directory to run | Auto-detect |
| `--dry-run`, `-n` | Show what would run without executing | `false` |

---

## Modes

| Mode | Timeout | Use Case |
|------|---------|----------|
| `default` | < 30s | Quick smoke tests during development |
| `debug` | < 120s | Verbose traces with detailed error output |
| `optimize` | < 180s | Parallel execution for performance testing |
| `release` | < 300s | Full suite with coverage and all checks |

---

## Examples

```bash
# Run all tests with default mode
/craft:test:run

# Debug specific test file
/craft:test:run debug --path tests/test_auth.py

# Optimize mode with pattern filter
/craft:test:run optimize --filter "integration"

# Preview release tests
/craft:test:run release --dry-run
```

---

## See Also

- [/craft:test:cli-run](cli-run.md) — CLI-specific test runner
- [/craft:check](../check.md) — Pre-flight validation
- [Code & Testing Commands](../code.md) — All testing commands
