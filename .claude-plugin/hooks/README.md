# Craft Plugin Hooks

This directory contains hook scripts that execute during agent lifecycle events.

## orchestrate-hooks.sh

Agent-scoped hooks for orchestrator-v2 that provide:

- **Resource monitoring**: Track active agents and enforce limits
- **Session logging**: Record agent start/completion times
- **Result caching**: Save agent results for reuse
- **State persistence**: Save orchestration session state

### Hook Events

| Event | When | Actions |
|-------|------|---------|
| **PreToolUse** | Before agent starts | Check resource limits, log start |
| **PostToolUse** | After agent completes | Log completion, update cache |
| **Stop** | Orchestration ends | Save session state, cleanup |

### Resource Limits by Mode

| Mode | Max Concurrent Agents |
|------|----------------------|
| debug | 1 (sequential) |
| default | 2 |
| optimize | 4 |
| release | 4 |

### Generated Files

```
.craft/
├── logs/
│   └── orchestration.log           # Agent activity log
└── cache/
    ├── agent-*.status              # Individual agent status
    ├── agent-results.cache         # Agent results for reuse
    └── last-orchestration.json     # Session summary
```

### Example Session Summary

```json
{
  "timestamp": "2026-01-17T14:30:00-08:00",
  "total_agents": 3,
  "mode": "default",
  "agents": [
    {
      "agent": "arch-1",
      "status": "completed",
      "start_time": "2026-01-17T14:25:00-08:00",
      "end_time": "2026-01-17T14:27:15-08:00",
      "duration_seconds": 135,
      "mode": "default"
    },
    {
      "agent": "code-1",
      "status": "completed",
      "start_time": "2026-01-17T14:27:20-08:00",
      "end_time": "2026-01-17T14:29:45-08:00",
      "duration_seconds": 145,
      "mode": "default"
    }
  ],
  "log_file": ".craft/logs/orchestration.log"
}
```

### Hook Configuration

Hooks are configured in `.claude-plugin/plugin.json` (future):

```json
{
  "hooks": {
    "PreToolUse": {
      "command": "/bin/bash .claude-plugin/hooks/orchestrate-hooks.sh",
      "scope": "agent",
      "agents": ["orchestrator-v2"]
    },
    "PostToolUse": {
      "command": "/bin/bash .claude-plugin/hooks/orchestrate-hooks.sh",
      "scope": "agent",
      "agents": ["orchestrator-v2"]
    },
    "Stop": {
      "command": "/bin/bash .claude-plugin/hooks/orchestrate-hooks.sh",
      "scope": "agent",
      "agents": ["orchestrator-v2"]
    }
  }
}
```

### Testing

Test the hook script manually:

```bash
# Test PreToolUse
HOOK_EVENT=PreToolUse TOOL_NAME=test-agent CRAFT_MODE=default \
  bash .claude-plugin/hooks/orchestrate-hooks.sh

# Test PostToolUse
HOOK_EVENT=PostToolUse TOOL_NAME=test-agent DURATION=42 \
  bash .claude-plugin/hooks/orchestrate-hooks.sh

# Test Stop
HOOK_EVENT=Stop AGENT_COUNT=3 \
  bash .claude-plugin/hooks/orchestrate-hooks.sh

# View logs
cat .craft/logs/orchestration.log

# View session summary
cat .craft/cache/last-orchestration.json | jq .
```

## See Also

- `/craft:orchestrate` - Multi-agent orchestration
- `agents/orchestrator.md` - Orchestrator agent documentation
- Claude Code 2.1.0 hook documentation
