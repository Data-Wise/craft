# Git Commands Learning Guide

**ADHD-Optimized Learning System for Claude Code Git Workflow**

## 🎯 Learning Philosophy

**Key Principle:** Learn by doing, not by memorizing.

Instead of trying to learn all 7 commands at once, you'll build muscle memory through a 4-week progressive learning path. Each week adds one or two commands to your routine.

### 🛡️ Safety-First Learning

**You're learning on REAL work** (for motivation) **with SAFETY RAILS** (for confidence).

**Core safety promise:**
- See what will happen BEFORE it happens
- You approve every git operation
- Easy undo if something goes wrong
- Git is designed to be hard to break

**Three safety documents:**
1. **Safety Rails Guide** - `GIT-SAFETY-RAILS.md` - How commands keep you safe
2. **Undo Guide** - `GIT-UNDO-GUIDE.md` - Fix mistakes quickly
3. **This Learning Guide** - Progressive trust model

**Week 1-2: Maximum safety** - Review everything, don't push
**Week 3: Moderate safety** - Spot check, batch push
**Week 4+: Trust with awareness** - Confident workflow

Read `GIT-SAFETY-RAILS.md` before starting Week 1!

## 📅 4-Week Learning Path

### Week 1: Foundation (Days 1-7)
**Goal:** Make `/done` automatic

**Commands to learn:**
- `/done` - End every session with this

**🛡️ Safety Mode: MAXIMUM**

**Daily practice:**
```bash
[work on anything]
/done                # Every time you stop work
> [accomplishments]
> [next steps]
> review             # ← ALWAYS choose 'review' in Week 1!
[read the full diff carefully]
> y                  # ← Commit after reviewing
> n                  # ← DON'T push yet (Week 1-2)

# Later when confident:
git log -1           # Review your commit
git push             # Push manually
```

**Success metric:** You use `/done` without thinking about it

**Why start here:**
- You already have the habit of stopping work
- `/done` bundles commit/push automatically
- Builds trust in the AI helping with git

**Cheat sheet for week 1:**
```
STOP WORK = /done
```

---

### Week 2: Status Awareness (Days 8-14)
**Goal:** Check git status becomes automatic

**New commands:**
- `/git-recap` - Start each session with this

**Daily practice:**
```bash
# Morning
/git-recap   # What happened yesterday?

[work]

# End of day
/done
```

**Success metric:** You check `/git-recap` before starting work

**Why add this:**
- Gives context for what you did yesterday
- Helps with ADHD memory gaps
- Builds awareness of git activity

**Cheat sheet for week 2:**
```
START DAY = /git-recap
STOP WORK = /done
```

---

### Week 3: Mid-Work Commits (Days 15-21)
**Goal:** Save progress during work

**New commands:**
- `/commit` - Use during focus sessions

**🛡️ Safety Mode: REVIEW FIRST**

**Daily practice:**
```bash
# Morning
/git-recap

# During work (Days 15-17: Review every commit)
/focus "task"
[work 25 minutes]
/commit
> review         # ← Review first 5-10 commits
[read the diff]
> y              # ← Commit
> n              # ← Don't push yet

[work 25 minutes]
/commit
> review         # ← Still reviewing
> y
> n

# During work (Days 18-21: Trust more)
/commit
> y              # ← Can skip review if AI message is accurate
> n              # ← Still batching pushes

# End of day
git log -4       # Review all today's commits
/done
> y / y          # ← NOW push everything
```

**Success metric:** You commit at least 2-3 times during work session

**Why add this:**
- Prevents losing work
- Creates smaller, cleaner commits
- Gives sense of progress

**Cheat sheet for week 3:**
```
START DAY = /git-recap
WORK = /commit every 25 min
STOP WORK = /done
```

---

### Week 4: Syncing & Branches (Days 22-28)
**Goal:** Stay in sync, organize work

**New commands:**
- `/sync` - Start of day (after /git-recap)
- `/branch` - When starting new features

**Daily practice:**
```bash
# Morning
/git-recap
/sync          # NEW: Get latest changes

# Starting new work
/branch new feature-name   # NEW: Create branch
/focus "task"
[work with /commit]

# End of day
/done
```

**Success metric:** No merge conflicts because you sync daily

**Cheat sheet for week 4:**
```
START DAY = /git-recap + /sync
NEW FEATURE = /branch new <name>
WORK = /commit every 25 min
STOP WORK = /done
```

---

### Week 5+: Advanced (As Needed)
**Goal:** Use PR commands when collaborating

**New commands:**
- `/pr-review` - Before creating PRs
- `/pr-create` - When feature is ready

**When to use:**
```bash
# Feature complete
/pr-review     # Check quality
/pr-create     # Share with team
```

**Success metric:** Your PRs have fewer reviewer comments

**Note:** You might not use these every day. That's fine.

## 🧠 Memory Strategies

### 1. **Anchor to Existing Habits**

Map new commands to things you already do:

| You Already Do | New Command | Anchoring Phrase |
|----------------|-------------|------------------|
| Close laptop for day | `/done` | "Closing = /done" |
| Open laptop in morning | `/git-recap` | "Opening = recap" |
| Pomodoro break | `/commit` | "Break = commit" |
| Start new task | `/branch new` | "New task = new branch" |

### 2. **Physical Placement**

**Print & Post Method:**
- Print `GIT-REFCARD.md`
- Put it next to your monitor
- Week 1: Only look at `/done`
- Week 2: Look at `/git-recap` and `/done`
- etc.

**Digital Wallpaper:**
Create a desktop wallpaper with just the current week's commands:
```
Week 1:
┌────────────────┐
│  STOP = /done  │
└────────────────┘
```

### 3. **Verbal Rehearsal**

Say commands out loud as you type them:
- "Slash done" while typing `/done`
- "Slash commit" while typing `/commit`

This engages auditory memory and helps with ADHD focus.

### 4. **Gesture Association**

Create a physical gesture for each command:
- `/done` - Close fist (ending)
- `/commit` - Tap desk twice (checkpoint)
- `/sync` - Pull hands together (syncing)
- `/branch` - Open hands wide (branching out)

### 5. **Color Coding**

Assign mental colors:
- 🔴 `/done` - Red (stop)
- 🟢 `/git-recap` - Green (start)
- 🔵 `/commit` - Blue (ongoing)
- 🟡 `/sync` - Yellow (caution/sync)
- 🟣 `/branch` - Purple (new)

### 6. **Story Method**

Create a narrative:
> "Every morning I **recap** what happened (green start).
> I **sync** to stay current (yellow caution).
> I **branch** out for new work (purple new).
> I **commit** progress along the way (blue ongoing).
> I **done** when I stop (red stop)."

## 🎮 Practice Exercises

### Exercise 1: Morning Routine (5 min)
```bash
# Day 1-7 (Week 1)
# No exercise - just use /done

# Day 8+ (Week 2+)
/git-recap
# Read the output
# Notice: commits from yesterday, any warnings
```

**Goal:** Make this automatic before coffee

---

### Exercise 2: Work Session (25 min)
```bash
# Day 15+ (Week 3+)
/focus "practice git workflow"
[Timer: 25 minutes]
[Make small changes to a practice file]
/commit
[Make more changes]
/commit
[Timer ends]
/done
```

**Goal:** Commit feels natural, not disruptive

---

### Exercise 3: Feature Development (Full day)
```bash
# Day 22+ (Week 4+)
/git-recap
/sync
/branch new practice-feature
/focus "build practice feature"
[work + /commit x3]
/done
```

**Goal:** Branch workflow becomes second nature

---

### Exercise 4: PR Workflow (When needed)
```bash
# Week 5+ (As needed)
# Complete a real feature
/pr-review
# Fix any issues it finds
/pr-review  # Re-check
/pr-create
```

**Goal:** Confident PR creation

## 📊 Progress Tracking

### Week 1 Checklist
- [ ] Used `/done` at least 5 times
- [ ] `/done` felt natural by end of week
- [ ] Didn't have to look up `/done` syntax

### Week 2 Checklist
- [ ] Started 5+ sessions with `/git-recap`
- [ ] Read the git-recap output each time
- [ ] Still using `/done` automatically

### Week 3 Checklist
- [ ] Committed during work at least 10 times
- [ ] Used `/commit` without looking at notes
- [ ] Committed 2+ times per work session

### Week 4 Checklist
- [ ] Synced every morning for 5+ days
- [ ] Created 2+ feature branches
- [ ] No merge conflicts (because of regular syncing)

### Week 5+ Checklist
- [ ] Created 1+ PR with `/pr-create`
- [ ] Used `/pr-review` before PR
- [ ] Reviewer had fewer than 3 comments

## 🎯 Learning Shortcuts

### Quick Start (If you want to skip the 4-week plan)

**Minimum viable workflow:**
```bash
/done    # Use this always
```

Everything else is optional optimization. `/done` alone will get you 80% of the benefits.

**Medium workflow (add when ready):**
```bash
/git-recap   # Morning
/commit      # During work
/done        # End of day
```

**Full workflow (add when comfortable):**
```bash
/git-recap + /sync          # Morning
/branch new                 # New features
/commit                     # During work
/pr-review + /pr-create     # Sharing work
/done                       # End of day
```

## 🔧 Built-In Learning Features

### Command Help System

Every command has examples built-in. To learn a command:

1. **Just try it** - Commands will guide you
2. **Read the prompts** - AI explains each step
3. **Choose 'view' options** - Most commands offer to show you details

Example:
```
User: /commit
AI: [Shows what will be committed]
    [Suggests commit message]
    [Asks: accept/edit/stage/cancel]
```

Each prompt teaches you what the command does.

### Progressive Disclosure

Commands reveal features as you need them:

**First time using `/sync`:**
```
AI: Your branch is up to date!
```

**When you have conflicts:**
```
AI: ⚠️ CONFLICTS DETECTED
    Options:
    1. Resolve now (I'll help)
    2. View conflicts first
    3. Abort sync
```

You learn features when they're relevant.

### Example Gallery

Each command includes examples. Reference them:
```bash
# See examples in command files:
~/.claude/commands/git/commit.md      # Section: "Examples"
~/.claude/commands/git/branch.md      # Section: "Examples"
# etc.
```

## 🚫 Common Learning Pitfalls

### Pitfall 1: Trying to learn all 7 commands at once
**Solution:** Follow the 4-week path. One command per week.

### Pitfall 2: Not using commands because you "don't remember the syntax"
**Solution:** Just type the command. AI will prompt you for details.

### Pitfall 3: Going back to old git commands
**Solution:** Delete `git commit` from muscle memory. Replace with `/commit`.

### Pitfall 4: Feeling overwhelmed by options
**Solution:** Always start with the AI's suggestion. Edit later when comfortable.

### Pitfall 5: Skipping the morning `/git-recap`
**Solution:** Put a post-it on your monitor: "What did I do yesterday?"

## 💪 Reinforcement Strategies

### 1. Habit Stacking
Link new commands to existing habits:

```
Existing: Open laptop
New: /git-recap
Stack: "When I open laptop, I type /git-recap"

Existing: Close laptop
New: /done
Stack: "When I close laptop, I type /done"
```

### 2. Implementation Intentions
Create "if-then" rules:

```
IF I'm about to take a break
THEN I type /commit

IF I'm starting a new feature
THEN I type /branch new <name>

IF I'm about to create a PR
THEN I type /pr-review first
```

### 3. Tiny Wins
Celebrate small successes:
- ✅ Used `/done` 3 days in a row? Success!
- ✅ Committed during work once? Success!
- ✅ Created a branch without looking at notes? Success!

### 4. Error Recovery
When you forget:
- ❌ "Oh no, I forgot to /commit"
- ✅ "That's fine, I'll /commit now and remember next time"

No guilt. Just do it next time.

### 5. Weekly Review
Every Sunday:
```bash
/git-recap --detailed   # (if implemented)
# Review your week's commits
# Celebrate your git activity
```

## 🎨 Customization Ideas

### Add Command Aliases
In your `~/.zshrc`:
```bash
alias gd='/done'         # Shorter /done
alias gc='/commit'       # Shorter /commit
alias gr='/git-recap'    # Shorter /git-recap
```

**Warning:** Only do this after commands are automatic. Aliases can delay real learning.

### Create Morning Script
```bash
#!/bin/bash
# ~/morning.sh
echo "🌅 Good morning! Let's check your git status..."
claude /git-recap
claude /sync
echo "✅ Ready to work!"
```

### iTerm2 Trigger
Set up iTerm2 trigger:
- When you type `work`, automatically suggest: "Run /git-recap first?"

## 📈 Measuring Success

### Week 1 Success
✅ You use `/done` without conscious thought

### Week 4 Success
✅ Morning routine is: `/git-recap`, `/sync`
✅ Work routine is: `/commit` every 25 minutes
✅ End routine is: `/done`

### Week 8 Success
✅ You create PRs with `/pr-review` → `/pr-create`
✅ You never lose work (regular commits)
✅ You rarely have merge conflicts (regular syncing)
✅ You think in git workflow naturally

## 🔗 Integration with Your Workflow

### Current Aliases (Still Work!)
All 133+ aliases continue working:
- `work <project>` - No change
- `pb` - No change
- `pv` - No change
- `finish` - Now also suggests `/done`

### New Git Layer
The git commands layer on top:
```bash
work my-project       # Jump to project (existing)
/git-recap            # Check status (new)
/sync                 # Get latest (new)
/branch new feat-x    # Create branch (new)
/focus "work"         # Start focus (existing)
[work + /commit]      # Commit during work (new)
/done                 # End session (enhanced)
```

## 🎓 Advanced Learning

### Once Commands Are Automatic

**Explore advanced features:**
- Conflict resolution in `/sync`
- Auto-fix mode in `/pr-review`
- Breaking change detection in `/pr-create`
- Stale branch cleanup in `/branch`

**Read full command docs:**
```bash
cat ~/.claude/commands/git/commit.md
cat ~/.claude/commands/git/pr-review.md
# etc.
```

**Customize commands:**
- Add your own templates
- Modify commit message patterns
- Adjust PR description formats

## 📝 Learning Journal Template

Track your progress:

```markdown
# Git Workflow Learning Journal

## Week 1 (Date: ____)
Commands learned: /done
Times used: [____]
Challenges: _____________
Wins: _________________

## Week 2 (Date: ____)
Commands learned: /git-recap
Times used: [____]
Challenges: _____________
Wins: _________________

[Continue for each week]
```

## ❓ FAQ

**Q: Do I have to follow the 4-week path exactly?**
A: No. It's a guide. Skip ahead if comfortable, slow down if needed.

**Q: What if I forget a command for a few days?**
A: That's normal. Just restart when you remember. No guilt.

**Q: Can I use old git commands alongside new ones?**
A: Yes, but it slows learning. Try to use new commands exclusively.

**Q: What if the AI suggests a bad commit message?**
A: Choose 'edit' and fix it. You're always in control.

**Q: How long until commands feel automatic?**
A: Typically 3-4 weeks of daily use. ADHD brains may take 4-6 weeks.

**Q: What if I'm on a team that doesn't use these commands?**
A: That's fine. These are for your local workflow. Team sees normal git.

---

**Remember: Learning is not linear. Some days you'll forget. That's expected and okay.**

**The goal is progress, not perfection.**

*Created: 2025-12-14*
*Version: 1.0*
