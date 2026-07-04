# NEXT-SESSION Plan — 2026-07-03

> **SUPERSEDED 2026-07-04.** Everything below is now stale or resolved:
> **A1** shipped (`12f50b4b`, 2026-07-03). **A2** was grilled 2026-07-04
> (`GRILL-planning-refactor-a2-2026-07-04.md`) and **deferred** — not "unchanged,
> still needed" as this doc's item #2 says; it's now sequenced after A3, with
> no concrete friction case yet. Per user direction, the **entire
> SPEC-planning-refactor-2026-06-22.md thread is paused**, folded into a future
> larger renaming + hardening + refactoring effort (scope not yet defined) — do
> NOT resume A3/A5-A8 standalone from this doc. See `.STATUS` (`PAUSED
> 2026-07-04` entry) and `docs/internal/PROPOSAL-planning-refactor-report.html`
> for current state. Kept below for historical record only.

Handoff for the next Claude Code session. Entry point + pending work after
the planning-asset-audit sync-check this session.

**Note on `.STATUS`:** the file's tail is stale — a `chore(.STATUS): reset`
commit (inside #237's merge) wiped recent history. Treat `git log` as ground
truth until `.STATUS` is next properly appended; this doc's "State at
handoff" below is verified against `git log`, not `.STATUS`.

## State at handoff

- **Planning-refactor spec active** — `docs/specs/SPEC-planning-refactor-2026-06-22.md`,
  decisions D1–D12 locked, now includes a 2026-07-03 sync-check section
  (§11) reconciling it against 3 commits that landed in the same surface
  since the spec was written: #237 (plugin-audit skill), #239 (orchestrate
  wave-1 simplification), #240 (orchestrate-dispatch mode). Committed
  `edfb23ae`, pushed to `dev`.
- **#237 plugin-audit-skill is MERGED**, not HELD — the 2026-07-02
  NEXT-SESSION doc's backlog item marking it "HELD (jq schema mismatch)" is
  now stale; it shipped 2026-07-03 (`8955163c`).
- **Corrected file-state facts** (spec originally had these wrong):
  `commands/plan/feature.md` is NOT deprecated (141 lines, active, has
  `--refine`); `commands/orchestrate/plan.md` is NOT deprecated (57 lines,
  active, gained orchestrate-dispatch); `commands/orchestrate/resume.md` was
  **deleted** (#239) — 523 lines of unimplemented fiction, never real code.
- **Carried forward, not reverified this session** — docs-site hardening
  (task #1 in the 2026-07-02 doc) shows as merged in `git log`
  (`feat(docs-site): ... #259`), so likely closed; phase-briefing skill
  (task #2) and worktree cleanup (task #4) status unknown — check before
  assuming either is still open.

## Pending work (priority order)

### 1. A1 — Fix `project-planner` ↔ `plan-orchestrator` trigger collision (HIGH)

- `skills/planning/SKILL.md` (`project-planner`) still has unchanged,
  over-broad triggers ("break down a feature", "create a roadmap", "plan a
  sprint") that collide with `plan-orchestrator`'s artifact-generation
  triggers. Confirmed live via direct read this session — zero drift.
- **Action:** strip artifact verbs from `project-planner`'s description;
  keep it to strategy/advice only (estimation, agile coaching, risk).
- Ref: spec §4 (C1), §6 (A1), §11.

### 2. A2 — Add `/plan` dispatcher command

- Single entry point routing the 5-tier spine (brainstorm → spec →
  plan/strategy → plan/artifact → orchestrate/execute). Distinct problem
  from `orchestrate-dispatch` (#240), which handles parallel-agent fan-out,
  not skill-routing — don't conflate the two "dispatch" meanings.
- Ref: spec §5 (ADR target spine), §6 (A2), §11.

### 3. A3 — Finish deprecated-stub shrink (partially done already)

- `commands/plan/sprint.md` (108 lines) and `commands/plan/roadmap.md`
  (116 lines) are correctly flagged `deprecated: true`, but not yet reduced
  to real thin alias stubs pointing at `plan-orchestrator`. `feature.md`
  needs no action (not deprecated). `orchestrate/resume.md` needs no
  action (already deleted in #239).
- Ref: spec §6 (A3, revised), §11.

### 4. A5–A8 — not yet started

- A5: fold `~/.claude/rules/{brainstorm-mode,spec-only-mode,draft-as-dev-research}.md`
  logic into craft skills (also closes C7's scope-gap 2 for `plugin-audit`).
- A6: document (don't edit) superpowers `writing-plans`/`executing-plans` as
  disable-candidates; `dispatching-parallel-agents` now redundant given #240.
- A7: inventory `feature-dev` + `full-stack-orchestration` (no refactor).
- A8: docs for public release (REFCARD, CHANGELOG, counts).

### 5. Backlog carried from 2026-07-02 (reverify status first)

- Phase-briefing skill (`SPEC-phase-briefing-2026-07-01.md`) — grill not yet
  done per that doc; confirm still true.
- Worktree/branch cleanup (`/craft:git:clean`) — orphaned worktrees +
  ~17 merged `feature/*` branches listed in the 2026-07-02 doc; confirm
  still present before re-running.
- Teaching-residue audit (craft↔scholar) — unscheduled, no new info.

## Entry point for next session

```bash
cd ~/projects/dev-tools/craft && claude
```

Then: *"Read `docs/specs/SPEC-planning-refactor-2026-06-22.md` §11 and this
NEXT-SESSION doc, start A1."*
