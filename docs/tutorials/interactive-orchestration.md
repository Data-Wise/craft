# Tutorial: Interactive Orchestration

> **What you'll learn:** How to use the new interactive orchestration workflow with plan confirmation, wave checkpoints, and mode selection.
>
> **Level:** Intermediate
>
> **Prerequisites:** Basic familiarity with `/craft:orchestrate`

---

## What You'll Learn

1. Select an orchestration mode interactively
2. Review and confirm a task plan before execution
3. Use wave checkpoints to control progress
4. Handle decision points during orchestration
5. Choose the right mode for your task

---

## Part 1: Starting an Orchestration

### Step 1.1: Launch Without a Mode

When you run orchestrate without specifying a mode, you'll be prompted:

```bash
/craft:orchestrate "add user authentication with OAuth"
```

The orchestrator asks which mode to use:

```
? Which orchestration mode should I use?
  > Default (Recommended) — 2 agents max, balanced speed and oversight
    Debug — 1 agent, sequential, verbose output
    Optimize — 4 agents, aggressive parallelization
    Release — 4 agents, full audit trail
```

Select **Default** for most tasks. Use **Debug** when troubleshooting, **Optimize** for speed, and **Release** for thorough pre-release validation.

### Step 1.2: Launch With a Mode

Skip the mode prompt by specifying it directly:

```bash
/craft:orchestrate "add user authentication" optimize
```

This jumps straight to the task analysis.

---

## Part 2: Reviewing the Plan

### Step 2.1: Read the Task Analysis

After mode selection, the orchestrator analyzes your task and shows a plan:

```
## TASK ANALYSIS

Request: Add user authentication with OAuth
Complexity: complex
Mode: default (2 agents max)
Estimated subtasks: 5
Delegation strategy: hybrid

| # | Task              | Agent | Wave | Dependencies |
|---|-------------------|-------|------|--------------|
| 1 | Design auth flow  | arch  | 1    | none         |
| 2 | Implement backend | code  | 1    | none         |
| 3 | Create login UI   | code  | 2    | 1            |
| 4 | Add tests         | test  | 2    | 2            |
| 5 | Update docs       | doc   | 3    | 2,3          |
```

**Key things to check:**

- Are the subtasks correct? Missing anything?
- Are the wave groupings logical? (Independent tasks in the same wave)
- Are dependencies accurate?

### Step 2.2: Confirm or Modify

```
? Proceed with this orchestration plan?
  > Yes - Start Wave 1 (Recommended)
    Modify steps
    Change mode
    Cancel
```

| Choice | When to use |
|--------|-------------|
| **Yes - Start Wave 1** | Plan looks good, proceed |
| **Modify steps** | Need to add, remove, or reorder tasks |
| **Change mode** | Realize you need a different execution style |
| **Cancel** | Task isn't right, start over |

---

## Part 3: Wave Execution and Checkpoints

### Step 3.1: Wave 1 Executes

After confirmation, the orchestrator spawns agents for Wave 1:

```
Spawning Wave 1 agents...
  arch-1: Design auth flow (running)
  code-1: Implement backend (running)
```

### Step 3.2: Wave Checkpoint

When Wave 1 completes, you see results and are asked to continue:

```
## WAVE 1 COMPLETE

| Agent  | Task            | Status  | Output                        |
|--------|-----------------|---------|-------------------------------|
| arch-1 | Design auth     | Done    | OAuth 2.0 + PKCE recommended  |
| code-1 | Backend routes  | Done    | 4 endpoints created           |

Next: Wave 2
| Agent  | Task            | Dependencies |
|--------|-----------------|-------------|
| code-2 | Create login UI | arch-1      |
| test-1 | Add tests       | code-1      |

? Wave 1 complete. Continue to Wave 2?
  > Yes - Continue (Recommended)
    Review results first
    Modify next wave
    Stop here
```

| Choice | When to use |
|--------|-------------|
| **Yes - Continue** | Results look good, proceed to next wave |
| **Review results first** | Want to see detailed output from Wave 1 agents |
| **Modify next wave** | Need to adjust Wave 2 tasks based on Wave 1 results |
| **Stop here** | Wave 1 output is sufficient, don't need more waves |

### Step 3.3: Continue Through Waves

Repeat for each wave until all tasks are complete. The final summary shows everything that was accomplished.

---

## Part 4: Decision Points

### Step 4.1: Active Prompts

During orchestration, if a decision is needed (e.g., a design choice), you'll get a structured prompt instead of a passive text listing:

```
## DECISION REQUIRED

Context: The auth implementation needs a token strategy
Impact: Affects security model and scalability
Blocking: code-1 agent paused waiting

? The auth implementation needs a token strategy. Which approach?
  > JWT with refresh tokens (Recommended) — Stateless, scalable
    Session cookies — Simple, easy revocation
    Hybrid (JWT + sessions) — Most flexible but complex
```

Select an option and the blocked agent resumes immediately.

---

## Part 5: Mode Comparison

### When to Use Each Mode

| Scenario | Mode | Why |
|----------|------|-----|
| Add a feature | `default` | Balanced — 2 agents, asks per wave |
| Debug a failing test | `debug` | Sequential — 1 agent, asks every step, verbose output |
| Bulk refactoring | `optimize` | Fast — 4 agents, minimal prompts |
| Pre-release validation | `release` | Thorough — 4 agents, asks every step, full audit |

### Output Differences

Try the same task in different modes to see the difference:

```bash
# Minimal output, per-wave checkpoints
/craft:orchestrate "add auth" default

# Verbose output, per-step checkpoints
/craft:orchestrate "add auth" debug

# Parallel execution, wave-end checkpoints
/craft:orchestrate "add auth" optimize
```

---

## Summary

You've learned how to:

- Select orchestration modes (interactively or via argument)
- Review task plans before any agents are spawned
- Use wave checkpoints to control execution flow
- Respond to structured decision points
- Choose the right mode for your task

---

## Next Steps

- **Deep dive:** [Orchestrator Deep Dive](../reference/../orchestrator.md) — Full reference for all orchestrator features
- **Pattern guide:** [Interactive Commands Guide](../guide/interactive-commands.md) — How this pattern works across all 4 commands
- **Check command:** [/craft:check](../commands/check.md) — Uses the same interactive pattern for pre-flight checks
