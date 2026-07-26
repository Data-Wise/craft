# GRILL: #263 Close-Out (RTK Hook Safety + branch-guard Robustness) — Decision Log

**Date:** 2026-07-26 · **Method:** one-question-at-a-time grill with user · **Result:** all 4 branches resolved, folded into `SPEC-rtk-hook-safety-close-out-2026-07-26.md`

---

## Why this doc exists

`SPEC-rtk-hook-safety-close-out-2026-07-26.md` found that #263's core hook-ordering question was
already answered (2026-07-07, official Claude Code hooks docs) but never cross-referenced back
into the craft-repo doc #263 actually points at. Four load-bearing branches were interrogated
before closing the issue or touching any file.

## Decision Ledger

| # | Branch | Decision |
|---|---|---|
| 1 | Docs citation vs. live confirmatory test | **Add one quick live confirmatory test.** The official-docs citation is authoritative, and RTK has been passively rewriting commands all session with branch-guard active and no bypass observed — but that's incidental, not deliberate, evidence. One staged test (a catastrophic pattern on a disposable branch, RTK active) turns it into deliberate, logged evidence at near-zero cost, without re-running the original 5-task disposable-repo apparatus the docs citation already makes redundant. |
| 2 | Fate of `SPEC-rtk-branch-guard-hook-order-probe-2026-07-01.md` | **Archive with a superseded pointer** — `Status: SUPERSEDED`, moved to `docs/specs/_archive/`, pointing at this close-out spec and `~/.claude/PROPOSAL-rtk-guard-safety.md`. Matches this repo's existing convention; avoids leaving a stale unexecuted 5-task plan live in the active specs directory. |
| 3 | Scope B — branch-guard robustness | **Include a narrow regression test now**, scoped exactly to today's confirmed bug (the `2>&1`/`1>&2` + literal `>` in quoted text false-positive), verified against a positive control (fails on pre-fix code). Directly tied to a real, confirmed gap — not speculative. |
| 4 | Wider audit (Patterns 2-4, catastrophic regexes) | **Explicitly deferred, not built.** Consistent with the 2026-07-07 PROPOSAL's own devops-lens guidance ("monitor errors, not metrics initially... revisit only if the empirical check actually surfaces a real gap") — today's gap was confirmed in Pattern 1 specifically; the other patterns are unconfirmed risk, and auditing them now would be exactly the premature-process anti-pattern that guidance already warned against once. |

## AMENDMENT (2026-07-26, same session) — decision #1's rationale corrected, decision unchanged

Post-grill verification (re-fetching `https://code.claude.com/docs/en/hooks` directly, rather
than trusting `~/.claude/PROPOSAL-rtk-guard-safety.md`'s quote of it) found the official docs
confirm **parallel hook execution** but do **not** explicitly state that a sibling hook's
`updatedInput` cannot affect a concurrently-evaluating hook — the PROPOSAL's "does not propagate
to sibling hooks" clause is not directly supported by the current doc text as fetched today.

This does not change decision #1's outcome (a live confirmatory test was already the chosen
option, not "docs citation alone"), but it changes the reasoning for why: the test is now the
primary evidence for #263's closure, not a belt-and-suspenders extra on top of an already-settled
question. Recorded here rather than silently correcting the SPEC's original framing, per this
repo's own convention (an amendment is a more useful record than a quietly-fixed claim).

## Notes for implementation

- Decision #1's live test is a *lighter* version of the original SPEC's Task 3 — one command,
  not three, and no disposable-repo setup/teardown (RTK is already installed globally, so
  Task 2's install/uninstall cycle doesn't apply).
- Decision #3's regression test should assert the exact failure mode found today: a command
  containing a literal `>` inside an already-quoted argument, combined with a trailing
  `2>&1`/`1>&2`, must NOT be misdetected as file creation — using the same
  `subprocess.run(["/bin/bash", "branch-guard.sh"], input=payload)` harness built during today's
  debugging session, with a positive control (git-stash the fix, confirm the test goes red,
  restore).
- Decision #4 means Scope B's acceptance criteria narrows to exactly one regression test — no
  broader Pattern 2-4 or catastrophic-regex changes are in scope for this close-out.
