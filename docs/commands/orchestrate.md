# /craft:orchestrate

> **Launch orchestrator mode with subagent delegation, monitoring, and chat compression.**

---

## Synopsis

```bash
/craft:orchestrate <task> [mode]
/craft:orchestrate <command>
```

**Quick examples:**

```bash
# Start orchestrated workflow
/craft:orchestrate "add user authentication"

# Use specific mode
/craft:orchestrate "add tests for all endpoints" optimize

# Control commands
/craft:orchestrate status
/craft:orchestrate timeline
/craft:orchestrate abort
```

---

## Description

Activates Orchestrator v2.1 mode which decomposes complex tasks into subtasks, spawns background subagents to work in parallel, monitors progress, and manages context compression.

**What it does:**

1. **Selects mode** — prompts interactively if no mode specified (NEW)
2. **Shows plan** — displays task analysis before acting (NEW)
3. **Confirms** — asks before spawning any agents (NEW)
4. **Spawns** background subagents to work in parallel
5. **Checkpoints** — pauses between waves for review (NEW)
6. **Monitors** progress with visual status dashboard
7. **Tracks** context usage with token estimation
8. **Compresses** chat when approaching limits
9. **Reports** results with ADHD-friendly formatting

---

## Modes

| Mode | Max Agents | Compression | Use Case |
|------|------------|-------------|----------|
| `default` | 2 | 70% | Quick tasks |
| `debug` | 1 (sequential) | 90% | Troubleshooting |
| `optimize` | 4 | 60% | Fast parallel work |
| `release` | 4 | 85% | Pre-release audit |

**Examples:**

```bash
/craft:orchestrate "add auth" optimize    # Fast parallel
/craft:orchestrate "prep release" release # Thorough audit
/craft:orchestrate "debug login" debug    # Sequential verbose
```

---

## Control Commands

During orchestration, use these commands:

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
| `continue` | Resume previous session |
| `save` | Force save session state |
| `history` | List recent sessions |

---

## Interactive Workflow (NEW)

Commands now follow a "Show Steps First" pattern — plans are shown before execution, and confirmation is required at key points.

### Step 0: Mode Selection

If no mode is specified, you'll be prompted:

```
/craft:orchestrate "add user authentication"

? Which orchestration mode should I use?
  › Default (Recommended) — 2 agents max, balanced speed and oversight
    Debug — 1 agent, sequential, verbose output
    Optimize — 4 agents, aggressive parallelization
    Release — 4 agents, full audit trail
```

### Step 1: Plan Display

The orchestrator shows its plan **before spawning any agents**:

```
## TASK ANALYSIS

Request: Add user authentication
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

### Step 2: Confirmation

You decide whether to proceed:

```
? Proceed with this orchestration plan?
  › Yes - Start Wave 1 (Recommended)
    Modify steps
    Change mode
    Cancel
```

### Step 3: Wave Checkpoints

After each wave, results are shown and you can pause, review, or modify:

```
## WAVE 1 COMPLETE

| Agent  | Task            | Status  | Output                   |
|--------|-----------------|---------|--------------------------|
| arch-1 | Design auth     | ✅ Done | OAuth 2.0 + PKCE         |
| code-1 | Backend routes  | ✅ Done | 4 endpoints created      |

? Wave 1 complete. Continue to Wave 2?
  › Yes - Continue (Recommended)
    Review results first
    Modify next wave
    Stop here
```

### Mode-Specific Behavior

Each mode produces visibly different output:

| Behavior | default | debug | optimize | release |
|----------|---------|-------|----------|---------|
| Plan display | Summary table | Step traces with rationale | Parallel dependency map | Full audit with risk notes |
| Checkpoints | Per wave | Every step | Wave end only | Every step |
| Agent output | Summary | Verbose (full output) | Summary | Full output + diffs |
| Auto-proceed | Ask per wave | Ask every step | Ask per wave | Ask every step |

---

## Examples

### Start Orchestrated Workflow

```bash
/craft:orchestrate "add user authentication with OAuth"

## TASK ANALYSIS

Request: Add OAuth authentication
Complexity: complex
Mode: default (2 agents max)
Estimated subtasks: 5

| # | Task              | Agent | Wave | Dependencies |
|---|-------------------|-------|------|--------------|
| 1 | Design auth flow  | arch  | 1    | none         |
| 2 | Implement backend | code  | 1    | none         |
| 3 | Create login UI   | code  | 2    | 1            |
| 4 | Add tests         | test  | 2    | 2,3          |
| 5 | Update docs       | doc   | 3    | 2            |

? Proceed with this orchestration plan?
  › Yes - Start Wave 1 (Recommended)

Spawning Wave 1 agents...
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

### View Timeline

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

### Context Budget

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

---

## Session Management

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
| 1 | Jan 14 | Add auth to API | complete |
| 2 | Jan 13 | Fix parsing bug | complete |
| 3 | Jan 12 | Refactor CLI | abandoned |
```

**State file locations:**

```
.claude/orchestrator-session.json     # Current session
.claude/orchestrator-history/         # Archived sessions
```

---

## Context Monitoring

The orchestrator tracks context usage:

| Level | Action |
|-------|--------|
| < 50% | 🟢 Normal operation |
| 50-70% | 🟡 Status shown in dashboard |
| 70-85% | ⚠️ Warning, prepare for compression |
| > 85% | 🔴 Auto-compress triggered |

**Automatic triggers:**

- Exchange count > 20
- Large agent response (> 3000 tokens)
- Claude system warning about context
- User says "getting long"

---

## Compression

When context gets high, compression archives completed work:

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

---

## Integration

Works with all craft commands:

- Routes to `/craft:arch:*` for design tasks
- Routes to `/craft:code:*` for implementation
- Routes to `/craft:test:*` for testing
- Routes to `/craft:docs:*` for documentation
- Routes to `/brainstorm` (v2.4.0) for context gathering

---

## Orchestrating Brainstorm Sessions (v2.4.0 NEW)

The orchestrator coordinates complex workflows that include context gathering with `/brainstorm`:

### Example

```bash
/craft:orchestrate "plan new authentication feature"
```

Flow:

1. Brainstorm d:8 with categories for comprehensive context
2. Spawn backend-architect agent for design
3. Spawn frontend specialist for UI
4. Coordinate test strategy
5. Synthesize into implementation plan

### Brainstorm + Orchestration Patterns

```bash
# Quick context then implement
/craft:orchestrate "add payment" default
# → Brainstorm q:2 → backend implementation

# Deep context with parallel agents
/craft:orchestrate "design microservices" optimize
# → Brainstorm d:8 -C tech,risk → 4 agents in parallel

# Full lifecycle (v2.4.0)
/craft:orchestrate "implement feature" release
# → Brainstorm d:10 -C req,tech,success → arch + code + test + docs
```

### Benefits

- **Structured context** - Question bank ensures comprehensive requirements
- **Focused agents** - Agents receive filtered context
- **Milestone progress** - Unlimited questions with prompts
- **Spec capture** - Brainstorm → orchestrator → SPEC.md

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Agents timing out | Use `debug` mode for sequential execution |
| Context getting high | Run `compress` command |
| Need to stop | Run `abort` to save state and stop |
| Lost progress | Run `continue` to resume |
| Wrong mode | Run `mode <name>` to switch |
| Too many parallel | Switch to `default` mode (2 agents max) |

### Performance Optimization

| Symptom | Solution |
|---------|----------|
| Slow parallel execution | Use `default` mode instead of `optimize` |
| High context usage | Run `compress` early (at ~60%) |
| Agents timeout | Use `debug` mode (sequential) |
| Lost session | Run `continue` to restore from checkpoint |

### Recommended Modes by Scenario

| Scenario | Mode | Agents | Best For |
|----------|------|--------|----------|
| Simple feature | `default` | 2 max | Quick tasks |
| Complex system | `optimize` | 4 parallel | Speed |
| Debugging | `debug` | 1 sequential | Troubleshooting |
| Pre-release | `release` | 4 + audit | Comprehensive |

---

## See Also

- **Simple routing:** `/craft:do` - Simpler task routing (no monitoring)
- **Pre-flight:** `/craft:check` - Validation before actions
- **Discovery:** `/craft:hub` - Find all commands
- **Brainstorm:** `/brainstorm` - Context gathering (v2.4.0)
