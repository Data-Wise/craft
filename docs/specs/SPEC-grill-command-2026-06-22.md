# SPEC — `/craft:grill` Command (ported from `grill-me`)

> **Repo:** `~/projects/dev-tools/craft` · **Branch:** `dev` · **Date:** 2026-06-22
> **Status:** Design (captured from `/craft:workflow:brainstorm -d -s`). Implementation needs a worktree.
> **Origin:** ports mattpocock's `/grill-me` + `grill-with-docs` (Claude Code marketplace), adapted to craft.
> **Pairs with:** SPEC-B (planning-refactor — grill is the "interrogate" step in the `/plan` spine) ·
> SPEC-orchestrate-clarify-refactor (orchestrate Step 0.5 invokes `/craft:grill`).

---

## 0. Objective

Add `/craft:grill` — an adversarial, one-question-at-a-time interrogation command that
stress-tests a plan/spec (or a bare topic), walks the design tree resolving dependent decisions,
proposes a recommended answer for every question, reads the codebase to auto-resolve what it can,
and captures the result as a durable decision-ledger spec that feeds the `/plan → /do` pipeline.

This is the productized form of the manual grilling done throughout the 2026-06-22 planning
session and the interrogation engine the orchestrate Step 0.5 Clarify will reuse.

## 1. Source mechanics (faithful port target)

The `grill-me` three directives (verbatim):

> "Interview me relentlessly about every aspect of this plan until we reach a shared
> understanding. Walk down each branch of the design tree, resolving dependencies between
> decisions one-by-one. For each question, provide your recommended answer. Ask the questions one
> at a time. If a question can be answered by exploring the codebase, explore the codebase
> instead."

Properties: one-question-at-a-time · recommended answer per question · codebase-first ·
design-tree traversal (Brooks, *The Design of Design*) · stop when every branch resolves (no
fixed count) · output must feed a durable artifact. `grill-with-docs` adds on-the-spot ADR +
glossary (`CONTEXT.md`) updates.

## 2. Locked decisions (brainstorm `-d`, 8 branches)

| # | Branch | Decision |
|---|---|---|
| G1 | Form factor | **Standalone `/craft:grill` command** (not a brainstorm mode; not a hidden engine). |
| G2 | Interaction model | **True one-at-a-time, free-text**, with a recommended answer on every question. NOT AskUserQuestion batches — this is the deliberate exception to craft's batch convention, because decision-tree fidelity is the point. |
| G3 | Codebase-first | **Read-then-confirm.** Auto-resolve from repo evidence (`.STATUS`, git, specs, command tree, `settings.json`…), but SHOW each auto-answer as an overridable recommended answer rather than silently skipping. |
| G4 | Input contract | **Accept a target artifact OR a bare topic.** Prefer an artifact (spec/plan/ORCHESTRATE/diff); on a bare topic, sketch a skeleton first, then grill it. |
| G5 | vs brainstorm | **Generate vs interrogate.** brainstorm = divergent (expands the option space); grill = convergent (attacks a position for gaps/contradictions). Documented in both command headers so users pick correctly. |
| G6 | Output / handoff | **Decision-ledger spec** → `docs/specs/SPEC-*.md`, then offer handoff to `/plan` tier 4 (plan-orchestrator) → ORCHESTRATE → `/do` seam (per SPEC-B §4). |
| G7 | Docs-on-the-spot | **Full grill-with-docs** — maintain a live decision ledger AS the interview proceeds, plus ADRs + a `CONTEXT.md` glossary updated on the spot (phased — see §6). |
| G8 | Orchestrate integration | **orchestrate Step 0.5 Clarify invokes `/craft:grill --bound 2 --no-capture`** — one interrogation implementation, reused. `--no-capture` prevents the embedded pass from writing a `GRILL-*` spec mid-orchestration (decisions return inline). Reconciles SPEC-orchestrate-clarify. |
| G9 | Embedded interaction mode | When grill is invoked **embedded** (orchestrate Step 0.5), it runs bounded + no-capture; the host flow's AskUserQuestion rhythm resumes after. Standalone grill keeps the one-at-a-time free-text loop. The mode switch is deliberate and documented so it doesn't read as an unflagged UX seam. |
| G10 | Progress + halt UX | **Milestone checkpoints** every N branches (default 5; reuse brainstorm's milestone pattern: "keep going / wrap up / show ledger so far") so an unbounded interrogation stays ADHD-friendly. **Halt token** is a distinct sentinel — empty-enter or `/done` — NOT the bare word "stop" (which can be a legitimate answer). |

## 3. Behavior (the contract)

```
/craft:grill [target]        # target = spec path | topic | (empty → detect from context)
/craft:grill <spec.md>       # interrogate an existing artifact (preferred)
/craft:grill "<topic>"       # sketch skeleton, then interrogate
/craft:grill --yes           # auto-accept recommended answers (fast pass)
```

Flow:

1. **Resolve target (G4).** Artifact present → load it. Bare topic → sketch a 3–5 bullet skeleton,
   show it, then grill. Empty → detect from `.STATUS`/branch/recent work.
2. **Codebase-first sweep (G3).** Before asking, read repo evidence and pre-answer every branch you
   can. Each pre-answer becomes a recommended answer the user can override.
3. **Grill loop (G2).** One free-text question per turn, walking the design tree, dependencies
   first. Every question carries a **Recommended:** line. Stop when every branch resolves or the
   user says stop. No fixed count (deep by nature).
4. **Live ledger (G7).** Append each resolved decision to a running locked-decision table
   immediately — crash/compaction-safe.
5. **Capture (G6).** Write/append `docs/specs/SPEC-<topic>-<date>.md` with the ledger + an
   open-questions section; update ADR(s) + `CONTEXT.md` glossary if those exist (phased).
6. **Handoff.** Offer `/plan` tier 4 → ORCHESTRATE → `/do`. One-directional into the pipeline.

## 4. Relationship map (consistency with the planning spine)

```
brainstorm (GENERATE, divergent) ──► spec skeleton
                                        │
/craft:grill (INTERROGATE, convergent) ─► decision-ledger SPEC ──► /plan tier 4 ──► ORCHESTRATE ──► /do
                                        ▲
orchestrate Step 0.5 Clarify ──invokes──┘   (reuses grill on ambiguous tasks; SPEC-orchestrate-clarify)
```

grill sits between brainstorm (generation) and plan-orchestrator (artifact). It is the
"interrogate" tier the original planning spine lacked.

## 5. Distinctions to enforce (avoid the accretion trap)

- **grill ≠ brainstorm** (G5): divergent vs convergent. Headers must state this.
- **grill ≠ AskUserQuestion clarify** (G2): grill is one-at-a-time free-text deep interrogation;
  the lighter AskUserQuestion batch pattern stays for quick gates that don't need full grilling.
- **grill is the single interrogation impl** (G8): orchestrate reuses it; do not fork a second.

## 6. Phases

| Phase | Scope | Gate |
|---|---|---|
| **P1 — Core grill** | G1–G6: standalone command, one-at-a-time loop, codebase-first read-then-confirm, decision-ledger spec capture, `/plan` handoff | none |
| **P2 — Docs-on-the-spot** | G7 full grill-with-docs: ADRs + `CONTEXT.md` glossary + live-append ledger | P1 |
| **P3 — Orchestrate reuse** | G8: rewrite orchestrate Step 0.5 to invoke `/craft:grill`; remove bespoke clarify logic | P1 + SPEC-orchestrate-clarify |

P2 is the heavy option — defer if it threatens P1 velocity.

## 7. Documentation & Discoverability

- [ ] Tutorial (`docs/tutorials/TUTORIAL-grill.md`) — when to grill vs brainstorm, worked example
- [ ] Help + command reference (`docs/help/grill.md`, `docs/commands/grill.md`)
- [ ] REFCARD entry (`docs/REFCARD.md`)
- [ ] Help hub / discovery (`/craft:hub` via frontmatter; `commands/smart-help.md` entry)
- [ ] Website (`mkdocs.yml` nav) + `docs/skills-agents.md` catalog row
- [ ] CHANGELOG `[Unreleased]` + count bumps; `validate-counts.sh` + `docs-staleness-check.sh` clean
- [ ] **Count cascade:** new command → ~14 bump-version files + plugin.json `(N craft)` subtotal + ~29 doc refs (memory: adding-a-command-cascades-30-file-count-bump)

## 8. Known Risks (from session pattern)

- **Accretion** — grill is a 4th interrogation-flavored asset (brainstorm, AskUserQuestion clarify,
  manual grilling). G5/G8 distinctions are what keep it from being redundant; enforce them in docs
  and tests, or it becomes the exact bloat the planning-refactor spec fights.
- **One-at-a-time vs craft convention** — G2 deliberately breaks the AskUserQuestion norm; the
  command body must justify it so a future audit doesn't "fix" it back to batches.
- **G7 scope creep** — ADR/glossary machinery is a known heavy lift; keep it in P2.

## 9. Acceptance criteria

- `/craft:grill <spec>` runs a one-at-a-time loop, every question carries a Recommended line,
  auto-resolves ≥1 branch from the repo and shows it as overridable.
- Produces/updates a `docs/specs/SPEC-*.md` decision ledger and offers the `/plan` handoff.
- `/craft:grill "<bare topic>"` sketches a skeleton then grills it.
- Behavioral tests: loop fires; `--yes` auto-accepts; codebase auto-resolve shows recommended
  answers; ledger written; brainstorm-vs-grill header distinction present.
