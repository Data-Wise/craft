# SPEC-D — Domain Specialist Gates (agent-skills: security, refactoring, frontend, backend)

> **Repo:** `~/projects/dev-tools/craft` · **Branch:** `dev` · **Date:** 2026-07-09
> **Status:** Proposed, not yet implemented. Scoped narrowly on purpose — see §0.
> **Builds on:** `SPEC-orchestrator-consolidation-2026-07-04.md` (SPEC-C) and the
> pending agent-skills-as-4th-mode ADR (referenced there, not yet filed as an
> ADR file). Does not reopen or contradict either.
> **Scope:** optional, per-mode injection of four external agent-skills domain
> skills into craft's existing three orchestration engines. No new engine, no
> change to planning ownership.

---

## 0. Why this is scoped narrowly

Verified against the actual `addyosmani/agent-skills` skill list and its own
`AGENTS.md` governance doc (not assumed from skill names). Two findings shaped
this scope:

1. **The four requested domains map to exact, existing skills** (Build/Review
   phase, not Define/Plan — this matters for §3):

   | Domain | agent-skills skill | Phase |
   |---|---|---|
   | Refactoring | `code-simplification` (Chesterton's Fence, clarity-first) | Review |
   | Security | `security-and-hardening` (vuln detection, threat modeling) | Review |
   | Frontend | `frontend-ui-engineering` (component arch, WCAG 2.1 AA) | Build |
   | Backend | `api-and-interface-design` (REST/GraphQL, frontend/backend boundary — named explicitly in its own description) | Build |

2. **A hard platform constraint**, stated in agent-skills' own `AGENTS.md`:
   *"subagents cannot spawn other subagents, and teams cannot nest."* Their
   own multi-persona pattern (`/ship`'s parallel fan-out of
   `code-reviewer`/`security-auditor`/`test-engineer`) is the *only* endorsed
   way they spawn multiple personas — flat fan-out-then-merge, never nested.

## 1. The concrete hazard this scoping avoids

`plan-orchestrator`'s `orchestrate-dispatch` mode already dispatches a
background `Agent` (`plan-orchestrator/SKILL.md` L84-91). If that dispatched
agent, mid-execution, tried to invoke agent-skills' `/ship` — which itself
fans out to 3 personas — **that is a subagent spawning subagents**, which the
platform does not support per agent-skills' own docs. Same risk inside
`workflow-engine`'s wave dispatch if a `parallel` stage's file-scoped agent
tried to call `/ship` internally.

**This rules out "just add agent-skills' `/ship` as a stage"** as a naive
integration — it would silently violate a platform constraint neither repo
currently checks for.

## 2. Proposal: domain skills as leaf-level content, not spawned personas

Two integration shapes, chosen per mode based on what is already structurally
safe.

### `workflow` — the correct home for this (leaf-scoped by design already)

`workflow-engine` already dispatches **file-scoped, non-nesting leaf agents**
under its semaphore (`workflow-engine/SKILL.md`, Responsibilities §3). Adding
a new stage type, `domain-gate`, that injects one domain skill's **content**
(not a spawned sub-persona) into a single leaf agent's prompt is structurally
identical to what workflow-engine already does for every other stage. No
nesting risk — still one flat dispatch layer.

```yaml
- stage: security-review
  type: domain-gate
  skill: security-and-hardening   # content injected, not spawned
  scope: [files changed in this run]
  gate: structural + semantic_warning   # reuses D2's existing hybrid gate
```

### `drive` and `fanout` — content-injection only, never spawn

For `drive`'s condition-synthesis step and `fanout`'s per-wave confirm gate:
inject the relevant domain skill's checklist as **prompt content** the live
session reasons over directly — not a `Task`/`Agent` call. This sidesteps the
nesting question entirely because nothing is spawned.

### Explicitly ruled out for this proposal

Adopting agent-skills' `/ship` fan-out pattern wholesale (its 3-persona
parallel dispatch) anywhere inside craft's existing dispatch layers — that
would be the one actual nesting violation. If craft wants that pattern
specifically, it belongs as a **top-level, non-nested command** (e.g. a new
`/craft:ship:audit` that runs standalone, the way agent-skills' own `/ship`
runs standalone) — not embedded inside `fanout`/`drive`/`workflow`.

## 3. Why this does not reopen the planning-ownership question

All four domain skills are **Build/Review phase**, not Define/Plan. None of
them touch `/spec` or `/plan`. The prior resolution — craft owns planning
end-to-end (`grill` → `plan.md`/`plan-orchestrator` → `ORCHESTRATE`); any
future agent-skills adoption stays execution-only — is untouched by this
proposal.

## 4. Sequencing (builds on, does not reorder, SPEC-C)

1. **Land SPEC-C's already-scoped work first.** Domain-gates touch
   `workflow-engine`, `drive.md`, `orch.md` — the same files SPEC-C's D4
   (verify-gate consolidation) already touches. Sequencing after avoids a
   two-PR collision on the same sections.
2. **`workflow`'s `domain-gate` stage type** — smallest, safest, structurally
   consistent with the existing D1-D8 design. Ship first.
3. **`drive`'s content-injection into condition synthesis** —
   `security-and-hardening` first, given `drive` is explicitly for driving
   specs to production-ready green.
4. **`fanout`'s per-wave injection** — last; fanout's improvised nature makes
   this the least structurally clean fit, lowest priority.
5. **Do not build the `/ship`-pattern standalone command** as part of this
   spec — flag as a separate future proposal if wanted; keep this scoped.

## 5. Non-goals

- No new orchestration engine.
- No adoption of agent-skills' `/ship` fan-out pattern inside existing
  dispatch layers (nesting hazard, §1).
- No change to planning ownership (§3).
- `frontend-ui-engineering` and `api-and-interface-design` are Build-phase,
  not Review — they slot in as **pre-implementation content** (inject before
  the leaf agent writes code), not as a post-hoc gate like the two
  Review-phase skills. Stated explicitly so a future reader does not assume
  all four slot in the same way.

## 6. Files to touch (future implementation, not this spec)

- `skills/orchestration/workflow-engine/SKILL.md` — add `domain-gate` stage
  type to the responsibilities list and the stage-type table.
- `commands/orch/drive.md` — Step 3 (condition synthesis) gains an optional
  domain-skill content-injection sub-step.
- `commands/orch.md` — per-wave confirm gate gains an optional domain-skill
  content-injection note.
- New: a small mapping file (e.g.
  `skills/orchestration/references/domain-skill-sources.md`) recording where
  each of the four skill's content is vendored/fetched from, so the four
  citations in §0 stay a single source of truth rather than four hardcoded
  copies.

## 7. Origin

Drafted via `/prompt-refiner`-assisted Claude.ai chat session, 2026-07-09,
following an adversarial review of craft's three orchestration engines and a
verified read of `addyosmani/agent-skills`' actual skill catalog and
`AGENTS.md`. Not yet reviewed or approved.
