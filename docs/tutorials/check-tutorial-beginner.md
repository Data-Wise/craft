---
title: "Tutorial: Pre-Flight Checks with /craft:check"
description: "Beginner-friendly step-by-step guide to validating code before commits"
category: "tutorial"
level: "beginner"
time_estimate: "10 minutes"
version: "2.9.0"
related:
  - ../commands/check.md
  - ../guide/check-command-mastery.md
  - ../reference/REFCARD-CHECK.md
  - ../cookbook/common/check-code-quality-before-commit.md
---

# Tutorial: Pre-Flight Checks with /craft:check

**Level:** Beginner
**Time:** 10 minutes
**Prerequisites:** Craft plugin installed
**Version:** 2.9.0+ (includes "Show Steps First" pattern)

## What You'll Learn

By the end of this tutorial, you'll know how to:

1. Run pre-flight checks before committing
2. Understand the check output
3. Use different modes (default vs thorough)
4. Skip specific checks when needed
5. Troubleshoot common failures

## Overview

`/craft:check` is your safety net before committing code. It runs appropriate validation checks for your project type and tells you if something's wrong **before** you push broken code.

**Think of it as:**

- ✈️ Pre-flight checklist for pilots
- 🏥 Pre-surgery checklist for doctors
- ✅ Pre-commit checklist for developers

## Step 1: Your First Check

Let's start with the simplest usage.

**Run this command:**

```bash
/craft:check
```

**What happens (v2.9.0 "Show Steps First"):**

```
╭─ Pre-Flight Validation Plan ─────────────────╮
│ Mode: default                                 │
│ Estimated time: 5-10 seconds                  │
├───────────────────────────────────────────────┤
│                                               │
│ Steps to run:                                 │
│                                               │
│ 1. Code Quality (2s)                          │
│    • markdownlint (24 rules)                  │
│    • python linting (ruff)                    │
│                                               │
│ 2. Quick Tests (3s)                           │
│    • Unit tests (fast subset, ~200 tests)     │
│                                               │
│ 3. Basic Validation (2s)                      │
│    • Config files                             │
│    • Required files                           │
│                                               │
├───────────────────────────────────────────────┤
│ Proceed with these checks? (y/n/switch-mode)  │
╰───────────────────────────────────────────────╯
```

**What you see:**

- **Mode:** Which mode is running (default = quick checks)
- **Time estimate:** How long it will take
- **Steps:** What will be checked
- **Prompt:** Choice to proceed, cancel, or switch modes

**Your options:**

- Type `y` to proceed
- Type `n` to cancel
- Type `switch-mode` to use thorough mode instead

**Try it:** Type `y` and press Enter.

## Step 2: Understanding the Output

After running, you'll see results like this:

### ✅ Successful Check

```
╭─ Pre-Flight Check Results ───────────────────╮
│                                               │
│ ✓ Code Quality (2.1s)                         │
│   • markdownlint: 45 files, 0 issues          │
│   • python linting: 12 files, 0 issues        │
│                                               │
│ ✓ Quick Tests (3.4s)                          │
│   • Unit tests: 203 passed, 0 failed          │
│                                               │
│ ✓ Basic Validation (1.8s)                     │
│   • Config files: valid                       │
│   • Required files: all present               │
│                                               │
├───────────────────────────────────────────────┤
│ Results: 3/3 checks passed                    │
│ Issues: 0 warnings, 0 errors                  │
│ Next steps: Ready to commit ✓                 │
╰───────────────────────────────────────────────╯
```

**What this means:**

- ✓ Green checkmarks = everything passed
- Ready to commit safely
- All checks completed in ~7 seconds

**What to do next:**

```bash
git add .
git commit -m "feat: add new feature"
git push
```

### ❌ Failed Check

```
╭─ Pre-Flight Check Results ───────────────────╮
│                                               │
│ ✓ Code Quality (2.1s)                         │
│   • markdownlint: 44 files ok, 1 file failed  │
│   • python linting: 12 files, 0 issues        │
│                                               │
│ ✗ Quick Tests (2.8s)                          │
│   • Unit tests: 202 passed, 1 failed          │
│     Failed: test_auth_flow (line 45)          │
│     Error: AssertionError: Expected 200, got 401│
│                                               │
│ ✓ Basic Validation (1.8s)                     │
│   • Config files: valid                       │
│   • Required files: all present               │
│                                               │
├───────────────────────────────────────────────┤
│ Results: 2/3 checks passed                    │
│ Issues: 0 warnings, 2 errors                  │
│ Next steps: Fix errors before committing ✗    │
╰───────────────────────────────────────────────╯
```

**What this means:**

- ✗ Red X = something failed
- 2 errors found (1 markdown issue, 1 test failure)
- **DO NOT commit** until fixed

**What to do:**

1. **Fix the markdown issue:**
   - See which file failed: check output
   - Run auto-fix: `npx markdownlint-cli2 --fix "**/*.md"`

2. **Fix the test failure:**
   - Open the test file
   - Check line 45 (test_auth_flow)
   - Fix the assertion or the code being tested

3. **Re-run check:**

   ```bash
   /craft:check
   ```

4. **Commit only when all checks pass**

## Step 3: Preview Mode (Dry Run)

Want to see what will be checked **without** actually running it?

**Use dry-run mode:**

```bash
/craft:check --dry-run
```

**Output:**

```
╭─ Pre-Flight Validation Plan (DRY RUN) ───────╮
│ Mode: default                                 │
│ Estimated time: 5-10 seconds                  │
├───────────────────────────────────────────────┤
│                                               │
│ Would run these steps:                        │
│                                               │
│ 1. Code Quality (2s)                          │
│    • markdownlint (24 rules)                  │
│    • python linting (ruff)                    │
│                                               │
│ 2. Quick Tests (3s)                           │
│    • Unit tests (fast subset, ~200 tests)     │
│                                               │
│ 3. Basic Validation (2s)                      │
│    • Config files                             │
│    • Required files                           │
│                                               │
├───────────────────────────────────────────────┤
│ DRY RUN - No checks executed                  │
╰───────────────────────────────────────────────╯
```

**When to use:**

- First time using `/craft:check` (learn what it does)
- Checking what mode will do
- Planning your commit workflow

## Step 4: Mode Selection

There are 2 modes available:

### Default Mode (Fast - 5-10 seconds)

```bash
/craft:check
# or explicitly:
/craft:check --mode=default
```

**What it checks:**

- ✓ Basic code linting
- ✓ Fast subset of tests
- ✓ Config file syntax
- ✓ Required files exist

**Use for:** Before every commit

### Thorough Mode (Comprehensive - 2-5 minutes)

```bash
/craft:check --mode=thorough
```

**What it checks:**

- ✓ All linters with strict rules
- ✓ Full test suite
- ✓ Coverage analysis (85%+ threshold)
- ✓ Broken link detection
- ✓ Dependency security audit
- ✓ Build verification

**Use for:**

- Before creating PR
- Before merging to main
- Before releases
- After major refactoring

### Mode Comparison

| Feature | Default | Thorough |
|---------|---------|----------|
| Time | 5-10s | 2-5 min |
| Lint rules | Basic | Strict |
| Tests | Fast subset | Full suite |
| Coverage | No | Yes (85%+) |
| Links | No | Yes |
| Dependencies | No | Yes (security audit) |
| Build | No | Yes |
| **Use case** | **Every commit** | **PR/Release** |

## Step 5: Skipping Checks

Sometimes you want to skip specific checks.

### Skip Tests (Docs-Only Changes)

```bash
/craft:check --skip=tests
```

**Use when:**

- Only changed documentation
- Changed README or markdown files
- No code changes

**What runs:**

- ✓ Linting
- ✗ Tests (skipped)
- ✓ Validation

### Skip Multiple Checks

```bash
/craft:check --skip=lint,docs
```

**Available skip options:**

| Flag | Skips | When to use |
|------|-------|-------------|
| `--skip=lint` | Code/markdown linting | Already ran linter manually |
| `--skip=tests` | Test execution | Docs-only changes |
| `--skip=docs` | Documentation validation | Code-only changes |
| `--skip=build` | Build verification | Not ready to build yet |
| `--skip=deps` | Dependency audit | No dependency changes |

⚠️ **Warning:** Only skip checks when you're **certain** they're not needed. When in doubt, run all checks.

## Step 6: Common Scenarios

### Scenario 1: Quick Commit

```bash
# Make some changes
echo "# New Section" >> README.md

# Check
/craft:check

# If passes, commit
git add README.md
git commit -m "docs: add new section to README"
git push
```

**Time:** 6-10 seconds total

### Scenario 2: Before PR

```bash
# Feature complete, ready for review
git checkout feature/new-auth

# Run thorough check
/craft:check --mode=thorough

# If passes, create PR
gh pr create --base dev --title "Add JWT authentication"
```

**Time:** 2-5 minutes

### Scenario 3: Docs-Only Change

```bash
# Updated tutorials
git status
# modified: docs/tutorials/new-tutorial.md

# Check (skip tests since no code changed)
/craft:check --skip=tests

# Commit
git add docs/
git commit -m "docs: add new tutorial"
git push
```

**Time:** 3-5 seconds

## Step 7: Troubleshooting

### Issue 1: "Markdown lint failed"

**Error:**

```
✗ Code Quality
  • markdownlint: 1 file failed
    docs/guide.md:15:1 MD022 Headings should be surrounded by blank lines
```

**Solution:**

```bash
# Auto-fix markdown issues
npx markdownlint-cli2 --fix "docs/guide.md"

# Re-run check
/craft:check
```

### Issue 2: "Tests failed"

**Error:**

```
✗ Quick Tests
  • Unit tests: 1 failed
    test_api_auth: Expected 200, got 401
```

**Solution:**

1. Open the test file
2. Look at the failing test
3. Fix either:
   - The test (if test is wrong)
   - The code (if code is wrong)
4. Re-run: `/craft:check`

### Issue 3: "Coverage below threshold"

**Error (thorough mode only):**

```
✗ Coverage Analysis
  • Current: 82%
  • Threshold: 85%
  • Missing coverage in: src/auth.py
```

**Solution:**

```bash
# Add tests for uncovered code
# Then re-run
/craft:check --mode=thorough
```

### Issue 4: "Check takes too long"

**Problem:** Thorough mode takes 5+ minutes

**Solutions:**

```bash
# Option 1: Use default mode for quick feedback
/craft:check

# Option 2: Skip heavy checks
/craft:check --mode=thorough --skip=tests

# Option 3: Run only specific checks later
/craft:test:run              # Just tests
/craft:docs:check-links      # Just link validation
```

## Step 8: Best Practices

### ✅ DO

- **Run `/craft:check` before every commit**
- **Use default mode for commits, thorough for PRs**
- **Fix all errors before committing**
- **Read the error messages** (they tell you what's wrong)
- **Re-run after fixing issues**

### ❌ DON'T

- **Skip checks to save time** (you'll regret it later)
- **Commit when checks fail** (breaks the build)
- **Ignore warnings** (they often become errors)
- **Use --skip unless you're sure** (easy to miss issues)

### Workflow Integration

**Good workflow:**

```bash
# 1. Make changes
<edit files>

# 2. Check
/craft:check

# 3. If fails, fix and repeat
<fix issues>
/craft:check

# 4. When passes, commit
git add .
git commit -m "message"
git push
```

**Bad workflow:**

```bash
# ❌ Don't do this
git add .
git commit -m "message"
git push
# <build breaks, CI fails, teammates angry>
```

## Step 9: Interactive Practice

Try these exercises to build muscle memory:

### Exercise 1: First Check

```bash
# Run your first check
/craft:check

# Questions:
# - What mode ran?
# - How long did it take?
# - Did it pass?
```

### Exercise 2: Dry Run

```bash
# See the plan without running
/craft:check --dry-run

# Questions:
# - How many steps would run?
# - What's the estimated time?
```

### Exercise 3: Mode Comparison

```bash
# Run both modes
/craft:check --mode=default
/craft:check --mode=thorough --dry-run

# Questions:
# - What's the time difference?
# - What extra checks does thorough include?
```

### Exercise 4: Skip Practice

```bash
# Skip tests
/craft:check --skip=tests

# Questions:
# - Did it run faster?
# - What still ran?
# - When would you use this?
```

## Step 10: Next Steps

You now know how to use `/craft:check`! Here's what to learn next:

### Immediate Next Steps

1. **Add to workflow:** Run `/craft:check` before your next commit
2. **Set up automation:** Add pre-commit hook (optional)
3. **Explore modes:** Try thorough mode before your next PR

### Further Learning

- **Command mastery:** [Check Command Mastery Guide](../guide/check-command-mastery.md)
- **Quick reference:** [Check Command Reference](../reference/REFCARD-CHECK.md)
- **Cookbook recipe:** [Check Before Commit](../cookbook/common/check-code-quality-before-commit.md)
- **All commands:** [Commands Overview](../commands/overview.md)

### Advanced Topics

- **Custom validators:** Add project-specific checks
- **CI integration:** Use in GitHub Actions
- **Mode customization:** Configure coverage thresholds
- **Auto-fix workflows:** Automate common fixes

## Quick Reference Card

### Essential Commands

```bash
# Basic usage
/craft:check                     # Run default mode

# Preview mode
/craft:check --dry-run           # Show plan without running

# Mode selection
/craft:check --mode=default      # Fast (5-10s)
/craft:check --mode=thorough     # Comprehensive (2-5min)

# Skip checks
/craft:check --skip=tests        # Skip test execution
/craft:check --skip=lint,docs    # Skip multiple
```

### Decision Tree

```
Before committing?
  → /craft:check

Before PR?
  → /craft:check --mode=thorough

Docs only?
  → /craft:check --skip=tests

Want to preview?
  → /craft:check --dry-run
```

### Troubleshooting Cheat Sheet

| Error | Solution |
|-------|----------|
| Markdown lint failed | `npx markdownlint-cli2 --fix "**/*.md"` |
| Tests failed | Fix the test or code, re-run check |
| Coverage too low | Add more tests |
| Checks too slow | Use --skip or default mode |

---

**Congratulations!** You've completed the `/craft:check` beginner tutorial. You're now ready to validate your code before committing.

**Time to complete:** ~10 minutes
**Commands learned:** 5
**Next tutorial:** [Smart Routing with /craft:do](smart-routing-tutorial.md)

---

**Last Updated:** 2026-01-29 (v2.9.0)
**Tutorial Version:** 1.0
**Prerequisites:** Craft v2.9.0+
