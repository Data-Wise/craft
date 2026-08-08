# Security Guidance Plugin Cheat Sheet

Run `claude plugin install security-guidance@claude-plugins-official` — it
runs automatically as a hook, no invocation needed.

## What it does

Injects security-review reminders and dual-use-tooling policy (pentesting,
defensive security, CTF, exploit development require clear authorization
context) via a `PreToolUse`/session hook — runs quietly in the background,
not something you call directly.

## Setup

```bash
claude plugin install security-guidance@claude-plugins-official
```

No config — the hook (`hooks/security_reminder_hook.py`) fires on its own
trigger conditions.

## Gotchas

1. **It's a hook, not a skill you invoke.** Don't look for a slash command
   or "ask naturally" trigger — check `ps aux | grep
   security_reminder_hook` to confirm it's actually running if you're
   debugging.
2. **Policy is advisory context, not a hard block.** It shapes how requests
   near the dual-use boundary get framed, but the actual refuse/assist
   decision still comes from the model reading the specific request.
3. **Runs per-session, not per-repo.** It's a user-level hook — expect it
   active in every session on this machine, not scoped to a particular
   project.
