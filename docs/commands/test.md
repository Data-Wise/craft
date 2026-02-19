# /craft:test

> **Unified test runner with category filtering and execution modes**

---

## Synopsis

```bash
/craft:test [category] [mode] [--path PATH] [--filter PATTERN]
            [--coverage] [--watch] [--dry-run]
```

**Quick examples:**

```bash
/craft:test                         # Run all tests (default mode)
/craft:test unit                    # Unit tests only
/craft:test e2e                     # End-to-end tests only
/craft:test hub                     # Hub domain tests only
/craft:test debug                   # Verbose output with traces
/craft:test unit --filter="auth"    # Unit tests matching "auth"
/craft:test --coverage              # Coverage report
/craft:test --watch                 # Re-run on file changes
/craft:test --dry-run               # Preview execution plan
```

---

## Description

Runs project test suites with category filtering and mode-based execution strategies. Supports pytest markers for tiered execution (unit, integration, e2e) and domain filtering (hub, claude_md, branch_guard, etc.).

Replaces the old `/craft:test:run`, `/craft:test:coverage`, `/craft:test:debug`, and `/craft:test:watch` commands.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `category` | Test category filter (tier or domain marker) | All tests |
| `mode` | Execution mode: `default`, `debug`, `optimize`, `release` | `default` |
| `--path PATH` | Test file or directory to run | `tests/` |
| `--filter PATTERN` | Test name filter (`-k` flag) | All tests |
| `--coverage` | Enable coverage reporting | `false` |
| `--watch` | Re-run tests on file changes | `false` |
| `--dry-run`, `-n` | Preview execution plan without running | `false` |

---

## Modes

| Mode | Budget | pytest Flags | Use Case |
|------|--------|-------------|----------|
| **default** | < 30s | `-x -q --tb=short` | Quick smoke check |
| **debug** | < 120s | `-v --tb=long --capture=no` | Verbose traces |
| **optimize** | < 180s | `-n auto --dist loadfile` | Parallel execution |
| **release** | < 300s | `--cov --cov-report=term -v --maxfail=5` | Full suite + coverage |

---

## Examples

```bash
# Quick validation before commit
/craft:test unit

# Debug a specific failing test
/craft:test debug --filter="test_plugin_json"

# Full pre-release validation
/craft:test release

# Domain-specific during development
/craft:test hub
/craft:test claude_md

# Combined filter
/craft:test "integration and orchestrator" debug

# Run specific file
/craft:test --path tests/test_craft_plugin.py

# Preview what would run
/craft:test release --dry-run
```

---

## See Also

- [/craft:test:gen](test/gen.md) — Generate test suites
- [/craft:test:template](test/template.md) — Manage test templates
- [/craft:check](check.md) — Pre-flight validation
- [Test Commands Reference](../guide/test-commands.md) — Full reference
