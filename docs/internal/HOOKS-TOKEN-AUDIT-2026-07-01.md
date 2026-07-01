# Hooks Token-Cost Audit — 2026-07-01

**Task:** SPEC-token-efficiency-and-context-tooling-2026-07-01 Part D #2 (linear plan Step 3).
**Method:** measured stdout byte count per hook on its common-case path (the only stdout that enters model context is the token cost). Frequent-path hooks probed with representative stdin JSON; session/stateful hooks measured read-only or by their emit channel. Block-path (rare, intentional) measured separately.
**Scope note:** the levers that matter for *per-turn* cost are hooks on high-frequency events — `PreToolUse`/`PostToolUse` (fire on every matching tool call) and `UserPromptSubmit` (every prompt). `SessionStart` fires once/session; `Stop`/`SessionEnd` fire as the session ends and their stdout does **not** re-enter the ongoing conversation.

---

## Headline

**Craft's own hooks cost 0 tokens per turn on the happy path.** Every craft-owned frequent-path hook (`branch-guard`, `no-switch-guard`, `worktree-status-reminder`, `version-sync-hook`) emits **0 bytes of stdout** when it allows an operation — they speak only when they block, which is rare and intentional. No craft hook needs trimming.

The only measurable per-turn cost among always-on hooks is a **global (non-craft) hook, `prompt-optimizer.sh`**, which also carries a latent JSON-contract bug. That's an external finding, not a craft-repo change.

---

## Measurements

### Craft-owned hooks

| Hook | Event | Owner | Happy-path stdout | Block/active-path | Per-turn token cost |
|---|---|---|---:|---:|---|
| `branch-guard.sh` | PreToolUse `Bash`, `Edit\|Write` | craft (`scripts/branch-guard.sh`, symlinked) | **0 B** | 1188 B on **stderr** + exit 2 (block only) | **0** on allow; block cost is rare + safety-critical |
| `no-switch-guard.sh` | PreToolUse `Bash` | craft (`scripts/no-switch-guard.sh`) | **0 B** | 297 B stdout on block only | **0** on allow |
| `worktree-status-reminder.sh` | PostToolUse `Bash` | craft | **0 B** | — | **0** |
| `version-sync-hook.sh` | PreToolUse `Edit\|Write` | craft | **0 B** | (emits only on version drift) | **0** on allow |
| `session-facet.sh` | SessionEnd | craft (`scripts/install-session-facet.sh`) | **0 B** | writes a facet file, no stdout | **0** (SessionEnd — not injected into ongoing context) |

**Interpretation:** craft's hooks follow the correct pattern for cost — silence on the happy path, output only on the exceptional path. `branch-guard`'s 1188-byte block message is on **stderr with exit 2** (shown to the model as tool-error feedback), fires only when a real violation is caught, and is deliberately verbose because it's safety-critical UX (tells you exactly why the op was blocked and how to proceed). **Keep as-is** — do not trim block-path output.

### Global (non-craft) hooks — context only, not craft's to change

| Hook | Event | Happy-path stdout | Note |
|---|---|---:|---|
| `prompt-optimizer.sh` | UserPromptSubmit | ~62 B (echoes prompt) → **500+ B** on trigger words (`[brainstorm]` etc.) | **Per-turn cost + latent bug** — see below |
| `session-register.sh` | SessionStart | 101 B | Once/session |
| `fix-local-plugins.sh` | SessionStart | 0 B | Once/session |
| `skills-audit.py --write-index` | SessionStart | 0 B (`>/dev/null`) | Once/session |
| `done-reminder.sh`, `session-cleanup.sh` | Stop | n/a | Session ending — no ongoing-context injection |
| `post-compact-reinject.sh` | PostCompact | (fires on compaction only) | Rare |

---

## Actionable finding (external): `prompt-optimizer.sh`

Two issues, both in the **global** `~/.claude/hooks/prompt-optimizer.sh` (not a craft file):

1. **Per-turn echo cost.** On UserPromptSubmit it reads stdin and echoes it back to context on the no-trigger path (`echo "$USER_PROMPT"; exit 0`). Every prompt pays a small duplication cost; on trigger words it injects a multi-hundred-byte template.
2. **Latent JSON-contract bug.** Line 9 is `USER_PROMPT=$(cat)` — it treats the entire stdin as raw prompt text, but Claude Code sends a JSON envelope (`{"prompt":"…","cwd":"…"}`). Observed: the injected brainstorm template embedded the raw JSON (`{"prompt":" new feature","cwd":"…"}`) instead of the extracted prompt. This matches the known craft lesson *"hooks receive JSON on STDIN, not raw text"* — the hook is running on the stale pre-JSON contract.

**Recommendation:** fix or retire `prompt-optimizer.sh` in the user's global `~/.claude/` config (parse `.prompt` from the JSON via `jq`, and emit context only when it actually rewrites the prompt). Out of scope for the craft repo — flagged here because the audit surfaced it while confirming craft's own hooks are clean.

---

## Conclusion

- **No craft hook change needed.** Craft's hooks are token-frugal by design: 0 per-turn stdout on the happy path, verbose only on rare/safety-critical block paths.
- **The per-turn hook cost lives in the global setup**, chiefly `prompt-optimizer.sh` — a personal-config fix, not a craft-repo one.
- This closes SPEC Part D #2. The methodology (measure happy-path stdout as the per-turn cost proxy) is reusable for any future hook added to craft: **a new hook should emit 0 stdout unless it blocks or has something the model must act on.**
