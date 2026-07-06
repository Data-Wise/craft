# Craft Orchestrator Reference

> 📚 **Reference Documentation** - Technical details and advanced usage.
>
> New to orchestrator? Start with the [**User Guide**](guide/orchestrator.md) for practical examples and quick start.

The orchestrator coordinates multiple specialized agents to handle complex development tasks through intelligent delegation and parallel execution.

> **Three orchestration modes:** `/craft:orch` (this page) improvises each
> turn; [`/craft:orch:drive`](commands/orch/drive.md) drives an
> approved spec to verified green; [`/craft:orch:workflow`](commands/orch/workflow.md)
> executes a coded, fixed-control-flow program with schema-gated agents and
> resumable replay. See [Orchestrator Modes Compared](tutorials/orchestrator-modes-compared.md).

## Overview

Orchestrator v2 provides:

- **Mode-aware execution** - Adapts based on urgency and complexity
- **Subagent monitoring** - Real-time progress tracking
- **Context tracking** - Token budget management
- **Timeline view** - Execution visualization
- **Result synthesis** - Unified, actionable output

## Basic Usage

```bash
# Let orchestrator choose mode
/craft:orch "add authentication"

# Specify mode explicitly
/craft:orch "add auth" optimize    # Fast parallel
/craft:orch "prep release" release # Thorough

# Monitor execution
/craft:orch status                 # Agent dashboard
/craft:orch timeline               # Execution timeline
/craft:orch budget                 # Context tracking
```

## Modes

### Optimize Mode (Fast)

**Time:** <180s
**Agents:** 3-4 in parallel
**Use case:** Feature development, quick iterations

```bash
/craft:orch "implement user profiles" optimize
```

**Workflow:**

1. Launches 3-4 agents simultaneously
2. Monitors progress in real-time
3. Synthesizes results as agents complete
4. Provides actionable recommendations

### Release Mode (Comprehensive)

**Time:** <300s
**Agents:** 4+ comprehensive checks
**Use case:** Production preparation, quality audit

```bash
/craft:orch "prepare for production" release
```

**Workflow:**

1. Security audit (security-specialist)
2. Performance check (performance-engineer)
3. Test suite (testing-specialist)
4. Deployment readiness (devops-engineer)
5. Code quality (code-quality-reviewer)

### Debug Mode (Verbose)

**Time:** <120s
**Agents:** 2-3 with detailed logging
**Use case:** Troubleshooting, diagnostics

```bash
/craft:orch "why is CI failing" debug
```

## Agent Coordination

### Parallel Execution

**Sequential (Old):**

```
Agent 1: ████████ (60s)
Agent 2:         ████████ (60s)
Agent 3:                 ████████ (60s)
Total:   ████████████████████████ (180s)
```

**Parallel (Orchestrator v2):**

```
Agent 1: ████████ (60s)
Agent 2: ████████ (60s)
Agent 3: ████████ (60s)
Total:   ████████ (~60s)
```

**Performance gain:** 3× faster

### Agent Communication

Agents can share context and coordinate:

```
security-specialist: "SQL injection vulnerability found"
→ Notifies backend-architect

backend-architect: "Implementing parameterized queries"
→ Notifies testing-specialist

testing-specialist: "Adding security test cases"
```

## Monitoring & Status

### Status Dashboard

```bash
/craft:orch status
```

**Output:**

```
╭──────────────────────────────────────────╮
│ 📊 Orchestrator Status                   │
├──────────────────────────────────────────┤
│                                          │
│ Active Agents: 3                         │
│                                          │
│ ✅ security-specialist    [Complete]     │
│ 🔄 performance-engineer   [Running 45s]  │
│ ⏳ testing-specialist     [Queued]       │
│                                          │
│ Mode: optimize                           │
│ Est. completion: 30s                     │
│                                          │
╰──────────────────────────────────────────╯
```

### Timeline View

```bash
/craft:orch timeline
```

**Visualizes:**

- Agent start/end times
- Parallel execution periods
- Idle time (if any)
- Total execution time

### Context Budget

```bash
/craft:orch budget
```

**Tracks:**

- Tokens used per agent
- Total token consumption
- Budget remaining
- Cost estimate

## Result Synthesis

After agents complete, orchestrator synthesizes results:

### Synthesis Process

1. **Collect Results**

   ```
   Agent 1: Security audit → No critical issues
   Agent 2: Performance → 2 slow queries
   Agent 3: Tests → 245/245 passing
   ```

2. **Identify Priorities**

   ```
   Critical: None
   Important: Optimize 2 queries
   Optional: Increase coverage
   ```

3. **Generate Summary**

   ```
   ╭──────────────────────────────────────────╮
   │ 🎯 Orchestration Complete                │
   ├──────────────────────────────────────────┤
   │                                          │
   │ ✅ Security: No vulnerabilities          │
   │ ⚠️  Performance: 2 queries to optimize   │
   │ ✅ Tests: 245/245 passing (85% coverage) │
   │                                          │
   │ 📋 Next Steps:                           │
   │    1. Optimize identified queries        │
   │    2. Increase coverage to 90%           │
   │    3. Ready for staging deployment       │
   │                                          │
   ╰──────────────────────────────────────────╯
   ```

## Advanced Features

### Dynamic Agent Selection

Orchestrator intelligently selects agents based on:

- Task pattern
- Mode
- Project context
- Previous results

**Example:**

```
Task: "add authentication"
Pattern: FEATURE_IMPLEMENTATION + SECURITY
Mode: optimize

Selected agents:
→ backend-architect (API design)
→ security-specialist (OAuth2/JWT)
→ testing-specialist (test strategy)
```

### Error Handling

If an agent fails, orchestrator continues gracefully:

```
Agent 1: ✅ Success
Agent 2: ❌ Timeout
Agent 3: ✅ Success

→ Continues with 2 results
→ Notes "Agent 2 unavailable"
→ Still provides actionable output
```

### Resource Management

Orchestrator manages:

- **Token budget:** Prevents context overflow
- **Time budget:** Respects mode time limits
- **Agent limits:** Max 4-6 agents simultaneously
- **Memory:** Efficient result storage

## Best Practices

### When to Use Orchestrator

**Good use cases:**

- Complex multi-faceted tasks
- Production readiness checks
- Comprehensive code reviews
- Architecture decisions

**Not ideal for:**

- Simple single-command tasks
- Quick status checks
- Narrow focused operations

### Mode Selection

- **Daily work:** Use `optimize` mode
- **Troubleshooting:** Use `debug` mode
- **Release prep:** Use `release` mode
- **Quick tasks:** Skip orchestrator, use direct commands

### Monitoring

Always check status for long-running tasks:

```bash
# Start long task
/craft:orch "comprehensive audit" release

# Check progress (separate prompt)
/craft:orch status

# View timeline when complete
/craft:orch timeline
```

## See Also

- **[Commands Reference](commands.md)** - All commands
- **[Skills & Agents](skills-agents.md)** - Agent details
- **[Architecture Guide](architecture.md)** - System design
