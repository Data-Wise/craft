# Implementation Plan: v4.0.0 Train (folio split + v4 surface rider)

> Derived from `docs/plans/ORCHESTRATE-folio-split.md` (plan of record) — this file is the
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
P4 release:   T4.1 folio:do ∥ T4.2 rollback-runbook → T4.3 folio v1.0.0 (ask)
               → T4.4 craft v4.0.0 (ask) → T4.5 verify fan-out
                                  ▼ CP-4 done
```

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
| T1.4/T1.5/T1.6 · T2.3∥T2.4 · T3.2/T3.3/T3.5 sweep batches (disjoint files) · T3.5.3's five families · T4.1∥T4.2 | filter-repo before any repoint · P2 fully before P3 · salvage before ANY kill · counts (parent) after all file mutations · folio release before craft tag |

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| filter-repo path list wrong | High | T2.1 dry-run against the disposition table; count grafted files before graft commit |
| Salvage diff misses unique logic | High | R2 gate mechanical (>150L); tripwire tests; 12 enumerated jobs |
| ci.yml floor forgotten in a PR | High | T3.4/T3.5.4 are explicit tasks; floors listed in CP checklists |
| Agent edits race on shared file | Med | Disjoint file lists per agent; parent commit-per-batch |
| dev moves under the worktree | Med | Rebase check at each CP; push dev before PRing |
| Release automation misfires | High | folio-first order; runbook (T4.2) written BEFORE any tag |

## Open Questions

None blocking — all decisions locked. Execution-time deviations → roster ledger (±2 tolerance).
