# Tutorial: orchestrate:resume — Resume an Orchestration Session

By the end of this tutorial you will have:

- Resumed a paused or interrupted orchestration session by ID
- Synced session state across devices
- Understood how session teleportation works

**Prerequisites:** craft installed, a prior orchestration session that was saved or interrupted.

---

## Step 1: List Available Sessions

Before resuming, see what sessions are available:

```
/craft:orchestrate history
```

Output:

```
Session History
───────────────
# │ Date        │ Goal                              │ Status
──┼─────────────┼───────────────────────────────────┼────────────
1 │ 2026-06-19  │ Add OAuth2 authentication          │ 60% complete
2 │ 2026-06-18  │ Refactor auth middleware           │ complete
3 │ 2026-06-17  │ Generate CI workflow               │ abandoned
```

---

## Step 2: Resume by Session Number

```
/craft:orchestrate:resume --session-id 1
```

Restores the session state and continues from where it was interrupted:

```
Resuming Session #1 — OAuth2 Authentication
─────────────────────────────────────────────
Restored: 3 completed waves
Remaining: Wave 4 (frontend login UI)

Continuing from Wave 4...
  Spawning agent: ui-1 (frontend login component)
```

---

## Step 3: Resume the Most Recent Session

Without `--session-id`, resumes the most recent incomplete session:

```
/craft:orchestrate:resume
```

---

## Step 4: Sync Session State Across Devices

If you started a session on one machine and want to continue on another:

```
/craft:orchestrate:resume --sync
```

Pulls the latest session state from the shared state store before resuming. Requires atlas session sync to be configured.

---

## Step 5: Resume on a Specific Device

For session teleportation — continue an orchestration in Claude Desktop from a Claude Code session:

```
/craft:orchestrate:resume --session-id abc123 --device desktop
```

This packages the session state for handoff to the Claude Desktop environment.

---

## Step 6: Session State Location

Sessions are stored at:

```
.claude/orchestrator-session.json     # Current session
.claude/orchestrator-history/         # Archived sessions
```

---

## What's Next

- Use `/craft:orchestrate continue` (shorthand) in the same session to resume the last saved state
- Use `/craft:orchestrate save` to checkpoint before switching devices
- See [orchestrate workflow tutorial](TUTORIAL-orchestrate-workflow.md) for the full orchestration flow
