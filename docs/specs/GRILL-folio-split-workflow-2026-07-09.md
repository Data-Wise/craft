# GRILL — folio split, dynamic-Workflow implementation approach

> **Target:** How to implement the folio split (`ORCHESTRATE-folio-split.md`) using the dynamic
> `Workflow()` agent fan-out — capturing parallel speedup without racing the serial gates.
> **Date:** 2026-07-09
> **Feeds:** an execution-design addendum to `docs/plans/ORCHESTRATE-folio-split.md`.
> **Upstream:** `docs/specs/GRILL-folio-split-2026-07-09.md` (the architecture; B1–B5 locked).

## Codebase / tool evidence (pre-grill)

- **Workflow fit:** the split's phase spine (P0→P2→P3, cross-repo, breaking) is dominantly serial
  and hard-gated. `Workflow()` is built for parallel decompose-and-cover, not serial gates.
- **Two structural blockers for naive fan-out:** (1) Workflow agents inherit the parent's cwd —
  folio is a NEW repo, so cross-repo agents can't just `cd`; (2) `isolation:'worktree'` per agent
  conflicts with a `git subtree split` (agents would diverge from the history being preserved).
- **Where fan-out genuinely helps:** P0 parallel caller-audit (per namespace), P2 mechanical
  repoint pipeline (per file), P3 count-cascade sweep (~30 files), and adversarial verification of
  the two gates (P0 partition, P3.4 "craft builds its own site").

## Decision Ledger

### W1 — Workflow's role vs. the serial gate spine  ✅ LOCKED

**Decision:** **Fan-out INSIDE phases; the live parent session owns the serial sequence and every
gate.** Each phase dispatches its own Workflow only for the independent sub-work within it.

**Why:** no agent ever crosses a go/no-go gate or races shared-file mutation; the human checkpoint
stays at each breaking step (craft v4.0.0, new-repo creation). Rejects the single-Workflow-all-phases
option (turns breaking gates into unattended script barriers) and the read-only-only option (leaves
real P2/P3 mechanical speedup on the table).

**Consequence accepted:** the orchestration is NOT one script — it's the parent driving a sequence
of smaller per-phase Workflow dispatches, reading each schema'd result to clear the gate before the
next.

### W2 — cross-repo execution: who runs git, where do agents point?  ✅ LOCKED

**Decision:** **The parent session runs ALL git operations itself** (worktree add, subtree split,
repo create, commits, cross-repo moves) — never an agent. Agents receive **explicit absolute paths**
(craft worktree path OR folio repo path) and do only file-content work (grep, repoint, write
tests). **No `isolation:'worktree'`.**

**Why:** the irreversible + cross-repo git work stays in one controlled place; agents become pure
content transforms with no cwd ambiguity. Rejects per-agent isolated worktrees (conflicts with the
subtree-split history preservation; agents can't create the folio repo) and two-parent-sessions
(loses the single-orchestrator gate handoff). Matches the session-proven "dev session implements
onto a worktree via absolute paths" pattern (memory `dynamic-workflow-runs-from-worktree-session`).

**Consequence accepted:** agents can't self-verify by running the repo's git; the parent must stage
and verify every mutation the agents produce (which is desired for a breaking change anyway).

## Handoff (grill closed 2026-07-09)

W1–W2 locked interactively above. The remaining branches (W3 which-phases-get-Workflows,
W4 schemas/verification, W5 budget/concurrency) were resolved as **reviewable spec decisions** in
`docs/specs/SPEC-folio-split-workflow-2026-07-09.md` — the user redirected mid-grill to produce
the artifacts via the native spec-driven flow rather than continue question-rounds. Empirical
grounding: Phase 0 already executed under this exact model (parent gate + read-only fan-out,
7 agents, adversarial verify) and passed. Plan artifacts: `tasks/plan.md` + `tasks/todo.md`
(working, feature-branch only).
