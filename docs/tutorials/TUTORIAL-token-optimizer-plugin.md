# Token Optimizer Plugin Cheat Sheet

Run `claude plugin install token-optimizer@token-optimizer`, then use its
`smart_*` MCP tools in place of raw Bash/Read for large or repeated file
operations.

## What it does

Wraps common dev operations (read, grep, glob, git, tests, lint, and more)
in cached/diffed MCP tools that cut token usage on large or repeated reads.
Claude Code will proactively suggest one — e.g. "Consider the smart_read MCP
tool (cached/diffed) to save tokens" — when you `Read` a large file.

## Setup

```bash
claude plugin install token-optimizer@token-optimizer
```

No config needed — the MCP server registers ~60 `smart_*` tools
automatically (smart_read, smart_grep, smart_edit, smart_test, smart_git,
and more).

## Gotchas

1. **Only worth it for large/repeat operations.** A one-off read of a small
   file gets no benefit from the caching layer — the tip only fires on
   large files for a reason.
2. **Tool surface is large.** ~60 `smart_*` tools plus analytics/cache-admin
   tools (`cache_audit`, `token_audit`, `waste_audit`) — use `ToolSearch` to
   find the right one rather than guessing names.
3. **Cache staleness is possible.** If a file changed outside Claude Code's
   awareness (another process wrote it), the cached read could be stale —
   fall back to a plain `Read` if something looks wrong.
