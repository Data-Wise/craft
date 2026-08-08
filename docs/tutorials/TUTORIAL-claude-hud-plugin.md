# Claude HUD Plugin Cheat Sheet

Run `claude plugin install claude-hud@claude-hud`, then restart your Claude
Code session to pick up the new status line.

## What it does

A live status-line/dashboard process that surfaces session state (context
usage, git branch, active task) at a glance, without asking.

## Setup

```bash
claude plugin install claude-hud@claude-hud
```

Restart the session after install — the status line process
(`claude-hud`) needs a fresh session start to attach.

## Gotchas

1. **Runs as a background process per session.** Check `ps aux | grep
   claude-hud` if the status line isn't showing up — a stale or crashed
   process won't restart itself mid-session.
2. **Statusline config lives outside this plugin.** If the HUD content
   looks wrong (missing fields, wrong format), check your Claude Code
   statusline settings separately — this plugin supplies data, not the
   full rendering config.
3. **One instance per open session.** Multiple concurrent sessions each get
   their own HUD process — don't expect a single shared dashboard across
   sessions.
