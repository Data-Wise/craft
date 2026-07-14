# INVESTIGATE: `/goal` engine detection gap in `/craft:orch:drive`

**Date:** 2026-07-14 | **Trigger:** live failure — `/craft:orch:drive` invoked against a real
approved SPEC (savant issue #198) from a Claude Agent SDK/CCD session (not the interactive
Claude Code CLI). No `/goal` tool, skill, or mechanism was available; the command's precondition
table gave no way to detect this cleanly, so the executing agent had to infer unavailability by
absence rather than by any documented check.

**Grilled:** [GRILL-goal-engine-detection-2026-07-14.md](GRILL-goal-engine-detection-2026-07-14.md) — the initial detection idea (tool-introspection) was overturned mid-grill; the final fix is empirical (observe the real `/goal` attempt), not predictive. Read it first.

## Finding

`commands/orch/drive.md`'s precondition table (Step 2) lists:

| Check | Block reason | Remedy shown |
|-------|--------------|--------------|
| `/goal` available (Claude Code ≥ v2.1.139) | Engine missing | Upgrade Claude Code |
| Hooks not blocking `/goal` (`disableAllHooks` / `allowManagedHooksOnly`) | `/goal` disabled by policy | Adjust hook policy |

Traced this back to `docs/specs/SPEC-orchestrate-drive-2026-06-03.md`'s Acceptance Criteria
(line 76-79): the **only** documented unavailability classes are:

1. Claude Code version < v2.1.139
2. `disableAllHooks` hook policy
3. `allowManagedHooksOnly` hook policy

None of these describe the actual failure mode encountered: **the executing harness is not
Claude Code CLI at all** — it's a different product (Claude Agent SDK / CCD) that shares the
same command/skill surface (this repo's commands and skills load identically in both) but has
no `/goal` primitive, no version string to check against v2.1.139, and no hook-policy flags to
inspect, because the whole `/goal` feature doesn't exist as a concept in that harness.

Searched the codebase for any existing harness-detection mechanism (`Cowork`, `SDK`, `harness`,
`isInteractive`, `CLAUDE_CODE_VERSION` env var, etc.) — found precedent for **Cowork vs. Claude
Code routing** at the ecosystem level (`~/projects/dev-tools/CLAUDE.md`'s "Cowork vs. Claude
Code (tool routing)" section) but nothing inside craft's own commands/skills that lets an
executing agent positively self-identify which harness it's running in. The precondition table
was written assuming its only audience is the interactive CLI, so "not that at all" was never a
considered case — a distinct gap from "old version of the right product."

## Why this matters

`drive`'s failure mode when this gap is hit is silent-ish: there's no error, no exception, just
an executing agent that has to reason from indirect evidence ("no /goal-shaped tool in my
available-tools list") rather than a documented, checkable signal. A less careful execution could
plausibly hallucinate a `/goal`-like behavior instead of correctly blocking — the precondition
table's intent (block clearly, never route around) depends on the check being *checkable*, and
right now, for this specific unavailability class, it isn't.

## Reproduction

1. Have an approved `docs/specs/SPEC-*.md` and a `feature/*` worktree (both real preconditions,
   satisfied).
2. Invoke `/craft:orch:drive <spec>` from a Claude Agent SDK/CCD session rather than the
   interactive Claude Code CLI.
3. Step 2's precondition table offers no mechanism to detect this before Step 6 attempts to
   emit `/goal <condition>` — which has nothing to receive it.

(Live-reproduced this session: savant issue #198, `docs/specs/SPEC-2026-07-14-profile-harvest.md`,
`feature/profile-harvest` worktree — both real preconditions satisfied, `/goal` still
unavailable for the harness-mismatch reason above, not a version or hook-policy reason.)

## Not yet done (deliberately — investigation only, no fix built)

- No detection mechanism designed or implemented.
- No decision on remedy wording (today's "Upgrade Claude Code" remedy is actively wrong advice
  for this failure class — upgrading Claude Code CLI version does nothing for a session that
  isn't running Claude Code CLI at all).
- No decision on whether `drive-engine`/`workflow-engine` have the same blind spot (not
  investigated this pass — scoped to `orch:drive`'s own precondition table only).

## Candidate next steps (not started, needs its own brainstorm/grill pass)

1. Add a third unavailability class to the precondition table: "harness is not Claude Code CLI"
   — needs an actual detection signal (tool/skill introspection? an explicit environment
   marker? nothing exists today to check against).
2. Correct the remedy text for that class — "use `/craft:orch --swarm` instead" (this session's
   actual working fallback) rather than "Upgrade Claude Code" (wrong advice for this class).
3. Check whether `plan-orchestrator` / other `/goal`-dependent surfaces in this repo have the
   same gap.

## Status

Investigation only. No code changed. Findings ready for a brainstorm/grill pass before any fix
is built.
