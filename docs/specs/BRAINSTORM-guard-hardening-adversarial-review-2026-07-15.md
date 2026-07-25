# BRAINSTORM: Guard-Hardening Follow-Ups — Adversarial Review

**Date:** 2026-07-15 · **Depth:** default · **Focus:** ops
**Branch:** dev · **Categories:** tech, risks, timeline

## Origin

After PR #284 (branch-guard.sh target-resolution fix), two items were flagged
as deferred/out-of-scope without verification:

1. "`no-switch-guard.sh` has the same whole-string-matching false-positive
   pattern as branch-guard.sh had pre-#284 (compound `"main"` substring,
   worktree-cleanup)."
2. "Guard-state concurrency safety under Workflow/orchestrate parallel
   dispatch — unverified whether a race actually exists."

Both were carried forward from `docs/specs/GRILL-branch-guard-target-resolution-2026-07-14.md`
as assumptions, not confirmed findings. This brainstorm's job — per its
"adversarial review" framing — was to verify each claim against the actual
code before locking any new scope, not to design fixes for bugs that were
never confirmed to exist.

## Context Scan

### Item 1: re-read `no-switch-guard.sh` line by line

- **Compound `"main"` substring claim — does not reproduce.** The file's
  only "main" check (§3b, line 113) runs on `target`, a value extracted by
  `switch_target()` (line 71-75), which only fires when `is_switch` was set
  by an explicit `switch` or `checkout` regex match (§3, line 98-104).
  `git pull origin main && git push origin dev` contains neither keyword —
  `is_switch` never sets, §3 never runs, nothing fires. This specific
  scenario, as described, is not a bug in this file.
- **Worktree-cleanup claim — not a bug, a deliberate policy.**
  `worktree remove|move` (line 93-95) is documented in the file's own header
  (line 18) as unconditional RED tier: "destructive worktree op ... always
  ask." It fires on the whole command regardless of compounding by design —
  that's the intended behavior for a destructive op, not an accidental
  compound-block. Separately, `scripts/branch-guard.sh` (the file that
  *does* handle `git branch -D`, lines 630-648) already has a squash-merge
  safety check (`is_squash_merged`, line 635-641) that auto-allows
  force-delete when all commits are already in the integration branch — so
  even the underlying "branch-delete not checked against merge state"
  worry, as applied to branch-guard.sh, is already handled. (Whether that
  check predates or postdates #284 wasn't determined — the point is it's
  present now.)
- **The bug that *is* real, found by direct inspection:**
  `git_dir` resolution (line 64) only recognizes an explicit `-C <path>`
  flag. Unlike branch-guard.sh's now-fixed resolver (added in #284, which
  handles both `-C` and a leading `cd <path> &&`), `no-switch-guard.sh` has
  no `cd`-parsing at all. Concretely: `cd ~/.git-worktrees/craft/feature-x
  && git switch feature-x` — `is_dirty()` (line 65-69) runs `git status
  --porcelain` against the **session's own repo** (no `-C`, no target
  resolution), not the worktree actually being switched into. A dirty
  session repo would incorrectly block a switch in an unrelated, clean
  worktree; conversely a clean session repo would silently pass through a
  switch into a genuinely dirty worktree target. Same root-cause class as
  the #284 bugs (CWD-based inference instead of per-command target
  resolution), different manifestation than what was assumed.

### Item 2: guards.json write path

- `.claude/allow-once` (branch-guard.sh line 286) and `.claude/allow-dev-edit`
  (`/craft:git:unprotect`, `commands/git/unprotect.md` line 87) are both
  written under `PROJECT_ROOT` — i.e., already per-repo/per-worktree scoped.
  Parallel Workflow agents in separate worktrees can't collide on these; a
  race here was never actually plausible.
- `~/.claude/guards.json` is the real shared-state surface: a single global
  file, `enabled`/`muted_until` fields mutated via `/craft:git:guard
  enable|disable|profile` (`skills/dev/git/SKILL.md`, Operation 12, line
  245-275). The skill explicitly documents the mutation pattern as
  `jq`-mutate ("never raw `cat >`") but **names no locking mechanism** —
  Operation 12 is called "the sole sanctioned mutator" only as a documented
  convention ("descriptive, not test-enforced"), not an enforced invariant.
- **Falsification test run this session** (scratch copy of `guards.json`,
  two background loops each running the documented
  `jq '...' file > tmp.$$ && mv tmp.$$ file` pattern 40 times against
  different fields of the same file, concurrently): **26/40 and 14/40
  writes landed respectively — 40 of 80 total increments were silently
  lost.** This confirms a genuine, easily-triggered lost-update race under
  the *exact* pattern the skill documents as the sanctioned mutation path.
  (The test also incidentally hit a second bug — both background loops
  resolved `$$` to the same PID since bash doesn't reassign `$$` inside a
  backgrounded function call, colliding their temp filenames too — a
  second, compounding hazard if `guard.md`'s implementation used the same
  `$$`-based temp-naming idiom.)

## Locked Decisions

| # | Question | Decision |
|---|---|---|
| 1 | Should item 1 keep its original framing ("main substring," worktree-cleanup)? | **No — rescope entirely.** Drop the disproven framing. New scope: give `no-switch-guard.sh`'s `git_dir` resolution the same leading-`cd` handling branch-guard.sh got in #284, so `is_dirty()` and `switch_target()` check the actual target repo, not session CWD. |
| 2 | Is the guards.json concurrency risk real enough to act on? | **Yes — confirmed empirically, not just structurally.** 50% loss rate at 40 concurrent writes on a synthetic scratch copy. Not a theoretical worry; a reproducible lost-update race in the exact code path the skill documents as sanctioned. |

## Options Considered

### Item 1: no-switch-guard.sh cd-target-resolution

- **Port branch-guard.sh's resolver verbatim** — most consistent, but that
  resolver also carries branch-guard-specific concerns (protection-tier
  recomputation, `INTEGRATION_BRANCH` detection) that don't apply here;
  no-switch-guard.sh only needs the target *directory* for `is_dirty()` and
  needs no protection-tier logic at all.
- **Minimal targeted fix (recommended direction, not yet locked as
  implementation)** — extend `git_dir` extraction (line 64) to also match a
  leading `cd <path> &&`/`cd <path>;` prefix, mirroring just the path-only
  subset of branch-guard.sh's §8d0 resolver. Smaller diff, no unrelated
  protection-tier code pulled in.

### Item 2: guards.json write safety

- **Add file locking (`flock`)** — closes the race directly; requires
  `flock` availability (present on Linux by default, not always on macOS —
  same portability class of gotcha as `stat -f` documented in
  `~/.claude/CLAUDE.md`'s macOS-shell-portability rule). Needs a
  macOS-compatible fallback (e.g. `mkdir`-based lock directory, which is
  atomic on both platforms) if `flock` isn't guaranteed.
- **Atomic compare-and-swap style write (retry loop)** — read, compute,
  write to temp, then verify the source file's mtime/hash hasn't changed
  since the read before the final `mv`; retry on conflict. More portable
  than `flock`, more code than a lock.
- **Do nothing, narrow the blast radius instead** — since parallel Workflow
  agents are recommended to each get their own worktree (`isolation:
  "worktree"`), and `guards.json` mutation only happens via an explicit user
  command (`/craft:git:guard`), the actual concurrent-caller scenario (two
  agents *simultaneously* running `/craft:git:guard` against the same
  global file) is rare in practice even though the race is real. Worth
  weighing against the cost of a locking fix for a low-frequency trigger.

## Risks / Edge Cases

- Item 1's minimal fix only handles `cd`/`-C`-prefixed compounds — a
  command with `cd` appearing mid-chain (`git status && cd <path> && git
  switch x`) needs the same "does the resolver need cumulative-cwd
  tracking" call that was left unresolved for branch-guard.sh in the #284
  GRILL. Same open question, now duplicated across two files — worth
  answering once and applying to both, not re-litigating per-file.
- Item 2: any lock/CAS fix must not block or hang the interactive
  `/craft:git:guard` command itself if a stale lock is left behind by a
  crashed process — needs a timeout/staleness check, not a bare `flock`
  wait.
- The disproof of item 1's original framing means the #284-era GRILL doc's
  "Scope for Implementation" table is now stale on this specific line —
  worth a one-line correction note there so a future session doesn't
  re-inherit the disproven claim.

## Next Steps

1. If proceeding to implementation: `/craft:grill` this doc first (per the
   project's own convention — brainstorm → grill → plan) since item 2 in
   particular has a real design choice (flock vs. CAS-retry vs.
   do-nothing-narrow-blast-radius) that deserves adversarial interrogation
   before locking, the same way #284's `rm -rf .git` question got grilled.
2. For item 1, decide the cumulative-cwd-tracking question once (not
   per-file) — this same open question was deferred, unresolved, in the
   #284 GRILL.
3. Add a one-line correction to `docs/specs/GRILL-branch-guard-target-resolution-2026-07-14.md`'s
   "Scope Summary" noting decision #5 (no-switch-guard "same pattern") was
   re-investigated and found to not reproduce as originally described.

## Test-Plan Scaffolding

| Tier | Scope |
|---|---|
| unit | N/A — no new parser being introduced in this brainstorm; scoping only |
| e2e | Once implemented: full hook invocation for `cd <worktree> && git switch <branch>` (item 1) and two concurrent `/craft:git:guard disable` calls against a scratch `guards.json` (item 2) — the exact test run informally this session, formalized |
| dogfood | Existing `tests/test_no_switch_guard*.sh` (if present) / `tests/test_branch_guard_dogfood.py`-equivalent for no-switch-guard stays green |
| integration | N/A — single-hook scope, no cross-command data flow |
| dependency | N/A — no new external dependency (flock/mkdir-lock are already-available shell primitives) |
| count-cascade | N/A — not a new command/skill/agent |

## Documentation Scaffolding

- `docs/reference/REFCARD-BRANCH-GUARD.md` — needs a no-switch-guard
  cd-resolution note once item 1 ships (mirrors the #284-era update to this
  same file).
- `docs/guide/guard-suite.md` (referenced from `commands/git/guard.md`) —
  needs a locking/atomicity note on `guards.json` once item 2's fix lands,
  since Operation 12's "sole sanctioned mutator" line currently overstates
  the actual safety guarantee.
