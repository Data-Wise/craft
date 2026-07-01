# BRAINSTORM: `/refine` — Flags to Modify Behavior

**Date:** 2026-07-01 · **Depth:** standard · **Focus:** arch
**Target:** `commands/workflow/refine.md` (thin shim) → `skills/workflow/prompt-refiner/SKILL.md`
(canonical behavior).

---

## Trigger for this brainstorm

Earlier today, a new requirement landed (saved as
[refine-copy-paste-execute-edit-skip.md](../../../../../.claude/projects/-Users-dt-projects-dev-tools-craft/memory/refine-copy-paste-execute-edit-skip.md)
in memory): every `/refine` call should print the refined prompt in a copy-paste-ready fenced code
block, then ask a follow-up question about what happens next. That requirement was adopted
ad hoc, in-session, with no code change yet — this brainstorm is where it (and other flag ideas)
get designed properly before landing in the skill.

## Current state

`commands/workflow/refine.md` is a thin shim (frontmatter + args only) pointing at
`skills/workflow/prompt-refiner/SKILL.md`, which owns:

- **Procedure:** read context → rewrite → show before/after box → confirm via `AskUserQuestion`
  (Accept / Edit / Use original) → return the chosen prompt string to the caller.
- **Two entry paths:** the explicit `/craft:workflow:refine` command, and the `--refine` flag on
  `brainstorm` / `do` / `orchestrate` / `plan:feature` / `arch:plan`.
- **One existing flag:** `--explain` — adds a one-line rationale per change under "Changed:".
- **`--yes` interaction:** auto-accepts, skips the picker, prints "refined (auto-accepted)".
- **Standalone behavior:** with no downstream command, stop after the confirm step and print the
  refined prompt (this is the path the new requirement modifies).

## Key finding: this session used /refine in two genuinely different modes

`★ Insight ─────────────────────────────────────`

Reviewing today's actual `/refine` calls in this session surfaces a pattern the current design
doesn't distinguish:

1. **Act-here mode** — "refine: meta monitor new orchestrate dispatch pipeline" → the refined
   prompt became a protocol *this same session* immediately started applying.
2. **Hand-off mode** — "refine: create a prompt for me to use it in a separate session" → the
   refined prompt was explicitly for pasting into a *different* session/context, never executed
   here.

The existing Accept/Edit/Use-original confirm doesn't ask *which* of these the user wants — it
only asks whether the rewrite is good. The new copy-paste-block requirement was really solving
for mode 2 (hand-off), but a naive Execute/Edit/Skip question (as first proposed) collapses modes
1 and 2 back into one "Execute now" bucket, losing the distinction that motivated the requirement
in the first place.

`─────────────────────────────────────────────────`

## Resolved design: a single 4-way follow-up question

Rather than two sequential confirms (accept-the-rewrite, then decide-what-to-do-with-it) or a
3-way that conflates act-here and hand-off, collapse into **one** `AskUserQuestion` after the
before/after box:

| Option | Meaning |
|---|---|
| **Execute now** (Recommended when a clear action is implied) | Accept the rewrite AND act on it in this session (dispatch, run a command, apply as a rule). |
| **Copy for elsewhere** | Accept the rewrite, print it in a fenced code block, take NO action here — the hand-off mode. |
| **Edit first** | Revise the text inline, then re-ask this same question with the edited version. |
| **Skip** | Reject — keep nothing, take no action. |

This replaces the current Accept/Edit/Use-original **for standalone `/refine` only** (per today's
scope decision) — internal `--refine` callers (brainstorm/do/orchestrate/plan:feature) keep their
existing Accept/Edit/Use-original confirm unchanged, since those callers already have their own
downstream flow and a second execute-routing question would double-prompt.

The fenced-code-block requirement applies to **all four** outcomes except Skip — even "Execute
now" should show the copy-paste block first (costs nothing, and the user may want to reuse it
elsewhere later even after acting on it now).

## Flag ideas (beyond the confirm-flow redesign)

### Quick Wins (< 30 min each)

1. **`--target <here|elsewhere>`** — pre-declare the mode instead of asking every time. When set,
   skip the 4-way question and go straight to the corresponding behavior (still show the before/
   after box). Useful once a user has a strong habitual pattern (e.g., always hand-off when
   drafting for a teammate).
2. **`--terse`** — suppress the "Changed:" line entirely, show only Original/Refined. For users
   who've internalized the tool and don't need the explanation every time.

### Medium Effort (1–2 hrs)

- [ ] **`--n <N>`** — generate N candidate rewrites (e.g. 2-3 different angles: more directive,
  more scoped, more context-rich) and let the picker choose among them instead of a single
  rewrite + edit. Higher token cost per call; gate behind an explicit flag, never default-on.
- [ ] **`--scope <minimal|full>`** — control rewrite aggressiveness. `minimal` only fixes typos/
  ambiguity; `full` (current default) adds scope, specifics, and inferred intent. Addresses a risk
  the original skill doc already flags ("without inventing requirements the user didn't imply") —
  a `minimal` mode gives users who feel the rewrite over-reaches an escape hatch.

### Long-term (future sessions)

- [ ] **Session-scoped default for `--target`** — if a user runs `/refine --target elsewhere`
  three times in a session, offer to remember it as the session default (saves the flag on
  subsequent calls). Only worth building if usage data shows the pattern repeats — don't
  pre-build on a guess.
- [ ] **`--history`** — show the last N refined prompts from this session (a lightweight local
  log), useful for the hand-off mode when a user wants to batch-copy several refined prompts at
  session end rather than one at a time.

---

## The debate: how much of this to build now vs. defer

| Option | What | Verdict |
|---|---|---|
| **A — ship only the 4-way confirm + fenced block** | Minimal change matching today's actual, confirmed requirement | ✅ **Recommended** — the only piece with a live, confirmed need; everything else is speculative |
| **B — also add `--target` + `--terse`** | Two cheap flags reducing friction for repeat use | ⚠️ Reasonable follow-up, but no evidence yet that users hit the 4-way question often enough to want a bypass |
| **C — build `--n`, `--scope`, `--history` now** | Full flag surface in one pass | ❌ **Reject for now** — no confirmed demand; risks the same "creating skills preemptively" anti-pattern this session's bloat-grill already flagged for other surfaces |

**Why A:** the copy-paste-block + follow-up-question requirement is the only piece with a real,
stated need (today's memory entry). `--target`/`--terse`/`--n`/`--scope`/`--history` are all
plausible but unconfirmed — building them now risks the same over-eager-scope-creep pattern this
session already caught and corrected elsewhere (teaching-residue, shim retirement, skill-per-
doc-type). Ship A, watch actual usage, revisit B/C only if the 4-way question becomes friction in
practice.

## Risks / edge cases

- **Scope creep on the confirm flow itself.** The 4-way question is already a meaningful behavior
  change to a canonical skill (`prompt-refiner`) that 5 other commands depend on via `--refine`.
  Ship it scoped to standalone-only (already decided) and verify no internal caller's tests break.
- **"Execute now" ambiguity.** For a refined prompt that doesn't describe a clear action (e.g., a
  refined *question* rather than a *task*), "Execute now" has no obvious meaning. The skill should
  fall back to "just print the text" behavior when no downstream action is implied — don't force
  an artificial action.
- **Token cost of `--n`.** Multiple candidate rewrites means multiple rewrite passes — real
  per-call cost increase. Must stay opt-in, never default.

## Test Plan (default-on)

- **e2e:** standalone `/refine "vague request"` → before/after box → fenced code block → 4-way
  question (Execute now / Copy for elsewhere / Edit first / Skip) — not the old 3-way Accept/Edit/
  Use-original.
- **e2e:** `--refine` flag on `brainstorm`/`do`/`orchestrate`/`plan:feature` → unchanged
  Accept/Edit/Use-original confirm, NO fenced block, NO 4-way question (scope guard).
- **dogfood:** grep `skills/workflow/prompt-refiner/SKILL.md` to confirm the 4-way question logic
  is conditioned on "no downstream command" (standalone), not applied unconditionally.

## Documentation

- Update `skills/workflow/prompt-refiner/SKILL.md`'s "Standalone use" section with the new 4-way
  confirm + fenced-block requirement.
- Update `commands/workflow/refine.md`'s scope note if the flag surface changes (currently just
  documents what was dropped during consolidation — would need a line on the new confirm shape).
- REFCARD: no dedicated refine refcard currently exists; skip unless usage justifies one.

## Recommended Next Step

→ **Option A only** — implement the 4-way confirm + fenced-code-block requirement, scoped to
standalone `/refine` invocations, replacing (not adding to) the existing Accept/Edit/Use-original
confirm for that path only. Grill this brainstorm (open question: exact wording of the 4th option
and whether "Skip" needs a distinct icon/label from "Use original") before implementing — this is
a canonical skill 5 commands depend on, worth a judgment-lock pass before touching it.
