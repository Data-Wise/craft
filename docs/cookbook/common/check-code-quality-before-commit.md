---
title: "Recipe: Check Code Quality Before Commit"
description: "Run pre-commit checks to catch issues before they reach the repository"
category: "cookbook"
level: "beginner"
time_estimate: "2 minutes"
related:
  - ../../../commands/check.md
  - ../../../commands/code/lint.md
  - ../../../commands/test/run.md
---

# Recipe: Check Code Quality Before Commit

**Time:** 2 minutes
**Level:** Beginner
**Prerequisites:** None (works with any project type)

## Problem

I want to check code quality, run tests, and validate my changes before committing to avoid pushing broken code.

## Solution

1. **Quick validation (recommended)**

   ```bash
   /craft:check
   ```

   Why: Runs all pre-flight checks (lint, test, validation) appropriate for your project type

2. **Review results**
   - Green checkmarks = all good
   - Yellow warnings = should fix but not blocking
   - Red errors = must fix before committing

3. **Fix any issues**
   - Address errors and warnings shown in output
   - Re-run `/craft:check` to verify fixes

4. **Commit with confidence**

   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

   Why: Your code has passed all quality checks

## Explanation

`/craft:check` is a universal pre-flight validator that runs appropriate checks based on your project type:

**For all projects:**

- Git status check (clean working directory, on correct branch)
- File count validation (no massive unintended changes)
- Documentation links validation

**For Node.js projects:**

- `npm run lint` or `eslint` checks code style
- `npm test` runs unit tests
- `package.json` validation
- Dependency audit for security issues

**For Python projects:**

- `flake8` or `black` checks code formatting
- `pytest` runs tests
- `mypy` type checking (if configured)
- `bandit` security scan

**For R packages:**

- `R CMD check` validates package structure
- `lintr` checks code style
- Test coverage check
- Documentation completeness

**For Quarto/Markdown projects:**

- Link validation (no broken internal links)
- Image reference checks
- YAML frontmatter validation
- Spell checking (if configured)

The command is smart about what to run and fails fast if critical issues are found.

## Variations

- **Run only lint checks:**

  ```bash
  /craft:code:lint
  ```

  Use when you only want to check code style without running tests

- **Run only tests:**

  ```bash
  /craft:test:run
  ```

  Use when you want to run tests without linting

- **Verbose output for debugging:**

  ```bash
  /craft:check debug
  ```

  Shows detailed information about what's being checked

- **Optimize mode for faster checks:**

  ```bash
  /craft:check optimize
  ```

  Skips slow checks, focuses on critical validations

- **Release mode for thorough validation:**

  ```bash
  /craft:check release
  ```

  Runs all possible checks, including slow ones (use before releases)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Linter not found" | Install project-specific linter (eslint, flake8, lintr) |
| "Tests failed" | Fix failing tests before committing; use `/craft:test:run` to run tests only |
| "Broken links detected" | Fix or remove broken links; use `/craft:site:check` for detailed link report |
| "Command runs too slowly" | Use `optimize` mode: `/craft:check optimize` |
| "Check passes but CI fails" | CI might run additional checks; use `/craft:code:ci-local` to match CI environment |
| "Working directory not clean" | Commit or stash changes; `/craft:check` expects clean state |

## Related

- [Check Command Reference](../../../commands/check.md) — Full documentation
- [Lint Command](../../../commands/code/lint.md) — Code style checks only
- [Test Run Command](../../../commands/test/run.md) — Test execution only
- [CI Local Command](../../../commands/code/ci-local.md) — Run full CI checks locally
- [Automate Release Workflow](automate-release-workflow.md) — Set up CI automation
