# ADVERSARIAL REVIEW: Repo Triage

**Date:** 2026-08-07 · **Reviewed:** [`BRAINSTORM-repo-triage-2026-08-07.md`](BRAINSTORM-repo-triage-2026-08-07.md), [`GRILL-repo-triage-2026-08-07.md`](GRILL-repo-triage-2026-08-07.md)
**Method:** 4 independent parallel lenses (backend/systems, frontend/interaction, architecture, ADHD-friendly cognitive-load), each grounded against the real codebase, not just the planning docs.

## Verdict: 2 of the GRILL's 8 locked decisions rest on factually wrong premises

This isn't stylistic feedback — two lenses independently found the planning docs made claims
about the codebase that are false, and those claims are load-bearing for locked decisions.
Recommend re-opening those branches before `/craft:plan`, not proceeding past them.

## Blockers (resolve before `/craft:plan`)

| # | Lens | Finding | Why it's a blocker |
|---|---|---|---|
| 1 | Architecture | `skills/dev/git/SKILL.md` **Operation 13 ("Issue Premise Check")** already wraps `issue-check`'s `classify_issue()` as a skill operation (lines 300–322) — neither doc's codebase sweep found it, despite it sitting ~250 lines from Op 4/5 in the same file. | Decision 1 ("thin orchestrator, new skill") was decided against "extend `dev/git`," partly on the claim that `dev/git` "mixes git-mechanics with issue-triage judgment calls, a scope mismatch." Op 13 proves that mixing **already exists** in `dev/git` today — the scope-mismatch argument is contradicted by the file it's about. All 3 of repo-triage's planned dependencies (issue-check, Op4, Op5) already live inside `dev/git`. Decision 1 needs to be re-argued on the surviving argument (file size alone), not the false one. |
| 2 | Backend | `classify_issue()` (`commands/git/issue-check.md`) is **pure regex/stdlib Python — no LLM call**. BRAINSTORM's Risks section calls it "an LLM semantic read"; that's the doc's own factual claim about the code, and it's wrong per the code shown in the same file. | GRILL Decision 2 (pre-filter, concurrency cap of 15) was reasoned entirely around "expensive LLM read per issue." If `classify_issue()` is called by direct import, concurrency is moot (sub-millisecond CPU). If repo-triage instead shells out to `/craft:git:issue-check` as an agent-turn per issue, cost model is completely different (real LLM cost, real rate limits). The docs never picked an invocation mode — "15" isn't sized against any actual constraint until that's decided. |
| 3 | Backend | The 3-source merge ("one itemized list") has no defined schema, join key, or dedup rule. Op4 emits branch names as prose (no structured output today); Op5's `worktree clean` has no output contract at all; issue-check emits `{status, evidence[], reasoning}`. A worktree and its branch can each independently appear — nothing says whether they merge into one list item or two, and independent opt-outs on a coupled pair can leave the repo half-cleaned. | Merging is Decision 4's central mechanism ("merges... into one itemized list... single yes/no with per-item opt-out"). Without a schema this is unimplementable as specified, not just under-specified. |
| 4 | Frontend | "Batch confirm, per-item opt-out" has no mapping onto `AskUserQuestion`'s real constraint — **max 4 options per call**. `skills/code/SKILL.md` (~line 113) already documents the standard craft workaround (group by priority, show top 4, mention remainder) — neither planning doc references it. GRILL's own concurrency cap (15) guarantees runs routinely exceed 4 candidates. | Decision 4 as written ("single yes/no with per-item opt-out" across a merged list) cannot execute as one tool call at the scale the design's own numbers imply. This is the same category of gap as #1/#2: a claim about how the system works that doesn't hold. |
| 5 | Backend | Partial mid-loop failure (`gh issue view` errors/rate-limits on issue *k* of *n*; Op4/Op5 collection errors partway) is entirely undiscussed in both docs. | Decision 4's "execute approved items directly" assumes a complete, correct candidate list. A silently-partial list presented as complete is worse than a visible failure — this needs a decided behavior (abort / skip-and-continue / flag-incomplete), not silence. |
| 6 | Architecture | GRILL's own Open Questions (§3) flags "needs a contract test" for the Op5 `--dry-run` output, then explicitly defers the design to "the implementation plan, not the ledger." | Given finding #3, this is the load-bearing schema question, not a scoping nicety. Deferring it risks Op5's dry-run PR shipping a shape that doesn't fit what the merge actually needs, forcing rework. Resolve the field-level contract *before or alongside* the Op5 prerequisite fix, not after. |

## High (resolve before build; can wait on `/craft:plan` itself)

| # | Lens | Finding |
|---|---|---|
| 7 | Frontend | Flat merged list with no grouping by source (issues vs. branches vs. worktrees) — dissimilar-register items (LLM prose vs. field-dump git evidence) sit undifferentiated in one list. |
| 8 | ADHD | No cap or pagination on the batch-confirm list or the grill-ready bucket. This session alone hand-produced 5 actionable items (#327, PR #325, PR #321, 1 worktree, 1 branch) — a real run trivially exceeds the repo's own 5-item-list convention on its first use. |
| 9 | ADHD | No single "start here" pointer after a run completes. The architecture diagram fans out to 3 parallel buckets (grill/plan/defer) with no stated ordering — conflicts with "end with one concrete next action." |

## Medium

| # | Lens | Finding |
|---|---|---|
| 10 | Frontend | No shared evidence-citation template across the 3 item types — issue evidence is prose, branch/worktree evidence is field-dump; inconsistent rendering per source. |
| 11 | Frontend | "One-line rationale per group" is ambiguous — group-level taxonomy justification vs. per-item guidance; GRILL Decision 8 defines the former, which is a large information-density drop next to the delete-confirm section's rich per-item evidence. |
| 12 | ADHD | No duration/progress surfacing for the issue-check loop — even once #2 is resolved (whichever invocation mode), the user-facing design never shows "checking N/M" or a time estimate. |
| 13 | ADHD | No resume-after-interruption provision if the batch confirm is interrupted mid-execution — no partial-completion record. |
| 14 | Backend | Idempotency (safe to re-run) holds only by construction (each dependency re-reads live state), not by design — no test pins this property; a future change to any of the 3 dependencies could silently break it. |

## Low

| # | Lens | Finding |
|---|---|---|
| 15 | Architecture | No naming collision found against the ~40-skill inventory — checked, not a real risk. |

## Recommendation

Re-open GRILL branches **1, 2, 4, and 5/Open-Question-3** with the corrected facts before running
`/craft:plan` — proceeding on the current ledger would plan against premises two independent
lenses found to be false. Branches 3 (worktree-lock sequencing), 6 (pre-filter no-age-filter), 7
(content-diff scope), and 8 (bucket rule reuse) are unaffected by these findings and stay locked.

Suggested resolution order:

1. Decide issue-check's invocation mode (direct import vs. agent-turn shell-out) — this unblocks
   both #2 (concurrency sizing) and clarifies whether repo-triage's dependency on `issue-check` is
   a function call or a command dispatch.
2. Re-argue Decision 1 (new skill vs. `dev/git` Operation 14) now that Op 13 is known — the
   scope-mismatch argument no longer holds; decide on file-size grounds explicitly if the answer
   doesn't change.
3. Define the 3-source merge schema (join key, worktree/branch pairing rule) and the `AskUserQuestion`-compatible confirm UX (grouped-top-4-plus-remainder, per craft's existing pattern) together — they're the same underlying design gap (#3/#4) seen from two lenses.
4. Fold in the High/Medium findings (list caps, single next-action, evidence template) as GRILL
   branches or explicit SKILL.md requirements, whichever the re-grill session decides.
