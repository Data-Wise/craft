---
description: Resume orchestration session across devices using Claude Desktop session teleportation
category: orchestrate
arguments:
  - name: session-id
    description: Session ID to resume (from /craft:orchestrate:sessions)
    required: false
  - name: sync
    description: Sync session state before resuming
    required: false
    default: true
  - name: device
    description: Source device name (for cross-device resume)
    required: false
---

# /craft:orchestrate:resume - Session Teleportation

Resume orchestration sessions across devices using Claude Desktop's session teleportation feature.

## Usage

```bash
# Resume most recent session
/craft:orchestrate:resume

# Resume specific session by ID
/craft:orchestrate:resume abc123-def456

# Resume session from another device
/craft:orchestrate:resume --device "MacBook Pro"

# Resume without syncing (use local cache)
/craft:orchestrate:resume --sync false
```

## What is Session Teleportation?

**Session teleportation** allows you to:

- Continue orchestration work on different devices
- Resume interrupted sessions after system restart
- Share orchestration state across team members
- Recover from crashed or timed-out sessions

### How It Works

```
Device A (MacBook Pro)
  │
  ├─ User: "/craft:orchestrate add auth"
  ├─ Orchestrator spawns agents
  ├─ Session state saved to .craft/cache/
  │
  └─→ SYNC → Claude Desktop Cloud
      │
      └─→ DOWNLOAD → Device B (iMac)
          │
          └─ User: "/craft:orchestrate:resume abc123"
             └─ Orchestrator loads state, continues work
```

## Session State Format

Sessions are stored in `.craft/cache/orchestration-sessions/`:

```
.craft/cache/orchestration-sessions/
├── abc123-def456.json           # Session metadata
├── abc123-def456/               # Session artifacts
│   ├── agent-outputs/           # Agent results
│   ├── decisions.log            # User decisions
│   └── files-modified.txt       # Changed files
└── index.json                   # Session registry
```

### Session Metadata Schema

```json
{
  "session_id": "abc123-def456",
  "created_at": "2026-01-17T14:30:00Z",
  "updated_at": "2026-01-17T14:45:00Z",
  "device": "MacBook Pro",
  "project": "/path/to/my-app",
  "goal": "Add authentication system",
  "mode": "default",
  "status": "in_progress",
  "progress": 0.65,
  "agents": [
    {
      "id": "arch-1",
      "type": "backend-architect",
      "status": "completed",
      "started_at": "2026-01-17T14:30:15Z",
      "completed_at": "2026-01-17T14:32:30Z",
      "duration_seconds": 135,
      "result": "success"
    },
    {
      "id": "code-1",
      "type": "feature-dev",
      "status": "in_progress",
      "started_at": "2026-01-17T14:33:00Z",
      "progress": 0.6,
      "blocking_on": null
    }
  ],
  "completed_work": [
    "Architecture design (OAuth 2.0 with PKCE)",
    "Code stubs created (src/auth/oauth.ts)"
  ],
  "pending_tasks": [
    "Complete code-1 implementation",
    "Add unit tests",
    "Update documentation"
  ],
  "files_modified": [
    "src/auth/oauth.ts",
    "src/middleware/auth.ts"
  ],
  "context_usage": {
    "estimated_tokens": 25000,
    "last_compression": null
  },
  "teleportation": {
    "enabled": true,
    "last_sync": "2026-01-17T14:45:00Z",
    "sync_status": "success",
    "devices": ["MacBook Pro", "iMac"]
  }
}
```

## Session Sync Process

### Automatic Sync (Default)

Session state syncs automatically via Claude Desktop:

```markdown
## 🔄 SESSION SYNC

**Trigger**: Every agent completion, decision, or error
**Method**: Claude Desktop cloud storage (encrypted)
**Latency**: < 2 seconds (background)

### Sync Events
- ✅ Agent started: abc123-def456
- ✅ Agent completed: abc123-def456
- ✅ Decision made: abc123-def456
- ✅ Error encountered: abc123-def456
- ✅ Session paused: abc123-def456

**Last sync**: 2 seconds ago
**Status**: Up to date on all devices
```

### Manual Sync

Force sync with:

```bash
/craft:orchestrate:sync [session-id]
```

### Sync Conflicts

When sessions conflict (both devices modified):

```markdown
## ⚠️ SYNC CONFLICT DETECTED

**Session ID**: abc123-def456
**Devices**: MacBook Pro, iMac

### Conflict Details
| Property | MacBook Pro | iMac |
|----------|-------------|------|
| Last modified | 14:45:23 | 14:45:31 |
| Progress | 65% | 70% |
| Active agent | code-1 | test-1 |

### Resolution Options
1. **Use MacBook Pro** (local, current device)
2. **Use iMac** (remote, newer timestamp) [RECOMMENDED]
3. **Merge** (combine both sessions)
4. **Cancel** (keep separate sessions)

**Recommendation**: Option 2 (iMac is newer by 8 seconds)

Waiting for your choice...
```

## Resume Workflow

### Basic Resume

```markdown
## 🔄 RESUMING SESSION

**Session ID**: abc123-def456
**Goal**: Add authentication system
**Started**: 15 minutes ago on MacBook Pro
**Progress**: 65% complete
**Current device**: iMac

### Session State
- ✅ Architecture design completed (arch-1)
- 🔄 Code implementation in progress (code-1, 60%)
- ⏸️ Testing pending (test-1, blocked)
- ⏸️ Documentation pending (doc-1, blocked)

### Completed Work
- OAuth 2.0 architecture designed
- Code stubs created in src/auth/

### Next Actions
1. Continue code-1 (60% → 100%)
2. Unblock and run test-1
3. Unblock and run doc-1
4. Final validation

### Context Budget
- Tokens used: ~25,000 (20%)
- Compression: Not needed

**Resuming code-1 on iMac...**
```

### Cross-Device Resume

```markdown
## 📱 CROSS-DEVICE RESUME

**Session ID**: abc123-def456
**Origin**: MacBook Pro
**Current**: iMac
**Sync status**: ✅ Up to date (synced 5s ago)

### Device Compatibility
| Check | MacBook Pro | iMac | Compatible |
|-------|-------------|------|------------|
| Project path | ~/projects/my-app | ~/projects/my-app | ✅ Yes |
| Craft version | 1.23.0 | 1.23.0 | ✅ Yes |
| Git branch | feature/auth | feature/auth | ✅ Yes |
| Dependencies | ✅ Installed | ✅ Installed | ✅ Yes |

**All checks passed. Safe to resume.**

Proceeding with code-1 execution on iMac...
```

## Session Management

### List Sessions

```bash
/craft:orchestrate:sessions
```

```markdown
## 📋 ORCHESTRATION SESSIONS

| Session ID | Goal | Device | Status | Progress | Last Modified |
|------------|------|--------|--------|----------|---------------|
| abc123 | Add auth | MacBook Pro | ⏸️ Paused | 65% | 5 min ago |
| def456 | Fix tests | iMac | ✅ Complete | 100% | 2 hours ago |
| ghi789 | Refactor | MacBook Pro | 🔴 Error | 30% | 1 day ago |

**Total sessions**: 3 (1 active, 1 complete, 1 error)
**Storage**: 12.4 MB (.craft/cache/orchestration-sessions/)
```

### Archive Old Sessions

```bash
/craft:orchestrate:archive [session-id]
```

Archives completed or abandoned sessions:

```markdown
## 📦 SESSION ARCHIVED

**Session ID**: def456
**Goal**: Fix tests
**Status**: Complete
**Duration**: 45 minutes
**Archived to**: .craft/archive/orchestration-def456.tar.gz

**Space saved**: 8.2 MB
**Accessible**: Yes (can unarchive with /craft:orchestrate:unarchive def456)
```

## Configuration

### Enable Session Teleportation

In `.claude/settings.local.json` or project `.craft/config.json`:

```json
{
  "orchestration": {
    "session_teleportation": {
      "enabled": true,
      "auto_sync": true,
      "sync_interval_seconds": 10,
      "storage": "claude-desktop",
      "max_sessions": 10,
      "archive_after_days": 7
    }
  }
}
```

### Teleportation Options

| Option | Default | Purpose |
|--------|---------|---------|
| `enabled` | `true` | Enable session teleportation |
| `auto_sync` | `true` | Sync automatically on state changes |
| `sync_interval_seconds` | `10` | Max time between syncs |
| `storage` | `claude-desktop` | Storage backend (claude-desktop, local, s3) |
| `max_sessions` | `10` | Max concurrent sessions |
| `archive_after_days` | `7` | Archive completed sessions after N days |

### Storage Backends

**1. Claude Desktop (Default)**

```json
{
  "storage": "claude-desktop",
  "storage_options": {
    "encryption": "aes-256",
    "compression": "gzip"
  }
}
```

**2. Local Storage**

```json
{
  "storage": "local",
  "storage_options": {
    "path": "~/.craft/sessions"
  }
}
```

**3. AWS S3**

```json
{
  "storage": "s3",
  "storage_options": {
    "bucket": "my-craft-sessions",
    "region": "us-west-2",
    "encryption": "aws:kms"
  }
}
```

## Security & Privacy

### Encryption

All session data is encrypted at rest and in transit:

```markdown
## 🔒 SESSION SECURITY

**Encryption**: AES-256-GCM
**Key derivation**: PBKDF2 (100k iterations)
**Storage**: Claude Desktop cloud (Anthropic-managed)

### What is encrypted
- Session metadata (goal, progress, decisions)
- Agent outputs and results
- File paths and content hashes
- User decisions and preferences

### What is NOT stored
- Actual file contents (only hashes)
- API keys or secrets
- Passwords or credentials
- Personal data (unless explicitly in session state)
```

### Privacy Controls

```bash
# Disable teleportation for sensitive sessions
/craft:orchestrate --no-teleport "add secret feature"

# Clear all sessions
/craft:orchestrate:clear --confirm

# Export session for manual transfer
/craft:orchestrate:export abc123 --output session.encrypted
```

## Team Collaboration

### Shared Sessions

Enable team collaboration:

```bash
# Share session with team member
/craft:orchestrate:share abc123 --email colleague@example.com

# Accept shared session
/craft:orchestrate:accept def456
```

```markdown
## 👥 SHARED SESSION

**Session ID**: abc123-def456
**Owner**: john@example.com
**Shared with**: alice@example.com, bob@example.com
**Permissions**: read-write

### Collaboration Protocol
- ✅ Multi-device resume
- ✅ Real-time sync
- ✅ Conflict resolution
- ❌ Simultaneous editing (last write wins)

**Current editor**: alice@example.com (iMac, 2 min ago)
**Waiting to edit**: No queue

You can resume this session. Changes will sync to all team members.
```

## Troubleshooting

### Session Not Found

```markdown
## ❌ SESSION NOT FOUND

**Session ID**: abc123-def456
**Device**: iMac

### Possible Causes
1. Session was archived or deleted
2. Session belongs to different project
3. Sync hasn't completed yet

### Solutions
1. **Wait for sync**: Try again in 10 seconds
2. **Force sync**: /craft:orchestrate:sync
3. **Check archived**: /craft:orchestrate:list --archived
4. **Recreate session**: Start new orchestration
```

### Sync Failure

```markdown
## ⚠️ SYNC FAILURE

**Reason**: Network timeout
**Last successful sync**: 5 minutes ago
**Status**: Working offline (local cache)

### Recovery Options
1. **Retry sync**: /craft:orchestrate:sync
2. **Continue offline**: Work will sync when connection restored
3. **Export session**: /craft:orchestrate:export abc123

**Working offline**: ✅ Safe (local state preserved)
**Resume later**: ✅ Yes (sync will resume automatically)
```

## Integration

### With /craft:orchestrate

Session teleportation is automatic:

```bash
/craft:orchestrate "add auth"
# Session state auto-saved and synced

# On different device
/craft:orchestrate:resume  # Continues automatically
```

### With Git Worktrees

Sessions preserve worktree context:

```bash
# On MacBook Pro (worktree: feature/auth)
/craft:orchestrate "implement auth"

# On iMac (same worktree)
/craft:orchestrate:resume  # Checks out same worktree
```

### With CI/CD

Sessions can trigger CI builds:

```bash
# When session completes
/craft:orchestrate "run tests" --on-complete "trigger-ci"
```

## See Also

- `/craft:orchestrate` - Start orchestration
- `/craft:orchestrate:sessions` - List sessions
- `/craft:orchestrate:sync` - Force sync
- `/craft:orchestrate:archive` - Archive sessions
- `/craft:orchestrate:plan` - Generate ORCHESTRATE file from spec, with optional worktree creation
- [Session State Schema](../docs/SESSION-STATE-SCHEMA.md)
- [Teleportation Guide](../docs/SESSION-TELEPORTATION.md)
