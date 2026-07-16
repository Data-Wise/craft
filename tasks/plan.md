# Implementation Plan: v4.0.0 Train (folio split + v4 surface rider)

> Derived from `ORCHESTRATE-folio-split.md` (repo root — plan of record; corrected 2026-07-16,
> the `docs/plans/` path this line used to cite doesn't exist) — this file is the
> execution-grade breakdown (sized tasks, per-task verification, parallelization map).
> Working artifact: feature branch only, never merged to dev. Task detail: `tasks/todo.md`.

## Overview

Two coupled deliverables in ONE breaking release train: (1) extract folio (public docs-authoring
plugin, ≈15 cmds + 6 agents + 6 skills) from craft via history-preserving `git filter-repo`;
(2) the v4 surface rider — craft 69 → **26 commands** (roster locked, R1–R4). Parent session
owns all git + gates; dynamic Workflows fan out inside phases (W1–W5).

## Architecture Decisions (all locked — do not relitigate)

- B1–B5 (grill) · W1–W5 (exec spec) · border filter · R1–R4 roster — see the four
  `docs/specs/*folio*`/`*v4*` files. Deviations >±2 commands go back to the ledger.
- Mechanism: `git filter-repo` per-path (NOT subtree split). folio repo MUST be public.
- Salvage-before-delete everywhere (ADR-002); counts via bump-version.sh only; grep-zero
  docs gate; folio releases FIRST, craft tag LAST.

## Dependency Graph

```
P1 scaffold ──────────────────────┐
  T1.1 worktree                   │
  T1.2 public repo ← T1.1         │
  T1.3 skeleton ← T1.2            │
  T1.4 tooling ∥ T1.5 tap ∥ T1.6 protection+App   (parallel after T1.3)
                                  ▼ CP-1
P2 extraction: T2.1 filter-repo → T2.2 graft → { T2.3 repoint ∥ T2.4 salvage/merge }
               → T2.5 folio CI → T2.6 release workflows → T2.7 hub+site → T2.8 verify
                                  ▼ CP-2
P3 amputation: T3.1 rm → { T3.2 routing ∥ T3.3 tests ∥ T3.5 docs-sweep } → T3.4 ci-floor
               → T3.6 counts → T3.7 MIGRATION → T3.8 gates
                                  ▼ CP-3 (PR holds for 3.5)
P3.5 rider:   T3.5.1 salvage×12 → T3.5.2 kills → T3.5.3 consolidations (5 ∥ families)
               → T3.5.4 cascade+hub-regen+floor18 → T3.5.5 suites
                                  ▼ CP-3.5 → PR → dev (ask)
P4 release:   T4.0 sync-local-folio → T4.1 folio:do → T4.1b tests → T4.1c docs+version
               (∥ T4.2 rollback-runbook, no dependency on T4.0/T4.1/T4.1b/T4.1c)
               → T4.3 folio v1.0.0 (ask×4: PR/merge/tag/release) → T4.4 craft v4.0.0 (ask)
               → T4.5 verify fan-out
                                  ▼ CP-4 done (both repos' tasks/ cleaned up)
```

**Re-grounded 2026-07-16** (via `/agent-skills:planning-and-task-breakdown`): the original P4 line
above (`T4.1 folio:do ∥ T4.2`) undersold the real dependency chain — direct inspection of both
repos found `T4.1` (folio:do) doesn't exist as a file yet, folio's `origin/main` never received
Phase 1+2 at all (still the init scaffold commit — extraction only ever landed on `origin/dev`),
and CP-2's own flagged release-readiness gap (zero e2e/dogfood tests, `plugin.json` still `0.1.0`)
was never turned into a tracked task. `T4.0`/`T4.1b` were added; see `tasks/todo.md` Phase 4 for
full acceptance/verification per task.

**Adversarially re-checked 2026-07-16** (second pass — same skill, applied to its own output):

- T4.0's "3 unexplained local commits" resolved: diffed local `dev` vs `origin/dev` directly —
  local is purely *behind* (missing `scripts/aggregator-sync.sh` + stale `counts.json`), nothing
  to reconcile. Fast-forward/reset is safe.
- **New**: folio's `main` branch protection has `required_status_checks: None` — T2.6's own
  acceptance criterion to add one after the first green PR run was never executed, since `main`
  has never had a PR run against it. T4.3 as originally scoped would merge the first-ever
  `dev→main` PR with zero CI gate. Added as an explicit T4.3 sub-step.
- **New**: folio's `origin/dev` already carries a leftover `tasks/session-plan-T2.4-CP2.md`
  working file. CP-4's "delete tasks/ from branch" was singular/craft-only in the original
  wording; now explicit for both repos.
- **Split**: the original T4.1b bundled tests + version bump + docs under one M-sized task —
  realistically 15+ files across 3 independent concerns. Split into T4.1b (tests) and T4.1c
  (docs + version).
- **Unresolved, needs a human decision**: T4.2's rollback runbook doesn't address the
  partial-rollback case (folio ships, craft's release then fails/stalls) — is that a stable
  end-state on its own?

**`/goal`-readiness, 2026-07-16**: `/craft:orch:drive` (the `/goal` wrapper) synthesizes its
condition from a spec's `## Acceptance Criteria` + `## Review Checklist` sections, not from this
file's prose bullets. Two real SPECs now exist in that shape for the tasks that are actually
autonomous-loop-safe: `docs/specs/SPEC-folio-phase4-tests-docs-2026-07-16.md` (T4.1b + T4.1c,
folio repo) and `docs/specs/SPEC-v4-rollback-runbook-2026-07-16.md` (T4.2, craft repo — instructed
to stop and surface the partial-rollback question above rather than answer it). T4.3/T4.4
deliberately have no SPEC — each has multiple mid-flow human-ask gates, which doesn't fit `/goal`'s
autonomous-loop model; drive those by hand instead. See `tasks/todo.md` Phase 4 header for the
same note with per-task detail.

## Vertical slicing note

P2's unit of verticality = one moved file (move → repoint → verify via pipeline). P3.5's =
one command family (salvage → kill/consolidate → tests for that family). Never "all moves
then all tests."

## Checkpoints (every one = transcripts + adversarial sound=true + human ask)

- **CP-1**: folio public/valid/tooling-green/App installed
- **CP-2**: folio suites green · history proof (`git log --follow` ×3) · hub present
- **CP-3**: craft@69 pytest+bash+strict+grep-zero (PR held for 3.5)
- **CP-3.5**: craft@26, hub regenerated, floor 18, MIGRATION complete → the ONE PR to dev
- **CP-4**: both released (folio first), both green on main, rollback runbook exercised-dry

## Parallelization Map

| Safe parallel | Must be sequential |
|---|---|
| T1.4/T1.5/T1.6 · T2.3∥T2.4 · T3.2/T3.3/T3.5 sweep batches (disjoint files) · T3.5.3's five families · T4.2 (independent of T4.0/T4.1/T4.1b/T4.1c) | filter-repo before any repoint · P2 fully before P3 · salvage before ANY kill · counts (parent) after all file mutations · T4.0 before any folio-touching Phase 4 work · T4.1 before T4.1b/T4.1c (tests/docs should exercise the real `do.md`) · folio's main-protection status check configured before the T4.3 merge · folio release (T4.3) before craft tag (T4.4) |

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| filter-repo path list wrong | High | T2.1 dry-run against the disposition table; count grafted files before graft commit |
| Salvage diff misses unique logic | High | R2 gate mechanical (>150L); tripwire tests; 12 enumerated jobs |
| ci.yml floor forgotten in a PR | High | T3.4/T3.5.4 are explicit tasks; floors listed in CP checklists |
| Agent edits race on shared file | Med | Disjoint file lists per agent; parent commit-per-batch |
| dev moves under the worktree | Med | Rebase check at each CP; push dev before PRing |
| Release automation misfires | High | folio-first order; runbook (T4.2, `docs/RUNBOOK-v4-release-rollback.md`, craft PR #293 MERGED) written BEFORE any tag |
| folio's `main` has never actually received a release (still the init scaffold commit) — T4.3 is a first-time operation, not routine maintenance | High | Treat T4.3 as CP-1/CP-2-style gated (transcripts + human ask at merge/tag/release), not a quick follow-up; verify `origin/main` state directly before starting, don't assume from the plan doc |
| folio's `main` branch protection has zero required status checks — confirmed via `gh api`, not assumed | High | T4.3 now has an explicit sub-step to configure a required context BEFORE that PR merges, not after |
| homebrew-tap's `feature/folio-formula` still holds PLACEHOLDER sha256/url values | Med | Explicit sub-step inside T4.3 (finalize with real values only after the real tag exists) — sequencing already correct, just wasn't a tracked checklist item before |
| T4.2's runbook (now merged) states, but doesn't answer, the partial-rollback question (folio ships, craft stalls) | Med | Runbook's Path C presents arguments both ways and instructs stopping to ask — do not silently decide this in execution |

## Open Questions

Was "none blocking" — **corrected 2026-07-16, re-confirmed on a second adversarial pass**: T4.0
(local folio sync) is confirmed low-risk (pure staleness, no reconciliation needed) but still a
blocking pre-step. Two more gaps surfaced only by checking live state rather than trusting this
doc: folio's `main` has no required status check, and folio's own `tasks/` dir already has
leftover cruft. All P1–P3.6 decisions remain locked; execution-time deviations there still go to
the roster ledger (±2 tolerance). **T4.2 itself is done** (runbook merged, craft PR #293) — the
partial-rollback question is written into the runbook as an explicit open question rather than
answered, which satisfies T4.2's completion criterion. The underlying human decision is still
pending, though — it needs answering whenever T4.3/T4.4 sequencing is actually executed, not
before.
