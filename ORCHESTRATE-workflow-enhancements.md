# ORCHESTRATE: Workflow Command Enhancements (done, do, hub)

**Feature Branch:** `feature/workflow-enhancements`
**Spec:** `docs/specs/SPEC-workflow-enhancements-2026-02-26.md`
**Brainstorm:** `BRAINSTORM-workflow-enhancements-2026-02-26.md`
**Created:** 2026-02-26
**Estimated:** ~6-7 hours across 2-3 sessions

---

## Goal

Overhaul three core workflow commands to close the learning loop: `/workflow:done` (producer — auto-git, CLAUDE.md sync, memory capture), `/craft:do` (consumer — memory-aware routing, pipeline suggestion), `/craft:hub` (reflector — live counts, .STATUS next action, worktree status). Every new step is opt-out, adds less than 3s to the happy path, and degrades gracefully when data sources are missing.

## Architecture

Three commands form a unidirectional data flow:

```text
/workflow:done (producer)
  ├── writes → MEMORY.md        → /craft:do reads (routing hints)
  ├── writes → facets/*.json    → /craft:do reads (friction avoidance)
  │                              → /craft:hub reads (recent usage)
  ├── updates → .STATUS         → /craft:hub reads (next action)
  ├── syncs → CLAUDE.md         (counts + active work)
  └── pushes → git remote

/craft:do (consumer)
  ├── reads → MEMORY.md, facets, specs
  └── routes → commands / agents / pipeline

/craft:hub (reflector)
  ├── reads → _discovery.py (live counts)
  ├── reads → .STATUS (next action)
  ├── reads → git worktree list (active worktrees)
  └── reads → facets (recent usage)
```

## Increments

### Phase 1: Quick Wins (Session 1, ~2-3 hours)

---

### Increment 1: Hub Live Counts (20 min)

**Files:** `commands/hub.md`
**Risk:** Low

Tasks:

- [x] Replace all hardcoded count literals in hub.md banner template
- [x] Change "107 commands | 26 skills | 8 agents" to instruction: "Populate from `stats['total']`, skill count, and agent count loaded in Step 0"
- [x] Replace hardcoded test count with instruction to read from CLAUDE.md or .STATUS
- [x] Verify Step 0 discovery engine load still works correctly

**Verify:**

```bash
# Check no hardcoded counts remain in banner area
grep -n "107\|26 skills\|8 agents" commands/hub.md
# Should return zero results in the banner template section
```

---

### Increment 2: Hub .STATUS Next Action (30 min)

**Files:** `commands/hub.md`
**Risk:** Low

Tasks:

- [x] Add Step 1.5: Read .STATUS file and extract "Next Action" section
- [x] Display "NEXT ACTION" section at top of hub layout (above command grid)
- [x] Parse multi-option format (A/B/C entries with descriptions)
- [x] Graceful skip if .STATUS doesn't exist or has no Next Action

**Verify:**

```bash
# Ensure .STATUS section is referenced in hub.md
grep -n "STATUS\|Next Action" commands/hub.md
```

---

### Increment 3: Worktree-Aware Routing in /do (30 min)

**Files:** `commands/do.md`
**Risk:** Low

Tasks:

- [x] Add Step 0.5: Worktree Detection
  - Run `git worktree list` and check if CWD is inside a worktree
  - If in worktree on feature/* branch: skip branch protection prompts
  - If ORCHESTRATE-*.md exists in CWD: load as routing context
- [x] Update Step 2 (branch check) to skip if worktree already detected
- [x] Update routing decision to not suggest "create worktree" when already in one

**Verify:**

```bash
# Check that worktree detection is documented in do.md
grep -n "worktree\|Step 0.5" commands/do.md
```

---

### Increment 4: Worktree Status in /done Summary (30 min)

**Files:** `commands/workflow/done.md`
**Risk:** Low

Tasks:

- [x] Add Step 1.14: Worktree Status Summary
  - Detect if session is in a worktree via `git rev-parse --show-toplevel` vs `git worktree list`
  - If in worktree: show branch, distance from dev (ahead/behind), other active worktrees
  - If not in worktree but worktrees exist: list them with staleness
- [x] Add "WORKTREE" section to Step 2 interactive summary template
- [x] If in worktree and all ORCHESTRATE increments done: suggest PR creation
- [x] Graceful skip if not a git repo or no worktrees

**Verify:**

```bash
grep -n "1.14\|worktree\|WORKTREE" commands/workflow/done.md
```

---

### Increment 5: Update Published Docs (Phase 1) (20 min)

**Files:** `docs/commands/hub.md`, `docs/commands/do.md`, `docs/commands/done.md`
**Risk:** Low
**Depends on:** Increments 1-4

Tasks:

- [x] Copy hub.md changes to docs/commands/hub.md
- [x] Copy do.md changes to docs/commands/do.md
- [x] Copy done.md changes to docs/commands/done.md (no published done.md exists yet — skipped)
- [x] Run `mkdocs build` to verify no broken links

**Verify:**

```bash
mkdocs build --strict 2>&1 | grep -E "(WARNING|ERROR)" | head -10
```

---

### Phase 2: Integration (Session 2, ~2-3 hours)

---

### Increment 6: /done Auto-Git (45 min)

**Files:** `commands/workflow/done.md`
**Risk:** Medium (pushes to remote)
**Depends on:** Increment 4 (worktree awareness)

Tasks:

- [x] Add Step 3.5: Auto-Git after Option A
  - `git add <changed-files>` (specific files, never -A)
  - `git commit -m "<generated-msg>"` with session summary
  - `git push origin <branch>` (set upstream with -u if needed)
  - If on main: SKIP (protected, never push)
  - If behind remote: attempt `git pull --rebase` first, report if conflicts
  - If push fails: report error, continue with .STATUS update
- [x] Update Option A label: "Full auto: .STATUS + commit + push + sync"
- [x] Add `SKIP_GIT_SYNC` env var opt-out
- [x] Document safety constraints: never force-push, skip main, only current branch

**Verify:**

```bash
grep -n "3.5\|auto-git\|SKIP_GIT_SYNC\|git push" commands/workflow/done.md
```

---

### Increment 7: /done CLAUDE.md Auto-Sync (30 min)

**Files:** `commands/workflow/done.md`
**Risk:** Low

Tasks:

- [x] Add Step 1.10: CLAUDE.md Auto-Sync
  - Run `utils/claude_md_sync.py --fix` silently
  - Update counts (commands, skills, agents, tests) if changed
  - Update version in Active Work section if .STATUS version differs
  - Include CLAUDE.md in session commit (not separate commit)
- [x] Add "SYNCED" section to Step 2 interactive summary
- [x] Add `SKIP_CLAUDE_MD_SYNC` env var opt-out
- [x] Mechanical only: never rewrite prose, only counts and version

**Verify:**

```bash
grep -n "1.10\|claude_md_sync\|SKIP_CLAUDE_MD_SYNC" commands/workflow/done.md
```

---

### Increment 8: Hub Worktree Status Section (30 min)

**Files:** `commands/hub.md`
**Risk:** Low

Tasks:

- [x] Add "WORKTREES" section after "NEXT ACTION" in hub layout
  - Parse `git worktree list --porcelain` for paths and branches
  - Show commits ahead/behind dev for each worktree
  - Show uncommitted file count from `git -C <path> status --short | wc -l`
  - Flag stale worktrees (no commits in 3+ days)
- [x] Section hidden if no worktrees exist (graceful degradation)

**Verify:**

```bash
grep -n "WORKTREE\|worktree list" commands/hub.md
```

---

### Increment 9: /do Pipeline Suggestion (45 min)

**Files:** `commands/do.md`
**Risk:** Low
**Depends on:** Increment 3 (worktree awareness)

Tasks:

- [x] Add pipeline detection in Step 5 (routing decision):
  - If complexity >= 6 AND category = feature AND no existing spec:
    - Suggest: "Substantial feature detected. Recommended: /brainstorm → spec → worktree"
    - User confirms or declines (suggest only, don't auto-route)
  - If complexity >= 6 AND spec exists for topic:
    - Suggest: "Found SPEC-TOPIC.md. Create worktree with ORCHESTRATE plan?"
  - If user declines: proceed with normal agent routing
- [x] Add spec auto-load for agent delegation:
  - When routing to an agent, check `docs/specs/` for matching spec
  - If found, include spec contents in agent prompt

**Verify:**

```bash
grep -n "pipeline\|brainstorm.*spec.*worktree\|auto-load" commands/do.md
```

---

### Increment 10: Update Published Docs (Phase 2) (20 min)

**Files:** `docs/commands/hub.md`, `docs/commands/do.md`, `docs/commands/done.md`, `CLAUDE.md`, `docs/REFCARD.md`
**Risk:** Low
**Depends on:** Increments 6-9

Tasks:

- [x] Copy Phase 2 changes to published docs
- [x] Update CLAUDE.md Active Work section with new capabilities (deferred to Phase 3 final)
- [x] Update REFCARD.md workflow command descriptions
- [x] Run `mkdocs build --strict` to verify

**Verify:**

```bash
mkdocs build --strict 2>&1 | grep -E "(WARNING|ERROR)" | head -10
```

---

### Phase 3: Learning Loop (Session 3, ~2-3 hours)

---

### Increment 11: /done Insights Capture (45 min)

**Files:** `commands/workflow/done.md`
**Risk:** Low

Tasks:

- [ ] Add Step 1.13: Insights Capture
  - Analyze session for friction signals (wrong branch, undone commands, test-then-fix cycles)
  - Write facet JSON to `~/.claude/usage-data/facets/session-<timestamp>.json`
  - Schema: session_id, project, branch, duration, goal_category, outcome, friction_events, learnings_captured, commits, files_changed
  - If 3+ friction events: show one-line summary and suggest `/craft:insights`
  - If no friction: silent (no output)
- [ ] Create `~/.claude/usage-data/facets/` directory if missing
- [ ] Add cleanup: delete facets older than 90 days
- [ ] Add `SKIP_INSIGHTS` env var opt-out

**Verify:**

```bash
grep -n "1.13\|facets\|SKIP_INSIGHTS\|friction" commands/workflow/done.md
```

---

### Increment 12: /done Memory Capture (1 hour)

**Files:** `commands/workflow/done.md`
**Risk:** Medium (writes to persistent memory)

Tasks:

- [ ] Add Step 1.11: Memory Capture
  - Scan session for: errors with workarounds, repeated friction (2+), user-stated learnings ("remember", "always", "never")
  - For each candidate: check MEMORY.md for existing similar heading (>60% word overlap)
  - If duplicate: skip with note "Similar learning already captured"
  - If new: format as `### [Title] ([date])` + 2-3 sentence explanation
  - Show user list of candidates, accept with Enter (multiSelect for exclusion)
  - Append confirmed entries to "## Key Learnings" section
- [ ] Add size check: if Key Learnings exceeds 200 lines, suggest archiving
- [ ] Add `SKIP_MEMORY_UPDATE` env var opt-out
- [ ] Memory is append-only: never delete/modify existing entries programmatically

**Verify:**

```bash
grep -n "1.11\|MEMORY\|SKIP_MEMORY_UPDATE\|append" commands/workflow/done.md
```

---

### Increment 13: /do Memory-Aware and Insights-Informed Routing (45 min)

**Files:** `commands/do.md`
**Risk:** Low (read-only, suggestions only)
**Depends on:** Increments 11, 12

Tasks:

- [ ] Add Step 1.0: Memory Lookup
  - Extract key terms from task description
  - Search MEMORY.md Key Learnings for matching headings (case-insensitive substring)
  - If match: show "Memory note: [title] — [first sentence]" and adjust routing hints
  - If no match: zero overhead, proceed normally
- [ ] Add Step 1.5: Insights Check
  - Read last 5 facet files from `~/.claude/usage-data/facets/`
  - Filter for current project
  - If recent friction matches task type: show note and add guardrail to routing
  - If no relevant friction: proceed normally
- [ ] Both steps are read-only; surface as notes, not forced overrides

**Verify:**

```bash
grep -n "Memory Lookup\|Insights Check\|Step 1.0\|Step 1.5" commands/do.md
```

---

### Increment 14: Hub Recent Usage (30 min)

**Files:** `commands/hub.md`
**Risk:** Low
**Depends on:** Increment 11 (facets data)

Tasks:

- [ ] Add "RECENTLY USED" section in hub footer
  - Read last 10 facet files from `~/.claude/usage-data/facets/`
  - Extract command invocations (if tracked)
  - Show command frequency with recency: `/craft:do (3x) · /craft:check (2x)`
  - Section hidden if no facets data exists
- [ ] Fallback: if no facets, skip section silently (graceful degradation)

**Verify:**

```bash
grep -n "RECENTLY\|facets\|recent usage" commands/hub.md
```

---

### Increment 15: Final Docs + Tests + PR (30 min)

**Files:** Published docs, CLAUDE.md, REFCARD.md
**Risk:** Low
**Depends on:** All above

Tasks:

- [ ] Copy all Phase 3 changes to published docs
- [ ] Update CLAUDE.md with full new capability list
- [ ] Update REFCARD.md workflow section
- [ ] Run full test suite: `python3 -m pytest tests/ -v`
- [ ] Run `mkdocs build --strict`
- [ ] Run `./scripts/validate-counts.sh`
- [ ] Create PR: `gh pr create --base dev`

**Verify:**

```bash
python3 -m pytest tests/ -v
mkdocs build --strict
./scripts/validate-counts.sh
```

---

## Session Plan

### Session 1 (~2-3 hours): Phase 1 Quick Wins

1. Increment 1: Hub live counts
2. Increment 2: Hub .STATUS next action
3. Increment 3: Worktree-aware routing in /do
4. Increment 4: Worktree status in /done
5. Increment 5: Update published docs (Phase 1)

### Session 2 (~2-3 hours): Phase 2 Integration

6. Increment 6: /done auto-git
7. Increment 7: /done CLAUDE.md auto-sync
8. Increment 8: Hub worktree status section
9. Increment 9: /do pipeline suggestion
10. Increment 10: Update published docs (Phase 2)

### Session 3 (~2-3 hours): Phase 3 Learning Loop

11. Increment 11: /done insights capture (facets)
12. Increment 12: /done memory capture
13. Increment 13: /do memory + insights routing
14. Increment 14: Hub recent usage
15. Increment 15: Final docs + tests + PR

---

## Security Checklist

- [ ] Auto-git never force-pushes (regular `git push` only)
- [ ] Auto-git skips main branch entirely
- [ ] Memory append-only (never delete/modify existing entries)
- [ ] Facets contain no secrets (only session metadata)
- [ ] CLAUDE.md sync is mechanical only (counts + version, never prose)
- [ ] All subprocess calls use list-form (no shell injection)

## Backward Compatibility

- [ ] All existing command invocations produce identical output when new data sources missing
- [ ] No new required arguments (all features auto-detected)
- [ ] No schema changes to existing files (.STATUS, CLAUDE.md, plugin.json)
- [ ] New files are additive (facets JSON, MEMORY.md append)
- [ ] All 112 existing tests pass unchanged

## Env Var Opt-Outs

| Variable | Default | Step |
|----------|---------|------|
| `SKIP_CLAUDE_MD_SYNC` | unset (runs) | 1.10 |
| `SKIP_MEMORY_UPDATE` | unset (runs) | 1.11 |
| `SKIP_GIT_SYNC` | unset (runs) | 3.5 |
| `SKIP_INSIGHTS` | unset (runs) | 1.13 |
| `SKIP_WORKTREE_STATUS` | unset (runs) | 1.14 |

## Done Criteria

- [ ] All acceptance criteria from spec met
- [ ] All existing tests pass + docs build clean
- [ ] `/workflow:done` auto-commits, pushes, and syncs
- [ ] `/workflow:done` syncs CLAUDE.md counts silently
- [ ] `/craft:do` skips worktree prompts when already in worktree
- [ ] `/craft:do` suggests pipeline for complexity 6+ features
- [ ] `/craft:hub` shows live counts (no hardcoded numbers)
- [ ] `/craft:hub` shows Next Action and worktree status
- [ ] Emergency exit path completes in less than 30s
- [ ] PR created to dev
