# Git Undo Guide - Emergency Reference

**Quick fixes for "Oh no!" moments**

⚠️ **BEFORE PANICKING:** Git is designed to be hard to break. You probably didn't lose anything.

---

## 🆘 Emergency Triage

### Step 1: What happened?

- [ ] I committed the wrong message → [Fix Message](#fix-wrong-commit-message)
- [ ] I committed to the wrong branch → [Fix Wrong Branch](#committed-to-wrong-branch)
- [ ] I want to undo my last commit → [Undo Last Commit](#undo-last-commit)
- [ ] I pushed something wrong → [Undo Push](#undo-a-push)
- [ ] I deleted something important → [Recover Deleted Work](#recover-deleted-work)
- [ ] I have merge conflicts → [Fix Conflicts](#resolve-merge-conflicts)
- [ ] Everything is broken → [Nuclear Option](#nuclear-option-reset-everything)

---

## Fix Wrong Commit Message

**Just committed, message is wrong:**

```bash
# Option 1: Amend the message
git commit --amend -m "correct message here"

# Option 2: Interactive amend (opens editor)
git commit --amend
# Edit message, save, close editor
```

**Already pushed?**

```bash
# If on feature branch and no one else using it:
git commit --amend -m "correct message"
git push --force-with-lease origin feature-branch

# ⚠️ Only if:
# - You're NOT on main/master
# - You're the only one working on this branch
# - You noticed within minutes
```

**Committed several commits ago?**

```bash
# Interactive rebase (advanced)
git rebase -i HEAD~3     # Edit last 3 commits

# In the editor:
# Change 'pick' to 'reword' for the commit you want to fix
# Save and close
# Edit the message when prompted
```

---

## Committed to Wrong Branch

**Oh no, I'm on main but wanted feature-branch!**

```bash
# 1. Note the commit (just in case)
git log -1        # Copy the commit hash (e.g., a3f9d2e)

# 2. Undo the commit (keeps changes)
git reset --soft HEAD~1

# 3. Switch to correct branch
git checkout feature-branch
# Or: /branch switch feature-branch

# 4. Commit again (now on right branch)
/commit
```

**If you already pushed to wrong branch:**

```bash
# On the wrong branch (e.g., main):
git log -1                        # Note commit hash
git reset --hard HEAD~1           # Undo commit
git push --force-with-lease       # ⚠️ Dangerous! Only if you're sure

# Switch to right branch:
git checkout feature-branch
git cherry-pick <commit-hash>     # Apply commit here
git push
```

---

## Undo Last Commit

### Keep Changes (Most Common)

```bash
# Undo commit, keep files as uncommitted changes:
git reset HEAD~1

# Or keep files as staged changes:
git reset --soft HEAD~1
```

**When to use:** "I committed too early, want to add more files"

### Discard Changes (Dangerous!)

```bash
# Undo commit AND delete changes:
git reset --hard HEAD~1

# ⚠️ This DELETES your work! Only use if you're 100% sure.
```

**When to use:** "That commit was a bad experiment, throw it away"

### Undo Multiple Commits

```bash
# Undo last 3 commits (keep changes):
git reset HEAD~3

# Undo last 3 commits (discard changes - dangerous!):
git reset --hard HEAD~3
```

---

## Undo a Push

### Just Pushed to Feature Branch

```bash
# 1. Undo locally
git reset --hard HEAD~1       # Or HEAD~2 for 2 commits, etc.

# 2. Force push (overwrites remote)
git push --force-with-lease origin feature-branch

# ⚠️ Only safe if:
# - You're on YOUR feature branch
# - No one else is using this branch
# - You're okay overwriting remote history
```

### Pushed to Main (OH NO!)

```bash
# DON'T force push to main!
# Instead, create a revert commit:

git revert HEAD               # Creates new commit undoing last one
git push origin main          # Safe push

# This preserves history while undoing changes
```

**Revert multiple commits:**

```bash
# Revert last 3 commits:
git revert HEAD~2..HEAD       # Reverts HEAD, HEAD~1, HEAD~2
git push origin main
```

---

## Recover Deleted Work

### Deleted Commit (Git Reflog to the Rescue!)

Git keeps a 90-day history of EVERYTHING:

```bash
# 1. See all operations
git reflog

# Output shows:
# a3f9d2e HEAD@{0}: reset: moving to HEAD~1
# b4e8c1a HEAD@{1}: commit: my deleted commit  ← This one!
# c5f7a2d HEAD@{2}: commit: previous commit

# 2. Find the deleted commit (note the hash)
# In example above: b4e8c1a

# 3. Restore it
git cherry-pick b4e8c1a       # Bring back one commit
# Or
git reset --hard b4e8c1a      # Jump back to that point
```

### Deleted Branch

```bash
# 1. Find the branch in reflog
git reflog | grep branch-name

# 2. Find the last commit on that branch
# e.g., a3f9d2e HEAD@{5}: checkout: moving from branch-name

# 3. Recreate branch
git branch branch-name a3f9d2e
git checkout branch-name
```

### Deleted Files (Uncommitted)

If you deleted files but haven't committed:

```bash
# Restore one file:
git checkout HEAD -- file.txt

# Restore all deleted files:
git checkout HEAD -- .
```

---

## Resolve Merge Conflicts

### When /sync Says "Conflicts Detected"

**Don't panic! Conflicts are normal.**

#### Step 1: See What's Conflicted

```bash
git status

# Shows:
# Unmerged paths:
#   both modified: src/file.js
```

#### Step 2: Look at the Conflict

```bash
cat src/file.js

# You'll see:
<<<<<<< HEAD (Your changes)
const API_URL = "https://api.staging.com";
=======
const API_URL = "https://api.prod.com";
>>>>>>> origin/main (Their changes)
```

#### Step 3: Fix It

Open `src/file.js` in your editor and decide:

**Option A: Keep yours**

```javascript
const API_URL = "https://api.staging.com";
```

**Option B: Keep theirs**

```javascript
const API_URL = "https://api.prod.com";
```

**Option C: Combine both**

```javascript
const API_URL = process.env.API_URL || "https://api.staging.com";
```

Remove the conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).

#### Step 4: Mark as Resolved

```bash
git add src/file.js       # Mark as resolved
```

#### Step 5: Complete the Merge

```bash
# If rebase:
git rebase --continue

# If merge:
git merge --continue

# Or use /sync which will guide you
```

### Abort If You're Stuck

```bash
# During merge:
git merge --abort

# During rebase:
git rebase --abort

# This returns you to before the operation
```

---

## Fix Messed Up Files

### Restore One File to Last Commit

```bash
# Discard changes to one file:
git checkout HEAD -- src/file.js

# Or restore from specific commit:
git checkout a3f9d2e -- src/file.js
```

### Restore All Files to Last Commit

```bash
# Discard ALL changes (dangerous!):
git reset --hard HEAD

# This returns working directory to last commit
```

### Get File from Different Branch

```bash
# Copy file from main branch:
git checkout main -- src/file.js

# Now src/file.js matches main branch version
```

---

## Nuclear Option: Reset Everything

**If everything is completely broken and you just want to start over:**

### Option 1: Reset to Remote

```bash
# Throw away all local changes, match remote exactly:
git fetch origin
git reset --hard origin/main        # Or origin/feature-branch

# ⚠️ This deletes all uncommitted work!
```

### Option 2: Stash Everything

```bash
# Hide all changes (can bring back later):
git stash save "emergency stash before reset"
git reset --hard HEAD

# Later, if you want them back:
git stash pop
```

### Option 3: Start Fresh Branch

```bash
# Create new branch from clean main:
git checkout main
git pull origin main
git checkout -b new-feature-branch-attempt-2

# Your old branch still exists if you need it
```

---

## Common Scenarios

### "I Committed Secret/Password!"

**PRIORITY 1: Remove from history NOW**

```bash
# If not pushed yet:
git reset --soft HEAD~1              # Undo commit
# Remove secret from file
git commit -m "add feature"          # Commit again without secret

# If already pushed (URGENT):
# 1. Remove secret from file
# 2. Change the secret/password immediately (it's compromised!)
# 3. Contact team lead
# 4. Force push only if approved:
git commit --amend
git push --force-with-lease

# Better: Use git-filter-repo or BFG Repo-Cleaner (search for guides)
```

### "I Committed Huge Files"

```bash
# Before pushing:
git reset --soft HEAD~1
# Move large files out
git commit

# After pushing:
# Use BFG Repo-Cleaner to remove from history
# (Search: "remove large file from git history")
```

### "I Merged Main Into Feature by Accident"

```bash
# Reset feature branch to before merge:
git reflog                           # Find commit before merge
git reset --hard <commit-before-merge>

# Then do proper rebase:
/sync                                # Or git rebase origin/main
```

---

## Safety Commands (Read-Only)

These commands LOOK at things without changing anything:

```bash
git status                # What's changed?
git log                   # Commit history
git log --oneline -10     # Last 10 commits, compact
git diff                  # What changed in working directory?
git diff HEAD             # Diff vs last commit
git diff --stat           # Summary of changes
git reflog                # Everything you've done (90 days)
git show <commit>         # Show specific commit
git branch -a             # All branches
```

**Use these to investigate before fixing.**

---

## When to Ask for Help

Get help if:

- ❌ You pushed secrets/passwords
- ❌ You're about to force push to main
- ❌ You deleted commits that others depend on
- ❌ Reflog doesn't show what you need
- ❌ You're not sure what happened
- ❌ Multiple people are affected

**Better to ask than to make it worse!**

---

## Prevention Better Than Cure

### Before Any Risky Operation

```bash
# Create safety branch:
git branch backup-before-risky-thing

# If things go wrong:
git checkout backup-before-risky-thing
```

### Daily Backups

```bash
# Push to remote daily:
/done         # End of day
> y           # Commit
> y           # Push

# Your work is backed up to GitHub
```

### Use Feature Branches

```bash
# Never work directly on main:
/branch new feature-name

# Experiment freely, can always delete branch
```

---

## Git Reset Cheat Sheet

| Command | Commits | Staging | Working Directory |
|---------|---------|---------|-------------------|
| `--soft` | Reset | Keep | Keep |
| (default) | Reset | Reset | Keep |
| `--hard` | Reset | Reset | Reset ⚠️ |

**Examples:**

```bash
git reset --soft HEAD~1    # Undo commit, keep everything
git reset HEAD~1           # Undo commit, unstage, keep files
git reset --hard HEAD~1    # Undo commit, delete everything ⚠️
```

---

## Reflog is Your Time Machine

**Remember:** Git keeps 90 days of history in reflog.

**You can undo almost anything:**

```bash
git reflog                # See everything
git reset --hard <hash>   # Jump to any point
```

**Even if you:**

- Deleted a branch
- Reset --hard
- Rebased and lost commits
- Merged when you shouldn't have

**Reflog has it all!**

---

## Quick Reference Card

Print this and keep it handy:

```
┌────────────────────────────────────────────────┐
│ GIT UNDO QUICK REFERENCE                       │
├────────────────────────────────────────────────┤
│ Wrong message:                                 │
│   git commit --amend -m "new message"          │
│                                                │
│ Undo commit (keep changes):                    │
│   git reset HEAD~1                             │
│                                                │
│ Undo commit (delete changes):                  │
│   git reset --hard HEAD~1                      │
│                                                │
│ Find deleted commits:                          │
│   git reflog                                   │
│                                                │
│ Restore file:                                  │
│   git checkout HEAD -- file.txt                │
│                                                │
│ Abort merge/rebase:                            │
│   git merge --abort                            │
│   git rebase --abort                           │
│                                                │
│ When stuck: git status                         │
│ When lost: git reflog                          │
│ When unsure: ASK FOR HELP!                     │
└────────────────────────────────────────────────┘
```

---

## Remember

1. **Git rarely loses data** - Reflog keeps 90 days
2. **Read-only commands are safe** - status, log, diff, reflog
3. **Commits can be undone** - reset, revert, amend
4. **Branches are cheap** - Create backups before risky operations
5. **Ask for help** - Better than making it worse

**You've got this! Take a breath, read the guide, fix it step by step.**

---

*Created: 2025-12-14*
*Keep this handy during Weeks 1-4*
