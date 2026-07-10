# BRAINSTORM — folio Border Filter (move vs. kill vs. merge)

> **Bounded scope:** the 26-command moves-set + 6 agents + skills partition + folio launch shape.
> B1–B5 / W1–W2 stay locked; this decides only WHAT crosses the border.
> **Date:** 2026-07-09 · Feeds the post-review amendment of
> `SPEC-folio-split-workflow-2026-07-09.md` + `ORCHESTRATE-folio-split.md`.
> **Principle:** never pay extraction cost (history-preserving move + repoint + CI) for
> something you'd delete in v1.1. Kill at the border, salvage rich bodies per ADR-002.

## Evidence (repo-verified this session)

- **8 of the 26 "moving" commands are ALREADY `deprecated: true`:** all 7 live `site:*`
  (build, check, progress, publish, status, update — deploy is the 8th, dying separately per
  B2) plus `docs:nav-update`. All `replaced-by:` → `skills/docs/{site-management, navigation}`
  — which move to folio anyway.
- **`site:progress` is teaching residue** ("semester progress dashboard") — scholar leftover.
- **ADR-002 risk quantified:** `site-management/SKILL.md` = 284-line router, NO `references/`
  dir, vs ~80KB of deprecated command bodies. Kills need rich-body salvage into folio's
  `skills/docs/site-management/references/`, not blind deletion.
- `docs:check` (health: links+staleness+nav) vs `docs:check-links` (links only) — subset overlap.
- `site/docs/frameworks.md` is reference material wearing a command's clothes.
- `skills/docs/` has 8 dirs; 3 have live craft-core callers (ADRs ← adhd-workflow +
  audit-deprecated-commands.py + grill test; claude-md ← staying trio; changelog-automation ←
  staying `docs:changelog`).

## The Border Table

### Commands (26 candidates)

| Verdict | Items | N | Rationale |
|---|---|---|---|
| ☠️ **KILL at border** | `site:{build, check, progress, publish, status, update}` + `docs:nav-update` | 7 | Already deprecated; replaced-by skills move to folio; salvage rich bodies → folio skill `references/`. `site:progress` = pure kill (teaching residue, no salvage) |
| 🔀 **MERGE in transit** | `docs:check-links` → flag/section of `docs:check` | 1 | Subset function; folio lands one health command |
| 📚 **DEMOTE to skill reference** | `site:docs:frameworks` | 1 | Reference doc, not a command — fold into site-management `references/` |
| 📦 **MOVE clean** | `docs:{api, check, demo, generate, guide, help, lint, mermaid, prompt, quickstart, site, sync, tutorial, website, workflow}` | 15 | Genuine authoring surface (help/prompt/workflow kept: v2.60.0 audit judged the 9 generators genuinely distinct) |
| 🏠 **RESOLVED: trio STAYS in craft** | `docs:claude-md:{sync, init, edit}` | 0 moved | Craft-internal CLAUDE.md governance (B5 fix — decided here as one unit, resolves the double-booking) |

### Agents (6) — all MOVE

api-documenter · demo-engineer · docs-architect · mermaid-expert · reference-builder ·
tutorial-engineer — all genuinely authoring; no craft-core callers.

### Skills (8 + 1)

| Verdict | Items |
|---|---|
| 📦 MOVE (6) | doc-classifier · mermaid-linter · navigation · site-management · openapi-spec-generation · `skills/code/demonstration-builder` |
| 🏠 STAY (3) | architecture-decision-records (craft governance callers) · claude-md (backs the staying trio) · changelog-automation (pairs with staying `docs:changelog`) |

## Resulting Shape (fixes review B4/B5 arithmetic)

| | Commands | Agents | Skills |
|---|---|---|---|
| **craft after** | **69** (94 − 24 leaving − 1 deploy alias; trio stays) | 2 (8 − 6) | 39 (45 − 6) |
| **folio v1.0.0** | **≈15** (15 clean + check absorbing check-links) | 6 | 6 |
| Killed at border | 7 commands + 1 demoted + 1 merged | — | — |

folio launches as a **focused authoring toolkit** — no inherited deprecation debt, no zombie
`site:*` namespace, one health command, discovery via `/folio:hub` shipped in Phase 2 (review
fix). ~40% less extraction/repoint/CI work than the naive 26-command transplant.

## Not Doing (and why)

- **Re-simplifying craft's remaining 69** — that's the refuted Phase-2 cascade-thinning
  territory; craft's surface stands on the PR #279 outcome. Out of scope.
- **Merging the 9 `docs:generate` targets** — v2.60.0 already audited them as genuinely
  distinct; don't relitigate without new evidence.
- **Renaming folio's namespaces at the border** (`/folio:docs:*` → `/folio:*`) — tempting
  (the `docs:` prefix is redundant inside a docs plugin) but it breaks the 1:1 MIGRATION-v4
  mapping and doubles user relearning. Defer to folio v2 with usage data.
- **Killing `docs:help/prompt/workflow`** on vibes — no deprecation marker, no overlap
  evidence; they move and can die later with folio's own usage data.

## Open Questions

- Salvage depth for the 7 killed site commands: full body → `references/` (safe, bulky) vs.
  distilled ops guide (clean, riskier)? Recommend: distill, but diff-audit against the 284-line
  router first (ADR-002 line-conservation gate).
- folio skill count keys: validate-counts must key on SKILL.md-only (memory:
  `validate-counts-skill-breakdown-overcounts`).

## Recommended Next Step

→ Fold this border table into the ONE amendment commit (review fixes + final moves-set +
corrected counts 69/≈15), then re-gate at CP-A. The kill-list also shrinks wf-p2-repoint's
pipeline by ~40%.
