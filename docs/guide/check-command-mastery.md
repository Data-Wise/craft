# Check Command Mastery Guide

> **Master the `/craft:check` command to prevent issues before they reach CI** — Learn when to use each mode, how to integrate with workflows, and troubleshooting strategies.

---

## Overview

The `/craft:check` command is your local pre-flight validation system. It detects your project type and runs the right combination of lint, test, and security checks **before** you commit, create a PR, or deploy.

**Core philosophy:** Catch issues locally in 10 seconds rather than waiting 5 minutes for CI to fail.

---

## Decision Framework

### When to Run Which Mode

```
Task: About to commit
├─ Quick commit (1-3 files changed)
│   → /craft:check
│   Time: ~8 seconds
│
├─ Medium commit (4-10 files changed)
│   → /craft:check --for commit
│   Time: ~15 seconds
│
└─ Large refactor (10+ files changed)
    → /craft:check thorough --for commit
    Time: ~40 seconds
```

```
Task: Creating a pull request
├─ Draft PR (work in progress)
│   → /craft:check --for pr
│   Time: ~25 seconds
│
└─ Final PR (ready for review)
    → /craft:check thorough --for pr
    Time: ~60 seconds
```

```
Task: Preparing a release
└─ Always use full validation
    → /craft:check thorough --for release
    Time: ~90 seconds (comprehensive)
```

### Mode Selection Quick Reference

| Scenario | Command | Why |
|----------|---------|-----|
| **Quick sanity check** | `/craft:check` | Fast validation (8-10s), catches obvious issues |
| **Before committing** | `/craft:check --for commit` | Prevents bad commits, checks git status + lint + tests |
| **Before creating PR** | `/craft:check --for pr` | Comprehensive, matches what CI will run |
| **Before releasing** | `/craft:check thorough --for release` | Full audit including security, docs, version sync |
| **Before deploying** | `/craft:check thorough --for deploy` | Release checks + environment validation |
| **CI simulation** | `/craft:code:ci-local` | Exact CI environment replication |

---

## Scenario Library

### Scenario 1: Pre-Commit — Fast Validation

**Workflow:**

```bash
# You've changed 3 files
git status
# modified: src/auth.py
# modified: tests/test_auth.py
# modified: docs/api.md

# Quick check before committing
/craft:check
```

**What runs (default mode):**

```
Pre-flight Check Plan:
  Project: myapp (Python)
  Mode: default
  Files changed: 3

  Checks to run:
  1. Git status (clean working tree?)
  2. Lint (ruff on 3 changed files)
  3. Tests (pytest --fail-fast)

? Run these pre-flight checks?
  › Yes - Run all (Recommended)

  [1/3] Git status... clean
  [2/3] Lint (3 files)... 0 issues
  [3/3] Tests... 47/47 passed

  Results: 3/3 checks passed
  Time: 8.2s
  Next steps: Ready to commit
```

**Time saved:** CI would take ~2 minutes. You found issues in 8 seconds.

### Scenario 2: Pre-PR — Comprehensive Without Externals

**Workflow:**

```bash
# Feature complete, ready to create PR
git log origin/dev..HEAD
# 7 commits since branching from dev

# Run PR checks
/craft:check --for pr
```

**What runs (PR context):**

```
Pre-flight Check Plan:
  Project: myapp (Python)
  Mode: default
  Context: pr (pre-PR validation)
  Branch: feature/add-auth (7 commits ahead of dev)

  Checks to run (8 for PR context):
  1. Git status (ahead of dev?)
  2. Lint (all files)
  3. Unit tests (full suite)
  4. Type check (mypy)
  5. Security advisory (pip-audit)
  6. Internal link validation
  7. Merge conflict detection
  8. Coverage threshold (80% minimum)

? Run these pre-flight checks?
  › Yes - Run all (Recommended)
    Skip security (faster)
    Skip type check (faster)
    Dry run (show commands only)
```

**Execution:**

```
[1/8] Git status... 7 commits ahead of dev ✓
[2/8] Lint (all 47 files)... 0 issues ✓
[3/8] Unit tests... 152/152 passed ✓
[4/8] Type check... no type errors ✓
[5/8] Security... 0 vulnerabilities ✓
[6/8] Internal links... 47 links checked, 0 broken ✓
[7/8] Merge conflicts... none detected ✓
[8/8] Coverage... 85% (target: 80%) ✓

Results: 8/8 checks passed
Time: 24.7s
Issues: 0
Next steps: Create PR (gh pr create)
```

**Why this matters:** All PR checks passed locally. CI will pass on first try.

### Scenario 3: Pre-Release — Full Audit Mode

**Workflow:**

```bash
# Preparing v2.9.0 release
git checkout dev
git pull origin dev

# Full validation before release
/craft:check thorough --for release
```

**What runs (release context + thorough mode):**

```
Pre-flight Check Plan:
  Project: craft (Claude Plugin)
  Mode: thorough (comprehensive)
  Context: release (pre-release audit)
  Target version: v2.9.0

  Checks to run (12 for release context):
  1. Git status (clean + tagged?)
  2. Lint (all files, strict rules)
  3. Unit tests (full suite + coverage report)
  4. Integration tests
  5. Type check (strict mode)
  6. Security audit (full)
  7. Documentation validation
  8. Internal + external link validation
  9. Version sync audit (v2.9.0 across all files)
  10. Changelog entry exists
  11. Release notes present
  12. Tag existence check
```

**Execution with detailed output:**

```
[1/12] Git status...
  ✓ Working tree clean
  ✓ All changes committed
  ✓ Branch: dev (synced with origin)
  ⚠ Tag v2.9.0 does not exist yet

[2/12] Lint (153 files, strict)...
  ✓ Python: 0 issues (ruff --select ALL)
  ✓ Markdown: 0 issues (30 rules)
  ✓ YAML: 0 issues

[3/12] Unit tests (full + coverage)...
  ✓ 1294 tests passed
  ✓ Coverage: 92% (all modules > 80%)
  Report: htmlcov/index.html

[4/12] Integration tests...
  ✓ 38 integration tests passed
  ✓ End-to-end workflows validated

[5/12] Type check (strict)...
  ✓ mypy: no type errors
  ✓ strict mode enabled

[6/12] Security audit...
  ✓ pip-audit: 0 vulnerabilities
  ✓ No known CVEs in dependencies

[7/12] Documentation validation...
  ✓ All command docs present (108 commands)
  ✓ All help files valid YAML
  ✓ mkdocs builds without warnings

[8/12] Link validation (internal + external)...
  ✓ Internal: 847 links, 0 broken
  ⚠ External: 12 links, 2 unreachable (timeout)

[9/12] Version sync audit...
  ✓ CLAUDE.md: v2.9.0
  ✓ .STATUS: v2.9.0
  ✓ docs/index.md: v2.9.0
  ✓ mkdocs.yml: v2.9.0
  All 47 version references match ✓

[10/12] Changelog entry...
  ✓ CHANGELOG.md has ## [2.9.0] section
  ✓ Release date: 2026-01-29

[11/12] Release notes...
  ✓ docs/RELEASE-v2.9.0.md exists
  ✓ Contains features, fixes, documentation

[12/12] Tag check...
  ⚠ Tag v2.9.0 not found (run: git tag v2.9.0)

Results: 10/12 checks passed, 2 warnings
Time: 87.3s
Issues: 2 warnings (external links timeout, tag missing)

Warnings summary:
  • 2 external links unreachable (non-blocking)
  • Tag v2.9.0 not created yet

Next steps:
  1. Create release tag: git tag v2.9.0
  2. Push tag: git push origin v2.9.0
  3. Create GitHub release: gh release create v2.9.0
```

**Why this matters:** Every release criterion verified. No surprises during deployment.

### Scenario 4: CI Simulation — Match GitHub Actions

**Workflow:**

```bash
# Want to replicate exact CI environment locally
/craft:code:ci-local
```

This runs the EXACT commands from `.github/workflows/ci.yml` in the same order, with the same flags.

**What it does differently from `/craft:check`:**

| Aspect | `/craft:check thorough --for pr` | `/craft:code:ci-local` |
|--------|--------------------------------|----------------------|
| Environment | Local env | CI-like (isolated) |
| Commands | Optimized for speed | Exact CI commands |
| Dependencies | Use local installs | Fresh install (optional) |
| Cache | Uses local cache | Simulates CI cache |
| Output | Formatted summaries | Raw CI output |

**When to use CI simulation:**

- CI is failing but local checks pass
- Dependency version mismatch suspected
- Debugging flaky tests in CI
- Validating CI workflow changes

---

## Mode Combinations Deep Dive

### Understanding Mode × Context Matrix

The command has two dimensions:

1. **Mode** (depth of checks): `default` or `thorough`
2. **Context** (which checks run): `--for commit|pr|release|deploy`

**Combined effect:**

| Command | Lint Depth | Test Depth | Security | Links | Time |
|---------|-----------|-----------|---------|-------|------|
| `/craft:check` | Changed files | Fail-fast | Skip | Skip | ~8s |
| `/craft:check --for commit` | Changed files | Full suite | Skip | Skip | ~15s |
| `/craft:check --for pr` | All files | Full suite | Advisory | Internal | ~25s |
| `/craft:check thorough` | All files (strict) | Full + coverage | Skip | Skip | ~40s |
| `/craft:check thorough --for pr` | All files (strict) | Full + coverage | Full audit | Internal + external | ~60s |
| `/craft:check thorough --for release` | All files (strict) | Full + coverage + integration | Full audit | Internal + external | ~90s |

### Example: Same Project, Different Modes

**Project:** Python web app (152 tests, 47 files)

**Mode 1: Default (no flags)**

```
Checks: Git status, lint (3 changed files), tests (fail-fast)
Time: 8.2s
```

**Mode 2: --for commit**

```
Checks: Git status, lint (all 47 files), tests (full suite)
Time: 15.1s
```

**Mode 3: --for pr**

```
Checks: Git status, lint (all files), tests (full), types, security, links, merge
Time: 24.7s
```

**Mode 4: thorough --for pr**

```
Checks: All from --for pr, but with strict rules, coverage report, external links
Time: 61.4s
```

**Mode 5: thorough --for release**

```
Checks: All from thorough --for pr, plus integration tests, version sync, changelog, release notes
Time: 87.3s
```

---

## Performance vs Thoroughness Trade-Offs

### Time Budget Analysis

| Time Available | Recommended Mode | Coverage |
|---------------|-----------------|----------|
| **< 10 seconds** | `/craft:check` | Basic validation (git, lint changed, tests fail-fast) |
| **10-20 seconds** | `/craft:check --for commit` | Commit-ready (git, lint all, tests full) |
| **20-40 seconds** | `/craft:check --for pr` | PR-ready (+ types, security, links) |
| **40-70 seconds** | `/craft:check thorough --for pr` | PR-ready strict (+ coverage, external links) |
| **70-120 seconds** | `/craft:check thorough --for release` | Release-ready (+ integration, version sync, docs) |

### Parallelization Strategies

Some checks can run in parallel to save time:

**Sequential (current):**

```
[1] Git status → [2] Lint → [3] Tests → [4] Types → [5] Security
Total: 24s
```

**Parallel (if implemented):**

```
[1] Git status (2s)
[2] Lint (8s) ║ Tests (12s) ║ Types (6s)
[3] Security (3s)
Total: 15s (39% faster)
```

**Current workaround** — Run checks manually in parallel terminals:

```bash
# Terminal 1
/craft:code:lint &

# Terminal 2
/craft:test:run &

# Terminal 3
mypy . &

# Wait for all
wait
```

---

## Integration Patterns

### Git Hooks Integration

#### Pre-Commit Hook

```bash
# .git/hooks/pre-commit

#!/bin/bash
echo "Running pre-commit checks..."

# Run craft check
if ! claude-code run "/craft:check --for commit"; then
  echo "❌ Pre-commit checks failed. Commit aborted."
  echo "Fix issues or use 'git commit --no-verify' to skip."
  exit 1
fi

echo "✅ Pre-commit checks passed."
exit 0
```

#### Pre-Push Hook

```bash
# .git/hooks/pre-push

#!/bin/bash
echo "Running pre-push checks..."

# Determine target branch
current_branch=$(git branch --show-current)

if [[ "$current_branch" == "main" || "$current_branch" == "dev" ]]; then
  # Full validation for protected branches
  claude-code run "/craft:check thorough --for pr"
else
  # Quick validation for feature branches
  claude-code run "/craft:check --for pr"
fi

if [ $? -ne 0 ]; then
  echo "❌ Pre-push checks failed. Push aborted."
  exit 1
fi

echo "✅ Pre-push checks passed."
exit 0
```

### CI/CD Pipeline Equivalents

Map local checks to CI jobs:

| Local Command | GitHub Actions Equivalent |
|--------------|---------------------------|
| `/craft:check --for commit` | `lint` and `test` jobs |
| `/craft:check --for pr` | Full `ci.yml` workflow |
| `/craft:check thorough --for release` | `release-validation.yml` |
| `/craft:code:ci-local` | Exact `ci.yml` replication |

**Example workflow integration:**

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install craft
        run: pip install craft-plugin
      - name: Run checks
        run: craft check --for pr
```

### Pre-Push Validation Workflow

**Daily development loop:**

```bash
# Morning: Start work
cd ~/.git-worktrees/project/feature-auth
claude

# Midday: Commit work in progress
git add .
git commit -m "wip: auth implementation"
# Pre-commit hook runs: /craft:check --for commit (15s)

# Afternoon: More commits
git add .
git commit -m "feat: complete OAuth flow"
# Pre-commit hook runs again

# End of day: Push to remote
git push origin feature-auth
# Pre-push hook runs: /craft:check --for pr (25s)
```

**Benefit:** Every push is validated. CI rarely fails.

---

## Troubleshooting Matrix

### Lint Failures → Auto-Fix Workflow

**Error:**

```
[2/3] Lint... ❌ FAILED
  src/auth.py:42:1: E501 line too long (92 > 88 characters)
  src/auth.py:67:5: F401 'os' imported but unused
  tests/test_auth.py:12:1: E302 expected 2 blank lines, found 1
```

**Solution:**

```bash
# Auto-fix formatting issues
/craft:code:lint --fix

# Re-run check
/craft:check
```

**Result:**

```
Auto-fixing lint issues...
  ✓ Formatted src/auth.py (line length fixed)
  ✓ Removed unused import 'os'
  ✓ Added blank line in tests/test_auth.py

[2/3] Lint... ✅ PASSED (0 issues)
```

### Test Failures → Debugging Strategy

**Error:**

```
[3/3] Tests... ❌ FAILED
  FAILED tests/test_auth.py::test_login_success - AssertionError
  152 passed, 1 failed
```

**Solution:**

```bash
# Run tests with verbose output
/craft:test:run --verbose tests/test_auth.py::test_login_success

# Or use debug mode for full output
/craft:check debug
```

**Debug mode shows:**

```
[3/3] Tests (debug mode)...
  Running: pytest -vv tests/test_auth.py::test_login_success

  ============================= test session starts ==============================
  collected 1 item

  tests/test_auth.py::test_login_success FAILED                            [100%]

  =================================== FAILURES ===================================
  _______________________________ test_login_success _____________________________

      def test_login_success():
          response = client.post("/auth/login", json={"username": "test"})
  >       assert response.status_code == 200
  E       AssertionError: assert 401 == 200

  tests/test_auth.py:45: AssertionError
```

**Now you can fix the issue with full context.**

### Link Validation → Ignore Patterns

**Error:**

```
[6/8] Internal links... ❌ FAILED
  docs/brainstorm/BRAINSTORM-feature.md → docs/specs/SPEC-feature.md (not found)
```

**Solution:**

Create `.linkcheck-ignore` to document expected broken links:

```markdown
# .linkcheck-ignore

### Brainstorm References
Files: `docs/brainstorm/*.md`
Targets: `docs/specs/*.md`
- Reason: Brainstorm files link to specs that may not exist yet
```

**Re-run:**

```bash
/craft:check --for pr

[6/8] Internal links...
  ✓ 846 links checked
  ⊘ 1 link ignored (expected broken - see .linkcheck-ignore)
  ✅ PASSED
```

### Version Sync → Update Strategy

**Error:**

```
[9/12] Version sync... ❌ FAILED
  docs/index.md: v2.8.1 (expected: v2.9.0)
  CLAUDE.md: v2.8.1 (expected: v2.9.0)
  mkdocs.yml: v2.8.1 (expected: v2.9.0)
```

**Solution:**

```bash
# Use docs:update to fix all version references
/craft:docs:update --category=version_refs

# Re-run check
/craft:check thorough --for release

[9/12] Version sync... ✅ PASSED
  All 47 version references match v2.9.0
```

---

## Advanced Usage

### Custom Check Profiles

Create project-specific check configurations:

**File:** `.craft/check-config.yml`

```yaml
# Custom check profile for this project
profiles:
  quick:
    mode: default
    skip:
      - security  # Skip for speed
      - external-links

  pr-ready:
    mode: thorough
    for: pr
    require:
      - lint
      - tests
      - types
      - coverage: 85%  # Higher than default 80%

  release:
    mode: thorough
    for: release
    require:
      - all  # All checks must pass
    fail-on-warning: true
```

**Usage:**

```bash
# Load custom profile
/craft:check --profile quick

# Load PR profile
/craft:check --profile pr-ready
```

### Project-Specific Overrides

**File:** `.craft/overrides.yml`

```yaml
# Override default check behavior
checks:
  lint:
    # Use different linter
    python: flake8  # instead of ruff
    rules:
      - E501  # Enable line length check
      - F401  # Enable unused import check

  tests:
    # Custom test command
    command: "pytest -n auto"  # Parallel execution
    coverage-threshold: 90  # Higher than default 80%

  security:
    # Skip specific advisories
    ignore:
      - CVE-2023-12345  # Known false positive
```

### Multi-Project Workflows

**Scenario:** Monorepo with multiple projects

```bash
# Check all projects in parallel
for project in frontend backend services/*; do
  (cd "$project" && /craft:check --for pr) &
done
wait

# Or use craft orchestrator
/craft:orchestrate "run checks across all projects" optimize
```

---

## Summary

**Key takeaways:**

1. **Use `/craft:check`** for quick sanity checks (8s)
2. **Use `/craft:check --for commit`** before committing (15s)
3. **Use `/craft:check --for pr`** before creating PRs (25s)
4. **Use `/craft:check thorough --for release`** before releases (90s)
5. **Integrate with git hooks** for automatic validation
6. **Match CI commands** with `/craft:code:ci-local` for debugging
7. **Auto-fix lint** with `/craft:code:lint --fix`
8. **Debug failures** with verbose test output

**Time investment:** 10-90 seconds locally vs 5-10 minutes waiting for CI.

**Success rate:** 95%+ CI passes on first try when using pre-PR checks.

---

## Next Steps

- **Command reference:** [/craft:check](../commands/check.md) — Full flag documentation
- **Auto-fix guide:** [Code Quality Commands](../commands/code.md) — Lint and fix workflows
- **Pattern guide:** [Interactive Commands](interactive-commands.md) — How the preview pattern works
- **Quick reference:** [Check Refcard](../reference/REFCARD-INTERACTIVE-COMMANDS.md) — Cheat sheet
