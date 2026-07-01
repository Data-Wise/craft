# SPEC: Grill Attack-Angles

**Status:** Draft — for review, then grill, then implement. No code yet.
**Date:** 2026-07-01
**Target command:** `commands/grill.md` (inline-logic command; there is no grill *skill*)

---

## Problem

`/craft:grill` interrogates one question at a time but has **no explicit attack-angle
concept**. Unlike `/review` (which enumerates 8 named finder angles), grill leaves *which*
weaknesses to attack entirely to the model's improvisation. Result: grill quality is
inconsistent — a strong session attacks the riskiest assumption; a weak one asks surface
questions and misses the load-bearing risk.

This session produced a 7-axis adversarial prompt
([docs/reference/GRILL-PROMPT-craft.md](../reference/GRILL-PROMPT-craft.md)) that measurably
improved a grill (caught a phantom-command trap + a rich-body-trap before implementation). That
prompt is craft-self-tuned. This spec generalizes its *transferable* part into the command.

## Goal

Give grill a **project-agnostic** set of adversarial attack angles it considers when choosing
what to interrogate — **without** hardcoding any project-specific gotcha into the command
(that would poison grills of other users' projects).

## Non-goals

- Converting grill to a thin-command/fat-skill (separate refactor; grill is inline-logic today).
- Hardcoding craft internals (rich-body-trap, `_discovery`, python-3.9) into the command —
  those stay in the reusable snippet + craft's CLAUDE.md.
- Turning grill into a mandatory N-angle sweep — it must stay lightweight for `--bound` gates.

## Design

### The generic angles (project-agnostic)

1. **Weakest recommendation** — the call that looks worst in hindsight; name the cheaper/safer alternative.
2. **Riskiest assumption** — the load-bearing belief that breaks the plan if false. Prioritise **silent** failures (behavior lost, not errors thrown).
3. **Implementation regret** — the step you'd curse mid-build. **Source project-specific traps at runtime from the target project's `CLAUDE.md` / ADRs / memory** — do NOT hardcode them. (This is the key generalization: grilling craft surfaces craft's gotchas because grill reads craft's CLAUDE.md; grilling project X surfaces X's.)
4. **Benefit honesty** — is any claimed benefit (perf, token, time saved) **measured or merely asserted**? Separate real levers from wishful ones.
5. **Workflow discipline** — does execution respect the project's *documented* workflow (branch model, test command, verify-before-merge) as stated in its CLAUDE.md?
6. **Blast radius** — does the change silently alter a convention or require a doc/drift sweep? Scoped or hidden?
7. **Reversibility & scope creep** — anything irreversible or ballooning past stated scope? Hold vs. proceed?

Angles 1–2, 7 are the generic adversarial core; 3–6 are framed to **read the target project's
own conventions** rather than embed any one project's specifics.

### Interaction with existing flags

- **`--bound N`:** grill selects the **N highest-value angles for this specific target**, not a
  fixed sweep. Angles guide *branch selection/prioritisation*, they are not a mandatory checklist.
  A quick `--bound 2` gate (orchestrate Step 0.5) still asks only 2 questions.
- **`--yes` / `--non-interactive`:** angles still apply; grill auto-picks the Recommended answer per selected branch.
- **`--no-capture`:** unchanged — angles affect *what* is asked, not *whether* a ledger is written.
- **Recommendation-first:** every angle's question still leads with an explicit recommendation (existing behavior).

### Where the angle list lives

Inline in `commands/grill.md` (small, considered-guidance prose). **Do NOT** extract it to a
file under `commands/` — `commands/_discovery.py` would discover it as a phantom command
(see the orchestrate-family grill, finding A2). If extraction is ever wanted, target `docs/` or
a (future) grill skill, never `commands/**`.

## Test Plan

Tiers (per change shape: prose/frontmatter command + behavioral contract → e2e + dogfood):

- **e2e:** grilling a target with a known weak assumption surfaces it (angle 2 fires); `--bound 2`
  asks exactly 2 questions (angles don't inflate a bounded gate); `--yes` emits zero prompts.
- **dogfood:** `commands/grill.md` contains **no project-specific hardcoded strings**
  (assert the angle prose is generic — no `_discovery`, `python3.9`, `ADR-002`, `dev→feature`
  literals in the command body).
- **dogfood:** angle-3 prose explicitly instructs reading the target's CLAUDE.md (regression net
  against someone later hardcoding craft traps into the general command).

Run the full suite via a working interpreter (NOT bare `python3` = the 3.9 baseline gotcha):
`/opt/homebrew/bin/python3.13 -m pytest tests/ -q`.

## Documentation

- Update `commands/grill.md` help/body with the angles section.
- Update `docs/guide/pipeline-orchestrate-guide.md` — **also fix its stale
  `/craft:grill (skills/orchestration/...)` reference** (no grill skill exists).
- `docs/REFCARD.md` grill entry if it describes behavior.
- Cross-link the reusable craft snippet as the craft-tuned superset.

## Open Questions

- [ ] Fixed 7-angle list, or extensible via command frontmatter (let a project add its own angles)?
- [ ] Default angle budget for an **unbounded** grill — cap at ~5 load-bearing branches, or truly open-ended?
- [ ] Should angle-3's "read the project's CLAUDE.md for traps" be automatic, or only when a `CLAUDE.md` is present in the target's tree?

## Next step

Review this spec → grill it (dogfood: run the saved
[craft grill prompt](../reference/GRILL-PROMPT-craft.md) against this very spec) → implement in a
`feature/grill-attack-angles` worktree.
