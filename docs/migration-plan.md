# Commands → Skills Migration Plan (v3)

**Source:** `commands/` (108 markdown files)
**Target:** `skills/` (26 existing + ~10-12 new, all nested under thematic category dirs)
**Created:** 2026-05-13 · **Revised:** 2026-05-13 (v3 — post-spike, post-re-audit)
**Spec:** [`docs/specs/SPEC-commands-to-skills-migration-2026-05-13.md`](specs/SPEC-commands-to-skills-migration-2026-05-13.md) (authoritative; this doc is the summary)
**Status:** **IMPLEMENTED** — Batches 1+2+3 complete (11 new skills, 56 commands consolidated, 011b4d33 latest). Only v3.0.0 cleanup PR remains.

## What this is

A migration of craft commands into Claude Code's skill format, consolidating by *concern* rather than 1:1 porting. After a full audit against the 26-skill baseline:

| Status | Count | % |
|---|---|---|
| **COVERED** by existing skill | 43 | 39% |
| **PARTIAL** (skill touches, doesn't fully cover) | 12 | 11% |
| **GAP** (no skill exists) | 53 | 49% |
| **DELETE** (internal doc) | 1 | 1% |

The 53 GAPs consolidate into **~10-12 new skills** (not 53 ports).

## Revision history

| v | Date | Change |
|---|---|---|
| v1 | 2026-05-13 (early) | Initial 1-to-1 batch plan (5 batches × ~22 commands). **WRONG PREMISE** — assumed no skills existed. |
| v2 | 2026-05-13 (mid) | Gap-analysis correction. Discovered 13 thematic skills, reduced to ~11 new skills. **STILL WRONG** on skill count (missed nested sub-skills). |
| v3 | 2026-05-13 (current) | Full re-audit against 26-skill baseline (nested categories). Coverage refined 47%→39%. Nested-path convention. task-dispatcher removed. |

## Batches (v3)

### Batch 1 — Highest-leverage gaps (3 new skills)

| New skill (nested path) | Source commands | Status |
|---|---|---|
| `skills/workflow/adhd-workflow/SKILL.md` | workflow/{done, focus, next, recap, refine, spec-review, stuck} = 7 cmds | ✅ DONE (c2aaa18d) |
| `skills/dev/git/SKILL.md` | git/*(10) + git/docs/* (4) = 14 cmds | pending Batch 1 wave 2 |
| `skills/workflow/task-management/SKILL.md` | workflow/{task-cancel, task-output, task-status} = 3 cmds | pending Batch 1 wave 2 |

**Target release:** v2.34.0 · **Risk:** lowest (largest gap, no skill overlap)

### Batch 2 — Pre-flight + orchestration + ideation + coverage (4 new skills)

| New skill (nested path) | Source commands |
|---|---|
| `skills/check/SKILL.md` | check.md + check/gen-validator.md (2; `project-detector` doesn't cover pre-flight orchestration) |
| `skills/orchestration/plan-orchestrator/SKILL.md` | orchestrate/plan + plan/{feature, roadmap, sprint} = 4 cmds |
| `skills/workflow/brainstorm-insights/SKILL.md` | workflow/{brainstorm, insights} = 2 cmds |
| `skills/code/coverage-metrics/SKILL.md` | code/{coverage, demo} = 2 cmds (coverage metrics + instructional demos) |

**Target release:** v2.35.0 · **Risk:** low–medium (some PARTIAL overlap with project-detector and task-analyzer to navigate)

### Batch 3 — Docs/site/dist consolidation (4 new skills)

| New skill (nested path) | Source commands |
|---|---|
| `skills/docs/claude-md/SKILL.md` | docs/claude-md/{init, sync, edit} = 3 cmds |
| `skills/docs/navigation/SKILL.md` | docs/nav-update + site/{add, nav} = 3 cmds |
| `skills/docs/site-management/SKILL.md` | site/{build, deploy, publish, theme, status, update, create, audit, consolidate, progress, ...} = ~12 cmds |
| `skills/distribution/dist-extras/SKILL.md` | dist/{pypi, curl-install, marketplace} = 3 cmds |

**Target release:** v2.36.0 · **Risk:** medium (consolidation ratio is highest in this batch — ~21 cmds → 4 skills)

### Cleanup PR — v3.0.0

- Remove ~30 deprecated commands that have aged through ≥1 minor release.
- Delete `commands/discovery-usage.md`.
- Update `_discovery.py` & tests to drop removed-command assertions.
- BREAKING CHANGE CHANGELOG entry with per-removed-command replacement map.

## Out-of-scope (no new skill needed)

These commands stay as-is, fully covered by existing skills (per re-audit):

- All `commands/arch/*` → covered by `skills/architecture/SKILL.md`
- All `commands/ci/*` except `ci/status` → covered by `skills/ci/SKILL.md`
- Most `commands/code/*` (12 of 16) → covered by `skills/code/SKILL.md`, `skills/release/SKILL.md`, `skills/design/*`
- `commands/test.md`, `commands/test/gen.md` → covered by `skills/testing/*`
- `commands/dist/homebrew.md` → covered by 5 nested `skills/distribution/homebrew-*` skills
- `commands/do.md` → covered by `skills/orchestration/task-analyzer/SKILL.md`
- `commands/orchestrate.md`, `commands/orchestrate/resume.md` → covered by `skills/orchestration/{session-state,task-analyzer}/`
- `commands/workflow/{done,focus,next,recap,refine,spec-review,stuck}` → covered by `skills/workflow/adhd-workflow/` (NEW)

## Section additions (lightweight, not new skills)

PARTIAL commands get sections added to existing skills:

| Existing skill | Add coverage for |
|---|---|
| `skills/ci/SKILL.md` | `ci/generate`, `ci/validate` (currently PARTIAL — multi-project monorepo + best-practices linting) |
| `skills/release/SKILL.md` | `git/sync` workflow patterns |
| `skills/guard-audit/SKILL.md` | `git/{protect, protect-baseline, unprotect}` lifecycle |
| `skills/testing/test-generator/SKILL.md` | `test/template` lifecycle ops |
| `skills/docs/doc-classifier/SKILL.md` | `docs/{check, tutorial}` orchestration |

## Process per batch

1. **Spike** (one skill first if uncertain) — proves frontmatter + trigger-phrase shape
2. **Parallel dispatch** of remaining batch skills (one Agent call per skill, single message)
3. **Validate** — run `pytest -k skill`, regenerate `_cache.json`, smoke-test `/craft:hub`
4. **Deprecate** source commands — add `deprecated: true` + `replaced-by:` to frontmatter
5. **Update docs** — CLAUDE.md, REFCARDs, `_discovery.py` if needed (Tier-2 sweep)
6. **CHANGELOG entry + minor version bump**
7. **Release** via `/release`

## Summary stats

| Batch | New skills | Commands consolidated | Risk | Target |
|---|---|---|---|---|
| 1 wave 1 (spike) | 1 ✅ | 7 | low | done |
| 1 wave 2 | 2 | 17 | low | v2.34.0 |
| 2 | 4 | 10 | low–medium | v2.35.0 |
| 3 | 4 | 21 | medium | v2.36.0 |
| Cleanup | 0 | -30 (removed) | medium | v3.0.0 |
| **Net new** | **11** | **55 consolidated, 30 removed** | | |

Authoritative detail in the SPEC. This doc is the at-a-glance summary.
