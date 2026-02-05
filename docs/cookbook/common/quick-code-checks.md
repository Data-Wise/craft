---
title: "Recipe: Quick Code Checks"
description: "Run fast code quality checks in default mode to catch issues early"
category: "cookbook"
level: "beginner"
time_estimate: "1 minute"
related:
  - ../../commands/code.md
  - ../../commands/check.md
---

# Recipe: Quick Code Checks

**Time:** 1 minute
**Level:** Beginner
**Prerequisites:** Craft installed, project with code files

## Problem

I want a fast code quality scan to catch obvious issues without waiting for a full test suite.

## Solution

1. **Run the linter in default mode**

   ```bash
   /craft:code:lint
   ```

   Why: Default mode runs in under 10 seconds and catches formatting errors, style violations, and common mistakes

2. **Read the output**

   ```
   Linting results:
     ✓ Python: ruff (0 issues)
     ✗ Markdown: markdownlint (2 issues)
       docs/guide/setup.md:14  MD032  Blank line around list
       docs/guide/setup.md:28  MD040  Fenced code block without language
   ```

   Why: Each issue includes the file, line number, rule ID, and a short description so you can fix it quickly

3. **Fix the reported issues**

   Edit the flagged files to resolve warnings. For markdown issues, the rule ID (e.g., MD032) tells you exactly what to change.

4. **Re-run to confirm**

   ```bash
   /craft:code:lint
   ```

   Why: A clean run confirms all issues are resolved before you commit

## Explanation

`/craft:code:lint` detects your project type and runs the appropriate linters automatically. For Python projects it uses `ruff` or `flake8`; for Node.js it uses `eslint`; for documentation projects it runs `markdownlint` with 24 enforced rules. Default mode prioritizes speed over thoroughness. If you need deeper analysis, use `debug` mode for verbose traces or `release` mode for the full rule set.

## What's Next

- [Code Commands Reference](../../commands/code.md) -- All code quality commands (format, coverage, ci-local)
- [Check Command Reference](../../commands/check.md) -- Full pre-flight validation before commits
- [Check Code Quality Before Commit](check-code-quality-before-commit.md) -- Complete pre-commit workflow
