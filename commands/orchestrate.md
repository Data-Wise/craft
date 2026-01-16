---
name: orchestrate
description: Launch orchestrator mode with subagent delegation, monitoring, mode-aware execution, and chat compression
category: smart
agent: orchestrator-v2
version: 1.1.0
triggers:
  - /craft:orchestrate
  - orchestrate
  - spawn agents
  - delegate tasks
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
---

# /craft:orchestrate — Launch Orchestrator Mode

## Usage

```bash
/craft:orchestrate <task>              # Start with default mode
/craft:orchestrate <task> <mode>       # Start with specific mode
/craft:orchestrate <task> --dry-run    # Preview orchestration plan
/craft:orchestrate <task> -n           # Preview orchestration plan
/craft:orchestrate status              # Show agent dashboard
/craft:orchestrate timeline            # Show execution timeline
/craft:orchestrate compress            # Force chat compression
/craft:orchestrate continue            # Resume previous session
/craft:orchestrate abort               # Stop all agents
```

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

## What It Does

Activates **Orchestrator v2.1** mode which:

1. **Analyzes** your task and decomposes into subtasks
2. **Spawns** background subagents to work in parallel
3. **Monitors** progress with visual status dashboard
4. **Tracks context** usage with token estimation
5. **Compresses** chat when approaching limits
6. **Reports** results with ADHD-friendly formatting

## Examples

### Start Orchestrated Workflow
```bash
/craft:orchestrate "add user authentication with OAuth"

## 📋 TASK ANALYSIS

**Request**: Add OAuth authentication
**Complexity**: complex
**Mode**: default (2 agents max)
**Estimated subtasks**: 5
**Delegation strategy**: hybrid

| # | Task | Agent | Priority | Dependencies |
|---|------|-------|----------|--------------|
| 1 | Design auth flow | arch | P0 | none |
| 2 | Implement backend | code | P0 | 1 |
| 3 | Create login UI | code | P1 | 1 |
| 4 | Add tests | test | P1 | 2,3 |
| 5 | Update docs | doc | P2 | 2 |

Spawning agents...
```

### Fast Parallel Mode
```bash
/craft:orchestrate "add tests for all endpoints" optimize

## 🚀 ORCHESTRATOR v2.1 — OPTIMIZE MODE

**Configuration**:
- Max parallel agents: 4
- Compression threshold: 60%
- Output verbosity: Minimal
- Strategy: Aggressive parallelization

Spawning 4 test agents in parallel...
```

### Check Status
```bash
/craft:orchestrate status

## 🔄 AGENT STATUS

| Agent | Task | Status | Progress | Context |
|-------|------|--------|----------|---------|
| main  | orchestrate | 🟢 active | - | 45% |
| arch-1 | design | ✅ complete | 1/1 | 0% |
| code-1 | backend | 🟡 running | 3/7 | 18% |
| code-2 | frontend | 🟡 running | 2/5 | 12% |

**Context Budget**: 67% (~86K tokens) | **Mode**: default
```

### View Timeline (NEW)
```bash
/craft:orchestrate timeline

## ⏱️ EXECUTION TIMELINE

TIME     0    1m    2m    3m    4m
─────────┼─────┼─────┼─────┼─────┤
arch-1   ██████░░░░░░░░░░░░░░░░░░ ✅ 1.2m
code-1   ░░░░░░████████████░░░░░ 🟡 2.5m
code-2   ░░░░░░░░██████░░░░░░░░░ ✅ 1.8m
─────────┼─────┼─────┼─────┼─────┤
                         NOW ▲

**ETA**: ~1.5 min remaining
```

### Context Budget (NEW)
```bash
/craft:orchestrate budget

## 📊 CONTEXT BUDGET

| Component | Tokens (est) | % of ~128K |
|-----------|--------------|------------|
| System prompt | ~3,000 | 2.3% |
| Conversation | ~15,000 | 11.7% |
| Agent results | ~8,000 | 6.3% |
| **Total** | **~26,000** | **20.3%** |

Status: 🟢 Healthy (< 50%)
```

### Force Compression
```bash
/craft:orchestrate compress

## ⚠️ CONTEXT COMPRESSION

### Completed (Archived)
- ✅ Auth design: OAuth 2.0 + PKCE
- ✅ Backend routes: /auth/*, /callback

### Active (Retained)
- 🔄 Frontend login component
- 🔄 Test generation

**New context usage**: ~35%
```

### Resume Previous Session (NEW)
```bash
/craft:orchestrate continue

## 🔄 RESUMING PREVIOUS SESSION

**Session**: 2025-12-27-abc123
**Goal**: Add sensitivity analysis to RMediation
**Progress**: 60% complete

### Completed
- ✅ Architecture design
- ✅ Test stubs created

### In Progress
- 🔄 Implementation (code-1)

Resuming...
```

### Abort All Agents
```bash
/craft:orchestrate abort

## 🛑 ABORTING ALL AGENTS

Stopping: arch-1, code-1, code-2, test-1
State preserved to: .claude/orchestrator-session.json
```

## Control Commands

During orchestration, say:

| Command | Action |
|---------|--------|
| `status` | Show agent dashboard |
| `timeline` | Show execution timeline |
| `budget` | Show context budget |
| `compress` | Force chat compression now |
| `mode X` | Switch to mode X |
| `pause <agent>` | Pause specific agent |
| `resume all` | Resume paused agents |
| `abort` | Stop everything, save state |
| `report` | Detailed progress report |
| `focus <task>` | Reprioritize |
| `continue` | Resume previous session |
| `save` | Force save session state |
| `history` | List recent sessions |
| `new` | Start fresh (archive current) |

## Session Management (NEW in v1.1.0)

Sessions persist across disconnects:

```bash
# Resume previous session
/craft:orchestrate continue

# Force save current state
/craft:orchestrate save

# View session history
/craft:orchestrate history

## 📜 SESSION HISTORY

| # | Date | Goal | Status |
|---|------|------|--------|
| 1 | Dec 27 | Add auth to API | complete |
| 2 | Dec 26 | Fix parsing bug | complete |
| 3 | Dec 25 | Refactor CLI | abandoned |

# Resume specific session from history
/craft:orchestrate history 2

# Start fresh (archives current session)
/craft:orchestrate new
```

### State File Location

```
.claude/orchestrator-session.json     # Current session
.claude/orchestrator-history/         # Archived sessions
```

### Auto-Save Events

State is automatically saved on:
- Task analysis completion
- Agent start/complete/fail
- Decision checkpoints
- Before compression
- User says `save` or `abort`

## Context Monitoring

The orchestrator tracks context usage with heuristics:

| Level | Action |
|-------|--------|
| < 50% | 🟢 Normal operation |
| 50-70% | 🟡 Status shown in dashboard |
| 70-85% | ⚠️ Warning, prepare for compression |
| > 85% | 🔴 Auto-compress triggered |

### Automatic Triggers
- Exchange count > 20
- Large agent response (> 3000 tokens)
- Claude system warning about context
- User says "getting long"

## Integration

Works with all craft commands:
- Routes to `/craft:arch:*` for design tasks
- Routes to `/craft:code:*` for implementation
- Routes to `/craft:test:*` for testing
- Routes to `/craft:docs:*` for documentation

## See Also

- `/craft:do` — Simpler task routing (no monitoring)
- `/craft:check` — Pre-flight validation
- `/craft:hub` — Discover all commands
