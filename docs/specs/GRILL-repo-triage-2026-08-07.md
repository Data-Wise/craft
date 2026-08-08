# GRILL: Repo Triage

**Date:** 2026-08-07 · **Target:** [`BRAINSTORM-repo-triage-2026-08-07.md`](BRAINSTORM-repo-triage-2026-08-07.md)

## Codebase-First Sweep (what reshaped the interrogation)

Before asking anything, re-checked the BRAINSTORM's own claims against the codebase:

- **Decision #2 in the BRAINSTORM ("New logic, since nothing exists") was wrong.**
  `skills/dev/git/SKILL.md` Operation 4 (Branch Cleanup) already does squash-merge-safe
  branch grounding via `is_squash_merged` (`lib/git-utils.sh`), with a documented
  `--dry-run`. Operation 5 has a `worktree clean` sub-action ("Remove stale/merged
  worktrees safely"). This single finding reshaped every branch below — the grill
  pivoted from "design new grounding logic" to "design the thin orchestration layer
  over existing logic."

## Decision Ledger

| # | Branch | Decision |
|---|---|---|
| 1 | Skill shape | **Thin orchestrator.** repo-triage calls `dev/git` Op 4 (branch cleanup) + Op 5 (worktree clean) + `/craft:git:issue-check`, and adds only the missing piece: cross-cutting evidence citation + prioritize/group-into-buckets. No duplicated grounding logic anywhere. Supersedes BRAINSTORM Decision #2. |
| 2 | Issue-check cost at scale | **Cheap pre-filter before the expensive per-issue check** — not age-based (rejected: this session's own #327/#316 were both *recently* touched and still stale/superseded, so "recently updated = still valid" is backwards for the actual failure mode observed). Instead: bounded concurrency/count cap (e.g. 15 by default, `--all` to lift it), checking in whatever order `gh issue list` returns. |
| 3 | Worktree-lock-before-branch-delete | **Sequence, not new detection code.** repo-triage always calls Op 5 (worktree clean) before Op 4 (branch cleanup) within its own run, so no branch is ever locked by a worktree when deletion is attempted. This fixes it only inside repo-triage's own run — `/craft:git:clean` run standalone still has the gap (out of scope for this ledger, noted below). |
| 4 | Confirm layering | **One unified batch confirm.** repo-triage runs Op 4/5 in dry-run/non-interactive collection mode, merges their proposed deletions with issue-check's results into one itemized list (evidence per item), single yes/no with per-item opt-out, then executes approved items directly — bypassing Op 4/5's own interactive confirms rather than stacking prompts. |
| 5 | Op 5 dry-run gap | **Verified real, not assumed:** Op 4 documents `--dry-run` explicitly (line 101); Op 5's `worktree clean` sub-action has no documented dry-run/non-interactive mode — just a one-line table entry. Decision: add `--dry-run` to Op 5 as a **small prerequisite fix to `dev/git`**, shipped/landed before repo-triage's build starts, rather than repo-triage reimplementing worktree grounding itself. |
| 6 | Pre-filter heuristic | **No age filter — cap concurrency/count instead**, per branch 2's reasoning. Never silently skip a checkable issue based on an age guess. |
| 7 | Content-diff scope (squash-merge safety) | **Scope the diff to files the branch's own commits touched** (`git log --name-only` on the branch, then diff only those paths against the target) — matches what this session did manually for `codex/issue-316-spec`. **Residual limitation, not fully closed:** does not solve the case where `dev`'s later commits modified the *same* files the branch touched — that case still needs human judgment (flag as `needs-recheck`, not `safe`, when the scoped diff is non-empty). |
| 8 | Grill/plan/defer bucket rule | **Reuse grill's own self-definition, don't invent a second taxonomy.** grill-ready = item has a genuinely unresolved load-bearing design branch (per grill's own Step 3 angle set); plan-ready = scope is a single clear next-action, no open design question; defer = neither, and no near-term owner/deadline. |

## Open Questions (flagged, not resolved here)

- **`/craft:git:clean` standalone still has the worktree-lock gap.** Branch 3's fix is
  scoped to repo-triage's own call sequence; a user running `/craft:git:clean` directly
  (not through repo-triage) can still hit the same silent-skip failure this session
  observed. Worth a follow-up issue against `dev/git` itself, separate from repo-triage's
  build.
- **Branch 7's residual limitation** (same-file-later-modified case) means the
  "safe-to-delete" evidence for squash-merged branches is strong-but-not-airtight even
  after the fix — acceptable per the decision, but should be stated plainly in
  repo-triage's own output ("scoped diff clean" ≠ "provably zero content risk").
- **Contract stability between repo-triage and its 3 dependencies** (Op 4, Op 5,
  issue-check): Decision 1's own stated consequence was "needs a contract test." Not
  designed here — belongs in the implementation plan, not the ledger.

## Amendment (post-adversarial-review, 2026-08-07)

Triggered by [`REVIEW-repo-triage-2026-08-07.md`](REVIEW-repo-triage-2026-08-07.md) — 4
parallel lenses (backend, frontend/interaction, architecture, ADHD-friendly) found that
**Decisions 1 and 2 above rested on factually wrong claims** about the codebase, not just
under-specification. Re-opened those branches plus the confirm-UX/merge-schema gap the
review flagged as unimplementable-as-specified. Original decisions above are left
unedited per grill convention (append, never rewrite) — treat 9–14 below as superseding
1 and 2 where they conflict.

| # | Branch | Decision |
|---|---|---|
| 9 | Issue-check invocation mode | **Correction of fact:** `classify_issue()` (`commands/git/issue-check.md`) is plain regex/stdlib Python, not an LLM call — Decision 2's "expensive per-issue check" framing was wrong. **Decision:** direct-import `classify_issue()` (same as `tests/test_issue_check_unit.py` already does) rather than shelling out to `/craft:git:issue-check` per issue. Trade-off accepted: a Python-level dependency on issue-check's internals, not just its CLI contract — if the function signature changes, repo-triage breaks at import time. |
| 10 | Pre-filter fate | **Supersedes Decision 2's concurrency cap.** Direct import (branch 9) means checking is sub-millisecond CPU work — the cost the cap was hedging against doesn't exist. Drop the pre-filter entirely: check every open issue, every run, no cap, no `--limit` flag. Revisit only if `classify_issue()` itself later grows expensive (e.g. gains an LLM layer). |
| 11 | Skill placement, re-argued | **Correction of fact:** `skills/dev/git/SKILL.md` Operation 13 ("Issue Premise Check," lines 300–322) already wraps `issue-check` as a skill operation — neither the BRAINSTORM's nor this GRILL's original codebase sweep found it. This disproves the original "scope mismatch" argument for rejecting "extend `dev/git`" (Op 13 proves `dev/git` already mixes git-mechanics with issue-triage judgment). **Decision: Decision 1's OUTCOME still holds** (new skill, thin orchestrator) — but re-argued purely on file size (`dev/git`'s SKILL.md is already large; this session's own read tooling flags it) and separation of concern (git-mechanics primitives vs. cross-cutting judgment+UX), not the disproven scope-mismatch claim. Ledger correction, not a reversal. |
| 12 | Confirm UX | **Resolves the frontend-lens blocker.** `AskUserQuestion` caps at 4 options; the original "single yes/no with per-item opt-out across a merged list" can't execute as designed once real runs exceed 4 candidates (guaranteed once the pre-filter is dropped, branch 10). Adopt craft's existing precedent from `skills/code/SKILL.md` (~line 113): group candidates by source (issues / branches / worktrees) first, show the top 4 highest-confidence items per `AskUserQuestion` call, chain additional calls for the rest. Requires defining a confidence/evidence-strength sort key — new but small design point. |
| 13 | Merge schema — worktree/branch coupling | **Resolves the backend-lens blocker.** When Op 4 flags a branch and Op 5 flags its live worktree, merge into ONE candidate item ("delete branch X + its worktree at path Y") with a single opt-out — not two independent items. Prevents the split-decision state (branch deleted, worktree orphaned, or vice versa). Requires the merge join key to be branch name; this is the concrete shape the Op 5 `--dry-run` contract (Decision 5 / Open Question 3) needs to produce. |
| 14 | Partial mid-loop failure | **Resolves the remaining backend-lens blocker.** Skip-and-continue on an individual collection error (a flaky `gh issue view`, an Op4/Op5 collection-step error) — never abort the whole run on one failure. The final batch-confirm output must visibly flag what was skipped and why ("N items skipped due to error: ...") — never silently present a partial list as complete. |

## Handoff

Ready for `/craft:plan` — target: `docs/specs/GRILL-repo-triage-2026-08-07.md`
(this file, including the Amendment above) plus `docs/specs/BRAINSTORM-repo-triage-2026-08-07.md`
for the original scope/context and `docs/specs/REVIEW-repo-triage-2026-08-07.md` for the
full adversarial-review findings (including Medium/Low items not re-grilled: evidence-template
consistency, bucket-size caps, single-next-action output, progress/duration surfacing,
idempotency test coverage — left for the implementation plan to fold in as it sees fit).

Sequencing note for the plan: Decision 13's merge-schema shape should be finalized alongside
Decision 5's `dev/git` Op 5 `--dry-run` prerequisite (branch 9's direct-import approach doesn't
remove Op4/Op5's own missing-structured-output gap) — both need to land before repo-triage's
orchestration logic is built against them.
