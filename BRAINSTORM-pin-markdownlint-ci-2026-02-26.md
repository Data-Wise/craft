# BRAINSTORM: Pin markdownlint-cli2 in CI

**Date:** 2026-02-26
**Depth:** deep | **Focus:** feature
**Duration:** ~8 min (10 questions)

---

## Problem Statement

`npx -y markdownlint-cli2` downloads the package fresh every CI run. npm's registry occasionally returns HTTP 403 (rate-limiting or geo-blocking on GitHub Actions runners), causing the entire CI pipeline to fail even though the code is correct.

**Impact:** This hit craft during the v2.28.0 release -- initial CI on main failed, re-run passed. It's infrastructure flakiness masquerading as test failure.

**Root cause:** 5 separate systems all use `npx -y markdownlint-cli2` independently:

| System | File | Occurrences |
|--------|------|-------------|
| CI docs-quality | `.github/workflows/docs-quality.yml:42` | 1 (npm install) + 1 (npx) |
| Pre-commit hook | `scripts/hooks/pre-commit-markdownlint.sh` | 3 |
| Docs lint script | `scripts/docs-lint.sh` | 2 (fallback path) |
| Unit tests | `tests/test_markdownlint_list_spacing_unit.py` | 14 |
| E2E tests | `tests/test_markdownlint_list_spacing_e2e.py` | 10 |
| Validation tests | `tests/test_markdownlint_list_spacing_validation.py` | 4 |
| Utils | `utils/docs_update_orchestrator.py` | 1 |

**Total:** ~35 occurrences of `npx -y markdownlint-cli2` or similar across the codebase.

---

## Current State

### What exists

- `package.json` already has `markdownlint-cli2` as a devDependency (`^0.14.0`)
- `package-lock.json` exists locally but is gitignored
- `node_modules/` exists locally (gitignored)
- `.pre-commit-config.yaml` pins to `rev: v0.14.0` (its own install)
- CI docs-quality.yml does `npm install --save-dev markdownlint-cli2` (installs from scratch each time)
- CI ci.yml does NOT set up Node.js at all

### What's broken

1. **CI flakiness:** `npx -y` downloads from npm registry every run -- 403s cause spurious failures
2. **No lockfile in git:** `npm ci` can't work without `package-lock.json` committed
3. **Version drift:** `^0.14.0` could resolve to different versions across environments
4. **Redundant installs:** pre-commit, CI, and tests all install independently
5. **No npm cache:** CI doesn't cache node_modules or npm global cache

---

## Decisions Made (from questions)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Pin strategy | package.json devDependency | Locks version, cached by Actions, works for CI + local |
| Scope | CI + local (all systems) | Consistent behavior everywhere |
| Hook update | Yes - use local npx | Hook uses local install, no -y download |
| Test update | Yes - all 28+ subprocess calls | Tests use local binary, no npm 403 risk |
| npm command | `npm ci` | Deterministic, uses lockfile exactly |
| CI scope | Both ci.yml and docs-quality.yml | Consistent setup across all workflows |
| Lint enforcement | Keep continue-on-error: true | Pre-commit catches issues locally |
| Lockfile | Commit package-lock.json | Required for `npm ci` |
| docs-lint.sh | Local first, global, then npx | Most reliable resolution order |
| Version pin | Exact: `0.14.0` | Maximum reproducibility, matches pre-commit rev |

---

## Quick Wins (< 30 min each)

1. **Pin exact version in package.json** -- Change `"^0.14.0"` to `"0.14.0"` and commit `package-lock.json`
2. **Update docs-quality.yml** -- Replace `npm install --save-dev` with `npm ci`, add npm cache
3. **Update ci.yml** -- Add Node.js setup with npm cache for markdownlint tests
4. **Remove -y from pre-commit hook** -- Use `npx markdownlint-cli2` (local resolution)

## Medium Effort (1-2 hours)

5. **Update all test files** -- Replace 28+ `npx -y markdownlint-cli2` calls with `npx markdownlint-cli2`
6. **Update docs-lint.sh** -- Add local node_modules/.bin/ as first resolution path
7. **Update utils/docs_update_orchestrator.py** -- Use local binary

## Long-term (Future sessions)

8. **Consider GitHub Actions markdownlint action** -- `avto-dev/markdown-lint@v1` or similar (eliminates npm entirely)
9. **Dependabot for npm deps** -- Auto-PR when markdownlint-cli2 updates

---

## Architecture

### Resolution Priority Chain

```
Caller (CI/hook/test/script)
  │
  ├─ 1. ./node_modules/.bin/markdownlint-cli2 (local install via npm ci)
  ├─ 2. $(which markdownlint-cli2) (global install)
  └─ 3. npx -y markdownlint-cli2 (download fallback -- LAST RESORT)
```

### File Change Map

```
package.json                          Pin "0.14.0" (exact)
package-lock.json                     Commit to git (remove from .gitignore if present)
.github/workflows/ci.yml             Add Node.js setup + npm ci + cache
.github/workflows/docs-quality.yml   Replace npm install with npm ci + cache
scripts/hooks/pre-commit-markdownlint.sh  Remove -y flag, use local npx
scripts/docs-lint.sh                  Add local node_modules check first
tests/test_markdownlint_list_spacing_unit.py       Remove -y (14 calls)
tests/test_markdownlint_list_spacing_e2e.py        Remove -y (10 calls)
tests/test_markdownlint_list_spacing_validation.py Remove -y (4 calls)
utils/docs_update_orchestrator.py     Remove -y (1 call)
```

### CI Workflow Changes

**docs-quality.yml:**

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'

- name: Install dependencies
  run: npm ci

- name: Run markdown linting
  run: npx markdownlint-cli2 "docs/**/*.md" "README.md" "CLAUDE.md" --config .markdownlint.json
  continue-on-error: true
```

**ci.yml (new steps before test suite):**

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'

- name: Install npm dependencies
  run: npm ci
```

### Pre-commit Hook Change

**Before:**

```bash
VIOLATIONS=$(npx -y markdownlint-cli2 $STAGED_MD_FILES 2>&1 || true)
```

**After:**

```bash
VIOLATIONS=$(npx markdownlint-cli2 $STAGED_MD_FILES 2>&1 || true)
```

The `-y` flag means "yes, download if not found." Without it, `npx` checks `./node_modules/.bin/` first (the local install), which is always available after `npm install`.

### Test File Change Pattern

**Before (every subprocess call):**

```python
["npx", "-y", "markdownlint-cli2", temp_path]
```

**After:**

```python
["npx", "markdownlint-cli2", temp_path]
```

### docs-lint.sh Change

**Before:**

```bash
if command -v markdownlint-cli2 &>/dev/null; then
    echo "markdownlint-cli2"
else
    echo "npx markdownlint-cli2"
fi
```

**After:**

```bash
if [ -x "./node_modules/.bin/markdownlint-cli2" ]; then
    echo "./node_modules/.bin/markdownlint-cli2"
elif command -v markdownlint-cli2 &>/dev/null; then
    echo "markdownlint-cli2"
else
    echo "npx markdownlint-cli2"
fi
```

---

## Implementation Order

| # | Deliverable | Effort | Risk | Dependencies |
|---|-------------|--------|------|--------------|
| 1 | Pin exact version + commit lockfile | 10 min | Low | None |
| 2 | Update docs-quality.yml (npm ci + cache) | 10 min | Low | 1 |
| 3 | Update ci.yml (add Node.js + npm ci) | 10 min | Low | 1 |
| 4 | Update pre-commit hook (remove -y) | 5 min | Low | 1 |
| 5 | Update docs-lint.sh (local-first resolution) | 10 min | Low | 1 |
| 6 | Update test files (28+ calls) | 15 min | Low | 1 |
| 7 | Update utils/docs_update_orchestrator.py | 5 min | Low | 1 |
| 8 | Run full test suite to verify | 5 min | Low | All above |

**Total:** ~70 min (1 session)

---

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Pin mechanism | package.json devDep (exact) | Deterministic, cacheable, works everywhere |
| Commit lockfile | Yes | Required for `npm ci`, standard practice |
| npm command | `npm ci` | Faster, deterministic, fails on lockfile mismatch |
| Resolution order | local > global > npx -y | Most reliable, eliminates network dependency |
| Remove -y flag | Yes (all files) | Forces local resolution, no surprise downloads |
| CI cache | actions/setup-node cache: 'npm' | Built-in, zero config npm cache |

---

## Open Questions

1. **Should .gitignore be updated?** -- `package-lock.json` might be in `.gitignore` (needs check). If so, remove the rule.
2. **Pre-commit still downloads independently** -- `.pre-commit-config.yaml` uses `repo: https://github.com/DavidAnson/markdownlint-cli2` which downloads its own copy. This is fine (pre-commit manages its own virtualenvs) but means two copies exist. Not worth changing.
3. **Homebrew formula impact** -- Does the formula use markdownlint? No -- it only installs craft plugin files. No impact.

---

## Related Artifacts

- Memory entry: "npm Registry Flakiness in GitHub Actions CI" (saved 2026-02-26)
- CI workflow: `.github/workflows/ci.yml`
- CI workflow: `.github/workflows/docs-quality.yml`
- Pre-commit hook: `scripts/hooks/pre-commit-markdownlint.sh`
- Test files: `tests/test_markdownlint_list_spacing_*.py`
