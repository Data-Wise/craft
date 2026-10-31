# GRILL: Branch Triage Verdicts

**Date:** 2026-10-31 · **Target:** GitHub issue #374 (Data-Wise/craft)

## Codebase-First Sweep

- `scoped_diff_result` is not scoped: it runs a full `git diff base..branch` (`lib/git-utils.sh:138`), identical to `is_squash_merged`'s fallback, so it adds no evidence. Increment 0's question is answered: no per-commit content-presence check exists.
- `pr_state` (`lib/git-utils.sh:133`) discards `gh` errors, so lookup failure and "no PR" both yield `unknown`; it matches by branch name only, with no head-SHA check.
- The empty-operand bug is not in the repo: `is_squash_merged` already returns UNKNOWN for bad refs (`lib/git-utils.sh:34`). It was in the issue author's own script.
- No verdict layer exists. Collectors emit evidence only; `merge_candidates` (`lib/repo-triage-utils.sh`) is a pure jq join; `repo_triage_classify.py` handles issues only.


## Decision Ledger

| # | Branch | Decision |
|---|---|---|
| 1 | Where verdict derivation lives | Pure jq verdict function in lib/repo-triage-utils.sh over evidence-only collectors (branch_cleanup_dry_run gains evidence fields, never a verdict). Rules unit-test on hand-written JSONL; a missing or empty evidence field maps to UNKNOWN. Rejected: verdict inside the bash collector (needs a git fixture per verdict) and a Python module (second language for a jq-sized transform). |
| 2 | DELETE-SAFE evidence | Requires a merged PR whose headRefOid equals the branch tip AND whose mergeCommit is an ancestor of the triage base (git merge-base --is-ancestor). Missing/unfetched merge commit, empty operand, or failed gh lookup => UNKNOWN, never a delete command. Tip-is-ancestor-of-base remains an alternate DELETE-SAFE path. Rejected: head==tip alone (stacked PRs merged into an unmerged feature branch would read safe) and baseRefName check alone (misses reverts/rewrites). |
| 3 | LAND-CANDIDATE scope | Defer Increment 3 (content_absent, conflict_files, behind_base, LAND-CANDIDATE) to a follow-up: it is the only heuristic verdict (content comparison is a lower bound; benefit is asserted, not measured). v1 = Increments 1, 2, 4: pr_head_match + mergeCommit check, upstream/worktree/owner_hint, verdicts DELETE-SAFE/BACKUP-THEN-DECIDE/KEEP/UNKNOWN, per-verdict command blocks. Unmerged-with-upstream branches stay plain not-merged evidence meanwhile. Rejected: shipping all verdicts at once; patch-id-only variant (misses rebased/edited landed commits). |
| 4 | owner_hint source and role | Configurable branch-prefix list (default codex/, dependabot/); advisory evidence field. KEEP-for-tool-owned applies only when DELETE-SAFE evidence is absent, so a fully verified merged codex/* branch (e.g. codex/release-4-8-1, PR #373) stays cleanable. Rejected: last-commit author (all sessions commit as Stat-Wise, so it cannot distinguish tools) and always-KEEP prefixes (merged tool branches would never be offered). Known gap: an unlisted tool prefix is unprotected. |
| 5 | v1 done-gate | Two parts, both required: (1) the issue's 6 red-first cases in the shell/jq tests (multi-commit squash, unmerged+unpushed, live worktree, failed gh lookup, empty operand, planted one-commit-off control); (2) a read-only live run on this repo's real branches against hand-written verdicts recorded beforehand, transcript quoted in the PR body (e2e-before-pr). New JSONL fields are additive, so merge_candidates and tests/test_git_dryrun.sh keep working. Rejected: fixtures only (passes can still misjudge real branches) and live only (no regression protection). |

## Open Questions

- Default `owner_hint` prefix list beyond `codex/` and `dependabot/`: unlisted tool prefixes stay unprotected (Decision 4).
- `pr_state` today cannot distinguish a failed `gh` call from no PR; Decision 2 requires the new lookup to surface failure as `UNKNOWN`. Whether to change the existing `pr_state` field or add a new one is an implementation choice (additive is the safe default).
- LAND-CANDIDATE (Decision 3) needs its own grill before the follow-up: lower-bound content comparison and an unmeasured benefit.
- Issue #374 body says its code claims were unverified; the sweep above corrects them (no empty-operand bug in the repo; `scoped_diff_result` is not scoped). Worth a comment on the issue.

## Test Plan

Red first, in the existing shell suites (`tests/test_git_dryrun.sh`, `tests/test_repo_triage_utils.sh`): the 6 cases in Decision 5. jq verdict function tested on hand-written JSONL (missing/empty field gives UNKNOWN). Live read-only run on this repo with pre-recorded hand verdicts.

## Documentation

`skills/orchestration/repo-triage/SKILL.md` (verdict table, command blocks per verdict), `skills/dev/git/SKILL.md` Operation 4, CHANGELOG, `docs/CHANGELOG.md` mirror. Update the JSONL contract comment in `lib/git-utils.sh`.
