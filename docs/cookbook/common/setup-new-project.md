---
title: "Recipe: Set Up New Project"
description: "Add Craft to a new project in 5 minutes"
category: "cookbook"
level: "beginner"
time_estimate: "5 minutes"
related:
  - ../../guide/getting-started.md
  - ../../../commands/git/init.md
  - ../../../commands/check.md
---

# Recipe: Set Up New Project

**Time:** 5 minutes
**Level:** Beginner
**Prerequisites:** Git repository initialized

## Problem

I want to add Craft to my new project with recommended settings and git workflow patterns.

## Solution

1. **Navigate to your project**
   ```bash
   cd /path/to/your/project
   ```
   Why: Craft needs to be run from your project root

2. **Initialize Craft**
   ```bash
   /craft:git:init
   ```
   Why: Sets up recommended git workflow patterns, creates `.claude/` directory, and configures project-specific settings

3. **Verify setup**
   ```bash
   /craft:check
   ```
   Why: Runs pre-flight validation to ensure everything is configured correctly

4. **Review generated files**
   - `.claude/settings.local.json` — Project-specific Craft configuration
   - `.gitignore` updates — Craft temporary files excluded
   - Git hooks (optional) — Pre-commit validation

## Explanation

`/craft:git:init` performs the following:

1. **Creates `.claude/` directory** for project-specific configuration
2. **Detects project type** (Node.js, Python, R package, Quarto, etc.)
3. **Sets up git patterns** for the detected project type:
   - Conventional commit templates
   - Pre-commit hooks (if requested)
   - Branch naming conventions
4. **Configures defaults** based on project type (test runners, build commands, lint rules)
5. **Initializes worktree support** for feature branch isolation

All settings are stored in `.claude/settings.local.json` and can be customized later.

## Variations

- **Skip interactive prompts:** Use defaults without confirmation
  ```bash
  /craft:git:init --yes
  ```

- **Custom project type:** Override auto-detection
  ```bash
  /craft:git:init --type python
  ```

- **Skip git hooks:** Initialize without pre-commit hooks
  ```bash
  /craft:git:init --no-hooks
  ```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Not a git repository" | Run `git init` first, then retry |
| "Permission denied" | Check write permissions in project directory |
| Settings not applied | Verify `.claude/settings.local.json` exists and is valid JSON |
| Wrong project type detected | Use `--type` flag to specify manually |

## Related

- [Getting Started Guide](../../guide/getting-started.md) — Comprehensive setup walkthrough
- [Git Worktree Command](../../../commands/git/worktree.md) — Feature branch isolation
- [Check Command](../../../commands/check.md) — Pre-flight validation
- [Configuration Reference](../../reference/configuration.md) — Customize settings
