# orchestrate-dispatch mode — Orchestration Plan

> **Branch:** `feature/orchestrate-dispatch-mode`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-orchestrate-dispatch-mode`
> **Spec:** `docs/specs/SPEC-orchestrate-dispatch-mode-2026-07-01.md` — **not committed to this
> worktree** (only the GRILL below and this ORCHESTRATE file were). See the Phase 1 note below.
> **Grill (decisions locked):** [`docs/specs/GRILL-plan-orchestrator-dispatch-mode-2026-07-01.md`](../specs/GRILL-plan-orchestrator-dispatch-mode-2026-07-01.md) — 15 branches, 0 open questions
> **Version Target:** next minor (no count-cascade expected — flag enum value, not a new command/skill/agent)

> **This file is self-contained.** An implementer (a fresh session or a background agent) should
> be able to execute it by reading only this file + the GRILL doc linked above (the SPEC was not
> committed — see the Phase 1 note). It does not depend on the conversation that produced it.

---

## How to start

```bash
cd ~/.git-worktrees/craft/feature-orchestrate-dispatch-mode
# then: "Read docs/plans/ORCHESTRATE-orchestrate-dispatch-mode-2026-07-01.md and start Phase 1"
```

---

## Objective

Add a third `output` mode, `orchestrate-dispatch`, to `plan-orchestrator`'s Mode 1
(Spec → ORCHESTRATE): same self-containment guarantee as the existing STOP-new-session mode, but
execution happens via a dispatched background `Agent` call from the live planning session
instead of a fresh human session — with explicit handling for the failure modes a background
agent introduces that a human session doesn't (ambiguity, hangs, silent failures, resumability,
concurrency).

## Phase Overview

| Phase | Increment | Priority | Effort | Status |
|-------|-----------|----------|--------|--------|
| 1 | Add `orchestrate-dispatch` output value + confirm-gate + self-containment prompt shape | High | Low-Med | ✅ done |
| 2 | Concurrency cap (scoped) + failure/hang detection + confirmed-failure disposition | High | Med | ✅ done |
| 3 | Resumability + `.STATUS` auto-write scoping | Medium | Low | ✅ done |
| 4 | Documentation & Discoverability | Medium | Low | ✅ done |

---

**Note (not a blocker):** `docs/specs/SPEC-orchestrate-dispatch-mode-2026-07-01.md` (linked at the
top of this file) is not present in the worktree — only the GRILL file and this ORCHESTRATE file
were committed. The GRILL is the upstream source the SPEC was synthesized from and is fully
self-contained (all 15 decision branches inline their own rationale), so implementation proceeded
using GRILL branch numbers as the index instead of the SPEC's `§3.N` references. `§3.N` maps
1:1 to GRILL branches 1-12; for branches 13-15 (added post-grill) use the branch number directly,
not `§3.N`. The dispatching session should either commit the missing SPEC file or update this
file's front-matter link.

## Phase 1 — Add the `orchestrate-dispatch` output value

**Scope:** wire the third enum value into the command's argument surface and the skill's Mode 1
section; implement the confirm-before-dispatch gate and the self-containment prompt shape.

- [x] 1.1 Update `commands/orchestrate/plan.md` frontmatter: `output` arg description becomes
      `orchestrate-worktree (default) | orchestrate-only | orchestrate-dispatch` (SPEC §3.2).
- [x] 1.2 In `skills/orchestration/plan-orchestrator/SKILL.md` Mode 1 section, document the new
      flow branch: after worktree creation (existing step 6), if `--output orchestrate-dispatch`,
      skip the "STOP, new session" instruction and instead run the confirm gate (1.3) then dispatch.
- [x] 1.3 Implement the confirm-before-dispatch `AskUserQuestion` gate (SPEC §3.7): show the
      generated ORCHESTRATE summary + worktree path, options **dispatch-now / review-first /
      cancel**. This gate is a design requirement, not a suppressible prompt — document explicitly
      that `--yes` does NOT skip it (SPEC §6 e2e test).
- [x] 1.4 Implement the self-containment prompt shape (SPEC §3.3): the dispatched `Agent`'s entire
      prompt is "read `ORCHESTRATE-<topic>.md` in full, then execute it" — no other context passed.
- [x] 1.5 Document the GRILL-file precondition as warn-only (SPEC §3.6/§3.11 in the grill,
      branches 6 and 11): if no `GRILL-*.md` exists for the spec's topic, print an advisory
      warning, do not block. Document the ungrilled backstop: an agent hitting genuine unresolved
      ambiguity leaves that phase's checkbox unchecked, adds a one-line blocker note, and stops.

**Key files:**

- `commands/orchestrate/plan.md` (update — frontmatter arg description only, stays a thin shim)
- `skills/orchestration/plan-orchestrator/SKILL.md` (update — Mode 1 section)

**Acceptance:** `--output orchestrate-dispatch` documented end-to-end in the skill; confirm gate
and self-containment prompt shape specified precisely enough for the e2e tests in Phase 4 to
assert against.

---

## Phase 2 — Concurrency cap, failure/hang detection, confirmed-failure disposition

**Scope:** the three safety mechanisms that don't exist in the STOP-new-session mode because a
human session doesn't need them.

- [x] 2.1 Document the concurrency cap (SPEC §3.9): soft cap of 2 concurrent
      `orchestrate-dispatch` dispatches per session; explicit confirm gates any 3rd+. **Scope the
      counter to `orchestrate-dispatch`-labeled calls only** — do not count unrelated background
      `Agent` calls the session may have running (this scoping is the part most likely to be
      silently gotten wrong; write it as an explicit rule in the skill, not an implication).
- [x] 2.2 Document failure/hang detection (SPEC §3.10): cross-check the Agent tool's completion
      notification against the ORCHESTRATE file's own checkboxes.
  - Notification fires, no checkboxes moved → flag suspected silent failure, do not offer merge.
  - No notification within the hang-detection window → surface crash/hang explicitly, do not wait
    silently.
- [x] 2.3 Document the hang-detection window formula (SPEC §3.10, grill branch 14): **2× the
      dispatched ORCHESTRATE file's own stated phase-effort estimate** — not a fixed wall-clock
      constant. State explicitly where that effort estimate comes from (the Phase Overview table's
      Effort column, already required by Mode 1's existing template).
- [x] 2.4 Document confirmed-failure disposition (SPEC §3.11, grill branch 15): on a confirmed
      silent-failure or hang, leave the worktree and branch in place — never auto-delete. Add a
      `.STATUS` note in the same HELD style already used for PR #237 this session.

**Key files:**

- `skills/orchestration/plan-orchestrator/SKILL.md` (update — new subsections under Mode 1)

**Acceptance:** all three mechanisms specified with enough precision that the dogfood tests in
Phase 4 can assert the concurrency-counter scoping and the hang-window formula against concrete
examples (not just prose).

---

## Phase 3 — Resumability + `.STATUS` auto-write scoping

**Scope:** the two remaining behaviors that make `orchestrate-dispatch` safe to re-invoke and
safe to track without manual busywork.

- [x] 3.1 Document resumability (SPEC §3.8): re-dispatching against the SAME ORCHESTRATE file
      detects already-checked `- [ ] 1.1`-style phases (via the Phase Overview status column,
      branch 5's own tracking) and instructs the new agent to start from the first unchecked
      phase, never restart from Phase 1.
- [x] 3.2 Document `.STATUS` auto-write scoping (SPEC §3.12): auto-write only the factual fields
      (branch, path, PR link once opened) at dispatch time. The narrative/purpose prose column
      stays manual — do not attempt to auto-generate it.

**Key files:**

- `skills/orchestration/plan-orchestrator/SKILL.md` (update — resumability + `.STATUS` subsections)

**Acceptance:** resumability logic references the exact tracking mechanism from Phase 1/2 (no new
tracking invented); `.STATUS` auto-write is scoped to factual fields only, verified by inspecting
a sample entry.

---

## Phase 4 — Documentation & Discoverability (REQUIRED — final phase)

- [x] 4.1 Update `docs/guide/pipeline-orchestrate-guide.md` (already documents Mode 1) with a new
      subsection: `orchestrate-dispatch` vs. the existing STOP-new-session mode — when to use
      which, with the token/attention-cost tradeoff from the grill's "Prior research" section.
- [x] 4.2 Help + command reference pages: update `commands/orchestrate/plan.md`'s own doc examples
      to show the third `--output orchestrate-dispatch` value.
- [x] 4.3 REFCARD — checked `docs/reference/orchestrate-reference.md` and `docs/REFCARD.md`: **N/A
      — neither file has an `output` value table to extend.**
- [x] 4.4 Help hub / discovery — checked `commands/hub.md` (line 629, one-line pointer to the
      skill, no per-flag detail) and `commands/smart-help.md` (no `orchestrate:plan` reference at
      all): **N/A — no new entry needed, confirmed explicitly, no new command was added.**
- [x] 4.5 Website — no new nav page added (existing guide page updated in 4.1); `mkdocs build
      --strict` run, exit 0, no warnings attributable to files touched in this branch (pre-existing
      unrelated INFO notices only — see Verification section results below).
- [x] 4.6 Catalog — `docs/skills-agents.md`: no new skill/command row added; existing
      `plan-orchestrator` row description extended with a one-line mention of the new mode.
- [x] 4.7 CHANGELOG `[Unreleased]` entry added to both `CHANGELOG.md` and `docs/CHANGELOG.md`
      (kept mirrored per this repo's own convention).
- [x] 4.8 `./scripts/validate-counts.sh` clean (expect **no count changes** — flag enum, not a new
      command/skill/agent; confirm this expectation holds, don't assume).
- [x] 4.9 `./scripts/docs-staleness-check.sh` clean — GREEN, 0 issues across all 4 phases.

---

## Test Plan (from SPEC §6 — emit as red-first stubs, tier-inferred: flag/prose-only change → e2e + dogfood)

### e2e

- [ ] `--output orchestrate-dispatch` on a spec with no `GRILL-*.md` present → warns (not blocks),
      proceeds to the confirm gate. `# TODO(author): delete if not contract-bearing`
- [ ] Confirm gate presents dispatch-now/review-first/cancel; `--yes` does NOT suppress this gate
      (design decision, not a prompt-refiner echo). `# TODO(author): delete if not contract-bearing`
- [ ] Re-dispatch against an ORCHESTRATE file with Phase 1 already checked → the new agent's
      prompt instructs skipping Phase 1. `# TODO(author): delete if not contract-bearing`

### dogfood

- [ ] Concurrency-cap counter only increments/decrements on `orchestrate-dispatch`-labeled agent
      calls, verified against a mixed session with unrelated background agents running.
      `# TODO(author): delete if not contract-bearing`
- [ ] Hang-detection window math: given an ORCHESTRATE file with a stated phase effort estimate of
      `X`, the documented flag-as-hung threshold is `2X`, not a hardcoded number.
      `# TODO(author): delete if not contract-bearing`

Unselected tiers (unit, integration, dependency, count-cascade): **N/A** — this change is
documentation/prose within an existing skill file, no new parser, script, cross-command data
flow, external dependency, or new command/skill/agent.

---

## Friction Prevention

- **Context first**: read this ORCHESTRATE file and the SPEC + GRILL before starting work.
- **Verify location**: confirm CWD is the worktree, not the main repo, before any edit.
- **No autonomous starts**: after each phase, STOP and confirm before proceeding.
- **Test per phase**: run the Verification section's commands after each phase.
- **This is a meta-feature** (planning the planner) — be extra careful not to conflate the
  `orchestrate-dispatch` MODE being specified here with the dispatch MECHANISM used to implement
  this very plan. They may or may not be the same invocation depending on how this ORCHESTRATE
  file itself gets executed — that's an operational choice for the dispatching session, not
  something this plan's content should assume.

## Acceptance Criteria

- [x] `plan-orchestrator/SKILL.md` Mode 1 documents `orchestrate-dispatch` as a third `output`
      value, with the confirm-before-dispatch gate and self-containment prompt shape.
- [x] Concurrency-cap logic is scoped to `orchestrate-dispatch` calls only, not all background
      agents.
- [x] Failure/hang detection cross-checks notification against ORCHESTRATE checkboxes, with the
      2×-effort-estimate window — not a fixed constant.
- [x] Confirmed-failure disposition leaves worktree/branch in place + adds a HELD-style `.STATUS`
      note.
- [x] Resumability: re-dispatch against a partially-complete ORCHESTRATE file skips already-checked
      phases.
- [x] `.STATUS` auto-write covers only factual fields; narrative prose stays manual.
- [x] Documentation & Discoverability phase complete (tutorial/guide update, REFCARD confirmed
      N/A, hub confirmed N/A, CHANGELOG mirrored, `validate-counts.sh` clean).

## Commit Strategy

Conventional commits, one per phase:

- `docs(plan-orchestrator): add orchestrate-dispatch output mode + confirm gate (Phase 1)`
- `docs(plan-orchestrator): document concurrency cap + failure/hang detection (Phase 2)`
- `docs(plan-orchestrator): document resumability + .STATUS write scoping (Phase 3)`
- `docs(orchestrate-dispatch): documentation + discoverability sweep (Phase 4)`

Then `gh pr create --base dev`. Commit as you go.

**Review gate:** under this session's standing authorization (see main repo `.STATUS`), the
dispatching session pushes/opens the PR/merges directly once CI is green (or confirmed-benign per
the documented `Validate Plugin Structure` pattern) and the checkboxes + Verification section have
been re-run and confirmed — no separate ask per merge. Post-merge, run the applicable check
(`validate-counts.sh` / `docs-staleness-check.sh`).

## Verification

```bash
# Full suite via a working interpreter (bare python3 on this Mac is Xcode's 3.9 — crashes on
# dict | None in commands/_discovery.py; use a 3.10+ interpreter)
/opt/homebrew/bin/python3.13 -m pytest tests/ -q
# Baseline at time of writing: 2072 passed / 7 failed / 13 errors (documented, env/pre-existing —
# NOT regressions; compare against this exact count, not zero)

./scripts/validate-counts.sh          # expect: no count changes (flag enum, not new surface)
./scripts/docs-staleness-check.sh     # expect: green
mkdocs build --strict                 # expect: 0 warnings
```

## Session Instructions

### Context

You are in the **craft repo worktree** for the `orchestrate-dispatch-mode` feature. This is a
**documentation-only change** to an existing skill (`plan-orchestrator/SKILL.md`) and its thin
command shim (`commands/orchestrate/plan.md`) — no new command, skill, or agent file. The SPEC has
full design details; the GRILL has the resolved decision ledger this SPEC was synthesized from.

### How to Start

```bash
cd ~/.git-worktrees/craft/feature-orchestrate-dispatch-mode
claude
```

On session start, paste:

> Read `docs/plans/ORCHESTRATE-orchestrate-dispatch-mode-2026-07-01.md` and the linked SPEC +
> GRILL. Start Phase 1.

### Phase-by-Phase

1. Read current state of each file listed in the phase.
2. Implement changes per the SPEC's design (§3, cross-referenced to grill branch numbers).
3. Run verification after each phase.
4. Commit in logical groups.
5. STOP and confirm before next phase.

## .STATUS + tracking

- Add an Active Worktrees row for `feature/orchestrate-dispatch-mode` when the worktree is created
  (factual fields only, per this plan's own Phase 3 principle — branch, path, purpose one-liner).
- Update each Phase Overview status cell (☐ → ⏳ → ✅) as phases complete.
