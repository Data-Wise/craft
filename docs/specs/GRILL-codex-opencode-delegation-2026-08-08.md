# GRILL: Codex/OpenCode Delegation Routing — Adversarial Review

**Date:** 2026-08-08 · **Target:** [SPEC-codex-opencode-delegation-2026-08-08.md](SPEC-codex-opencode-delegation-2026-08-08.md)
**Branches interrogated:** 5 (riskiest assumption, weakest recommendation ×2, benefit honesty, workflow discipline/default policy)

Codebase-first sweep found the load-bearing issue before any question was asked: `codex-rescue`
is owned by the separately-installed `codex` plugin, not craft — no cross-plugin agent
invocation exists in this repo (established by craft's own prior router-consolidation audit).
Three of the SPEC's five candidate rows cited it as reuse precedent; Branch 1 corrects this.

## Decision Ledger

| # | Branch | Decision |
|---|---|---|
| 1 | delegation mechanism | Craft's `--delegate` flag shells to `codex exec` directly (same mechanism as the tutorial's Monitor template), never through the `codex-rescue` agent — that agent belongs to a different plugin and can't be invoked cross-plugin. SPEC's "why" column for `code:debug`/`code:refactor`/`ci:triage` needs rewording to drop the implied reuse; the underlying candidate choices stand, only the mechanism description was wrong. |
| 2 | monitoring enforcement | The "mandatory monitor" step is documentation-only today (copy-paste templates, nothing enforces use). New acceptance criterion: any future command implementing `--delegate` must ship with a test asserting its dispatch path includes a status/token check — same enforcement pattern as `--refine`'s `test_refine_default_policy_table_exhaustive`. Craft's own hooks-as-defense-in-depth precedent says prompts/docs alone get silently skipped; a doc-only requirement here would regress to fire-and-forget exactly the way the SPEC's own Problem statement complains about. |
| 3 | ci:fix vs ci:triage | Only `ci:triage` gets `--delegate`, not `ci:fix`. Triage is diagnosis-only (advisory output, human decides) — safe to delegate. `ci:fix` already mutates the repo; delegating a write-capable command's decision-making to an external model raises the blast radius with no safeguard proposed in this pass. Candidate list is now 4 distinct commands, not 5 (`code:debug`, `code:refactor`, `code:test-gen`, `arch:review`, `ci:triage` — `ci:fix` dropped). |
| 4 | cost-comparison honesty | The "650× cheaper" figure compares codex's raw token count against opencode's metered dollar cost — not like-for-like, since codex ran on a flat Plus subscription (sunk cost) while `opencode-go` bills per call. Token count is still a valid signal (context-window pressure, rate limits are real under a subscription too), but the SPEC/BRAINSTORM must state plainly that "650× cheaper" is a token-count fact, not necessarily a cash-cost fact, so a future reader doesn't misapply it as a dollar comparison. |
| 5 | default policy | `--delegate` defaults **OFF** on all 4 candidate commands — matches `--refine`'s existing OFF-default precedent for "execution engine" commands (`orch`/`orch:workflow`). Delegation costs real money/tokens and hits an external network dependency, unlike `--refine` (free, local, no network) — it should never fire silently. This also makes Branch 2's monitoring requirement easier to guarantee: an explicit, deliberate flag is easier to gate a test on than a heuristic auto-trigger. |

## Open Questions (not locked, hand to `/craft:plan`)

- Exact wording/placement of the corrected "why" column text for Branch 1 (mechanical doc fix,
  not a design decision — small enough to do inline when Task 1 is picked up).
- Whether the dogfood-test requirement from Branch 2 should live in a shared test helper (one
  test parametrized over all 4 commands) or 4 separate per-command tests — implementation
  detail, not blocking.
- Whether `code:test-gen`'s and `arch:review`'s delegation targets should also default to a
  specific `providerId`/`modelId` (e.g. always `deepseek-v4-pro` for review-shaped delegation,
  matching tonight's dogfood run) or require the user to specify one each time — not raised
  during this grill, worth a quick decision at implementation time.

## Documentation Plan

- `docs/specs/SPEC-codex-opencode-delegation-2026-08-08.md` — apply Branches 1, 3, 4, 5 (reword
  candidate table, drop `ci:fix` row, add cost-honesty caveat, add default-OFF decision + new
  acceptance criterion for the dogfood-test requirement).
- `docs/specs/BRAINSTORM-codex-opencode-delegation-2026-08-08.md` — Branch 4's cost-honesty
  caveat applies to its "Cost delta is ~650×" line too (same claim, same fix).
- No `commands/*.md` changes yet — `--delegate` itself is still unbuilt (SPEC D2/out-of-scope);
  this ledger only corrects and locks the design it will follow when built.
