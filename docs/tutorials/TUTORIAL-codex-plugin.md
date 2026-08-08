# Codex Plugin Cheat Sheet

Run `claude plugin install codex@openai-codex`, then ask Claude to "hand this
to Codex" or "get a second implementation pass" when you're stuck.

## What it does

Hands a coding task to OpenAI Codex through a shared runtime, for a second
implementation pass, a deeper root-cause dig, or when Claude Code itself is
stuck. Exposes the `codex:codex-rescue` agent.

## Setup

```bash
claude plugin install codex@openai-codex
```

No further config needed — the plugin starts a broker process per working
directory the first time it's used in that directory.

## Gotchas

1. **One broker per cwd, not global.** Each project directory that uses
   Codex gets its own `app-server-broker.mjs` process with its own Unix
   socket (`/var/folders/.../cxc-*/broker.sock`). Don't expect one broker to
   serve multiple projects.
2. **Brokers linger after use.** They show up in `ps aux` as
   `node .../app-server-broker.mjs serve --cwd <path>` and don't
   auto-exit when idle — check for stray ones with
   `ps aux | grep app-server-broker` if you're auditing background
   processes.
3. **Invoke it by intent, not by name.** Say "get a second opinion from
   Codex" or "this is stuck, hand it off" rather than trying to call the
   agent directly — the `codex-rescue` agent is meant to trigger
   proactively when Claude Code is stuck.
