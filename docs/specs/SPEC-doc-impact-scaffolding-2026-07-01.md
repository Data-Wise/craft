# SPEC: Documentation-Impact Scaffolding — Rubric Extension + Site-Consistency Checklist

**Source brainstorm:** [BRAINSTORM-doc-impact-scaffolding-2026-07-01.md](BRAINSTORM-doc-impact-scaffolding-2026-07-01.md)
**Source grill (decisions locked):** [GRILL-doc-impact-scaffolding-2026-07-01.md](GRILL-doc-impact-scaffolding-2026-07-01.md) — 3 branches resolved, 2 open questions (both resolved below).
**Date synthesized:** 2026-07-01
**Status:** Ready for `/craft:orchestrate:plan`.

---

## 1. Problem

The doc-scorer rubric (`commands/docs/sync.md`) scores 4 output types (Guide, Refcard, Demo,
Mermaid). Requests for tutorial, API, architecture, and cookbook coverage — plus structural checks
(mkdocs nav, index, site-update) — aren't covered. 5 doc agents already exist that could author
the missing content types (`api-documenter`, `tutorial-engineer`, `docs-architect`,
`reference-builder`, `mermaid-expert`); the gap is in the *scorer* and a *site-consistency
checklist*, not in authoring capability.

## 2. Goal

Extend the existing rubric (single source of truth) to cover the missing content types, add a
separate Site-Consistency checklist for structural checks, and wire both into every spec-producer
that already reads the scorer — without creating any new skill (Option C, confirmed by the grill
under a token-efficiency lens).

## 3. Design (from the Decision Ledger + resolved Open Questions)

### 3.1 Two categories, two mechanisms (brainstorm's key finding)

- **Content types** (what doc to author) → belong in the doc-scorer rubric, scored 0–N, threshold
  gates a recommendation.
- **Structural checks** (did the site stay consistent) → belong in a separate **Site-Consistency
  checklist**, boolean pass/fail, never mixed into the score.

### 3.2 Rubric extension with tiered thresholds (grill branch 1)

Add Tutorial, API, Cookbook, Architecture-doc as new scored output types in
`commands/docs/sync.md`, with **tiered thresholds keyed to spawn cost**:

- Cheap in-context types (Refcard, Mermaid, index/nav tweak) — stay at `score ≥3`.
- Heavy agent-authored types (Tutorial, API, Cookbook, Architecture doc) — `score ≥5` **or** a
  concrete "new user-facing surface" trigger, so an expensive doc-agent spawn only happens when
  authoring is genuinely needed, not for minor edits.

### 3.3 Arch-doc double-count fix (Open Question, resolved)

"Architecture change" is currently a scoring **factor** (+3 Mermaid). Promoting "Architecture doc"
to an output **type** risks double-triggering: one arch change boosts Mermaid AND fires the
arch-doc type. **Resolution:** when computing the Architecture-doc type's score, subtract the
Mermaid factor's contribution from the shared "architecture change" signal before applying the
type's own ≥5 threshold — i.e., the same underlying signal must not count twice toward two
different recommendations. Document this subtraction rule explicitly in `commands/docs/sync.md`
next to the rubric table, not left implicit.

### 3.4 Propagation (grill branch 2)

Extend the scorer **once**, in `commands/docs/sync.md` only. All spec-producers
(`brainstorm`, `plan:feature`, `grill`, `orchestrate`/`plan-orchestrator`) already read this single
scorer — no per-consumer gating logic, no forked copies. This is what "propagate to all
spec-producers" means concretely: zero new code in the consumers, they inherit the extension for
free because they already call the shared rubric.

### 3.5 Site-Consistency checklist (grill branch 3)

Render as ORCHESTRATE checkboxes (in `references/scaffold-templates.md`) that invoke the
**existing** `/craft:site:update` + `docs-staleness-check.sh` tooling — real checks, not manual
recall, and **not** a new implementation of drift detection. **Advisory, not a hard block per
spec** — the release pipeline already hard-gates docs-staleness
(`docs-staleness-check.sh --non-interactive`, release Step 3b); a second per-spec hard gate would
double-gate and add blocking friction to every feature for no additional safety.

Three checkboxes:

- [ ] mkdocs nav updated (new pages added to `mkdocs.yml` nav)?
- [ ] index file updated (if new top-level doc)?
- [ ] `/craft:site:update` / `docs-staleness-check.sh` run?

### 3.6 Single-source drift guard (Open Question, resolved)

The expanded types **must live only** in `commands/docs/sync.md` (the scorer). Neither
`references/scaffold-templates.md` nor `plan-orchestrator/SKILL.md`'s body may hardcode a parallel
type list — they read the scorer's current type list at doc-emission time. **Resolution:**
implement as a dogfood test (§6) that greps both files for a hardcoded type enumeration matching
the rubric's type names and fails if found outside a "see `commands/docs/sync.md`" reference.

## 4. Explicitly rejected (do not re-litigate)

- **Option A — skill per doc type** (tutorial-gen, cookbook-author, api-doc, …): duplicates the 5
  existing doc agents, multiplies surface + count cascade — the exact anti-pattern this session's
  orchestrate-family audit is fighting elsewhere.
- **Option B — one `docs-impact` skill**: premature. `plan-orchestrator` already emits the
  Documentation section inline by reading the scorer; a dedicated skill adds resting cost for no
  behavior the inline approach can't already do. Revisit only if inline scorer-reuse becomes
  unwieldy in practice.
- **Orchestrate-only propagation**: rejected — would require adding per-consumer gating logic to
  fork the scorer's output, breaking the single-source rule for no benefit over extending the
  shared scorer once.
- **Site-consistency as a per-spec hard gate**: rejected — the release pipeline already hard-gates
  this; double-gating adds friction without additional safety.
- **Mixing structural checks into the 0–N score**: rejected — booleans (nav/index/site-update)
  corrupt a numeric scorer; keep them as a separate checklist.

## 5. Acceptance Criteria

- [ ] `commands/docs/sync.md` rubric table includes Tutorial, API, Cookbook, Architecture-doc as
      scored output types, with tiered thresholds (≥3 cheap / ≥5 or surface-trigger heavy)
      documented inline.
- [ ] The Architecture-doc double-count subtraction rule (§3.3) is documented next to the rubric
      table, not left implicit.
- [ ] `references/scaffold-templates.md` gains a `## Site Consistency` block with the 3 checkboxes
      (§3.5), referencing `/craft:site:update` + `docs-staleness-check.sh` by name.
- [ ] No new skill file created (Option C confirmed).
- [ ] No parallel type list exists outside `commands/docs/sync.md` — verified by the dogfood test
      in §6.
- [ ] `plan-orchestrator/SKILL.md`'s Documentation-scaffolding section description mentions the
      expanded type list (still reads the scorer, not hardcoded).
- [ ] Documentation & Discoverability phase complete (REFCARD entry for the expanded section,
      `validate-counts.sh` clean — no new command/skill/agent expected).

## 6. Test Plan (default-on)

- **e2e:**
  - An ORCHESTRATE emitted for an architecture change pre-checks Architecture-doc + Mermaid
    correctly (not double-counted per §3.3's subtraction rule) — assert the two scores don't both
    fire off the same underlying signal without the subtraction applied.
  - The Site-Consistency block is present with exactly 3 unchecked boxes on a fresh ORCHESTRATE
    emission.
  - **Audit-path e2e (the gap this SPEC closes):** run `/craft:site:audit` (or
    `docs-staleness-check.sh`) against a fixture site with a deliberately introduced mkdocs-nav
    drift (a page not in `mkdocs.yml` nav) and assert the Site-Consistency checkbox mechanism
    actually surfaces that drift — not just that the checkbox exists, but that checking it against
    real tooling output catches a real omission. This is the half the original test plan didn't
    cover (doc-type *creation* firing was covered; the *audit* half catching a real drift was not).
- **dogfood:**
  - The expanded types live in `commands/docs/sync.md` ONLY — grep `references/scaffold-templates.md`
    and `plan-orchestrator/SKILL.md` for a hardcoded type list matching the rubric's type names;
    fail if found outside a cross-reference to `commands/docs/sync.md` (single-source guard, §3.6).
  - The Documentation section references existing agents by name (`api-documenter`,
    `tutorial-engineer`, `docs-architect`, `reference-builder`, `mermaid-expert`) — assert no new
    `skills/docs-*` directory is created.

## 7. Documentation

- Update `commands/docs/sync.md` rubric table + threshold documentation.
- Update `references/scaffold-templates.md` with the Site-Consistency block.
- Update the doc-scorer type-list mention in `plan-orchestrator/SKILL.md`.
- REFCARD entry for the expanded doc-impact section (`docs/REFCARD.md` or a dedicated reference
  page, per existing convention for larger scaffold changes).
- No count-cascade expected (rubric/template extension, not a new command/skill/agent) — confirm
  with `validate-counts.sh` after implementation regardless.
