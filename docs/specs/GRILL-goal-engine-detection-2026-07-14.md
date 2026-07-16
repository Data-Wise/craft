---
tags: [grill, orch-drive, goal-engine, precondition]
status: closed
created: 2026-07-14
closed: 2026-07-14
spec: INVESTIGATE-goal-engine-detection-2026-07-14.md
---

# GRILL: `/goal` engine detection gap in `/craft:orch:drive`

Adversarial interrogation of `INVESTIGATE-goal-engine-detection-2026-07-14.md`'s 3 candidate
next steps before any implementation. 5 branches; the design changed twice mid-grill as
successive checks invalidated earlier answers — the final fix is empirical, not predictive.

**Status: CLOSED.** Proceeds to implementation directly (small, well-scoped prose-instruction
edit to `commands/orch/drive.md`).

## Decision ledger (5 branches, with 2 corrections)

| # | Gap pressed | Resolution (evolved across the branch) |
|---|---|---|
| 1 | **Riskiest assumption** — is a detection signal for "not Claude Code CLI at all" buildable? | Initial answer: yes, via tool/skill introspection. **Overturned by adversarial check**: `/goal` is a native slash command in the real CLI, not a discrete introspectable tool — the same way none of this repo's own `/craft:*` commands appear as "tools" in a session's tool list either. Tool-introspection can't distinguish "CLI with `/goal`" from "SDK without it," since neither surfaces it as an inspectable object. **Final**: detection must be empirical (observe the real attempt), not predictive. |
| 2 | **Weakest recommendation** — HOW does a prose-only command file perform any check? | Initial answer: add an explicit "check for a /goal-shaped tool" instruction. **Superseded by branch 1's reversal** — this instruction has nothing coherent to check for. |
| 3 | **Benefit honesty** — is "use `/craft:orch --swarm` instead" the right remedy text, given this session's own earlier grill found `--swarm` adds zero value for single-scope tasks? | **Corrected**: remedy text must lead with "assess scope first" — direct implementation for single-scope specs, `--swarm` only as a footnote for genuinely parallelizable specs. The original candidate (bare "--swarm" pointer) would have repeated an over-broad recommendation this same session already caught and fixed once. |
| 4 | **Workflow discipline** — does candidate 3 (check sibling `/goal`-dependent surfaces) need more work? | Pre-sweep found `workflow-engine` has zero `/goal` references. Deeper sweep (requested) checked `plan-orchestrator`'s actual invocation paths — its only "goal" mentions are an unrelated sprint-planning `--goal <text>` flag. **Confirmed closed, no gap**: only `orch:drive`/`drive-engine` depend on `/goal`; no fix needed elsewhere. |
| 5 | **Final scope + probe safety** — given detection must be empirical (branch 1's correction), does a separate "probe" emission risk setting a real goal state in a working CLI session? | **Resolved**: no separate probe. Step 6's real condition emission IS the test — in a working CLI, it correctly starts the drive loop (no wasted attempt); in a non-CLI harness, nothing observable happens, and *that absence* is the block signal, reported after the one real attempt rather than predicted before it. |

## Net effect (final fix, ready to implement)

1. **Drop the Step 2 predictive precondition check entirely** for the "wrong harness" class — it
   cannot be checked in advance (branch 1). The version/hook-policy checks in the existing table
   stay as-is; only the new class differs by being empirical.
2. **Step 6 gains a documented empirical fallback**: after emitting `/goal <condition>`, if there
   is no observable effect (no goal-status echo, no state change reported), STOP and report
   "no observable effect after emitting `/goal` — this harness likely doesn't support the native
   `/goal` engine" rather than proceeding as if the loop is running.
3. **Rewrite the remedy text** (wherever it's surfaced — the block message, not the precondition
   table row, since the check itself moved from predictive to empirical): lead with "implement
   the spec directly" for single-scope work, `--swarm` only for specs that genuinely decompose
   into independent parallel scopes.
4. **No fix needed for sibling surfaces** — `workflow-engine` and `plan-orchestrator` confirmed
   clean via both a grep sweep and a deeper invocation-path check.

## What the adversarial pass actually caught

Branch 1's reversal is the load-bearing catch this grill produced: the brainstorm-stage
candidate ("add a detection signal") looked reasonable and specific, but rested on an unverified
assumption (that `/goal` is introspectable as a tool) that turned out to likely be false for
*both* environments, not just the one lacking `/goal`. Without the adversarial check, this would
have shipped a "fix" that doesn't actually detect anything — the exact failure mode (an
uncheckable check) the investigation doc originally complained about, just relocated rather than
resolved.

## Handoff

Implement directly in this worktree (`feature/goal-engine-detection`) — a 2-3 line edit to
`commands/orch/drive.md`'s Step 2/Step 6/remedy text. No new files, no test-suite implications
(prose-instruction change only). Commit, then hold for PR per house rules (never auto-merge).
