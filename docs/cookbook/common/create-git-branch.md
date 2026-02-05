---
title: "Recipe: Create a Git Feature Branch"
description: "Create properly named feature branches using the Craft git workflow"
category: "cookbook"
level: "beginner"
time_estimate: "2 minutes"
related:
  - ../../commands/git.md
  - ../../guide/worktree-advanced-patterns.md
---

# Recipe: Create a Git Feature Branch

**Time:** 2 minutes
**Level:** Beginner
**Prerequisites:** Craft installed, git repository with a `dev` branch

## Problem

I want to create a feature branch that follows the project's branch architecture: `main` (protected) <- `dev` (integration) <- `feature/*` (work).

## Solution

1. **Verify you are on the dev branch**

   ```bash
   /craft:git:status
   ```

   Why: Feature branches must be created from `dev`, not from `main` or another feature branch

2. **Create the feature branch as a worktree**

   ```bash
   /craft:git:worktree feature/add-search
   ```

   Why: Worktrees give you an isolated directory for the feature without switching branches in your main repo. The branch is automatically created from `dev`

   ```
   ✓ Branch: feature/add-search
   ✓ Location: ~/.git-worktrees/<project>/feature-add-search
   ✓ Based on: dev
   ```

3. **Navigate to the worktree**

   ```bash
   cd ~/.git-worktrees/<project>/feature-add-search
   ```

   Why: All your feature work happens in this separate directory while the main repo stays on `dev` or `main`

4. **Confirm the branch**

   ```bash
   git branch --show-current
   ```

   Expected output: `feature/add-search`

   Why: A quick sanity check before you start writing code

## Explanation

Craft enforces a three-tier branch architecture. The `main` branch is protected and only receives code through pull requests. The `dev` branch is the integration hub where features are planned and merged. Feature branches (`feature/*`) are where all implementation happens, isolated in git worktrees so you never need to stash or switch branches. When your feature is done, you push and create a PR targeting `dev`. After review, `dev` is periodically released to `main`.

## What's Next

- [Git Commands Reference](../../commands/git.md) -- Branch, worktree, sync, and clean commands
- [Worktree Advanced Patterns](../../guide/worktree-advanced-patterns.md) -- Multi-worktree workflows and team collaboration
- [Setup Parallel Worktrees](setup-parallel-worktrees.md) -- Work on multiple features simultaneously
