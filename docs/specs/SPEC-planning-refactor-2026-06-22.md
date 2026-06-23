# SPEC-B — craft-internal Planning Refactor

> **Repo:** `~/projects/dev-tools/craft` · **Branch:** `dev` · **Date:** 2026-06-22
> **Status:** Design revised after adversarial review + interactive decision pass. Implementation
> gated on **A0 (live C2 verification)** and **SPEC-A / P2 (protocol)**.
> **Scope narrowed:** craft-internal generic-software planning only. Cross-plugin federation
> moved to **SPEC-planning-federation-2026-06-22 (SPEC-A)**. Orchestrate clarify/refactor moved
> to **SPEC-orchestrate-clarify-refactor-2026-06-22**.
> **Honesty note:** the collision "Resolution" column says **surfaced/mitigated**, not "resolved"
> — a visibility guard warns, it does not block.

---

## 0. Objective (reframed)

Give craft a **single predictable entry point** for generic software planning and **unambiguous
ownership per intent** — NOT fewer files for their own sake. The win is routing-disambiguation
plus a clean `/plan`↔`/do` seam, with real (phased) asset reduction via a deprecation horizon.

Earlier framing ("consolidate ~20 assets") was wrong on two counts: (1) it counted domain
planning that belongs to sibling plugins (now SPEC-A), and (2) the action list *added* assets.
This spec is honest about both.

## 1. Decision ledger (all rounds)

| # | Topic | Decision |
|---|---|---|
| **A0** | C2 premise | **Verify live first** — confirm superpowers `brainstorming` actually preempts craft before building anything. Everything downstream gates on the verdict. |
| D-enf | Enforcement | **Visibility-only.** Guard warns; never blocks. Register Resolution column = "surfaced," not "resolved." |
| D-A6 | superpowers handling | **Document precedence only.** No "disable" language — the manifest is all-or-nothing (no per-skill toggle), so disabling dupes while keeping additives is impossible. |
| D-guard | Drift-guard source | Read `~/.claude/settings.json:enabledPlugins["superpowers@claude-plugins-official"]` (a bool). **NOT** `installed_plugins.json` (install-only, no state, no per-skill granularity — verified). Match key by prefix (marketplace suffix varies). Fire-on-live-env-first. |
| D-rule | Global rules | **Hybrid shared-source**, but neutral-only (see SPEC-A / F3). Domain rules stay domain-scoped. |
| D-fd | feature-dev / full-stack | Audited under SPEC-A / P1 before any "conflict-free" claim. |
| D-router | `/do` vs `/plan` | **Seam composition** (see §4). `/plan` owns tiers 1–4; delegates execution to `/do` at the orchestrate seam; one-directional. |
| D-reduce | Consolidation | **Actually reduce, via deprecation horizon** — alias now, hard-delete at **v2.50.0**. |
| D-test | Test bar | **Behavioral tests gate the PR** (routing, alias warnings, guard live-env detection). |
| D-exec | Execution | **Gate on A0**; any write touching the shared rule file or `~/.claude` requires explicit confirmation (a craft `git revert` cannot restore non-craft-repo files). |
| D-ns | Namespacing | `/craft:plan` (NOT bare `/plan` — verify no clash with native plan mode / EnterPlanMode). |

## 2. Review lenses (D9, retained)

- **Code:** executor surface = `commands/_discovery.py`, `commands/_schema.json`,
  `commands/orchestrate/_workflow_schema.json`. Deprecated `plan/*` bodies are still parsed by
  discovery — alias stubs do NOT reduce that surface (see §6 / A3 caveat).
- **Architecture:** ADR §5.
- **Tech debt:** collision register §3.
- **Skill quality:** `project-planner` over-claims artifact verbs it does not own.

## 3. Collision register (Resolution = surfaced/mitigated, not resolved)

| # | Collision | Sources | Severity | Disposition |
|---|---|---|---|---|
| C1 | `project-planner` ↔ `plan-orchestrator` both fire on 'plan sprint/roadmap/feature' | craft-internal | HIGH | **A1** strip artifact verbs from project-planner (genuinely resolvable — craft owns both) |
| C2 | superpowers `brainstorming` HARD-GATE preempts craft | cross | **CRITICAL (unverified)** | **A0** verify first; if real → **surfaced** by A4 visibility guard (warn, not block) |
| C3 | `plan-orchestrator` ↔ superpowers `writing-plans` | cross | MED | **documented** (A6) — craft cannot disable a sibling skill |
| C4 | `orchestrate:resume`+`session-state` ↔ superpowers `executing-plans` | cross | MED | **documented** (A6) |
| C5 | user `brainstorm-mode`/`spec-only-mode` logic detached from craft | user↔craft | LOW-MED | **A5** hybrid shared-source (neutral only) |
| C6 | deprecated `plan/*` + `orchestrate/plan` bodies still parsed | craft-internal | LOW | **A3** alias stubs now → delete v2.50.0 |

## 4. The `/plan` ↔ `/do` seam (D-router — ADR core)

Two intents on one axis (**deliberate ↔ act**), mirroring `~/.claude/rules/action-verb-execution.md`:

```
/craft:plan  → brainstorm → spec → strategy → artifact ─┐  (tiers 1–4: DELIBERATION)
                                                         │ hands ORCHESTRATE/spec to
                                                         ▼
/craft:do    → complexity route → command / agent / orchestrator   (tier 5 + all direct ACTION)
```

Rules:

1. **`/craft:plan` owns tiers 1–4** (brainstorm → spec → strategy via `project-planner` →
   artifact via `plan-orchestrator`). It produces durable `SPEC-*.md` / `ORCHESTRATE-*.md` and
   then **stops** — it does NOT re-implement routing.
2. **Delegation at the seam:** `/plan`'s final step hands the artifact to `/craft:orchestrate`
   (or `/craft:do --orch`). `/do`'s existing complexity router is the ONLY execution engine —
   no duplicated heuristics.
3. **One direction only:** `plan → do`. `/do` may *suggest* `/plan` on deliberate-verb /
   high-uncertainty intent (soft nudge, consistent with visibility-only), but **never invokes**
   it — avoids circular delegation (§9 of the original).
4. **Intent classifier** seeds from the action-verb rule: deliberate verbs → `/plan`, action
   verbs → `/do`. `/do --plan X` is pure sugar forwarding to `/craft:plan X` (alias, not a mode).
5. **No plan mode on `/do`** — it would re-overload "do" and fork deliberation. `/do` keeps
   `--dry-run` for preview.

They do not overlap (different tiers); they compose (plan feeds do); they meet at exactly one
seam (orchestrate).

## 5. ADR — Architecture decision

**Context.** craft and superpowers run parallel generic-planning pipelines overlapping at every
tier. The most severe issue (C2) is upstream preemption — but it is **unverified**.

**Decision.** craft is the canonical home for **generic** planning (domain planning federates —
SPEC-A). Introduce `/craft:plan` as the single deliberation entry (tiers 1–4), composing with
`/craft:do` at the orchestrate seam. Tighten each craft skill's trigger surface so exactly one
asset owns each intent. Treat superpowers as **documented-precedence** (never edited in-cache,
never claimed "disabled"). A visibility guard **surfaces** active overlapping superpowers skills;
it does not block.

**Consequences.** (+) one predictable entry, unambiguous ownership, upstream-safe,
public-releasable. (−) C2/C3/C4 are surfaced not resolved (honest); alias shims persist until
v2.50.0; the guard is advisory.

### Target spine (canonical in craft, generic only)

```
/craft:plan  (deliberation entry — tiers 1–4)
  ├─ 1. BRAINSTORM   → craft brainstorm (absorbs brainstorm-mode FORMAT;
  │                    superpowers brainstorming SURFACED in craft repos, not blocked)
  ├─ 2. SPEC         → spec capture + spec-only-mode logic → docs/specs/SPEC-*.md
  ├─ 3. PLAN/strategy→ project-planner   (advice ONLY: estimation, agile, risk)
  └─ 4. PLAN/artifact→ plan-orchestrator (ORCHESTRATE, feature/sprint/roadmap)
        │ seam (one-directional)
        ▼
/craft:do / /craft:orchestrate  (tier 5: EXECUTE — existing engine, unchanged)
```

(Canonical brainstorm = `craft:workflow:brainstorm`; the bare `workflow:brainstorm` alias is
reconciled in A1.)

## 6. Action list (revised)

| # | Where | Action | Gate | Kills |
|---|---|---|---|---|
| **A0** | craft repo (read-only) | **Verify C2 live.** In a craft repo, issue "let's build X"; if superpowers `brainstorming` auto-activates before any craft asset, C2 is real. Test the `/do` path too (it shares the intent surface). Record verdict. | none | premise check |
| A1 | craft | Tighten `skills/planning` (`project-planner`) → **strategy verbs only** (estimate, agile, risk). Remove artifact verbs → owned by plan-orchestrator. Reconcile the two brainstorm entries to one canonical. | — | C1 |
| A2 | craft | Add `commands/plan.md` = **`/craft:plan` dispatcher, tiers 1–4**, delegating execution to `/craft:do`/`orchestrate` at the seam (§4). One-directional. Keep `/craft:plan:{feature,sprint,roadmap}` as alias shims. | SPEC-A/P2 | C2 (entry) |
| A3 | craft | Convert deprecated `plan/{feature,roadmap,sprint}` + `orchestrate/plan` bodies → **thin alias stubs + deprecation warning, slated for removal in v2.50.0**. *Caveat: stubs are still parsed/counted by discovery; the surface shrinks only at v2.50.0 deletion.* | — | C6 |
| A4 | craft | **Visibility-only** drift-guard: reads `settings.json:enabledPlugins` (prefix-match `superpowers@…`); if enabled, emit a WARN that lists overlapping skills + recommends `/craft:plan` precedence. **Never disables, never blocks.** Fire-on-live-env-first. Re-runs after plugin updates. | A0 (only if C2 real) | C2,C3,C4 (surface) |
| A5 | user↔craft | **Hybrid shared-source** for NEUTRAL rules (`brainstorm-mode` format, `spec-only-mode`). Domain rules (`draft-as-dev-research`, `research-session-defaults`) stay domain-scoped per SPEC-A/F3. Cross-boundary writes **require confirmation**. | D-exec | C5 |
| A6 | upstream (doc only) | **Document precedence only** — recommend nothing be disabled (all-or-nothing manifest sacrifices the additive `subagent-driven-development` / `dispatching-parallel-agents`). Never edit cache. | — | C3,C4 (doc) |
| A7 | scope | Sibling + feature-dev/full-stack audit → **SPEC-A / P1**. | — | — |
| **A8a** | craft | **Behavioral tests** (PR gate): `/craft:plan` routes each intent to the right asset; alias stubs emit deprecation warnings; drift-guard detects live `enabledPlugins` state on the real env. | — | D-test |
| A8b | craft | Docs + counts cascade: REFCARD, hub, `docs/skills-agents.md`, `mkdocs.yml` nav, CHANGELOG `[Unreleased]`; `validate-counts.sh` + `docs-staleness-check.sh`. **Note:** adding `/craft:plan` triggers the ~30-file count cascade; v2.50.0 deletion triggers another. | — | — |

## 7. Drift guard (A4 detail)

On session start inside a craft repo: read `~/.claude/settings.json` → `enabledPlugins`;
prefix-match `superpowers@`. If enabled AND craft `/plan` precedence is not configured, emit a
compact WARN + the one-line resolution ("use `/craft:plan`; superpowers brainstorming may
preempt — see docs"). Re-runs after plugin updates (clobber protection). **Visibility, not
prevention** — mirrors the shipped v2.45.0 SessionStart governance hook. Validate the checker on
the live env before wiring (a false positive poisons any soak ledger — memory
`r04-content-drift-not-filetype`).

## 8. Migration & rollback (honest)

- craft-repo changes are additive + reversible: `git revert <impl-commit>` restores them.
- **A5 caveat:** edits to `~/.claude` / the shared rule file are **outside the craft repo** — a
  craft revert does NOT restore them. Hence D-exec: A5 is a separate, confirmed, separately-
  revertable step.
- Aliases (A3) keep old command references working until the v2.50.0 deletion.

## 9. Effort (honest)

Not 60–90 min. `/craft:plan` dispatcher + seam wiring + visibility guard + neutral-rule hybrid +
alias stubs + behavioral tests + the count cascade ≈ **half a day**, and that is *after* A0 and
SPEC-A/P2 clear. If A0 shows no preemption, A4 (and most of the superpowers story) drops out and
the job shrinks to "`/craft:plan` entry + seam + count hygiene."

## 10. Gating order (execution contract)

1. **A0** (live C2 verify) — read-only, runnable now.
2. **SPEC-A / P2** (protocol) — `/craft:plan` cannot finalize its domain-defer shape without it.
3. Then a worktree for A1–A8 with cross-boundary confirmations. If A0 = no preemption, prune A4.
