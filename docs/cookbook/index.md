---
title: "Cookbook & Examples"
description: "Task-focused recipes for common Craft workflows"
category: "cookbook"
level: "beginner"
time_estimate: "2 minutes"
related:
  - guide/getting-started.md
  - commands/do.md
---

# Cookbook & Examples

Welcome to the Craft Cookbook! This section provides task-focused, step-by-step recipes for accomplishing common goals with Craft.

## What Are Cookbook Recipes?

Each recipe follows a problem-solution format:

- **Problem:** What you're trying to accomplish
- **Solution:** Step-by-step commands with explanations
- **Explanation:** How it works behind the scenes
- **Variations:** Alternative approaches for different scenarios
- **Troubleshooting:** Common issues and fixes
- **Related:** Links to relevant guides and commands

Recipes are categorized by difficulty level (Beginner, Intermediate, Advanced) and include time estimates so you can plan your workflow.

## Common Recipes

### Quick Start (< 3 minutes)

- [Find the Right Command](common/find-the-right-command.md) — Use the Hub to discover commands in 2 minutes
- [Quick Code Checks](common/quick-code-checks.md) — Fast code quality scan in 1 minute
- [Check Code Quality Before Commit](common/check-code-quality-before-commit.md) — Run pre-commit checks in 2 minutes
- [Create a Git Branch](common/create-git-branch.md) — Create feature branches following branch architecture in 2 minutes
- [View Project Architecture](common/view-project-architecture.md) — Quick architecture overview in 2 minutes

### Documentation (3-5 minutes)

- [Update a Single Doc](common/update-single-doc.md) — Refresh one documentation section in 3 minutes
- [Post-Merge Documentation Update](common/post-merge-documentation.md) — Auto-update docs after merging in 3-5 minutes
- [Deploy Course Website](common/deploy-course-website.md) — Safely publish course site updates in 3 minutes

### Testing (3-5 minutes)

- [Run Tests by Category](common/run-tests-by-category.md) — Filter tests by tier or domain in 3 minutes
- [Generate Tests for a Project](common/generate-tests-for-project.md) — Auto-generate a full test suite in 5 minutes

### Workflow and Orchestration (5-10 minutes)

- [Set Up New Project](common/setup-new-project.md) — Add Craft to a new project in 5 minutes
- [Use Interactive Orchestration](common/use-interactive-orchestration.md) — Run complex tasks with mode selection and checkpoints in 5-7 minutes
- [Setup Parallel Worktrees](common/setup-parallel-worktrees.md) — Create isolated feature branches with auto-generated plans in 8-10 minutes

### CI/CD and Automation (10 minutes)

- [Automate Release Workflow](common/automate-release-workflow.md) — Set up GitHub Actions CI in 10 minutes
- [Distribute Plugin via Homebrew](common/distribute-plugin-via-homebrew.md) — Set up Homebrew formula for a Claude Code plugin in 10 minutes

## Browse by Time Available

Got limited time? Find recipes that fit your schedule:

### Quick Wins (< 3 minutes)

Perfect for between meetings or when you need a quick confidence boost.

- **1 min:** [Quick Code Checks](common/quick-code-checks.md)
- **2 min:** [Find the Right Command](common/find-the-right-command.md)
- **2 min:** [Check Code Quality Before Commit](common/check-code-quality-before-commit.md)
- **2 min:** [Create a Git Branch](common/create-git-branch.md)
- **2 min:** [View Project Architecture](common/view-project-architecture.md)

### Short Tasks (3-10 minutes)

Great for focused work sessions or getting familiar with Craft.

- **3 min:** [Update a Single Doc](common/update-single-doc.md)
- **3 min:** [Run Tests by Category](common/run-tests-by-category.md)
- **3 min:** [Deploy Course Website](common/deploy-course-website.md)
- **3-5 min:** [Post-Merge Documentation Update](common/post-merge-documentation.md)
- **5 min:** [Set Up New Project](common/setup-new-project.md)
- **5 min:** [Generate Tests for a Project](common/generate-tests-for-project.md)
- **5-7 min:** [Use Interactive Orchestration](common/use-interactive-orchestration.md)
- **8-10 min:** [Setup Parallel Worktrees](common/setup-parallel-worktrees.md)
- **10 min:** [Automate Release Workflow](common/automate-release-workflow.md)
- **10 min:** [Distribute Plugin via Homebrew](common/distribute-plugin-via-homebrew.md)

!!! tip "ADHD-Friendly"
    All recipes include clear time estimates. Start with the 1-minute tasks to build momentum!

## Examples

Detailed walkthroughs showing real-world command sessions:

- [Interactive Docs Update Example](../examples/docs-update-interactive-example.md) — Step-by-step `/craft:docs:update --interactive` session
- [Release Workflow Example](../examples/release-workflow-example.md) — End-to-end release pipeline walkthrough

## Troubleshooting

Having issues? Check the troubleshooting section:

- [Command Not Found](troubleshooting/command-not-found.md) — Fix "command not found" errors
- [Command Times Out](troubleshooting/command-times-out.md) — Resolve timeout issues
- [Wrong Command Output](troubleshooting/wrong-command-output.md) — Debug unexpected results
- [CI Workflow Fails](troubleshooting/ci-workflow-fails.md) — Fix GitHub Actions failures
- [Pre-commit Blocks Commit](troubleshooting/pre-commit-blocks-commit.md) — Resolve pre-commit hook issues
- [Worktree Won't Create](troubleshooting/worktree-wont-create.md) — Fix git worktree creation problems
- [Broken Links After Update](troubleshooting/broken-links-after-update.md) — Repair broken internal links
- [CLAUDE.md Out of Sync](troubleshooting/claude-md-out-of-sync.md) — Re-sync CLAUDE.md with project state
- [MkDocs Build Fails](troubleshooting/mkdocs-build-fails.md) — Debug MkDocs build errors

## Need More Help?

- **Quick questions?** Try the [ADHD Quick Start](../ADHD-QUICK-START.md)
- **Comprehensive guide?** See [Getting Started](../guide/getting-started.md)
- **Command reference?** Browse [Commands](../commands/hub.md)
- **Smart routing?** Use [`/craft:do`](../commands/do.md) to let Craft figure out what you need
