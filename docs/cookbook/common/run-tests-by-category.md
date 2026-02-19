---
title: "Run Tests by Category"
description: "Filter and run tests by tier, domain, or combination using pytest markers"
category: "cookbook"
level: "beginner"
time_estimate: "3 minutes"
related:
  - guide/test-commands.md
  - tutorials/testing-quickstart.md
---

# Run Tests by Category

## Problem

You want to run only a subset of tests — fast ones during development, or domain-specific ones when working on a feature.

## Solution

### By tier (speed)

```bash
/craft:test smoke           # < 30s total, quick validation
/craft:test unit             # Pure function tests, < 2s each
/craft:test integration      # Subprocess/filesystem, < 10s each
/craft:test e2e              # Full workflows, < 60s each
```

### By domain (feature area)

```bash
/craft:test hub              # Hub discovery tests
/craft:test branch_guard     # Branch protection
/craft:test claude_md        # CLAUDE.md sync/audit
/craft:test commands         # Command parsing
/craft:test release          # Release pipeline
```

### Combined filters

```bash
/craft:test "unit and hub"             # Unit tests for hub only
/craft:test "integration and not slow" # Fast integration tests
/craft:test "e2e and branch_guard"     # Branch guard e2e only
```

## Explanation

Tests use **pytest markers** defined in `pyproject.toml`. Every test file has a module-level `pytestmark`:

```python
pytestmark = [pytest.mark.unit, pytest.mark.hub]
```

The `/craft:test` command translates category arguments into `-m` flags for pytest.

## Variations

### With debug output

```bash
/craft:test unit debug       # Verbose output for unit tests
```

### With coverage

```bash
/craft:test unit --coverage  # Unit tests with coverage report
```

### Specific file

```bash
/craft:test --path tests/test_hub.py
```

### Name pattern filter

```bash
/craft:test --filter "test_discover"   # Tests matching pattern
```

## Related

- [Testing Quickstart](../../tutorials/testing-quickstart.md)
- [Test Commands Reference](../../guide/test-commands.md)
