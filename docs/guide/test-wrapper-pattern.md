---
title: "Test Wrapper Pattern Guide"
description: "The _check_* + test_* dual-runner pattern used in Craft's test suite"
version: "v2.11.0"
---

# Test Wrapper Pattern

Craft's test suite uses a dual-runner pattern that supports both `pytest`
discovery and standalone execution. This guide explains the pattern and how
to use it when writing tests.

## The Pattern

Every test has two parts:

```python
def _check_feature_works() -> CheckResult:
    """Performs the actual check and returns structured result."""
    import time
    start = time.time()

    # ... check logic ...

    duration = (time.time() - start) * 1000
    return CheckResult("Feature Works", True, duration, "All good", "category")


def test_feature_works():
    """Thin pytest wrapper that asserts on the check result."""
    result = _check_feature_works()
    assert result.passed, result.details
```

## Why This Pattern

### Problem 1: PytestReturnNotNoneWarning

Pytest warns when `test_*` functions return values. Before v2.11.0, test
functions returned `CheckResult` objects, generating 236 warnings:

```
PytestReturnNotNoneWarning: Expected None, but test_feature returned CheckResult
```

### Problem 2: Soft Failures

When tests returned `CheckResult(passed=False)`, pytest treated them as
passing (the function completed without raising). This hid 21 real failures.

### Problem 3: Standalone Runner

Test files double as standalone scripts (`python3 tests/test_file.py`) with
custom reporting. The `_check_*` functions power both modes.

### Solution

Split responsibility:

| Function | Purpose | Returns | Called By |
|----------|---------|---------|-----------|
| `_check_*` | Logic + measurement | `CheckResult` | Both runners |
| `test_*` | Pytest integration | `None` (asserts) | Pytest only |
| `run_all_tests()` | Standalone runner | `List[CheckResult]` | `__main__` |

## CheckResult Dataclass

```python
@dataclass
class CheckResult:
    name: str           # Human-readable check name
    passed: bool        # True if check passed
    duration_ms: float  # Execution time in milliseconds
    details: str        # Description of result
    category: str = "general"  # Grouping category
```

**Important:** Do not name it `TestResult` — pytest will try to collect
classes starting with `Test` and emit `PytestCollectionWarning`.

## Writing New Tests

### Step 1: Define the Check

```python
def _check_config_valid() -> CheckResult:
    """Validate configuration file format."""
    import time
    start = time.time()

    config_path = Path(__file__).parent.parent / "config.json"

    if not config_path.exists():
        return CheckResult(
            "Config Valid", False, 0,
            f"Config not found: {config_path}", "structure"
        )

    try:
        import json
        data = json.loads(config_path.read_text())
    except json.JSONDecodeError as e:
        duration = (time.time() - start) * 1000
        return CheckResult(
            "Config Valid", False, duration,
            f"Invalid JSON: {e}", "structure"
        )

    duration = (time.time() - start) * 1000
    return CheckResult(
        "Config Valid", True, duration,
        f"Valid config with {len(data)} keys", "structure"
    )
```

### Step 2: Add Pytest Wrapper

```python
def test_config_valid():
    """Validate configuration file format."""
    result = _check_config_valid()
    assert result.passed, result.details
```

### Step 3: Register in Standalone Runner

```python
def run_all_tests():
    tests = [
        _check_config_valid,
        # ... other checks ...
    ]
    results = []
    for test_fn in tests:
        result = test_fn()
        results.append(result)
        status = "PASS" if result.passed else "FAIL"
        print(f"  {status} ({result.duration_ms:.1f}ms) - {result.details}")
    return results
```

## Special Cases

### Skipping When Tools Missing

When a check depends on an external tool (e.g., `mkdocs`), skip instead of
failing:

```python
def test_mkdocs_build():
    result = _check_mkdocs_build()
    if 'not found' in result.details:
        pytest.skip(result.details)
    assert result.passed, result.details
```

### Threshold-Based Assertions

Use minimum thresholds instead of exact counts for resilience:

```python
# Fragile — breaks when commands are added
if len(commands) != 97:
    return CheckResult("Command Count", False, ...)

# Resilient — only fails if something is drastically wrong
if len(commands) < 95:
    return CheckResult("Command Count", False, ...)
```

### Class Naming

Avoid prefixing classes with `Test` unless they are actual pytest test
classes:

```python
# BAD — pytest tries to collect this as a test class
class TestResult:
    ...

# GOOD — clear it's a data container
class CheckResult:
    ...

# BAD — pytest collects but finds no test_ methods
class TestE2EWorkflows:
    ...

# GOOD — helper class, not a test class
class E2EWorkflows:
    ...
```

## File Template

```python
#!/usr/bin/env python3
"""
Test Suite for [Feature Name]
=============================
Run with: pytest tests/test_feature.py -v
"""

import time
from dataclasses import dataclass
from pathlib import Path

import pytest


@dataclass
class CheckResult:
    name: str
    passed: bool
    duration_ms: float
    details: str
    category: str = "general"


def _check_example() -> CheckResult:
    start = time.time()
    # ... logic ...
    duration = (time.time() - start) * 1000
    return CheckResult("Example", True, duration, "OK", "unit")


def test_example():
    result = _check_example()
    assert result.passed, result.details


def run_all_tests():
    tests = [_check_example]
    results = []
    for fn in tests:
        result = fn()
        results.append(result)
        status = "PASS" if result.passed else "FAIL"
        print(f"  {status} ({result.duration_ms:.1f}ms) - {result.details}")
    return results


if __name__ == "__main__":
    results = run_all_tests()
    passed = sum(1 for r in results if r.passed)
    print(f"\n{passed}/{len(results)} passed")
    exit(0 if passed == len(results) else 1)
```

## Impact

The v2.11.0 refactoring applied this pattern across 13 test files:

| Metric | Before | After |
|--------|--------|-------|
| Tests | 847 | 1111 |
| Warnings | 236 | 0 |
| Hidden failures | 21 | 0 |
| Dual-runner support | Partial | Full |
