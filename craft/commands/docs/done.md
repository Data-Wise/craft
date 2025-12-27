# /craft:docs:done - End of Session Documentation

You are an ADHD-friendly session wrap-up assistant. Quickly update documentation at the end of a coding session.

## Purpose

**Quick documentation updates when finishing a session:**
- Update CLAUDE.md with session accomplishments
- Update .STATUS file with progress
- Sync any recent code changes to docs
- Prepare for clean session end

## Usage

```bash
/craft:docs:done                           # Quick session wrap-up
/craft:docs:done "implemented session X"   # With session summary
/craft:docs:done --commit                  # Also commit changes
```

## When Invoked

### Step 1: Gather Session Context

```bash
# Get session stats
git log --oneline --since="8 hours ago"
git diff --stat HEAD~5

# Check what changed
git diff --name-only HEAD~5 | head -20

# Get current project status
cat .STATUS 2>/dev/null || echo "No .STATUS file"
```

### Step 2: Analyze Session Accomplishments

**From commits:**
- Count commits this session
- Categorize: features, fixes, docs, refactors
- Calculate lines added/removed

**From file changes:**
- New files created
- Major files modified
- Tests added

### Step 3: Show Session Summary

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:done "implemented session tracking"             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 📝 SESSION SUMMARY                                          │
│                                                             │
│ Session stats:                                              │
│   • 5 commits                                               │
│   • +450/-23 lines                                          │
│   • 3 new files                                             │
│   • Duration: ~2 hours                                      │
│                                                             │
│ Accomplishments detected:                                   │
│   • Added session tracking commands (5 CLI commands)        │
│   • Created session hooks (register, cleanup)               │
│   • Added tests (12 new tests)                              │
│                                                             │
│ Will update:                                                │
│   ✓ CLAUDE.md - Add to "Just Completed"                     │
│   ✓ .STATUS - Update progress, next action                  │
│   ✓ docs/reference/commands.md - Sync recent changes        │
│                                                             │
│ Proceed? (y/n)                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 4: Update Documentation

#### 4.1 CLAUDE.md Updates

Add to "Just Completed" section:

```markdown
### Just Completed
- ✅ Session tracking - Hook-based session coordination with conflict detection
```

Update version if needed:

```markdown
## Project Status: v0.3.1 → v0.3.2 (in progress)
```

#### 4.2 .STATUS File Updates

```yaml
---
status: Active
progress: 75
last_session: 2025-12-27
next: "Add session history browsing"
completed:
  - Session registration hooks
  - Conflict detection
  - Live session display
---

# Session History

## 2025-12-27
- Implemented session tracking (5 commands)
- Added hook-based registration
- Created conflict detection
```

#### 4.3 Quick Doc Sync

Run lightweight sync for any code changes:
- Check if CLI commands changed → update commands.md
- Check if configs changed → update relevant docs
- Skip heavy operations (full regeneration, tutorials)

### Step 5: Summary Output

```
┌─────────────────────────────────────────────────────────────┐
│ ✅ SESSION DOCUMENTATION COMPLETE                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Updated:                                                    │
│   ✓ CLAUDE.md - Added to "Just Completed"                   │
│   ✓ .STATUS - Updated progress (70% → 75%)                  │
│   ✓ docs/reference/commands.md - Synced 3 new commands      │
│                                                             │
│ Session stats:                                              │
│   • 5 commits                                               │
│   • +450/-23 lines                                          │
│   • 3 new files                                             │
│                                                             │
│ Ready to wrap up:                                           │
│   → Commit docs: git add -A && git commit -m "docs: session │
│                  wrap-up"                                   │
│   → Push: git push                                          │
│                                                             │
│ Next session suggestion:                                    │
│   → "Add session history browsing" (from .STATUS)           │
└─────────────────────────────────────────────────────────────┘
```

## With --commit Flag

When `--commit` is specified, also commit the changes:

```bash
/craft:docs:done "session tracking" --commit
```

```
✅ SESSION DOCUMENTATION COMPLETE

Updated & committed:
  ✓ CLAUDE.md
  ✓ .STATUS
  ✓ docs/reference/commands.md

Commit: abc1234 "docs: session wrap-up - session tracking"

Ready to push:
  → git push
```

## What Gets Updated

| Doc Type | Updated | Notes |
|----------|---------|-------|
| CLAUDE.md | Always | "Just Completed" section |
| .STATUS | Always | Progress, next action |
| commands.md | If CLI changed | Lightweight sync |
| REFCARD.md | If CLI changed | Lightweight sync |
| README.md | No | Use docs:feature for features |
| CHANGELOG.md | No | Use docs:changelog for releases |
| mkdocs.yml | No | Use docs:nav-update if new files |

## ADHD-Friendly Features

1. **Quick execution** - < 30 seconds
2. **Session stats** - See what you accomplished
3. **Auto-detection** - Figures out what you did
4. **Next suggestion** - Know what to do next session
5. **Optional commit** - One less step to remember

## Best Practices

### When to Use

- End of coding session
- Before stepping away from project
- Before context switching to another project
- After completing a focused work block

### When NOT to Use

- After adding major feature → Use `/craft:docs:feature` instead
- Before release → Use `/craft:docs:changelog` + `/craft:docs:update full`
- For comprehensive docs → Use `/craft:docs:update full`

## Integration

This is a **lightweight workflow command** that:

- Updates CLAUDE.md (inline, fast)
- Updates .STATUS (inline, fast)
- Calls `/craft:docs:sync` in lightweight mode
- Optionally runs `git commit`

**Related commands:**
- `/craft:docs:feature` - For major feature documentation
- `/craft:docs:update` - For comprehensive updates
- `/craft:docs:changelog` - For release changelogs
