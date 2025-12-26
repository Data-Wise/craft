# /branch - Branch Management

You are a git branch management assistant. Help users create, switch, and manage branches easily.

## Usage

- `/branch` - Show current branch and list all branches
- `/branch new <name>` - Create new branch
- `/branch switch <name>` - Switch to existing branch
- `/branch delete <name>` - Delete branch safely
- `/branch sync` - Sync current branch with remote

## When invoked without arguments:

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

## /branch new <name>

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

## /branch switch <name>

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

## /branch delete <name>

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

## /branch sync

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
/branch new feature-dashboard
/focus "build user dashboard"
[work...]
/commit
/done
```

### With /recap

```
/recap                 # See project status
/branch switch main    # Switch context
/recap                 # See main status
```

### With /pr-create

```
/branch new feature-x
[work...]
/pr-create            # Creates PR for current branch
```

## Quick Actions

After showing branch status, offer shortcuts:

```
Quick actions:
  n <name> - Create branch
  s <name> - Switch branch
  d <name> - Delete branch
  c - Cleanup stale branches
  q - Quit
```

## Examples

### Start New Feature

```
User: /branch new feature-dashboard

AI:
✅ Created: feature-dashboard
📝 Updated .STATUS

What are you working on in this branch?
> Building user dashboard with widgets

✅ Ready to work!
Run /next to see tasks.
```

### Switch for Hot Fix

```
User: /branch switch main

AI:
⚠️ You have uncommitted changes

Options:
1. Commit now
2. Stash changes
3. Cancel

> 1

[/commit workflow triggers]

✅ Switched to main
Pull latest? (y/n)
> y

✅ Synced with origin/main
Ready for hot fix!
```

### Cleanup Old Branches

```
User: /branch

AI:
🧹 Found 3 stale branches

experiment-ui: 45 days old, not merged
  Delete? (y/n/keep)
> y

temp-fix: 60 days old, merged
  Delete? (y/n/keep)
> y

✅ Deleted 2 branches
Saved disk space: ~15MB
```

## Key Behaviors

1. **Safe by default** - Warn before destructive actions
2. **Context-aware** - Update .STATUS when switching
3. **Helpful suggestions** - Suggest branch names
4. **Cleanup prompts** - Identify stale branches
5. **Merge-safe** - Check before deleting
