---
description: Smart git synchronization with remote repositories
category: git
arguments:
  - name: dry-run
    description: Preview sync operations without executing
    required: false
    default: false
    alias: -n
---

# /craft:git:sync - Smart Git Sync

Safe, intelligent syncing with remote repositories.

## Usage

```bash
# Preview sync operations
/craft:git:sync --dry-run
/craft:git:sync -n

# Execute sync
/craft:git:sync
```

## Dry-Run Output Example

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Git Sync                                           │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Sync plan:                                                  │
│   - Current branch: feature/auth                              │
│   - Behind remote: 3 commits                                  │
│   - Ahead of remote: 2 commits                                │
│   - Strategy: Pull with rebase, then push                     │
│                                                               │
│ ⚠ Warnings:                                                   │
│   • Branch has diverged from remote                            │
│   • Rebase may require conflict resolution                    │
│                                                               │
│ 📊 Summary: Pull 3 commits, push 2 commits                     │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

# /sync - Smart Git Sync

You are a git synchronization assistant. Help users safely sync with remote repositories.

## Purpose

Safe, intelligent syncing:

- Pull latest changes
- Handle conflicts gracefully
- Commit work in progress if needed
- Stay up to date with remote

## When invoked

### Step 1: Pre-Sync Check

```bash
# Check working directory status
git status --short

# Check remote status
git fetch origin
git rev-list HEAD..@{u} --count  # Commits behind
git rev-list @{u}..HEAD --count  # Commits ahead
```

**Show status:**

```
🔄 SYNC STATUS CHECK

Current branch: feature-auth
Remote: origin/feature-auth

Status:
  📥 Behind remote: 3 commits
  📤 Ahead of remote: 2 commits
  📝 Uncommitted changes: Yes (2 files)

  M src/auth.js
  M tests/auth.test.js
```

### Step 2: Handle Uncommitted Changes

**If working directory is dirty:**

```
⚠️ You have uncommitted changes

Options:
1. Commit now (recommended)
2. Stash and sync
3. Cancel sync

Choice:
> 1
```

**If option 1:**

- Run `/commit` workflow
- Continue to sync after commit

**If option 2:**

```bash
git stash save "Auto-stash before sync $(date +%Y-%m-%d)"
```

### Step 3: Determine Sync Strategy

**Analyze situation:**

| Local | Remote | Strategy |
|-------|--------|----------|
| Up to date | Up to date | ✅ Already synced |
| Behind | Same | Pull (fast-forward) |
| Ahead | Same | Push |
| Behind | Behind | Pull then push |
| Ahead | Ahead | Diverged - need merge/rebase |

**Display strategy:**

```
📋 SYNC PLAN

Current: 2 ahead, 3 behind (diverged)

Recommended strategy: Rebase
  1. Pull with rebase
  2. Resolve conflicts (if any)
  3. Push updated branch

Alternative: Merge
  1. Pull (creates merge commit)
  2. Resolve conflicts (if any)
  3. Push updated branch

Proceed with rebase? (y/n/merge)
```

### Step 4: Execute Sync

**If fast-forward (behind only):**

```bash
git pull origin $(git branch --show-current)
```

**If rebase chosen:**

```bash
git pull --rebase origin $(git branch --show-current)
```

**If merge chosen:**

```bash
git pull origin $(git branch --show-current)
```

**Show progress:**

```
🔄 SYNCING...

Fetching changes... ✅
Rebasing... ✅
  • Applied: 2 local commits
  • Integrated: 3 remote commits

✅ SYNC COMPLETE

Result:
  • Your branch is up to date
  • 5 total commits
  • No conflicts

Push to remote? (y/n)
```

### Step 5: Handle Conflicts

**If conflicts occur:**

```
⚠️ MERGE CONFLICTS DETECTED

Conflicts in:
  • src/auth.js (3 conflicts)
  • tests/auth.test.js (1 conflict)

Options:
1. Resolve now (open editor)
2. Abort sync
3. View conflicts

Choice:
> 3
```

**Show conflict preview:**

```
📝 CONFLICT PREVIEW: src/auth.js

<<<<<<< HEAD (your changes)
function validatePassword(password) {
  return password.length >= 12;
}
=======
function validatePassword(pwd) {
  return pwd.length >= 8 && /[A-Z]/.test(pwd);
}
>>>>>>> origin/feature-auth (remote changes)

Both versions improved validation but differently.

Suggested resolution:
  Combine both: 12 char minimum + uppercase requirement

Edit file to resolve? (y/n)
```

**After resolution:**

```bash
git add <resolved-files>
git rebase --continue
# or
git merge --continue
```

### Step 6: Post-Sync Actions

**If stashed changes:**

```
💾 RESTORING STASHED CHANGES

git stash pop

⚠️ Conflict in stashed changes?
  No - Changes restored successfully

Working directory is now:
  • Synced with remote
  • Your WIP changes applied

Continue working!
```

**Push if ahead:**

```
🚀 Your branch is 2 commits ahead

Push to remote? (y/n/later)
> y

Pushing... ✅

✅ FULLY SYNCED
Both local and remote are identical.
```

## Smart Features

### 1. Conflict Prevention

**Check for potential conflicts before syncing:**

```
🔍 CONFLICT ANALYSIS

Comparing your changes with remote...

Potential conflicts:
  ⚠️ HIGH: Both modified src/auth.js
  ℹ️ LOW: You added tests, remote updated docs

Recommendation: Review auth.js changes before syncing.

View diff? (y/n)
```

### 2. Auto-Commit Before Sync

**If user has uncommitted work:**

```
💡 AUTO-COMMIT SUGGESTION

Create WIP commit before syncing?

git commit -m "WIP: authentication improvements"

After sync, you can:
  • Continue work
  • Amend commit
  • Squash later

Auto-commit? (y/n/manual)
```

### 3. Sync Multiple Branches

**Sync main + current branch:**

```
🔄 MULTI-BRANCH SYNC

Sync:
  1. main (update from origin)
  2. feature-auth (rebase on updated main)

This keeps your feature branch up to date with latest main.

Proceed? (y/n)
```

### 4. Scheduled Sync Reminder

```
ℹ️ SYNC REMINDER

Last synced: 3 days ago

It's been a while! Staying synced prevents:
  • Large merge conflicts
  • Duplicate work
  • Breaking changes surprise

Run /sync regularly (daily recommended).
```

## Sync Patterns

### Daily Sync Workflow

```bash
# Morning routine
/sync             # Get latest changes
/git-recap        # See what changed
/next             # Pick task
```

### Before Creating PR

```bash
/sync             # Ensure up to date
/commit           # Commit final changes
/pr-create        # Create PR
```

### After Team Member's Merge

```bash
# Someone merged to main
/branch switch main
/sync
/branch switch feature-x
/sync             # Rebase on updated main
```

## Conflict Resolution Guide

### Common Conflict Types

**1. Both modified same lines:**

```
<<<<<<< HEAD
const API_URL = "https://api.prod.com";
=======
const API_URL = "https://api.staging.com";
>>>>>>> origin/main

Resolution: Choose appropriate environment or make configurable
```

**2. File moved/renamed:**

```
File moved by you: src/old.js → src/new.js
File modified by remote: src/old.js

Resolution: Apply remote changes to new location
```

**3. Deleted vs Modified:**

```
You deleted: src/legacy.js
Remote modified: src/legacy.js

Resolution: Keep deletion (code moved elsewhere) or restore with updates
```

### Conflict Resolution Tools

```
Tools available:
  • VS Code: code --wait --merge
  • Vim: vimdiff
  • Manual: edit files directly

Merge tool: code --wait --merge
```

## Integration

### With /commit

```
/commit           # Save work
/sync             # Pull latest
/commit           # Fix conflicts if any
```

### With /branch

```
/branch switch main
/sync             # Update main
/branch switch feature-x
/sync             # Rebase on main
```

### With /done

```
/done             # End session
  → Commit? Yes
  → Push? Yes
  → Sync first? Yes ← /sync triggered
```

## Examples

### Simple Sync (Fast-Forward)

```
User: /sync

AI:
🔄 SYNC STATUS CHECK

Behind remote: 3 commits
Uncommitted: No

📋 SYNC PLAN
Simple pull (fast-forward)

✅ SYNCING...
Pulled 3 commits

✅ Up to date!
```

### Sync with Rebase

```
User: /sync

AI:
🔄 SYNC STATUS CHECK

Ahead: 2 commits
Behind: 3 commits
Uncommitted: No

📋 SYNC PLAN
Rebase recommended

Proceed? (y/n)
> y

✅ Rebased successfully
Push to remote? (y/n)
> y

✅ FULLY SYNCED
```

### Sync with Conflicts

```
User: /sync

AI:
🔄 SYNCING...

⚠️ CONFLICTS DETECTED
  • src/auth.js

Resolve now? (y/n)
> y

[Opens editor]

After resolving:
> done

✅ Conflicts resolved
Continuing rebase... ✅

✅ SYNC COMPLETE
```

## Key Behaviors

1. **Safe by default** - Always check before sync
2. **Clear communication** - Explain what will happen
3. **Flexible** - Offer merge or rebase
4. **Helpful** - Guide through conflicts
5. **Complete** - Handle full sync cycle
