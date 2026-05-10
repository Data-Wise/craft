---
name: session-state
description: This skill should be used when the user asks to "save session", "resume session", "continue where I left off", "session history", or needs orchestrator session state persistence including save, load, resume, and history management.
category: orchestration
---

# Session State Manager

Handles persistent state for orchestrator sessions, enabling resume after disconnects.

## State File Location

```
.claude/orchestrator-session.json     # Current session (project-local)
.claude/orchestrator-history/         # Session history (project-local)
  └── 2025-12-27-abc123.json         # Archived sessions
```

## Session State Schema

```json
{
  "schema_version": "1.0",
  "session_id": "2025-12-27-abc123",
  "created": "2025-12-27T10:30:00Z",
  "updated": "2025-12-27T11:45:00Z",
  "project": {
    "name": "my-project",
    "path": "/path/to/my-project",
    "git_branch": "dev"
  },
  "goal": "Add sensitivity analysis to RMediation::medci()",
  "mode": "default",
  "status": "in_progress",
  "agents": [
    {
      "id": "arch-1",
      "type": "arch",
      "task": "Design sensitivity API",
      "status": "complete",
      "started": "2025-12-27T10:30:00Z",
      "completed": "2025-12-27T10:32:00Z",
      "result_summary": "3 methods proposed: bootstrap, delta, MCMC",
      "context_tokens": 1500
    },
    {
      "id": "code-1",
      "type": "code",
      "task": "Implement primary method",
      "status": "in_progress",
      "started": "2025-12-27T10:32:00Z",
      "progress": 60,
      "context_tokens": 3200
    }
  ],
  "completed_work": [
    {
      "task": "Architecture design",
      "outcome": "3 methods proposed",
      "files": ["R/sensitivity.R"]
    }
  ],
  "pending_tasks": [
    "Complete code-1 implementation",
    "Add unit tests",
    "Update documentation"
  ],
  "decisions_made": [
    {
      "decision": "Use bootstrap for confidence intervals",
      "rationale": "Best balance of accuracy and performance",
      "timestamp": "2025-12-27T10:31:00Z"
    }
  ],
  "context_usage": {
    "estimated_tokens": 25000,
    "percentage": 20,
    "last_compression": null
  },
  "errors": []
}
```

## Operations

### Save Session

Called automatically on:

- Agent completion
- User says `save`
- Before compression
- On abort

```python
def save_session(state: dict) -> Path:
    """Save current session state."""
    state["updated"] = datetime.now().isoformat()

    session_file = Path(".claude/orchestrator-session.json")
    session_file.parent.mkdir(exist_ok=True)
    session_file.write_text(json.dumps(state, indent=2))

    return session_file
```

### Load Session

Called when user says `continue`:

```python
def load_session() -> Optional[dict]:
    """Load existing session if available."""
    session_file = Path(".claude/orchestrator-session.json")

    if not session_file.exists():
        return None

    state = json.loads(session_file.read_text())

    # Validate schema version
    if state.get("schema_version") != "1.0":
        return None  # Incompatible version

    return state
```

### Archive Session

Called on session completion or new session start:

```python
def archive_session(state: dict) -> Path:
    """Move session to history."""
    history_dir = Path(".claude/orchestrator-history")
    history_dir.mkdir(exist_ok=True)

    archive_file = history_dir / f"{state['session_id']}.json"
    archive_file.write_text(json.dumps(state, indent=2))

    # Remove current session file
    Path(".claude/orchestrator-session.json").unlink(missing_ok=True)

    return archive_file
```

### List History

```python
def list_history(limit: int = 10) -> list[dict]:
    """List recent sessions."""
    history_dir = Path(".claude/orchestrator-history")

    if not history_dir.exists():
        return []

    sessions = []
    for f in sorted(history_dir.glob("*.json"), reverse=True)[:limit]:
        state = json.loads(f.read_text())
        sessions.append({
            "id": state["session_id"],
            "goal": state["goal"],
            "status": state["status"],
            "created": state["created"]
        })

    return sessions
```

## Resume Flow

When user says `continue`:

```markdown
## 🔄 RESUMING SESSION

**Session ID**: 2025-12-27-abc123
**Goal**: Add sensitivity analysis to RMediation::medci()
**Started**: 2 hours ago
**Progress**: 60% complete

### Completed Work
- ✅ Architecture design (3 methods proposed)
- ✅ Test stubs created

### In Progress
- 🔄 code-1: Implement primary method (60%)

### Pending
1. Complete code-1 implementation
2. Add unit tests
3. Update documentation

### Context Budget
- Tokens used: ~25,000 (20%)
- Last compression: Never

**Resuming from code-1...**
```

## State Transitions

```
┌─────────────────────────────────────────────────────────┐
│                    Session Lifecycle                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [new task] ──► CREATED ──► IN_PROGRESS ──► COMPLETE   │
│                    │              │             │       │
│                    │              │             ▼       │
│                    │              │         [archive]   │
│                    │              │                     │
│                    │              ▼                     │
│                    │          PAUSED ◄── [disconnect]  │
│                    │              │                     │
│                    │              ▼                     │
│                    │         [continue]                 │
│                    │              │                     │
│                    │              ▼                     │
│                    └────► IN_PROGRESS                   │
│                                                         │
│  [abort] ──► ABORTED ──► [archive]                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Auto-Save Triggers

| Event | Action |
|-------|--------|
| Agent starts | Update state, save |
| Agent completes | Update result, save |
| Agent fails | Log error, save |
| Decision made | Log decision, save |
| User says `save` | Force save |
| Compression | Save before compress |
| Session end | Archive |

## Error Recovery

If session file is corrupted:

```markdown
## ⚠️ SESSION RECOVERY

The previous session file appears corrupted.

**Options**:
1. **Start fresh**: Begin new session (old state lost)
2. **View history**: Check archived sessions
3. **Manual recovery**: I'll try to extract what I can

Which would you prefer?
```

## Integration with Orchestrator

The orchestrator calls session state operations at key points:

```python
# On startup
if args == "continue":
    state = load_session()
    if state:
        resume_from_state(state)
    else:
        print("No session to resume")

# On task analysis
state = create_new_session(goal, mode)
save_session(state)

# On agent completion
update_agent_status(state, agent_id, "complete", result)
save_session(state)

# On shutdown
if status == "complete":
    archive_session(state)
else:
    save_session(state)  # Keep for resume
```
