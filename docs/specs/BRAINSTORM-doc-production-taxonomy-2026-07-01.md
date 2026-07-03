# BRAINSTORM: Doc Production Taxonomy (Proposal / Grill / Plan / Tasks / Todos)

**Date:** 2026-07-01
**Depth:** default (2 expert questions, both unanswered by user — proceeded on recommended
defaults per auto-mode) · **Focus:** ops

## Topic

Which of the 5 doc-production types this session actually used — proposal, grill, plan
(ORCHESTRATE), tasks, todos — is the right vehicle for which purpose: your review vs. craft's
own internal execution vs. my in-session working memory. User's stated prior: "I think of
proposal as for my review."

## Expert questions asked (unanswered — proceeded on recommended defaults)

1. **Doc mapping** — which existing craft convention should each type map onto?
2. **Blur risk** — what's the biggest failure mode if boundaries drift over time?

## Recommended answer

| Type | Audience | Purpose | Example this session |
|---|---|---|---|
| **Proposal** | **You** | Findings + ranked recommendations, awaiting your decision. Never executed on its own. | `PROPOSAL-orchestrate-family-simplification-2026-07-01.md` |
| **Grill** | You + future implementer | Locks judgment calls *before* dispatch — a decision ledger, not a to-do list. Required precondition for unattended/background work. | `GRILL-plan-orchestrator-dispatch-mode-2026-07-01.md` (15 branches resolved) |
| **Plan (ORCHESTRATE)** | An implementer (you in a new session, OR a dispatched background agent) | The durable execution contract — self-contained enough that reading it alone is sufficient to do the work. Structural requirement for the STOP-new-session rule and for any future background-dispatch mode. | `docs/plans/2026-07-01-token-efficiency-linear-implementation.md` |
| **Tasks** (session TaskList) | Me, this session only | Lightweight in-flight tracking across a single conversation. Not durable — doesn't survive a new session on its own (unlike ORCHESTRATE checkboxes). | The `#1-#6` list visible in every turn this session |
| **Todos / ad hoc** | Nobody durable | Scratch — a thought captured inline in chat, never saved. Fine to lose. | Most of this conversation's back-and-forth before something got promoted to a file |

**One-line rule:** *the more unattended the eventual execution, the more durable and
self-contained the doc needs to be.* Todos → Tasks → Plan is an increasing-durability ladder;
Proposal and Grill sit outside that ladder — they're gates (review / judgment-lock), not
execution artifacts themselves.

## Guard against the identified blur risk

Same failure mode just found in the orchestrate-family audit (`orchestrate:plan` vs.
`plan-orchestrator` skill: two files claiming the same content, drifting independently).
**Rule going forward: each type links back to its source, never copies content forward.** A
GRILL file back-links to its SPEC; a PROPOSAL that gets approved becomes a SPEC/GRILL pointer,
not a re-written duplicate; an ORCHESTRATE file references its GRILL/SPEC rather than
re-explaining resolved decisions inline.

## Not resolved (needs your input, not mine to decide)

- [ ] Should "Proposal" formally become part of craft's own doc conventions (i.e., should the
      `brainstorm` skill or a lint rule recognize `PROPOSAL-*.md` the way it already recognizes
      `SPEC-*.md`/`GRILL-*.md`), or is this an ad hoc pattern used only in this session?
- [ ] Does "Proposal" overlap enough with the existing "SPEC" type that it should collapse into
      it (one of the answer options above), rather than becoming a 6th first-class type?

## Suggested next command

None auto-suggested — this is a process/convention topic, not a feature spec. If you want the
answer above locked in as an actual convention (e.g., added to a CLAUDE.md or a skill), say so
and I'll draft that change directly.
