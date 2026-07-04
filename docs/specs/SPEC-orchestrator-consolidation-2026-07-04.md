# SPEC-C — Orchestrator Consolidation & Platform-Grounding

> **Repo:** `~/projects/dev-tools/craft` · **Branch:** `dev` · **Date:** 2026-07-04
> **Status:** Scoped, not yet implemented. This spec is the "future larger renaming +
> hardening + refactoring effort" that `SPEC-planning-refactor-2026-06-22.md` was paused
> into on 2026-07-04 — its scope was undefined then; it is defined here now. No code
> changes shipped by this spec itself.
> **Absorbs:** `SPEC-planning-refactor-2026-06-22.md` A2–A8 (the flag/boundary
> consolidation half) and the `.STATUS` 2026-07-04 backlog entry "Investigate default
> agent-dispatch behavior re: stray/leaking background processes" (the dispatch-safety
> half). Both are closed into this spec rather than left as separate open items.
> **Scope:** craft-internal planning/orchestration/execution surface only — no platform
> or upstream changes are made here (see §7 Non-Goals for the one escalation
> recommendation), no cross-plugin material (stays in SPEC-A).

---

## 0. Objective

Two problems, scoped together because they share root cause and files:

1. **Boundary clarity** — `/craft:plan`-family (do/orchestrate/plan:*) commands and
   skills have drifted flags and responsibilities since
   `SPEC-planning-refactor-2026-06-22.md` was written; give them one predictable entry
   point and unambiguous per-intent ownership (continuing that spec's own objective,
   §0 there).
2. **Dispatch safety** — craft's bespoke `orchestrate-dispatch` background-agent mode
   was built on an unvalidated token-savings premise, using a mechanism (manual
   backgrounding) the platform has since made a default, with a safety net
   (concurrency cap, hang detection) that turns out to be non-enforcing prose. Right-size
   it against what the platform actually provides today.

Both are informed by four research tracks run 2026-07-04 (§1–§4 below), then combined
into one action list (§5) so files touched by both problems (none currently overlap, but
sequencing matters — see §8) aren't edited twice independently.

## 1. Track 1 — Flags & Boundaries Audit

Full agent report, condensed. Builds on `SPEC-planning-refactor-2026-06-22.md` without
re-deriving its decision ledger (§1), collision register C1–C7 (§3), or ADR (§5) —
extends it with what changed or was missed.

### 1.1 Flag inventory & conflicts

| Command/skill | Flags it owns |
|---|---|
| `do` | `task`, `--dry-run`/`-n`, `--orch`, `--orch-mode`, `--refine` (default **ON**)/`--no-refine`, `--brief` |
| `orchestrate` | `task`, positional `mode`, `--dry-run`/`-n`, `--swarm`, `--refine` (default **OFF**), `--engine`, `--no-clarify`, `--yes`/`--non-interactive` |
| `orchestrate/drive` | `spec`, `-n`, `--yes`/`-y`, `--max-turns`, `--no-auto`, `--agents`, `--condition` |
| `orchestrate/workflow` | `workflow`, `-n`, `--resume`, `--refine` (default **OFF**) |
| `orchestrate/plan` | `spec-path`, `--output` |
| `grill` | `target`, `--bound`, `--no-capture`, `--yes`, `--refine` (ON, topic-scoped) |
| `plan/feature` | `--refine` (ON), `--no-tests`, `--no-docs` |

**Conflicts found (new, beyond C1–C7):**

1. **`--refine` default is genuinely inconsistent** — ON for `do`/`grill`/`plan:feature`,
   OFF for `orchestrate`/`workflow`. Same flag name, opposite default, no documented
   rule for why.
2. **`--yes` is used in `do.md`'s body (L48-49) but never declared in its frontmatter.**
3. **`--plan` on `/do` is spec'd** (`SPEC-planning-refactor-2026-06-22.md` §4 rule 4:
   "`/do --plan X` is pure sugar forwarding to `/craft:plan X`") **but unimplemented** —
   no such arg exists in `commands/do.md` today.
4. **`mode` is positional on `orchestrate` but `--orch-mode` is a flag on `do`** — three
   spellings of the same 4-value enum (`default`/`debug`/`optimize`/`release`) across
   `do`, `orchestrate`, and `~/projects/dev-tools/craft/CLAUDE.md`'s own table.

### 1.2 Boundary map

Clean separations confirmed: brainstorm (divergent → SPEC), grill (convergent → GRILL
ledger), plan-orchestrator (committed artifacts), the drive/workflow engines. **Two real
bleeds found:**

- **project-planner bleeds into plan-orchestrator** — see 1.3, C1-residual.
- **Intent classification has two owners** — `task-analyzer` (skill) claims activation
  "when the user invokes /craft:do" and owns Workflow Selection, while `do.md`
  independently hardcodes the same category/complexity tables inline. They can drift
  from each other with no shared source.

### 1.3 New findings beyond C1–C7

- **C1-residual (the strongest finding):** `SPEC-planning-refactor-2026-06-22.md` marks
  C1 "✅ RESOLVED 2026-07-03." True only for `skills/planning/SKILL.md`'s frontmatter
  description. Its **body** — Capabilities (L22-52), Outputs (L64-71), Integration
  (L80-87) sections — still teaches artifact-production language A1 was supposed to
  strip. This is the exact body/frontmatter-drift class that spec's own §12 takeaway
  warned future A-items to check for, reintroduced in the very next skill.
- **C2-new:** the verify-gate detection table is triplicated verbatim across
  `drive-engine:34-40`, `workflow-engine:103-109`, `plan-orchestrator:207-215`.
- **C3-new (re-verified during adversarial review, 2026-07-04):** `session-state`'s
  resume/archive/history contracts are for **orchestrator-v2 session state**
  (`.claude/orchestrator-session.json`, triggered by "resume session" /
  "continue where I left off") — confirmed still live and functional, **not** wired to
  the deleted `orchestrate:resume` slash command (`grep` for
  `orchestrate:resume`/`orchestrate/resume.md` in `session-state/SKILL.md` returns
  nothing). The actual problem is narrower than first stated: not a dead-docs surface,
  but a **confusing name overlap** — a reader could reasonably assume `session-state`'s
  "resume" capability is the deleted command's replacement, when it's an unrelated,
  always-functioning mechanism.
- **C4-new (a live three-way contradiction):** `commands/plan/feature.md:19-20` carries
  `deprecated: true`, continuously, since 2026-05-14. Since then it gained active
  features (#215's `--refine` arg, #216's scaffolding defaults). Tests enforce it as
  live (`test_craft_plugin.py:583`, `test_plugin_dogfood.py:426`,
  `test_scaffold_defaults_e2e.py:17`). And `SPEC-planning-refactor-2026-06-22.md` §11
  declared it "NOT deprecated" — a factual claim that turns out to be wrong; the
  `deprecated: true` flag is still literally present in the file. Three sources
  disagree with each other and with the file itself.
- **C5-new:** `plan/sprint.md` (108 lines) / `plan/roadmap.md` (116 lines) are still
  full-length bodies, not thin alias stubs — confirms A3 (from the paused spec) remains
  unfinished, independently of this new spec.
- **C6-new:** the 4-value mode enum (`default`/`debug`/`optimize`/`release`) is
  duplicated across `do`, `orchestrate`, and `CLAUDE.md`, not sourced from a single
  `skills/modes` reference.

### 1.4 Proposed refactoring (net-neutral-to-reducing, per this spec-family's own

honesty convention — §0 of the original spec explicitly rejected "consolidate for its
own sake")

| # | Action | Resolves |
|---|---|---|
| D3 | Fix `project-planner`'s **body** (Capabilities/Outputs/Integration) to strategy-only language, mirroring what A1 already did to its frontmatter | C1-residual |
| D2 | Resolve the `plan/feature.md` contradiction — **recommended: un-deprecate it** (remove `deprecated: true` at L19-20; it's cheaper than editing three test files to stop enforcing it as live) | C4-new |
| D1a | Finish A3 (shrink `plan/sprint.md`/`plan/roadmap.md` to real thin stubs) | C5-new, closes paused-spec A3 |
| D1b | Land A2 (`/craft:plan` deterministic repo-state router) — only after D1a, per the paused spec's own A2-after-A3 sequencing (§13 there) | paused-spec A2 |
| D4 | Consolidate the triplicated verify-gate table (`drive-engine`, `workflow-engine`, **and** `plan-orchestrator` — all three sites named in C2-new) into one new shared reference file, `skills/orchestration/references/verify-gate-detection.md` | C2-new |
| D6 | Normalize `--refine` default: **ON** for deliberation-entry commands (`do`, `plan:*`, `grill`), **OFF** for execution engines (`orchestrate`, `workflow`) — state the rule once in the `prompt-refiner` skill, reference it from each command instead of repeating a bare "default: on/off" | Conflict 1.1.1 |
| D5 | Collapse `do.md` ↔ `task-analyzer` dual intent-routing ownership — pick one source (recommend: `task-analyzer` skill owns the category/complexity tables, `do.md` calls it rather than duplicating the tables inline) | 1.2 bleed |
| D9 | Dedupe the mode enum (`default`/`debug`/`optimize`/`release`): `skills/modes/SKILL.md` (the `mode-controller` skill) **already exists and already owns the canonical definitions** — `do.md`, `orchestrate.md`, and `CLAUDE.md` each independently hardcode their own copy instead of referencing it. No new file needed; just point the three duplicates at the existing skill. | C6-new |
| D10 | Rename or annotate `session-state`'s "resume" language to avoid the name collision with the deleted `orchestrate:resume` command — the mechanism itself is confirmed fine (see C3-new's revised note, §1.3), this is a documentation clarity fix, not a functional change | C3-new |
| D7 | Set a **new, concrete deprecation horizon** for `plan/sprint.md`/`plan/roadmap.md` (the original v2.50.0 target already passed at v2.59.0) | C5-new (horizon-setting only — see D8 for actual removal) |
| D8 | **Execute** the horizon D7 sets: delete `plan/sprint.md` and `plan/roadmap.md` once it passes. This is the item that actually removes the 2 files — D7 alone only schedules a date, it does not perform a deletion. Contingent/deferred: runs later than the rest of this list, once the horizon arrives. | C5-new follow-through (the actual fix) |

**Net effect (revised 2026-07-04 after adversarial review — the original "nets to
reduction" framing didn't hold up):**

- **+1 file** — D4's new `verify-gate-detection.md` reference file (the original spec
  undercounted this: it credited D4 as part of a "−2" figure that was actually about
  D8's deletions, not D4's own file cost).
- **+1 command** — D1b's `/craft:plan` router (assuming it's a genuine new command file,
  not merely an alias inside `do.md` — this spec doesn't fully resolve that ambiguity;
  flagged for the implementing session to confirm before counting it either way).
- **−2 files** — D8's deletions, but **only once D8 actually executes**, which is
  contingent on the horizon D7 sets, not immediate. Until then this is +2 pending, not
  banked.
- **D9, D10, D6, D5, D3, D2** have no file-count effect — they edit existing files in
  place.

**Honest bottom line: net 0 (not a reduction) once D8 eventually executes; net +2 in the
interim between D7 firing and D8 executing.** This revises the original spec's
overstated "nets to reduction, unlike the original action list" — the corrected framing
is closer to "flat, with a deferred cleanup," which is still a fair outcome (the
original planning-refactor spec's action list only ever added), just not the clean win
first claimed.

**Suggested order:** D3 → D2 → D1a → D4/D6/D9/D10 → D5 → D1b → D7 → D8 (D8 last and
deferred — it depends on D7's horizon actually arriving, not on the other items; D1b
still last-before-D7/D8 since it depends on D1a and benefits from D5/D6 being settled
first).

## 2. Track 2 — Orchestrate-Dispatch Reliability Audit

Full agent report, condensed. All line refs are `skills/orchestration/plan-orchestrator/SKILL.md`
unless noted.

### 2.1 Mechanism as designed

`orchestrate-dispatch` is the third `output` value of Mode 1 (Spec → ORCHESTRATE),
added #240/v2.57.0, designed by `SPEC-orchestrate-dispatch-mode-2026-07-01.md`. Flow:
GRILL-file precondition (warn-only, L66-70) → confirm-before-dispatch `AskUserQuestion`
gate, unconditional even under `--yes` (L72-82) → dispatch a background `Agent` with a
fixed self-containment prompt: *"Read `ORCHESTRATE-<topic>.md` in full, then execute
it."* — no other context (L84-91).

**Caps/timeouts that exist today — all prose-level, none executable:**

- **Concurrency cap:** soft cap of 2 concurrent `orchestrate-dispatch` dispatches **per
  session** (L97-105) — an in-context running tally the LLM maintains by tagging each
  dispatch's `description`, not a system-enforced semaphore.
- **Hang-detection window:** `2 × the ORCHESTRATE file's own stated phase-effort
  estimate` (L116-122) — read from the Phase Overview table, mapped to wall-clock via
  "the same effort→duration mapping the session already uses." No fixed constant, no
  timer.
- **Failure detection:** cross-check the `Agent` completion notification against the
  ORCHESTRATE file's checkboxes (L107-114). Notification with no checkbox movement =
  suspected silent failure; no notification within the window = surface a hang. Both
  are **reports to the user**, not kills.
- **Resumability:** idempotent re-dispatch driven by the file's own checkbox state
  (L130-137) — genuinely craft-specific value, no platform equivalent.
- **`.STATUS` auto-write:** only factual fields (branch, worktree path, PR link)
  (L139-143).

**Confirmed by grep:** no `TaskStop`, `pkill`, `pgrep`, `kill`, or timer machinery
anywhere in `skills/orchestration/`. Even `orchestrator-resilience/SKILL.md`'s sections
titled "Timeout Handling," "Force terminate," "Circuit Breaker" (L53-118) are markdown
display templates the LLM prints — narrative text, not a syscall.

### 2.2 Concrete failure modes

1. **Parent session ends/crashes before the background agent completes — nothing tracks
   or reaps the orphan.** Every cap/timeout above is executed by the orchestrating
   session's own LLM. If that session dies, the watcher dies with it — same underlying
   exposure as the `.STATUS` 2026-07-04 example (a `while true` loop from a separate
   Claude Desktop/Cowork session, still running 6.5+ hours later, PID 45054). craft's
   design is *somewhat* safer (bounded phase-work by construction, not an intentional
   infinite loop) but has **no structural orphan bound**.
2. **Hang past the 2×-window produces a report, not a kill.** L113-114/L124-128: "surface
   the crash/hang case explicitly," "never auto-delete the worktree or branch... add a
   `.STATUS` note." No `TaskStop`/kill step exists.
3. **Cross-session interference is real and unguarded.** The concurrency cap is
   per-session (L97) — two craft sessions each independently allow 2 dispatches, no
   shared counter. `.STATUS` auto-writes race with no locking. Worktree path is
   deterministic from topic (`~/.git-worktrees/<project>/feature-<topic>`, L47) — two
   sessions dispatching the same topic collide. The v2.57.0 `.STATUS` milestone already
   records a live near-miss: *"recovered a killed agent's completed-but-uncommitted
   Phase 3 work."*
4. **Does the savant `while true` leak reproduce identically?** No — craft never emits
   an infinite polling loop; dispatched work is finite phase-list execution. But the
   *governing property* that let the savant loop leak — "persists until the owning
   session ends or is explicitly stopped, nothing bounds it if the owner goes away" —
   is unaddressed by craft's design too.

### 2.3 Root cause tie-in (Track 4)

The entire premise for building this bespoke mechanism — "save tokens vs. N
cold-started sessions" — was never measured, and the mechanism it credits
(warm-session context reuse) doesn't require backgrounding specifically; a synchronous
foreground `Agent` call gets the same benefit (see §4). Combined with §3's finding that
the platform now backgrounds subagents by default with completion notifications, the
custom concurrency-cap/hang-detection layer is solving a problem the platform has
already absorbed, while providing none of the enforcement it implies.

### 2.4 Decision: simplify toward platform-native (confirmed direction, 2026-07-04)

- **Drop/shrink:** the manually-maintained concurrency-cap tally (L97-105), and
  `orchestrator-resilience`'s "Timeout/Force terminate/Circuit Breaker" templates
  (L53-118) *where they overlap platform-native background-agent handling*. Replace with:
  rely on the platform's default background execution and
  `agent_completed`/`agent_needs_input` notification hooks (confirmed live as of
  2026-07-01, see §3) instead of re-implementing a supervision loop in prose.
  **Clarification added 2026-07-04 (adversarial review finding #4):** the hang-detection
  window's *formula* (L116-122, `2 × phase-effort estimate`) is **not** part of this drop
  — it survives as the ledger sweep's overdue-threshold input (§2.5 needs exactly this
  number to know what "past its expected window" means). What's actually dropped is only
  the *active, in-session polling/reporting behavior* built on top of that formula (the
  live session babysitting a dispatch and self-reporting a hang) — the platform's
  notification hooks replace that active loop, not the threshold math itself.
- **Keep — genuinely craft-specific, no platform equivalent:**
  - The confirm-before-dispatch human gate (L72-82) — a deliberate, non-suppressible
    checkpoint before handing off to an unsupervised agent.
  - The ORCHESTRATE self-containment prompt guarantee (L84-91) — the dispatched agent's
    entire context is the durable file, matching STOP-new-session mode's own guarantee.
  - Resumability via checkboxes (L130-137) — file-driven idempotent re-dispatch.
- **Add — the one gap the platform doesn't close:** a persistent, cross-session dispatch
  ledger (Track 2's proposal P1/P2 below) — the platform's background-by-default and
  notification hooks are *per-session*; they don't give craft (or the user) a way to see
  "what did any craft session on this machine dispatch, and is it still alive," which is
  exactly what the `.STATUS` backlog item asked for.
- **Escalate, don't simulate:** a genuine TTL/kill mechanism requires an executable stop
  at the platform/harness layer (a per-agent max-lifetime, or an orphan-reaper when a
  session ends) — craft cannot guarantee this from inside a markdown skill. Recommend
  this be asked of/filed with the platform rather than faked with more prose.

### 2.5 Ledger design (the one net-new piece of craft-side machinery)

- **File:** `.claude/orchestrate-dispatches.json` (project-local, gitignored).
- **Record per dispatch:** `dispatch_id`, `session_id`, `topic`, `worktree_path`,
  `orchestrate_file`, `dispatched_at`, `status` (`dispatched` / `completed` /
  `suspected-hung` / `suspected-failed`).
- **Written at dispatch time** (session already has every field at that point — no new
  logic to produce them, per L139-143's existing precedent for `.STATUS` factual writes).
- **Surfaced via** a read-only step added to `/craft:check` (or a small new
  `/craft:orchestrate:sweep` command) that lists ledger entries whose expected
  completion window has passed — "expected" computed via the same `2 × phase-effort
  estimate` formula §2.4 keeps (L116-122), just evaluated by the sweep instead of a live
  session's active polling. Modeled directly on how `/craft:git:clean` already surfaces
  orphaned worktrees. **Report-only first** — matches this repo's own gentle-ramp
  precedent (ADR-003, release-drift advisory-not-hard-gate).

### 2.6 Documentation gaps to close (regardless of what else ships)

1. State plainly, in `plan-orchestrator/SKILL.md` itself, that the caps described are
   LLM-instruction discipline, not runtime enforcement — no reader should come away
   believing "concurrency cap" or "force terminate" is a mechanism with teeth.
2. Document what happens (today: nothing) if the parent session dies mid-dispatch.
3. Document the cross-session story explicitly: N sessions × 2-per-session cap, no
   shared `.STATUS`-write lock, deterministic worktree-path collisions.
4. Add a one-line disclaimer to `orchestrator-resilience/SKILL.md`: its
   Timeout/Force-terminate/Circuit-Breaker sections are **report templates for
   orchestrator-v2's own narrative output**, not the orchestrate-dispatch supervisor.

## 3. Track 3 — opusplan / ultracode / Current Platform Capability

Grounded via live web research 2026-07-04 (sources cited in the research agent's report;
carried here without re-verifying, per this spec's own honesty convention of not
re-deriving already-gathered evidence):

- **`opusplan`** — a real, current `/model` selection value in Claude Code: Opus during
  Plan Mode (architecture/reasoning), auto-switches to Sonnet once a plan is approved
  and execution begins. An `opusplan[1m]` variant forces 1M context in both phases.
  Orthogonal to dispatch-safety concerns — relevant to craft only insofar as any future
  orchestrator work should not assume a fixed model across plan vs. execute phases.
- **`ultracode`** — a session **effort setting** (`xhigh` reasoning + automatic dynamic
  workflow orchestration), enabled via `/effort ultracode` (session-wide) or the keyword
  in a single prompt (task-scoped). Concurrency-capped at 16 concurrent / 1000 total
  agent calls per run. Requires Claude Code v2.1.154+.
- **Directly load-bearing for §2:** subagents now run **in the background by default**
  (confirmed shipped 2026-07-01) — the parent session keeps working and is notified on
  completion rather than blocking. New `agent_needs_input`/`agent_completed` notification
  hook events exist for background agent sessions. Worktree-based background code
  sessions now auto-commit/push/open a draft PR on finishing (no longer stop to ask).
  Subagents and context-compaction now inherit the parent session's extended-thinking
  configuration.

**Implication:** craft's `orchestrate-dispatch` (designed pre-2026-07-01) manually
implements what the platform has since made a default. This is the direct evidence
behind §2.4's "simplify toward platform-native" decision.

## 4. Track 4 — Token-Savings Rationale, Verified

The stated reason for building `orchestrate-dispatch` (`SPEC-orchestrate-dispatch-mode-2026-07-01.md:16-22`)
was to avoid "N cold-started sessions, each reloading `CLAUDE.md`/system-prompt" — a
qualitative claim, never a measured number, and never re-verified since.

- **What it actually credits:** dispatching from an already-warm live session instead of
  N fresh terminal sessions. This "no reload" saving is achievable via a **synchronous**
  foreground `Agent` call too — forked-context isolation applies to both; nothing
  token-wise is specific to *backgrounding*.
- **What backgrounding specifically adds, per the spec itself:** attention/parallelism
  (notification-driven vs. babysitting N terminals) — not a token claim.
- **The "68.3%" figure** (`.STATUS` v2.56.0 milestone) measures an unrelated
  namespace-string tokenization probe (243→77 tokens on a command-string refactor),
  reproducible via `scripts/token-probe.py` — not orchestrate-dispatch.
- **The 60/70/85/90% "compression" figures** (`agents/orchestrator-v2.md:733-788`,
  `commands/orchestrate.md:120`) are **context-window-usage trigger thresholds** (compress
  when context hits N% full) — not tokens saved, and not evidence for or against
  dispatch's rationale.
- **Explicit disclaim already on record:** `SPEC-token-efficiency-and-context-tooling-2026-07-01.md:29,73`
  states a related 48% figure is line-count, "that causal link is unvalidated," and the
  real `/usage` checkpoint (~2026-07-14) is the only thing that will confirm or refute
  actual token savings anywhere in this lineage — still open as of this spec's date.

**Conclusion:** the token-savings premise for background dispatch specifically was
asserted, never measured, and the mechanism it credits doesn't require backgrounding.
This does not mean orchestrate-dispatch has no value — §2.4 identifies what's genuinely
worth keeping (confirm gate, self-containment, resumability) independent of the token
claim.

## 5. Combined Decision Summary

| Area | Decision | Detail |
|---|---|---|
| Orchestrate-dispatch caps | Drop/shrink toward platform-native (hang-detection *formula* kept, only active polling dropped — see §2.4 clarification) | §2.4 |
| Orchestrate-dispatch value-add | Keep confirm-gate, self-containment, resumability | §2.4 |
| Cross-session visibility | Add dispatch ledger + report-only sweep | §2.5 |
| Real TTL/kill | Escalate to platform, don't simulate | §2.4 |
| Dispatch docs | Fix 4 gaps in §2.6 | §2.6 |
| D3 — project-planner body | Fix Capabilities/Outputs/Integration to strategy-only language | §1.4 |
| D2 — plan/feature.md contradiction | Un-deprecate (remove `deprecated: true`) | §1.4 |
| D1a — sprint/roadmap stubs | Shrink to real thin stubs | §1.4 |
| D4 — verify-gate table | Consolidate 3 sites into new `verify-gate-detection.md` | §1.4 |
| D6 — `--refine` default | Normalize ON/OFF split, state once | §1.4 |
| D9 — mode enum | Dedupe against existing `skills/modes/SKILL.md` | §1.4 |
| D10 — session-state naming | Clarify "resume" language, no functional change | §1.4 |
| D5 — intent-routing ownership | Collapse `do.md`↔`task-analyzer` to one source | §1.4 |
| D1b — `/craft:plan` router | Land after D1a; file-vs-alias question still open | §1.4 |
| D7 — deprecation horizon | Set new concrete date | §1.4 |
| D8 — actual deletion | Delete sprint/roadmap once D7's horizon passes (deferred) | §1.4 |

*(Track 1's 10 D-items now itemized individually per adversarial-review finding #5 —
the original single collapsed row was the reason findings C3-new/C6-new initially slipped
through with no decision attached; per-item rows make that check possible on a read-through.)*

## 6. Files Touched (future implementation, not this spec)

- `skills/orchestration/plan-orchestrator/SKILL.md` — trim §2.4's drop list, add ledger
  write step, fix §2.6 doc gaps, **and D4** (remove its own copy of the verify-gate
  table, point at the new shared reference — this file was missing from D4's scope in
  the original draft; it's one of the three sites C2-new actually names).
- `skills/orchestration/orchestrator-resilience/SKILL.md` — add the disclaimer from
  §2.6 item 4; trim overlap with platform-native handling.
- `skills/planning/SKILL.md` (project-planner) — D3 body fix.
- `commands/plan/feature.md` — D2 (remove `deprecated: true`).
- `commands/plan/sprint.md`, `commands/plan/roadmap.md` — D1a (shrink to stubs now);
  **D8** (deleted outright once D7's horizon passes — deferred, later than the rest of
  this list).
- `commands/do.md` — D5 (defer to `task-analyzer` instead of duplicating tables), D1b
  (new `/craft:plan` router, once D1a lands — **confirm at implementation time whether
  this is a standalone `commands/plan.md` file or an alias inside `do.md`; this spec
  counts it as "+1 command" in §1.4 but does not resolve which**), `--yes` frontmatter
  declaration, D9 (mode-enum table → reference `skills/modes/SKILL.md` instead of
  hardcoding).
- `skills/orchestration/task-analyzer/SKILL.md` — D5 counterpart.
- `skills/orchestration/drive-engine/SKILL.md`, `workflow-engine/SKILL.md` — D4
  (remove their own copies of the verify-gate table, point at the new shared reference).
- New: `skills/orchestration/references/verify-gate-detection.md` — D4's shared
  reference file (the one genuinely new file this spec's flag/boundary track adds).
- `skills/workflow/prompt-refiner/SKILL.md` — D6 (state the ON/OFF rule once).
- `commands/orchestrate.md`, `CLAUDE.md` — D9 counterpart (dedupe their own mode-enum
  copies against `skills/modes/SKILL.md`).
- `skills/orchestration/session-state/SKILL.md` — D10 (clarify/rename the "resume"
  language to avoid the name collision with the deleted `orchestrate:resume` command).
- New: `.claude/orchestrate-dispatches.json` (gitignored, runtime-created, not
  hand-authored) and its `/craft:check` or `/craft:orchestrate:sweep` surface.
- CHANGELOG/count-cascade files, per craft's own convention, once any command/skill
  count changes (D1b adds one now; D8 removes two, later, once its horizon fires).

## 7. Non-Goals

- No code changes ship as part of this spec — it is scoping only.
- No platform/upstream changes are made here. The one escalation this spec recommends
  (§2.4, real TTL/kill) is a request to raise, not a workaround to build.
- Cross-plugin material (superpowers collisions, sibling-plugin audits) stays in
  `SPEC-planning-federation-2026-06-22.md` (SPEC-A) — out of scope here, unchanged.
- This spec does not re-litigate `SPEC-planning-refactor-2026-06-22.md` §14's A0 verdict
  (C2 downgraded Critical→Medium) — it builds on that verdict as settled.

## 8. Gating & Sequencing

This spec **is** the "future larger effort" `SPEC-planning-refactor-2026-06-22.md`'s
pause was waiting on scoped. Once approved:

1. Open a worktree before any code changes (per this repo's own worktree-workflow
   rules) — `git worktree add ~/.git-worktrees/craft/feature-orchestrator-consolidation
   -b feature/orchestrator-consolidation dev`.
2. The two decision areas (§2 dispatch-safety, §1 flags/boundaries) touch disjoint file
   sets (see §6) and can proceed as two parallel implementation tracks inside that one
   worktree, or as two separate worktrees if preferred — no shared-file conflict between
   them.
3. Within the flag/boundary track, execute in the 4 waves below (§8.1) — supersedes the
   flat D3→D2→D1a→D4/D6→D5→D1b→D7 ordering from earlier drafts of this spec, which
   predates D8/D9/D10 (added during adversarial review, §1.4).
4. Behavioral tests gate the PR per this repo's existing `pre-pr-testing` convention —
   full suite, not a subset, given this touches routing logic multiple tests already
   pin (C4-new's three test files, §1.3). Each wave below gets its own test-gate before
   moving to the next — don't batch all 10 D-items into one untested PR.

### 8.1 Waves (flag/boundary track, D3–D10)

| Wave | Items | Why grouped | Gate before next wave |
|---|---|---|---|
| **1 — Do first** | D3, D2, D1a | Cheap, independently unblocked, no cross-item dependency. Highest confidence, lowest risk — start here. | Full suite green; the 3 test files pinning C4-new (`test_craft_plugin.py:583`, `test_plugin_dogfood.py:426`, `test_scaffold_defaults_e2e.py:17`) updated to match D2's un-deprecation. |
| **2 — Cleanup** | D4, D6, D9, D10 | Independent of each other and of Wave 1 — pure consolidation/dedupe, no new routing behavior. Can run in any order, even in parallel across sub-agents. | New `verify-gate-detection.md` (D4) referenced correctly from all 3 sites; `--refine` default rule (D6) documented once, not repeated. |
| **3 — Depends on Waves 1+2** | D5, D1b | D5 needs Wave 2's dedupe settled (it collapses `do.md`↔`task-analyzer`, which D9's mode-enum dedupe also touches). D1b needs D1a's stubs shrunk first (Wave 1) and benefits from D5/D6 being settled (avoids building the router against tables about to move). | `/craft:plan` router routes each intent correctly (behavioral test per D-table); confirm file-vs-alias resolved (§6 flagged this as open) before counting it in any release count-cascade. |
| **4 — Deferred** | D7, D8 | Runs on its own clock, independent of Waves 1–3 landing. D7 sets a date; D8 executes on it later — do not schedule D8 in the same PR cycle as Waves 1–3. | D7's horizon documented in `.STATUS`/CHANGELOG so a future session knows to check back; D8 only executes once that date arrives. |

**Dispatch-safety track (§2) runs independently of all 4 waves above** — different files
(§6), no ordering dependency either direction. Sequence within it: ledger design (§2.5)
before the `/craft:check`/`sweep` surface that reads it; documentation fixes (§2.6) can
land anytime, including before the ledger exists.

## 9. `.STATUS` Cross-Reference

See `.STATUS` 2026-07-04 entry: the original "PAUSED, scope not yet defined" framing is
superseded by this spec's existence; the stray-agent backlog bullet is closed into §2 of
this spec rather than left as a standalone open question.
