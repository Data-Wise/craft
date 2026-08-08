# Remember Plugin Cheat Sheet

Run `claude plugin install remember@claude-plugins-official`, then just work
— it writes session summaries automatically. Ask "what did we do last time"
to read them back.

## What it does

Keeps a rolling, file-based session log per project under `.remember/`, and
injects a summary of recent activity at the start of each new session — no
manual note-taking required.

## Setup

```bash
claude plugin install remember@claude-plugins-official
```

Files it manages, in `.remember/`:

| File | Scope |
|---|---|
| `now.md` | Current session buffer |
| `today-*.md` | Daily log |
| `recent.md` | Last 7 days |
| `archive.md` | Older, compressed |
| `core-memories.md` | Key moments, kept long-term |

## Gotchas

1. **It's a rolling log, not curated memory.** Durable preferences and
   decisions belong in Claude's separate memory system, not here —
   `.remember/`'s older entries are expected to decay/compress over time.
2. **Rotated archives aren't auto-injected.** `archive-YYYY-MM-DD*.md` files
   exist on disk but are NOT loaded into context automatically — grep them
   manually when a question reaches further back than `recent.md` covers.
3. **Search on request only.** Don't assume every past detail is in
   context just because the plugin is active — if you need something
   specific from history, ask explicitly so it greps the archives.
