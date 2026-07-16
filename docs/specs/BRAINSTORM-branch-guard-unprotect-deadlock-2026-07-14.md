# BRAINSTORM: branch-guard.sh self-blocking deadlock in `/craft:git:unprotect`

**Date:** 2026-07-14
**Depth/Focus:** default / arch
**Status:** Investigated + adversarially reviewed. No fix implemented yet — recommendation below needs a decision before implementation starts.

## Problem

`/craft:git:unprotect` is supposed to bypass branch-guard by writing `.claude/allow-dev-edit` (or `.claude/allow-once` for a single action) after collecting a reason via `AskUserQuestion`. But creating that marker file is *itself* intercepted by branch-guard's own `_confirm()` gate (six call sites — grep `~/.claude/hooks/branch-guard.sh` for `allow-dev-edit`). In a non-interactive/auto-mode session, `_confirm()` degrades to a hard `exit 2` the model cannot resolve, even after a human has already answered `AskUserQuestion` with explicit consent. Reproduced 2026-07-13 in a private research repo on its integration branch.

**What "fixed" looks like:** a non-interactive session running `/craft:git:unprotect` (with consent already collected via `AskUserQuestion`) must be able to actually write `.claude/allow-dev-edit` and proceed — without Claude being able to silently self-grant that bypass with no human ever having agreed to it.

## Investigation Findings

1. **`_confirm()` never emits the real permission protocol.** It does `printf message >&2; exit 2` for both MEDIUM ("ask"/`[CONFIRM]`) and HIGH ("block") tiers — there is no `hookSpecificOutput` JSON on stdout anywhere in the file. The `[CONFIRM]` text is prose the model reads, not a harness-level dialog. Mechanically, "ask" and "block" are identical today: a hard stop with no resolution path.

2. **Claude Code's actual hook protocol supports a real `"ask"` decision**, distinct from `"allow"`/`"deny"`/`"defer"` (source: `code.claude.com/docs/en/hooks`):

   ```json
   {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": "..."}}
   ```

   `"ask"` "escalates to the user with an interactive permission prompt... pauses execution and requires the user to respond yes/no." Its exact behavior in non-interactive/headless sessions is **not documented** — the public docs only say it "likely" falls back to deny or defer.

3. **`/craft:git:unprotect` (`commands/git/unprotect.md`) is deprecated but still the live implementation** (routed to via `skills/dev/git/SKILL.md` Operation 10, "already a thin shim, unchanged"). Its flow: `AskUserQuestion` for a reason → `cat > .claude/allow-dev-edit << 'MARKER' ... MARKER` (heredoc write). Whether this executes via the Bash tool or the Write tool changes which branch-guard handler catches it, but both paths currently hit an unconditional `_confirm "write_guard_bypass"`.

4. **Hooks are stateless per-invocation** — there is no built-in signal visible to `branch-guard.sh` that `AskUserQuestion` already ran and got a real answer this turn. Any such signal would have to be manufactured by the skill itself (a file write) and checked by the hook.

## Options Considered

### Option A — real `"ask"` JSON decision

Change `_confirm()` (for the unprotect call sites) to emit `permissionDecision: "ask"` instead of `exit 2`. Gets a genuine interactive dialog in attended sessions. **Unverified** whether it degrades safely (deny) or unsafely (allow/no-op) in headless/auto-mode sessions — exactly the case in the bug report.

### Option B — nonce-bound skill trust

`/craft:git:unprotect` writes a short-lived, single-use signal (session ID + timestamp) right after `AskUserQuestion` returns; `branch-guard.sh` checks for that exact signal before downgrading the marker-write `_confirm()` to an allow.

### Option C — document the manual-only path

Leave the hook as-is; fix `/craft:git:unprotect`'s own output to say plainly, on first hitting this block in a non-interactive session, that the bypass requires a human running it directly in an interactive terminal — instead of repeating the same blocked command.

**Initial direction from the depth/focus questions:** A+B layered, hook+skill together, with B as the primary mechanism (deterministic, testable) and A as the fallback for attended sessions with no valid nonce.

## Adversarial Security Review (agent-skills:security-auditor)

Full design (A+B layered) reviewed against the invariant this hook exists to protect: **Claude must never be able to silently self-grant a branch-protection bypass with no human having actually consented.**

**Verdict: fundamentally flawed as specified.** Findings, most severe first:

- **[CRITICAL] The Option-B consent file has no binding to `AskUserQuestion` actually having fired.** `.claude/.unprotect-consent` is an ordinary file Claude can write directly with the same Bash/Write tool access the "skill" would use — `printf '%s' "$CLAUDE_SESSION_ID" > .claude/.unprotect-consent` requires no `AskUserQuestion` call at all. Nothing distinguishes "the skill wrote this after a real human answer" from "Claude decided to." **This makes Option B strictly worse than the status quo** — today Claude is stuck (safe failure); under B, Claude can unstick itself with zero human involvement.
- **[HIGH] `$CLAUDE_SESSION_ID` provides no authentication value** — it's an ambient value available to the same process that would forge the consent file, not a secret held by a separate trust boundary. Comparing "value Claude wrote" against "value Claude also knows" is a format check, not consent proof.
- **[HIGH] Option A's headless-mode behavior is unverified and, if it degrades to allow/no-op instead of deny, reopens the hole across every `_confirm()` call site** in the file (force-push, `reset --hard`, `.env` edits, `clean -f`), not just the unprotect path — because `_confirm()` is the shared helper for all of them.
- **[HIGH] The consent-file pattern is a template other call sites will copy without the same scrutiny** — this codebase has already been bitten by "marker file = implicit trust" once (the H1 hardening at section 8e that stops `allow-dev-edit` from silently bypassing catastrophic checks).
- **[MEDIUM] TOCTOU on the read-then-delete nonce check** — not using an atomic consume (`mv`/`flock`) could let one nonce cover more than the intended single write if PreToolUse hooks for concurrent tool calls race.
- **[MEDIUM]** TTL/mtime spoofing is moot given the CRITICAL finding, but noted for completeness.
- **[LOW]** `session_id` extraction from the PreToolUse stdin payload is asserted, not confirmed — the hook's current `_json_get` calls never read `.session_id` today.
- **Confirmed clean:** the catastrophic-ops checks (section 8d: `rm -rf .git`, `git branch -D`) run unconditionally before any marker/protection-level gate and have no code path back into the proposed consent logic — this part of the design doesn't need to change.

**Reviewer's reframing of the real question:** *is there any Claude-Code-harness-level primitive that can record "a human answered `AskUserQuestion`" somewhere Claude itself cannot write?* If yes, bind Option A/B to that instead of a session ID Claude already knows. If no such primitive exists, the honest fix is not a new bypass path — it's making the *hard* block resolvable only by a genuinely out-of-band human action (the user runs a command themselves outside the Claude Code tool surface, or a Claude Code native permission-prompt UI element the model cannot programmatically approve).

## Revised Recommendation

1. **Drop Option B (file-based nonce) entirely as specified.** It provides no security value over the status quo and is disqualified by the CRITICAL finding — do not build it.
2. **Empirically verify Option A's headless-mode behavior before deciding anything else.** Concretely: add a throwaway `_confirm()`-style test hook emitting `permissionDecision: "ask"`, trigger it from a genuinely non-interactive/auto-mode session (reproduce the original repro conditions), and observe whether the tool call proceeds, is denied, or hangs. This single test resolves the open question the whole design currently hinges on.
   - **If "ask" safely denies (or hangs/times out — not allows) in headless mode:** ship Option A, scoped *narrowly* to the `allow-dev-edit`/`allow-once` marker-write call sites only — not globalized to every `_confirm()` site (per the HIGH finding on scope creep). In attended sessions this gives a real human-clickable dialog Claude cannot forge (an actual harness-rendered permission prompt is not writable by the model, unlike a file). In headless sessions it safely falls back to blocked — which is the correct behavior per Option C below, just automatic instead of requiring a docs fix.
   - **If "ask" behaves unsafely or unpredictably in headless mode:** do not ship Option A either. Fall through to Option C.
3. **Ship Option C's messaging fix regardless of what Option A verification finds**, since it's low-risk and directly improves the failure mode for the case that stays blocked: on first hit of this block in a session, `/craft:git:unprotect` should say plainly *"this bypass requires a human running it directly in an interactive `claude` terminal — it cannot complete from here,"* instead of Claude silently repeating the same blocked command (as happened in the original reproduction).

## Test Plan

| Tier | Coverage | N/A reason |
|---|---|---|
| e2e | Reproduce the exact deadlock in a scratch repo (or the original private repro repo) before the fix; confirm resolution after | — |
| dogfood | Run `/craft:git:unprotect` end-to-end in both an interactive and a genuinely headless/auto-mode session post-fix | — |
| unit | N/A — the fix is a conditional branch inside existing shell functions, covered by e2e | No new parser/script |
| integration | Add a regression test to `craft`'s existing branch-guard test suite (`tests/test_branch_guard.sh` or equivalent) asserting the `allow-dev-edit`/`allow-once` marker-write path resolves correctly under the chosen mechanism, without weakening the 8d catastrophic-checks tests | — |
| dependency | N/A | No external dependency touched |
| count-cascade | N/A | Not a new command/skill/agent |

Stubs should be written red-first (failing placeholder) once the Option-A verification result is known — don't scaffold tests against an unverified assumption about headless "ask" behavior.

## Documentation

- `docs/guide/guard-design.md` — needs a note on the resolved mechanism once implemented (score ≥3 per doc-scorer: behavior change to a documented guard).
- `docs/reference/claude-code-instruction-enforcement.md` — currently only documents `permissionDecision: "deny"`; add `"ask"`/`"defer"` once Option A's headless behavior is verified, since this doc is the canonical local reference for hook JSON control and is already stale on this point.
- `commands/git/unprotect.md` / `skills/dev/git/SKILL.md` — update Step 3/Operation 10 with whichever mechanism ships, plus the Option-C messaging fix.
- `N/A — score <3`: refcard, demo, mermaid diagram (no new user-facing command surface, no new visual flow).

## Suggested Next Command

`/craft:grill` on the empirical question in Recommendation step 2 (does `permissionDecision: "ask"` deny safely in headless mode?) before writing any code — this is a factual unknown, not a design tradeoff, and the whole recommendation branches on its answer.
