# SPEC: Branch Guard Target-Resolution Fix

**Date:** 2026-07-14 · **Status:** Approved (locked via `/craft:brainstorm` → `/craft:grill`)
**Brainstorm:** [`BRAINSTORM-branch-guard-target-resolution-2026-07-14.md`](BRAINSTORM-branch-guard-target-resolution-2026-07-14.md)
**Grill:** [`GRILL-branch-guard-target-resolution-2026-07-14.md`](GRILL-branch-guard-target-resolution-2026-07-14.md)
**Rule reference:** [`REPORT-branch-guard-2026-07-14.md`](REPORT-branch-guard-2026-07-14.md)

## Problem

`~/.claude/hooks/branch-guard.sh` infers a Bash command's target branch/repo
from session CWD plus whole-string substring matching, not from what each
git subcommand in the command actually targets. This causes four documented
false positives (worktree push, cross-repo `main`, compound `"main"`
substring match, worktree-cleanup compound block — see BRAINSTORM §Origin)
and one policy gap surfaced during grill (catastrophic `rm -rf .git` cannot
be confirmed even on same-repo dev/draft, because it's also enforced by the
classifier-level `hard_deny` layer, which has no git execution context and
so cannot be scoped to "same repo only" — see GRILL decision 3).

## Scope

### In scope

1. **Per-clause target resolution.** Split compound Bash commands on
   `&&`/`;`/`||`. For each git-touching clause, resolve its actual target
   from its own args (`-C <path>`, a leading `cd <path> &&`, remote+refspec
   in `push`/`pull`) instead of session CWD or whole-string matching.
   Classify each clause independently against the existing LOW/MEDIUM/HIGH
   tiers.
2. **Cross-repo `main` → confirm, not block.** When a resolved clause
   targets a different repo than the session's, and that target's branch
   would trigger MEDIUM/HIGH, surface `[CONFIRM]` — never a hard block.
3. **Remove `delete-git-dir` from the hard_deny catalog.** Drop it from
   `scripts/hard-deny-rules.json`'s installed rule set and the
   `/craft:git:protect` install list. `branch-guard.sh`'s own HIGH tier
   becomes the sole gate for `rm -rf .git`: `[CONFIRM]` on dev/draft, hard
   block only on `main`.

### Out of scope (explicitly deferred)

- Concurrency-safety for guard state (`.claude/allow-once`, `guards.json`)
  under Workflow/orchestrate parallel dispatch — separate follow-on
  brainstorm/grill (GRILL decision 5).

### Open, left to implementation judgment (GRILL decision 6, open questions)

- Whether the resolver needs cumulative cwd-tracking (a bare `cd <path> &&`
  clause updates the effective target for every clause after it) to fully
  resolve problem #1, versus a documented fallback to `[CONFIRM]` for that
  specific shape. **Pick one and document the choice in the ORCHESTRATE
  phase notes** — do not silently default.
- Size of the rollout blast radius from removing `delete-git-dir` from
  hard_deny across other craft installs — at minimum, call this out
  prominently in the PR description per the GRILL's own recommendation.

## Acceptance Criteria

- [ ] `git -C <other-repo-path> push` (or a leading `cd <other-repo> &&`
      prefix) resolves the target branch from the OTHER repo, not session
      CWD — verified by a hook invocation test with mismatched session/target
      branches.
- [ ] A compound command containing the literal substring `"main"` inside a
      clause targeting a non-protected branch (e.g.
      `git pull origin main && git push origin dev` while on `dev`) is not
      classified using the `main` clause's protection level.
- [ ] `git worktree remove <path> && git branch -D <branch>` classifies the
      two clauses independently; the branch-delete clause is evaluated
      against actual merge state, not blocked purely for being compound.
- [ ] A cross-repo command targeting `main` in another repo triggers
      `[CONFIRM]`, never a hard exit-2 block.
- [ ] `scripts/hard-deny-rules.json` no longer lists `delete-git-dir` as an
      installed `hard_deny` rule; `rm -rf .git` on `dev`/`draft` in the
      current repo triggers branch-guard.sh's `[CONFIRM]` flow; on `main`
      it remains a hard block.
- [ ] All 5 existing branch-guard test files
      (`test_branch_guard.sh`, `test_branch_guard_e2e.sh`,
      `test_branch_guard_interactive.sh`, `test_branch_guard_dogfood.py`,
      `test_integration_branch_guard.py`) pass, with new/updated cases
      covering the 4 originating false positives + the hard_deny removal.
- [ ] `docs/adr/ADR-001-workflow-branch-guard.md` and
      `docs/reference/REFCARD-BRANCH-GUARD.md` updated to reflect per-clause
      resolution and the hard_deny catalog change.
- [ ] CHANGELOG `[Unreleased]` entry added (fix, not feat).

## Review Checklist

- [ ] No regression in any currently-correct block (the 5-file test suite's
      pre-existing passing cases stay green).
- [ ] Per-clause resolution stays within the existing ~25ms/hook-invocation
      performance budget for typical (2–4 clause) compound commands.
- [ ] `[CONFIRM]` messages for the cross-repo case name the resolved
      repo/branch explicitly (not just "main") so the prompt is
      distinguishable from the ordinary same-repo dev confirm flow.
- [ ] The hard_deny removal is called out prominently in the PR
      description (not buried) given its cross-repo blast radius.

## Key Files

- `~/.claude/hooks/branch-guard.sh` (955 lines) — core parser/classifier change
- `scripts/hard-deny-rules.json` — remove `delete-git-dir` entry
- `scripts/install-hard-deny.sh` — verify install/uninstall paths still consistent
- `docs/adr/ADR-001-workflow-branch-guard.md`, `docs/reference/REFCARD-BRANCH-GUARD.md` — doc updates
- `tests/test_branch_guard.sh`, `tests/test_branch_guard_e2e.sh`, `tests/test_branch_guard_interactive.sh`, `tests/test_branch_guard_dogfood.py`, `tests/test_integration_branch_guard.py` — test surface

## Test Plan

Per the brainstorm's scaffold: **unit** (clause-splitter + resolver
functions — single command, 2/3-clause compound, `-C` override, leading
`cd`, remote+refspec parse), **e2e** (full hook invocation for each of the
4 originating scenarios + the hard_deny-removal scenario), **dogfood**
(existing suite stays green — this is a classification-internals refactor,
not new protection scope). No cross-command data flow beyond this hook
(N/A integration); no external dependency change (N/A dependency); not a
new command/skill/agent (N/A count-cascade).
