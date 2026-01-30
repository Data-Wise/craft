---
title: "Recipe: Setup Parallel Worktrees"
description: "Create isolated feature branches with automatic ORCHESTRATE.md and SPEC.md generation"
category: "cookbook"
level: "intermediate"
time_estimate: "8-10 minutes"
related:
  - ../../commands/git/worktree.md
  - ../../tutorials/TUTORIAL-worktree-setup.md
  - ../../reference/REFCARD-GIT-WORKTREE.md
---

# Recipe: Setup Parallel Worktrees

**Time:** 8-10 minutes
**Level:** Intermediate
**Prerequisites:** Git repository, feature to implement
**NEW:** v2.9.0 - Automatic ORCHESTRATE.md and SPEC.md generation

## Problem

I want to work on a feature branch in isolation without switching branches in my main repository. I also want automatic setup of orchestration files to plan my work.

## Solution

1. **Create worktree with automatic setup (v2.9.0)**

   ```bash
   /craft:git:worktree feature/user-authentication
   ```

   **What happens (v2.9.0 auto-setup):**

   ```
   ╭─ Worktree Creation ──────────────────────────╮
   │ Branch: feature/user-authentication           │
   │ Location: ~/.git-worktrees/craft/feature-...  │
   │                                               │
   │ Detected scope: feature implementation        │
   │ Auto-generating:                              │
   │ ✓ ORCHESTRATE.md (orchestration plan)         │
   │ ✓ SPEC.md (technical specification)           │
   │                                               │
   │ Creating worktree...                          │
   ╰───────────────────────────────────────────────╯
   ```

2. **Review generated files**

   The worktree automatically includes:

   **ORCHESTRATE.md** - Orchestration plan template:

   ```markdown
   # ORCHESTRATE - User Authentication Feature

   **Feature:** User authentication with JWT
   **Branch:** feature/user-authentication
   **Target:** dev
   **Mode:** phase (recommended for features)

   ---

   ## Phase 1: Foundation - Auth Backend

   ### Files to Create/Modify
   1. src/auth/jwt.ts (NEW) - JWT token handling
   2. src/auth/middleware.ts (NEW) - Auth middleware
   3. src/routes/auth.ts (NEW) - Auth routes

   ### Success Criteria
   - [ ] JWT generation working
   - [ ] Token validation working
   - [ ] Tests passing

   **Estimated:** 2-3 hours

   ---

   ## Phase 2: Integration - Connect to Existing System

   [Auto-generated template continues...]
   ```

   **SPEC.md** - Technical specification template:

   ```markdown
   # SPEC - User Authentication Feature

   **Feature:** User authentication with JWT
   **Branch:** feature/user-authentication
   **Target Release:** v2.10.0

   ---

   ## Overview

   Implement JWT-based authentication for the API.

   [Auto-generated template continues with sections for:
    - User Stories
    - Architecture Decisions
    - API Changes
    - Database Schema
    - Testing Strategy
    - Security Considerations
    - Success Criteria]
   ```

3. **Navigate to worktree**

   ```bash
   cd ~/.git-worktrees/craft/feature-user-authentication
   ```

   Or use the provided alias:

   ```bash
   # Shown in output after creation
   alias wt-user-auth="cd ~/.git-worktrees/craft/feature-user-authentication"
   ```

4. **Review and customize the plan**

   Edit ORCHESTRATE.md to:
   - Adjust phase breakdown
   - Add specific file paths for your project
   - Refine success criteria
   - Update time estimates

   Edit SPEC.md to:
   - Fill in architectural decisions
   - Add user stories
   - Define API contracts
   - Specify test requirements

5. **Start implementation**

   With your plan in place:

   ```bash
   # Option 1: Use orchestrator with your plan
   /craft:orchestrate --file ORCHESTRATE.md

   # Option 2: Work phase by phase manually
   # Refer to ORCHESTRATE.md as you work
   # Check off tasks as you complete them
   ```

6. **When feature is complete**

   ```bash
   # In worktree directory
   git push -u origin feature/user-authentication
   gh pr create --base dev

   # Then clean up worktree
   cd ~/projects/dev-tools/craft  # Back to main repo
   git worktree remove ~/.git-worktrees/craft/feature-user-authentication
   ```

## Explanation

### Automatic File Generation (v2.9.0)

The worktree command detects your branch pattern and generates appropriate files:

**Branch patterns recognized:**

| Pattern | Detected Scope | Generated Files |
|---------|----------------|-----------------|
| `feature/*` | Feature implementation | ORCHESTRATE.md (phase mode), SPEC.md |
| `fix/*` | Bug fix | SPEC.md (focused on fix description) |
| `docs/*` | Documentation update | ORCHESTRATE.md (docs phases) |
| `refactor/*` | Code refactoring | ORCHESTRATE.md (refactor phases), SPEC.md |
| `experiment/*` | Experimental work | SPEC.md (hypothesis, experiments) |

### ORCHESTRATE.md Template

Auto-generated based on:

- Branch name (extracts feature name)
- Project type (detects craft plugin, R package, etc.)
- Common phase patterns for that scope

**For feature branches:**

- Phase 1: Foundation/Backend
- Phase 2: Integration
- Phase 3: Testing
- Phase 4: Documentation

**For docs branches:**

- Phase 1: Content update
- Phase 2: Link validation
- Phase 3: Build verification
- Phase 4: Deployment

### SPEC.md Template

Includes sections:

- Overview
- User Stories (for features)
- Architecture Decisions
- API Changes
- Testing Strategy
- Success Criteria
- Dependencies
- Rollout Plan

## Variations

- **Create worktree without auto-generation:**

  ```bash
  /craft:git:worktree feature/my-feature --no-setup
  ```

  Creates worktree only, no ORCHESTRATE.md or SPEC.md

- **Create worktree with custom location:**

  ```bash
  /craft:git:worktree feature/my-feature --path ~/my-worktrees/my-feature
  ```

  Uses custom directory instead of default ~/.git-worktrees

- **Create from specific base branch:**

  ```bash
  /craft:git:worktree feature/my-feature --from main
  ```

  Branches from main instead of dev

- **Generate orchestration file in existing worktree:**

  ```bash
  cd ~/existing-worktree
  /craft:git:worktree --generate-orch
  ```

  Adds ORCHESTRATE.md to existing worktree

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "ORCHESTRATE.md not generated" | Older version (<v2.9.0), update craft plugin |
| "Generated files have wrong phase structure" | Edit them manually, templates are starting points |
| "Worktree location hard to remember" | Use the provided alias shown in output |
| "Want different base branch" | Use --from flag: /craft:git:worktree feature/x --from main |
| "ORCHESTRATE.md doesn't match my project" | Templates are generic, customize for your needs |
| "How to use orchestrator with ORCHESTRATE.md?" | Run: /craft:orchestrate --file ORCHESTRATE.md |

## Advanced Workflows

### Workflow 1: Parallel Feature Development

Work on 2 features simultaneously:

```bash
# Main repo stays on dev/main
cd ~/projects/dev-tools/craft

# Create first feature worktree
/craft:git:worktree feature/auth
# Location: ~/.git-worktrees/craft/feature-auth

# Create second feature worktree
/craft:git:worktree feature/payments
# Location: ~/.git-worktrees/craft/feature-payments

# Work on auth
cd ~/.git-worktrees/craft/feature-auth
# Customize ORCHESTRATE.md, start work

# Switch to payments (different terminal)
cd ~/.git-worktrees/craft/feature-payments
# Customize ORCHESTRATE.md, start work

# Both features in progress, no branch switching!
```

### Workflow 2: Experiment Without Disruption

Test a risky refactor:

```bash
/craft:git:worktree experiment/new-architecture

# Work in experiment worktree
cd ~/.git-worktrees/craft/experiment-new-architecture

# If experiment succeeds: merge to dev
git push -u origin experiment/new-architecture
gh pr create --base dev

# If experiment fails: just delete worktree
cd ~/projects/dev-tools/craft
git worktree remove ~/.git-worktrees/craft/experiment-new-architecture --force
git branch -D experiment/new-architecture
# Main repo unaffected!
```

### Workflow 3: Review PR in Isolated Worktree

Review someone's PR without switching your main branch:

```bash
# Create worktree from PR branch
/craft:git:worktree review/pr-123 --from origin/feature/their-feature

cd ~/.git-worktrees/craft/review-pr-123
# Test their changes, run tests, review code

# When done, remove worktree
cd ~/projects/dev-tools/craft
git worktree remove ~/.git-worktrees/craft/review-pr-123
```

## Example: Complete Feature Workflow

```bash
# Step 1: Create worktree with auto-setup
/craft:git:worktree feature/oauth

# Output shows:
# ✓ ORCHESTRATE.md generated (4 phases)
# ✓ SPEC.md generated
# ✓ Worktree created at ~/.git-worktrees/craft/feature-oauth
# ✓ Alias: wt-oauth

# Step 2: Navigate and plan
cd ~/.git-worktrees/craft/feature-oauth

# Step 3: Review and customize ORCHESTRATE.md
# Edit phase breakdown to match your project structure

# Step 4: Execute with orchestrator
/craft:orchestrate --file ORCHESTRATE.md --mode phase

# Step 5: Work through phases with checkpoints
# Orchestrator guides you through each phase
# Checkpoints after each phase for review

# Step 6: Complete and create PR
git push -u origin feature/oauth
gh pr create --base dev

# Step 7: Clean up after merge
cd ~/projects/dev-tools/craft
git worktree remove ~/.git-worktrees/craft/feature-oauth
git branch -d feature/oauth
```

## Related

- [Git Worktree Command](../../commands/git/worktree.md) — Full command reference
- [Worktree Setup Tutorial](../../tutorials/TUTORIAL-worktree-setup.md) — Complete tutorial
- [Git Worktree Quick Reference](../../reference/REFCARD-GIT-WORKTREE.md) — Quick reference
- [Advanced Worktree Patterns](../../guide/worktree-advanced-patterns.md) — Complex scenarios
- [Orchestrate Command](../../commands/orchestrate.md) — Using orchestrator with ORCHESTRATE.md
