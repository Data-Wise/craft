# SPEC: #263 close-out — RTK hook-ordering resolution + branch-guard robustness

**Status:** GRILLED — 4 branches locked. See `GRILL-rtk-hook-safety-close-out-2026-07-26.md`.
**Date:** 2026-07-26
**Target:** `docs/internal/TUTORIAL-rtk-cli-token-proxy.md` §4.2, `docs/specs/SPEC-rtk-branch-guard-hook-order-probe-2026-07-01.md`, `~/.claude/hooks/branch-guard.sh`, craft's guard test suite
**Source issue:** #263 (RTK compatibility: verify hook-ordering safety against branch-guard.sh before adoption)

## Final scope (post-grill)

| Item | Call |
|---|---|
| Docs citation vs. live test | **Add one lightweight live confirmatory test** (one catastrophic pattern, disposable branch, RTK active) — not the full 5-task probe, not docs-citation-only |
| `SPEC-rtk-branch-guard-hook-order-probe-2026-07-01.md` | **Archive** to `docs/specs/_archive/` with `Status: SUPERSEDED` pointer |
| Scope B — branch-guard regression test | **Include**, narrowly scoped to today's confirmed `2>&1`/`1>&2` + quoted-`>` bug, with a positive control |
| Wider Pattern 2-4 / catastrophic-regex audit | **Explicitly deferred** — not built this pass |

The sections below are retained as the reasoning trail; superseded by the table above where they
floated open questions the grill has since resolved.

## Why this spec exists, and why it isn't the probe #263 originally asked for

Issue #263 (filed 2026-07-01) asked for an empirical probe in a disposable repo to determine whether
RTK's command-rewriting `PreToolUse` hook could defeat `branch-guard.sh`'s anchored
catastrophic-command regexes, and shipped a full 5-task verification plan
(`SPEC-rtk-branch-guard-hook-order-probe-2026-07-01.md`) to do it. A 2026-07-24 audit comment
left it open, calling it "an external-dependency risk assessment... needs an empirical
multi-hook-ordering test run against the actual tool, which this session didn't have set up."

Direct inspection today (2026-07-26) found the situation has moved past that framing:

1. **RTK is already installed globally on this machine** (`/opt/homebrew/bin/rtk`, confirmed via
   `which rtk`) and has been actively rewriting commands all session (`find` → `rtk find`,
   `pytest` → `rtk pytest`, observed live in this transcript). This directly contradicts #263's
   own precondition ("do not install RTK globally on this machine... until the verification plan
   below has been run").
2. **Partially, not fully, answered by documentation — corrected during this spec's own grill.**
   `~/.claude/PROPOSAL-rtk-guard-safety.md` (dated 2026-07-07) cites
   `https://code.claude.com/docs/en/hooks` for the claim: "Each hook receives the **original**
   tool input... it does not propagate to sibling hooks." **Re-fetching that page directly during
   this spec's own verification pass found only the first half confirmed** — the current docs
   state plainly: *"All matching hooks run in parallel, and identical handlers are deduplicated
   automatically"* — but say nothing explicit about whether an earlier/sibling hook's
   `updatedInput` can affect what a concurrently-running hook evaluates. Parallel execution is
   necessary but not sufficient to guarantee isolation; the PROPOSAL's "does not propagate"
   clause was either true of an older doc revision, or an inference presented with more
   confidence than the current source supports.

   **Consequence for this spec:** the live confirmatory test (see Scope A) is not a
   nice-to-have precaution on top of an already-settled question — it is the thing actually
   carrying the safety claim, since the docs alone leave the cross-hook-isolation question
   genuinely open. This correction doesn't change #263's practical bottom line (RTK has run
   alongside branch-guard all session with no observed bypass), but it changes *why* the close-out
   is safe to do: observed behavior plus one deliberate test, not documentation citation alone.
3. **`~/.claude/settings.json` already carries a dated note** recording this resolution and why
   the hook array order (guards before `rtk hook claude`) is intentional documentation, not a
   safety dependency.
4. **What's actually still stale is craft-repo-local**: `docs/internal/TUTORIAL-rtk-cli-token-proxy.md`
   §4.2 still reads "unverified," "what I don't know, and you should verify before relying on
   this," "I haven't independently verified" — none of which is true anymore. This is the one
   piece #263's own acceptance criteria explicitly named ("`docs/internal/TUTORIAL-rtk-cli-token-proxy.md`
   §4.2 updated to reflect the confirmed result instead of 'unverified'") and it was never done,
   because the resolution happened in a different file (`~/.claude/PROPOSAL-rtk-guard-safety.md`,
   outside the craft repo) that nobody cross-referenced back into the tutorial.
5. **A genuinely new, unrelated finding from today**: while debugging a real user-reported
   `branch-guard.sh` false positive (`git commit -m "...(7 -> 9)" 2>&1` misdetected as file
   creation — see PR history 2026-07-26), the exact empirical hook-invocation technique #263's
   probe plan called for (synthetic stdin JSON fed directly to `branch-guard.sh`, bypassing the
   Claude Code harness) was used and *did* surface a real branch-guard robustness bug — just a
   different one than the RTK question. This suggests the technique is sound and possibly worth
   pointing at branch-guard's other extraction patterns (`tee`, `cp`, `touch`, and the
   catastrophic-command regexes #263 originally worried about) rather than closing the file
   entirely once #263's specific question is resolved.

## Scope A — Close #263 (mechanical, already-resolved)

1. Rewrite `docs/internal/TUTORIAL-rtk-cli-token-proxy.md` §4.2 from "unverified risk" framing
   to "resolved" framing: cite `~/.claude/PROPOSAL-rtk-guard-safety.md`'s official-docs finding,
   state the guarantee (parallel execution, no cross-hook input mutation) as the reason RTK and
   branch-guard coexist safely, and drop the "what I don't know" hedging paragraph entirely
   (nothing in it remains true).
2. Decide the fate of `SPEC-rtk-branch-guard-hook-order-probe-2026-07-01.md`: it is now
   superseded by evidence, not executed. Options: (a) mark `Status: SUPERSEDED` at the top with
   a pointer to the resolution, moved to `_archive/`, consistent with how other superseded specs
   in this repo are handled; (b) leave it live as a template for a *future* similar question
   (a different tool with the same rewrite mechanism) since its task structure is generic and
   reusable. **Open — grill this.**
3. Close #263 on GitHub with a comment linking both the tutorial fix and
   `~/.claude/PROPOSAL-rtk-guard-safety.md` as evidence, rather than the originally-planned
   probe-execution comment.

## Scope B — branch-guard.sh robustness audit (new, from today's finding)

Today's fix patched exactly one instance of a false-positive class in Pattern 1's coarse
redirect-detection gate (`2>&1`/`1>&2` fd-duplication wrongly satisfying "a real redirect is
present," then extraction misattributing an unrelated `>` elsewhere in the command). The same
*general* risk — a coarse gate over-triggering, then a fine extraction re-scanning the whole
original command and picking up unrelated quoted-text characters — could exist in:

- Pattern 2 (`tee`), Pattern 3 (`cp`), Pattern 4 (`touch`) — do any of these have an analogous
  coarse/fine mismatch?
- The catastrophic-command regexes #263 itself was worried about (`git commit|push`, `git reset
  --hard`, `rm -rf .git`) — these are anchored patterns, a structurally different mechanism than
  Pattern 1-4's extraction, but worth one confirmatory pass now that the hook-invocation test
  technique is proven out (Scope A's resolution didn't require it, but Scope B's audit can reuse
  the exact `subprocess.run(["/bin/bash", "branch-guard.sh"], input=payload)` harness built today).

**Open question for the grill:** is this audit worth doing *now*, piggybacking on today's
momentum and reusable test harness, or is it exactly the kind of "over-build process before a
risk is confirmed real" the 2026-07-07 PROPOSAL explicitly warned against for a *different*
open item (the regression-test-suite deferral)? The PROPOSAL's own devops-lens guidance was:
"monitor errors, not metrics initially... do not build this now... revisit only if the
empirical check actually surfaces a real gap." Today's `2>&1` bug *is* exactly that — a real
gap the empirical check surfaced. That arguably reopens the case for at least a narrow
regression-test addition (not a general fuzzing framework), scoped to the specific bug class
found, not a comprehensive audit of every pattern speculatively.

## Acceptance criteria

**Scope A:**

- [ ] `docs/internal/TUTORIAL-rtk-cli-token-proxy.md` §4.2 rewritten, "unverified" framing removed
- [ ] `SPEC-rtk-branch-guard-hook-order-probe-2026-07-01.md`'s fate decided (archive-with-pointer
      vs. keep-as-reusable-template) — decided by grill, not defaulted
- [ ] #263 closed on GitHub with evidence links

**Scope B (scope decided by grill — may be narrowed or cut):**

- [ ] If kept: a regression test added to craft's guard test suite for today's specific
      `2>&1`/quoted-`>` false-positive class (not a speculative audit of unrelated patterns)
- [ ] If cut: explicit decision recorded, not silently dropped

## Test plan

- Scope A is docs-only; verify via `docs-staleness-check.sh` (should stay GREEN — this doesn't
  touch counted surfaces) and a manual read-through confirming no remaining "unverified" language.
- Scope B, if kept: extend `tests/test_branch_guard*.sh` or add a new Python-harness test using
  today's `subprocess.run` pattern; verify it fails on the pre-fix hook state (git stash the fix,
  confirm red, restore) as a positive control.
