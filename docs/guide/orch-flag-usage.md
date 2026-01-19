# Using the --orch Flag for Quick Orchestration

**Added in**: v2.5.0
**Status**: Stable

## Overview

The `--orch` flag provides a shorthand for spawning the orchestrator without requiring a separate `/craft:orchestrate` command invocation. This enables quick orchestration for complex tasks directly from any supported command.

## Supported Commands

| Command | Use Case |
|---------|----------|
| `/craft:do` | Universal task routing with orchestration |
| `/craft:workflow:brainstorm` | Parallel context gathering with orchestration |
| `/craft:check` | Orchestrated validation workflows |
| `/craft:docs:sync` | Multi-agent documentation updates |
| `/craft:ci:generate` | Complex CI workflow generation |

## Usage Patterns

### Basic Usage

```bash
# Enable orchestration with interactive mode selection
/craft:do "implement user authentication" --orch

 Orchestration Mode Selection
==================================================

Available modes:
  default   - Quick tasks (2 agents max, 70% compression)
  debug     - Sequential troubleshooting (1 agent, 90% compression)
  optimize  - Fast parallel work (4 agents, 60% compression)
  release   - Pre-release audit (4 agents, 85% compression)

[AskUserQuestion prompt appears]
```

### Explicit Mode Selection

```bash
# Specify mode directly
/craft:do "add payment integration" --orch=optimize

# Different modes for different scenarios
/craft:do "debug authentication flow" --orch=debug
/craft:do "prepare release v2.0" --orch=release
/craft:do "quick refactor" --orch=default
```

### Preview Mode (Dry-Run)

```bash
# Preview orchestration without executing
/craft:do "refactor auth module" --orch=release --dry-run

+---------------------------------------------------------------------+
| DRY RUN: Orchestration Preview                                      |
+---------------------------------------------------------------------+
| Task: refactor auth module                                          |
| Mode: release                                                       |
| Max Agents: 4                                                       |
| Compression: 85%                                                    |
+---------------------------------------------------------------------+
| This would spawn the orchestrator with the above settings.          |
| Remove --dry-run to execute.                                        |
+---------------------------------------------------------------------+
```

### Combining with Other Flags

```bash
# Brainstorm with categories
/craft:workflow:brainstorm "authentication" -C req,tech --orch=optimize

# Pre-release checks
/craft:check --for release --orch=release

# Documentation sync with orchestration
/craft:docs:sync --orch=default
```

## Orchestration Modes

| Mode | Max Agents | Compression | Best For |
|------|------------|-------------|----------|
| `default` | 2 | 70% | Quick tasks, simple orchestration |
| `debug` | 1 | 90% | Sequential troubleshooting, detailed analysis |
| `optimize` | 4 | 60% | Fast parallel work, maximum throughput |
| `release` | 4 | 85% | Pre-release audit, comprehensive validation |

### Mode Descriptions

- **default**: Quick tasks with 2 agents max and 70% compression. Ideal for most orchestration needs.
- **debug**: Sequential troubleshooting with 1 agent and 90% compression. Best for detailed, step-by-step analysis.
- **optimize**: Fast parallel work with 4 agents and 60% compression. Maximum throughput for time-sensitive tasks.
- **release**: Pre-release audit with 4 agents and 85% compression. Comprehensive validation before releases.

## When to Use --orch

### Use --orch When:

1. **Complex multi-step tasks** that require coordination across multiple agents
2. **Cross-category work** spanning code, docs, and CI
3. **Time-sensitive tasks** where parallel execution is beneficial
4. **Pre-release validation** requiring comprehensive checks
5. **Research and investigation** tasks needing multiple perspectives

### Alternative: Complexity-Based Routing

The orchestrator is automatically triggered for high-complexity tasks (score 8-10) via `/craft:do`. Use `--orch` for:

- Explicit control over orchestration mode
- Lower-complexity tasks that would benefit from orchestration
- Situations where you want orchestration regardless of complexity score

## Examples

### Feature Development

```bash
# Quick orchestration for feature work
/craft:do "add OAuth2 authentication with PKCE flow" --orch=optimize
```

### Debugging Complex Issues

```bash
# Detailed debugging with sequential agents
/craft:do "investigate performance bottleneck in database queries" --orch=debug
```

### Release Preparation

```bash
# Comprehensive release validation
/craft:check --for release --orch=release

# Or directly
/craft:do "prepare v2.0 release" --orch=release
```

### Documentation Updates

```bash
# Orchestrated documentation sync
/craft:docs:sync --orch=default
```

### CI Workflow Generation

```bash
# Complex CI configuration with orchestration
/craft:ci:generate --orch=optimize
```

## Troubleshooting

### Common Issues

**"Invalid mode" error**
```
Error: Invalid mode: 'fast'. Valid modes: default, debug, optimize, release
```
Make sure to use one of the valid mode names.

**Orchestrator not spawning**
Ensure `--orch` flag is present and the command supports orchestration.

**Mode prompt not appearing**
If you specify `--orch` without a mode, the mode selection prompt should appear automatically.

### Getting Help

- Run `/craft:check` before committing to validate your changes
- Use `--dry-run` to preview orchestration without execution
- Check CLAUDE.md for workflow guidance

## Integration with Other Features

### Works With

- **Complexity Scoring**: `--orch` overrides complexity-based routing
- **Dry-Run Mode**: Preview orchestration with `--dry-run`
- **Categories Flag**: Combine with `-C` for focused orchestration (brainstorm)
- **Context Detection**: Orchestrator receives full context from command

### Backward Compatibility

The `--orch` flag is opt-in and doesn't affect existing workflows. Commands work normally without the flag.

## Performance Considerations

| Mode | Estimated Overhead | Use When |
|------|-------------------|----------|
| default | ~1-2 seconds | Quick orchestration needed |
| debug | ~2-3 seconds | Detailed analysis required |
| optimize | ~1 second | Speed is priority |
| release | ~3-5 seconds | Thorough validation needed |

## Next Steps

1. Start with `/craft:do "task" --orch=optimize` for most use cases
2. Use `--dry-run` to preview before executing
3. Try `--orch=debug` for complex debugging scenarios
4. Use `--orch=release` before major releases

For more information, see:
- [Complexity Scoring Algorithm](../guide/complexity-scoring-algorithm.md)
- [Orchestrator Command](../commands/orchestrate.md)
- [Version History](../VERSION-HISTORY.md)
