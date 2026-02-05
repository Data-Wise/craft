# Documentation Gap-Fill Orchestration Plan

> **Branch:** `feature/docs-gap-fill`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-docs-gap-fill`

## Objective

Fill the documentation gaps identified in the v2.12.0 gap analysis. Focus on high-impact items: cookbook recipes, troubleshooting guides, and beginner tutorials.

## Phase Overview

| Phase | Task | Priority | Status |
| ----- | ---- | -------- | ------ |
| 1 | Cookbook: 5 beginner recipes | High | Pending |
| 2 | Troubleshooting: 8 critical recipes | High | Pending |
| 3 | Tutorial: "Your First 10 Minutes" | High | Pending |
| 4 | Commands: Individual pages for top 15 | Medium | Pending |
| 5 | Category pages: Add scenarios/depth | Medium | Pending |

## Phase 1: Beginner Cookbook Recipes (5)

Create in `docs/cookbook/common/`:

1. **find-the-right-command.md** — Using /craft:hub effectively
2. **update-single-doc.md** — Targeted docs:update for one category
3. **quick-code-checks.md** — code:lint default mode
4. **create-git-branch.md** — git:branch workflow
5. **view-project-architecture.md** — arch:analyze quick overview

Template for each recipe:

- TL;DR (30 seconds)
- Prerequisites
- Steps (with code blocks)
- Expected output
- What's next

## Phase 2: Troubleshooting Recipes (8)

Create in `docs/cookbook/troubleshooting/`:

1. **command-times-out.md** — Switching modes, understanding budgets
2. **wrong-command-output.md** — Mode mismatches, flag errors
3. **ci-workflow-fails.md** — Debugging GitHub Actions
4. **pre-commit-blocks-commit.md** — Understanding and fixing hook failures
5. **worktree-wont-create.md** — Path conflicts, branch conflicts
6. **broken-links-after-update.md** — Using docs:check-links
7. **claude-md-out-of-sync.md** — Running sync command
8. **mkdocs-build-fails.md** — Common mkdocs errors

## Phase 3: Beginner Tutorial

Create `docs/tutorials/TUTORIAL-first-10-minutes.md`:

- Install craft
- Verify with /craft:hub
- Run /craft:check
- Use /craft:do for first task
- Explore commands by category

## Phase 4: Individual Command Pages (Top 15)

Create in `docs/commands/` subdirectories:

- code/lint.md, code/debug.md, code/refactor.md
- test/run.md, test/coverage.md
- site/create.md, site/deploy.md
- git/sync.md, git/clean.md
- docs/update.md, docs/sync.md, docs/check.md
- arch/analyze.md, arch/plan.md
- workflow/brainstorm.md (enhance existing)

## Phase 5: Category Page Depth

Expand with real-world scenarios:

- docs/commands/code.md — "When to use lint vs check"
- docs/commands/docs.md — "Which docs command for what"
- docs/commands/site.md — "Site create vs site build"
- docs/commands/git.md — "Worktree vs branch decision"

## Acceptance Criteria

- [ ] All new pages build without mkdocs errors
- [ ] All internal links resolve
- [ ] mkdocs.yml nav updated for new pages
- [ ] Consistent formatting (TL;DR, progress indicators, next steps)
- [ ] Pre-commit hooks pass

## How to Start

```bash
cd ~/.git-worktrees/craft/feature-docs-gap-fill
claude
# Then: /craft:do "start phase 1 cookbook recipes"
```
