---
title: "Recipe: Use Interactive Orchestration"
description: "Run complex multi-step tasks with mode selection and wave checkpoints"
category: "cookbook"
level: "intermediate"
time_estimate: "5-7 minutes"
related:
  - ../../commands/orchestrate.md
  - ../../tutorials/interactive-orchestration.md
  - ../../reference/REFCARD-INTERACTIVE-COMMANDS.md
---

# Recipe: Use Interactive Orchestration

**Time:** 5-7 minutes
**Level:** Intermediate
**Prerequisites:** Complex task requiring multiple steps or agents
**NEW:** v2.9.0 - Interactive mode selection and wave checkpoints

## Problem

I have a complex task that requires multiple steps, different specialized agents, or coordination across several files. I want to run it with visibility and control over the execution.

## Solution

1. **Start orchestration with task description**

   ```bash
   /craft:orchestrate "add user authentication with JWT, update docs, and add tests"
   ```

   **What happens (v2.9.0 "Show Steps First" pattern):**

   ```
   ╭─ Task Analysis ──────────────────────────────╮
   │ Task: add user authentication with JWT,      │
   │       update docs, and add tests              │
   │ Complexity: 8/10 (high)                       │
   │ Estimated agents: 3                           │
   │ Estimated time: 2-4 hours                     │
   ╰───────────────────────────────────────────────╯
   ```

2. **Choose orchestration mode (v2.9.0)**

   You'll be asked:

   ```
   Select orchestration mode:

   1. default - Sequential execution (one step at a time)
      Best for: Simple multi-step tasks
      Time: Moderate

   2. wave - Parallel waves with checkpoints
      Best for: Independent parallel tasks
      Time: Faster

   3. phase - Sequential phases with validation
      Best for: Complex dependent tasks
      Time: Comprehensive

   Which mode? (1/2/3)
   ```

   **Choose based on your task:**
   - **default** (1): For straightforward tasks, no parallelization
   - **wave** (2): For tasks with independent steps that can run in parallel
   - **phase** (3): For complex tasks with dependencies and validation needs

3. **Review execution plan**

   After selecting mode, you'll see:

   ```
   ╭─ Execution Plan (wave mode) ─────────────────╮
   │                                               │
   │ Wave 1 (parallel):                            │
   │   • backend-architect: JWT implementation     │
   │   • security-specialist: Auth security review │
   │                                               │
   │ Wave 2 (after wave 1):                        │
   │   • test-automator: Add auth tests            │
   │   • docs-architect: Update auth documentation │
   │                                               │
   │ Checkpoints:                                  │
   │   ✓ After wave 1: Review JWT implementation   │
   │   ✓ After wave 2: Verify all tests pass       │
   │                                               │
   ╰───────────────────────────────────────────────╯

   Proceed with this plan? (y/n/adjust)
   ```

4. **Confirm or adjust**

   Options:
   - **y** - Proceed with the plan
   - **n** - Cancel and revise your task description
   - **adjust** - Modify mode or agent selection

5. **Monitor execution with checkpoints (v2.9.0)**

   During execution:

   ```
   ╭─ Wave 1 Progress ────────────────────────────╮
   │ [████████████░░░░░░░░] 60%                    │
   │                                               │
   │ ✓ backend-architect: JWT implementation done  │
   │ ⟳ security-specialist: Reviewing...           │
   ╰───────────────────────────────────────────────╯
   ```

   After each wave:

   ```
   ╭─ Wave 1 Checkpoint ──────────────────────────╮
   │ Both agents completed successfully            │
   │                                               │
   │ Results:                                      │
   │ • src/auth/jwt.ts created (145 lines)         │
   │ • Security review: No critical issues found   │
   │                                               │
   │ Continue to wave 2? (y/n/adjust)              │
   ╰───────────────────────────────────────────────╯
   ```

6. **Review final results**

   When complete:

   ```
   ╭─ Orchestration Complete ─────────────────────╮
   │ All waves completed successfully              │
   │                                               │
   │ Summary:                                      │
   │ • 4 agents executed                           │
   │ • 8 files modified                            │
   │ • 342 lines added                             │
   │ • 89 lines removed                            │
   │ • All tests passing (45 new tests)            │
   │                                               │
   │ Next steps:                                   │
   │ 1. Review changes in modified files           │
   │ 2. Run /craft:check --mode=thorough           │
   │ 3. Commit changes                             │
   ╰───────────────────────────────────────────────╯
   ```

## Explanation

### Interactive Mode Selection (v2.9.0)

The orchestrator now asks you to choose how to execute:

**default mode:**

- Sequential execution
- One step completes before next begins
- Best for: Simple multi-step tasks where order matters
- Example: "Update docs then deploy"

**wave mode:**

- Parallel waves with checkpoints
- Independent tasks run simultaneously
- Pauses between waves for review
- Best for: Tasks with parallelizable steps
- Example: "Update multiple documentation files" (parallel) → "Build site" (after all updates)

**phase mode:**

- Sequential phases with validation
- Each phase has clear deliverables
- Comprehensive validation at checkpoints
- Best for: Complex projects with dependencies
- Example: "Phase 1: Design → Phase 2: Implement → Phase 3: Test → Phase 4: Document"

### Wave Checkpoints (v2.9.0)

After each wave completes:

1. **Shows results** from all agents in that wave
2. **Asks for confirmation** before continuing
3. **Allows adjustments** if issues found
4. **Provides context** for decision-making

Benefits:

- Catch problems early before they cascade
- Review intermediate results
- Adjust plan based on actual outcomes
- ADHD-friendly: natural break points in long tasks

## Variations

- **Quick orchestration without mode selection:**

  ```bash
  /craft:orchestrate "simple task" --mode=default
  ```

  Skips mode selection, goes directly to execution

- **Preview plan without executing:**

  ```bash
  /craft:orchestrate "task" --dry-run
  ```

  Shows the execution plan but doesn't run it

- **Use with /craft:do for automatic mode selection:**

  ```bash
  /craft:do "complex multi-step task"
  ```

  If complexity score is 8-10, automatically routes to orchestrator

- **Resume paused orchestration:**

  ```bash
  /craft:orchestrate:resume
  ```

  Continue from last checkpoint if interrupted

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Mode selection not showing" | Update to v2.9.0+, older versions don't have interactive mode |
| "Wave checkpoint hangs" | One agent may be waiting for input, check agent output |
| "Want to switch modes mid-execution" | Cancel (Ctrl+C) and restart with different mode |
| "Checkpoint shows errors" | Review agent output, fix issues, then choose "adjust" to modify plan |
| "Too many confirmation prompts" | Use --mode flag to skip mode selection, or --yes to auto-confirm |
| "Need to see what mode will do" | Use --dry-run first to preview execution plan |

## When to Use Each Mode

### Use **default** mode when

- Task has 2-4 simple sequential steps
- No parallelization possible
- You want simplest execution
- Example: "Lint code, run tests, commit"

### Use **wave** mode when

- Multiple independent subtasks
- Can benefit from parallel execution
- Want checkpoints to review progress
- Example: "Update 5 documentation files + generate diagrams" (wave 1: parallel updates, wave 2: build site)

### Use **phase** mode when

- Complex multi-phase project
- Strong dependencies between phases
- Need comprehensive validation
- Example: "Design API → Implement backend → Add tests → Update docs → Deploy" (must be sequential)

## Example Workflows

### Example 1: Documentation Update (wave mode)

```bash
/craft:orchestrate "update all tutorials for v2.9.0 features"

# Choose mode: 2 (wave)

# Execution:
# Wave 1 (parallel): Update 4 tutorial files
# Wave 2 (parallel): Update 3 reference cards
# Wave 3 (sequential): Rebuild docs site, validate links

# Result: 7 files updated in parallel, then validated
```

### Example 2: Feature Implementation (phase mode)

```bash
/craft:orchestrate "add OAuth2 authentication to API"

# Choose mode: 3 (phase)

# Execution:
# Phase 1: Design (security review, API design)
# Phase 2: Implement (backend code, database)
# Phase 3: Test (unit tests, integration tests)
# Phase 4: Document (API docs, tutorial)

# Each phase validated before next begins
```

### Example 3: Quick Multi-Step (default mode)

```bash
/craft:orchestrate "fix markdown lint errors and commit"

# Choose mode: 1 (default)

# Execution: Sequential
# 1. Run markdownlint --fix
# 2. Stage changes
# 3. Commit with message

# Simple, fast, no parallelization needed
```

## Related

- [Orchestrate Command](../../commands/orchestrate.md) — Full command reference
- [Interactive Orchestration Tutorial](../../tutorials/interactive-orchestration.md) — Complete guide
- [Interactive Commands Reference](../../reference/REFCARD-INTERACTIVE-COMMANDS.md) — Quick reference
- [Do Command](../../commands/do.md) — Automatic routing to orchestrator
