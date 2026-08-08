---
name: repo-triage
description: This skill should be used when the user asks to "triage the repo", "clean up open issues and stale branches", "what needs attention in this repo", or wants a batch pass over open GitHub issues plus stale worktrees/branches, grounded against current repo state, with confirmed (never automatic) deletion/closure and the remainder sorted into grill-ready/plan-ready/defer buckets.
category: orchestration
---

# Repo Triage Skill

Batch-grounds open GitHub issues and stale worktrees/branches against current
repo state, offers confirmed deletion/closure of what's superseded, and
groups everything else into grill-ready / plan-ready / defer buckets. A thin
orchestrator over three existing pieces — it contributes no parallel
classification or merge-detection logic of its own beyond the join/bucket
step (Phase 3/4).

## Boundary with Adjacent Skills

| Skill / Operation | Owns | repo-triage's relationship |
|---|---|---|
| `commands/git/issue-check.md` (`classify_issue()`) | Single-issue premise verdict (valid/moot/unclear) | Runtime-extracted and reused verbatim via `utils/repo_triage_classify.py` — never reimplemented. See "Source identity" below. |
| `dev/git` Operation 4 (Branch Cleanup) | Detecting locally-merged/squash-merged branches | Called via `branch_cleanup_dry_run()` (`lib/git-utils.sh`) — collection only, no deletion. |
| `dev/git` Operation 5 (Worktree Management, `clean`) | Detecting stale/merged worktrees | Called via `worktree_clean_dry_run()` (`lib/git-utils.sh`) — collection only, no removal. |
| `skills/workflow/grill/SKILL.md` | Interrogating a genuinely unresolved, load-bearing design question | repo-triage's `grill-ready` bucket reuses grill's own self-definition ("load-bearing branch") as the membership test — never a separate taxonomy. |

This skill never deletes a branch, removes a worktree, or closes an issue on
its own initiative — every mutation requires an explicit confirm captured in
the same run (see Confirm UX below).

## Procedure

### Step 1 — Issue triage (no pre-filter, no concurrency cap)

```bash
python3 utils/repo_triage_classify.py Data-Wise/craft
```

This loops over every open issue from `gh issue list`, classifying each with
the SAME `classify_issue()` that `commands/git/issue-check.md` and
`tests/test_issue_check_unit.py` use — extracted at runtime from that file's
fenced ```python block, never copied. `tests/test_repo_triage_classify_unit.py`
asserts source identity between the two loaders as a standing regression
guard: if repo-triage ever grows a parallel classifier, that test fails.

A `gh issue view`/classification failure on one issue is skipped and
recorded in the `errors` array of the JSON output — it never aborts the
whole run. Surface these in the final report (Step 4).

### Step 2 — Worktree/branch triage (sequenced)

Call Operation 5 **before** Operation 4 — this ordering closes the exact
silent-skip gap where `gh pr merge --delete-branch` fails on a
worktree-locked branch with no clear error:

```bash
source lib/git-utils.sh
worktree_clean_dry_run dev > /tmp/repo-triage-worktrees.jsonl   # FIRST
branch_cleanup_dry_run dev > /tmp/repo-triage-branches.jsonl    # SECOND
```

Both are collection-only (no `git worktree remove`, no `git branch -D`).
Apply the same skip-and-continue discipline as Step 1 to any per-item
collection error (e.g. a branch whose `gh pr list` lookup fails — that
candidate still gets `pr_state: "unknown"`, it is not dropped).

### Step 3 — Merge + confirm UX

```bash
source lib/repo-triage-utils.sh
merge_candidates /tmp/repo-triage-branches.jsonl /tmp/repo-triage-worktrees.jsonl
```

Joins Step 2's two streams on `branch` (the required join key both
`lib/git-utils.sh` functions emit) so a branch that is also checked out in a
worktree renders as **one** candidate — never two independent opt-outs.
Unmatched branches (`type: "branch"`) and unmatched worktrees
(`type: "worktree"`) pass through unchanged. `merge_candidates()` itself does
**not** filter by evidence strength — it is a pure join, and its own test
suite asserts a `not-merged`/`unknown`-evidence branch passes through
unchanged (so a caller can still surface it, e.g. in Step 4's defer bucket).

**Before building the deletion candidate list**, restate `dev/git` Operation
4's own rule here: never offer a branch/worktree item for deletion whose
`merge_evidence` is `not-merged` or `unknown` — exclude those from the
Step 3 confirm entirely (route them to Step 4's bucketing instead, same as
an unresolved issue). Only `merge_evidence: "merged"` or `"squash-merged"`
items are eligible for the batch-confirm below.

**Confirm UX** — group the *eligible* merged candidates by source (issues / branches /
worktrees), sort each group by evidence strength (a squash-merge with both
`ancestor_result: "ancestor"` AND `scoped_diff_result: "clean"` ranks above
one with only `ancestor_result`), and present via `AskUserQuestion`:

- Max 4 options per call (harness limit — same pattern as
  `skills/code/SKILL.md` Step 4). If more than 4 candidates exist, present
  the top 4 highest-confidence items and chain additional `AskUserQuestion`
  calls for the remainder — never truncate silently.
- Each option's description cites the evidence: issue items show
  `classify_issue()`'s `reasoning` string; branch/worktree items show the
  structured fields from Step 2 (`merge_evidence`, `ancestor_result`,
  `pr_state`, `scoped_diff_result`) under a one-line-summary-plus-detail
  template.
- On confirm, execute the approved deletion/closure directly — Operation
  4/5's own interactive confirms are bypassed (already collected via
  `--dry-run` mode in Step 2), so there is exactly one confirm gate per
  item, not two.
- Visibly flag any items skipped due to a Step 1/2 collection error in the
  confirm output — e.g. "2 issues skipped due to error: #114 (gh timeout),
  #201 (malformed body)" — never present a partial list as if it were
  complete.

### Step 4 — Bucket the remainder

Everything not actioned in Step 3 (i.e. `moot`-classified issues that were
closed, and `merged`/`squash-merged` branches+worktrees that were deleted,
drop out of scope here) gets bucketed:

```bash
source lib/repo-triage-utils.sh
python3 utils/repo_triage_classify.py Data-Wise/craft | jq -c '.results[]' | bucket_candidates
```

Bucket membership (`lib/repo-triage-utils.sh`'s `bucket_candidates()`,
reusing `classify_issue()`'s existing three-way status rather than inventing
a second taxonomy):

| Bucket | Membership test |
|---|---|
| `grill-ready` | `status == "unclear"` — cannot mechanically verify == a genuinely unresolved, load-bearing question (grill's own self-definition, `skills/workflow/grill/SKILL.md`). |
| `plan-ready` | `status == "valid"` — premise holds, single clear next action (implement the fix). |
| `defer` | Fallback — no near-term owner/deadline, neither of the above. |

**Output additions** (not a second display mechanism — reuses the
top-4-plus-remainder pattern from Step 3):

- Cap each bucket's displayed items at 4, same chaining rule as the confirm
  UX.
- Print exactly ONE explicit "start here" next action at the end of the
  run: the highest-priority `grill-ready` item, or the top `plan-ready`
  item if `grill-ready` is empty.

## Non-Goals

- Never calls `git branch -D`, `git worktree remove`/`prune`, or
  `gh issue close` without a preceding explicit confirm captured in the
  same run (verified by `tests/test_repo_triage_utils.sh`'s and
  `tests/test_git_dryrun.sh`'s "never mutates" checks on the underlying
  helper functions).
- Never re-implements `classify_issue()`, `is_squash_merged()`, or the
  Operation 4/5 detection logic — it only calls them and merges/buckets
  their output.
- Not a scheduler or a cron job — one explicit invocation per run, no
  background polling.

## Idempotency

Re-running this skill twice in a row against the same repo state must
produce an empty or shrinking candidate set — items already actioned
(deleted/closed) in a prior run must never be re-proposed, since Step 1/2
always re-derive candidates from live `gh`/`git` state rather than a cached
list.

## Related Files

- `utils/repo_triage_classify.py` — issue-triage runner (Step 1).
- `lib/git-utils.sh` — `worktree_clean_dry_run()`, `branch_cleanup_dry_run()` (Step 2).
- `lib/repo-triage-utils.sh` — `merge_candidates()`, `bucket_candidates()` (Steps 3–4).
- `tests/test_repo_triage_classify_unit.py`, `tests/test_git_dryrun.sh`,
  `tests/test_repo_triage_utils.sh` — unit coverage per phase.
