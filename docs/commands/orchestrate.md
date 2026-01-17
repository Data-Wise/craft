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
1. **Analyzes** your task and decomposes into subtasks
2. **Spawns** background subagents to work in parallel
3. **Monitors** progress with visual status dashboard
4. **Tracks** context usage with token estimation
5. **Compresses** chat when approaching limits
6. **Reports** results with ADHD-friendly formatting

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

## Examples

### Start Orchestrated Workflow

```bash
/craft:orchestrate "add user authentication with OAuth"

## 📋 TASK ANALYSIS

**Request**: Add OAuth authentication
**Complexity**: complex
**Mode**: default (2 agents max)
**Estimated subtasks**: 5

| # | Task | Agent | Priority | Dependencies |
|---|------|-------|----------|--------------|
| 1 | Design auth flow | arch | P0 | none |
| 2 | Implement backend | code | P0 | 1 |
| 3 | Create login UI | code | P1 | 1 |
| 4 | Add tests | test | P1 | 2,3 |
| 5 | Update docs | doc | P2 | 2 |

Spawning agents...
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

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Agents timing out | Use `debug` mode for sequential execution |
| Context getting high | Run `compress` command |
| Need to stop | Run `abort` to save state and stop |
| Lost progress | Run `continue` to resume |
| Wrong mode | Run `mode <name>` to switch |

---

## See Also

- **Simple routing:** `/craft:do` - Simpler task routing (no monitoring)
- **Pre-flight:** `/craft:check` - Validation before actions
- **Discovery:** `/craft:hub` - Find all commands
