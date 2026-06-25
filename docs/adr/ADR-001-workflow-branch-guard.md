# ADR-001: Workflow() Tool vs Worktree Branch Model

**Status:** Accepted
**Date:** 2026-06-24
**Issue:** #171

## Context

Claude Code's `Workflow()` tool spawns in-session agents that inherit the parent
session's CWD. When the parent session is on `dev`, branch-guard blocks new code
files in all spawned agents. `isolation: 'worktree'` creates ephemeral worktrees
(no persistent branch), incompatible with the craft `feature/*` branch model.

## Decision

`Workflow()` is safe for READ operations from `dev` sessions (research, audit,
analysis). Feature code writes use the ORCHESTRATE protocol: plan on `dev` →
create a `feature/*` worktree → commit the ORCHESTRATE file → start a new session
in the worktree. No change to branch-guard or Workflow semantics.

## Alternatives Considered

1. `isolation: 'worktree'` per `agent()` call — rejected: ephemeral, no branch name, state discarded at session end.
2. Workflow-aware branch-guard bypass — rejected: the safety invariant exists for correctness, not policy.
3. Pre-create a worktree then call Workflow from `dev` — rejected: agents inherit the calling session's CWD, not the worktree path.
4. Disable Workflow on `dev` entirely — rejected: too restrictive for read-only use.

## Consequences

Constraint formally documented. No code added. Usage guidance stays in TUTORIAL
and ORCHESTRATE docs. Issue #171 closed by this record.
