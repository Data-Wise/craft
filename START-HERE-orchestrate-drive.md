# START HERE — feature/orchestrate-drive

Worktree session kickoff for implementing `/craft:orchestrate:drive`.

## Context

- **Spec:** `docs/specs/SPEC-orchestrate-drive-2026-06-03.md`
- **Plan:** `docs/specs/PLAN-orchestrate-drive-2026-06-03.md` (10 bite-sized TDD tasks)
- **Branch:** `feature/orchestrate-drive` (off `dev@4414bd91`)
- **Task 0 (worktree) is DONE** — you are already inside it. Start at **Task 1**.

## Kickoff prompt (paste into a fresh `claude` session here)

> Read `docs/specs/PLAN-orchestrate-drive-2026-06-03.md` and execute it
> task-by-task using the superpowers:subagent-driven-development skill.
> Start at Task 1 (Task 0's worktree already exists — you're in it).
> Run the tests at each step; stop at the verified-green PR handoff in
> Task 10.

## Build summary (what you're shipping)

1. `skills/orchestration/drive-engine/SKILL.md` — shared dispatch + real verify gate
2. `commands/orchestrate/drive.md` — thin command (condition synthesis, gating, confirm gate)
3. Count sync (cmd 108→109, skill 36→37) + website update (page, nav, `docs/commands.md` index)
4. Help page, tutorial, cookbook, REFCARD, CHANGELOG (both mirrors), swarm↔drive cross-link
5. Tests: unit (`test_craft_plugin.py`) + e2e nav assertion + full e2e/dogfood runs
6. Stop at verified-green; print `gh pr create --base dev` — do NOT open the PR

## Cleanup on merge

Delete this `START-HERE-*.md` before/at PR time — it's a working artifact, not for `dev`.
