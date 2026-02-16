# Tutorial: Git Worktree Setup and Workflow

> **What you'll learn:** How to use git worktrees with craft's auto-setup feature for parallel development without branch switching.
>
> **Level:** Beginner to Intermediate
>
> **Time:** 15-20 minutes
>
> **Prerequisites:** Basic git knowledge (branches, commits, merges)

---

## What You'll Learn

1. What worktrees are and when to use them
2. How to set up worktrees for your project
3. How to create a worktree with auto-setup
4. What workflow files get created and why
5. How to complete and clean up after finishing
6. Real-world scenarios and troubleshooting

---

## Part 1: Understanding Worktrees

### What's a Worktree?

A worktree is a separate folder where a different branch is checked out. Instead of switching branches in one folder, each branch gets its own dedicated folder.

**Traditional workflow (branch switching):**

```
~/projects/craft/
  └── main branch (clean)
      Switch to feature/auth
      └── feature/auth branch (working)
          Stash changes
          Switch to fix/urgent-bug
          └── fix/urgent-bug branch
```

**Worktree workflow (no switching):**

```
~/projects/craft/
  └── main branch (always clean)

~/.git-worktrees/craft/
  ├── feature-auth/        ← feature/auth branch
  └── fix-urgent-bug/      ← fix/urgent-bug branch
```

### When to Use Worktrees

| Scenario | Without Worktree | With Worktree |
|----------|------------------|---------------|
| **Quick PR review** | Stash → switch → review → switch → unstash | Open worktree in separate terminal |
| **Urgent hotfix mid-feature** | Stash → switch → fix → switch → unstash | Create hotfix worktree, keep working |
| **Dev server running** | Stop server → switch → restart | Run server in worktree A, work in worktree B |
| **Claude Code sessions** | One session, one branch | Multiple sessions, multiple branches |

**TL;DR:** If you switch branches more than once a day, worktrees will save you hours.

---

## Part 2: First-Time Setup

### Step 2.1: Create the Worktree Folder

```bash
/craft:git:worktree setup
```

**Output:**

```
Worktree Setup Plan:
  Project: craft
  Main repo: ~/projects/dev-tools/craft
  Worktree folder: ~/.git-worktrees/craft/

  This will create the parent folder for all worktrees.

? Proceed with worktree setup?
  > Yes - Create folder (Recommended)
    Choose different location
    Cancel

  [1/1] Creating ~/.git-worktrees/craft/... ✅

Setup complete!
Next: /craft:git:worktree create feature/my-feature
```

**What happened:**

- Created `~/.git-worktrees/craft/` directory
- This folder will contain all future worktrees for this project
- Main repo stays at `~/projects/dev-tools/craft` on `main` branch

### Step 2.2: Verify Main Repo Branch

```bash
cd ~/projects/dev-tools/craft
git branch --show-current
# Should show: main
```

**IMPORTANT:** The main repo should always stay on `main` (or `dev` if that's your integration branch). Never do feature work in the main repo after setting up worktrees.

!!! tip "Branch Protection (v2.16.0)"
    Craft includes a `branch-guard.sh` PreToolUse hook that **automatically prevents** accidental edits on protected branches. With it enabled, `main` blocks all edits and `dev` blocks new code files — so even if you forget to switch to a worktree, the guard catches it. See `/craft:git:protect` and `/craft:git:unprotect`.

---

## Part 3: Creating Your First Worktree

### Step 3.1: Create a Feature Worktree

```bash
/craft:git:worktree create feature/add-auth
```

**Output (with new interactive preview):**

```
Worktree Setup Plan:
  Project: craft
  Action: create
  Branch: feature/add-auth
  Base: dev
  Location: ~/.git-worktrees/craft/feature-add-auth

  Steps:
  1. Create worktree directory
  2. Create branch from dev
  3. Install dependencies (Python detected)
  4. Auto-setup workflow files (scope: medium)

? Proceed with this worktree setup?
  > Yes - Create worktree (Recommended)
    Change base branch (currently: dev)
    Change location
    Cancel
```

Choose **"Yes - Create worktree"**.

**Execution:**

```
[1/4] Creating directory... ✅
  Created: ~/.git-worktrees/craft/feature-add-auth

[2/4] Creating branch from dev... ✅
  Branch: feature/add-auth
  Base: dev
  Commits ahead: 0

[3/4] Installing dependencies... ✅
  Detected: Python (pyproject.toml)
  Ran: pip install -e .
  Installed: 23 packages

[4/4] Auto-setup workflow files...
```

---

## Part 4: Auto-Setup and Scope Detection (NEW)

### Step 4.1: Scope Detection Prompt

After creating the worktree, craft detects the scope from your branch pattern:

```
Scope Detection:
  Branch: feature/add-auth
  Pattern: feature/* → Medium scope

Medium scope features typically:
  - Add new functionality (not just bug fixes)
  - Require planning across multiple files
  - Take 2-8 hours of focused work
  - Need orchestration or spec documents

? What workflow files should I create?
  > Create ORCHESTRATE file (Recommended)
    Multi-phase project (ORCHESTRATE + SPEC + .STATUS + CLAUDE.md)
    Minimal (no files)
    Custom
```

**Scope Detection Rules:**

| Branch Pattern | Detected Scope | Auto-Creates |
|----------------|---------------|--------------|
| `fix/*` | Small (< 2 hours) | Nothing |
| `feature/*` | Medium (2-8 hours) | ORCHESTRATE file |
| `v*` (e.g., `v2.9.0`) | Release | ORCHESTRATE + SPEC |
| User chooses "Multi-phase" | Large (> 8 hours) | All files |

### Step 4.2: ORCHESTRATE File Creation

Choose **"Create ORCHESTRATE file"**:

```
Creating workflow files...

  ✅ ORCHESTRATE-add-auth.md (template created)

Template includes:
  - Feature overview
  - Acceptance criteria
  - Implementation phases
  - How to start
  - Testing checklist

Worktree ready!
  Location: ~/.git-worktrees/craft/feature-add-auth
  Branch: feature/add-auth
  Files: ORCHESTRATE-add-auth.md

Next steps:
  1. cd ~/.git-worktrees/craft/feature-add-auth
  2. Review and customize ORCHESTRATE-add-auth.md
  3. Start development
```

### Step 4.3: What the ORCHESTRATE Template Contains

```markdown
# Feature: Add Auth

**Status:** WIP
**Branch:** feature/add-auth
**Target:** Implement OAuth 2.0 authentication

## Overview

[Describe the feature and its purpose]

## Acceptance Criteria

- [ ] Users can sign in with OAuth 2.0
- [ ] Sessions persist across browser restarts
- [ ] Logout functionality works correctly
- [ ] Tests cover happy path and edge cases

## Implementation Phases

### Phase 1: Backend Routes (2 hours)
- [ ] Create `/auth/login` endpoint
- [ ] Create `/auth/logout` endpoint
- [ ] JWT token generation and validation

### Phase 2: Frontend Integration (3 hours)
- [ ] Login page UI
- [ ] Session management
- [ ] Protected route guards

### Phase 3: Testing (2 hours)
- [ ] Unit tests for auth endpoints
- [ ] Integration tests for OAuth flow
- [ ] E2E tests for user login/logout

## How to Start

1. Review this plan and adjust phases
2. Start with Phase 1
3. Check off items as you complete them
4. Run `/craft:check` before committing
5. Create PR when all acceptance criteria met

## Notes

[Add design decisions, dependencies, or blockers here]
```

**Why this is useful:**

- Gives you a structured starting point
- Breaks work into phases
- Tracks acceptance criteria
- Serves as PR description draft

---

## Part 5: Working in the Worktree

### Step 5.1: Navigate to the Worktree

```bash
cd ~/.git-worktrees/craft/feature-add-auth
```

**Verify you're on the right branch:**

```bash
git branch --show-current
# Should show: feature/add-auth
```

### Step 5.2: Customize the ORCHESTRATE File

```bash
# Open in your editor
code ORCHESTRATE-add-auth.md  # VS Code
vim ORCHESTRATE-add-auth.md   # Vim
```

Fill in the details based on your feature requirements.

### Step 5.3: Start Development

```bash
# Start Claude Code session
claude

# Or work manually
git status
# Make changes to files
git add .
git commit -m "feat: add OAuth login endpoint"
```

### Step 5.4: Track Progress

As you work, check off items in `ORCHESTRATE-add-auth.md`:

```diff
### Phase 1: Backend Routes
- [x] Create `/auth/login` endpoint
- [x] Create `/auth/logout` endpoint
- [ ] JWT token generation and validation
```

---

## Part 6: Multi-Phase Projects

### Step 6.1: When to Use Multi-Phase Setup

For larger features (> 8 hours), choose **"Multi-phase project"** during auto-setup:

```bash
/craft:git:worktree create feature/v2.9.0
```

**Scope detection:**

```
Scope Detection:
  Branch: feature/v2.9.0
  Pattern: v* → Release scope

? What workflow files should I create?
    Create ORCHESTRATE file
  > Multi-phase project (ORCHESTRATE + SPEC + .STATUS + CLAUDE.md)
    Minimal (no files)
    Custom
```

Choose **"Multi-phase project"**.

### Step 6.2: Files Created

```
Creating workflow files...

  ✅ ORCHESTRATE-v2.9.0.md
  ✅ docs/specs/SPEC-v2.9.0-2026-01-29.md
  ✅ .STATUS (updated with worktree info)
  ✅ CLAUDE.md (updated with active worktrees)

Files created:
  - ORCHESTRATE-v2.9.0.md — Task plan with phases
  - docs/specs/SPEC-v2.9.0-2026-01-29.md — Requirements and design
  - .STATUS — Marks branch as WIP in project status
  - CLAUDE.md — Adds worktree to "Active Development" section
```

**SPEC file template:**

```markdown
# SPEC: v2.9.0 Release

**Created:** 2026-01-29
**Status:** Draft
**Branch:** feature/v2.9.0

## Requirements

### Functional Requirements
- FR1: [Requirement 1]
- FR2: [Requirement 2]

### Non-Functional Requirements
- NFR1: Performance targets
- NFR2: Security requirements

## Design Decisions

### Decision 1: [Topic]
**Options considered:** A, B, C
**Chosen:** B
**Rationale:** [Why B is best]

## Implementation Plan

See ORCHESTRATE-v2.9.0.md for detailed task breakdown.

## Testing Strategy

- Unit tests: [Scope]
- Integration tests: [Scope]
- E2E tests: [Scenarios]
```

---

## Part 7: Finishing and Cleanup

### Step 7.1: Pre-Finish Checklist

Before running `/craft:git:worktree finish`, verify:

```bash
# 1. All changes committed
git status
# Should show: nothing to commit, working tree clean

# 2. Branch up to date with dev
git fetch origin dev
git rebase origin/dev

# 3. Tests pass
/craft:check
```

### Step 7.2: Run Finish Workflow

```bash
/craft:git:worktree finish
```

**Output:**

```
Finish Feature Workflow:
  Branch: feature/add-auth
  Commits: 7 since branching from dev
  Target: dev

  Steps:
  1. Run tests
  2. Generate changelog entry
  3. Create pull request

? Proceed with finish workflow?
  > Yes - Complete feature (Recommended)
    Skip tests (faster)
    Draft PR (don't notify reviewers)
    Cancel

[1/3] Running tests... ✅
  Detected: Python (pytest)
  Ran: pytest -v
  Result: 47/47 passed

[2/3] Generating changelog... ✅
  Branch type: feature/* → "Added" section
  Entry: "Add OAuth 2.0 authentication system"

[3/3] Creating pull request... ✅
  Title: feat: Add OAuth 2.0 authentication
  Base: dev
  PR: https://github.com/Data-Wise/craft/pull/42

Finish workflow complete!

Next steps:
  1. Review PR: gh pr view 42
  2. Request reviews
  3. After merge: /craft:git:worktree clean
```

### Step 7.3: Clean Up After Merge

After the PR is merged:

```bash
# Go back to main repo
cd ~/projects/dev-tools/craft

# Pull the merged changes
git checkout dev
git pull origin dev

# Clean up the merged worktree
/craft:git:worktree clean
```

**Output:**

```
Cleaning merged worktrees...

Checking: feature-add-auth
  Branch: feature/add-auth
  Merged: ✓ (merged into dev)
  Location: ~/.git-worktrees/craft/feature-add-auth

? Remove worktree for merged branch feature/add-auth?
  > Yes - Remove (Recommended)
    Keep for reference
    Skip

[1/2] Removing worktree... ✅
  Removed: ~/.git-worktrees/craft/feature-add-auth

[2/2] Deleting local branch... ✅
  Deleted: feature/add-auth

Cleanup complete!
  Removed: 1 worktree
  Remaining: 0 active worktrees
```

---

## Part 8: Real-World Scenarios

### Scenario 1: Urgent Hotfix While Working on Feature

```bash
# You're working in feature worktree
cd ~/.git-worktrees/craft/feature-add-auth

# Urgent bug comes in
# Don't stash! Just create a new worktree:
cd ~/projects/dev-tools/craft
/craft:git:worktree create fix/urgent-login-bug

# Work on hotfix in separate folder
cd ~/.git-worktrees/craft/fix-urgent-login-bug
# Fix the bug, commit, create PR

# Go back to feature work
cd ~/.git-worktrees/craft/feature-add-auth
# Your work is exactly as you left it!
```

### Scenario 2: You Forgot to Create a Worktree

```bash
# You're on feature/add-auth in the main repo with uncommitted work
cd ~/projects/dev-tools/craft
git branch --show-current
# Oops: feature/add-auth (should be on main!)

# Use the "move" action to fix this
/craft:git:worktree move
```

**Output:**

```
Move Branch to Worktree:
  Current branch: feature/add-auth
  Uncommitted files: 15

  This will:
  1. Stash your work
  2. Switch main repo to 'main'
  3. Create worktree for feature/add-auth
  4. Restore your stashed work in the worktree

? Move feature/add-auth to worktree?
  > Yes - Move (Recommended)
    Cancel

[1/5] Stashing work... ✅
  Stashed: 15 files

[2/5] Switching to main... ✅
  Main repo now on: main

[3/5] Creating worktree... ✅
  Location: ~/.git-worktrees/craft/feature-add-auth

[4/5] Restoring work... ✅
  Applied stash: 15 files restored

[5/5] Installing dependencies... ✅

Done! Your setup:
  Main repo: ~/projects/dev-tools/craft (main)
  Feature work: ~/.git-worktrees/craft/feature-add-auth

All 15 uncommitted files are now in the worktree.
```

### Scenario 3: Running Dev Servers in Parallel

```bash
# Create worktrees for frontend and backend work
/craft:git:worktree create feature/frontend-redesign
/craft:git:worktree create feature/api-v2

# Terminal 1: Run frontend dev server
cd ~/.git-worktrees/craft/feature-frontend-redesign
npm run dev -- --port 3000

# Terminal 2: Run backend dev server
cd ~/.git-worktrees/craft/feature-api-v2
npm run dev -- --port 4000

# Terminal 3: Code changes
cd ~/.git-worktrees/craft/feature-frontend-redesign
claude  # Work on frontend while both servers run
```

---

## Part 9: Troubleshooting

### Issue: "Branch already exists"

```bash
# Error
git: branch 'feature/add-auth' already exists

# Solution: Use existing branch
/craft:git:worktree create feature/add-auth --use-existing

# Or: Delete and recreate
git branch -D feature/add-auth
/craft:git:worktree create feature/add-auth
```

### Issue: Dependencies Not Installed

```bash
# After creating worktree, dependencies are missing

# Solution: Install manually
cd ~/.git-worktrees/craft/feature-add-auth
/craft:git:worktree install

# Or run project-specific install
npm install        # Node.js
pip install -e .   # Python
```

### Issue: Can't Delete Worktree

```bash
# Error
fatal: worktree still has modifications

# Solution 1: Force remove
git worktree remove ~/.git-worktrees/craft/feature-add-auth --force

# Solution 2: Commit or discard changes first
cd ~/.git-worktrees/craft/feature-add-auth
git status
git add . && git commit -m "WIP"
# Then remove
```

### Issue: Worktree Path Too Long (macOS)

```bash
# Path is too long for macOS
~/.git-worktrees/craft/feature-very-long-descriptive-branch-name/

# Solution: Use shorter location
/craft:git:worktree create feature/short-name
```

---

## After Brainstorm: Creating ORCHESTRATE Files

If you used `/brainstorm` to plan a feature and captured a spec, you can create an ORCHESTRATE file and worktree in one step:

### From Brainstorm to Worktree

```bash
# 1. Brainstorm produces a spec
/brainstorm d:8 f "user notifications"
# → BRAINSTORM-notifications-2026-02-15.md saved
# → "Capture as spec?" → Yes
# → docs/specs/SPEC-notifications-2026-02-15.md saved

# 2. Create ORCHESTRATE + worktree from the spec
/craft:orchestrate:plan docs/specs/SPEC-notifications-2026-02-15.md

# Output:
# Orchestration Plan:
#   Spec: SPEC-notifications-2026-02-15.md
#   Phases found: 3 (setup, implementation, integration)
#   Branch: feature/notifications
#   Worktree: ~/.git-worktrees/craft/feature-notifications
#
# ? Proceed?
#   > Yes - Create ORCHESTRATE + worktree (Recommended)
#     ORCHESTRATE only (no worktree)
#     Modify phases
#     Cancel
#
# Created:
#   ✅ ORCHESTRATE-notifications.md (in worktree root)
#   ✅ Worktree at ~/.git-worktrees/craft/feature-notifications
#   ✅ .STATUS updated with worktree entry

# 3. Start working
cd ~/.git-worktrees/craft/feature-notifications
claude
# → "Read ORCHESTRATE-notifications.md and start Phase 1"
```

### What the ORCHESTRATE File Contains

The generated ORCHESTRATE file includes:

- **Objective** — pulled from spec summary
- **Phase breakdown** — with tasks, priorities, and effort estimates
- **Friction prevention** — based on insights from past sessions
- **Acceptance criteria** — from the spec
- **Verification commands** — test and validation commands for the project
- **Session instructions** — how to start, what to read first, phase-by-phase guidance

### Without a Spec

If you don't have a spec, `/craft:orchestrate:plan` will scan for available specs and brainstorms:

```bash
/craft:orchestrate:plan

# Output:
# Available specs:
#   1. SPEC-auth-2026-02-10.md (no ORCHESTRATE yet)
#   2. SPEC-dashboard-2026-02-12.md (has ORCHESTRATE)
#
# Brainstorms without specs:
#   3. BRAINSTORM-caching-2026-02-14.md (offer to create spec first)
#
# ? Which one?
```

---

## Summary

You've learned:

- What worktrees are and when to use them (parallel development without branch switching)
- How to set up worktrees for your project (`/craft:git:worktree setup`)
- How to create a worktree with auto-setup (`/craft:git:worktree create`)
- What scope detection does and what files it creates (ORCHESTRATE, SPEC, .STATUS, CLAUDE.md)
- How to work in a worktree (customize ORCHESTRATE, track progress)
- How to finish and clean up (`/craft:git:worktree finish`, `/craft:git:worktree clean`)
- Real-world scenarios (hotfixes, forgot to create worktree, parallel dev servers)

---

## Next Steps

- **Command reference:** [/craft:git:worktree](../commands/git/worktree.md) — Full documentation
- **Quick reference:** [Git Worktree Refcard](../reference/REFCARD-GIT-WORKTREE.md) — Cheat sheet
- **Workflow guide:** [Git Feature Workflow](../workflows/git-feature-workflow.md) — Complete git workflow
- **Pattern guide:** [Interactive Commands Guide](../guide/interactive-commands.md) — How this pattern works
