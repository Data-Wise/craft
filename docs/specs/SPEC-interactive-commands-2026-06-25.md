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
| **D6** | **Refine on grill** | Add `- name: refine` to `grill.md`, **default-on** for a quoted/bare topic (the freetext that seeds the skeleton); **SKIP** refine when the argument is a path (spec/plan/diff file — nothing to refine). Bumps the sanctioned refine set 6 → 7; `test_refine_flag_scope` expected-set must add `commands/grill.md`. |
| **D7** | **Other refine candidates** | Evaluated, NOT auto-added (avoid silent scope creep) — see §8 matrix. Recommend **grill** (D6, locked) + **smart-help** (refine the help query); **hold** `spec-review` (arg is usually a spec name/path, weak freetext). User confirms §8 before any beyond grill land. |

## 3. Affected files

**Interaction model (D1/D2):**

- `commands/grill.md` — rewrite Step 3 loop (free-text → AskUserQuestion-per-branch + consequences); invert line 52 directive; add `--yes`/`--non-interactive`. Keep `--bound N`, `--no-capture`, milestone checkpoints (already AskUserQuestion).
- `commands/orchestrate.md` — Step 0.5 clarify adopts D1; add `--yes`.

**Refine default-on (D3/D4):**

- `commands/workflow/brainstorm.md`, `commands/do.md`, `commands/plan/feature.md` — flip `--refine` documentation to "runs by default; `--no-refine` to skip"; wire `--yes` → refine auto-accept.
- `commands/grill.md` (D6) — add `- name: refine` frontmatter; default-on for quoted/bare topic, skip for path arg.
- `skills/workflow/prompt-refiner/SKILL.md` — confirm `--yes`/auto auto-accept path is documented (already exists per refine flow).

**Test fixtures (must change in lockstep):**

- `tests/test_plugin_e2e.py::test_refine_flag_scope` — `expected` set 6 → 7 (add `commands/grill.md`). The default-on commands still DECLARE `- name: refine` (the flag still exists as the opt-out's inverse), so the keying logic is unchanged; only the membership set grows.

## 4. Test plan (TDD)

Two tiers, mirroring craft's split: **e2e** = structural/declaration checks against the command
tree (no execution); **dogfood** = run real scripts/parsers against live repo state and assert
real output. Markers: `pytest.mark.e2e`, `pytest.mark.dogfood`.

### 4a. e2e (structural — `tests/test_plugin_e2e.py`)

- [ ] **`test_refine_flag_scope`** (EDIT existing): expected set 6 → 7, add `commands/grill.md`. Asserts no extra/missing declarers — the regression guard for D6.
- [ ] **refine default-on declared**: `brainstorm.md`, `do.md`, `plan/feature.md`, `grill.md` each document default-on + a `--no-refine` opt-out (assert the frontmatter/prose contract, not behavior).
- [ ] **`--yes` flag declared**: `grill.md` + `orchestrate.md` declare `- name: yes` (alias `non-interactive`) in frontmatter.
- [ ] **grill interaction directive inverted**: `grill.md` no longer carries the "do not fix to batches" line; instead documents AskUserQuestion-per-branch + Recommended-first + consequences (assert the new contract string is present, old is absent).
- [ ] **grill path-vs-topic refine rule**: `grill.md` documents "skip refine when arg is a path".

### 4b. dogfood (behavioral — `tests/test_plugin_dogfood.py`)

- [ ] **grill `--yes` headless**: invoke grill in `--yes` mode on a fixture topic → ZERO AskUserQuestion calls, all Recommended auto-picked, `GRILL-*` ledger still written (assert file exists + decisions captured).
- [ ] **grill interactive structure**: a grilled branch emits options where option[0] is the Recommended and every option carries a consequence line (assert structure of the emitted question payload, not prose).
- [ ] **refine default-on fires**: running `brainstorm`/`do`/`plan:feature` with NO `--refine` flag triggers the prompt-refiner path (assert the refiner is invoked, e.g. via a marker/log).
- [ ] **`--no-refine` skips**: same commands with `--no-refine` do NOT invoke the refiner.
- [ ] **`--yes` cascade**: one `--yes` both auto-accepts the refiner AND suppresses the interactive loop (assert both effects from a single flag).
- [ ] **grill refine skips on path arg**: grill on a spec *path* does NOT invoke the refiner; grill on a quoted *topic* does.
- [ ] **orchestrate clarify**: Step 0.5 clarify uses the D1 model and honors `--yes` (no prompts in headless mode).

## 5. Cascade / non-goals

- **No new commands** → no 30-file count cascade. Flag + behavior changes only.
- **Non-goal:** changing what questions get asked — only *how* (structure) and *whether* (flag).
- **Non-goal v1:** the consistency follow-ons in D5 (drive/plan/workflow/roadmap/sprint/arch) — separate PR if desired.

## 6. Open questions (resolve at implementation)

1. Flag name final call: `--yes` vs `--non-interactive` as the canonical (other = alias). *Lean `--yes` (shortest, matches refine).*
2. Should `--yes` on a command with refine-default-on also imply `--no-refine` is unnecessary (refine just auto-accepts)? *Yes per D4 — document explicitly.*
3. grill's `--no-capture` embedded path (orchestrate Step 0.5): does it inherit `--yes` from the orchestrate parent automatically? *Lean yes — parent flag propagates.*

## 7. Documentation

Doc updates land in the SAME PR as the behavior change (craft convention — no doc lag).

- [ ] **`commands/grill.md`** — self-docs: replace the "deliberate free-text / no batches" rationale with the AskUserQuestion-per-branch + Recommended-first + consequences model; document `--yes`/`--non-interactive` and the refine path-vs-topic rule.
- [ ] **`commands/orchestrate.md`** — document `--yes` and the D1 clarify model.
- [ ] **`commands/{workflow/brainstorm,do,plan/feature}.md`** — flip `--refine` description to "on by default; `--no-refine` to skip".
- [ ] **`commands/hub.md`** — any `--refine` opt-in mention → "default-on"; grill row notes `--yes`.
- [ ] **Refcards / tutorials** — `commands/git/docs/refcard.md` is git-only; check `help:refcard`, `help:refcards:quick-reference`, and any `--refine` tutorial stub. `grep -rl "\-\-refine" docs/ site/` for the long tail.
- [ ] **CHANGELOG** (root + `docs/CHANGELOG.md` — must mirror, per release rule) — `### Changed`: refine default-on for brainstorm/do/plan/grill; grill/orchestrate interactive model + `--yes`.
- [ ] **Memory** — update/retire any memory entry pinning grill's old "free-text, no batches" design so future sessions don't re-assert it.
- [ ] **`docs-staleness-check.sh --fix`** — run after edits to sweep mechanical `--refine` references.

## 8. Refine-candidate matrix (D7 — "other candidates for grill")

Scan of every command with a free-text NL argument (the precondition for refine being useful):

| Command | NL arg | Has `--refine` now | Verdict |
|---------|--------|--------------------|---------|
| `do` | task description | ✅ | **default-on** (D3) |
| `plan:feature` | feature description | ✅ | **default-on** (D3) |
| `workflow:brainstorm` | topic | ✅ | **default-on** (D3) |
| **`grill`** | quoted/bare topic | ❌ | **ADD + default-on** (D6, locked) — skip on path arg |
| `orchestrate` | task description | ✅ | keep opt-in (long run; refine at entry only) |
| `orchestrate:workflow` | engine input | ✅ | keep opt-in |
| `arch:plan` | plan topic | ✅ | keep opt-in |
| **`smart-help`** | topic / question | ❌ | **candidate** — refine the help query. Lower value (help is quick) but cheap. **Recommend add (opt-in), default-OFF.** |
| **`workflow:spec-review`** | spec name / topic | ❌ | **hold** — arg is usually a spec *name/path*, weak freetext; refine rarely helps. Revisit if used as freetext. |

**Interaction-model candidates** (commands that could adopt the D1 grill-style structured Q&A
beyond grill+orchestrate): `workflow:brainstorm` milestone checkpoints (already AskUserQuestion),
`plan:*` clarifications, `workflow:spec-review`. Out of scope v1 — listed for a future sweep.

**Locked for this spec:** grill (D6). **Recommended add:** smart-help (opt-in). **Held:** spec-review.
Everything beyond grill needs user sign-off (per D7) before it lands.

---

## Handoff

`/craft:plan` (tier 4) → `ORCHESTRATE-interactive-commands.md` → worktree → TDD per §4.
