# SPEC: prompt-refiner — remaining scope (#268 cleanup + #266 grill mode)

**Status:** GRILLED + ADVERSARIALLY REVIEWED — RE-SCOPED. Only Scope A3 proceeds; A1 cut,
A2 deferred, Scope B cut. See `docs/specs/GRILL-prompt-refiner-remaining-2026-07-26.md`'s
AMENDMENT section for the full reversal record and evidence (savant `edit-loop` shipped
2026-07-13, mooting Scope B; no consumer exists for A1's return tuple).
**Date:** 2026-07-26
**Target:** `skills/workflow/prompt-refiner/SKILL.md`, `commands/smart-help.md`,
`tests/test_plugin_e2e.py` (A3 only — see Final Scope below)
**Source issues:** #268 (A3 only; #266 closed separately against savant `edit-loop`)
**Prior art:** `docs/specs/SPEC-prompt-refiner-consolidated-improvements-2026-07-05.md`,
`docs/specs/GRILL-prompt-refiner-decisions-2026-07-05.md` (original consolidated redesign —
sub-ask 1, the 4-way confirm, shipped in v4.1.0; #267 and #265 have since shipped and closed
as their own small PRs)

## Final scope (post-review)

| Item | Call |
|---|---|
| A1 — named Copy-for-elsewhere destinations | **CUT** — see amendment |
| A2 — `--scope global` | **DEFERRED** — see amendment |
| A3 — smart-help + exhaustive Default Policy table | **SHIP** (re-specified: key rows on file path, add `commands/plan.md` + `commands/arch/plan.md`, fix the `test_plugin_e2e.py` equality-asserting allowlist, add a drift test) |
| Scope B — #266 grill mode | **CUT from craft** — closes against `savant/src/plugin-api/skills/edit-loop/SKILL.md` |

The sections below are retained as the historical record of what was originally proposed; they
are superseded by the table above and the GRILL amendment, not current instructions.

## Why this spec exists

The 2026-07-05 consolidated redesign (#268's parent umbrella) closed most of its scope. A
2026-07-24 audit (see #268's own comment thread) found three items still genuinely open, plus
confirmed #266 (multi-round grill mode) as a separate, larger design question that was
explicitly deferred rather than decided in the original grill. This spec covers everything
still outstanding across both issues, so one grill pass and one implementation arc can close
both.

## Scope A — #268 remaining items (small, mechanical)

Current `skills/workflow/prompt-refiner/SKILL.md` state confirmed by direct read (2026-07-26):

### A1. Named "Copy for elsewhere" destinations

Step 5's confirm table (line 99) currently reads: "Accept the rewrite, take NO further action
here." No named sub-destinations exist. #268 proposed plain print / Apple Note / Obsidian
folder, with the constraint that the skill **never calls the destination MCP tools directly**
(would violate its own "never execute/call tools" constraint, line 113, and couple a shared
5-caller skill to one user's local app connections). The skill hands back structured
text + a destination *intent*; the actual write happens one layer up (the caller, or the
top-level session), outside the skill.

**Open design question:** does "Copy for elsewhere" become a sub-menu (a second
AskUserQuestion) inside that branch, or a single option that returns a
`{text, destination_intent}` tuple for the caller to interpret? A sub-menu adds a round-trip to
every "just copy it" invocation; a returned tuple keeps it one confirm but pushes destination
logic into 5+ callers.

### A2. `--scope global` flag

Zero mentions of `scope` in the current SKILL.md. Proposed in the 2026-07-05 spec as a
rewrite-time flag that skips Step 1's context-read entirely (project-agnostic rewrite) —
explicitly NOT a 4-way checkbox option, since by Accept-time (step 5) the context-read has
already happened in step 1. Needs: where the flag is parsed (caller command files, per D6's
existing per-caller flag-ownership pattern), and how "skip Step 1" is signaled internally
(an early-return, or Step 1 becomes conditional on flag presence).

### A3. D7 — `smart-help` `--refine` declaration

`grep -n "refine" commands/smart-help.md` returns zero matches (confirmed 2026-07-26). The
2026-07-05 spec called for smart-help to declare `--refine` as **opt-in, default-OFF** — this
was decided but never implemented. Mechanical: add the flag declaration + default-OFF policy
line, consistent with the existing per-command table in SKILL.md's "Default Policy" section
(currently lists `do`/`brainstorm`/`plan:feature`/`grill`/`orchestrate`/`orchestrate:workflow`
— `smart-help` and `arch:plan` are both absent from that table and should probably both be
added, or the table's own scope should be clarified as non-exhaustive).

## Scope B — #266: multi-round grill mode (design, larger)

### Problem

`prompt-refiner`'s canonical flow is a single rewrite-then-confirm cycle (steps 1–6). A
2026-07-05 manuscript-revision session organically needed a different shape entirely:
decompose a target into individually-checkable units (claims, terms, transitions), surface
each as its own `AskUserQuestion` with 2–3 resolution options + a recommendation, apply
immediately, and loop until the user signals done — ~20+ rounds in the observed case. This
is qualitatively different from a single before/after box: per-unit granularity, immediate
application (not batched), and an open-ended loop instead of one confirm.

### Candidate approaches (for the grill to choose between, not pre-decided)

1. **Delegate to `skills/workflow/grill/SKILL.md`'s existing per-unit loop** (Step 4: "the
   grill loop — deliberate, one question at a time," with Recommended-first options +
   consequences, halt on `/done` or empty-enter). `craft:grill` already implements almost
   exactly this shape for specs/plans/topics. The question is whether its "interrogate a
   position for gaps" framing generalizes to "interrogate prose/claims for correctness/clarity"
   without forcing an awkward fit.
2. **Build a standalone `--grill` mode inside `prompt-refiner`** replicating the loop
   mechanics locally — avoids coupling two skills' procedures together, but duplicates loop
   logic (halt conditions, Recommended-first AskUserQuestion, immediate-apply-then-reverify)
   that `grill` already has tested and shipped.
3. **New shared primitive** — extract the loop mechanics from `grill` into something both
   skills call, if the shapes turn out compatible enough (this was flagged as "worth checking"
   in #266's own issue body, not yet investigated).

### Open questions the grill must resolve

- Decomposition unit: is "claim/term/transition" the right granularity for prompt-refiner's
  general audience (not just manuscript prose), or does this only make sense for the
  research/manuscript branch of Step 1's context-read (A2/Scope-A adjacent: this is a second
  reason Step 1's project-type detection matters)?
- Trigger: implicit phrasing detection ("grill this", "interrogate this one at a time") vs.
  an explicit `--grill` flag vs. both?
- Re-verification step: the observed session re-ran "render + de-AI re-audit" after each
  applied unit — is that manuscript-specific tooling, or does a generic re-verify step need
  to be pluggable per project type?
- Interaction with the existing 4-way confirm (step 5): does grill mode replace it entirely
  for the session, or does each round still end in a scoped version of the same confirm?

## Acceptance criteria

**Scope A (#268):**

- [ ] "Copy for elsewhere" supports named destinations without the skill calling external
      MCP tools directly (mechanism decided by grill: sub-menu vs. returned intent tuple)
- [ ] `--scope global` (or unified `--scope`) resolves before Step 1, not inside the 4-way
      checkbox, and is documented in SKILL.md's Inputs section
- [ ] `smart-help` declares `--refine` (opt-in, default-OFF); the Default Policy table's
      coverage (exhaustive vs. illustrative) is clarified
- [ ] Full pytest suite green, not a scoped subset

**Scope B (#266):**

- [ ] A grill-mode design is locked (delegate to `craft:grill` / standalone / shared
      primitive) with a named decision, not left as "investigate later"
- [ ] If shipped: triggering phrase(s) or flag documented, loop halt condition documented,
      interaction with the existing 4-way confirm documented
- [ ] If NOT shipped this cycle (e.g. scoped too large): a explicit close-or-defer decision
      recorded in the GRILL ledger, not silently dropped

## Test plan

- Scope A: e2e coverage per caller for the destination sub-menu (or tuple-return) path,
  `--scope global` skip-gate unit test (Step 1 not invoked when flag present), smart-help
  dogfood test asserting `--refine` declared + default-OFF.
- Scope B: contingent on the locked design — if delegating to `grill`, extend `grill`'s own
  test suite; if standalone, new unit tests for the loop's halt conditions and immediate-apply
  ordering.

## Recommended execution order

Scope A first (small, independently shippable, no design risk) — same "implement/test each
caller independently, not one bundled diff" guidance as the original 2026-07-05 spec, since
this again touches a skill shared by 5+ callers. Scope B only after its design questions are
locked by the grill — it is not blocked on Scope A landing first, but is large enough to
warrant its own PR regardless of ordering.
