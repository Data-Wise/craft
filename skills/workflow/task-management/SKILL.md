---
name: background-task-manager
description: This skill should be used when the user asks to "check task status", "view task output", "cancel task", "kill background task", "list running tasks", "wait for task", "show task results", "stop background job", or mentions background task IDs from `/workflow:brainstorm --background`, `/workflow:refine`, or other backgrounded commands. Manages the lifecycle of already-launched background tasks — status inspection, output retrieval, and cancellation.
---

# Background Task Manager Skill

Expert in the **lifecycle of already-launched background tasks** in craft workflows. Covers the three post-launch operations: checking status, retrieving output, and cancelling. Does not launch tasks itself — that is done by `/workflow:brainstorm --background`, `/workflow:refine` option 2, and similar backgrounding commands.

## When to Use

| User intent | Operation |
|-------------|-----------|
| "is it done", "what's the status", "list tasks", "wait for X" | Status check |
| "show me the output", "view results", "what did it produce" | Output retrieval |
| "cancel it", "kill that task", "stop the background job", "abort all" | Cancellation |

If a task ID is in the prompt, route directly to the matching operation. If not, default to listing all active tasks (status without args).

## Operations

### 1. Status Check (task-status)

Inspect background task state — running, complete, failed, queued.

**Inputs:** optional `<task_id>`; flags `--wait`, `--all`.

**Modes:**

- **List all** (no args) — table of active and recently completed tasks with elapsed time and estimated duration.
- **Specific task** (`<task_id>`) — single-task detail: command, started-at, ETA, current step.
- **Wait** (`--wait <task_id>`) — block until completion, then hand off to output retrieval.

**Output:** scannable table for the list view; for `--wait`, return only when task transitions to `complete`/`failed`. Show top 5 by recency when the list grows long.

### 2. Output Retrieval (task-output)

Surface results from a completed (or in-progress) background task.

**Inputs:** `<task_id>`, or `--latest` for most recent completion; flag `--raw` to skip formatting.

**Steps:**

1. Resolve task — explicit ID, `--latest`, or prompt the user to pick from the active list.
2. Read stored result — formatted summary (default) or raw stdout (`--raw`).
3. If task is still running, show partial output and remind user to re-run when complete.
4. Suggest the next action implied by the result (e.g., a brainstorm output may prompt spec capture).

**Output:** the task's produced artifact (proposal, analysis, refined prompt) plus a one-line "what to do next" footer.

### 3. Cancellation (task-cancel)

Stop a background task before it completes.

**Inputs:** `<task_id>`, or `--all` to cancel everything active; flag `--force` to skip confirmation.

**Steps:**

1. Confirm intent — show task command + elapsed time, ask "Cancel? (y/N)" unless `--force` or `--all`.
2. Send termination signal to the task.
3. Preserve any partial output for later retrieval via `task-output --raw`.
4. Report cancellation outcome and surface any remaining active tasks.

**When to suggest:** task is taking far longer than its ETA, user asked the wrong question, user wants to retry with different inputs.

## Relation to task-analyzer and session-state

These three skills occupy distinct slices of the "task" concept — keep them disjoint:

- **`task-analyzer`** (orchestration) — analyzes a natural-language task *description* and routes to the right craft command sequence **before any work is launched**. It is a planning/routing skill; it never inspects running processes.
- **`session-state`** (orchestration) — persists **orchestrator session** state (multi-agent coordination, decisions, completed work) so a session can resume after disconnect. Operates on `.claude/orchestrator-session.json`, not on individual background-task IDs.
- **`background-task-manager`** (this skill) — operates **after** a background task has been launched by an interactive command. Concerned with task IDs, exit status, output buffers, and cancellation — not with task routing or session-level orchestration state.

If the user says "what should I run" → task-analyzer. If they say "resume my orchestrator session" → session-state. If they say "is task abc123 done yet" → this skill.

## Integration

Replaces three commands during the v2.34.0 → v3.0.0 migration:

- `/workflow:task-status` → operation 1
- `/workflow:task-output` → operation 2
- `/workflow:task-cancel` → operation 3

Both invocation paths work during the deprecation cycle. The skill auto-fires on task-ID mentions and natural-language match; explicit `/craft:workflow:task-*` paths continue to function until v3.0.0.

## Related Skills

- `adhd-workflow` — session-level workflow (done, recap, next, focus, stuck). Sibling in `skills/workflow/`.
- `task-analyzer` — pre-launch task routing.
- `session-state` — orchestrator session persistence.
