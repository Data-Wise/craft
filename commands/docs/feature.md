# /craft:docs:feature - Feature Documentation Workflow

You are an ADHD-friendly documentation assistant. After a feature is implemented, update ALL relevant docs in one workflow.

## Purpose

**ONE command to document a new feature completely:**
- Detects what was added from recent commits
- Updates CLI help, reference docs, REFCARDs
- Updates README feature list
- Updates CLAUDE.md with completion status
- Updates mkdocs navigation
- Optionally creates tutorial/guide

## Usage

```bash
/craft:docs:feature                    # Auto-detect feature from recent commits
/craft:docs:feature "session tracking" # Specify feature name
/craft:docs:feature --interactive      # Guide through each doc type
```

## When Invoked

### Step 1: Detect Feature Scope

```bash
# Analyze recent commits for feature scope
git log --oneline -20 | head -10
git diff --name-only HEAD~10

# Look for patterns
# - New files in src/
# - New CLI commands
# - New modules/packages
# - Configuration changes
```

**Feature detection heuristics:**
- Multiple related commits → Group as feature
- New directory → Major feature
- New CLI commands → User-facing feature
- New hooks/events → Infrastructure feature

### Step 2: Show Feature Summary

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:feature "session tracking"                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 📦 FEATURE: Session Tracking                                │
│                                                             │
│ Detected components:                                        │
│   • 5 new CLI commands (sessions live/task/conflicts/...)   │
│   • 2 new hooks (session-register, session-cleanup)         │
│   • 1 new module (src/aiterm/sessions/)                     │
│   • 15 commits over 2 days                                  │
│                                                             │
│ Documentation updates needed:                               │
│   1. CLI Help epilogs                                       │
│   2. docs/reference/commands.md                             │
│   3. docs/REFCARD.md                                        │
│   4. docs/reference/REFCARD-SESSIONS.md (NEW)               │
│   5. docs/guide/sessions.md (NEW)                           │
│   6. README.md feature list                                 │
│   7. CLAUDE.md "Just Completed"                             │
│   8. mkdocs.yml navigation                                  │
│                                                             │
│ Proceed with all updates? (y/n/select)                      │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: Execute Documentation Updates

#### 3.1 CLI Help Epilogs

```python
# For each new command, add helpful epilog
# Example: ait sessions live
"""
Examples:
    ait sessions live              # Show all active sessions
    ait sessions live --json       # JSON output for scripts
    ait sessions live --project .  # Filter to current project
"""
```

#### 3.2 Commands Reference

Update `docs/reference/commands.md`:

```markdown
## Session Commands

| Command | Description |
|---------|-------------|
| `ait sessions live` | Show active Claude Code sessions |
| `ait sessions current` | Show current session details |
| `ait sessions task "desc"` | Set task for current session |
| `ait sessions conflicts` | Detect parallel session conflicts |
| `ait sessions history` | Browse session history |
```

#### 3.3 Quick Reference (REFCARD)

Update `docs/REFCARD.md`:

```markdown
## Sessions
| Command | Action |
|---------|--------|
| `ait sessions live` | Active sessions |
| `ait sessions conflicts` | Detect conflicts |
```

#### 3.4 Domain REFCARD (New if Needed)

Create `docs/reference/REFCARD-SESSIONS.md`:

```markdown
# Session Commands Quick Reference

## Essential Commands
...

## Workflow Examples
...

## Troubleshooting
...
```

#### 3.5 Feature Guide (New if Complex)

If feature has learning curve, create `docs/guide/sessions.md`:

```markdown
# Session Coordination Guide

## Overview
...

## Quick Start
...

## How It Works
...

## Common Workflows
...
```

#### 3.6 README Feature List

Add to README.md features section:

```markdown
- **Session Coordination** - Track and manage parallel Claude Code sessions
```

#### 3.7 CLAUDE.md Status

Update "Just Completed" section:

```markdown
### Just Completed
- ✅ Session coordination (hook-based tracking, conflict detection)
```

#### 3.8 mkdocs Navigation

Add new docs to `mkdocs.yml`:

```yaml
nav:
  - Guide:
    - guide/sessions.md  # NEW
  - Reference:
    - reference/REFCARD-SESSIONS.md  # NEW
```

### Step 4: Summary Output

```
┌─────────────────────────────────────────────────────────────┐
│ ✅ FEATURE DOCUMENTATION COMPLETE                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 📦 Feature: Session Tracking                                │
│                                                             │
│ Updated:                                                    │
│   1. ✓ CLI Help - Added epilog examples to 5 commands       │
│   2. ✓ docs/reference/commands.md (+85 lines)               │
│   3. ✓ docs/REFCARD.md (+8 lines, sessions section)         │
│   4. ✓ docs/reference/REFCARD-SESSIONS.md (NEW - 120 lines) │
│   5. ✓ docs/guide/sessions.md (NEW - 250 lines)             │
│   6. ✓ README.md - Added to features list                   │
│   7. ✓ CLAUDE.md - Added to "Just Completed"                │
│   8. ✓ mkdocs.yml - Added 2 new nav entries                 │
│                                                             │
│ What's next?                                                │
│   → Validate: /craft:docs:validate                          │
│   → Preview: /craft:site:preview                            │
│   → Commit: git add -A && git commit -m "docs: add session  │
│             tracking documentation"                         │
└─────────────────────────────────────────────────────────────┘
```

## Interactive Mode

When `--interactive` is specified:

```
📝 FEATURE DOCUMENTATION WIZARD

Step 1/8: CLI Help Epilogs
  Found 5 new commands. Add epilog examples?
  [y] Yes, generate examples
  [n] Skip this step
  [c] Customize each command

Step 2/8: Commands Reference
  Update docs/reference/commands.md?
  [y] Yes, add all commands
  [s] Select which to add
  [n] Skip

... (continue for each doc type)
```

## Smart Suggestions

### Tutorial Detection

If feature is complex (>3 commands, new module), suggest tutorial:

```
💡 This feature has 5 commands and a new module.
   Consider creating a tutorial for better onboarding.

   Create docs/tutorials/session-tracking.md? (y/n)
```

### Breaking Change Detection

If feature changes existing behavior:

```
⚠️  BREAKING CHANGE DETECTED

   The 'ait status' command output format changed.

   Suggested actions:
   1. Update migration guide
   2. Add breaking change to CHANGELOG
   3. Update existing tutorials

   Proceed? (y/n)
```

## ADHD-Friendly Features

1. **One command** - No remembering multiple steps
2. **Auto-detection** - Figures out what was added
3. **Visual progress** - See what's being updated
4. **Interactive option** - Step-by-step when needed
5. **What's next** - Clear follow-up actions

## Integration

This is a **workflow command** that orchestrates:

- `/craft:docs:sync` - For code-to-doc mapping
- `/craft:docs:claude-md` - For CLAUDE.md updates
- `/craft:docs:nav-update` - For mkdocs navigation
- `/craft:docs:generate` - For new guide/tutorial creation

**Related commands:**
- `/craft:docs:update` - Quick sync of all docs
- `/craft:docs:done` - End of session updates
- `/craft:docs:changelog` - For release changelogs
