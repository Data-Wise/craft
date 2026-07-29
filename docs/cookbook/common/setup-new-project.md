---
title: "Recipe: Set Up New Project"
description: "Add Craft to a new project in 5 minutes"
category: "cookbook"
level: "beginner"
time_estimate: "5 minutes"
related:
  - ../../guide/getting-started.md
  - ../../commands/git.md
  - ../../commands/check.md
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

   > **Note (2026-07 v4 consolidation):** `/craft:git:init` was folded into the `dev/git` skill — the command itself no longer exists. Ask naturally instead.

   ```text
   "init repo" / "set up git" / "bootstrap repository"
   ```

   Why: Bootstraps the git repo (idempotent if `.git/` already exists), creates the `dev`
   branch off `main` for the recommended `main-dev` workflow, sets up the remote if given
   one, applies local branch-guard rules, scaffolds a starter `.gitignore`/`README.md`/
   `CLAUDE.md` if absent, and offers to run the branch-protection audit wizard immediately
   after.

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

The `dev/git` skill's Repo Init operation (Operation 1) performs the following when you ask
"init repo" / "set up git" / "bootstrap repository":

1. **Runs `git init`** (idempotent — detects an existing `.git/` and skips)
2. **Scaffolds an initial commit** if the working tree is empty
3. **Creates a `dev` branch off `main`** for the recommended `main-dev` workflow pattern
   (pass `simple` or `gitflow` if you want a different pattern)
4. **Sets up the remote** if you give one (`OWNER/REPO` or a URL) — creates the GitHub repo
   (private by default), sets origin, pushes both branches
5. **Applies local branch-guard rules** and offers GitHub-side baseline protection
6. **Writes a starter `.gitignore`, `README.md` skeleton, and `CLAUDE.md` template** if absent
7. **Offers to run the branch-protection audit wizard** immediately after setup

## Variations

- **Skip interactive prompts:** pass `--yes` for non-interactive defaults

  ```text
  "bootstrap repository --yes"
  ```

- **Preview without applying:** pass `--dry-run`

  ```text
  "set up git --dry-run"
  ```

- **Different workflow pattern:** specify `simple` or `gitflow` instead of the `main-dev` default

  ```text
  "init repo with the simple workflow pattern"
  ```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Not a git repository" | The skill runs `git init` for you — just ask "init repo" |
| "Permission denied" | Check write permissions in project directory |
| GitHub repo creation fails | Verify `gh` CLI is authenticated (`gh auth status`) |
| Wrong workflow pattern applied | Re-run with the pattern named explicitly, e.g. "init repo with the simple workflow pattern" |

## Related

- [Getting Started Guide](../../guide/getting-started.md) — Comprehensive setup walkthrough
- [Git Commands](../../commands/git.md) — Worktree, branch, sync
- [Check Command](../../commands/check.md) — Pre-flight validation
- [Configuration Reference](../../reference/configuration.md) — Customize settings
