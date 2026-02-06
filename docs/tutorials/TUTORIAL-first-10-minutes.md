---
title: "Tutorial: Your First 10 Minutes with Craft"
description: "A complete beginner's walkthrough of Craft essentials"
category: "tutorial"
level: "beginner"
time_estimate: "10 minutes"
related:
  - ../QUICK-START.md
  - ../ADHD-QUICK-START.md
  - ../commands/overview.md
---

# Your First 10 Minutes with Craft

> **Time:** 10 minutes | **Level:** Beginner | **Prerequisites:** Claude Code installed, Craft plugin loaded

## What You'll Learn

1. Confirm Craft is loaded and explore available commands
2. Run a health check on your project
3. Use smart routing to describe tasks in plain English
4. Navigate the 3-layer command discovery system
5. Run a real linting command and read its output
6. Validate your documentation

## Before You Start

Make sure the Craft plugin is installed:

```bash
claude plugin install craft@local-plugins
```

Open any project directory in Claude Code. Craft auto-detects your project type (Python, Node, R, Quarto, MkDocs, or generic).

## Step 1: Verify Craft Is Loaded

**Run:** `/craft:hub`

**Expected output:**

```
┌──────────────────────────────────────────────────────────┐
│  CRAFT - Full Stack Developer Toolkit v2.15.0            │
│  my-project (Python Package) on main                     │
│  106 Commands | 21 Skills | 8 Agents | 4 Modes          │
├──────────────────────────────────────────────────────────┤
│ SMART COMMANDS (Start Here):                             │
│    /craft:do <task>     AI routes to best workflow        │
│    /craft:check         Pre-flight validation             │
├──────────────────────────────────────────────────────────┤
│ CODE (12)  TEST (10)  DOCS (25)  GIT (8)                 │
│ SITE (16)  ARCH (12)  CI (6)     WORKFLOW (7)  ...       │
└──────────────────────────────────────────────────────────┘
```

**Why it matters:** The hub is your home base. If you see the listing with 106 commands, Craft is working. The project type and branch are auto-detected.

## Step 2: Run Your First Health Check

**Run:** `/craft:check`

**Expected output:**

```
╭─ Pre-Flight Validation Plan ──────────────╮
│ Mode: default | Time: 5-10 seconds        │
├───────────────────────────────────────────┤
│  1. Validate project structure             │
│  2. Check for lint errors                  │
│  3. Run fast test suite                    │
│  4. Verify documentation links             │
╰───────────────────────────────────────────╯
Proceed? (Y/n)
```

After confirming, you see green checkmarks for passing checks and warnings for anything that needs attention.

**Why it matters:** Running `/craft:check` before every commit catches broken links, lint errors, and test failures early. Think of it as a pre-flight checklist.

## Step 3: Use Smart Routing

Instead of memorizing commands, describe what you want in plain English.

**Run:** `/craft:do "check my code quality"`

**Expected output:**

```
Analyzing task: "check my code quality"
Complexity score: 2/10 (simple)
Routing to: /craft:code:lint (direct command)
Running code quality checks...
```

Craft scores your task on a 0-10 complexity scale and routes it automatically:

| Score | Route | Example |
|-------|-------|---------|
| 0-3 | Direct command | "lint my code" |
| 4-7 | Single agent | "refactor the auth module" |
| 8-10 | Orchestrator | "add a full test suite with CI" |

**Why it matters:** `/craft:do` is the universal entry point. Describe the task and Craft figures out the rest.

## Step 4: Explore Commands by Category

The hub uses 3-layer progressive disclosure. Start broad and drill down.

**Layer 1** -- Run `/craft:hub` to see the main menu (Step 1 above).

**Layer 2** -- Pick a category when prompted, e.g., "Code & Testing":

```
CODE & TESTING (22 commands)
────────────────────────────
  /craft:code:lint [mode]     Lint code with auto-fix
  /craft:code:debug           Debug with traces
  /craft:code:refactor        AI-assisted refactoring
  /craft:test:run [mode]      Run test suite
  /craft:test:coverage        Coverage report
  ...
```

**Layer 3** -- Pick a specific command for full details, usage examples, and related guides.

**Why it matters:** With 106 commands, you never need to memorize anything. Browse by category and the hub shows you how to use each command.

## Step 5: Try a Real Command

**Run:** `/craft:code:lint`

**Clean output:**

```
Linting project...
  Files checked: 24 | Errors: 0 | Warnings: 0
All checks passed.
```

**Output with warnings:**

```
Linting project...
  Files checked: 24 | Errors: 0 | Warnings: 3

  src/utils.py:42  W291 trailing whitespace
  src/utils.py:88  W293 whitespace before ':'
  docs/index.md    MD032 Lists should be surrounded by blank lines
```

!!! tip "Execution modes"
    Every command supports four modes: `default` (quick), `debug` (verbose), `optimize` (performance), and `release` (thorough). Append the mode name, e.g., `/craft:code:lint release`.

## Step 6: Check Documentation Health

**Run:** `/craft:docs:check`

This validates internal links, checks for missing pages, and flags stale references. A clean run means your documentation is consistent and navigable.

**Why it matters:** Broken links and missing pages erode trust in your docs. A quick check keeps everything connected.

## What's Next

You have covered the essentials. Here are paths forward depending on what you need:

| Goal | Where to go |
|------|-------------|
| Common task recipes | [Cookbook](../cookbook/index.md) |
| Feature development | [Worktree Setup Tutorial](TUTORIAL-worktree-setup.md) |
| 30-second refresher | [ADHD Quick Start](../ADHD-QUICK-START.md) |
| Full command list | [Commands Reference](../commands/overview.md) |
| Smart routing deep dive | [Smart Routing Tutorial](smart-routing-tutorial.md) |

!!! note "The two commands that matter most"
    `/craft:do "describe your task"` routes any task automatically. `/craft:check` validates before you commit. Between these two, you can handle most workflows without memorizing anything else.
