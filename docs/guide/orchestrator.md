# Orchestrator Mode

⏱️ **8 minutes** • 🔴 Advanced • ✓ Power user features

> **TL;DR** (30 seconds)
>
> - **What:** Advanced task orchestrator coordinating multiple agents with 4 execution modes (10s, 2min, 3min, 5min)
> - **Why:** Handle complex multi-step tasks with proper delegation, monitoring, and ADHD-friendly tracking
> - **How:** `/craft:orchestrate "task" [mode]` where mode = default/debug/optimize/release
> - **NEW (v2.5.0):** Use `--orch` flag on supported commands for quick orchestration: `/craft:do "task" --orch=optimize`
> - **Next:** Try `/craft:orchestrate "add auth" debug` for verbose execution tracking

> 🎓 **User Guide** - Practical examples and quick start.
>
> Looking for technical details? See the [**Orchestrator Reference**](../commands/orchestrate.md) for implementation details and advanced features.
>
> **NEW (v2.5.0):** For quick orchestration without a separate command, see the [**--orch Flag Guide**](orch-flag-usage.md) for streamlined usage patterns.

## Overview

The orchestrator coordinates multiple agents and tools for complex, multi-step tasks.

!!! warning "Advanced Feature"
    The orchestrator is powerful but complex. Start with simple commands like `/craft:do` and `/craft:check` first. Come back here when you need parallel agent execution.

**Key Features:**

- Mode-aware execution (default/debug/optimize/release)
- Subagent delegation and monitoring
- Chat compression for long sessions
- ADHD-optimized status tracking
- Timeline view of execution
- Session persistence and resumption (v2.4.0)
- Brainstorm integration for context gathering (v2.4.0)

## Basic Usage

### Traditional Method (v2.4.0 and earlier)

```bash
/craft:orchestrate "implement user authentication"
```

### NEW (v2.5.0): Quick Orchestration with --orch Flag

The `--orch` flag enables orchestration directly from supported commands:

```bash
/craft:do "implement user authentication" --orch=optimize
```

**Supported Commands:**

| Command | Usage |
|---------|-------|
| `/craft:do` | `/craft:do "task" --orch=[mode]` |
| `/craft:workflow:brainstorm` | `/brainstorm "topic" --orch=[mode]` |
| `/craft:check` | `/craft:check --orch=[mode]` |
| `/craft:docs:sync` | `/craft:docs:sync --orch=[mode]` |
| `/craft:ci:generate` | `/craft:ci:generate --orch=[mode]` |

**Benefits:**

- No need to remember separate `/craft:orchestrate` command
- Integrates seamlessly with existing workflows
- Preserves command-specific context and arguments

### Orchestration Modes

| Mode | Max Agents | Compression | Use Case |
|------|------------|-------------|----------|
| `default` | 2 | 70% | Quick tasks |
| `debug` | 1 | 90% | Detailed troubleshooting |
| `optimize` | 4 | 60% | Fast parallel execution |
| `release` | 4 | 85% | Pre-release validation |

### Mode Examples

```bash
# Quick orchestration (default mode)
/craft:do "add validation" --orch

# Verbose debugging
/craft:do "fix the bug" --orch=debug

# Parallel execution (fastest)
/craft:do "implement auth" --orch=optimize

# Pre-release validation
/craft:do "prepare release" --orch=release
```

### Preview Mode (Dry-Run)

Preview orchestration without execution:

```bash
/craft:do "refactor auth" --orch=release --dry-run
```

This shows:

- Task description
- Selected mode
- Max agents
- Compression ratio
- What would be executed

The orchestrator will:

1. Analyze the task
2. Create an execution plan
3. Delegate to appropriate agents/commands
4. Monitor progress
5. Report results

## Modes

### Default Mode (<10s)

Quick orchestration for simple tasks:

```bash
/craft:orchestrate "add validation"
```

### Debug Mode (<120s)

Verbose output with detailed logging:

```bash
/craft:orchestrate "fix the bug" debug
```

### Optimize Mode (<180s)

Parallel execution for speed:

```bash
/craft:orchestrate "implement auth" optimize
```

**Benefits:**

- Runs up to 4 agents in parallel
- Faster completion
- Resource-efficient

### Release Mode (<300s)

Comprehensive audit for releases:

```bash
/craft:orchestrate "prep for v2.0 release" release
```

**Includes:**

- Full test suite
- Documentation validation
- Security checks
- Build verification

## Brainstorm Integration (v2.4.0 NEW)

Orchestrate complex features with structured context gathering:

```bash
/craft:orchestrate "plan new feature"
```

Flow:

1. `/brainstorm d:8` gathers context (requirements, users, scope, technical)
2. Spawns backend-architect agent
3. Spawns frontend specialist
4. Coordinates test strategy
5. Synthesizes into implementation plan

### Custom Brainstorm Context

```bash
# Focused categories for technical features
/craft:orchestrate "design API" optimize
# → Brainstorm d:8 -C tech,requirements

# User-focused for UX features
/craft:orchestrate "design dashboard" optimize
# → Brainstorm d:8 -C users,scope,success

# Risk-aware for critical systems
/craft:orchestrate "implement auth" release
# → Brainstorm d:10 -C req,tech,risk,success
```

## Monitoring

### Status Dashboard

```bash
/craft:orchestrate status
```

Shows:

- Active agents
- Completed tasks
- Pending work
- Resource usage

### Timeline View

```bash
/craft:orchestrate timeline
```

Visual timeline of execution steps.

### Budget Tracking

```bash
/craft:orchestrate budget
```

Context usage and remaining capacity.

## Resuming Sessions

If interrupted, resume with:

```bash
/craft:orchestrate continue
```

The orchestrator maintains state and continues from where it left off.

## Performance Tips

### Choose the Right Mode

| Scenario | Mode | Agents |
|----------|------|--------|
| Simple feature | `default` | 2 max |
| Complex system | `optimize` | 4 parallel |
| Debugging | `debug` | 1 sequential |
| Pre-release | `release` | 4 + audit |

### Reduce Context Usage

1. **Use focused categories**: `/brainstorm d:5 -C req,tech`
2. **Limit question count**: `d:5` instead of `d:20`
3. **Compress early**: Run `compress` at 60% context
4. **Archive completed**: Let auto-save handle checkpoints

## ADHD-Optimized Features

- **Clear status indicators** - Always know what's happening
- **Progress tracking** - See completion percentage
- **Time estimates** - Know how long tasks will take
- **Session state** - Resume interrupted work easily
- **Compressed chat** - Reduces cognitive load in long sessions
- **Visual timeline** - See execution progress at a glance

## Next Steps

- [Skills & Agents](skills-agents.md) - Understanding the system
- [Getting Started](getting-started.md) - Basic usage
- [Brainstorm Command](../commands/workflow/brainstorm.md) - Context gathering (v2.4.0)
- [**NEW** --orch Flag Guide](orch-flag-usage.md) - Quick orchestration (v2.5.0)
