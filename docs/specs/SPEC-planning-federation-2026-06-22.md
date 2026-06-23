# SPEC-A — Ecosystem Planning Federation

> **Repo:** `~/projects/dev-tools/craft` (protocol owner) · **Branch:** `dev` · **Date:** 2026-06-22
> **Status:** Design. Gated on a full cross-plugin planning audit (Phase 1) before any conformance work.
> **Supersedes:** the "craft = canonical home for ALL planning" framing of `SPEC-planning-refactor-2026-06-22` (now SPEC-B, craft-internal).
> **Pairs with:** SPEC-B (craft-internal `/plan` refactor, conforms to this protocol) · SPEC-orchestrate-clarify-refactor.

---

## 0. Objective

Define a **federated** planning model across the plugin ecosystem. craft owns **generic
software/git-workflow planning** and **the cross-plugin planning protocol**; the domain
plugins (savant, rforge, scholar) own their **domain** planning and *conform* to the
protocol. No plugin absorbs another's domain. The deliverable is a **protocol + a boundary
map**, not a refactor of any sibling.

This replaces the original spec's unscoped premise — it declared craft the canonical home
for "~20 planning assets" while never examining the three sibling plugins that run parallel,
domain-specific planning.

## 1. Why federation, not centralization (the fault being corrected)

The word "planning" conflated two different things:

- **Generic planning** — feature/sprint/roadmap, ORCHESTRATE, git-workflow. craft's domain;
  this is where the superpowers collision lives (SPEC-B / C2).
- **Domain planning** — research lifecycle (Idea→Identification→…→Submission), CRAN
  submission sequencing, course/semester planning. Own rules, own branch model
  (`draft` not `dev`), own methodology (estimation-not-NHST), own homes.

Folding domain planning into craft (original D1 + A5) would pull research/teaching logic into
a plugin that does not ship in research or teaching contexts — a domain-boundary violation
that also fights the "keep research enforcement intact" decision.

## 2. Locked decisions

| # | Decision | Choice |
|---|---|---|
| F1 | Planning authority | **Federated** — craft owns generic planning + the protocol; domains own their planning |
| F2 | Domain routing | `/craft:plan` **detects repo domain and defers** to the domain planner; never intercepts |
| F3 | Domain rules | Stay **domain-scoped**; the shared rule file holds **domain-neutral conventions only** |
| F4 | Sibling treatment | **Full cross-plugin planning audit** before certifying any "conflict-free" claim |
| F5 | Conformance | Domains conform to the protocol; craft never edits sibling internals |

## 3. The federation map

```
craft  = generic SW/git planning  +  THE cross-plugin PROTOCOL
         (spec format · ORCHESTRATE/WORKFLOW format · docs/specs/ convention · branch model)
                                   │ conform to
        ┌──────────────────────────┼───────────────────────────┐
   savant (research)          rforge (R / CRAN)           scholar (teaching)
   /savant:plan:* ×9          cascade · release · next     teaching:syllabus · config
   analysis-plan, gap,        (coordinated updates,        (course/semester planning)
   hypothesis, method-scout,  CRAN submission order,
   config, obsidian-sync,     ecosystem next-task)
   recap, resubmit, tutor
        └──── own their domain planning; craft DEFERS, never intercepts ────┘
```

### 3a. Domain-planning surfaces (audit seed — Phase 1 confirms/extends)

| Plugin | Domain | Known planning surface | Branch model | Methodology notes |
|---|---|---|---|---|
| savant | research | `/savant:plan:*` (9 cmds) | `draft` | estimation-not-NHST, research lifecycle |
| rforge | R packages | `cascade`, `release`, `next` | per-repo (some `dev`) | CRAN gates, revdep order |
| scholar | teaching | `teaching:syllabus`, `teaching:config` | per-repo | semester progress |
| craft | generic SW | `/craft:plan` (SPEC-B), orchestrate | `main←dev←feature/*` | — |

## 4. The protocol craft owns (the conformance contract)

A domain plugin "conforms" by honoring these craft-defined conventions — nothing more:

1. **Spec format & location** — durable specs as `docs/specs/SPEC-<topic>-<date>.md`.
2. **Orchestration artifact format** — `ORCHESTRATE-*.md` / `WORKFLOW-*.yaml` shape that
   `/craft:orchestrate` and `:drive`/`:workflow` engines can consume.
3. **Branch/worktree model** — the `main ← integration ← feature/*` pattern, with the
   `draft`=integration mapping for research repos (already in `draft-as-dev-research`).
4. **Decision-ledger convention** — locked-decision tables at the top of a spec.

craft provides these as **documented conventions + optional shared helpers**; it does **not**
reach into sibling command bodies. A domain plugin may adopt none, some, or all — conformance
is a recommendation surfaced by the planning drift-guard (SPEC-B / visibility-only), never
enforced.

## 5. Domain-defer routing contract (F2)

`/craft:plan` (defined in SPEC-B) MUST:

1. **Detect domain** from the repo: R-package (DESCRIPTION/`rforge`), research
   (`~/projects/research/*` or `draft` branch + savant markers), teaching (scholar markers).
2. **If a domain is detected** → defer: surface "this looks like a `<domain>` repo — use
   `/<domain>:plan…`" and **stop** (or hand off if an unambiguous mapping exists). Never run
   craft-generic planning over a domain repo.
3. **Else** → run craft-generic planning (SPEC-B tiers 1–4).

One direction only. craft defers *to* domains; domains are never required to call back into
craft. This avoids the circular-delegation risk and keeps craft decoupled from sibling internals.

## 6. Domain rules vs neutral shared file (F3)

| Rule | Domain | Disposition |
|---|---|---|
| `research-session-defaults.md` | research | **stays domain-scoped** (savant / global-but-tagged); craft never owns it |
| `draft-as-dev-research.md` | research | stays domain-scoped (already enforced by branch-guard) |
| `brainstorm-mode.md` | neutral-ish | format conventions → may live in the **neutral shared file** |
| `spec-only-mode.md` | neutral | spec-discipline → **neutral shared file** |

The SPEC-B "hybrid shared-source file" holds **only domain-neutral** planning conventions.
Research/teaching rules keep enforcing in their own repos; craft references them, never absorbs
them. This corrects original-A5.

## 7. Phases

| Phase | Gate | Output |
|---|---|---|
| **P1 — Audit** | none (read-only) | Full inventory of planning surfaces across savant/rforge/scholar/craft/superpowers/feature-dev/full-stack-orchestration; the boundary map; collisions that cross plugin lines |
| **P2 — Protocol** | P1 complete | The conformance contract (§4) written as a craft doc + the domain-defer routing contract (§5) |
| **P3 — Conformance (per domain, optional)** | P2 + domain owner opt-in | Each domain plugin adopts the conventions it wants; no craft edits to siblings |

craft-internal `/plan` work (SPEC-B) is **gated on P2** — craft cannot finalize its own
`/plan` shape until the protocol it must conform to exists.

## 8. Non-goals

- No refactor of savant/rforge/scholar planning (audit + boundary only).
- No "super-dispatcher" that routes into sibling internals (rejected — couples craft to every
  sibling).
- No absorption of domain rules or domain branch models.

## 9. Open questions for P1

- Do any sibling planning commands carry their own HARD-GATE-style preemption (a cross-plugin
  C2)? The conflict-free claim is unprovable until this is answered.
- Is there a clean, machine-detectable domain signal for F2 routing, or does `/craft:plan` need
  an explicit `--domain` escape hatch?
- Does `feature-dev` / `full-stack-orchestration` planning collide with craft generic planning,
  the domains, or both?
