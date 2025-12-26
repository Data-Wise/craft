# Git Safety Rails Guide

**Learning Git Commands with Confidence on Real Work**

## Philosophy

You're learning on **real work** (for ADHD motivation) but with **safety rails** (for peace of mind).

**Key principle:** See what will happen BEFORE it happens. You're always in control.

---

## Safety Rails by Week

### Week 1: /done (Maximum Safety)

**What /done does:**
1. ✅ Asks what you accomplished (just text, totally safe)
2. ✅ Asks what's next (just text, totally safe)
3. ⚠️ **PERMISSION REQUIRED**: "Commit these changes?"
4. ⚠️ **PERMISSION REQUIRED**: "Push to remote?"

**You control everything. Here's how:**

#### Before Any Git Operation

When `/done` asks "Commit these changes?", it will FIRST show you:

```
📊 CHANGES THAT WILL BE COMMITTED:

Modified:
  M src/auth.js (+20, -5)
  M tests/auth.test.js (+15, -0)

New:
  ?? docs/authentication.md (+42)

Total: 2 modified, 1 new | +77, -5 lines

📝 SUGGESTED COMMIT MESSAGE:
feat(auth): add password validation

- Add minimum length check (8 chars)
- Add special character requirement
- Update error messages
- Add comprehensive tests

💾 Commit these changes? (y/n/review/skip)
```

**Your options:**
- `y` - Commit (you saw what will be committed, you approve)
- `n` - Don't commit (changes stay uncommitted, totally fine)
- `review` - See full diff before deciding
- `skip` - Skip git, just update .STATUS

**Nothing happens until you say yes.**

#### Review Mode

If you choose `review`, you'll see:

```
📄 FULL DIFF:

src/auth.js:
  + function validatePassword(password) {
  +   if (password.length < 8) return false;
  +   if (!/[A-Z]/.test(password)) return false;
  +   return true;
  + }

tests/auth.test.js:
  + test('validates password length', () => {
  +   expect(validatePassword('short')).toBe(false);
  + });

[Full diff shown]

Commit these changes? (y/n/skip)
```

**Now you've seen EVERYTHING that will be committed.**

#### Push Safety

After committing, `/done` asks:

```
✅ COMMITTED: a3f9d2e

📊 Repository Status:
  Branch: feature-auth
  Ahead of origin: 1 commit
  Behind origin: 0 commits

🚀 Push to remote? (y/n/later)
```

**Your options:**
- `y` - Push now (your code goes to GitHub)
- `n` - Don't push (commit stays local, you can push manually later)
- `later` - Remind me next time

**Default in Week 1-2: Choose 'n' (don't push)**
- Commit stays local
- You can review it later
- You can amend it if needed
- You can push when confident

---

### Week 2: /git-recap (100% Read-Only)

**Safety level:** ✅✅✅ COMPLETELY SAFE

`/git-recap` only READS information. It cannot:
- ❌ Commit anything
- ❌ Push anything
- ❌ Delete anything
- ❌ Modify anything

**It only shows:**
- ✅ Commits you already made
- ✅ Current branch status
- ✅ Unpushed commits (if any)
- ✅ Open PRs (if any)

**Use freely, zero risk.**

---

### Week 3: /commit (Graduated Safety)

**Early Week 3 (Days 15-17): Maximum Safety Mode**

Every time you use `/commit`:

```
📊 CHANGES TO COMMIT:
  [shows changed files]

📝 SUGGESTED COMMIT:
  [AI-generated message]

🛡️ SAFETY MODE ACTIVE

Before committing, you can:
  1. review - See full diff
  2. edit   - Change commit message
  3. stage  - Stage files but don't commit yet
  4. cancel - Don't commit

What do you want to do? (1/2/3/4 or 'y' to accept)
```

**Always choose '1' (review) first few times:**
- See exactly what will be committed
- Verify it matches what you expect
- Build confidence

**After reviewing:**
- Files look right? Choose 'y' to commit
- Message needs tweaking? Choose '2' (edit)
- Not ready? Choose '4' (cancel)

**Late Week 3 (Days 18-21): Trust Mode**

Once you've reviewed 5-10 commits and they're always correct:

```
📝 SUGGESTED COMMIT:
feat(auth): add password validation

Trust AI suggestion? (y/edit/review/cancel)
```

**Now you can:**
- Choose 'y' directly (faster workflow)
- Still choose 'review' if uncertain
- Edit if message seems off

**Push Safety:**

```
✅ COMMITTED: a3f9d2e

Push to remote? (y/n/later)
```

**Week 3 recommendation: Choose 'n' (no push)**
- Build up 3-4 local commits
- Review them together: `git log -3`
- Then push all at once: `git push`

---

### Week 4: /sync and /branch (Guided Safety)

**`/sync` safety features:**

```
🔄 SYNC STATUS CHECK

Current branch: feature-auth
Remote: origin/feature-auth

Status:
  📥 Behind remote: 3 commits
  📤 Ahead of remote: 2 commits
  📝 Uncommitted changes: Yes (2 files)

⚠️ SAFETY CHECK: You have uncommitted changes

Before syncing, I need to handle these:
  1. Commit now (/commit workflow)
  2. Stash changes (hide temporarily)
  3. Show me the changes first
  4. Cancel sync

What should I do? (1/2/3/4)
```

**Always choose '3' first time:**
- See what changes exist
- Decide if you want to commit or stash
- No surprises

**If sync will create merge:**

```
📋 SYNC PLAN

Your branch has diverged from origin:
  • You have 2 commits
  • Remote has 3 commits

I recommend: Rebase
  What this does:
  - Takes your 2 commits
  - Applies remote's 3 commits first
  - Replays your 2 commits on top
  - Results in clean linear history

Alternative: Merge
  What this does:
  - Creates merge commit
  - Combines both histories
  - Easier but messier history

Show me what will happen? (y/n)
> y

[Shows detailed explanation of rebase steps]

Proceed with rebase? (y/n/cancel)
```

**You see the plan before execution.**

**`/branch` safety features:**

```
🌿 CREATE NEW BRANCH

Current branch: main
Current status: 3 uncommitted changes

⚠️ SAFETY CHECK: Uncommitted changes

These changes will come with you to the new branch.
Is that what you want?

Options:
  1. Yes, bring changes to new branch
  2. No, commit them to main first
  3. Show me the changes
  4. Cancel

What should I do? (1/2/3/4)
```

**No surprises about what happens to your changes.**

---

## Safety Features Built Into All Commands

### 1. Preview Before Action

Every command that modifies git shows you:
- What files will be affected
- What the operation will do
- Expected outcome

### 2. Confirm Before Destructive Operations

Commands ask permission before:
- Committing
- Pushing
- Deleting branches
- Force operations
- Rebasing

### 3. Uncommitted Changes Protection

If you have uncommitted changes, commands will:
- Warn you
- Show you the changes
- Ask what to do with them
- Never lose your work

### 4. Explanation Mode

Add `explain` to any operation:

```
📝 EXPLANATION MODE

What /commit does:
  1. Runs: git status --short
     → Shows which files changed

  2. Runs: git diff --stat
     → Shows how many lines changed

  3. Analyzes changes
     → Determines commit type (feat/fix/docs)

  4. Generates message
     → Follows Conventional Commits format

  5. Shows you everything
     → You review and approve

  6. If you say yes: git add -A && git commit -m "message"
     → Stages all changes and commits

  7. Asks about push
     → You control if code goes to remote

At any step, you can cancel. Nothing is permanent until you approve.

Continue with /commit? (y/n)
```

---

## Week-by-Week Safety Recommendations

### Week 1: Paranoid Mode ✅ (Recommended)

```bash
/done
> [answer accomplishments]
> [answer next steps]
> review          # ← ALWAYS review first time
> y               # ← Commit after reviewing
> n               # ← DON'T push yet

# Later, when ready:
git log           # Review commit
git push          # Push manually when confident
```

### Week 2: Still Cautious ✅

```bash
/git-recap        # Safe, read-only
/done
> review          # ← Still review, but faster now
> y               # ← Commit
> n               # ← Still not pushing yet
```

### Week 3 Early: Supervised Mode ✅

```bash
/commit
> review          # ← Review every commit first 5 times
> y               # ← Commit after reviewing
> n               # ← Don't push individual commits

# After 3-4 commits:
git log -4        # Review all commits together
git push          # Push batch when confident
```

### Week 3 Late: Trust But Verify ✅

```bash
/commit
> y               # ← Can skip review now (if AI is accurate)
> n               # ← Still batching pushes

# End of session:
/done
> y               # ← Trust the commit
> y               # ← NOW push (you've reviewed during the day)
```

### Week 4+: Graduated Autonomy ✅

```bash
/git-recap        # Quick check
/sync             # Trust the process
/commit           # Accept AI suggestions
> y / y           # Commit and push
/done             # Full auto
```

---

## Emergency Brake: How to Undo

### Just Committed, Want to Change Message

```bash
# Immediately after commit:
git commit --amend -m "better message"

# Or in /done workflow:
/done
> y              # Commit
> n              # Don't push
# Then fix it:
git commit --amend -m "corrected message"
```

### Committed to Wrong Branch

```bash
# Oh no, committed to main instead of feature branch!

# Don't panic, here's the fix:
git log -1                    # Note the commit hash (e.g., a3f9d2e)
git reset --soft HEAD~1       # Undo commit (keeps changes)
/branch switch feature-x      # Switch to correct branch
/commit                       # Commit again on right branch
```

### Pushed Something Wrong

```bash
# If you pushed and caught it immediately:

# 1. Fix locally
git commit --amend -m "fixed message"

# 2. Force push (ask first!)
git push --force-with-lease origin feature-branch

# Only do this if:
# - You're on a feature branch (NOT main)
# - No one else is using this branch
# - You caught it within minutes
```

### Want to Undo Last Commit Completely

```bash
# Undo commit, keep changes:
git reset --soft HEAD~1

# Undo commit, discard changes (dangerous!):
git reset --hard HEAD~1

# Undo commit, keep changes as uncommitted:
git reset HEAD~1
```

### Accidentally Deleted Commits (Panic Mode)

```bash
# Git has a 90-day undo history:
git reflog                    # See all operations

# Find the commit you want back:
# Look for: a3f9d2e HEAD@{2}: commit: your message

# Restore it:
git reset --hard a3f9d2e      # Time travel to that point

# Or cherry-pick specific commit:
git cherry-pick a3f9d2e       # Bring back one commit
```

---

## Safety Checklist

Print this and keep it visible during Weeks 1-3:

### Before Every /commit or /done:

- [ ] I know what files I changed
- [ ] I've tested my changes (if code)
- [ ] I'm ready to save this work

### During the prompts:

- [ ] Week 1-2: Choose 'review' every time
- [ ] Week 3: Choose 'review' if uncertain
- [ ] Week 4+: Trust but spot-check

### After committing:

- [ ] Week 1-3: Choose 'n' (don't push yet)
- [ ] Review with `git log -1`
- [ ] If message is wrong: `git commit --amend`
- [ ] Push when confident

### Before any /sync:

- [ ] Save work first (/commit)
- [ ] Know what branch I'm on
- [ ] Understand what sync will do

---

## Progressive Trust Model

### Days 1-5 (Week 1)
**Trust level:** ⭐☆☆☆☆ (Verify everything)
```
/done → review → read carefully → commit → don't push → review commit → push manually
```

### Days 8-14 (Week 2)
**Trust level:** ⭐⭐☆☆☆ (Verify most things)
```
/done → review → skim quickly → commit → don't push → batch push later
```

### Days 15-21 (Week 3)
**Trust level:** ⭐⭐⭐☆☆ (Spot check)
```
/commit → review first 2 of day → trust rest → batch push end of day
```

### Days 22+ (Week 4+)
**Trust level:** ⭐⭐⭐⭐☆ (Trust with awareness)
```
/commit → accept AI → push when done → /git-recap to verify
```

### Days 30+ (Mastery)
**Trust level:** ⭐⭐⭐⭐⭐ (Full trust, occasional verification)
```
/commit → y/y → continue working
```

---

## Red Flags (Stop and Review)

Always review manually if:
- ⚠️ Committing more than 10 files at once
- ⚠️ More than 200 lines changed
- ⚠️ You don't remember making some changes
- ⚠️ AI message doesn't match what you did
- ⚠️ On main branch (should be on feature branch)
- ⚠️ About to push after merging
- ⚠️ Sync says "conflicts detected"

**When in doubt, choose 'review' or 'cancel'.**

---

## Your Safety Net

Remember, you have multiple safety layers:

1. **Local commits first** - Nothing goes to remote unless you push
2. **Review before commit** - You see everything first
3. **Amend immediately** - Fix mistakes right away
4. **90-day reflog** - Undo anything within 90 days
5. **Feature branches** - Main branch protected
6. **PR process** - Code review before merge
7. **GitHub backup** - Remote copy of everything
8. **Git is designed to be safe** - Hard to truly lose work

---

## Confidence Building

### After Week 1 (5-7 uses of /done):
```bash
git log --oneline -10    # Review your commits

# Ask yourself:
# - Do the messages make sense? ✓
# - Did I lose any work? ✓ (No!)
# - Was it faster than manual git? ✓
```

**If all checks pass: You can trust the system.**

### After Week 3 (15-20 uses of /commit):
```bash
git log --oneline --since="1 week ago"

# Ask yourself:
# - Clean commit history? ✓
# - Good commit messages? ✓
# - Right commit granularity? ✓
# - Caught problems early? ✓
```

**If all checks pass: Graduate to "trust but verify" mode.**

---

## When to Ask for Help

Post in your learning channel if:
- AI suggests a message that doesn't match your changes
- You're consistently editing every commit message
- Sync creates conflicts you don't understand
- You feel anxious about using commands

**It's okay to ask! Better to ask than to avoid using the tools.**

---

## Summary: Safety Rails Philosophy

**Week 1-2:** "Show me everything, I'll decide"
- Maximum visibility
- Minimum auto-action
- Build confidence through transparency

**Week 3:** "I trust you, but I'm watching"
- Faster workflow
- Spot checks instead of full review
- Build confidence through repetition

**Week 4+:** "I trust you, tell me if something's wrong"
- Autonomous workflow
- Review only on red flags
- Confidence through experience

---

**The goal: Learn fast without fear, trust earned not assumed.**

*Created: 2025-12-14*
*Version: 1.0 - Safety Rails Edition*
