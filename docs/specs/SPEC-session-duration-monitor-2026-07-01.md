# Session Duration / Parallelism Monitor — Consolidated into Issue #169

**Status:** SUPERSEDED — folded into [issue #169](https://github.com/Data-Wise/craft/issues/169) (generic read-only repo/worktree milestone monitor) as a specific milestone type, not a standalone spec. See the addendum comment posted to #169 for the merged scope. This file is kept only as a pointer; do not implement from here directly.

## Why this got merged instead of standing alone

This spec originally proposed a SessionStart hook to surface two 2026-06-24 usage-report findings live (68% of usage from 8+ hour sessions, 15% from 4+ parallel sessions), instead of only in the weekly retrospective. On auditing open issues (2026-07-01), issue #169 turned out to already be asking the identical research question at a more general scope: a generic "watch a repo/worktree/branch, ping at milestones, read-only, cost-analyzed first" monitor, explicitly asking Claude Code's own primitives to be checked first (`ScheduleWakeup`, `/loop`, cron, cache-TTL cost tradeoffs, wake-cadence guards) before anything gets built.

Writing this as a second, parallel spec would have duplicated that research rather than extending it. "Watch this session's own elapsed time / concurrent-session count" is one specific milestone type (`idle-for-N` / a new `duration-threshold` type, and a `parallel-count-threshold` type) within #169's general "watch X, ping at milestone Y" shape — not a different mechanism.

## What carries over into #169 (see posted comment for full text)

- The two concrete milestone types this use case needs: session-duration-threshold (8h+) and concurrent-session-count-threshold (4+), as additions to #169's milestone-type list (which already includes new-commit, sdd-ledger task-complete, idle-for-N, file-appears, branch-merged).
- The existing `governance/session_hook.py` as a proven reference implementation for the "quiet, cheap, cache-aware SessionStart hook" pattern #169 will need regardless of which milestone types it ends up supporting.
- The same open platform question #169 already asks (Step 1 in this file's original draft): does SessionStart actually re-fire mid-session, or is a different mechanism (`ScheduleWakeup`, periodic `PreToolUse` check) needed for a duration check to mean anything beyond "elapsed time at session open, always ~0"? This is now one research question, asked once, in #169 — not asked separately here and there.
- The concurrent-session detection question (is there any shared state a hook can enumerate to count active sessions) similarly folds into #169's own Ask #1 (map needs onto native primitives, report the gap).

## Full original task breakdown

Preserved for reference / in case #169's eventual scope narrows and this needs to be re-split out — see git history of this file for the original 4-task plan (confirm platform mechanics → build duration hook → build parallelism hook → wire in and document). Superseded, not deleted, per repo convention (`docs/specs/` supersession pattern used elsewhere, e.g. `_archive/SPEC-superpowers-claude-context-workflows-2026-07-01.md`).
