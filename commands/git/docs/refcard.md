# Git Commands Quick Reference

**ADHD-Friendly Git Workflow for Claude Code**

## 🎯 The Core Loop

```
/recap → /next → /focus → work → /done
                                    ↓
                            [auto commits & pushes]
```

## ⚡ Essential Commands

| Command | What It Does | When To Use |
|---------|--------------|-------------|
| `/commit` | Smart commit with AI message | During work (save progress) |
| `/done` | End session + auto-commit | When stopping work |
| `/git-recap` | Show today's git activity | Morning check-in, status check |
| `/sync` | Pull/push with conflict help | Start of day, before PR |
| `/branch` | Manage branches safely | Starting new work, switching tasks |
| `/pr-create` | Create comprehensive PR | Feature complete, ready for review |
| `/pr-review` | Self-review before PR | Before creating PR |

## 🔄 Daily Workflow Patterns

### Morning Routine

```bash
/recap          # Where was I?
/git-recap      # What did I commit yesterday?
/sync           # Get latest changes
/next           # Pick today's task
```

### During Work

```bash
/focus "task"   # Start focused work
[work 25 min]
/commit         # Save progress (can do multiple times)
[work more]
/commit         # Save again
```

### End of Session

```bash
/done           # Accomplishments + auto-commit + push
```

### Feature Development

```bash
/branch new feature-name    # Start new branch
/focus "build feature"      # Focus session
[work + /commit as needed]
/pr-review                  # Check quality
/pr-create                  # Create PR
```

## 📋 Command Details

### /commit

**Purpose:** Quick, quality commits without breaking flow

```
Quick commit → AI suggests message → Accept/edit → Push?
```

**Example:**

```
User: /commit
AI: Analyzed changes...
    📝 SUGGESTED COMMIT:
    feat(auth): add login validation

    Accept? (y/edit/stage)
```

**When:** Any time you want to save progress
**Time:** ~30 seconds

---

### /done

**Purpose:** Graceful session end with git integration

```
Accomplishments → Commit? → Push? → Affirmation
```

**Example:**

```
User: /done
AI: 🎯 What did you accomplish?
You: Added login component and tests
AI: 💾 Commit these changes? (y/n)
You: y
AI: [Creates commit, offers to push]
```

**When:** Every time you stop work
**Time:** 1-2 minutes

---

### /git-recap

**Purpose:** Quick git activity overview

```
Shows: Today's commits, unpushed changes, open PRs
```

**Example:**

```
📊 GIT ACTIVITY SUMMARY
🌿 CURRENT: feature-auth (2 ahead)
📅 TODAY: 3 commits
🚀 UNPUSHED: 2 commits
💡 Create PR: /pr-create
```

**When:** Morning check-in, mid-session status
**Time:** 5 seconds

---

### /sync

**Purpose:** Safe syncing with conflict help

```
Check status → Handle uncommitted → Pull/Rebase → Resolve conflicts → Push
```

**Example:**

```
User: /sync
AI: 🔄 SYNC STATUS CHECK
    Behind remote: 3 commits
    📋 SYNC PLAN: Pull (fast-forward)
    ✅ SYNCING... Done!
```

**When:** Start of day, before creating PR
**Time:** 10-30 seconds (or 2-5 minutes if conflicts)

---

### /branch

**Purpose:** Safe branch management

```
List branches → Create/Switch/Delete → Auto-update .STATUS
```

**Example:**

```
User: /branch new feature-dashboard
AI: ✅ Created: feature-dashboard
    📝 Branch goal?
You: Building user dashboard
AI: ✅ Ready! Run /next
```

**When:** Starting new work, switching contexts
**Time:** 20 seconds

---

### /pr-create

**Purpose:** Comprehensive PR with auto-generated content

```
Analyze commits → Generate title/description → Link issues → Create
```

**Example:**

```
User: /pr-create
AI: 📝 SUGGESTED TITLE:
    feat(auth): implement authentication system

    📄 DESCRIPTION: [auto-generated]
    ✅ CREATED PR #45
    URL: github.com/user/repo/pull/45
```

**When:** Feature complete, tests pass
**Time:** 1-2 minutes

---

### /pr-review

**Purpose:** Self-review before submitting PR

```
Check code quality → Test coverage → Docs → Security → Fix issues
```

**Example:**

```
User: /pr-review
AI: 📊 PR SELF-REVIEW SUMMARY
    ✅ PASSED (8)
    ❌ MUST FIX (2)
      • Debug console.log() statements
      • Hardcoded API key

    Fix issues now? (y/n)
```

**When:** Before creating PR
**Time:** 2-5 minutes

## 🧠 Memory Aids

### Mnemonic: "CDSB PR²"

- **C**ommit - Save work anytime
- **D**one - End sessions
- **S**sync - Stay current
- **B**ranch - Organize work
- **PR**-review - Check quality
- **PR**-create - Share work

### Visual Memory Map

```
       START DAY              DURING WORK           END SESSION
           ↓                       ↓                     ↓
    /recap /sync          /commit /commit           /done
    /git-recap               ↓                        ↓
         ↓               /pr-review              [auto-push]
    /branch new          /pr-create
    /focus
```

### Command Families

```
📊 Status Commands:    /recap, /git-recap
🔧 Work Commands:      /commit, /done
🔄 Sync Commands:      /sync, /branch
📤 Share Commands:     /pr-review, /pr-create
```

## 🎨 Integration with Existing Workflow

### Your Existing Commands

These continue to work exactly as before:

- All 133+ zsh aliases
- `work <project>` - Jump to project
- `pb` - Build
- `pv` - Preview
- `finish` - End session (now enhanced as `/done`)

### New Git Additions

The 7 new commands layer on top seamlessly:

- `/commit` - Use during work sessions
- `/done` - Enhanced finish with git
- All others - On-demand tools

## 💡 Pro Tips

1. **Commit often** - Use `/commit` every 15-30 minutes of work
2. **Sync daily** - Run `/sync` every morning
3. **Review before PR** - Always `/pr-review` before `/pr-create`
4. **Branch per feature** - Use `/branch new` for each new task
5. **Let AI help** - Accept AI-generated commit messages when good

## ⚠️ Common Mistakes to Avoid

❌ Don't: Skip `/pr-review` before creating PR
✅ Do: Always self-review first

❌ Don't: Work on main branch
✅ Do: Create feature branches with `/branch new`

❌ Don't: Go days without `/sync`
✅ Do: Sync every morning

❌ Don't: Batch all commits at end of day
✅ Do: Commit throughout work session

## 🔗 Command Chaining

Common sequences:

```bash
# Start new feature
/branch new feature-x && /focus "build feature x"

# Morning routine
/recap && /git-recap && /sync

# Finish and ship
/pr-review && /pr-create && /done

# Quick save and continue
/commit && /focus "continue work"
```

## 📍 Quick Command Finder

**"I want to..."**

- **save my work** → `/commit`
- **stop for the day** → `/done`
- **see what I did** → `/git-recap`
- **get latest code** → `/sync`
- **start new feature** → `/branch new <name>`
- **create pull request** → `/pr-create`
- **check PR quality** → `/pr-review`

## 📂 Files Location

All commands stored in:

```
~/.claude/commands/
├── workflow/
│   └── done.md          # Enhanced with git
└── git/
    ├── commit.md        # Smart commits
    ├── git-recap.md     # Activity summary
    ├── branch.md        # Branch management
    ├── sync.md          # Remote syncing
    ├── pr-create.md     # PR creation
    └── pr-review.md     # PR self-review
```

---

**Print this and keep it visible until commands become automatic!**

*Created: 2025-12-14*
*Version: 1.0*
