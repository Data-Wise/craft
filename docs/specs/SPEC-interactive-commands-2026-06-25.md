# SPEC: Interactive-by-default commands + refine-by-default

**Status:** APPROVED (design) · **Date:** 2026-06-25 · **Driver:** user directive (grill/orchestrate interaction model + refine automation)
**Decisions locked via grill (2026-06-25):** AskUserQuestion+consequences · refine default-on opt-out · brainstorm→spec→worktree

---

## 1. Problem

Three related friction points in craft's interactive commands:

1. **`grill`** uses one-at-a-time *free-text* questions and explicitly forbids AskUserQuestion
   batches (`commands/grill.md:52`). The user wants every question rendered as **selectable
   options with a Recommended choice first and per-option consequences** — the global
   "ask-question-recommendations" preference. The current design contradicts that.
2. **`orchestrate`** (and its Step 0.5 clarify, which embeds grill) should adopt the same
   interaction model, plus a **non-interactive escape hatch** for automation/headless runs.
3. **`--refine`** is opt-in on 6 commands. For `brainstorm`, `do`, `plan` it should run
   **by default** (the prompt is always pre-processed) with an opt-out.

## 2. Locked decisions

| # | Decision | Detail |
|---|----------|--------|
| **D1** | **Interaction model** | grill + orchestrate ask **one question per AskUserQuestion call**: Recommended option FIRST, a one-line **consequence per option**, always an implicit "Other" free-text. Inverts grill's "no batches" directive (still one-at-a-time — *not* 4-question batches; the change is free-text → structured options). |
| **D2** | **Non-interactive flag** | `--yes` (alias `--non-interactive`) auto-accepts every Recommended answer, emits **zero** AskUserQuestion calls, logs each auto-pick. Consistent with prompt-refiner's existing `--yes`/auto. |
| **D3** | **Refine default-on** | `brainstorm`, `do`, `plan:feature` run prompt-refiner **by default**; `--no-refine` skips. Under `--yes`, refine auto-accepts (no Accept/Edit prompt). |
| **D4** | **Flag cascade** | A command's `--yes` cascades into refine AND the interactive loop — one flag, fully headless. `--no-refine` is independent of `--yes`. |
| **D5** | **Scope boundary** | Primary: `grill.md`, `orchestrate.md` (+ Step 0.5 clarify), `brainstorm.md`, `do.md`, `plan/feature.md`. Consistency follow-ons (note, don't block): `orchestrate/{drive,plan,workflow}.md`, `plan/{roadmap,sprint}.md`, `arch/plan.md`. |

## 3. Affected files

**Interaction model (D1/D2):**

- `commands/grill.md` — rewrite Step 3 loop (free-text → AskUserQuestion-per-branch + consequences); invert line 52 directive; add `--yes`/`--non-interactive`. Keep `--bound N`, `--no-capture`, milestone checkpoints (already AskUserQuestion).
- `commands/orchestrate.md` — Step 0.5 clarify adopts D1; add `--yes`.

**Refine default-on (D3/D4):**

- `commands/workflow/brainstorm.md`, `commands/do.md`, `commands/plan/feature.md` — flip `--refine` documentation to "runs by default; `--no-refine` to skip"; wire `--yes` → refine auto-accept.
- `skills/workflow/prompt-refiner/SKILL.md` — confirm `--yes`/auto auto-accept path is documented (already exists per refine flow).

**Docs / memory:**

- Update the grill design note (the "deliberate free-text, no batches" rationale) to reflect the new structured-options model — in `grill.md` itself and any memory entry that pins the old design.
- `commands/hub.md` / refcards mentioning `--refine` as opt-in → "default-on".

## 4. Test plan (TDD)

- [ ] **grill --yes**: zero AskUserQuestion calls, all Recommended auto-picked, ledger still written.
- [ ] **grill interactive**: each branch emits options with a Recommended-first + consequence (assert structure, not prose).
- [ ] **refine default-on**: `brainstorm`/`do`/`plan:feature` invoke prompt-refiner with no `--refine` flag present.
- [ ] **--no-refine**: skips the refiner.
- [ ] **--yes cascade**: refiner auto-accepts AND interactive loop is suppressed in one flag.
- [ ] **orchestrate clarify**: Step 0.5 uses the D1 model + honors `--yes`.

## 5. Cascade / non-goals

- **No new commands** → no 30-file count cascade. Flag + behavior changes only.
- **Non-goal:** changing what questions get asked — only *how* (structure) and *whether* (flag).
- **Non-goal v1:** the consistency follow-ons in D5 (drive/plan/workflow/roadmap/sprint/arch) — separate PR if desired.

## 6. Open questions (resolve at implementation)

1. Flag name final call: `--yes` vs `--non-interactive` as the canonical (other = alias). *Lean `--yes` (shortest, matches refine).*
2. Should `--yes` on a command with refine-default-on also imply `--no-refine` is unnecessary (refine just auto-accepts)? *Yes per D4 — document explicitly.*
3. grill's `--no-capture` embedded path (orchestrate Step 0.5): does it inherit `--yes` from the orchestrate parent automatically? *Lean yes — parent flag propagates.*

---

## Handoff

`/craft:plan` (tier 4) → `ORCHESTRATE-interactive-commands.md` → worktree → TDD per §4.
