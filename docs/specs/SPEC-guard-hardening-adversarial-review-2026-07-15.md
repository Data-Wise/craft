# SPEC: Guard-Hardening Follow-Ups (Post-#284 Adversarial Review)

**Date:** 2026-07-15 · **Status:** Approved (locked via `/craft:brainstorm` → `/craft:grill`, adversarially re-verified same session)
**Brainstorm:** [`BRAINSTORM-guard-hardening-adversarial-review-2026-07-15.md`](../../BRAINSTORM-guard-hardening-adversarial-review-2026-07-15.md)
**Grill:** [`GRILL-guard-hardening-adversarial-review-2026-07-15.md`](GRILL-guard-hardening-adversarial-review-2026-07-15.md)
**Predecessor:** PR #284 (`fix(guard): resolve Bash cross-context targets in branch-guard.sh`)

## Problem

Two items were flagged as deferred after PR #284, unverified. This session's brainstorm
adversarially re-checked both against the actual code:

1. **Disproven as originally framed, real bug found instead.** "`no-switch-guard.sh` has the
   same compound-`main`-substring / worktree-cleanup false-positive pattern as branch-guard.sh
   pre-#284" does not reproduce — neither scenario triggers anything in the file (verified by
   direct read). The **real, confirmed bug**: `no-switch-guard.sh`'s `git_dir` resolution only
   honors an explicit `-C <path>` flag, never a leading `cd <path> &&` — so `is_dirty()` checks
   the session's own repo, not the actual switch target, for commands like `cd <worktree> &&
   git switch <branch>`. Same root-cause class as #284, different manifestation.
2. **Confirmed empirically, not just structurally.** `~/.claude/guards.json`'s global
   `enabled`/`muted_until` state is mutated via an unsafe `jq ... > tmp && mv tmp file` pattern
   with no locking. A same-session test (two concurrent writers, 40 increments each, against a
   scratch copy) lost 40 of 80 writes — a real, easily-triggered lost-update race, not a
   theoretical worry. A second writer of the same file with the same unsafe pattern was found
   during a post-lock adversarial re-check: `scripts/install-guards.sh`'s seed/merge path.

## Scope

### In scope — two independent PRs (GRILL decision #3: unrelated files, unrelated risk profiles)

**PR A — cd-target resolution (no-switch-guard.sh + retrofit to branch-guard.sh)**

1. Add leading-`cd <path> &&`/`cd <path>;` parsing to `no-switch-guard.sh`'s `git_dir`
   resolution (currently `-C`-only), so `is_dirty()` and `switch_target()` check the actual
   command target, not session CWD.
2. **Cumulative-cwd tracking** (GRILL decision #2), applied to BOTH `no-switch-guard.sh`'s new
   resolver AND a retrofit of `scripts/branch-guard.sh`'s existing #284-era §8d0 resolver — which
   is confirmed (line 579, anchored `^cd`) to resolve only a single leading `cd`, not a
   multi-hop chain (`cd a && cd b && ...`). This is a genuine re-opening of already-merged #284
   code, not scope confined to the new file.
3. Test coverage: multi-hop `cd` chain cases in both `tests/test_branch_guard.sh`'s existing
   cross-context group and `tests/test_no_switch_guard.sh` (confirmed structurally compatible —
   `init_repo`/`make_tmpdir`/`json_bash`/`run_green` helpers with `cwd` override already exist;
   no new scaffolding needed).

**PR B — guards.json write-race fix**

1. A shared mkdir-based lock helper (atomic on both macOS and Linux, unlike `flock` — confirmed
   unavailable as a CLI on this machine's macOS) wrapping the guards.json read-modify-write,
   with a staleness timeout so a crashed caller can't wedge the lock permanently.
2. Used by **both** call sites: `skills/dev/git/SKILL.md` Operation 12's
   `enable`/`disable`/`profile` mutation, AND `scripts/install-guards.sh`'s seed/merge write path
   (the second-writer finding from the adversarial re-check — Operation 12's docs currently claim
   "sole sanctioned mutator," which is not accurate until this is fixed).
3. New `tests/test_guards_registry_concurrency.sh`: formalizes this session's ad hoc
   falsification test (2 concurrent writers, scratch-copy-only, never the real
   `~/.claude/guards.json`) as a permanent regression guard.
4. Doc correction: `skills/dev/git/SKILL.md` Operation 12's "descriptive, not test-enforced"
   sole-mutator line, updated once the shared lock makes the claim actually true.

### Out of scope

- The originally-suspected "compound `main` substring" / "worktree-cleanup blocked as a unit"
  bugs in `no-switch-guard.sh` — disproven by direct code read, not carried forward.
- A one-line correction to `docs/specs/GRILL-branch-guard-target-resolution-2026-07-14.md`'s
  stale "Scope for Implementation" table (still flagged from the BRAINSTORM's own Next Steps,
  not yet done) — a docs-only follow-up, not bundled into either PR's code scope.

### Left to implementation judgment

- Exact staleness-timeout value for the PR B lock (GRILL named "~5s" illustratively, not locked).

## Acceptance Criteria

- [ ] `cd <worktree> && git switch <branch>` in `no-switch-guard.sh` resolves dirtiness/target
      from the worktree, not session CWD — verified by a hook invocation test with mismatched
      session/target state.
- [ ] A multi-hop `cd a && cd b && git switch x` resolves to `b` as the target in both
      `no-switch-guard.sh` and `branch-guard.sh` — cumulative tracking, not single-hop.
- [ ] `branch-guard.sh`'s existing #284 single-hop cross-context tests stay green after the
      cumulative-tracking retrofit (no regression).
- [ ] Two concurrent `/craft:git:guard disable` calls (or the formalized concurrency test) against
      a scratch `guards.json` produce zero lost updates.
- [ ] Two concurrent writes — one via Operation 12, one via `install-guards.sh`'s seed/merge path
      — against the same scratch file also produce zero lost updates (proves the shared-helper
      requirement, not just Operation 12 alone).
- [ ] `tests/test_guards_registry_concurrency.sh` exists, passes, and never touches the real
      `~/.claude/guards.json`.
- [ ] `skills/dev/git/SKILL.md` Operation 12's sole-mutator claim is corrected to reflect the
      shared lock (both writers now actually coordinate, not just Operation 12 alone).
- [ ] CHANGELOG `[Unreleased]` entries added for both PRs (fix, not feat).

## Review Checklist

- [ ] No regression in any currently-correct block in either hook (existing test suites for both
      hooks stay green).
- [ ] PR A and PR B ship as two separate PRs (GRILL decision #3) — not bundled.
- [ ] PR B's lock doesn't introduce a hang: staleness timeout is exercised by a test that
      simulates a crashed lock-holder (stale lock dir present, timeout expired).
- [ ] PR descriptions call out the scope each widened during grill/adversarial-review (PR A:
      retrofitting already-merged #284 code; PR B: the second-writer finding), not buried.

## Key Files

- `~/.claude/hooks/no-switch-guard.sh` / `scripts/no-switch-guard.sh` — PR A primary
- `scripts/branch-guard.sh` (§8d0 resolver, ~line 552-600) — PR A retrofit
- `tests/test_branch_guard.sh`, `tests/test_no_switch_guard.sh` — PR A test surface
- `skills/dev/git/SKILL.md` (Operation 12) — PR B primary
- `scripts/install-guards.sh` (lines 159-182) — PR B second writer
- `tests/test_guards_registry_concurrency.sh` (new) — PR B test surface

## Test Plan

Per the BRAINSTORM's scaffold, extended by the GRILL's addendum: **e2e** (full hook invocation
for the cd-chain and cumulative-cwd scenarios in both PR A hooks), **dogfood** (existing suites
for both hooks stay green), **concurrency** (PR B's new dedicated test tier, scratch-copy-only,
exercising both writers). No cross-command data flow beyond these two hooks (N/A integration); no
external dependency change — mkdir/jq are already-available primitives (N/A dependency); not a
new command/skill/agent (N/A count-cascade).
