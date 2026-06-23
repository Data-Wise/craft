---
name: adhd-workflow
description: This skill should be used when the user asks to "wrap up the session", "what should I work on next", "I'm stuck", "help me focus", "where did I leave off", "review this spec", "rewrite my prompt", or mentions session boundaries, decision paralysis, blockers, context restoration, single-task focus, spec review, or prompt refinement. Provides ADHD-friendly session and task workflow support for craft users — capturing context at session end, restoring it at session start, prioritizing next action, focusing on one task, getting unstuck, reviewing specs, and refining vague prompts.
---

# ADHD Workflow Skill

Expert in ADHD-friendly session and task workflow for craft users. Reduces cognitive overhead at the points where ADHD costs the most: session boundaries (context loss), task selection (decision paralysis), being stuck (overwhelm), and unclear prompts (rework cost).

## When to Use

Activate this skill when the user's prompt matches any of these concerns:

| User intent | Operation |
|-------------|-----------|
| "I'm done", "wrap up", "end session", "save progress" | Session completion |
| "where did I leave off", "what's the state", "recap me" | Context restoration |
| "what next", "what should I work on", "I can't decide" | Next-task suggestion |
| "let me focus", "single task", "Pomodoro" | Focus mode |
| "I'm stuck", "I don't know what to do", "blocked" | Unblock helper |
| "review my spec", "approve spec", "archive spec" | Spec review |
| "fix my prompt", "rewrite this prompt", "optimize prompt" | Prompt refinement |

If multiple intents apply, pick the operation that matches the strongest verb in the prompt. If still ambiguous, default to **recap** (cheapest) and offer follow-ups.

## Operations

### 1. Session Completion (done)

Capture progress before context evaporates — typically the highest-leverage moment in an ADHD work session.

> **Canonical procedure:** the full session-completion flow lives in
> [`references/done.md`](references/done.md) — the single source of truth shared
> with the `/craft:workflow:done` slash shim. For anything beyond the quick
> summary below (Settings Sync, Memory Optimize, Insights Capture, Worktree
> Status, the interactive summary, auto-git), **load `references/done.md` and
> follow it.** Never reimplement that flow here or in the command shim. See
> [ADR-002](../../../docs/adr/ADR-002-done-command-skill-consolidation.md).

**Inputs:** `git status`, `git log --since="4 hours ago"`, current `.STATUS` file.

**Quick summary (full detail in `references/done.md`):**

1. Gather session activity — uncommitted changes, recent commits, files modified.
2. Summarize what was accomplished in 3–5 bullets, plain language.
3. Update `.STATUS` file: "✅ Just Completed", "🎯 Next Action", "🔴 Blockers".
4. Sync CLAUDE.md, audit settings drift, capture + optimize memory, write the insights facet (see reference for the exact steps).
5. Suggest a conventional-commits message; surface follow-ups (open PRs, failing tests, half-written specs).

**Producer role:** This is the upstream data producer for `/recap`, `/next`, and `/craft:hub` — make `.STATUS` writes accurate and complete.

### 2. Context Restoration (recap)

Quickly answer "where did I leave off?" — the opener for any returning session.

**Sources (priority order):**

1. `.STATUS` file (most authoritative) — "✅ Just Completed", "🎯 Next Action", "🔴 Blockers" sections.
2. Recent git activity (last 48h) — `git log --oneline --since="48 hours ago"`.
3. Open PRs / issues via `gh pr list --author @me --state open` and `gh issue list --assignee @me`.
4. Project planning files — `TODO.md`, `PLAN.md`, `ROADMAP.md`, `CLAUDE.md`.

**Output:** Short, scannable summary — what was completed, what's next, what's blocked. Aim for under 20 lines.

### 3. Next-Task Suggestion (next)

Cut decision paralysis by suggesting **one** clear next task — not a menu of five.

**Priority order:**

1. Unblocked items (was waiting, now ready).
2. In-progress work (maintain momentum).
3. Quick wins (< 15 min, builds confidence).
4. Important but not urgent.
5. Blocked items — acknowledge but don't suggest.

**Output:** One recommendation with a one-sentence rationale. Offer at most one alternative if there's a close second.

### 4. Focus Mode (focus)

Commit to one task and block mental distractions.

**Steps:**

1. Confirm the task — accept `/next`'s suggestion, or take a user-supplied task description.
2. Set focus parameters — suggested duration (25 min Pomodoro / 45 min standard / 90 min deep work).
3. Display a focus banner with the task, time budget, and "what to ignore" reminders.
4. Capture distractions to a list ("come back to these later") rather than acting on them.

### 5. Unblock Helper (stuck)

Targeted help when the user can't move forward.

**Six common stuck types** — ask which applies, then route:

| Type | Diagnostic | Routing |
|------|-----------|---------|
| 😵 Don't know where to start | Goal unclear or task too big | Smallest-first-step breakdown |
| 🤔 Don't understand something | Knowledge gap | Explain, link docs, or dispatch an Explore agent |
| 🔧 Technical problem/error | Bug or env issue | Suggest `/craft:code:debug` or `/bug-detective` |
| 😰 Overwhelmed by scope | Task too big | Break into 15-min subtasks |
| 🧱 Waiting on something external | True blocker | Acknowledge, suggest parallel work |
| 😴 Can't focus today | Energy issue | Suggest break, quick win, or non-coding task |

### 6. Spec Review (spec-review)

Interactive review of formal specs in `docs/specs/SPEC-*.md`.

**Sub-actions:**

| Action | Behavior |
|--------|----------|
| `list` (default if no topic) | Enumerate specs with status |
| `show <topic>` | Display spec content |
| `review <topic>` | Validate frontmatter, walk acceptance criteria, prompt for status updates |
| `approve <topic>` | Mark `Status: approved` |
| `archive <topic>` | Move to `docs/specs/archive/` (completed work) |

**Validation checks on `review`:**

- Frontmatter parses (`Status:`, `Created:`, `Related plan:` fields).
- Acceptance criteria are testable (each maps to a check).
- Open questions don't block the current batch.
- History table is up to date.

### 7. Prompt Refinement (refine)

Rewrite vague prompts into specific, well-structured requests.

**Steps:**

1. Get the prompt — argument or interactive.
2. Diagnose — what's missing? (goal, constraints, success criteria, context, format).
3. Rewrite — produce a clearer version that names the goal, constraints, expected output, and any project context the user implied.
4. Explain — short bullet list of what changed and why, so the user learns the pattern.

**Anti-patterns to fix:** "help me with X" (no goal), "make it better" (no criteria), "fix this" (no context), missing file paths, missing acceptance criteria.

## Cross-Operation Data Flow

This skill participates in a producer-consumer-reflector pattern with the rest of craft:

- **Producer:** `done` writes `.STATUS`, commits, memory entries.
- **Consumer:** `recap`, `next`, `focus`, `stuck` read `.STATUS` and session history before acting.
- **Reflector:** `/craft:hub` aggregates the state into a dashboard.

Always read `.STATUS` first when restoring context. Always update `.STATUS` last when completing a session.

## ADHD-Friendly Output Principles

- **One decision at a time** — never offer 5 options when 1 will do.
- **Visual hierarchy** — headers, tables, emoji markers (🎯 ✅ 🔴 🚧) for scannability.
- **Concrete next step** — every operation ends with a clear, actionable suggestion.
- **Quick wins highlighted** — explicitly label items under 15 minutes.
- **No "while you're here"** — stay scoped to the operation requested; capture-and-defer everything else.

## Integration

This skill replaces the seven `commands/workflow/*.md` commands during the v2.34.0 → v3.0.0 migration:

- `/done` → operation 1 (Session Completion)
- `/recap` → operation 2 (Context Restoration)
- `/next` → operation 3 (Next-Task Suggestion)
- `/focus` → operation 4 (Focus Mode)
- `/stuck` → operation 5 (Unblock Helper)
- `/spec-review` → operation 6 (Spec Review)
- `/refine` → operation 7 (Prompt Refinement)

Both invocation paths work during the deprecation cycle. The skill auto-fires on natural-language match; explicit `/craft:workflow:*` paths continue to function until v3.0.0.

## Related Skills

- `mode-controller` — switches execution mode (default/debug/optimize/release) orthogonally to these operations.
- `project-planner` — for multi-week project breakdowns (this skill handles session-scope; `project-planner` handles project-scope).
- `release` — when the next action is "ship it".
