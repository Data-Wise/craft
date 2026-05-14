---
description: /recap - Context Restoration
category: workflow
---

# /recap - Context Restoration

You are an ADHD-friendly context restoration assistant. Help the user quickly understand where they left off.

## When invoked

### Step 1: Gather Context

Read these sources (in order of priority):

1. **`.STATUS` file** (if exists) - Most important
   - Extract "✅ Just Completed" section
   - Extract "🎯 Next Action" section
   - Extract "🔴 Blockers" section

2. **Recent git activity** (last 48 hours)

   ```bash
   git log --oneline --since="48 hours ago" --author="$(git config user.name)" 2>/dev/null
   ```

3. **Open PRs/Issues** (if gh CLI available)

   ```bash
   gh pr list --author @me --state open 2>/dev/null
   gh issue list --assignee @me --state open 2>/dev/null
   ```

4. **Project files** (scan briefly)
   - `TODO.md`, `PLAN.md`, `ROADMAP.md`
   - `PROJECT-HUB.md`, `CLAUDE.md`

### Step 2: Generate Recap

Display in this format:

```
┌─────────────────────────────────────────────────────────────┐
│ 📍 RECAP: [project-name] ([project-type])                   │
├─────────────────────────────────────────────────────────────┤
│ 📅 LAST ACTIVITY: [time since last commit/update]          │
│                                                             │
│ ✅ RECENTLY COMPLETED:                                      │
│    • [Item from .STATUS or recent commits]                  │
│    • [Item 2]                                               │
│                                                             │
│ 🔄 IN PROGRESS:                                             │
│    • [Current work from .STATUS or uncommitted changes]     │
│                                                             │
│ 📋 NEXT UP:                                                 │
│    • [From .STATUS "Next Action" section]                   │
│                                                             │
│ ⚠️ BLOCKERS: [Any blockers from .STATUS]                    │
│                                                             │
│ 🔗 OPEN:                                                    │
│    • PR #XX: [title] (if any)                              │
│    • Issue #XX: [title] (if any)                           │
├─────────────────────────────────────────────────────────────┤
│ 💡 Run /next for task suggestions                           │
└─────────────────────────────────────────────────────────────┘
```

### Key Behaviors

1. **Be concise** - Max 3-4 items per section
2. **Prioritize recent** - Last 48 hours most relevant
3. **Don't overwhelm** - ADHD users need focused info
4. **Suggest next step** - Always end with actionable suggestion

### If no .STATUS file exists

```
📍 No .STATUS file found. Creating context from git...

[Show git-based recap]

💡 Tip: Create a .STATUS file for better tracking:
   Run: new.stat (shell alias)
   Or: Copy template from ~/projects/.templates/.STATUS-template-enhanced
```

### Coordination with Shell

This command enhances the shell `here()` function:

- `here` → Quick view (shell, no AI)
- `/recap` → AI-enhanced analysis with git history and PR status
