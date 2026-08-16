# OpenCode MCP Bridge Cheat Sheet

Two separate MCP servers let Claude Code delegate work to OpenCode. Ask
Claude to "hand this to OpenCode" or "delegate this to opencode" once
either is installed.

## The two bridges

| Name | Package | Style |
|------|---------|-------|
| `opencode` | `opencode-mcp` (npm) | Synchronous-first — ~80 tools, tiered (`opencode_setup` → `opencode_ask`/`opencode_run` → fine-grained session/message control) |
| `opencode-async` | local build, `~/tools/better-opencode-mcp` | Fire-and-forget — 7 tools (`opencode`, `opencode_sessions`, `opencode_respond`, `opencode_cancel`, `opencode_health`, `ping`, `Help`), built for long-running background tasks |

They are not duplicates: `opencode` covers everything from a one-shot
question to full session management; `opencode-async` is a thin
task-delegation layer (submit → poll `opencode_sessions` → `opencode_respond`
if it asks for input).

## Setup

```bash
# opencode — published npm package
claude mcp add opencode -s user -- npx -y opencode-mcp

# opencode-async — local build
claude mcp add opencode-async -s user -- node ~/tools/better-opencode-mcp/dist/index.js
```

`-s user` registers the server globally (every project, every session).
Drop it (or use `-s project`) to scope a bridge to one repo instead — see
`claude mcp add --help` for the full scope table.

## When to Use Which (routing table)

See [`SPEC-codex-opencode-delegation-2026-08-08.md`](../specs/SPEC-codex-opencode-delegation-2026-08-08.md)
for the full rationale. Quick version:

| Situation | Use | Why |
|---|---|---|
| Faster to just do it yourself | Don't delegate | Round-trip costs more than the task |
| Security / architecture / can't verify the result | Don't delegate | Not verifiable after the fact |
| Hard, well-scoped SWE task | [`codex`](TUTORIAL-codex-plugin.md) | Matches the existing `codex-rescue` trigger |
| One-shot question, need the answer this turn | `opencode` (`opencode_ask`/`opencode_run`) | Sync tier, blocks until done |
| Long task, don't want to block the session | `opencode-async` | Fire-and-forget, poll later |

**Status vocabularies are different between the two bridges — don't conflate them:**
`opencode-async` reports `working` / `input_required` / `completed` / `failed` / `cancelled`;
`opencode`'s `opencode_check` reports `running` / `completed` / `error`.

## Always Monitor a Delegation (mandatory, not optional)

Never fire a delegated task and silently wait. Use a background `Monitor` watching for status
changes, token/cost usage, and errors only — three signals, not raw logs. Copy-paste starting
points:

```bash
# opencode (sync tier) — wrap opencode_ask/opencode_run in a background call,
# then watch its stdout for the terminal "result" line + any error.
# (Called via the MCP tool directly in a live session — this is the CLI-probe
# equivalent for scripting/testing outside a session.)
```

```bash
# opencode-async — poll opencode_sessions for status until terminal:
# working -> completed | failed | cancelled (input_required needs opencode_respond)
```

```bash
# codex — codex exec (--json) already emits JSONL events; filter for the
# terminal event and any "token_count"/usage payloads, e.g.:
codex exec review --json --uncommitted 2>&1 | while IFS= read -r line; do
  case "$line" in
    *'"type":"turn.completed"'*|*'"type":"turn.failed"'*|*'"type":"error"'*|*token*|*usage* )
      echo "[codex] $(echo "$line" | cut -c1-400)" ;;
  esac
done
```

Real token-usage numbers aren't always in the CLI's own event stream — `codex`'s per-turn
usage can read all-zeros while the real total lives in a *child* rollout session file under
`~/.codex/sessions/**/rollout-*.jsonl` (`"type":"token_count"`, look for
`parent_thread_id` matching the review's own `thread_id`). Check there if the inline events
look empty.

## Gotchas

1. **New tool registrations need a session restart.** `claude mcp add`
   writes to `~/.claude.json` immediately, but a *running* Claude Code
   session doesn't pick up the new MCP server until it restarts — the
   tools won't appear via `ToolSearch` mid-session even though `claude mcp
   list` already shows them connected.
2. **`opencode` auto-starts an OpenCode SDK server.** First call spawns
   `OpenCode server ... on 127.0.0.1:4096` if one isn't already running —
   expect a few seconds of latency on cold start.
3. **Always discover providers/models first.** `opencode`'s own
   instructions warn against assuming a provider is available — call
   `opencode_setup` then `opencode_provider_models` before passing
   `providerID`/`modelID` to `opencode_ask`/`opencode_run`, or you may get
   empty responses.
4. **`opencode-async` tasks don't block.** `opencode` (the tool, not the
   server) returns a `taskId` immediately with status `"working"` — poll
   `opencode_sessions` to see completion, and watch for status
   `"input_required"`, which needs `opencode_respond` before the task can
   finish.
5. **Scope check before assuming a bridge is available.** Both were
   originally `local`-scoped to specific project directories (`~/`,
   `savant-openai` for `opencode`; `cc-config`, `better-opencode-mcp` for
   `opencode-async`) before being promoted to `user` scope — if either
   stops showing up, check `claude mcp list` and the project's
   `mcpServers` block in `~/.claude.json` before assuming it's broken.

## Verifying it works

Both servers were smoke-tested directly over stdio (JSON-RPC
`initialize` + `tools/list`, no live session needed):

- `opencode` — responds with 80 tools + a tiered usage guide in the
  initialize response's top-level `instructions` field (a sibling of
  `serverInfo`, not nested inside it); auto-starts its SDK server on port
  4096.
- `opencode-async` — responds with 7 tools (`Help`, `ping`,
  `opencode_health`, `opencode`, `opencode_sessions`, `opencode_respond`,
  `opencode_cancel`).

If you want to re-run the same check: spawn the server's command, write
newline-delimited JSON-RPC to stdin (not LSP-style `Content-Length`
framing — these two don't use it), and read the response from stdout.
