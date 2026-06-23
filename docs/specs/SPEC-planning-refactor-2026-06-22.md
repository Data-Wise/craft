# SPEC — Planning Asset Audit & Refactor

> **Repo:** `~/projects/dev-tools/craft` · **Branch:** `dev` · **Date:** 2026-06-22
> **Status:** Audit complete (read-only). Implementation queued (A1–A8).
> **Decisions:** D1–D12 locked (all recommended options).

---

## 0. Objective

Consolidate ~20 scattered planning assets across **craft + superpowers + user-level + official plugins** into one conflict-free planning spine, with **craft as the canonical home**, eliminating trigger collisions without mutating upstream-managed plugins.

## 1. Locked decisions (D1–D12)

| # | Decision | Choice |
|---|---|---|
| D1 | Canonical home | **craft** |
| D2 | Consolidation model | Keep specialized assets + add `/plan` router/index |
| D3 | Upstream posture | Delegate-to where craft adds value; disable pure dupes; document rest |
| D4 | Collision handling | Tighten skill descriptions + craft index as single entry point |
| D5 | Drift protection | Add drift-check to craft guard system |
| D6 | feature-dev / full-stack-orchestration | Inventory only, no refactor |
| D7 | Execution depth | Report + auto-execute craft-only changes with rollback, same run |
| D8 | User-level (`~/.claude`) | Keep storage at user-level; fold rule *logic* into craft skills; thin pointers |
| D9 | Review rigor | Run all 4 lenses |
| D10 | Trigger ergonomics | Granular `/plan:*` + add `/plan` dispatcher |
| D11 | Backward-compat | Aliases + deprecation warnings (no breakage) |
| D12 | Publishability | Design for public release (docs + tests) |

## 2. Review lenses applied (D9)

- **Code** (`engineering:code-review` + craft `check`/`code`): executor surface = `commands/_discovery.py`, `commands/_schema.json`, `commands/orchestrate/_workflow_schema.json`. Finding: deprecated `plan/*` command bodies are dead weight still parsed by discovery.
- **Architecture** (`engineering:architecture` ADR + `system-design`): see ADR §5.
- **Tech debt** (`engineering:tech-debt`): collision register §4.
- **Skill quality** (`skill-creator` + superpowers `writing-skills`): `project-planner` description over-claims artifact verbs it does not own.

## 3. Inventory

### 3a. craft — editable (source of truth)

| Asset | Type | Role | State |
|---|---|---|---|
| `skills/planning/` (`project-planner`) | skill | Strategy/advice (estimation, agile, risk) | **active — over-broad triggers** |
| `skills/orchestration/plan-orchestrator/` | skill | Artifact generator (ORCHESTRATE, feature/sprint/roadmap) | active — canonical artifact engine |
| `skills/orchestration/{workflow-engine,drive-engine,task-analyzer,session-state}/` | skill | Execution / routing / state | active |
| `skills/modes/` | skill | Mode system | active |
| `commands/plan/{feature,roadmap,sprint}.md` | command | Plan sub-commands | **deprecated → plan-orchestrator** |
| `commands/orchestrate/plan.md` | command | Spec → ORCHESTRATE → worktree | **deprecated → plan-orchestrator** |
| `commands/orchestrate/{drive,workflow,resume}.md` | command | Orchestration / resume | active |
| `commands/do.md` | command | Universal router (complexity score, agent delegation, pipeline suggestion) | active |
| `commands/orchestrate.md` | command | Launch orchestrator | active |

### 3b. superpowers 6.0.3 — upstream (shadow / disable / delegate only)

| Skill | Role | Overlap |
|---|---|---|
| `brainstorming` | HARD-GATE: 'MUST use before any creative work' | preempts craft brainstorm→spec pipeline |
| `writing-plans` | Impl plan from spec, before code (TDD) | dupes plan-orchestrator |
| `executing-plans` | Execute written plan w/ checkpoints | dupes orchestrate:resume + session-state |
| `subagent-driven-development` | Delegate to subagents | **no craft equivalent — additive** |
| `dispatching-parallel-agents` | Parallel fan-out | **no craft equivalent — additive** |
| `verification-before-completion` | Verify gate | partial overlap w/ craft `check`/verify |

### 3c. user-level `~/.claude` — editable

| Asset | Role | Plan |
|---|---|---|
| `rules/brainstorm-mode.md` | Brainstorm output format | fold logic → craft (D8) |
| `rules/spec-only-mode.md` | 'create a spec' = stop; no code on dev; worktree required | fold logic → craft (D8) |
| `rules/draft-as-dev-research.md` | Draft handling | fold logic → craft (D8) |
| `commands/workflow.md` | Workflow command | reconcile w/ craft workflow |
| `plans/` | Transient plan storage | **keep at user-level** (storage) |

### 3d. official — inventory only (D6)

`feature-dev` and `claude-code-workflows/full-stack-orchestration` contain suspected plan/orchestrate commands. Catalog in next session; **no refactor**.

## 4. Collision register (tech-debt lens, ranked)

| # | Collision | Sources | Severity | Resolution |
|---|---|---|---|---|
| C1 | `project-planner` ↔ `plan-orchestrator` both fire on 'plan sprint/roadmap/feature' | craft-internal | **HIGH** | A1: strip artifact verbs from project-planner |
| C2 | superpowers `brainstorming` HARD-GATE preempts craft pipeline | cross | **CRITICAL** | A2+A4: craft `/plan` single entry + drift-guard precedence |
| C3 | `plan-orchestrator` ↔ superpowers `writing-plans` (spec→plan) | cross | MED | A6: craft owns (ORCHESTRATE+worktree); disable dupe in craft repos |
| C4 | `orchestrate:resume`+`session-state` ↔ superpowers `executing-plans` | cross | MED | A6: craft owns (worktree+.STATUS aware); disable dupe |
| C5 | user `brainstorm-mode`/`spec-only-mode` logic detached from craft | user↔craft | LOW-MED | A5: fold logic in, thin pointers |
| C6 | deprecated `plan/*` + `orchestrate/plan` bodies still in tree | craft-internal | LOW | A3: convert to alias stubs |

## 5. ADR — Architecture decision

**Context.** craft and superpowers are two complete, parallel planning pipelines overlapping at every tier (brainstorm → spec → plan → orchestrate → execute). The most severe issue is upstream preemption (C2).

**Decision.** craft is the canonical planning home. Introduce a `/plan` **dispatcher** as the single entry point; tighten each skill's trigger surface so exactly one asset owns each intent; treat superpowers as either delegated-to (where it uniquely adds value) or disabled (pure dupes), never edited in-cache.

**Consequences.** (+) one predictable entry, no ambiguous routing, upstream-safe, public-releasable. (−) requires a drift-guard to catch upstream re-enabling the HARD-GATE after updates; alias shims must persist for back-compat.

### Target spine (canonical in craft)

```
/plan  (NEW dispatcher — single entry, routes by intent)
  |- 1. BRAINSTORM   -> craft brainstorm (absorbs brainstorm-mode format;
  |                     supersedes superpowers brainstorming IN craft repos)
  |- 2. SPEC         -> spec capture + spec-only-mode logic -> docs/specs/SPEC-*.md
  |- 3. PLAN/strategy-> project-planner   (advice ONLY: estimation, agile, risk)
  |- 4. PLAN/artifact-> plan-orchestrator (ORCHESTRATE, feature/sprint/roadmap)
  `- 5. ORCHESTRATE/ -> orchestrate (drive/workflow/resume) + do.md router;
        EXECUTE         session-state
```

## 6. Action list (executable — craft-only auto-exec under D7)

| # | Where | Action | Kills |
|---|---|---|---|
| **A1** | craft | Tighten `skills/planning` (`project-planner`) description → **strategy verbs only** (estimate, agile coaching, risk advice). Remove artifact verbs ('create a roadmap', 'plan a sprint', 'break down a feature') → owned by plan-orchestrator. | C1 |
| **A2** | craft | Add `commands/plan.md` **dispatcher** = single entry routing the 5 tiers. Keep `/plan:{feature,sprint,roadmap}` as alias shims. | C2 |
| **A3** | craft | Convert deprecated `plan/{feature,roadmap,sprint}` + `orchestrate/plan` bodies → thin alias stubs invoking plan-orchestrator + deprecation warning (D11). | C6 |
| **A4** | craft | Add planning-precedence doc + **drift-check** in guard system: detect active superpowers `brainstorming`/`writing-plans`/`executing-plans`; warn + recommend scope/disable; re-run after plugin updates (D5). | C2,C3,C4 |
| **A5** | user→craft | Fold `brainstorm-mode` + `spec-only-mode` + `draft-as-dev-research` logic into craft skills; replace user rules with thin pointers (D8). Keep `~/.claude/plans/` as storage. | C5 |
| **A6** | upstream (doc only) | Recommend disabling superpowers `writing-plans` + `executing-plans` as pure dupes in craft repos; **keep** `subagent-driven-development` + `dispatching-parallel-agents` (additive). Document — never edit cache (D3). | C3,C4 |
| **A7** | scope | Inventory `feature-dev` + `full-stack-orchestration` planning commands; no refactor (D6). | — |
| **A8** | craft | Docs for public release (D12): REFCARD, hub, `docs/skills-agents.md`, `mkdocs.yml` nav, CHANGELOG `[Unreleased]`; run `validate-counts.sh` + `docs-staleness-check.sh`. | — |

## 7. Drift guard (D5)

craft guard rule that, on session start inside a craft repo, reads `~/.claude/plugins/installed_plugins.json`; if `superpowers` is enabled and the `brainstorming` HARD-GATE / `writing-plans` / `executing-plans` lack craft precedence config, emit a warning + resolution. Re-runs after plugin updates (clobber protection against upstream re-enabling the gate).

## 8. Migration & rollback

- All craft changes **additive + reversible**; deprecated commands become aliases → **zero breakage** (D11).
- Single `git revert <impl-commit>` restores prior state.
- Upstream untouched → zero rollback risk there.

## 9. Failure states handled

- Superpowers update silently re-enables HARD-GATE → drift guard (A4) catches.
- Older doc references a deprecated command → alias stub persists indefinitely w/ warning.
- Circular delegation craft→superpowers→craft → precedence doc forbids.
- Orphaned `~/.claude/plans/*.md` → add `/plan:gc` (future).

## 10. Next session

Execute **A1–A8** (craft-only auto-exec authorized under D7). Estimated **60–90 min**. Start: read this spec → A1 → A2 → … → A8 → CHANGELOG + counts → PR `dev`.
