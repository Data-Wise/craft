---
title: "Tutorial: Insights SessionEnd Hook Setup"
description: "Install the SessionEnd facet hook so every session writes a baseline insights record automatically"
category: "tutorial"
level: "beginner"
time_estimate: "5 minutes"
related:
  - TUTORIAL-insights-workflow.md
  - ../guide/insights-improvements-guide.md
---

# Insights SessionEnd Hook Setup

> **Time:** 5 minutes | **Level:** Beginner | **Prerequisites:** Craft plugin loaded

## What This Does

The SessionEnd hook writes a shallow facet file at the end of every Claude Code
session. This gives the insights system a baseline record even when you do not
run `/done` at the end of a session.

## Install

```bash
bash scripts/install-session-facet.sh
```

The installer:

1. Copies `hooks/session-facet.sh` to `~/.claude/hooks/`
2. Registers it under `SessionEnd` in `~/.claude/settings.json` (idempotent — safe to run again)

## What Gets Written

Each session produces one file at `~/.claude/usage-data/facets/session-<id>.json`:

```json
{
  "session_id": "...",
  "timestamp": "2026-06-24T10:00:00Z",
  "project": "craft",
  "branch": "feature/my-feature",
  "goal_category": "unknown",
  "outcome": "session-end",
  "friction_events": [],
  "auto_collected": true
}
```

Deduplication is per-session-id: a second `SessionEnd` for the same session
(e.g., after a reconnect) is a no-op.

## Hook vs `/done` Fidelity

| Signal | Source | AI-enriched? | Fields populated |
|--------|--------|-------------|-----------------|
| SessionEnd hook | Automatic | No | session_id, project, branch, timestamp |
| `/done` command | Manual | Yes | All fields including goal_category, friction_events, outcome |

The hook provides **baseline coverage** — every session has some data. `/done`
provides **rich data** when you close a session intentionally. Both write to the
same `facets/` directory; `/done` produces a timestamped file, the hook a
session-id-named file.

## Verify

After your next Claude Code session ends, check:

```bash
ls ~/.claude/usage-data/facets/session-*.json
```

You should see one file per session.
