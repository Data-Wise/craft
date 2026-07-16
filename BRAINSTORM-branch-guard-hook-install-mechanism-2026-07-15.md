# BRAINSTORM: Branch Guard Hook Install Mechanism (Symlink → Copy)

**Date:** 2026-07-15 · **Depth:** default · **Focus:** ops
**Branch:** dev · **Categories:** tech, risks, timeline

## Origin

`~/.claude/hooks/branch-guard.sh` was a personal-machine symlink to
`craft/scripts/branch-guard.sh` on the `dev` checkout. This surfaced as a
real point of confusion during the branch-guard-target-resolution session
(2026-07-14): a worktree copy of the hook was edited and tested extensively,
but the *installed* (symlinked) hook still pointed at the stale `dev`
checkout until the feature branch merged — caught only by
`test_repo_copy_matches_installed`, not by any earlier signal.

## Context Scan

- `scripts/install-branch-guard.sh` — the actual installer — does **not**
  create symlinks by default. It copies `scripts/branch-guard.sh` to
  `~/.claude/hooks/branch-guard.sh` and explicitly special-cases an
  *existing* symlink: `if [[ -L "$HOOK_DEST" ]]; then ok "already
  symlinked... leave it"`. It never converts a symlink to a copy on its
  own. The symlink was a personal dev-environment choice, not craft's
  general install architecture — every other install on this machine (and
  every other user's) already uses a real copy.
- `tests/test_branch_guard_dogfood.py::test_repo_copy_matches_installed`
  already exists and already catches drift by content comparison — it is
  symlink-agnostic (reads both files, `assertEqual`s their contents). This
  safety net does not need to change for this switch.
- No other script or test depends on `~/.claude/hooks/branch-guard.sh`
  being a symlink specifically (checked via grep for `readlink`/`-L` +
  `branch-guard` across `.sh`/`.py`/`.md` — only hit was the installer's
  own leave-it-alone branch).

## Locked Decisions

| # | Question | Decision |
|---|---|---|
| 1 | Root cause of the actual complaint | **Not the symlink mechanism itself** (a symlink IS always current by construction) — the real issue was a *worktree* copy diverging from what the symlink pointed at (`dev`). Reframed from "symlinks are bad" to "which copy is live and current." |
| 2 | Replacement mechanism | **Copy-mode via the existing installer, re-run manually after edits** — matches how every non-dev install already works (`install-branch-guard.sh`'s default path). Rejected: a git post-checkout/post-merge auto-copy hook (adds infra for a problem the existing dogfood test already catches) and a dedicated `bin/sync-hook` + pre-push gate (more infrastructure than the actual risk warrants). |
| 3 | Migration on this machine | **Remove the symlink now, run `install-branch-guard.sh`'s copy path to install a real file** — one-time ~2 min action, done this session. |

## Options Considered (not selected)

- **Auto-copy git hook** (post-checkout/post-merge on `dev`) — would keep
  the installed hook synced to `dev`'s last commit automatically, no
  manual step. Rejected: adds a new git-hook dependency for a drift class
  that's rare (only matters while actively editing the hook itself) and
  already caught by the dogfood test before it reaches a PR.
- **Dedicated dev-sync script + strengthened pre-push gate** — most
  structurally sound (closes the drift-detection gap entirely, not just
  relies on remembering), but is more infrastructure than a personal
  dev-workflow annoyance warrants. Revisit if this recurs.

## Risks / Edge Cases

- Manual copy-mode means drift is possible again during active hook
  development — mitigated by the existing `test_repo_copy_matches_installed`
  dogfood test, which already fires in CI and locally with an explicit
  remedy message ("Run install-branch-guard.sh to sync").
- The installer's `-L` check means it will silently no-op if a symlink is
  ever re-created by habit — worth remembering this is now an anti-pattern
  for this repo's hook, not a supported fast path.

## Next Command

Executed inline this session (see below) — no further command needed
unless the "auto-copy git hook" or "dedicated sync script" options are
revisited later.
