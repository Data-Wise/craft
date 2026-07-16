# Spec: folio Split — Dynamic-Workflow Execution

> **Status:** AMENDED post-review (2026-07-09) — 3-lens adversarial review (6 blockers + 9
> majors) + border filter + v4-target all folded in; see the ORCHESTRATE for the task-level
> detail. Awaiting CP-A approval; no implementation yet.
> **Executes:** `docs/plans/ORCHESTRATE-folio-split.md` (Phases 1–4; Phase 0 ✅ complete + verified)
> **Architecture grill:** `docs/specs/GRILL-folio-split-2026-07-09.md` (B1–B5 locked)
> **Execution grill:** `docs/specs/GRILL-folio-split-workflow-2026-07-09.md` (W1–W2 locked; W3–W5
> resolved HERE as spec decisions)
> **Date:** 2026-07-09

## Objective

Execute the folio split (craft v4.0.0 / folio v1.0.0) using Claude Code's native dynamic
`Workflow()` tool for the parallelizable work inside each phase, while the live parent session
owns the serial phase spine, every go/no-go gate, and all git operations. Post-border-filter
shape: **craft 69** after the split (→ **~22** after the Phase 3.5 v4 rider), **folio ≈15
commands + 6 agents + 6 skills**; 7 already-deprecated commands die at the border with ADR-002
salvage. Success = the ORCHESTRATE's acceptance criteria met, with each gate cleared on
schema-validated, adversarially-verified Workflow evidence — the same method that shipped
Phase 0.

## Locked Execution Decisions

### W1 — Workflow's role (LOCKED, grill)

Fan-out INSIDE phases; the parent drives the phase sequence and every gate. No single
all-phases Workflow script — breaking steps (new repo, craft v4.0.0) keep a human checkpoint.

### W2 — cross-repo execution (LOCKED, grill)

Parent runs ALL git ops (worktree add, **`git filter-repo`** — NOT `subtree split`, which takes
one prefix and cannot express the scattered moves-set (review blocker B1) — repo create,
commits, pushes).
Agents receive explicit absolute paths — `~/.git-worktrees/craft/feature-folio-split` (craft)
or `~/projects/dev-tools/folio` (folio) — and do only file-content work. NO
`isolation:'worktree'` anywhere (conflicts with history preservation; matches the proven
`dynamic-workflow-runs-from-worktree-session` pattern).

### W3 — which phases get Workflows (spec decision)

| Phase | Parent inline | Workflow fan-out |
|---|---|---|
| 1 scaffold | repo create (public!), branches, protect-baseline, plugin.json, CLAUDE.md | **wf-p1-tooling**: 5 agents adapt the 5 count/bump scripts to folio + 1 adversarial verifier |
| 2 extraction | `git filter-repo` + graft, commits, CI + release-choreography authoring, `/folio:hub` | **wf-p2-repoint**: `pipeline(movedFiles ≈16, rewrite → verify)`; **wf-p2-verify**: counts + structure + spot-E2E fan-out |
| 3 amputation | `git rm` leaving-set, hub/do rebuild (staying-set + breadcrumb), enumerated test edits, **ci.yml floor edit**, `bump-version.sh` counts (parent-only), suites | **wf-p3-sweep**: docs-content grep-sweep agents on DISJOINT non-count files (grep-zero gate); **wf-p3-gate**: 3 adversarial verifiers on the self-build evidence |
| 4 release | version bumps, PRs, releases, tap/marketplace | **wf-p4-verify**: post-release surface checks (both suites, brew audit, site deploys) |

Rationale: Workflows go where ≥3 independent same-shaped work items exist (script adaptation,
per-file repoint, batch sweep, multi-lens verification); everything touching git or a gate stays
in the parent. Phase 1's repo creation and Phase 4's release choreography are inherently serial.

### W4 — schemas + verification (spec decision)

Every `agent()` call uses a structured-output schema (P0 pattern). Three canonical shapes:

- `EDIT_RESULT`: `{files_edited[], refs_changed, notes}` — mutation agents
- `VERDICT`: `{sound: bool, violations[], coverage_gaps[], verdict}` — verifiers, prompted to
  REFUTE (default `sound: false` on any finding)
- Gate evidence = parent-run command transcripts (suites, `mkdocs build --strict`,
  `git log --follow`) + a Workflow verifier pass over them. No transcript → gate not cleared.

### W5 — budget + concurrency (spec decision)

Reference: P0 = 7 agents / ~510k subagent tokens. Post-border-filter estimates: P1 ~6 agents,
P2 ~15–35 (pipeline over ≈16 moved files, 2 stages each — the kill-list cut this ~40%),
P3 ~10, P4 ~4. Total ≈ **1–1.8M subagent tokens** (excl. the Phase 3.5 rider, budgeted at its
own roster grill). Per-Workflow default concurrency cap applies; no
`model` overrides (inherit session model). If a Workflow errors mid-run, resume via
`resumeFromRunId` (never re-run completed agents; check `journal.jsonl` first).

## Tech Stack

Claude Code dynamic `Workflow()` (agent/pipeline/parallel, structured schemas, resume) ·
git worktree + `git subtree split` · craft's Python/pytest + bash CI suites · folio: mirrored
suites (Phase 1 adaptation) · mkdocs · `gh` CLI.

## Commands (gate verification, run by PARENT in the tree that ships)

```bash
# craft (worktree absolute path)
python3 -m pytest tests/                       # full suite
bash tests/test_git_shim_correctness.sh        # + other Validate-Plugin-Structure bash suites
./scripts/validate-counts.sh
mkdocs build --strict                          # Phase 3.4 gate proof
# folio
python3 -m pytest tests/ && ./scripts/validate-counts.sh && mkdocs build --strict
git log --follow <moved-file>                  # history-preservation proof (Phase 2 gate)
```

## Project Structure

```
~/.git-worktrees/craft/feature-folio-split/    → craft-side changes (Phases 2–4)
~/projects/dev-tools/folio/                    → NEW public repo (Phase 1); main←dev←feature/*
tasks/plan.md, tasks/todo.md                   → working artifacts, feature-branch only, NEVER merged to dev
docs/specs/SPEC-folio-split-workflow-*.md      → this spec (committed to dev)
```

## Workflow-Script Style

One exemplar (wf-p2-repoint core) — pipeline, no barrier, schema-validated, phase-tagged:

```js
const results = await pipeline(
  movedFiles,   // absolute paths in the folio repo, from the parent's graft
  f => agent(`Rewrite /craft: self-refs to /folio: in ${f}. Do NOT touch counts or
    frontmatter names. Repo root: /Users/dt/projects/dev-tools/folio (READ/EDIT this file only,
    never run git).`, { label: `repoint:${f}`, phase: 'Repoint', schema: EDIT_RESULT }),
  (r, f) => agent(`REFUTE: grep ${f} for any remaining /craft: self-ref or a broken
    cross-ref introduced by the rewrite. sound=false on ANY hit.`,
    { label: `verify:${f}`, phase: 'Verify', schema: VERDICT })
)
```

## Testing Strategy

Per ORCHESTRATE's scaffold: unit (folio's adapted count scripts), integration (craft release
doc-sync WITHOUT moved commands — the 3.4 gate), dependency (folio↔docs-standards absence
fallback), count-cascade both repos, e2e (one moved command produces equivalent output
post-move), dogfood (`/craft:do` with DOCS/SITE removed; `/folio:do` routes its own). Parent
runs ALL suites; Workflows only author/verify content. pytest ≠ bash suites — both run at
every craft gate (memory `pytest-doesnt-cover-craft-ci-bash-suites`).

## Boundaries

- **Always:** agents get absolute paths + "never run git" in every prompt · schema on every
  agent call · adversarial verify before any gate clears · ADR-002 salvage-then-delete for
  every removal (border kills AND 3.5 shim-kills) — MIGRATION-v4.md is the cross-repo safety
  net (the ADR-002 *test* can't see targets in another repo) · **parent commits after each
  completed Workflow batch** (dirty-tree recovery) · counts via bump-version.sh only ·
  leak-scan before every push · record each phase outcome into the ORCHESTRATE immediately.
- **Ask first (AskUserQuestion, Recommended-first):** create the folio repo · every push ·
  every PR merge · protection changes · entering each next phase · both releases (v4.0.0/v1.0.0)
  · any budget overrun beyond the W5 estimate.
- **Never:** agents run git or gh · `isolation:'worktree'` · manual count edits (bump-version.sh
  owns them) · force-push · merge on a failed or missing gate transcript · folio created private.

## Success Criteria

1. Each of Phases 1–4 exits only on its ORCHESTRATE gate with parent transcripts +
   verifier `sound: true`.
2. `git log --follow` shows craft-era history on ≥3 sampled moved files (Phase 2).
3. craft full suite (pytest AND bash, **incl. the edited ci.yml floors**) green at **69**
   post-P3 (→ ~22 after the 3.5 rider); folio green at **≈15/6/6**.
4. craft builds + deploys its own site with zero moved commands AND **grep-zero prose refs**
   to the leaving-set across docs/ (the strict build alone is a false-green — review B6).
5. `MIGRATION-v4.md` maps every moved/killed command, breadcrumbed from README/CHANGELOG/hub;
   both repos release independently — **folio first, craft tag last**, rollback runbook
   written before either.
6. Total subagent spend within the W5 envelope (report actuals per phase).

## Resolved (were Open Questions)

- `docs:claude-md:*` trio: **STAYS in craft as one unit** (border filter — craft-internal
  CLAUDE.md governance; fixes review B5's double-booking).
- folio's docs site: **minimal folio-built site at v1.0.0** — Phase 2.4's own exit criterion
  requires it, and launching the docs-authoring plugin without a dogfooded site was
  self-contradictory (review UX-F6). README-only recommendation withdrawn.
