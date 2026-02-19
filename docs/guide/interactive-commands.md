# Interactive Commands: The "Show Steps First" Pattern

> **TL;DR** (30 seconds)
>
> - **What:** Commands now show their plan before executing and ask for confirmation
> - **Why:** No more skipped steps — you see exactly what will happen
> - **How:** Step 0 (plan) → Step 0.5 (confirm) → Steps 1-N (execute) → Summary
> - **Applies to:** `/craft:orchestrate`, `/craft:check`, `/craft:docs:update`, `/craft:git:worktree`

---

## Overview

Starting in this release, the 4 most-used craft commands follow a consistent **"Show Steps First"** pattern. Every command:

1. **Shows** a numbered plan of what it will do
2. **Asks** for confirmation before executing
3. **Executes** with progress indicators
4. **Summarizes** results with next steps

This addresses the core pain point: **commands used to skip documented steps** because there was no accountability mechanism. Now the plan is visible and you decide whether to proceed.

---

## The Pattern

Every interactive command follows this structure:

```
Step 0:   Print what the command WILL do (numbered steps)
Step 0.5: Ask to proceed (confirm/modify/cancel)
Steps 1-N: Execute with progress indicators
Step N+1: Summary with next steps
```

### Example: /craft:check

```
/craft:check

Pre-flight Check Plan:
  Project: craft (Claude Plugin)
  Mode: default
  Branch: feature/auth

  Checks to run:
  1. Git status (clean working tree?)
  2. Unit tests (python3 tests/test_craft_plugin.py)
  3. Markdown lint (30 rules)

? Run these pre-flight checks?
  > Yes - Run all (Recommended)
    Skip lint (faster)
    Skip external links (faster)
    Dry run (show commands only)

  [1/3] Git status... clean
  [2/3] Unit tests... 13/13 passed
  [3/3] Markdown lint... 0 issues

  Results: 3/3 checks passed
  Next steps: Ready to commit
```

---

## Commands Using This Pattern

### /craft:orchestrate

| Step | What happens |
|------|-------------|
| Step 0 | Mode selection (if not specified) |
| Step 1 | Task analysis — shows subtask table with waves |
| Step 2 | Confirmation — proceed/modify/change mode/cancel |
| Steps 3-N | Execute waves with agent spawning |
| Checkpoints | After each wave — continue/review/modify/stop |
| Summary | Results with next steps |

**Key feature:** Wave checkpoints let you pause between groups of agents, review results, and decide whether to continue or modify the next wave.

### /craft:check

| Step | What happens |
|------|-------------|
| Step 0 | Show check plan (project type, checks to run) |
| Step 0.5 | Confirm — run all/skip lint/skip links/dry run |
| Steps 1-N | Execute checks with pass/fail per step |
| Summary | Total results, issues found, next steps |

**Key feature:** The `--for` flag (commit/pr/release/deploy) adjusts which checks run and their depth.

### /craft:docs:update

| Step | What happens |
|------|-------------|
| Step 0 | Detection — scan what needs updating (9 categories) |
| Step 0.5 | Confirm approach — interactive/auto-apply/preview/cancel |
| Steps 1-N | Execute per category with progress |
| Summary | Files changed, validation results |

**Key feature:** The `--post-merge` flag runs a specialized 5-phase pipeline after PR merges, auto-fixing safe categories and prompting for manual ones.

### /craft:git:worktree

| Step | What happens |
|------|-------------|
| Step 0 | Show setup plan (branch, location, steps) |
| Step 0.5 | Confirm — create/change branch/change location/cancel |
| Steps 1-N | Execute with progress indicators |
| Auto-setup | Scope detection → create workflow files |
| Summary | Worktree location, next steps |

**Key feature:** After creating a worktree, auto-detects scope from the branch name pattern and offers to create ORCHESTRATE and SPEC templates.

---

## Mode Differences

Each mode produces visibly different output across commands:

### Orchestrate Modes

| Behavior | default | debug | optimize | release |
|----------|---------|-------|----------|---------|
| Plan display | Summary | Step traces | Parallel map | Full audit |
| Checkpoints | Per wave | Every step | Wave end | Every step |
| Agent output | Summary | Verbose | Summary | Full + diff |

### Check Modes

| Check | default | debug | release |
|-------|---------|-------|---------|
| Tests | Quick | Verbose | Full + coverage |
| Lint | Changed files | All files | All + strict |
| Links | Skip external | Internal only | All links |

---

## Confirmation Options

All commands offer consistent confirmation options:

| Option | Available in | Effect |
|--------|-------------|--------|
| **Proceed (Recommended)** | All commands | Execute the plan as shown |
| **Modify** | orchestrate, worktree | Change the plan before executing |
| **Skip** | check | Skip specific checks for speed |
| **Dry run** | check, docs:update | Show commands without executing |
| **Cancel** | All commands | Exit without changes |

---

## End-to-End Example: Feature Pipeline

This shows the full interactive flow from brainstorm to PR, demonstrating how each command's "Show Steps First" pattern connects:

```bash
# Step 1: Brainstorm the feature
/brainstorm d:8 "real-time notifications"
# → Asks 8 questions across categories
# → Saves BRAINSTORM-notifications-2026-02-15.md
# → Offers to capture spec

# Step 2: Create orchestration from spec (v2.21.0)
/craft:orchestrate:plan docs/specs/SPEC-notifications.md
#
# Plan:
#   1. Parse spec for phases (found 3 phases)
#   2. Generate ORCHESTRATE-notifications.md
#   3. Create worktree at ~/.git-worktrees/craft/feature-notifications
#   4. Update .STATUS with worktree entry
#
# ? Proceed with this plan?
#   > Yes - Create ORCHESTRATE + worktree (Recommended)
#     ORCHESTRATE only (no worktree)
#     Modify phases
#     Cancel

# Step 3: Work in the worktree
cd ~/.git-worktrees/craft/feature-notifications
claude
# → Read ORCHESTRATE file, implement phase by phase
# → Each phase: implement → test → commit → checkpoint

# Step 4: Pre-flight check before PR
/craft:check --for pr
#
# Pre-flight Check Plan:
#   1. Unit tests (47 tests)
#   2. Integration tests
#   3. Markdown lint
#   4. Link validation
#   5. Count validation
#
# ? Run these checks?
#   > Yes - Run all (Recommended)
#
# Results: 5/5 passed

# Step 5: Finish and create PR
/craft:git:worktree finish
#
# Plan:
#   1. Run full test suite
#   2. Generate changelog from 12 commits
#   3. Remove ORCHESTRATE files (merge cleanup)
#   4. Create PR to dev with AI-generated description
#
# → PR #42 created: https://github.com/user/repo/pull/42
```

---

## Tips

- **First run:** Try each command once to see the preview format
- **Skip confirmation:** Not currently supported — confirmation is mandatory to prevent skipped steps
- **Mode flags:** Use explicit mode flags (`/craft:orchestrate "task" debug`) to skip the mode selection prompt
- **Dry run:** Use `--dry-run` where available to preview without risk

---

## See Also

- **Orchestration guide:** [Orchestrator Deep Dive](orchestrator.md)
- **Tutorial:** [Interactive Orchestration Tutorial](../tutorials/interactive-orchestration.md)
- **Check command:** [/craft:check](../commands/check.md)
- **Docs update:** [/craft:docs:update](../commands/docs/update.md)
- **Worktree:** [/craft:git:worktree](../commands/git/worktree.md)
