---
description: Git activity summary - recent commits, branch status, and productivity insights
category: git
arguments:
  - name: mode
    description: Display mode (default|detailed|summary)
    required: false
    default: default
  - name: dry-run
    description: Preview git commands that will be executed without running them
    required: false
    default: false
    alias: -n
deprecated: true
replaced-by: "skills/dev/git/"
---

# /git-recap - Git Activity Summary

You are a git activity assistant. Provide quick overview of recent git activity.

## Purpose

Quick git status check complementing `/recap`:

- Recent commits (today/week)
- Branch status
- Unpushed commits
- Open PRs

## Dry-Run Mode

Preview git commands that will be executed to gather activity data:

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Git Activity Summary                              │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Git Commands to Execute:                                    │
│                                                               │
│   1. Current Branch                                           │
│      Command: git branch --show-current                       │
│      Purpose: Identify active branch                          │
│                                                               │
│   2. Today's Commits                                          │
│      Command: git log --oneline --since="midnight"            │
│                --author="$(git config user.name)"             │
│      Purpose: Show today's activity                           │
│                                                               │
│   3. Weekly Statistics                                        │
│      Command: git log --oneline --since="1 week ago"          │
│                --author="$(git config user.name)" | wc -l     │
│      Purpose: Calculate weekly commit count                   │
│                                                               │
│   4. Unpushed Commits                                         │
│      Command: git log @{u}.. --oneline                        │
│      Purpose: Identify commits not yet pushed                 │
│                                                               │
│   5. Repository Status                                        │
│      Command: git status --short --branch                     │
│      Purpose: Check for uncommitted changes                   │
│                                                               │
│   6. Open Pull Requests (optional)                            │
│      Command: gh pr list --author @me --state open            │
│      Purpose: List your open PRs                              │
│      Requires: gh CLI installed                               │
│                                                               │
│   7. Stashed Changes                                          │
│      Command: git stash list                                  │
│      Purpose: Show stashed work                               │
│                                                               │
│ ✓ Analysis Steps:                                             │
│   - Parse commit messages for type (feat, fix, docs, etc.)    │
│   - Calculate productivity metrics                            │
│   - Identify warning conditions (dirty repo, diverged branch) │
│   - Generate actionable suggestions                           │
│                                                               │
│ ⚠ Notes:                                                      │
│   • All commands are read-only (no modifications)             │
│   • Some commands may fail gracefully if not in git repo      │
│   • gh CLI commands skipped if not installed                  │
│                                                               │
│ 📊 Summary: 7 git commands for activity analysis              │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

**Note**: This is a read-only command, so dry-run shows what will be analyzed without modifying any git state.

## When invoked

### Step 1: Gather Git Information

```bash
# Current branch
git branch --show-current

# Commits today
git log --oneline --since="midnight" --author="$(git config user.name)"

# Commits this week
git log --oneline --since="1 week ago" --author="$(git config user.name)" | wc -l

# Unpushed commits
git log @{u}.. --oneline 2>/dev/null || echo "No remote tracking"

# Branch status
git status --short --branch

# Open PRs (if gh available)
gh pr list --author @me --state open 2>/dev/null

# Stashes
git stash list
```

### Step 2: Display Summary

```
┌─────────────────────────────────────────────────────────────┐
│ 📊 GIT ACTIVITY SUMMARY                                     │
├─────────────────────────────────────────────────────────────┤
│ 🌿 CURRENT BRANCH: feature-auth                             │
│    Status: 2 commits ahead of origin                        │
│    Clean: Yes (no uncommitted changes)                      │
├─────────────────────────────────────────────────────────────┤
│ 📅 TODAY'S COMMITS (3)                                      │
│    a3f9d2e feat: add login component                        │
│    b4e8c1a test: add auth tests                             │
│    c5f7a2d docs: update API docs                            │
├─────────────────────────────────────────────────────────────┤
│ 📈 THIS WEEK: 15 commits                                    │
│                                                             │
│    By type:                                                 │
│    • feat: 7 commits                                        │
│    • test: 4 commits                                        │
│    • docs: 3 commits                                        │
│    • fix: 1 commit                                          │
├─────────────────────────────────────────────────────────────┤
│ 🚀 UNPUSHED COMMITS (2)                                     │
│    a3f9d2e feat: add login component                        │
│    b4e8c1a test: add auth tests                             │
│                                                             │
│    💡 Run: git push origin feature-auth                     │
├─────────────────────────────────────────────────────────────┤
│ 🔗 OPEN PRs (1)                                             │
│    #42: Add authentication system                           │
│         https://github.com/user/repo/pull/42                │
├─────────────────────────────────────────────────────────────┤
│ 💾 STASHES (1)                                              │
│    stash@{0}: WIP on main: quick experiment                 │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: Suggest Actions

Based on status, suggest next steps:

**If unpushed commits:**

```
💡 SUGGESTED ACTIONS:
• Push commits: git push origin feature-auth
• Create PR: /pr-create
```

**If working directory dirty:**

```
💡 SUGGESTED ACTIONS:
• Commit changes: /commit
• Stash changes: git stash save "description"
```

**If branch is behind remote:**

```
💡 SUGGESTED ACTIONS:
• Pull updates: git pull
• Sync with main: /sync
```

**If on main with unpushed:**

```
⚠️ WARNING: You have unpushed commits on main
💡 Consider creating a feature branch
```

## Display Modes

### Quick Mode (Default)

Shows:

- Current branch
- Today's commits (if any)
- Unpushed commits
- Open PRs

### Detailed Mode (`/git-recap --detailed`)

Additional info:

- This week's commits
- Commit breakdown by type
- Stashes
- Branch status vs remote

### Summary Mode (`/git-recap --summary`)

One-line summary:

```
📊 feature-auth | 3 commits today | 2 unpushed | 1 PR open
```

## Smart Analysis

### Productivity Insights

**Active day:**

```
🔥 PRODUCTIVE DAY!
15 commits today - that's above your average (8/day)

Top activity:
• Testing (6 commits)
• Features (5 commits)
• Docs (4 commits)
```

**Quiet period:**

```
💤 No commits in 3 days

Last activity: 2025-12-11
Last commit: feat: add user profile

💡 Time to catch up? Run /recap to see where you left off.
```

### Warning Flags

**Uncommitted changes:**

```
⚠️ You have uncommitted changes

  M src/auth.js
  ?? new-file.txt

💡 Commit before switching tasks: /commit
```

**Diverged branches:**

```
⚠️ Your branch has diverged from origin

Local: 2 commits ahead
Remote: 1 commit ahead

💡 You may need to rebase: git pull --rebase
```

**Large PR:**

```
ℹ️ PR #42 has 450+ lines changed

Consider splitting into smaller PRs for easier review.
```

## Integration Points

### With /recap

```
/recap        → Overall context (project + git)
/git-recap    → Git-specific detail
```

Use together for complete picture:

```
/recap        # Where was I in the project?
/git-recap    # What did I commit?
```

### With /commit

```
/git-recap    → See recent commits
/commit       → Add new commit
/git-recap    → Verify it's there
```

### With /sync

```
/git-recap    → Check if behind remote
/sync         → Pull and merge
/git-recap    → Verify synced
```

## Statistics Tracking

**Commit patterns:**

```
📊 YOUR GIT STATS (Last 30 days)

Commits: 127
Average/day: 4.2
Most active: Mondays (avg 7 commits)
Least active: Weekends (avg 1 commit)

Commit types:
feat:     45 (35%)
test:     32 (25%)
docs:     28 (22%)
fix:      15 (12%)
refactor:  7 (6%)

Peak hours: 9-11am, 2-4pm
```

## Quick Commands

### After /git-recap

Based on output, offer shortcuts:

**If unpushed:**

```
Quick actions:
p - Push commits
r - Create PR
c - Commit more changes
```

**If clean:**

```
✅ All committed and pushed!

Next:
n - Start new work (/next)
b - Create new branch (/branch new)
```

## Examples

### Morning Check-in

```
User: /git-recap

AI:
📊 GIT ACTIVITY SUMMARY
🌿 CURRENT: main (synced)
📅 YESTERDAY: 8 commits
🚀 UNPUSHED: None
🔗 OPEN PRS: 1 (#42)

💡 Start new work: /next
```

### Mid-Session

```
User: /git-recap

AI:
📊 GIT ACTIVITY SUMMARY
🌿 CURRENT: feature-auth (2 ahead)
📅 TODAY: 3 commits
⚠️ UNCOMMITTED: 2 files
🚀 UNPUSHED: 2 commits

💡 Commit changes: /commit
```

### End of Day

```
User: /git-recap

AI:
📊 GIT ACTIVITY SUMMARY
🌿 CURRENT: feature-auth
📅 TODAY: 12 commits 🔥
🚀 UNPUSHED: 5 commits
🔗 READY FOR PR: Yes

💡 Create PR: /pr-create
   Or push: git push origin feature-auth
```

## Key Behaviors

1. **Quick overview** - No overwhelming detail
2. **Actionable** - Always suggest next steps
3. **Context-aware** - Different suggestions based on state
4. **Encouraging** - Celebrate productive days
5. **Warning** - Flag potential issues early

---

## 🎓 Learning & Practice

### For Beginners

**Week 2 of Learning Path:** Add this to your morning routine

**Daily goal:** Start EVERY work session with `/git-recap`

**Why it matters:**

- Shows what you did yesterday (ADHD memory aid!)
- Catches issues early (uncommitted changes, etc.)
- Builds git awareness
- Takes only 5 seconds

**How to practice:**

```bash
# Every morning before starting work:
/git-recap    # What happened yesterday?
[read the output]
/done         # Continue using from Week 1
```

**Common questions:**

*Q: What if I didn't commit anything yesterday?*
A: You'll see that! It's a gentle reminder to commit more often with `/commit`.

*Q: Should I do this even on weekends?*
A: Only if you worked! Skip it on days off.

*Q: What if there are warnings?*
A: Read them and follow the suggestions. They're helpful, not scolding.

### Building the Habit

**Triggers to remember /git-recap:**

- Opening laptop in morning → `/git-recap`
- Before starting work → `/git-recap`
- After /sync → `/git-recap` (to see what changed)

**Physical reminder:**
Update your post-it note:

```
MORNING = /git-recap
STOP = /done
```

### Integration with Week 1

**New morning routine:**

```bash
/git-recap    # NEW: What happened yesterday?
/sync         # (You'll learn this in Week 4)
/next         # Pick today's task
```

**Still using /done:**

```bash
[work]
/done         # Keep doing this from Week 1!
```

### Progress Tracking

See your learning progress:

```bash
/git learn    # View 4-week path
```

Quick reference:

```bash
cat ~/.claude/commands/GIT-REFCARD.md
```

### Next Steps

Once you check `/git-recap` every morning (end of Week 2):

- **Week 3:** Add `/commit` during work sessions
- Keep using `/done` from Week 1
- Read full guide: `~/.claude/commands/GIT-LEARNING-GUIDE.md`

**See examples:** `/git examples`
**Get help:** `/git help git-recap`
