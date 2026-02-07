# Test Conventions

Patterns used across Craft's test suite (1380 tests, 13+ test files).

## The `_check_*` + `test_*` Pattern

Every test is split into two functions:

```python
def _check_feature_works() -> CheckResult:
    """Performs the actual check. Returns structured result."""
    start = time.time()
    # ... check logic ...
    duration = (time.time() - start) * 1000
    return CheckResult("Feature Works", True, duration, "details")

def test_feature_works():
    """Thin pytest wrapper. Asserts on the check result."""
    result = _check_feature_works()
    assert result.passed, result.details
```

**Why:** Separates check logic from assertion. Provides timing, details, and categories. Supports both `pytest` discovery and standalone `python3 tests/test_foo.py` execution.

## CheckResult Contract

```python
@dataclass
class CheckResult:
    name: str           # Human-readable check name
    passed: bool        # True if check passed
    duration_ms: float  # Execution time in milliseconds
    details: str        # Description of result
    category: str = "general"  # Grouping category
```

Each test file defines its own `CheckResult` (not shared). The `category` default varies by file (e.g., `"dogfood"`, `"integration"`, `"adhd"`).

## Pytest Rules

- **No return values** from `test_*` functions (triggers `PytestReturnNotNoneWarning`)
- **No test collection from classes** — use module-level `test_*` functions only
- **Warning-free** — all 236 legacy warnings were eliminated in v2.11.0

## File Naming

| Pattern | Purpose | Example |
|---------|---------|---------|
| `test_<feature>.py` | Unit/feature tests | `test_brainstorm_phase1.py` |
| `test_integration_<system>.py` | Integration tests | `test_integration_dependency_system.py` |
| `test_<feature>_e2e.py` | End-to-end tests | `test_command_enhancements_e2e.py` |
| `test_<tool>.sh` | Shell-based tests | `test_dependency_management.sh` |

## Full Guide

-> Complete pattern guide: [test-wrapper-pattern.md](../guide/test-wrapper-pattern.md)
