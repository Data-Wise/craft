# SPEC: Orchestrate Token-Efficiency — Deterministic `:workflow` Mode as Default (Parity-Gated)

**Status:** approved (core); **Phase Q (pre-flight quota gate) appended 2026-06-17 — pending review** (feasibility-checked; gate refined via interactive spec review)
**Created:** 2026-06-17
**From Brainstorm:** interactive `/workflow:refine` session — token-usage investigation → measure-first design → "dynamic workflow as default" → **corrected** after a red-team found the platform-engine premise infeasible for craft
**Author:** dt + Claude
**Supersedes:** `SPEC-workflow-as-default-engine-2026-06-17.md` (stub folded in here)

---

## Correction note (read first)

An earlier draft proposed migrating orchestrate's dispatch onto a *platform* `Workflow`
tool with native `agent()` / `schema` / `budget` / `isolation:'worktree'`. **An adversarial
review found this infeasible**: craft is a plugin whose commands are markdown prompts, and it
dispatches subagents **only via the portable Task tool** (`agents/orchestrator.md:84`,
`orchestrator-v2.md:305`). There is **no host `Workflow()` callable** from a craft command
(grep: zero references). The thing called "the workflow engine" in craft is its **own**
construct: `commands/orchestrate/workflow.md` + `skills/orchestration/workflow-engine/` +
`scripts/workflow_parse.py` — a deterministic YAML compiler that **still launches Task
subagents under a Python semaphore**.

This spec therefore targets the **real, feasible** reading of "dynamic workflow as default":
make craft's existing **deterministic `:workflow` mode** the default orchestrate path (where
a workflow can be derived), and earn token savings from how that engine *builds Task prompts*
plus context-floor and cache/model levers.

---

## Overview

Token usage is driven by a structural multiplier — `agents × inherited-context ×
loop-turns` — where each Task subagent re-pays a large context cost and **prompt caching is
the only structural discount**. Worktrees cost **zero tokens** (isolation only).

The remedy, in feasible terms:

1. **Make the deterministic `:workflow` engine the default** orchestrate path where a
   workflow is derivable (spec/ORCHESTRATE plan present), falling back to free-form fan-out
   otherwise. Determinism bounds agent count and turns, which bounds the multiplier.
2. **Lever A — context-floor trim** (docs): shrink the ~5,200-token floor inherited by every
   Task subagent.
3. **Lever B — prompt-trim in the workflow engine** (restored as an explicit, measurable
   lever): the engine composes each Task subagent prompt from a **spec slice + summaries of
   prior outputs**, not the full spec/transcript, and requires concise structured returns.
4. **Lever C — cache + model routing**: byte-stable tool set + batched turns (5-min cache
   TTL) and Haiku for cheap file-scoped subagents.

The default flip is governed by a **parity gate with teeth** (see Phase 3): a *failed* gate
**blocks the flip**, and the comparison controls for cache state.

### Goal & non-goals

- **Goal:** reduce orchestrate token usage; **primary mechanism = `:workflow` mode as default
  (where derivable)**, validated by measured deltas and a real parity gate.
- **Out of scope (explicit, no contradictions):**
  - **Loop/turn caps and budget-cutoff UX — fully out.** craft has *no* budget primitive
    (the platform `budget` referenced earlier does not exist here); we add none.
  - Full agent/skill consolidation beyond the minimum the default-flip requires
    (`orchestrator.md` vs `orchestrator-v2.md`).
  - `/done` CLAUDE.md/memory hygiene → `SPEC-context-floor-hygiene-2026-06-17.md`.

---

## Primary User Story

**As a** craft user running orchestrate on a spec or plan,
**I want** orchestrate to default to the deterministic `:workflow` engine — with
floor-trimmed, prompt-scoped Task subagents and cache-friendly routing —
**so that** structured runs cost measurably fewer tokens, with a proven parity gate and a
fallback to free-form fan-out so I'm never worse off.

### Acceptance Criteria

- Read-only token report attributes real input/output/cache tokens per run and per Task
  subagent, for **both** the fan-out default and the `:workflow` path.
- Documented baseline for one reference task on the **current default (fan-out)**.
- `:workflow`-as-default ships behind a flag and flips **only** after passing the Phase 3
  parity gate; free-form fan-out remains available (and the fallback for non-derivable tasks).
- Levers A and B each show a measured per-agent input-token reduction **against the inherited
  floor baseline** (not vs. full transcript).
- No parser failure can break an orchestrate run (post-hoc, read-only).

---

## Phase Spine & Branch Routing

| Phase | Work | Branch | Why |
|---|---|---|---|
| **0 — Instrument & baseline** | `scripts/orchestrate-token-report.py` (read-only) + run markers (with `engine` field); baseline reference task on the **fan-out** default; confirm `:workflow` produces equivalent behavior on it | **worktree** | New script (blocked on `dev`); marker emission is behavior |
| **A — Context-floor trim** | Trim `MEMORY.md`, root `dev-tools/CLAUDE.md`, `craft/CLAUDE.md` | **`dev` / no-commit** | Outside-repo / existing-file edits → `dev`-safe; ships now |
| **B — Engine prompt-trim** | In `workflow-engine`, build each Task subagent prompt from a spec slice + summarized prior outputs + structured returns | **worktree** | Engine behavior; **explicit measurable lever** |
| **1 — `:workflow` default flip** | Route `/craft:orchestrate` to the `:workflow` engine by default *where derivable*; behind `--engine=workflow\|fanout`; fan-out fallback for free-form | **worktree** | Default/routing change |
| **C — Cache + model routing** | Byte-stable tool set, batched turns, Haiku for cheap file-scoped subagents | **worktree** | Engine config |
| **3 — Parity gate** | Fixed cold-cache A/B (N≥5), report CI; flip default only if gate passes | **worktree** | Decision gate with teeth |

**Consequence:** Lever A ships today on `dev`. Phases 0/B/1/C/3 share one feature worktree
(`feature/orchestrate-workflow-default`).

---

## Phase 0 — Components & Data Flow (engine-agnostic)

### Run markers (reuse `.craft/` infra)

craft's runtime convention is `.craft/` (not `.flow/`), and `.craft/workflow-runs/` already
exists as the workflow engine's per-run cache (gitignored). Markers reuse it:

- **`:workflow` runs:** add the token-marker fields to the **existing**
  `.craft/workflow-runs/<run>/` manifest — no parallel system.
- **fan-out runs:** write `.craft/orchestrate-runs/<run-id>.json`.

Marker fields (both): `{ run_id, command, mode, engine, agents, max_turns, cwd, start_ts,
end_ts }`. `engine` ∈ {`fanout`,`workflow`}; `run-id` = `<start_ts>-<mode>`.

### Parser — `scripts/orchestrate-token-report.py`

Read-only. **Never writes to `~/.claude`.**

1. Resolve transcript dir from `cwd` (`~/.claude/projects/<slug>/`).
2. Slice session JSONL to the marker `[start_ts, end_ts]` window.
3. Sum ground-truth `usage`: `input_tokens`, `output_tokens`,
   `cache_creation_input_tokens`, `cache_read_input_tokens`.
4. Locate `agent-*.jsonl` for per-Task-subagent attribution.
5. Emit per-run totals, per-agent breakdown, **cache-hit ratio**, and (two runs) an
   **engine A/B diff with the cache-controlled metric below**. `--json` for machine output.

### The comparison metric (cost-weighted)

A raw token *sum* misprices the mix — output costs ~5× input, `cache_read` ~0.1×,
`cache_creation` ~1.25× — and raw `input_tokens` is unstable across runs (5-min cache TTL
swings `cache_read` vs `cache_creation`). The parser's A/B mode therefore reports a
**cost-weighted** metric: per-type token counts weighted by published price
(output ≈ 5×, `cache_creation` ≈ 1.25×, `cache_read` ≈ 0.1×, input = 1×), **plus** a **$
estimate** and the **raw per-type counts**. Parity is judged on the cost-weighted number —
both cache-state-robust (cache reads are down-weighted, not ignored) and faithful to actual
spend. Price weights live in a small parser-read table, updatable as pricing changes.

### Ground-truth basis

Claude Code already writes per-message `usage` to `~/.claude/projects/**/*.jsonl` (verified).
Worktrees get their own project dirs; subagents write `agent-*.jsonl`. Phase 0 is a read-only
parser over existing logs — no in-loop telemetry, no OTEL.

---

## Phase B — Engine Prompt-Trim (explicit Lever B)

In `skills/orchestration/workflow-engine/`, change how each Task subagent prompt is composed:

- Pass a **spec slice** (the phase/files for that agent), not the whole spec.
- Pass **summaries** of prior-stage outputs, not full transcripts.
- Require **concise structured returns** so only summaries re-enter the orchestrator context.

**Measurement (honest baseline):** per-agent `input_tokens` minus the inherited
context-floor (Lever A's domain) — so Lever B's win is measured on the *prompt* portion it
actually controls, not conflated with the floor. This keeps Lever B a distinct, provable lever.

---

## Phase 1 — `:workflow` Default Flip (constrained)

**Derivation rule (moderate):**

- Default to the `:workflow` engine when a workflow is **derivable from an existing SPEC or
  ORCHESTRATE plan**, reusing `orchestrate:drive`'s existing phase-derivation — **no new LLM
  pre-pass.**
- **Free-form prompts with no spec/plan fall back to fan-out.** A derivation pre-pass for
  arbitrary tasks is explicitly **out of scope** — it would add tokens and parity risk
  (it could eat the savings and produce a bad workflow).

**Confirm gate (auto-derived vs explicit):**

- **Auto-derived** workflow (from a spec) → **show it and confirm** before running, since the
  derivation can be wrong.
- **Explicit** workflow/ORCHESTRATE-plan file already on disk → **auto-run** (no prompt).
- A flag skips the confirm under auto-mode, consistent with craft's existing confirm-gate /
  auto-mode pattern.

**Flagging & fallback:**

- Behind `--engine=workflow|fanout`; default stays `fanout` until Phase 3 passes.
- Worktrees: orchestrate `--swarm` isolation is unchanged and orthogonal to tokens; not
  required unless agents write the same files in parallel.

---

## Phase 3 — Parity Gate (with teeth)

**Design (controls for the red-team's cache-noise objection):**

- **Paired:** run the *same* reference task on both engines under matched conditions, pairing
  runs so task/condition variance cancels.
- Both arms **cold-cache** (fresh session per run); compare on the **cost-weighted** metric
  (per-type price weights + $ estimate; defined in Phase 0).
- **N = 5 pairs.**

**Estimation, not a significance verdict.** We report graded evidence and magnitudes, and
avoid dichotomous "significant / not":

- **Primary effect size:** the **% reduction in cost-weighted tokens** (and absolute paired
  difference), with a **95% CI** on both.
- **Standardized paired effect size** (Cohen's *dₙ*) with its CI, for comparability across
  reference tasks.
- **Surprisal / S-value** (`S = −log₂ p` against the null of no reduction) reported as
  *bits of evidence* — continuous, **not** thresholded (per the Greenland/Amrhein reform).
- Per-arm spread (min/median/max) so cache-driven variance is visible.

**Flip decision (interval-based, magnitude-aware — both must hold):**

1. **Cost:** the **95% CI for the % reduction in cost-weighted tokens lies entirely above the
   practical floor of 15%** — i.e. we are confident the saving is real *and* materially large
   enough to justify permanent dual-engine maintenance. (Magnitude floor tunable; 15% chosen
   to clear the dual-engine cost.)
2. **Behavior:** equivalent outputs — same files changed, tests green, verify gate passes.
3. **Stability:** no new failure modes across the N pairs.

**Outcome:**

- **CI clears the floor + behavior parity** → flip default to `:workflow` (where derivable);
  keep `--engine=fanout`.
- **CI overlaps/below the floor, or wide/inconclusive** → **the default flip does not ship**;
  `:workflow` remains opt-in; report the estimated effect, its interval, and the surprisal so
  the gap is explicit. A wide or low interval is reported as-is, not spun.

**Gate cost:** ~10 orchestrate runs, **one-time**, for the flip decision — not part of normal
operation.

---

## Dual-Engine Cost (acknowledged)

Making `:workflow` the default does **not** retire fan-out — free-form, non-derivable tasks
still need it, so craft maintains **two dispatch paths** indefinitely. This spec accepts that
cost and does **not** solve it. **Sunset condition (out of scope):** fan-out could be retired
only if `:workflow` gains reliable auto-derivation for free-form tasks — a separate effort,
not promised here.

---

## Validation Protocol & Success Criteria

- **Baseline:** reference task on fan-out → Phase 0 report.
- **Lever A:** trim → re-measure inherited floor + per-agent input tokens.
- **Lever B:** engine prompt-trim → re-measure per-agent *prompt* tokens (floor-subtracted).
- **Lever C:** routing → cache-read ratio up; cheap stages on Haiku.
- **Phase 3:** paired A/B both engines (cold-cache, cost-weighted metric); flip only when the
  95% CI for the % reduction clears the 15% floor.
- **Success (discovered, not pre-set):** each shipped lever has a documented, floor-honest
  delta; the default flips only when the **95% CI for the cost-weighted % reduction lies
  entirely above 15%**, with effect size (Cohen's *dₙ*) and surprisal reported as graded
  evidence.

---

## Testing & Risk

### Tests

- Parser unit tests vs a committed **fixture JSONL** (deterministic, offline), incl. the
  cache-controlled metric.
- Marker-schema test (incl. `engine`).
- Parser **read-only** assertion.
- `:workflow` vs fan-out behavior-parity test on a small fixture task.
- Wire into craft's pytest suite.

### Risks & mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| `:workflow`-as-default changes behavior for tasks that worked under fan-out | Serious | Flag-gated; parity gate (behavior clause); fan-out fallback retained |
| `:workflow` needs a derivable workflow — not all tasks have one | Serious | Default applies only where derivable; explicit fan-out fallback |
| Cache-state noise corrupts A/B | Serious | Paired design + cold-cache arms + cost-weighted metric + effect-size/CI estimation with surprisal (Phase 3) |
| Lever B win conflated with the floor | Minor | Measure floor-subtracted per-agent prompt tokens |
| Dual-path maintenance burden | Minor | Acknowledged; sunset condition stated, not promised |
| JSONL schema is Claude-Code-internal | Minor | Parser fails soft on missing fields |

---

## Documentation & Discoverability

- CHANGELOG entry per phase with measured deltas + parity-gate outcome.
- `scripts/orchestrate-token-report.py --help`; reference from orchestrate docs.
- Update `commands/orchestrate.md` / `workflow.md` / `drive.md`: `--engine`, the
  derivable-vs-fallback rule, and the marker/report.

---

## Phase Q — Pre-Flight Quota Gate (appended 2026-06-17)

A command, `/craft:quota`, that estimates a heavy run's token cost and checks it against the
user's **live** 5-hour and weekly subscription limits, advising **SAFE / TIGHT / DEFER** before
the run starts. Builds directly on Phase 0's cost parser. **Prior art: greenfield** — research
found no integrated quota-aware planning advisor; only manual strategies and the interactive
`/usage` view exist.

### Why a new live-quota source is needed

The native subscription limits (`rate_limits.{five_hour,seven_day}.{used_percentage,resets_at}`)
exist **only in the statusline stdin payload** Claude Code pipes each render (docs:
<https://code.claude.com/docs/en/statusline>). A craft command (a markdown prompt) **cannot read
statusline stdin**, so the live quota must be *persisted* to a file the command can read.

### Components (each independently testable)

1. **rate_limits persister** — a one-line statusline addition (or wrapper) that writes the
   native `rate_limits` to `~/.claude/quota-cache.json` every render, **with a `captured_at`
   timestamp** and keep-last-good on absence. Official field; no Keychain, no endpoint. (Side
   benefit: permanently fixes the stale-cache problem that broke claude-hud's display.)
2. **cost estimator** — reuses Phase 0's parser over **historical** runs to build a
   per-run-type cost-weighted distribution (**median + 5–95% interval**). Run-types are the
   tagged markers (`fanout`, `workflow`); composite estimates compose them (parity gate ≈
   10 × `workflow` run).
3. **`/craft:quota <run-type>`** — joins fresh quota + estimate → reports the estimate, the
   **% of each remaining window** it would consume, the reset times, and a recommendation.
   Advisory (prompts advise, hooks enforce); `--json` output; optional `/craft:check` validator.
4. **flow consumer (cross-project follow-on, NOT in this spec):** `/craft:quota` writes
   `.craft/quota.json`; **flow-cli's `dash`** reads it to show a quota panel and advise
   cross-project ("30% weekly left → do the light task, defer the parity gate"). This belongs
   in flow-cli's own repo as a producer/consumer handoff — craft only **produces** the data.

### Data flow

```
statusline → quota-cache.json (live 5h/weekly % + resets + captured_at)
Phase-0 parser over history → per-run-type cost distribution (median, 5–95%)
        ↓
/craft:quota <run-type>  →  "Parity gate ≈ 11M cw (9–14M); ~9% of remaining weekly,
                              ~31% of 5h. 5h resets 14:20. → SAFE."   + .craft/quota.json
```

### Honest-uncertainty guardrails (from the feasibility check)

- **Stale-quota refusal:** if `quota-cache.json` is older than a threshold or `rate_limits` was
  absent, the gate **declines to advise on stale data** (warns with `captured_at` age) rather
  than silently trusting it — the explicit lesson from the claude-hud staleness failure.
- **Cold-start honesty:** with too little history (`n < K`) the gate reports
  **"insufficient history"** + a wide/unknown interval, never a false-precise point.
- **Mapping scope:** the gate is reliable for **known heavy run-types** (fan-out, `:workflow`,
  parity gate); arbitrary free-form tasks get a **labeled coarse** estimate, not a confident one.

### Tests

- Estimator unit tests vs the Phase-0 fixture history (distribution + interval; cold-start path).
- Persister test: given a stdin payload with `rate_limits`, writes a timestamped cache; given
  one without, keeps last-good and does not fabricate.
- Gate test: stale cache → refuses; fresh cache + estimate → correct % and recommendation.
- `/craft:quota --json` schema test (the contract flow consumes).

### Branch routing

New command + estimator + persister are feature code → **worktree** (shares
`feature/orchestrate-workflow-default` or its own). Estimation-stats framing applies (interval,
not point). The flow consumer is **out of scope** (flow-cli repo).

---

## Dependencies & Sequencing

1. **This spec ships first** (Phase 0 → Levers/Phases → Phase 3 → **Phase Q** quota gate, which
   depends on Phase 0's parser).
2. Then `SPEC-context-floor-hygiene-2026-06-17.md` (sustains Lever A via `/done`; depends on
   Phase 0; unaffected by the default flip — the floor is still inherited by Task subagents).
3. **flow-cli quota consumer** — a cross-project follow-on in flow-cli's repo that reads
   `.craft/quota.json` (Phase Q's output) into `flow dash`. Not implemented here; producer/
   consumer handoff only.
4. `SPEC-workflow-as-default-engine-2026-06-17.md` is **superseded** by this revision.

---

## Revision Note — 2026-06-18 (session-lever reconciliation + Workflow-tool path + default strategy)

**Context:** A separate session configured three Claude Code *session-level* token levers
(`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=55`, `/model opusplan`, and briefly
`CLAUDE_CODE_SUBAGENT_MODEL=sonnet`). Reconciling them against this spec surfaced one
regression, one missed path, and three decisions (taken interactively). Research/analysis
only — no engine code changed by this note.

### Finding 1 — `CLAUDE_CODE_SUBAGENT_MODEL` REGRESSES craft's own routing (resolved)

`agents/orchestrator-v2.md` (Model-routing table, ~L296–303 + spawn syntax ~L310) already
routes per task: **`Explore`/`Bash`/test → haiku**, **`general-purpose`/`Plan` → sonnet**,
passing `"model"` explicitly in each Task call. Claude Code's model resolution order is
**`CLAUDE_CODE_SUBAGENT_MODEL` env var > per-invocation `model` param > frontmatter**. So a
global `CLAUDE_CODE_SUBAGENT_MODEL=sonnet` **overrides craft's `haiku`**, forcing cheap
read-only/test agents *up* to Sonnet (~5× their intended cost). This is the inverse of Lever C.

**Decision:** **Do NOT set `CLAUDE_CODE_SUBAGENT_MODEL` globally.** The env var was reverted at
the session level. craft's per-task routing is finer than any flat global default and is the
correct mechanism. **Implication for Lever C:** Lever C ("Haiku for cheap file-scoped
subagents") is *already implemented* in orchestrator-v2's routing table — Lever C's remaining
work is to ensure the deterministic `:workflow` engine **preserves** per-task model assignment
(haiku/sonnet) when it composes Task calls, and to **never** recommend a global subagent-model
override (it silently defeats this). Ad-hoc main-session agents should pass `model:` explicitly.

### Finding 2 — the main-session `Workflow` tool is a third path this spec's correction scoped out

The Correction note ruled out the platform `Workflow()` because *craft commands (markdown
prompts) can't call it* — correct. But the **main Claude session can**, and it carries the one
structural lever this spec admits craft lacks: a **hard `budget` token ceiling**
(`budget.total` / `budget.remaining()`), plus free JS control flow, per-`agent()`
`model`/`effort`, and `schema`'d concise returns that keep full transcripts out of the
orchestrator context.

**Decision:** Document this as a **flow-level practice, NOT inside craft's dispatch.** Craft's
spec stays scoped to its Task engine (documenting a callable craft can't invoke would re-create
the infeasibility confusion this spec already corrected). The practice, recorded at the session/
flow level: *for a genuinely token-heavy multi-agent job, drive it through the main-session
`Workflow` tool with a `budget` cap, `schema`'d returns, and per-stage haiku/sonnet routing —
rather than craft orchestrate.* The budget ceiling is the win and it lives at the session level.
This remains an unmeasured hypothesis vs. fan-out; a paired cost-weighted A/B (Phase 3 method)
would confirm the magnitude before it becomes a default habit.

### Finding 3 — default orchestrate strategy: decision-rule by task shape

Worktrees (`--swarm`) are **isolation-only — 0 tokens, but also 0 token-savings**; they must
not be defaulted *for token reasons*. Adopted default-selection rule (composable — worktree
isolation overlays either engine):

```
if a SPEC/ORCHESTRATE plan is derivable   → :workflow engine   (bounds agents×turns)
elif agents write conflicting files in parallel → --swarm worktrees (isolation)
else (free-form)                          → fan-out
```

This refines Phase 1's derivation rule with an explicit worktree branch and states plainly that
worktrees are an isolation lever, not a token lever. **Open sub-item (defer):** tighter *task
decomposition* (bounded subtasks) in the default fan-out path is the largest unaddressed driver
of the `agents × context × turns` multiplier — worth its own follow-up; engine choice is
secondary to not over-spawning.

### Net spec deltas

- **Lever C** reframed: already realized in orchestrator-v2 routing; the active risk is a global
  `CLAUDE_CODE_SUBAGENT_MODEL` override — call it out as an anti-pattern; ensure `:workflow`
  preserves per-task model assignment.
- **Phase 1** default rule: add the explicit `:workflow` / `--swarm` / `fan-out` decision tree;
  note worktrees = isolation, not tokens.
- **New (out-of-spec, flow-level):** main-session `Workflow`-tool + `budget`-cap practice for
  heavy jobs; unmeasured — candidate for a Phase-3-style A/B.
- **No change** to Phases 0/A/B/3/Q mechanics.
