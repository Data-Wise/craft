---
title: "GRILL — Craft Refactor Proposal"
date: 2026-07-09
status: active
type: grill-ledger
target: docs/ideas/craft-refactor-proposal.html
---

# GRILL — Craft Refactor Proposal

Adversarial interrogation of the 3-phase refactor proposal
(`docs/ideas/craft-refactor-proposal.html`). Convergent counterpart to the
idea-refine ideation that produced the proposal. 7 load-bearing branches
resolved; the plan was materially de-risked and *shrank* (fewer irreversible
moves, every ADR-002-style silent-loss trap gated).

> Note: this ledger lives in `docs/specs/`, which decision **B2** removes from
> the *built* mkdocs site but keeps in-repo as the live capture target — this
> file existing here is the proof of that decision.

## Decision Ledger

### B1 — Deprecated-command drop scope · **Delete dead namespaces only**

- **Attack angle:** riskiest assumption / silent failure (ADR-002
  "deprecated-command rich-body trap" — craft has already lost logic this way).
- **Locked:** Delete the **39** commands in fully-/near-dead namespaces now
  (`git/` 15 + `workflow/` 5 + `task/` 3 + `check/` 1 + `site/`'s 15 deprecated,
  **keeping site's 1 live command**). The **17** deprecated-inside-live-namespaces
  (root 5, `docs/` 4, `dist/` 3, `code/` 2, `plan/` 2, `orch/` 1) get a
  **verified second pass** — diff each body vs its `replaced-by:` skill first.
- **Consequence:** 39/56 safe immediately; the report's "EFFORT: LOW" badge on
  Phase 1 is **corrected** — the 17-command tail is real verification work.

### B2 — Docs "delete" scope · **Exclude from built site, keep dirs**

- **Attack angle:** blast radius / self-contradiction — `docs/specs/` is the
  LIVE capture target for brainstorm/grill/spec (incl. this ledger).
- **Locked:** Do **not** `rm`. Use mkdocs `exclude_docs` to drop `docs/specs/`,
  `docs/plans/`, `docs/archive/` from the **published site**; keep the
  directories in-repo. Add a **retention rule** (prune artifacts older than N
  months — N TBD, see Open Questions). User confirmed mid-grill: "rm … from the
  built mkdocs site."
- **Consequence:** ~44K lines leave the maintained/built surface; the
  grill/brainstorm/spec spine keeps working.

### B3 — Docs success metric · **Files-touched-per-release**

- **Attack angle:** benefit honesty — after B2, "135K→55K lines" measures the
  wrong thing (most is exclude-not-delete; repo lines ~unchanged).
- **Locked:** Re-baseline on the tax actually felt: **count cascade (30→1
  file)**, **doc files changed per release**, **built-site page count**. Drop raw
  repo line-count as the headline.
- **Consequence:** honest, measurable before/after; report headline rewritten.

### B4 — `docs/commands/` generation · **Content-audit before generating**

- **Attack angle:** implementation regret — ADR-002 at the doc layer;
  craft's frontmatter parser is hand-rolled (not YAML), 84 pages = 12K lines
  (more than frontmatter).
- **Locked:** Measure what the 84 pages hold beyond frontmatter first. Generate
  **only thin mirrors**; leave content-rich pages hand-maintained. A valid
  outcome is "don't build the generator."
- **Consequence:** avoids silently dropping hand-written examples/prose and the
  fragile-parser scope creep.

### B5 — Plugin split (Phase 3) · **CUT entirely**

- **Attack angle:** reversibility & scope creep — a solo maintainer would own a
  second release pipeline, shared-skill ownership, marketplace + tap sync
  forever; "context dilution" is asserted, not measured.
- **Locked:** **Remove Phase 3.** Craft stays one plugin. Phases 1–2 are the
  whole plan. If context dilution proves real later, revisit with data.
- **Consequence:** no speculative fragmentation (the exact over-engineering that
  bloated craft). Dilution, if real, is deferred not solved.

### B6 — Exclusion ordering · **Sweep inbound links first**

- **Attack angle:** blast radius (craft's own `mkdocs-exclude-docs` memory +
  link-validation CI).
- **Locked:** Before `exclude_docs`, grep all **built** pages for links into
  specs/plans/archive **and check per-file nav membership**; remove/redirect
  inbound links, then exclude.
- **Consequence:** zero red link-CI; small upfront grep matching the memory that
  exists because this bit before.

### B7 — Migration surface · **Grep external surfaces first**

- **Attack angle:** riskiest assumption #1 in the report — external callers.
- **Locked:** Before v3.0.0, grep **flow-cli, atlas, `~/.claude`, shell history,
  craft's own tutorials/docs, the marketplace manifest** for the 56 dropped
  names. Any name with a live external caller stays a **thin alias one more
  cycle**.
- **Consequence:** no surprise breakage in the ecosystem; "drop 39" becomes the
  honest "39 minus external hits."

## Net Effect

| Phase | Original proposal | After grill |
|-------|-------------------|-------------|
| 1 · Prune | drop all 56 at once, "LOW effort" | 39 dead-namespace now (keep site's 1 live) + 17 verified 2nd pass; badge corrected |
| 2 · Docs | `rm` specs/plans/archive (~44K lines) | `exclude_docs` from built site, keep dirs + retention rule; sweep inbound links first |
| 2 · Metric | "135K → 55K lines" | files-touched-per-release + count cascade 30→1 + built-page count |
| 2 · docs/commands | generate from frontmatter | content-audit first; generate only thin mirrors |
| 3 · Split | peel `craft-docs` satellite | **CUT** — one plugin; measure only if dilution resurfaces |
| Cross-cutting | (implicit) | grep external callers before v3.0.0; keep externally-used names as aliases |

## Open Questions (unresolved — for /craft:plan)

1. **Retention threshold N** (B2): how old before a `docs/specs` artifact is
   pruned, and is prune = remove-from-repo or remove-from-build-only? Who runs
   it — manual, pre-commit hook, or CI?
2. **Phase-1 test cascade:** which count/discovery/e2e/dogfood tests assert the
   39 dropped commands exist? They must be updated in the same v3.0.0 (not
   grilled — mechanical, but real work).
3. **17-command verification effort:** how long is the per-command
   body-vs-skill diff for the deferred tail? Prices the Phase-1 "second pass."

## Handoff

`/craft:plan` tier 4 (plan-orchestrator) → `ORCHESTRATE-craft-refactor.md` →
`/craft:do` / `/craft:orch`. Grill interrogates; it does not execute.
