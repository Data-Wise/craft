# BRAINSTORM: Comprehensive Documentation-Impact Scaffolding

**Date:** 2026-07-01 · **Depth:** default · **Focus:** arch
**Refined from:** "include docs generating, refcards, tutorials, API/architecture docs, cookbooks,
docs reorg + mkdocs nav, index, and site-update check in every spec written by orchestrate; debate
creating skills for these."

---

## Current state (what already exists)

- **Doc-scorer rubric** (`commands/docs/sync.md`) scores **4 output types**: Guide, Refcard, Demo,
  Mermaid. Threshold ≥3. It is the declared **single source of truth** — plan-orchestrator says
  *"do NOT invent a new rubric — reuse the scorer."*
- **plan-orchestrator** already emits a **Documentation section by default** in every ORCHESTRATE,
  pre-checking boxes that clear the threshold. Template in `references/scaffold-templates.md`.
- **5 doc AGENTS already exist:** `craft:docs:api-documenter`, `docs-architect`,
  `reference-builder`, `tutorial-engineer`, `mermaid-expert`.

## The gap (what's requested)

| Requested | Category | Status today |
|---|---|---|
| Tutorials | content type | ❌ not scored (appears only as a stale-doc example) |
| API docs | content type | ❌ not scored (agent exists) |
| Architecture docs | content type | ⚠️ arch is a *scoring factor* (+3 Mermaid), not an output type |
| Cookbooks | content type | ❌ not scored |
| Docs reorg + mkdocs nav | **structural check** | ❌ absent |
| Index file | **structural check** | ❌ absent |
| Site-update check | **structural check** | ❌ absent |

## Two key findings (shape everything below)

`★ Insight ─────────────────────────────────────`

- **The requests split into two different categories.** Content types (tutorial, API, arch,
  cookbook) are *"what doc to author"* — they belong in the doc-scorer rubric. Structural checks
  (mkdocs nav, index, site-update) are *"did the site stay consistent"* — they're **checks, not
  authored artifacts**, and belong in a separate Site-Consistency checklist.
- **Creating skills for these would duplicate 5 existing agents.** `api-documenter`,
  `tutorial-engineer`, `docs-architect`, `reference-builder`, `mermaid-expert` already do the
  authoring. A new skill-per-type is the exact duplication the orchestrate-family audit is
  fighting.

`─────────────────────────────────────────────────`

---

## Quick Wins (< 30 min each)

1. **Extend the doc-scorer rubric with the missing content types** — add Tutorial, API, Cookbook
   columns (and promote "Architecture doc" from a factor to an output type) to the scoring table in
   `commands/docs/sync.md`. Single source of truth stays single; plan-orchestrator inherits them
   for free (it just reads the scorer).
2. **Add a `## Site Consistency` block to the scaffold template** (`references/scaffold-templates.md`)
   — three checkboxes: mkdocs nav updated? index file updated? `site:update` run? These are
   pass/fail checks, not scored artifacts.

## Medium Effort (1–2 hrs)

- [ ] **Wire the Documentation section to REFERENCE existing doc agents**, not new skills — each
  emitted doc type links to the agent that authors it (`api-documenter`, `tutorial-engineer`, …).
  The ORCHESTRATE tells the implementer *which agent to run*, not a new skill to write.
- [ ] **Fold the site-update check into the existing `/craft:site:update` + docs-staleness
  tooling** — the check should invoke what already exists, not re-implement drift detection.

## Long-term (future sessions)

- [ ] **A single `docs-impact` skill** (NOT one-per-type) that owns the expanded rubric + emits the
  section — only if the inline scorer-reuse proves too thin. Debated below.
- [ ] **Reorg-aware nav validation** — a check that new docs are actually added to `mkdocs.yml` nav
  (catches the "orphaned page" class the mkdocs memory already flags).

---

## The debate: create skills for these doc operations?

| Option | What | Verdict |
|---|---|---|
| **A — skill per doc type** (tutorial-gen, cookbook-author, api-doc, …) | New skill for each | ❌ **Reject** — duplicates the 5 existing doc AGENTS; multiplies surface + count cascade; the anti-pattern this session keeps finding |
| **B — one `docs-impact` skill** | Single skill owns expanded rubric + section emission | ⚠️ Maybe later — only if inline scorer-reuse gets unwieldy; today plan-orchestrator already emits the section inline, so a skill is premature |
| **C — no new skills; extend rubric + reference existing agents** (Recommended) | Scorer gains types; section references agents + site commands | ✅ **Recommended** — reuses the SoT rubric, reuses the 5 agents, adds zero duplicative surface |

**Why C:** the authoring capability already exists (agents) and the scoring SoT already exists
(rubric). The gap is *coverage in the rubric* + *a site-consistency checklist* — both are
extensions of existing single-source mechanisms, not new capabilities. Creating skills would
re-implement what agents do and fork the "single source of truth" the design explicitly protects.

## Risks / edge cases

- **Rubric bloat → false-positive doc recommendations.** Adding 4 types means more `score ≥3`
  triggers; tune factors so a one-line fix doesn't demand a cookbook.
- **Single-source discipline.** The expansion MUST land in `commands/docs/sync.md`, not be copied
  into the scaffold template or ORCHESTRATE body (drift trap).
- **Structural checks aren't scored.** Don't force mkdocs-nav/index/site into the 0–N scorer — they
  are boolean checks; mixing them into the score corrupts it.
- **Count cascade** only if this adds a *command*; extending a rubric + template does not.

## Test Plan (default-on)

- **e2e:** an ORCHESTRATE emitted for an arch change pre-checks Architecture + Mermaid; the
  Site-Consistency block is present with 3 unchecked boxes.
- **dogfood:** the expanded types live in `commands/docs/sync.md` ONLY (assert no parallel rubric
  in `scaffold-templates.md` or plan-orchestrator body — single-source guard).
- **dogfood:** the Documentation section references existing agents by name (no new `skills/docs-*`).

## Documentation (default-on)

- Update `commands/docs/sync.md` rubric table + `references/scaffold-templates.md`.
- Update the doc-scorer description in `plan-orchestrator/SKILL.md` (type list).
- Refcard entry for the expanded doc-impact section.

## Recommended Next Step

→ **Option C, starting with Quick Win #1** — extend the doc-scorer rubric in `commands/docs/sync.md`
with Tutorial/API/Cookbook/Architecture types. It's the smallest change that makes every
orchestrate-emitted spec cover the fuller set, it protects the single-source-of-truth, and it needs
zero new skills. Grill this brainstorm (open questions: rubric factor weights; whether
site-consistency is a hard gate or advisory) before implementing.
