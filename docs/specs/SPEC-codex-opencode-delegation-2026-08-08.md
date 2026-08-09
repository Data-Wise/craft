# Codex/OpenCode Delegation Routing — Spec

**Generated:** 2026-08-08 · **Status:** draft — reviewed
**Sources:** [`BRAINSTORM-codex-opencode-delegation-2026-08-08.md`](BRAINSTORM-codex-opencode-delegation-2026-08-08.md) ·
[`GRILL-codex-opencode-delegation-2026-08-08.md`](GRILL-codex-opencode-delegation-2026-08-08.md) (5 branches locked)

---

## TL;DR

3 delegation tools installed (`codex`, `opencode`, `opencode-async`), zero guidance on which
one to use, no way to watch cost or status while a delegated task runs. This spec adds both:
a short routing table + a mandatory "always monitor" step.

## Problem

3 delegation surfaces, no documented rule for which to use, no budget/failure guardrails.
Each tool's own docs cover *how* to call it — none cover *when*, or how to watch it while it
runs (tonight's session had to hand-build a token/status monitor from scratch each time).

## Routing Table (the core deliverable)

| Situation | Use | Why |
|---|---|---|
| Faster to just do it yourself | **Don't delegate** | Round-trip costs more than the task |
| Security / architecture / can't verify the result | **Don't delegate** | Not verifiable after the fact |
| Hard, well-scoped SWE task (deep bug, tricky refactor) | `codex` | Same shape of task the `codex` plugin's own `codex-rescue` agent proactively targets — craft calls `codex exec` directly, not that agent (different plugin, no cross-plugin dispatch) |
| One-shot question, need the answer this turn | `opencode` (`opencode_ask`/`opencode_run`) | Sync tier, blocks until done |
| Long task, don't want to block the session | `opencode-async` | Fire-and-forget, poll later |

## Mandatory: Monitor Every Delegation (new — the ADHD-friendly part)

Never fire-and-forget silently. Every delegation gets a live status+token watch, using the
`Monitor` pattern already proven tonight (codex + opencode reviews were both watched this way):

1. **Fire the call in the background** — never block the session on a delegated task.
2. **Watch for 3 things only** — status change, token/cost usage, error/failure. Nothing else
   is worth a notification (matches ADHD rule: filter to signal, not raw logs).
3. **One summary line per event** — what happened, in plain language, not raw JSON.
4. **Report cost + findings together at the end** — see tonight's side-by-side table
   (codex: 1.01M tokens; opencode/deepseek-v4-pro: 1,555 tokens, ~650× cheaper **by token
   count** on the same task) as the model for what "done" looks like. Caveat: that 650×
   figure compares tokens, not dollars — codex ran on a flat subscription (sunk cost),
   `opencode-go` bills per call. Token count is still a real signal (context pressure, rate
   limits), just don't read it as "codex costs 650× more in cash."

This closes the gap the Problem section names — "no way to watch cost while it runs" — as a
required step, not an afterthought.

## Decisions (from BRAINSTORM answers + this review)

| # | Decision |
|---|---|
| D1 | Only the 3 installed tools — no new tooling evaluation this pass |
| D2 | Must work standalone today AND be structured for a future skill to consume |
| D3 | Routing table above (corrected post-review — brainstorm had 2 factual bugs, both fixed) |
| D4 | Flexible timeline, quality over speed |
| D5 | **Monitoring is mandatory**, not optional — see section above (elevated from "budget practice" to a concrete required step this rewrite) |
| D6 | OpenCode's two bridges use **different** status words — don't conflate them: `opencode-async` = `working`/`input_required`/`completed`/`failed`/`cancelled`; `opencode` = `running`/`completed`/`error` |
| D7 | `--delegate` defaults **OFF** wherever it ships — matches `--refine`'s OFF-default precedent for execution-engine commands. Delegation costs real money/tokens and hits a network dependency; it must never fire silently. |
| D8 | Any future command implementing `--delegate` **must** ship a test asserting its dispatch path includes a status/token check — same enforcement pattern as `--refine`'s `test_refine_default_policy_table_exhaustive`. Doc-only guidance isn't enough (craft's own hooks-as-defense-in-depth precedent). |
| D9 | **Scope narrowed (2026-08-08, post-grill):** only 2 use cases move forward — adversarial review and brainstorm research. The 4-command `--delegate` rollout below is parked, not cancelled. |

## Use Cases (narrowed scope — 2 in, 4 parked)

### 1. Adversarial review — `arch:review`

Already dogfooded tonight (both reviewers, on this exact spec's source docs). `arch:review`
is the one command that gets `--delegate` now: routes to `opencode` (sync tier,
`opencode_ask`/`opencode_run`) for a cheap second opinion, `codex` available as an explicit
override for a deeper pass. Same routing-table row and monitoring requirement (D5/D8) as
before — narrowing is about *which commands*, not the routing/monitoring design itself.

### 2. Brainstorm research

The `brainstorm` skill's existing "Research Findings (web)" step (used tonight via
`WebSearch`) gets an optional escalation: when a topic needs deeper investigation than a web
search provides, delegate to `opencode`/`codex` the same way, still monitored per D5. Not a
new command — an enhancement to `skills/workflow/brainstorm/SKILL.md`'s existing research
step.

### Parked (not built, not cancelled)

`code:debug`, `code:refactor`, `code:test-gen`, `ci:triage` — all 4 were scoped and grilled
(GRILL Branches 1 and 3 apply to them), but user chose to limit rollout to the 2 use cases
above for now. Revisit this list before building any of them; nothing here expires.

**Explicitly excluded (not just parked):** `orch`, `orch:drive`, `orch:workflow`. These already
run their own native multi-agent delegation (wave checkpoints, model routing,
confirm-before-spawn). Adding external delegation here would recreate the exact anti-pattern
the `--refine`/brainstorm redesign already removed once — "one delegation mechanism, not two"
(see `skills/workflow/brainstorm/SKILL.md`'s "Going Deeper" section).

## Scope

**In:**

- One guidance doc: routing table + monitor-every-delegation step + the two-vocabulary note.
- Placement: fold into the existing 2 tutorials (`TUTORIAL-opencode-mcp-plugin.md`,
  `TUTORIAL-codex-plugin.md`), cross-linked — cheapest option, no new skill needed for a doc
  this short.
- A copy-paste `Monitor` command template for each of the 3 tools (codex, opencode sync,
  opencode-async), so "watch this delegation" isn't rebuilt from scratch again.

**Out:**

- The 4 parked commands (`code:debug`, `code:refactor`, `code:test-gen`, `ci:triage`) — scoped
  and grilled, not built (D9).
- A working `arch:review --delegate` / brainstorm-escalation dispatch implementation — D2 only
  needs the rule structured for future use; this pass is docs + design, not code.
- Evaluating tools beyond the 3 installed.
- Wiring `orchestrate-dispatch`'s existing hang/budget detection onto these external tools —
  real gap, real follow-up, not this spec.

## Acceptance Criteria

- [ ] Routing table + monitor-every-delegation step live in both tutorials (or one shared
      location both link to)
- [ ] A ready-to-copy `Monitor` template exists for all 3 tools
- [ ] Two-vocabulary note present and correct (guards against reintroducing finding F2)
- [ ] `arch:review`'s eventual `--delegate` flag defaults OFF (D7), enforced by a test once
      built (D8) — the brainstorm-research escalation (use case 2) has no flag to default,
      it's a skill-internal choice already gated by the skill's own interactive flow
- [ ] `markdownlint` + `mkdocs build --strict` clean

## Test Plan

| Tier | Status |
|---|---|
| e2e / dogfood | N/A — doc-only change, no new command/skill |
| everything else | N/A — no code, no parser, no data flow |

## Next

1. Implement into the 2 tutorials + Monitor templates.
2. Verify acceptance criteria.
3. `/craft:finish` — closes tonight's delegation-tooling thread.
