# /craft:code:ci-local

> **Run CI checks locally before pushing (lint, test, coverage, security)**

---

## Synopsis

```bash
/craft:code:ci-local [--quick] [--fix] [--verbose] [--only check] [--dry-run|-n]
```

**Quick examples:**

```bash
# Full CI suite
/craft:code:ci-local

# Skip slow checks
/craft:code:ci-local --quick

# Auto-fix issues
/craft:code:ci-local --fix

# Run only tests
/craft:code:ci-local --only tests

# Preview checks
/craft:code:ci-local --dry-run
```

---

## Description

Runs continuous integration checks locally before pushing to catch issues early. Detects CI configuration from `.github/workflows`, `.gitlab-ci.yml`, or other CI files and runs equivalent checks locally. Saves time by identifying failures before they hit remote CI.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--quick` | Skip slow checks (coverage, security) | false |
| `--fix` | Auto-fix issues where possible | false |
| `--verbose` | Show detailed output | false |
| `--only check` | Run specific check only (lint\|test\|coverage\|security\|types\|docs) | - |
| `--dry-run` / `-n` | Preview CI checks without executing | false |

---

## Checks Performed

| Check | Command | Threshold | Est. Time |
|-------|---------|-----------|-----------|
| **Lint** | `/craft:code:lint --strict` | 0 errors | ~3s |
| **Types** | mypy/tsc/etc. | 0 errors | ~45s |
| **Tests** | `/craft:test` | 100% pass | ~15s |
| **Coverage** | `/craft:code:coverage` | 80% minimum | ~20s |
| **Security** | `/craft:code:deps-audit` | No critical | ~8s |
| **Docs** | `/craft:docs:validate` | 0 errors | ~5s |

---

## Execution Strategy

- Runs sequentially with fail-fast enabled
- Stops on first failure
- Quick mode saves ~28 seconds by skipping coverage and security
- Full suite takes ~96 seconds

---

## Output Examples

### Success

```text
Running local CI checks...

[1/6] Lint           ✓ Pass (0 issues)
[2/6] Type check     ✓ Pass (0 errors)
[3/6] Tests          ✓ Pass (42/42)
[4/6] Coverage       ✓ Pass (87% > 80%)
[5/6] Security       ✓ Pass (0 critical)
[6/6] Docs           ✓ Pass (0 errors)

All checks passed! Safe to push.
```

### Failure

```text
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

---

## See Also

- [/craft:code:lint](lint.md) — Code style checks
- [/craft:code:deps-audit](deps-audit.md) — Security audit
- [/craft:check](../check.md) — Pre-flight validation
- [/craft:git:sync](../git/sync.md) — Commit and push with validation
