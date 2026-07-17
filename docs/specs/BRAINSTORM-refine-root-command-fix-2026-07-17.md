# BRAINSTORM: Fix `/craft:refine`'s confirm step, flags, docs, and root-entry question

**Date:** 2026-07-17 · **Depth:** standard · **Focus:** arch + UX
**Target:** `commands/refine.md` (thin shim) → `skills/workflow/prompt-refiner/SKILL.md`

---

## Trigger

User report: `/craft:refine` "asks for acceptance without printing first" — the
confirm question appears with no visible before/after shown beforehand. Asked
to adversarially review options/flags/docs and to "create a root /refine
command or alias."

## Finding 0 (clarifying, before anything else): a root `/craft:refine` already exists

`commands/refine.md` sits directly in `commands/` — same level as `done.md`,
`next.md`, `brainstorm.md`. It is **already** a root command, invokable as
`/craft:refine "..."`. `deprecated: true` in its frontmatter does **not** hide
it from Claude Code's slash-command palette — it's purely internal metadata
(doc generation, count exclusion) used identically on `done.md`/`next.md`/
`brainstorm.md`, all of which remain the primary, intended entry points despite
the same flag. So there's nothing to *create* here — the open question is
**why it doesn't feel like a working root command to you**, which likely comes
down to Finding 1.

## Finding 1 (the real bug): a 2026-07-01 decision was locked but never implemented

`docs/specs/BRAINSTORM-refine-flags-2026-07-01.md` already investigated this
exact "no visible output before the question" problem and reached a **Recommended**
resolution: after the before/after box, print the refined prompt in its own
**fenced, copy-paste-ready code block**, then ask a follow-up question about what
happens next — replacing the then-current Accept/Edit/Use-original wording.

That decision was never carried into the actual skill. Today,
`skills/workflow/prompt-refiner/SKILL.md` step 4 still reads:

```
4. Confirm via AskUserQuestion — Accept (Recommended) / Edit / Use original.
```

No fenced block, no updated vocabulary — the exact gap the 2026-07-01 brainstorm
was written to close. Two callers (`commands/brainstorm.md`, `commands/do.md`)
still reference the stale "Accept/Edit/Use-original" wording too.

**This is why it "asks for acceptance without printing first"**: nothing in the
current skill instructs printing the refined prompt as its own visible block —
the "boxed display" (step 3) is a compact diff, not a standalone copy-paste
artifact, and nothing computationally forces that text to render before the
`AskUserQuestion` tool call fires in the same turn. A prose-only skill (no code)
can't enforce ordering the way a hook can — it can only be *explicit* enough
that the model doesn't collapse steps 3+4 into one turn with no interstitial
text. The current wording isn't explicit enough.

## Finding 2: two competing "locked" vocabularies exist, neither implemented

- **Auto-memory** (`refine-copy-paste-execute-edit-skip.md`, saved 2026-07-01,
  same day): **3-way** — Execute now / Edit first / Skip.
- **`BRAINSTORM-refine-flags-2026-07-01.md`**'s "Resolved design" (same date,
  later in the doc): **4-way** — Execute now / Copy for elsewhere / Edit first /
  Skip, explicitly built to distinguish "act here" from "hand off to another
  session."

These disagree on whether "Copy for elsewhere" is a distinct 4th option or
folded into the base behavior (every refine already prints a fenced block, so
"copy" isn't a menu choice, just always-available). Neither is in the skill
today. This needs one decision, not two half-implemented ones.

## Finding 3: flags — current state is thin, matches the 2026-07-01 "ship A only" call

| Flag | Status |
|---|---|
| `--explain` | Implemented — one-line rationale per change |
| `--yes` | Implemented (via caller cascade) — auto-accepts, skips picker |
| `--no-refine` | Implemented on all 5 callers (brainstorm/do/orchestrate/plan:feature/arch:plan) |
| `--target` (session-default hand-off) | **Deferred by design** (2026-07-01 Option A explicitly rejected B/C for lack of demand) |
| `--terse` / `--n` / `--scope` / `--history` | **Deferred by design**, same reasoning |

No drift here — the deferrals were a deliberate, reasoned call, not an oversight.
Re-litigating them isn't warranted unless usage has since shown friction.

## Finding 4: no architecture/structure doc exists for `prompt-refiner`

Unlike the fresh `docs/architecture/craft-restore-pipeline.md` (this session),
there is no equivalent for `prompt-refiner` — despite it being a canonical skill
5+ callers depend on (`brainstorm`, `do`, `orchestrate`, `plan:feature`,
`arch:plan`, plus standalone `/craft:refine`). This is a real, standing gap,
not new.

---

## Quick Wins (< 30 min)

1. **Pick ONE vocabulary and implement it** (Recommended: the 3-way from memory —
   Execute now / Edit first / Skip — it's simpler, was the more recent/final
   note, and "Copy for elsewhere" is redundant once every refine *always* emits
   a fenced block regardless of the chosen option).
2. **Add an explicit ordering instruction to the skill**: "Emit the fenced
   before/after block and refined-prompt block as visible response text BEFORE
   calling AskUserQuestion in the same turn — never combine them into a single
   tool-call-only turn." This is the actual fix for Finding 1.
3. **Update the 2 stale callers** (`commands/brainstorm.md`, `commands/do.md`)
   to reference the new vocabulary instead of "Accept/Edit/Use-original".

## Medium Effort (1-2 hrs)

- [ ] Write `docs/architecture/prompt-refiner-pipeline.md` (same lightweight
  scale as `craft-restore-pipeline.md` / `mermaid-validation-pipeline.md`):
  entry points (5 callers + standalone), the D6 default-on/off table, the
  confirm-step vocabulary, `--yes` cascade.
- [ ] Grep all 5 caller docs for any other stale confirm-vocabulary references
  beyond the 2 already found, per the original brainstorm's own test-plan note.
- [ ] Add/update e2e test asserting the fenced block + 3-way question fire for
  standalone `/craft:refine` and at least one caller (`--refine` on `do`).

## Long-term (future sessions)

- [ ] Revisit `--target`/`--terse` only if real usage friction shows up (per
  2026-07-01's own explicit deferral condition — don't build speculatively).

## Recommended Next Step

→ **Quick Win #1+#2**: lock the 3-way vocabulary (Execute now / Edit first /
Skip) with an always-on fenced block, and add the explicit
print-before-ask instruction to `skills/workflow/prompt-refiner/SKILL.md`.
This directly fixes the reported bug and resolves the memory-vs-brainstorm
vocabulary conflict in one edit. The architecture doc (Medium Effort) is
worth doing right after, since it's a real standing gap this investigation
surfaced — but it's not blocking the bug fix.

No root-command creation is needed (Finding 0) — `/craft:refine` already works
as a root entry point; confirm whether the confirm-step fix above resolves the
"doesn't feel like a real command" impression before considering anything else.
