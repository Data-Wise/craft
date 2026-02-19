---
description: Run CI checks locally before pushing (lint, test, coverage, security)
category: code
arguments:
  - name: quick
    description: Skip slow checks (coverage, security)
    required: false
    default: false
  - name: fix
    description: Auto-fix issues where possible
    required: false
    default: false
  - name: verbose
    description: Show detailed output
    required: false
    default: false
  - name: only
    description: Run specific check only (lint|test|coverage|security|types|docs)
    required: false
  - name: dry-run
    description: Preview CI checks without executing them
    required: false
    default: false
    alias: -n
---

# /craft:code:ci-local - Run CI Locally

Run continuous integration checks locally before pushing.

## Usage

```bash
/craft:code:ci-local                    # Full CI suite
/craft:code:ci-local --quick            # Skip slow checks
/craft:code:ci-local --fix              # Auto-fix issues
/craft:code:ci-local --only tests       # Run specific check
/craft:code:ci-local --dry-run          # Preview checks
/craft:code:ci-local --quick -n         # Preview quick mode
```

## Dry-Run Mode

Preview CI checks that will be performed:

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Local CI Checks                                   │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ CI Configuration Detected:                                  │
│   - Source: .github/workflows/ci.yml                          │
│   - Jobs: lint, test, security                                │
│   - Python versions: 3.10, 3.11, 3.12                         │
│                                                               │
│ ✓ Local CI Suite (6 checks):                                  │
│                                                               │
│   [1/6] Linting                                               │
│       Command: /craft:code:lint --strict                      │
│       Tool: ruff check .                                      │
│       Threshold: 0 errors                                     │
│       Estimated: ~3 seconds                                   │
│                                                               │
│   [2/6] Type Checking                                         │
│       Command: mypy src/                                      │
│       Config: pyproject.toml                                  │
│       Threshold: 0 type errors                                │
│       Estimated: ~45 seconds                                  │
│                                                               │
│   [3/6] Tests                                                 │
│       Command: /craft:test                                    │
│       Tool: pytest                                            │
│       Threshold: 100% pass (135 tests)                        │
│       Estimated: ~15 seconds                                  │
│                                                               │
│   [4/6] Coverage                                              │
│       Command: /craft:code:coverage                           │
│       Tool: pytest --cov                                      │
│       Threshold: 80% minimum                                  │
│       Estimated: ~20 seconds                                  │
│                                                               │
│   [5/6] Security Audit                                        │
│       Command: /craft:code:deps-audit                         │
│       Tool: pip-audit                                         │
│       Threshold: No critical vulnerabilities                  │
│       Estimated: ~8 seconds                                   │
│                                                               │
│   [6/6] Documentation                                         │
│       Command: /craft:docs:validate                           │
│       Checks: Links, syntax, completeness                     │
│       Threshold: 0 errors                                     │
│       Estimated: ~5 seconds                                   │
│                                                               │
│ ✓ Execution Strategy:                                         │
│   - Run sequentially (fail-fast enabled)                      │
│   - Stop on first failure                                     │
│   - Total estimated time: ~96 seconds                         │
│                                                               │
│ ⚠ Notes:                                                      │
│   • Quick mode skips [4] Coverage and [5] Security (~28s)    │
│   • Fix mode adds --fix flag to lint command                  │
│   • Results match CI environment (GitHub Actions)             │
│                                                               │
│ 📊 Summary: 6 checks, ~96 seconds total                       │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

### Quick Mode Dry-Run

```bash
/craft:code:ci-local --quick --dry-run
```

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Local CI Checks (Quick Mode)                      │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Quick Mode: Skipping slow checks                            │
│   - Skipped: Coverage (~20s)                                  │
│   - Skipped: Security (~8s)                                   │
│                                                               │
│ ✓ Checks to Run (4):                                          │
│   [1/4] Linting (~3s)                                         │
│   [2/4] Type Checking (~45s)                                  │
│   [3/4] Tests (~15s)                                          │
│   [4/4] Documentation (~5s)                                   │
│                                                               │
│ 📊 Total time: ~68 seconds (28s saved)                        │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

**Note**: Dry-run shows the CI check plan without executing any commands. Use this to understand what will run before committing time to the full suite.

## What This Does

1. **Detects CI configuration** (.github/workflows, .gitlab-ci.yml, etc.)
2. **Runs equivalent checks** locally
3. **Reports failures** before they hit remote CI
4. **Saves time** by catching issues early

## Checks Performed

| Check | Command | Threshold |
|-------|---------|-----------|
| Lint | `/craft:code:lint --strict` | 0 errors |
| Tests | `/craft:test` | 100% pass |
| Coverage | `/craft:code:coverage` | 80% minimum |
| Security | `/craft:code:deps-audit` | No critical |
| Types | mypy/tsc/etc. | 0 errors |
| Docs | `/craft:docs:validate` | 0 errors |

## Options

- `--quick` - Skip slow checks (coverage, security)
- `--fix` - Auto-fix issues where possible
- `--verbose` - Show detailed output
- `--only <check>` - Run specific check only

## Examples

```bash
# Full CI check
/craft:code:ci-local

# Quick check before commit
/craft:code:ci-local --quick

# Fix issues automatically
/craft:code:ci-local --fix

# Run only tests
/craft:code:ci-local --only tests
```

## Output

```
Running local CI checks...

[1/6] Lint           ✓ Pass (0 issues)
[2/6] Type check     ✓ Pass (0 errors)
[3/6] Tests          ✓ Pass (42/42)
[4/6] Coverage       ✓ Pass (87% > 80%)
[5/6] Security       ✓ Pass (0 critical)
[6/6] Docs           ✓ Pass (0 errors)

All checks passed! Safe to push.
```

## Failure Output

```
Running local CI checks...

[1/6] Lint           ✗ Fail (3 issues)
  src/main.py:15 - trailing whitespace
  src/api.py:42 - line too long

[2/6] Tests          ✗ Fail (40/42)
  FAILED test_auth.py::test_login
  FAILED test_auth.py::test_logout

2 checks failed. Fix before pushing.
Run with --fix to auto-fix lint issues.
```

## Integration

Works with:

- `/craft:code:ci-fix` - Fix CI failures
- `/craft:git:sync` - Pre-push validation
