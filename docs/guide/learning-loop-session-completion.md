# Learning Loop & Session Completion

> Close the learning loop: capture what happened, remember what matters, avoid past friction.

---

## Overview

The learning loop connects three commands into a unidirectional data flow:

```text
/workflow:done (producer)
  |-- writes --> MEMORY.md        --> /craft:do reads (routing hints)
  |-- writes --> facets/*.json    --> /craft:do reads (friction avoidance)
  |                               --> /craft:hub reads (recent usage)
  |-- updates --> .STATUS         --> /craft:hub reads (next action)
  |-- syncs --> CLAUDE.md         (counts + active work)
  '-- pushes --> git remote

/craft:do (consumer)
  |-- reads --> MEMORY.md, facets, specs
  '-- routes --> commands / agents / pipeline

/craft:hub (reflector)
  |-- reads --> _discovery.py (live counts)
  |-- reads --> .STATUS (next action)
  |-- reads --> git worktree list (active worktrees)
  '-- reads --> facets (recent usage)
```

**Key principle:** `/done` writes, everything else reads. Data flows one direction.

---

## Session Completion with `/workflow:done`

### What Happens When You Run It

1. **Gather** — Scans git for commits, changed files, .STATUS context
2. **Check docs** — Detects stale counts, orphaned pages, doc drift
3. **Sync CLAUDE.md** — Updates command/skill/agent/test counts mechanically
4. **Capture memory** — Identifies learnings worth persisting
5. **Capture insights** — Writes friction metadata to facet JSON
6. **Worktree status** — Shows branch ahead/behind, ORCHESTRATE progress
7. **Present summary** — Interactive confirmation with all findings
8. **Auto-git** — Commits and pushes (Option A)

### The Fast Path (30 seconds)

```
/workflow:done
  --> [auto-detect everything]
  --> [show summary]
  --> A (accept)
  --> committed + pushed + done
```

Press A (or Enter) to accept the auto-detected summary. Everything else is automatic.

---

## Memory Capture (Step 1.11)

### What Gets Captured

The memory system looks for three signal types:

| Signal | Detection | Example |
|--------|-----------|---------|
| **Errors with workarounds** | Command failed, then succeeded differently | `git push` failed, switched to `git push -u origin` |
| **Repeated friction** | Same mistake 2+ times in one session | Edited wrong file twice |
| **User-stated learnings** | Phrases: "remember", "always", "never" | "Always run lint before committing" |

### Deduplication

Before saving, each candidate is checked against existing MEMORY.md entries:

- Extract 3-5 key terms from the new learning
- Compare against existing `### Heading` entries
- If >60% word overlap: skip (already captured)
- If new: present for confirmation

### User Confirmation

You choose which learnings to save via a multiSelect prompt:

```
Save these learnings to MEMORY.md?

[x] Pre-commit auto-fix recovery
    "After hook failure, re-stage auto-fixed files and create NEW commit"

[x] Worktree branch verification
    "Always verify CWD and branch before git operations"

[ ] Skip all
    "Don't save any learnings this session"
```

### Where Learnings Go

Learnings append to the `## Key Learnings` section of your project's MEMORY.md:

```
~/.claude/projects/<project-slug>/memory/MEMORY.md

## Key Learnings

### Pre-commit auto-fix recovery (2026-02-26)
After a pre-commit hook failure that auto-fixes markdown formatting,
re-stage the fixed files and create a NEW commit. Never amend — the
previous commit wasn't created, so amend would modify older work.
```

Memory is **append-only** — the system never deletes or modifies existing entries.

---

## Insights Capture (Step 1.13)

### What Gets Written

Each session produces a facet JSON file at `~/.claude/usage-data/facets/`:

```json
{
  "session_id": "abc-123",
  "timestamp": "2026-02-26T14:30:00Z",
  "project": "craft",
  "branch": "feature/workflow-enhancements",
  "duration_minutes": 45,
  "goal_category": "feature",
  "outcome": "completed",
  "friction_events": [
    {
      "type": "buggy_code",
      "description": "Pre-commit hook failed on MD031",
      "resolution": "Re-staged auto-fixed files"
    }
  ],
  "learnings_captured": 2,
  "commits": 3,
  "files_changed": 7
}
```

### Friction Types

| Type | What It Means |
|------|--------------|
| `wrong_approach` | Git ops on wrong branch, wrong file targeted |
| `buggy_code` | Lint failures, missing imports, version mismatches |
| `tool_limitation` | Environment constraints, TTY requirements |
| `misunderstood_request` | User correction ("no, I meant...") |

### When You See Friction Summaries

Only if 3+ friction events occurred:

```
FRICTION: 4 events detected this session
   wrong_approach (2): pushed to wrong branch, wrong file
   buggy_code (2): lint failures, missing import
   --> Run /craft:workflow:insights for full analysis
```

Fewer than 3 events: silent. The facet is still written for aggregate analysis.

### Retention

Facets older than 90 days are automatically deleted during cleanup.

---

## Auto-Git (Step 3.5)

### Safety Constraints

| Rule | Why |
|------|-----|
| Never force-push | Protects shared history |
| Skip on `main` | Branch is protected |
| Specific `git add` only | Never `git add -A` or `.` |
| Current branch only | Never pushes to other branches |
| Rebase before push | Attempts `git pull --rebase` if behind |

### What Happens on Failure

- **Rebase conflicts**: Reports error, skips push, continues with .STATUS update
- **Push fails**: Reports error, notes changes are committed locally
- **On main**: Skips entirely with message

### Opt-Out

Set `SKIP_GIT_SYNC=1` to skip auto-commit and push while keeping all other `/done` features.

---

## Env Var Quick Reference

| Variable | Skips | Default |
|----------|-------|---------|
| `SKIP_DOC_CHECK` | Documentation health check | Runs |
| `SKIP_DOC_DRIFT` | Doc drift detection | Runs |
| `SKIP_CLAUDE_MD_SYNC` | CLAUDE.md count sync | Runs |
| `SKIP_MEMORY_UPDATE` | Memory capture | Runs |
| `SKIP_INSIGHTS` | Insights facet write | Runs |
| `SKIP_WORKTREE_STATUS` | Worktree status display | Runs |
| `SKIP_GIT_SYNC` | Auto-commit and push | Runs |

All opt-outs are independent — skip any combination without affecting others.

---

## Best Practices

### Write Memorable Learnings

Good learnings are specific and actionable:

- "After version bump, grep entire repo for old version string"
- "Pre-commit hooks auto-fix MD031 — re-stage and NEW commit"

Avoid vague learnings:

- "Be careful with git" (too broad)
- "Tests are important" (obvious)

### Review Memory Before Sessions

Start each session with `/workflow:recap` or `/craft:hub` — both surface relevant memory and recent friction. This prevents repeating the same mistakes.

### Trust the Defaults

The learning loop is designed to be invisible when nothing interesting happened. No friction? No output. No learnings? No prompt. All counts match? Silent sync.

---

## See Also

- [Hub Live Dashboard](hub-live-dashboard.md) — How `/craft:hub` displays learning loop data
- [Session Wrap-Up Workflow](../cookbook/common/session-wrap-up.md) — Quick recipe
- [Insights Workflow Tutorial](../tutorials/TUTORIAL-insights-workflow.md) — Deeper friction analysis
- [/workflow:done Reference](../commands/workflow/done.md) — Full command reference
