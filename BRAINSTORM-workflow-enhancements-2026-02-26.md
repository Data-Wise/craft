# BRAINSTORM: Workflow Command Enhancements (done, do, hub)

**Date:** 2026-02-26
**Depth:** max | **Focus:** feature
**Duration:** ~12 min (2 agents + 4 deep questions)
**Scope:** Full overhaul + new features for `/workflow:done`, `/craft:do`, `/craft:hub`

---

## Problem Statement

Three core workflow commands have accumulated gaps based on real-world usage patterns:

1. **`/workflow:done`** — Captures session progress but misses CLAUDE.md sync, memory updates, and auto-git. Users must manually commit, push, and sync after `/done`, losing the "30-second exit" promise.
2. **`/craft:do`** — Routes tasks well but doesn't suggest the brainstorm→spec→worktree pipeline when relevant, and has no memory of past routing decisions or session patterns.
3. **`/craft:hub`** — Shows static command inventory. Doesn't surface recent usage, worktree status, or personalized suggestions from `.STATUS`.

---

## Research Findings

### Agent 1: Codebase Explorer — Gap Analysis

12-section analysis identified these critical gaps:

| Gap | Severity | Current State | Impact |
|-----|----------|---------------|--------|
| Worktree↔session state not linked | Critical | Dev session loses context when user `cd`s to worktree | User starts blind in worktree |
| `/done` no auto-git | High | Suggests commit msg but doesn't execute | Extra manual steps break flow |
| CLAUDE.md never auto-synced | High | `utils/claude_md_sync.py` exists but not called by `/done` | Counts drift between releases |
| MEMORY.md never auto-updated | High | Only manual updates via Write tool | Learnings lost between sessions |
| No increment tracking | Medium | ORCHESTRATE checkboxes are text-only | Can't programmatically report progress |
| `/do` no pipeline awareness | Medium | Routes to single commands, not multi-step workflows | Complex features get under-routed |
| `/hub` static display | Low | Always shows same inventory | No personalization |

### Agent 2: Tech Lead — Feature Design

Key architectural decisions recommended:

1. **Session state file** (`~/.claude/session-state.json`): Tracks current session's accomplishments, modified files, and timing — consumed by `/done` for accurate summaries.
2. **Handoff file** (`.claude/session-handoff.json` in worktree): Created by dev session, consumed by worktree session's `/recap`. Contains spec reference, ORCHESTRATE location, increment status.
3. **Memory append strategy**: Pattern buffer collects candidates during session; `/done` reviews and appends confirmed patterns (2+ occurrences or explicit confirmation).

---

## User Design Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| CLAUDE.md handling | Auto-sync counts + active work silently | No interruption, keeps CLAUDE.md fresh |
| Memory capture | Confirmed patterns only (2+ or explicit) | Prevents memory bloat from one-off observations |
| Pipeline integration | Suggest when relevant, don't auto-route | User stays in control of workflow escalation |
| Git on `/done` | Full auto: commit + push + sync | Eliminates the 3 manual steps after every session |

---

## Feature Designs

### A. `/workflow:done` v2.0 — Full Session Closure

**Current steps (1 through 1.9):** Git status, specs, doc health, CLAUDE.md staleness, .STATUS refresh, doc drift, interactive summary, commit suggestion.

**New steps to add:**

| Step | Name | What It Does |
|------|------|-------------|
| 1.10 | CLAUDE.md Auto-Sync | Run `utils/claude_md_sync.py --fix` silently. Update counts (commands, skills, agents, tests) and Active Work section. |
| 1.11 | Memory Capture | Review session for confirmed patterns. Append to `MEMORY.md` if pattern appeared 2+ times or user explicitly said "remember this". |
| 1.12 | Insights Trigger | If `~/.claude/usage-data/facets/` has new friction signals, mention: "N new insights detected — run `/craft:insights` to review." |
| 3.5 | Auto-Git | After user confirms summary (Option A), execute: `git add <files>`, `git commit -m "<msg>"`, `git push`, then `/craft:git:sync` behavior. |
| 3.6 | Worktree Handoff | If on feature branch, check if all ORCHESTRATE increments done. If yes, suggest PR creation. If not, update `.claude/session-handoff.json` with progress for next session. |

**Modified steps:**

| Step | Change |
|------|--------|
| Step 2 (Interactive Summary) | Add new sections: "Memory Captured", "CLAUDE.md Synced", "Insights Available" |
| Step 3 (Option A) | Becomes "Full auto: update .STATUS + commit + push + sync" (no manual git steps) |
| Step 3 (Option C) | Changes to "Skip .STATUS + git" (still captures memory) |

**Auto-Git flow:**

```
User selects Option A
  → git add <changed-files> (specific files, never -A)
  → git commit -m "<generated-msg>"
  → git push origin <branch>
  → If behind remote: pull --rebase first
  → If push fails: report error, don't retry
  → Show: "Committed abc1234, pushed to origin/<branch>"
```

**Memory capture flow:**

```
During session, collect pattern candidates:
  - Errors fixed 2+ times with same approach
  - User said "remember", "always", "never" about a pattern
  - Debugging insight that resolved a non-obvious issue

At /done Step 1.11:
  - Show: "Detected N potential memory items"
  - List each with 1-line summary
  - User confirms which to save (multiSelect)
  - Append confirmed items to MEMORY.md under appropriate section
```

### B. `/craft:do` v2.0 — Pipeline-Aware Router

**Current:** Complexity score 0-10 → route to command/agent/orchestrator.

**New features:**

#### B1. Pipeline Suggestion

When the task description matches a multi-step pattern, suggest the full pipeline instead of just routing to the first step:

| Pattern Detected | Suggestion |
|-----------------|------------|
| "new feature" + no spec exists | "This looks like a new feature. Want to start with `/brainstorm` → spec → worktree?" |
| "implement TOPIC" + spec exists | "Found SPEC-TOPIC.md. Want to create a worktree with ORCHESTRATE plan?" |
| "fix TOPIC" + on dev branch | "Bug fixes need a feature branch. Create worktree `fix/TOPIC`?" |

Implementation: Add Step 1.5 after task analysis, before routing:

```
Step 1.5: Pipeline Check
  - If complexity >= 4 AND no active worktree for this topic:
    - Check docs/specs/ for matching spec
    - If spec found: suggest "Spec exists → create worktree?"
    - If no spec: suggest "Start with /brainstorm?"
  - If user declines: proceed with normal routing
  - If user accepts: chain the appropriate commands
```

#### B2. Spec Auto-Load for Agents

When routing to an agent, automatically include the relevant spec in the agent prompt:

```
Current: Task(prompt="implement auth endpoints")
New:     Task(prompt="implement auth endpoints\n\nSpec: <contents of SPEC-auth.md>")
```

This ensures agents have full context without the user having to reference the spec.

#### B3. Memory-Aware Routing

Check MEMORY.md for relevant learnings before routing:

```
User: /craft:do "update homebrew formula"

Step 1.5b: Memory Check
  Found relevant memory entries:
  - "Manifest-Driven Code Generation vs Hand-Editing"
  - "Local-First SHA256 Principle"

  → Include in routing context so agent knows about these patterns
```

### C. `/craft:hub` v2.0 — Context-Aware Discovery

**Current:** Static 3-layer navigation (main → category → detail).

**New features:**

#### C1. Live Count Refresh

Replace hardcoded counts with auto-detected values at display time:

```
Current: "107 commands · 26 skills · 8 agents"
New:     Run get_command_stats() → display actual counts
```

Already partially implemented (Step 0 loads discovery engine), but the banner template still has hardcoded numbers. Fix: template uses `{stats['total']}` interpolation.

#### C2. Recent Usage Section

Add a "Recent" section showing commands used in the last 3 sessions:

```
┌─────────────────────────────────────────────────────────────┐
│ 📍 RECENT (last 3 sessions)                                 │
│                                                             │
│ /craft:check (5x) · /craft:do (3x) · /workflow:done (3x)  │
│ /craft:git:worktree (2x) · /craft:release (1x)            │
└─────────────────────────────────────────────────────────────┘
```

Source: Parse `.STATUS` file for session logs and extract command mentions.

#### C3. Contextual Suggestions from .STATUS

Read `.STATUS` "🎯 Next Action" and suggest relevant commands:

```
From .STATUS: "Finish pin-markdownlint: commit, test, PR"
Suggestion: "/craft:check → /craft:test → gh pr create"

From .STATUS: "Session 2: increments 5-8 of unified-release-watch"
Suggestion: "cd to worktree → /craft:orchestrate continue"
```

#### C4. Worktree Status Integration

Show active worktrees with their progress:

```
┌─────────────────────────────────────────────────────────────┐
│ 🌳 ACTIVE WORKTREES                                         │
│                                                             │
│ feature/pin-markdownlint    ~90% done  (10 files changed)  │
│ feature/unified-release-watch  ~50%  (Session 1 complete)  │
└─────────────────────────────────────────────────────────────┘
```

Source: `git worktree list` + read ORCHESTRATE files for progress.

---

## Documentation Updates

All three command files need updates:

| File | Updates Needed |
|------|---------------|
| `commands/workflow/done.md` | Add steps 1.10-1.12, 3.5-3.6. Update summary template. Add auto-git flow. |
| `commands/do.md` | Add Step 1.5 (pipeline check), B2 (spec auto-load), B3 (memory check). |
| `commands/hub.md` | Add C1-C4 sections. Update banner template. Add Recent and Worktree sections. |
| `docs/commands/done.md` | Published docs copy — mirror changes from commands/ |
| `docs/commands/do.md` | Published docs copy |
| `docs/commands/hub.md` | Published docs copy |
| `CLAUDE.md` | Update Active Work section with new capabilities |
| `docs/REFCARD.md` | Update workflow command descriptions |

---

## Quick Wins (< 30 min each)

1. **Hub live counts** — Replace hardcoded banner numbers with `get_command_stats()` interpolation
2. **`/done` CLAUDE.md sync** — Add Step 1.10: call `utils/claude_md_sync.py --fix` silently
3. **`/done` auto-commit** — Add Step 3.5: execute git add + commit + push after Option A
4. **`/do` spec auto-load** — When spec exists for topic, include in agent prompt

## Medium Effort (1-2 hours each)

5. **`/done` memory capture** — Pattern buffer + confirmation flow + MEMORY.md append
6. **`/do` pipeline suggestion** — Step 1.5 with spec detection + pipeline chaining
7. **Hub contextual suggestions** — Parse .STATUS + ORCHESTRATE for smart suggestions
8. **Hub worktree status** — `git worktree list` + ORCHESTRATE progress parsing

## Long-term (Future sessions)

9. **Session handoff files** — `.claude/session-handoff.json` for worktree context transfer
10. **Insights integration** — Friction detection → automatic insight triggers in `/done`
11. **Memory-aware routing in `/do`** — MEMORY.md lookup for relevant learnings
12. **Hub usage analytics** — Track command frequency across sessions

---

## Implementation Order

| # | Deliverable | Effort | Dependencies |
|---|-------------|--------|--------------|
| 1 | `/done` auto-git (Step 3.5) | 30 min | None |
| 2 | `/done` CLAUDE.md sync (Step 1.10) | 20 min | None |
| 3 | Hub live counts (C1) | 20 min | None |
| 4 | `/do` spec auto-load (B2) | 30 min | None |
| 5 | `/done` memory capture (Step 1.11) | 1 hour | None |
| 6 | `/do` pipeline suggestion (B1) | 1 hour | None |
| 7 | Hub contextual suggestions (C3) | 45 min | None |
| 8 | Hub worktree status (C4) | 30 min | None |
| 9 | `/done` worktree handoff (Step 3.6) | 45 min | #1 |
| 10 | Documentation updates | 1 hour | All above |

**Total:** ~6-7 hours across 2-3 sessions

---

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Auto-git scope | Commit + push + sync | User's explicit preference; eliminates 3 manual steps |
| Memory threshold | 2+ occurrences or explicit | Prevents bloat; quality over quantity |
| Pipeline routing | Suggest, don't auto-route | User stays in control; pipeline is opt-in |
| CLAUDE.md sync | Silent auto-fix | No interruption; counts stay fresh |
| Hub counts | Live from discovery engine | Already partially implemented; eliminates drift |
| Handoff mechanism | JSON file in worktree | Simple, inspectable, consumed by `/recap` |

---

## Open Questions

1. **Memory dedup** — How to detect if a pattern is already in MEMORY.md before appending? Fuzzy match on key phrases?
2. **Auto-git failure** — If push fails (behind remote, conflicts), should `/done` abort or continue with .STATUS update?
3. **Pipeline chain UX** — When user accepts pipeline suggestion in `/do`, should it launch brainstorm immediately or show the full pipeline plan first?
4. **Hub usage tracking** — Where to store command frequency data? `.claude/usage-stats.json`? Or parse .STATUS logs?

---

## Related Artifacts

- Current `/done`: `commands/workflow/done.md` (709 lines)
- Current `/do`: `commands/do.md` (811 lines)
- Current `/hub`: `commands/hub.md` (685 lines)
- CLAUDE.md sync util: `utils/claude_md_sync.py`
- Discovery engine: `commands/_discovery.py`
- Memory file: `~/.claude/projects/-Users-dt-projects-dev-tools-craft/memory/MEMORY.md`
- Insights: `~/.claude/usage-data/facets/`

Sources:

- Explore agent: 12-section codebase gap analysis
- User design decisions: 4 deep questions answered
- Real-world usage patterns: 20+ sessions tracked in .STATUS
