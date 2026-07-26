# GRILL: prompt-refiner Remaining Scope (#268 cleanup + #266 grill mode) — Decision Log

**Date:** 2026-07-26 · **Method:** one-question-at-a-time grill with user · **Result:** all 6 branches resolved, folded into `SPEC-prompt-refiner-remaining-2026-07-26.md`

---

## Why this doc exists

`SPEC-prompt-refiner-remaining-2026-07-26.md` covered #268's 3 remaining audit-confirmed items
(named Copy-for-elsewhere destinations, `--scope global`, D7 smart-help cleanup) plus #266's
multi-round grill-mode design, deliberately combined into one spec at the user's direction. Six
load-bearing branches were interrogated one at a time before any implementation starts.

## Decision Ledger

| # | Branch | Decision |
|---|---|---|
| 1 | A1 — Copy-for-elsewhere destination handoff | **Returned intent tuple.** "Copy for elsewhere" stays one option in the existing 4-way confirm; picking it adds a lightweight follow-up `AskUserQuestion` for destination, then the skill returns `{text, destination_intent}` for the caller to act on. Only the top-level dispatch needs a new branch, not each of the 5+ callers individually; no extra round-trip added to the other 3 confirm branches. |
| 2 | A2 — `--scope global` parsing | **Per-caller parsing, skill checks a boolean input.** Matches D6's existing pattern (each caller command file owns its own flags, passes them into the skill's Inputs). `SKILL.md` Step 1 becomes conditional: `if scope==global: skip to step 2`. Requires touching all 5+ caller command files to accept and forward the flag, but keeps the skill's own parsing surface at zero. |
| 3 | Weakest-recommendation check on Scope B commitment | **Design now, build separately.** This grill locks the architecture decision for #266, but implementation ships as its own PR after Scope A — not bundled into the same build arc. Avoids over-committing implementation effort to a pattern observed exactly once (n=1 manuscript-revision session) before it recurs. |
| 4 | #266 grill-mode architecture | **Delegate to `craft:grill`'s existing per-unit loop** (`skills/workflow/grill/SKILL.md` Step 4 — Recommended-first `AskUserQuestion`, halt on `/done`, one question at a time) rather than a standalone reimplementation or a speculative shared-primitive extraction. Zero duplicated loop logic; the real design work still owed is a thin adapter reconciling grill's "interrogate a position for gaps" framing with "interrogate prose for correctness/clarity" — the adapter is now the load-bearing open item for whoever implements this, not glossed over. |
| 5 | #266 grill-mode trigger | **Phrasing detection ("grill this", "interrogate one at a time") + an explicit flag**, both wired. Matches how the pattern was actually invoked in the observed session (plain language, not a flag), while still giving callers/scripts a reliable non-heuristic path in. The phrase-matching heuristic needs its own test coverage before shipping — false-positive risk (e.g. "look at this carefully" misfiring into a 20+ round loop) is real and was named explicitly, not waved off. |
| 6 | A3 — Default Policy table scope | **Make it exhaustive.** Add both `smart-help` (opt-in, default-OFF, per D7) and `arch:plan` (already OFF, currently only documented in prose below the table) as rows, so every current `--refine` call site appears in one place. Enables a future dogfood test asserting every caller command file has a corresponding table row — closes the "table vs. prose footnote" documentation-style split that existed before this decision. |

## AMENDMENT (2026-07-26, same session) — decisions #1, #4, #5 WITHDRAWN; #3's premise falsified

The six decisions above were locked, then the resulting spec was reviewed adversarially from a
code lens and a design lens before implementation started. Both independently returned
"do not proceed as-is." The original rows are left intact — the reversal is the useful record,
not an embarrassment to hide.

**What falsified decision #3.** Decision #3 deferred #266's build on an n=1 argument: "design
now, build when the pattern recurs." The pattern had already recurred and been solved —
`savant/src/plugin-api/skills/edit-loop/SKILL.md` + `/ms:edit-loop` shipped **2026-07-13**
(savant #192), 8 days after #266's originating manuscript session and 11 days before the
2026-07-24 audit that declared #266 "still valid, leaving open." Its grounding doc,
`savant/docs/tutorials/paragraph-revise-grill-cookbook.md` (Isolate → Grill → Revise → Verify),
landed 2026-07-07 — two days after the observation. savant is the correct home: it has the
mechanical numbers/equations/citations content guard and `ms:check` re-verify that craft
structurally cannot provide. Craft's evidence for a *general-purpose* (non-manuscript) grill
mode is n=0, not n=1.

The grill never asked *"should this live in craft at all?"* — that omission is what let five
downstream decisions be locked on a premise one cross-repo check would have dissolved.

| Decision | Status after review | Reason |
|---|---|---|
| #1 (destination intent tuple) | **WITHDRAWN — A1 cut** | The tuple has no consumer. Every caller is instructed to STOP on Copy-for-elsewhere (`commands/do.md:57`, `brainstorm.md:64`, `plan/feature.md:39`, `arch/plan.md:33`, `orch.md:62`), and `commands/refine.md:24` states outright "there is no caller to hand the result to." Decision #1's own rationale ("only the top-level dispatch needs a new branch") is false — for `/craft:do`, `do.md` **is** the top level and is told to stop. Also re-adds a category craft deliberately removed (`refine.md`: clipboard-copy and background execution dropped as "command-routing concerns, not prompt-refining"). |
| #2 (`--scope global` per-caller) | **DEFERRED** | Mechanism is sound (pre-Step-1, not a checkbox — correct call). But demand is n=1 from a single 2026-07-05 conversation turn, never independently re-requested, against a cost of 7 caller files of flag plumbing plus a permanent interface commitment. Also collides by value with `plan/feature.md:65`'s existing prose-documented `--scope <mvp\|full\|enterprise>`. Revisit on a second independent request. |
| #3 (design now, build later) | **PREMISE FALSIFIED** | See above — savant `edit-loop`. |
| #4 (delegate to grill's Step 4 loop) | **WITHDRAWN — Scope B cut** | Not implementable as recorded. Scope B's "apply immediately" contradicts `prompt-refiner/SKILL.md:114` ("NEVER write files") — and grill's loop never applies edits either (it asks and records). Neither skill can do what the observed session did; the ledger's "thin adapter" framing described a *vocabulary* reconciliation for what is actually a hard-constraint conflict. |
| #5 (phrase detection + flag) | **WITHDRAWN — Scope B cut** | Would have created an unguarded recursion: `grill/SKILL.md:44` calls `prompt-refiner` by default on any quoted topic, and the trigger phrase survives the round-trip (`/craft:grill "grill this paragraph"` → refine → phrase detected → grill → …). Craft's trigger-uniqueness test (`tests/test_craft_plugin.py:325`) matches identical quoted strings only, so this would have shipped green. Compounding: under `--yes`, prompt-refiner's documented cascade (`SKILL.md:103-106`) plus grill's zero-AskUserQuestion mode would auto-apply N rounds with no human at any point. |
| #6 (exhaustive Default Policy table) | **KEPT, re-specified** | The one item with independent provenance (`SPEC-interactive-commands-2026-06-25.md` §8) and a real dangling gap. But "exhaustive" was under-specified: it named only `smart-help` + `arch:plan` while `commands/plan.md:12-17` is also a live declarer (`default: true`), and three existing rows use stale display names. Re-scoped to key rows on command **file path**, add `plan.md` and `arch/plan.md`, fix the stale names, update the equality-asserting allowlist at `tests/test_plugin_e2e.py:162-180`, then add the drift test. |

**Net re-scope:** ship #6 only (as A3). Cut A1 and Scope B. Defer A2. One small PR instead of a
four-part arc. #266 closes against savant `edit-loop`.

## Notes for implementation

> **Superseded by the amendment above** — the three notes below applied to decisions #4 and #5,
> both now withdrawn. Retained for the record.

- Scope A (#268) and Scope B (#266)'s design lock are both closed by this grill; Scope B's
  *build* is explicitly NOT authorized by this ledger to start in the same PR as Scope A — a
  separate grill/plan step is not required to build it (architecture is locked here), but it
  should be its own PR per decision #3.
- Decision #4's adapter (reconciling grill's gap-interrogation framing with prose/claim
  interrogation) is the single highest-risk unresolved detail carried forward into
  implementation — flag it explicitly in whatever `/craft:plan` or `ORCHESTRATE-*` artifact
  picks this up next, rather than assuming delegation to `craft:grill` is a drop-in call.
- Decision #5's phrase-detection heuristic needs a documented boundary (what does and does not
  trigger it) before implementation, not just "detect similar phrasing" — left for the
  implementing session to draft concrete examples and non-examples.
