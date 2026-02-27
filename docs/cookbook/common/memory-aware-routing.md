# Memory-Aware Task Routing

> Quick recipe: how `/craft:do` uses past learnings and friction data to route smarter.

---

## How It Works

When you run `/craft:do <task>`, three checks happen before routing:

```text
/craft:do "add authentication"
  |
  1. Worktree detection -- skip branch prompts if in worktree
  2. Memory lookup     -- check MEMORY.md for relevant learnings
  3. Insights check    -- review recent friction from facets
  |
  4. Analyze + route as normal
```

All three are read-only and advisory. They add notes, never force overrides.

---

## Memory Lookup (Step 1.0)

Searches your project's MEMORY.md for headings matching the task:

```
/craft:do "fix pre-commit hook"

Memory note: Pre-commit auto-fix recovery —
  After hook failure, re-stage auto-fixed files and create NEW commit.
```

**How matching works:**

1. Extract 3-5 key terms from your task ("pre-commit", "hook", "fix")
2. Search `## Key Learnings` headings (case-insensitive)
3. If any term matches a heading: show the first sentence

**No match?** Zero output, zero overhead.

---

## Insights Check (Step 1.5)

Reads the last 5 session facets for your current project:

```
/craft:do "refactor database layer"

Recent friction: Previous session had wrong_approach (2x) on this project
  — pushed to wrong branch. Consider verifying branch first.
```

**What it checks:**

1. Load `~/.claude/usage-data/facets/session-*.json` (last 5)
2. Filter for current project name
3. Find `wrong_approach` or `buggy_code` events matching task type
4. Surface as a note with the resolution from last time

**No relevant friction?** Silent. No facets directory? Silent.

---

## Pipeline Suggestion (Step 2.5)

For complex features (complexity score >= 6) without an existing spec:

```
/craft:do "add payment processing"

Substantial feature detected (complexity: 7/10).
Recommended: /brainstorm --> spec --> worktree

Start with brainstorm pipeline?
  - Yes, brainstorm first
  - No, proceed directly
```

If a matching spec already exists:

```
Found SPEC-payment-processing.md. Create worktree with ORCHESTRATE plan?
  - Yes, create worktree + ORCHESTRATE
  - No, proceed with spec context
```

**Always advisory** — declining proceeds with normal routing.

---

## Spec Auto-Load (Step 2.6)

When routing to an agent, matching specs are automatically included:

```
/craft:do "implement auth from spec"

Loading spec context: SPEC-auth-system-2026-02-20.md
  - User Stories: 1 primary, 2 secondary
  - Acceptance Criteria: 3 items
  - Dependencies: OAuth2 SDK

Delegating to backend-architect agent with spec context...
```

No extra step needed — if a spec matches your task keywords, the agent gets it.

---

## Worktree Detection (Step 0.5)

If you're already in a worktree on a `feature/*` branch:

- Branch protection prompts are **skipped** (no "You're on dev" warning)
- If `ORCHESTRATE-*.md` exists: loaded as routing context
- "Create worktree" is **never suggested** (you're already in one)

---

## Quick Reference

| Step | Trigger | Output | Overhead |
|------|---------|--------|----------|
| Worktree detection | In worktree | Skip prompts | ~0s |
| Memory lookup | MEMORY.md has match | Advisory note | ~0s |
| Insights check | Recent friction matches | Advisory note | ~0s |
| Pipeline suggestion | Score >= 6, no spec | Prompt (optional) | User choice |
| Spec auto-load | Spec matches task | Agent gets context | ~0s |

---

## See Also

- [Learning Loop Guide](../../guide/learning-loop-session-completion.md) — How learnings get captured
- [Hub Live Dashboard](../../guide/hub-live-dashboard.md) — How hub displays the same data
- [/craft:do Reference](../../commands/do.md) — Full command reference
