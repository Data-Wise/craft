---
description: Interactive git branch management assistant
category: git
arguments:
  - name: action
    description: Action to perform (new|switch|delete|sync) or empty to show status
    required: false
  - name: name
    description: Branch name (for new/switch/delete actions)
    required: false
  - name: dry-run
    description: Preview branch operations without executing
    required: false
    default: false
    alias: -n
---

# /craft:git:branch - Branch Management

Interactive assistant for creating, switching, and managing git branches safely.

## Usage

```bash
# Show branch overview
/craft:git:branch

# Preview branch creation
/craft:git:branch new feature/my-feature --dry-run

# Create new branch
/craft:git:branch new feature/my-feature

# Preview branch deletion
/craft:git:branch delete old-branch -n

# Delete branch safely
/craft:git:branch delete old-branch

# Switch branches
/craft:git:branch switch main

# Sync with remote
/craft:git:branch sync
```

## Dry-Run Mode

Preview branch operations before executing:

```bash
# Preview branch creation
/craft:git:branch new feature/auth --dry-run
/craft:git:branch new feature/auth -n

# Preview branch deletion
/craft:git:branch delete old-feature --dry-run
/craft:git:branch delete old-feature -n
```

### Example Output: Create

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Create Branch                                      │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Operations:                                                 │
│   - Create new branch: feature/auth                           │
│   - Based on: main (current HEAD)                             │
│   - Working directory: clean                                  │
│   - Switch to new branch after creation                       │
│                                                               │
│ 📊 Summary: 1 branch to create from main                       │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

### Example Output: Delete

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Delete Branch                                      │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Branch to delete:                                           │
│   - old-feature (merged to main)                              │
│   - Last commit: 2 weeks ago                                  │
│   - Safe to delete (fully merged)                             │
│                                                               │
│ ⚠ Warnings:                                                   │
│   • This operation is irreversible                             │
│   • Remote branch will also be deleted if exists              │
│                                                               │
│ 📊 Summary: 1 branch to delete (safe)                          │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

## Interactive Mode (No Arguments)

### Show Branch Overview

```
┌─────────────────────────────────────────────────────────────┐
│ 🌿 BRANCH STATUS                                            │
├─────────────────────────────────────────────────────────────┤
│ CURRENT: feature-auth *                                     │
│          2 commits ahead of origin                          │
│          Last commit: 2 hours ago                           │
├─────────────────────────────────────────────────────────────┤
│ LOCAL BRANCHES (5):                                         │
│   * feature-auth (current)                                  │
│     main (synced)                                           │
│     feature-profile (3 commits ahead)                       │
│     bugfix-login (merged, safe to delete)                   │
│     experiment-ui (stale, 30 days old)                      │
├─────────────────────────────────────────────────────────────┤
│ REMOTE BRANCHES (3):                                        │
│     origin/main                                             │
│     origin/feature-auth                                     │
│     origin/feature-profile                                  │
├─────────────────────────────────────────────────────────────┤
│ 💡 ACTIONS:                                                 │
│    n - Create new branch                                    │
│    s - Switch branch                                        │
│    c - Cleanup old branches                                 │
└─────────────────────────────────────────────────────────────┘
```

## Actions

### new - Create New Branch

**Create new branch from current state:**

```bash
# Check if working directory is clean
git status --short

# If clean, create branch
git checkout -b <name>

# If dirty, offer to commit first
```

**Interactive mode (no name provided):**

```
🌿 CREATE NEW BRANCH

Current branch: main
Based on: main (up to date)

Branch name: (e.g., feature/user-auth, fix/login-bug)
> feature-dashboard

✅ Creating branch: feature-dashboard

📝 Update .STATUS with new branch context? (y/n)
```

**If .STATUS exists, update it:**

```markdown
## 🌿 Current Branch
feature-dashboard

## 🎯 Branch Goal
[What are you working on in this branch?]
```

**Result:**

```
✅ Created and switched to: feature-dashboard

Ready to work! Run /next to see what to do.
```

### switch - Switch Branches

**Switch to existing branch:**

```bash
# Check for uncommitted changes
git status --short

# If changes exist, warn and offer options
```

**Warning if uncommitted:**

```
⚠️ You have uncommitted changes:
   M src/file.js
   ?? new-file.txt

Options:
1. Commit now (/commit)
2. Stash changes (git stash)
3. Discard changes (dangerous!)
4. Cancel switch

Choice:
```

**After switch:**

```
✅ Switched to: main

Branch status:
  • Synced with origin/main
  • Last commit: 1 day ago
  • Clean working tree

Recent activity on this branch:
  • 3 commits this week
  • Last: docs: update README

Run /git-recap for full history.
```

### delete - Delete Branch Safely

**Safe branch deletion:**

```bash
# Check if branch is merged
git branch --merged | grep <name>

# Check if branch has commits
git rev-list HEAD..<name> --count
```

**If not merged:**

```
⚠️ BRANCH NOT MERGED

Branch: feature-experiment
Commits not in main: 5
Last commit: 3 days ago

This branch has changes that will be lost!

Still delete? (yes/no/merge-first)
```

**If merged:**

```
✅ SAFE TO DELETE

Branch: bugfix-login
Status: Fully merged into main
Last activity: 2 weeks ago

Delete local branch? (y/n)
> y

Delete remote branch too? (y/n)
> y
```

**Execute:**

```bash
git branch -d <name>  # Safe delete
# or
git branch -D <name>  # Force delete

# If remote:
git push origin --delete <name>
```

### sync - Sync with Remote

**Sync current branch with remote:**

```bash
# Fetch latest
git fetch origin

# Check status
git status --branch

# Pull if behind
git pull origin $(git branch --show-current)
```

**Display:**

```
🔄 SYNCING: feature-auth

Fetching from origin...
✅ Fetched

Status:
  • Local: 2 commits ahead
  • Remote: 1 commit ahead
  • Diverged: Yes

⚠️ Your branch has diverged from origin

Options:
1. Merge (git pull)
2. Rebase (git pull --rebase)
3. View diff first
4. Cancel

Recommended: 2 (rebase)
```

## Smart Features

### 1. Branch Naming Suggestions

Based on context:

```
💡 BRANCH NAME SUGGESTIONS:

Based on .STATUS:
  • feature-user-dashboard
  • feat-dashboard-redesign

Common patterns:
  • feature/description
  • fix/bug-description
  • docs/what-changed
  • refactor/component-name

Enter name:
```

### 2. Stale Branch Detection

```
🧹 STALE BRANCHES DETECTED

These branches haven't been updated in 30+ days:

  • experiment-ui (45 days old)
    Last: WIP experiment
    Merged: No

  • temp-fix (60 days old)
    Last: temporary fix
    Merged: Yes (safe to delete)

Clean up? (y/n/review)
```

### 3. Branch Dependency Tracking

```
ℹ️ BRANCH DEPENDENCIES

feature-profile depends on:
  ↳ feature-auth (current branch)

If you delete feature-auth:
  ⚠️ feature-profile may have conflicts

Proceed? (y/n)
```

### 4. Auto-Update .STATUS

When switching branches:

```
📝 .STATUS on feature-auth says:
"Working on authentication system"

Update .STATUS for main branch context? (y/n)
```

## Branch Patterns

### Feature Branches

```
feature/<description>
feat/<description>

Examples:
  feature/user-authentication
  feat/dark-mode-toggle
  feature/api-integration
```

### Bug Fix Branches

```
fix/<bug-description>
bugfix/<bug-description>

Examples:
  fix/login-validation
  bugfix/memory-leak
  fix/null-pointer-error
```

### Documentation Branches

```
docs/<what-changed>

Examples:
  docs/api-reference
  docs/installation-guide
```

### Experimental Branches

```
experiment/<idea>
exp/<idea>

Examples:
  experiment/new-architecture
  exp/performance-optimization
```

## Integration

### With /focus

```
/craft:git:branch new feature-dashboard
/focus "build user dashboard"
[work...]
/commit
/done
```

### With /recap

```
/recap                        # See project status
/craft:git:branch switch main # Switch context
/recap                        # See main status
```

### With /pr-create

```
/craft:git:branch new feature-x
[work...]
/pr-create                    # Creates PR for current branch
```

## Key Behaviors

1. **Safe by default** - Warn before destructive actions
2. **Context-aware** - Update .STATUS when switching
3. **Helpful suggestions** - Suggest branch names
4. **Cleanup prompts** - Identify stale branches
5. **Merge-safe** - Check before deleting
6. **Dry-run support** - Preview all operations

## See Also

- `/craft:git:clean` - Clean merged branches
- `/craft:git:worktree` - Worktree management
- Template: `templates/dry-run-pattern.md`
- Utility: `utils/dry_run_output.py`
- Specification: `docs/specs/_archive/SPEC-dry-run-feature-2026-01-15.md`
