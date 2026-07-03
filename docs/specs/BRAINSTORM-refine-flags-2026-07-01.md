# BRAINSTORM: `/refine` — Flags to Modify Behavior

**Date:** 2026-07-01 · **Depth:** standard · **Focus:** arch
**Target:** `commands/workflow/refine.md` (thin shim) → `skills/workflow/prompt-refiner/SKILL.md`
(canonical behavior).

---

## Trigger for this brainstorm

Earlier today, a new requirement landed (saved as `refine-copy-paste-execute-edit-skip` in this
session's memory — outside this repo, not a resolvable link): every `/refine` call should print
the refined prompt in a copy-paste-ready fenced code block, then ask a follow-up question about
what happens next. That requirement was adopted
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

**Scope decision (revised 2026-07-01, reversing the earlier standalone-only call):** this
replaces Accept/Edit/Use-original **everywhere `--refine` fires** — standalone `/refine` AND every
internal caller (`brainstorm`/`do`/`orchestrate`/`plan:feature`/`arch:plan`). One vocabulary, no
special-casing by caller. The mapping onto the old 3-way is direct for three of the four options:

- **Execute now** ≈ old **Accept** — proceed with the refined prompt into whatever comes next
  (the calling command's own flow, or the standalone print-and-stop path).
- **Edit first** ≈ old **Edit** — revise inline, then re-ask.
- **Skip** ≈ old **Use original** — proceed with the raw, unrefined text (not an abort).
- **Copy for elsewhere** is the new fourth option, universal escape hatch — print the fenced block
  and **short-circuit whatever called `--refine`**, regardless of caller. If `brainstorm --refine`
  hits "Copy for elsewhere," brainstorm's own question flow never starts; the refined prompt was
  for a different context, not for this invocation.

This costs internal callers exactly one extra option on a question they already ask (not a second
question) — no double-prompt, since it reuses the existing confirm step rather than adding one.

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
| **A — ship only the 4-way confirm + fenced block, uniformly** | Minimal change matching today's actual, confirmed requirement, applied to all 5 `--refine` call sites | ✅ **Recommended** — the only piece with a live, confirmed need; everything else is speculative |
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
  Applying it uniformly (revised decision) means all 5 callers' existing tests that assert
  Accept/Edit/Use-original wording need updating to the new 4-way vocabulary — grep for the old
  option labels across `tests/test_interactive_commands_e2e.py` and similar before implementing.
- **"Copy for elsewhere" as a universal abort.** When it short-circuits an internal caller (e.g.
  `brainstorm --refine`), the calling command must actually stop — not silently continue past the
  confirm step. This needs an explicit check in each caller's flow, not just in the skill.
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
- **e2e:** `--refine` flag on each of `brainstorm`/`do`/`orchestrate`/`plan:feature`/`arch:plan` →
  same 4-way question fires; "Copy for elsewhere" stops the caller's own flow before its first
  question (assert the caller's downstream questions never appear in that branch).
- **e2e:** same flag, "Execute now" branch → caller's normal downstream flow proceeds exactly as
  the old "Accept" branch did (behavior-preserving for the common case).
- **dogfood:** grep all 5 caller command/skill files for the old Accept/Edit/Use-original wording
  — none should remain; all must reference the shared 4-way vocabulary from `prompt-refiner`
  (single-source guard, same class of check this session used for the doc-scorer rubric).

## Documentation

- Update `skills/workflow/prompt-refiner/SKILL.md`'s "Procedure" section (step 4, currently
  Accept/Edit/Use original) with the new 4-way confirm + fenced-block requirement — this is now
  the ONE canonical confirm step for every caller, not a standalone-only variant.
- Update `commands/workflow/refine.md`'s scope note (currently documents what was dropped during
  consolidation — add a line on the new confirm shape).
- Update the 4 other callers' own command/skill docs (`brainstorm`, `do`, `orchestrate`,
  `plan:feature`, `arch:plan`) wherever they currently describe the Accept/Edit/Use-original
  interaction, since the vocabulary changes uniformly.
- REFCARD: no dedicated refine refcard currently exists; skip unless usage justifies one.

## Recommended Next Step

→ **Option A, applied uniformly** — implement the 4-way confirm + fenced-code-block requirement
as THE replacement for Accept/Edit/Use-original across all 5 `--refine` call sites (no
standalone/internal split). Grill this brainstorm (open questions: exact wording of the 4th
option; whether "Copy for elsewhere" needs caller-specific short-circuit logic or a single shared
implementation in the skill suffices) before implementing — this is a canonical skill 5 commands
depend on, worth a judgment-lock pass before touching it.
