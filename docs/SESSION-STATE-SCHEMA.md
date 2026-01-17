# Session State Schema - Craft Plugin

**Version**: 1.0.0
**Effective Date**: 2026-01-17
**Purpose**: Define the canonical session state format for orchestration teleportation

---

## Overview

This document defines the JSON schema for orchestration session state, enabling:
- Cross-device session resume
- Session teleportation via Claude Desktop
- Session archival and recovery
- Team collaboration on orchestration

---

## Root Schema

```json
{
  "$schema": "https://data-wise.github.io/craft/schemas/session-state-v1.json",
  "schema_version": "1.0.0",
  "session_id": "string (uuid)",
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp",
  "device": "string (device name)",
  "project": "string (absolute path)",
  "goal": "string (1-sentence task description)",
  "mode": "enum (debug, default, optimize, release)",
  "status": "enum (in_progress, paused, completed, error, aborted)",
  "progress": "float (0.0-1.0)",
  "agents": [],
  "completed_work": [],
  "pending_tasks": [],
  "decisions_made": [],
  "files_modified": [],
  "context_usage": {},
  "teleportation": {},
  "metadata": {}
}
```

---

## Field Definitions

### Core Fields

#### `session_id` (required)
- **Type**: string (UUID v4)
- **Format**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **Purpose**: Unique identifier for the session
- **Example**: `"abc12345-def6-7890-ghij-klmnopqrstuv"`

#### `schema_version` (required)
- **Type**: string (semantic version)
- **Format**: `MAJOR.MINOR.PATCH`
- **Purpose**: Schema version for backward compatibility
- **Example**: `"1.0.0"`

#### `created_at` (required)
- **Type**: string (ISO 8601 datetime)
- **Format**: `YYYY-MM-DDTHH:mm:ss.sssZ`
- **Purpose**: Session creation timestamp (UTC)
- **Example**: `"2026-01-17T14:30:00.000Z"`

#### `updated_at` (required)
- **Type**: string (ISO 8601 datetime)
- **Format**: `YYYY-MM-DDTHH:mm:ss.sssZ`
- **Purpose**: Last modification timestamp (UTC)
- **Example**: `"2026-01-17T14:45:23.142Z"`

#### `device` (required)
- **Type**: string
- **Purpose**: Device name where session was created/last modified
- **Example**: `"MacBook Pro"`, `"iMac"`, `"GitHub Codespace"`

#### `project` (required)
- **Type**: string (absolute path)
- **Purpose**: Project directory absolute path
- **Example**: `"/Users/dt/projects/my-app"`

#### `goal` (required)
- **Type**: string (1-3 sentences)
- **Purpose**: High-level task description
- **Example**: `"Add OAuth 2.0 authentication system with PKCE flow"`

#### `mode` (required)
- **Type**: enum
- **Values**: `debug`, `default`, `optimize`, `release`
- **Purpose**: Execution mode
- **Example**: `"default"`

#### `status` (required)
- **Type**: enum
- **Values**: `in_progress`, `paused`, `completed`, `error`, `aborted`
- **Purpose**: Current session state
- **Example**: `"in_progress"`

#### `progress` (required)
- **Type**: float (0.0-1.0)
- **Purpose**: Overall completion percentage
- **Example**: `0.65` (65% complete)

---

### Agent State

#### `agents` (required)
- **Type**: array of Agent objects
- **Purpose**: Track all agents spawned in session

**Agent Object Schema**:

```json
{
  "id": "string (agent-N)",
  "type": "enum (agent type)",
  "status": "enum (pending, running, completed, error, timeout)",
  "started_at": "ISO 8601 timestamp or null",
  "completed_at": "ISO 8601 timestamp or null",
  "duration_seconds": "integer or null",
  "progress": "float (0.0-1.0) or null",
  "result": "enum (success, failure, timeout, aborted) or null",
  "blocking_on": "string (agent-id) or null",
  "error": {
    "category": "enum (transient, resource, configuration, logical, permanent)",
    "message": "string",
    "retry_count": "integer",
    "last_retry_at": "ISO 8601 timestamp or null"
  } or null,
  "output_summary": "string (concise summary) or null",
  "artifacts": {
    "files_created": [],
    "files_modified": [],
    "files_deleted": []
  }
}
```

**Agent Status Values**:
- `pending`: Not yet started
- `running`: Currently executing
- `completed`: Finished successfully
- `error`: Failed with error
- `timeout`: Exceeded time limit

**Agent Type Values**:
- `feature-dev`
- `backend-architect`
- `bug-detective`
- `code-quality-reviewer`
- `test-specialist`
- `doc-writer`
- Custom agent types

**Example**:

```json
{
  "id": "arch-1",
  "type": "backend-architect",
  "status": "completed",
  "started_at": "2026-01-17T14:30:15.000Z",
  "completed_at": "2026-01-17T14:32:30.000Z",
  "duration_seconds": 135,
  "progress": 1.0,
  "result": "success",
  "blocking_on": null,
  "error": null,
  "output_summary": "OAuth 2.0 architecture designed with PKCE flow",
  "artifacts": {
    "files_created": ["docs/auth-architecture.md"],
    "files_modified": [],
    "files_deleted": []
  }
}
```

---

### Work Tracking

#### `completed_work` (required)
- **Type**: array of strings
- **Purpose**: List of completed tasks (human-readable)
- **Example**:
```json
[
  "Architecture design (OAuth 2.0 with PKCE)",
  "Code stubs created (src/auth/oauth.ts)",
  "Unit tests scaffolded (tests/auth.test.ts)"
]
```

#### `pending_tasks` (required)
- **Type**: array of strings
- **Purpose**: List of remaining tasks
- **Example**:
```json
[
  "Complete code-1 implementation (60% → 100%)",
  "Add unit tests (test-1)",
  "Update documentation (doc-1)"
]
```

#### `decisions_made` (required)
- **Type**: array of Decision objects
- **Purpose**: Track user decisions during orchestration

**Decision Object Schema**:

```json
{
  "timestamp": "ISO 8601 timestamp",
  "context": "string (what decision was about)",
  "options": ["string (option 1)", "string (option 2)"],
  "chosen": "string (selected option)",
  "reasoning": "string (why this choice) or null"
}
```

**Example**:

```json
{
  "timestamp": "2026-01-17T14:32:45.000Z",
  "context": "Authentication method selection",
  "options": ["JWT", "Session Cookies", "Hybrid (JWT + refresh tokens)"],
  "chosen": "Hybrid (JWT + refresh tokens)",
  "reasoning": "Balance of scalability and security"
}
```

---

### File Tracking

#### `files_modified` (required)
- **Type**: array of FileModification objects
- **Purpose**: Track all file changes

**FileModification Object Schema**:

```json
{
  "path": "string (relative to project root)",
  "action": "enum (created, modified, deleted)",
  "agent_id": "string (which agent made change)",
  "timestamp": "ISO 8601 timestamp",
  "lines_added": "integer or null",
  "lines_removed": "integer or null",
  "hash_before": "string (sha256) or null",
  "hash_after": "string (sha256) or null"
}
```

**Example**:

```json
{
  "path": "src/auth/oauth.ts",
  "action": "created",
  "agent_id": "code-1",
  "timestamp": "2026-01-17T14:35:00.000Z",
  "lines_added": 127,
  "lines_removed": 0,
  "hash_before": null,
  "hash_after": "a1b2c3d4e5f6..."
}
```

---

### Context Management

#### `context_usage` (required)
- **Type**: object
- **Purpose**: Track context consumption

**Schema**:

```json
{
  "estimated_tokens": "integer (estimated total tokens)",
  "compression_count": "integer (times compressed)",
  "last_compression": "ISO 8601 timestamp or null",
  "by_agent": {
    "agent-id": "integer (tokens used)"
  }
}
```

**Example**:

```json
{
  "estimated_tokens": 25000,
  "compression_count": 0,
  "last_compression": null,
  "by_agent": {
    "arch-1": 8000,
    "code-1": 12000,
    "test-1": 5000
  }
}
```

---

### Teleportation Metadata

#### `teleportation` (required)
- **Type**: object
- **Purpose**: Session teleportation metadata

**Schema**:

```json
{
  "enabled": "boolean",
  "last_sync": "ISO 8601 timestamp or null",
  "sync_status": "enum (success, pending, error) or null",
  "sync_error": "string or null",
  "devices": ["string (device name)"],
  "storage_backend": "enum (claude-desktop, local, s3)",
  "encrypted": "boolean",
  "shared_with": ["string (email)"] or null
}
```

**Example**:

```json
{
  "enabled": true,
  "last_sync": "2026-01-17T14:45:00.000Z",
  "sync_status": "success",
  "sync_error": null,
  "devices": ["MacBook Pro", "iMac"],
  "storage_backend": "claude-desktop",
  "encrypted": true,
  "shared_with": null
}
```

---

### Additional Metadata

#### `metadata` (optional)
- **Type**: object
- **Purpose**: Custom metadata

**Common Fields**:

```json
{
  "git_branch": "string or null",
  "git_commit": "string (sha1) or null",
  "craft_version": "string (semantic version)",
  "tags": ["string (tag1)", "string (tag2)"],
  "notes": "string or null"
}
```

**Example**:

```json
{
  "git_branch": "feature/auth",
  "git_commit": "a1b2c3d4e5f6...",
  "craft_version": "1.23.0",
  "tags": ["authentication", "oauth2"],
  "notes": "Using PKCE flow per security team recommendation"
}
```

---

## Complete Example

```json
{
  "$schema": "https://data-wise.github.io/craft/schemas/session-state-v1.json",
  "schema_version": "1.0.0",
  "session_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "created_at": "2026-01-17T14:30:00.000Z",
  "updated_at": "2026-01-17T14:45:23.142Z",
  "device": "MacBook Pro",
  "project": "/Users/dt/projects/my-app",
  "goal": "Add OAuth 2.0 authentication system with PKCE flow",
  "mode": "default",
  "status": "in_progress",
  "progress": 0.65,
  "agents": [
    {
      "id": "arch-1",
      "type": "backend-architect",
      "status": "completed",
      "started_at": "2026-01-17T14:30:15.000Z",
      "completed_at": "2026-01-17T14:32:30.000Z",
      "duration_seconds": 135,
      "progress": 1.0,
      "result": "success",
      "blocking_on": null,
      "error": null,
      "output_summary": "OAuth 2.0 architecture designed with PKCE flow",
      "artifacts": {
        "files_created": ["docs/auth-architecture.md"],
        "files_modified": [],
        "files_deleted": []
      }
    },
    {
      "id": "code-1",
      "type": "feature-dev",
      "status": "running",
      "started_at": "2026-01-17T14:33:00.000Z",
      "completed_at": null,
      "duration_seconds": null,
      "progress": 0.6,
      "result": null,
      "blocking_on": null,
      "error": null,
      "output_summary": null,
      "artifacts": {
        "files_created": ["src/auth/oauth.ts"],
        "files_modified": ["src/middleware/auth.ts"],
        "files_deleted": []
      }
    }
  ],
  "completed_work": [
    "Architecture design (OAuth 2.0 with PKCE)",
    "Code stubs created (src/auth/oauth.ts)"
  ],
  "pending_tasks": [
    "Complete code-1 implementation (60% → 100%)",
    "Add unit tests (test-1)",
    "Update documentation (doc-1)"
  ],
  "decisions_made": [
    {
      "timestamp": "2026-01-17T14:32:45.000Z",
      "context": "Authentication method selection",
      "options": ["JWT", "Session Cookies", "Hybrid (JWT + refresh tokens)"],
      "chosen": "Hybrid (JWT + refresh tokens)",
      "reasoning": "Balance of scalability and security"
    }
  ],
  "files_modified": [
    {
      "path": "src/auth/oauth.ts",
      "action": "created",
      "agent_id": "code-1",
      "timestamp": "2026-01-17T14:35:00.000Z",
      "lines_added": 127,
      "lines_removed": 0,
      "hash_before": null,
      "hash_after": "a1b2c3d4e5f6789012345678901234567890abcd"
    }
  ],
  "context_usage": {
    "estimated_tokens": 25000,
    "compression_count": 0,
    "last_compression": null,
    "by_agent": {
      "arch-1": 8000,
      "code-1": 12000,
      "test-1": 5000
    }
  },
  "teleportation": {
    "enabled": true,
    "last_sync": "2026-01-17T14:45:00.000Z",
    "sync_status": "success",
    "sync_error": null,
    "devices": ["MacBook Pro", "iMac"],
    "storage_backend": "claude-desktop",
    "encrypted": true,
    "shared_with": null
  },
  "metadata": {
    "git_branch": "feature/auth",
    "git_commit": "a1b2c3d4e5f6789012345678901234567890abcd",
    "craft_version": "1.23.0",
    "tags": ["authentication", "oauth2"],
    "notes": "Using PKCE flow per security team recommendation"
  }
}
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-17 | Initial schema definition |

---

## Validation

### JSON Schema Validation

```bash
# Validate session file
jsonschema -i session.json schema/session-state-v1.json
```

### Required Field Check

All session files must include:
- ✅ `schema_version`
- ✅ `session_id`
- ✅ `created_at`, `updated_at`
- ✅ `device`, `project`, `goal`
- ✅ `mode`, `status`, `progress`
- ✅ `agents[]`, `completed_work[]`, `pending_tasks[]`
- ✅ `files_modified[]`, `context_usage{}`
- ✅ `teleportation{}`

---

## See Also

- [Session Teleportation Command](../commands/orchestrate/resume.md)
- [Orchestrator v2 Agent](../agents/orchestrator-v2.md)
- [Teleportation Guide](SESSION-TELEPORTATION.md)
