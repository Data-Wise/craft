---
name: orchestrate
description: Launch orchestrator mode with subagent delegation, monitoring, mode-aware execution, and chat compression
category: smart
arguments:
  - name: task
    description: Task description
    required: false
  - name: mode
    description: Execution mode (default|debug|optimize|release)
    required: false
  - name: dry-run
    description: Preview orchestration plan without spawning agents
    required: false
    default: false
    alias: -n
  - name: swarm
    description: Run agents in isolated worktrees with branch convergence
    required: false
    default: false
  - name: refine
    description: Refine the prompt via the prompt-refiner skill before acting
    required: false
    default: false
  - name: engine
    description: "Override execution engine: workflow|fanout (default: fanout). When a WORKFLOW-*.yaml or ORCHESTRATE-*.md is derivable from the task, orchestrate auto-detects it and proposes --engine=workflow with confirm."
    required: false
    default: fanout
  - name: no-clarify
    description: "Skip Step 0.5 Clarify (the bounded /craft:grill pre-planning interrogation)"
    required: false
    default: false
  - name: yes
    description: "Non-interactive: auto-accept every Recommended answer, emit zero AskUserQuestion prompts (alias --non-interactive)"
    required: false
---

# /craft:orchestrate — Launch Orchestrator Mode

## Usage

```bash
/craft:orchestrate <task>              # Start with default mode
/craft:orchestrate <task> <mode>       # Start with specific mode
/craft:orchestrate <task> --dry-run    # Preview orchestration plan
/craft:orchestrate <task> -n           # Preview orchestration plan
/craft:orchestrate <task> --swarm     # Isolated worktrees per agent
/craft:orchestrate status              # Show agent dashboard
/craft:orchestrate timeline            # Show execution timeline
/craft:orchestrate compress            # Force chat compression
/craft:orchestrate continue            # Resume previous session
/craft:orchestrate abort               # Stop all agents
```

## --refine (prompt pre-processing)

When `--refine` is set, do NOT act on the raw argument. First invoke the
`prompt-refiner` skill with the argument and project context. Follow that
skill's canonical flow (before/after → Accept/Edit/Use-original; `--yes`
or auto mode auto-accepts). Then proceed using the prompt the skill
returns. On no-argument interactive commands, refine AFTER the topic is
captured.

`--yes` cascades: the prompt-refiner auto-accepts AND the interactive loop is suppressed —
one flag, fully headless.

## Dry-Run Mode

Preview the orchestration plan without spawning any agents:

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Orchestrator v2.1                                 │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Task Analysis:                                              │
│   - Input: "add user authentication with OAuth"               │
│   - Complexity: Complex                                       │
│   - Mode: default (2 agents max)                              │
│   - Estimated subtasks: 5                                     │
│   - Delegation strategy: Hybrid (parallel + sequential)       │
│                                                               │
│ ✓ Orchestration Plan:                                         │
│                                                               │
│   Wave 1 (Parallel - 2 agents):                               │
│   ├─ Agent: arch-1 (architecture)                             │
│   │  Task: Design OAuth flow and security model               │
│   │  Estimated: ~8 minutes                                    │
│   │  Dependencies: None                                       │
│   │                                                           │
│   └─ Agent: doc-1 (documentation)                             │
│      Task: Research OAuth 2.0 best practices                  │
│      Estimated: ~5 minutes                                    │
│      Dependencies: None                                       │
│                                                               │
│   Wave 2 (Sequential - awaits Wave 1):                        │
│   ├─ Agent: code-1 (backend)                                  │
│   │  Task: Implement auth endpoints                           │
│   │  Estimated: ~15 minutes                                   │
│   │  Dependencies: arch-1                                     │
│   │                                                           │
│   ├─ Agent: code-2 (frontend)                                 │
│   │  Task: Create login/logout UI                            │
│   │  Estimated: ~12 minutes                                   │
│   │  Dependencies: arch-1                                     │
│   │                                                           │
│   └─ Agent: test-1 (testing)                                  │
│      Task: Generate test suite                                │
│      Estimated: ~10 minutes                                   │
│      Dependencies: code-1, code-2                             │
│                                                               │
│ ✓ Resource Allocation:                                        │
│   - Max concurrent agents: 2                                  │
│   - Total agents required: 5                                  │
│   - Estimated total time: ~35 minutes (with parallelization)  │
│   - Sequential time: ~50 minutes                              │
│   - Time saved: ~15 minutes (30%)                             │
│                                                               │
│ ⚠ Warnings:                                                   │
│   • Context usage will be monitored (compression at 70%)      │
│   • Progress dashboard updates every 30 seconds               │
│   • Session state auto-saved at checkpoints                   │
│                                                               │
│ 📊 Summary: 5 agents, 2 waves, ~35 min execution              │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

**Note**: Dry-run shows the orchestration strategy, agent allocation, and parallelization plan without spawning actual background agents or consuming context.

## Modes (NEW in v1.1.0)

| Mode | Max Agents | Compression | Use Case |
|------|------------|-------------|----------|
| `default` | 2 | 70% | Quick tasks |
| `debug` | 1 (sequential) | 90% | Troubleshooting |
| `optimize` | 4 | 60% | Fast parallel work |
| `release` | 4 | 85% | Pre-release audit |

```bash
/craft:orchestrate "add auth" optimize    # Fast parallel
/craft:orchestrate "prep release" release # Thorough audit
/craft:orchestrate "debug login" debug    # Sequential verbose
```

## Execution Behavior (MANDATORY)

When this command runs, Claude MUST follow these steps in order. Do NOT skip
any step or proceed without confirmation.

### Step 0: Mode Selection (when no mode argument given)

If the user did not specify a mode (`default|debug|optimize|release`), prompt:

```json
{
  "questions": [{
    "question": "Which orchestration mode should I use?",
    "header": "Mode",
    "multiSelect": false,
    "options": [
      {
        "label": "Default (Recommended)",
        "description": "2 agents max, balanced speed and oversight. Best for most tasks."
      },
      {
        "label": "Debug",
        "description": "1 agent, sequential execution, verbose output. Use for troubleshooting."
      },
      {
        "label": "Optimize",
        "description": "4 agents, aggressive parallelization. Use for speed-critical work."
      },
      {
        "label": "Release",
        "description": "4 agents, full audit trail. Use for pre-release validation."
      }
    ]
  }]
}
```

If the user specified a mode via argument, skip this step and use that mode.

### Step 0.5: Clarify (default ON)

Before building any plan, assess task ambiguity. If the task is underspecified or admits multiple
valid interpretations, invoke `/craft:grill --bound 2 --no-capture` for a quick bounded
interrogation that LOCKS the decisions which change the plan — one question at a time, recommended
answer per question, codebase-first. `--no-capture` keeps it from writing a `GRILL-*` spec file
mid-orchestration; the decisions return inline. Then build Step 1 on the locked answers.

SKIP this step when:

- the user passed `--no-clarify` (or `--yes` to auto-proceed), OR
- a matching `SPEC-*` / `ORCHESTRATE-*` / `WORKFLOW-*` file already pins the decisions, OR
- the task is unambiguous (single interpretation, clear scope + success criteria).

Fallback if `/craft:grill` is unavailable: 1–2 `AskUserQuestion` rounds, recommended-option-first.

### Step 1: Task Analysis (show plan FIRST)

Analyze the task and display a numbered plan. Do NOT spawn any agents yet.

```text
## TASK ANALYSIS

**Request**: [1-sentence summary]
**Complexity**: [simple | moderate | complex | multi-phase]
**Mode**: [selected mode] ([max agents] agents max)
**Estimated subtasks**: N
**Delegation strategy**: [sequential | parallel | hybrid]

| # | Task | Agent | Wave | Dependencies |
|---|------|-------|------|--------------|
| 1 | ... | ... | 1 | none |
| 2 | ... | ... | 1 | none |
| 3 | ... | ... | 2 | 1 |
```

### Engine Selection (--engine routing)

When `--engine` is **not** specified:

1. **Scan CWD** for files whose names match the task topic: `WORKFLOW-*.yaml`, `ORCHESTRATE-*.md`, `SPEC-*.md`.
2. If a match is found, **auto-select `engine=workflow`** and surface a confirm gate (see Step 2 variant below) before proceeding.
3. If no match is found, fall back to **`engine=fanout`** (fan-out subagent delegation — the default).
4. An explicit `--engine` flag always overrides auto-detection.

**Default stays `fanout`** until the parity gate passes — see `docs/runbooks/parity-gate.md`.

### Step 2: Confirm Before Execution

After showing the plan, ALWAYS ask before spawning agents:

```json
{
  "questions": [{
    "question": "Proceed with this orchestration plan?",
    "header": "Continue",
    "multiSelect": false,
    "options": [
      {
        "label": "Yes - Start Wave 1 (Recommended)",
        "description": "Begin executing the plan as shown above."
      },
      {
        "label": "Modify steps",
        "description": "I'll adjust the task breakdown before executing."
      },
      {
        "label": "Change mode",
        "description": "Switch to a different execution mode."
      },
      {
        "label": "Cancel",
        "description": "Abort orchestration without spawning agents."
      }
    ]
  }]
}
```

Only spawn agents after the user selects "Yes - Start Wave 1".

**Variant — auto-detected workflow engine**: When a matching WORKFLOW/SPEC/ORCHESTRATE file was found in Step 1, replace the confirm question with:

```json
{
  "questions": [{
    "question": "Auto-detected WORKFLOW/SPEC: <filename>. Route to :workflow engine?",
    "header": "Engine",
    "multiSelect": false,
    "options": [
      {
        "label": "Yes use :workflow (Recommended)",
        "description": "Route to /craft:orchestrate:drive using the detected spec/workflow file."
      },
      {
        "label": "No use fanout instead",
        "description": "Ignore the detected file and proceed with standard fan-out subagent delegation."
      }
    ]
  }]
}
```

### Steps 3-N: Execute with Progress

Spawn agents according to the confirmed plan. Show progress after each wave.

### Mode-Specific Behavior

| Behavior | default | debug | optimize | release |
|----------|---------|-------|----------|---------|
| Plan display | Summary table | Step traces with rationale | Parallel dependency map | Full audit with risk notes |
| Checkpoints | Per wave | Every step | Wave end only | Every step |
| Agent output | Summary | Verbose (full output) | Summary | Full output + diffs |
| Auto-proceed | Ask per wave | Ask every step | Ask per wave | Ask every step |

## Examples

```bash
/craft:orchestrate "add user authentication with OAuth"   # default mode
/craft:orchestrate "prep release" release                 # thorough audit
/craft:orchestrate "refactor data layer" --swarm          # isolated worktrees per agent
/craft:orchestrate "add auth" --dry-run                    # preview plan, spawn nothing
```

Full worked examples with progress mockups live in the reference doc.

## Control Commands

During orchestration, say:

| Command | Action |
|---------|--------|
| `status` | Show agent dashboard |
| `timeline` | Show execution timeline |
| `compress` | Force chat compression now |
| `abort` | Stop everything, save state |
| `continue` | Resume previous session |
| `swarm status` | Show swarm agent worktree status |

Full control-command catalog (budget, pause/resume, focus, history, …) is in the reference doc.

## Swarm Mode (`--swarm`) — summary

`--swarm` runs agents in isolated worktrees with branch convergence (non-overlapping scopes,
per-agent branch, bottom-up merge + test gate). Full execution flow, configuration, cleanup, and
the dry-run mockup live in the reference doc.

## Reference

Mockups (status/timeline/budget/compression), the full control-command catalog, session
management, worktree types, swarm deep config, performance tips, and token instrumentation:
[orchestrate-reference.md](../docs/reference/orchestrate-reference.md).

## See Also

- `/craft:orchestrate:drive` — spec-anchored /goal turn-loop (vs --swarm fan-out)
- `/craft:quota` — Pre-flight quota check before heavy orchestrate runs
- `/craft:do` — Simpler task routing (no monitoring)
- `/craft:check` — Pre-flight validation
- `/craft:hub` — Discover all commands
- `/brainstorm` — Context gathering (v2.4.0)
