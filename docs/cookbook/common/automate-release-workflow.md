---
title: "Recipe: Automate Release Workflow"
description: "Set up GitHub Actions CI to automate testing before deployment"
category: "cookbook"
level: "intermediate"
time_estimate: "10 minutes"
related:
  - ../../../commands/ci/generate.md
  - ../../../commands/ci/validate.md
  - ../../../commands/code/ci-local.md
---

# Recipe: Automate Release Workflow

**Time:** 10 minutes
**Level:** Intermediate
**Prerequisites:** GitHub repository, tests written

## Problem

I want to automate testing and validation before deployment so broken code never reaches production.

## Solution

1. **Detect project setup**
   ```bash
   /craft:ci:detect
   ```
   Why: Analyzes your project to identify build tools, test frameworks, and CI requirements

2. **Generate CI workflow**
   ```bash
   /craft:ci:generate
   ```
   Why: Creates a GitHub Actions workflow tailored to your project type

3. **Review generated workflow**
   - Open `.github/workflows/ci.yml`
   - Verify jobs match your requirements
   - Customize triggers if needed (branches, pull requests)

4. **Test locally before committing**
   ```bash
   /craft:code:ci-local
   ```
   Why: Runs the same checks that will run in CI, catching issues before pushing

5. **Commit and push**
   ```bash
   git add .github/workflows/ci.yml
   git commit -m "ci: add GitHub Actions workflow"
   git push
   ```
   Why: Activates the CI workflow on your repository

6. **Verify CI runs**
   - Create a pull request or push to main
   - Check Actions tab on GitHub
   - Verify all checks pass

## Explanation

`/craft:ci:generate` creates a customized GitHub Actions workflow based on your project:

**For Node.js projects:**
- `npm install` dependencies
- `npm test` runs tests
- `npm run lint` checks code quality
- Matrix testing across Node versions (14, 16, 18)

**For Python projects:**
- `pip install` dependencies
- `pytest` runs tests
- `flake8`/`black` checks code style
- Matrix testing across Python versions (3.8, 3.9, 3.10)

**For R packages:**
- `R CMD check` validates package
- `R CMD build` builds tarball
- `covr::codecov()` reports coverage
- Matrix testing across R versions

**For Quarto projects:**
- `quarto check` validates syntax
- `quarto render` builds site
- Link validation
- Deploy to GitHub Pages (optional)

**Common features across all project types:**
- Dependency caching for faster builds
- Parallel job execution
- Pull request checks
- Branch protection support
- Status badges for README

The workflow runs on:
- Every push to `main` or `dev` branches
- Every pull request
- Manual workflow dispatch

## Variations

- **Run checks locally without generating workflow:**
  ```bash
  /craft:code:ci-local
  ```
  Use during development to catch issues early

- **Validate existing workflow:**
  ```bash
  /craft:ci:validate
  ```
  Use to check if your current CI workflow follows best practices

- **Generate with custom triggers:**
  ```bash
  /craft:ci:generate --on push,pull_request,schedule
  ```
  Add scheduled runs (e.g., nightly builds)

- **Multi-language projects:**
  ```bash
  /craft:ci:detect
  # Review detected languages
  /craft:ci:generate --lang python,node
  ```
  Creates workflow for multiple languages

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No test framework detected" | Install a test framework (pytest, jest, testthat) and retry |
| "CI workflow already exists" | Use `/craft:ci:validate` to check existing workflow, or backup and regenerate |
| "Tests pass locally but fail in CI" | Run `/craft:code:ci-local` to reproduce CI environment locally |
| "Dependency installation fails" | Check that `package.json`/`requirements.txt`/`DESCRIPTION` lists all dependencies |
| "Matrix builds taking too long" | Reduce matrix versions in `.github/workflows/ci.yml` |
| "Workflow not triggering" | Verify `.github/workflows/ci.yml` is committed and pushed to default branch |

## Related

- [CI Generate Command](../../../commands/ci/generate.md) — Full command reference
- [CI Validate Command](../../../commands/ci/validate.md) — Best practices checker
- [CI Local Command](../../../commands/code/ci-local.md) — Run checks locally
- [CI Detect Command](../../../commands/ci/detect.md) — Project analysis
- [GitHub Actions Documentation](https://docs.github.com/en/actions) — Official GitHub docs
