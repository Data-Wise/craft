# SPEC: Evaluate `Workflow` Tool as Default Orchestration Engine (Stub)

**Status:** SUPERSEDED (2026-06-17). This stub framed a *platform* `Workflow` engine as the
goal. An adversarial review found that infeasible for craft (craft commands dispatch via the
Task tool; there is no host `Workflow()` callable). The feasible decision — make craft's own
deterministic `:workflow` mode the default — now lives in
`SPEC-orchestrate-token-efficiency-2026-06-17.md`. This stub is retained only as a
decision-trail record; do not implement from it.

---

> **⚠️ Superseded.** Everything below was the *deferred* framing. It no longer governs — see
> `SPEC-orchestrate-token-efficiency-2026-06-17.md` for the active plan. Kept for history.

**Status (original):** stub / placeholder — NOT scheduled. Enabled by, but out of scope of,
`SPEC-orchestrate-token-efficiency-2026-06-17.md`.
**Created:** 2026-06-17
**From Brainstorm:** interactive `/workflow:refine` session — named destination for the
"make dynamic workflow the default" question, deliberately deferred
**Author:** dt + Claude

---

## Why this stub exists

During the token-efficiency brainstorm, the question arose: *should orchestrate's fan-out
be migrated to the deterministic `Workflow` tool as the default engine?* That migration was
**deliberately deferred** — it overlaps the architecture-consolidation goal that was set out
of scope, and it is an engine rewrite (behavior + test churn), not a token-only change.

This file is the **named destination** so the on-ramp has somewhere to point. It is a
placeholder, not an active plan.

---

## What must be true before this is picked up

- `SPEC-orchestrate-token-efficiency-2026-06-17.md` Phase 0 is shipped (engine-agnostic
  token measurement exists).
- A measured **head-to-head** on the same reference task: orchestrate Task-dispatch vs.
  `Workflow`-tool dispatch — tokens, control, behavior parity.
- Levers B (prompt-level scoping) and C (cache/routing) are shipped, so we know how much of
  the `Workflow` tool's advantage is already captured inside the current engine.

---

## Candidate scope (to be designed if activated)

- Decide whether `Workflow` becomes the default for the parallel/wave path, an opt-in mode,
  or stays a sibling.
- Reconcile `orchestrator.md` vs `orchestrator-v2.md`; `orchestration` vs `workflow` skills.
- Define behavior/UX parity and migration/test strategy.
- Worktree posture: `Workflow` uses per-agent `isolation:'worktree'` opt-in (parallel-write
  only); confirm no regression vs. `--swarm`.

---

## Decision gate

**Do not start** until the head-to-head measurement justifies the rewrite cost. If Levers
B/C already capture most of the `Workflow` tool's token advantage, this may be closed as
**won't-do** rather than implemented.
