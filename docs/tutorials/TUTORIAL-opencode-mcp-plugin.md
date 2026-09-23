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
| Hard, well-scoped SWE task (deep bug, tricky refactor) | [`codex`](TUTORIAL-codex-plugin.md) | Same task shape the `codex` plugin's `codex-rescue` agent targets — but craft shells to `codex exec` directly, never through that agent (different plugin, no cross-plugin dispatch) |
| One-shot question, need the answer this turn | `opencode` (`opencode_ask`/`opencode_run`) | Sync tier, blocks until done |
| Long task, don't want to block the session | `opencode-async` | Fire-and-forget, poll later |

**Status vocabularies are different between the two bridges — don't conflate them:**
`opencode-async` reports `working` / `input_required` / `completed` / `failed` / `cancelled`;
`opencode`'s `opencode_check` reports `running` / `completed` / `error`.

## Always Monitor a Delegation (mandatory, not optional)

Never fire a delegated task and silently wait. Every delegation follows the same four steps:

1. **Fire it in the background** — hand the command below to the `Monitor` tool (or run it
   with `run_in_background`), never block the session on it.
2. **Watch 3 signals only** — status change, token/cost usage, error. Nothing else earns a
   notification.
3. **One plain-language line per event** — each template `echo`s a single summary line, never
   the raw JSON.
4. **Report cost + findings together at the end** — the full event log is `tee`d to a file,
   so the answer and the final token/cost numbers come from the same place.

Copy-paste templates — each `echo`s only on a real event, so it costs nothing until something
happens:

### `opencode` sync tier — `opencode run --format json`

Uses the `opencode` CLI directly, so it works even when neither MCP bridge is registered.
Pick a model from `opencode models` (format `provider/model`).

```bash
LOG="${TMPDIR:-/tmp}/opencode-run.jsonl"
opencode run --format json -m opencode/big-pickle "<task>" </dev/null 2>&1 | tee "$LOG" |
while IFS= read -r line; do
  case "$line" in
    '{"type":"step_finish"'*)
      echo "[opencode] step done: $(printf '%s' "$line" | jq -c '{reason: .part.reason, tokens: .part.tokens.total, cost: .part.cost}')" ;;
    '{"type":"error"'*)
      echo "[opencode] ERROR: $(printf '%s' "$line" | jq -r '.error.data.message // .error.name')" ;;
  esac
done
echo "[opencode] exited"
```

End-of-task report (step 4): the answer and the totals, from the same log.

```bash
jq -r 'select(.type=="text") | .part.text' "$LOG"
jq -s '[.[] | select(.type=="step_finish") | .part] | {tokens: (map(.tokens.total) | add), cost: (map(.cost) | add)}' "$LOG"
```

Event shapes (verified 2026-09-23, opencode 1.18.31): top-level `type` is `step_start` →
`text` → `step_finish` on success; `step_finish.part` carries `reason`, `tokens`
(`total`/`input`/`output`/`reasoning`/`cache`) and `cost`. A failure emits a single
`{"type":"error", "error": {"name": …, "data": {"message": …}}}` line and exits 1. Note that
`part.type` uses hyphens (`step-finish`) while the top-level `type` uses underscores
(`step_finish`) — match the top level.

### `opencode-async` — in-session poll (MCP-only)

`opencode-async` has no CLI, so there is nothing for a shell `Monitor` to watch — it is polled
from inside the session:

1. Call `opencode` → returns a `taskId` with status `working`.
2. Call `opencode_sessions` periodically; report only when the status changes.
3. `input_required` → answer with `opencode_respond`, then keep polling.
4. Stop at a terminal status: `completed` / `failed` / `cancelled`.

Not re-verified 2026-09-23: the bridge was not registered on the verifying machine. The status
vocabulary above is from the 2026-08-08 stdio smoke test.

### `codex` — `codex exec --json`

```bash
LOG="${TMPDIR:-/tmp}/codex-exec.jsonl"
codex exec --json "<task>" </dev/null 2>&1 | tee "$LOG" | while IFS= read -r line; do
  case "$line" in
    '{"type":"turn.completed"'*|'{"type":"turn.failed"'*|'{"type":"error"'* )
      echo "[codex] $(echo "$line" | cut -c1-400)" ;;
  esac
done
echo "[codex] exited"
```

For a review, swap `exec "<task>"` for `exec review --json --uncommitted` — and expect a large
bill (one review ran to 1.01M tokens in the 2026-08-08 dogfood run). `</dev/null` matters:
`codex exec` otherwise prints `Reading additional input from stdin...` and can wait on an open
stdin under a background runner.

Real token-usage numbers aren't always in the CLI's own event stream — `codex`'s per-turn
usage can read all-zeros while the real total lives in a *child* rollout session file under
`~/.codex/sessions/**/rollout-*.jsonl` (`"type":"token_count"`, look for
`parent_thread_id` matching the run's own `thread_id`). Check there if the inline events
look empty.

Failure path verified 2026-09-23 (codex-cli 0.156.1): an unsupported model emits
`{"type":"error",…}` lines then `{"type":"turn.failed",…}`, and exits 1 — the filter catches
both. The patterns are anchored to the start of the line on purpose: `item.completed` events can
carry a nested `"type":"error"` for mere warnings (hook-timeout clamping, missing model
metadata), which an unanchored `*"type":"error"*` match would report as failures. `turn.completed`
carries the turn's `usage`. The success path is from the 2026-08-08 run and was not re-verified.

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
