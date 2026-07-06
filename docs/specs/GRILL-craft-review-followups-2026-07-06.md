# GRILL: Craft Review Follow-ups

**Target:** `docs/specs/SPEC-craft-review-followups-2026-07-06.md`
**Date:** 2026-07-06
**From SPEC:** `SPEC-craft-review-followups-2026-07-06.md`

---

## Decision Ledger

| # | Branch | Decision |
|---|---|---|
| 1 | H3 doc scope: does removing do.md's dead agent branch require sweeping the 24 docs that reference the 4 fictional agent names? | Yes, sweep all 24 in the same PR. Matches this repo's own memory: grep ALL callers including orphan scripts + tutorials when fixing a contract violation. |
| 2 | M1/M10 verify reuse mode: how should extending verify-surfaces.sh for ad-hoc incident diagnosis coexist with its existing BLOCK/exit-1 release-pipeline gating semantics? | Add a --report-only flag. Same script, same checks (5 existing legs + new GitHub-release + docs-site legs), but --report-only always exits 0 and prints ALIGNED/DRIFTED per surface. Release pipeline keeps the blocking default; incident diagnosis uses --report-only. |
| 3 | H3 test order: write the new routing test before or after deleting select_agent()'s dead branch? | Test-first: write test_do_score_4_7_no_agent_dispatch, confirm it fails against current code, then delete the dead branch and watch it go green. Avoids the same test-blind-spot class as M8's misdiagnosis and the dogfood hyphen-check bug. |
| 4 | G1: delete Chat-Instructions-v1.3.0.md outright, or commit-then-delete to preserve a git-history paper trail? | Just rm it. File is untracked (never committed) -- there is no history to preserve either way, and the canonical copy already lives outside this repo in ~/.claude/. |
| 5 | Verify UX: expose the new --report-only mode via a slash command, or leave it a raw script flag? | Fold into /craft:dist:surfaces -- add a --version override + the 2 new legs to its existing report. No new command surface, no REFCARD/count-cascade churn. |

---

## Open Questions

None remaining -- all branches load-bearing to implementation were resolved above. The
SPEC's own two Open Questions (extend-vs-new-script, command-vs-script-only) are answered
by decisions 2 and 5.

## Handoff

Ready for `/craft:plan` (tier 4, plan-orchestrator) -> `ORCHESTRATE-*.md` -> `/craft:do` /
`/craft:orch`. Grill does not execute -- this ledger is the locked artifact to hand forward.
