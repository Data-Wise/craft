# START HERE — feature/refine-flag

Worktree session kickoff for implementing the `--refine` flag.

## Context

- **Spec:** `docs/specs/SPEC-refine-flag-2026-06-03.md`
- **Plan:** `docs/specs/PLAN-refine-flag-2026-06-03.md` (8 bite-sized TDD tasks)
- **Branch:** `feature/refine-flag` (off `dev@a4861cfc`)
- **Task 0 (worktree) is DONE** — you are already inside it. Start at **Task 1**.

## Kickoff prompt (paste into a fresh `claude` session here)

> Read `docs/specs/PLAN-refine-flag-2026-06-03.md` and execute it
> task-by-task using the superpowers:subagent-driven-development skill.
> Start at Task 1 (Task 0's worktree already exists — you're in it).
> Run the tests at each step; stop at the verified-green PR handoff in
> Task 8.

## Build summary (what you're shipping)

1. `skills/workflow/prompt-refiner/SKILL.md` — the shared refiner + canonical flow
2. `--refine` flag + delegation block on 5 commands (brainstorm, do, orchestrate, plan:feature, arch:plan)
3. E2E scope guard (flag in exactly the 5) + dogfood anti-drift (delegate, don't restate)
4. Skill count sync (+1), help/tutorial/cookbook, mirrors/REFCARD/CHANGELOG, /refine sunset note
5. Stop at verified-green; print `gh pr create --base dev` — do NOT open the PR

## Cleanup on merge

Delete this `START-HERE-*.md` before/at PR time — working artifact, not for `dev`.
