# GRILL: Orchestrate-Family Simplification — First-Wave Scoping

**Target:** [PROPOSAL-orchestrate-family-simplification-2026-07-01.md](PROPOSAL-orchestrate-family-simplification-2026-07-01.md) (approved 2026-07-01)
**Date:** 2026-07-01
**Outcome:** 5 branches resolved (3 scoping + 2 convention), all on recommendation (user said
"go", did not override). **Wave 1 = ranks 1–3**, unblocked and independent of the 2 convention
branches. Handed off to an ORCHESTRATE-only plan for wave 1. All decisions reversible.

Convergent interrogation of the approved proposal's "Not decided yet" section. Two of the five
branches (marked **[convention]**) change craft-wide doc conventions, broader than the
orchestrate-family refactor itself — grilled as their own branches so scope-expansion stays
explicit.

## Decision Ledger

| # | Branch | Decision |
|---|---|---|
| 1 | First-wave scope | **Ranks 1–3 only** — delete fictional `resume.md`, thin-shim `plan.md`, extract shared engine ref. All low-risk; two reuse the PR #236 playbook; the trio unblocks the held orchestrate-dispatch design by removing the plan-template duplication. Defers the risky T1 `do.md` rewrite (rank 5) + ranks 6–8 to a wave 2 gated on the ~2026-07-14 `/usage` checkpoint. |
| 2 | Grill-then-plan vs. hold | **Proceed to plan now** — generate an ORCHESTRATE-only doc for wave 1 immediately (durable tracking artifact, a `.md` safe on `dev`). Worktree creation + actual code implementation stay **explicit user-triggered** steps (no-branch-switch rule): the implementing session/agent creates `feature/orchestrate-family-wave1` off `dev`. Not held. |
| 3 | Verify finding #6 first | **Deferred, not in wave 1.** Finding #6 (`--orch` reach on `check`/`docs:sync`/`ci:generate`) isn't touched by ranks 1–3. When a later wave touches `--orch`, first verify those 3 commands actually parse the flag before any doc/code change. Not blocking now. |
| 4 | **[convention]** Doc-types enforced vs. session-only | **Documented convention, advisory — not machine-enforced yet.** Adopt the proposal's doc-type defaults/options table as written guidance (a reference doc / CLAUDE.md note), matching craft's ADR-003 gentle-ramp precedent (advise before gate). A lint rule recognizing `PROPOSAL-*.md` can follow if the pattern proves durable. **Separable from wave 1** — does not block the code refactor. Reversible. |
| 5 | **[convention]** PROPOSAL as first-class type | **Promote `PROPOSAL-*.md` as a first-class, lightweight type** distinct from `SPEC-*` (different audience: PROPOSAL = review-gate awaiting your decision; SPEC = design source-of-record). Lightweight = naming convention + `brainstorm`-skill awareness, not a new pipeline. **Separable from wave 1.** Reversible. |

## Open Questions

- [ ] Convention branches 4 & 5 were auto-resolved on recommendation under "go" — confirm or veto
      before they're written into craft's actual conventions (a separate, small doc/CLAUDE.md
      change, NOT part of wave 1 implementation).
