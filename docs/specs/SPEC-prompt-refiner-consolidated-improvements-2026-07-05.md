# prompt-refiner: Consolidated Improvement Plan (Issues #264, #265, #266, #267 + D7)

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Status:** Draft — first spec written for any of these four issues. All four were previously standalone GitHub issues with no spec coverage (confirmed by grep across `docs/specs/*.md`, 2026-07-05). Task 5 is not a new issue — it closes a dangling, never-actioned recommendation (D7) from `SPEC-interactive-commands-2026-06-25.md`, folded in per user decision 2026-07-05 rather than left open indefinitely.

**Note on Task 3:** originally specced as a narrow standalone-only execute-offer for #264. Superseded during audit (2026-07-05) — #264 is fully subsumed by the already-approved, not-yet-built uniform 4-way confirm redesign in `BRAINSTORM-refine-flags-2026-07-01.md` ("Execute now" = the ask). Task 3 below implements that redesign instead of the narrower original.

**Goal:** `skills/workflow/prompt-refiner/SKILL.md` (86 lines) currently has four independently-filed, non-overlapping gaps, all surfaced by real dogfooding sessions rather than speculative review. Rather than writing four separate specs against the same small file — which risks conflicting edits and repeated re-reads of the same 86 lines — this spec covers all four as ordered, independently-shippable tasks against one file.

**Why consolidate now:** the four issues touch four different, non-competing parts of the same canonical `## Procedure` block (lines 44-68) plus its `## Standalone use` modifier (lines 76-79):

| Issue | Touches | Kind of change |
|---|---|---|
| #267 | New gate *before* step 2 (rewrite) | Add a fast-path skip |
| #265 | Step 1 (line 46, "Read context") | Widen detection scope |
| #264 | `## Standalone use` (lines 76-79) | Add a follow-up question |
| #266 | New optional mode, parallel to `## Optional: explain mode` (lines 81-86) | Add an opt-in mode |

None of the four requires touching another's target section. They can be implemented and shipped independently in any order, but are specced together because they'll all be read/reviewed against the same file in the same sitting regardless.

**Background:** All four issues were filed 2026-07-04 through 2026-07-05, three (`#264`, `#265`, `#266`) from dogfooding `/craft:workflow:refine` in savant/manuscript-repo sessions, one (`#267`) from a research-manuscript session (`Data-Wise/missing-effect`) with a sibling issue filed in parallel against savant (`Data-Wise/savant#111`, not in scope here — different subsystem, different repo, referenced only for context).

## Global Constraints

- **This skill's own Constraints section (lines 70-74) is unconditional and applies to every task below**: never execute the prompt or call tools, never write files beyond the confirm/display flow, never touch secrets/tokens. None of the four tasks below changes this.
- **Single canonical Procedure block, no forking.** Per line 44's own instruction ("callers MUST delegate here"), every caller (brainstorm/do/orchestrate/plan:feature/arch:plan/grill) shares this one procedure. Any task that adds a gate or a new step must add it once, in the shared block — never duplicated per-caller.
- **Read `PLAN-refine-flag-2026-06-03.md` and `SPEC-refine-flag-2026-06-03.md` before editing** — these are the original build docs that established the current structure; changes should extend that structure, not contradict it.
- **Check `docs/specs/BRAINSTORM-refine-flags-2026-07-01.md`** for prior discussion of step 4 (confirm) before touching it for #264 — it already references updating that step for unrelated reasons; avoid stepping on unmerged work there.
- **`docs/specs/SPEC-orchestrator-consolidation-2026-07-04.md` (D6)** is the source of the Default Policy table (lines 17-36) — do not restructure that table's *contents* as part of this spec (which commands are ON/OFF stays as-is); it's out of scope. **Terminology retrofit (resolved 2026-07-05, grilled with user):** D6's table is the **policy-level default** — a per-*command* setting resolved once, before any prompt is seen. Task 1's new gate (below) is a **runtime skip-gate** — a per-*invocation* check, evaluated only after the policy-level default has already resolved to "run the procedure." These are two different mechanisms that can each cause `--refine` to not visibly run, and must be named as such (not left implicit) both in this spec and retroactively in `SKILL.md`'s own D6 section header/prose. **Decided:** the skip-gate is universal — it applies regardless of a command's policy-level default, meaning if `--refine` is ever force-enabled on an OFF-by-default command (e.g. `orchestrate`), the terse-prompt skip-gate still fires consistently. Task 1 Step 2 below is updated accordingly.

---

### Task 1: #267 — Skip the confirm round-trip for terse, unambiguous prompts

**Files:**

- Edit: `skills/workflow/prompt-refiner/SKILL.md` (insert a gate before step 2, i.e. between step 1 "Read context" (line 46) and step 2 "Rewrite" (line 47))

**Steps:**

- [ ] **Step 1:** Define the "action-verb-execution" pattern precisely enough to implement consistently: a single clear verb + an already-scoped target, no compound clauses (no "and", no multiple distinct asks), no ambiguous pronouns/references needing project context to resolve. Write this as an explicit, testable checklist (not just "terse"), grounded in the issue's own examples ("render the article", "commit and push" — note the issue's second example itself contains "and", so clarify in the checklist whether "commit and push" counts as one compound action verb pair that's still unambiguous, or whether the checklist needs to allow certain conjunctions when the two verbs are a known, tightly-coupled pair).
- [ ] **Step 2:** Insert a new step between current step 1 (Read context) and step 2 (Rewrite): "If the raw prompt matches the action-verb-execution pattern, skip steps 2-4 and return the prompt unchanged." Renumber subsequent steps accordingly. **Per the resolved terminology (Global Constraints, D6 note):** this skip-gate sits inside the shared Procedure block, which only runs once the policy-level default has already resolved to ON (or been force-enabled). It must fire the same way regardless of *which* command reached this point — do not special-case it per command. Also retrofit D6's table section in `SKILL.md` (lines 17-36) with a one-line clarification distinguishing "policy-level default" (this table) from "runtime skip-gate" (this new step), so a future reader isn't left inferring the distinction.
- [ ] **Step 3:** Confirm this new gate composes correctly with `## Standalone use` (lines 76-79) — if a terse prompt is refined standalone, does skipping steps 2-4 mean it just returns instantly with no confirm box at all? Decide and state explicitly whether that's the intended behavior (the issue implies yes: "pass the prompt through unchanged").
- [ ] **Step 4:** Confirm composition with the `--yes` auto-accept cascade (lines 63-67) — the new gate should be checked *before* auto-accept logic, since a matched terse prompt skips the box entirely rather than auto-accepting it.
- [ ] **Step 5:** Update the skill's frontmatter `description` (line 3) if the new behavior changes what triggers the skill — likely not, since the skill still fires the same way; only its internal behavior changes. Confirm rather than assume.

**Done when:** A terse, single-action-verb prompt passes through with no box/confirm shown; a compound or ambiguous prompt still runs the full existing procedure unchanged; both behaviors are demonstrated with at least one example each in the skill file's own prose (matching the existing style of inline examples elsewhere in the file).

---

### Task 2: #265 — Manuscript/research-project detection in Step 1

**Files:**

- Edit: `skills/workflow/prompt-refiner/SKILL.md` (extend the "Inputs" `context` bullet, lines 41-42, and Step 1, line 46)

**Steps:**

- [ ] **Step 1:** Add a manuscript/research-project detection branch parallel to the existing software-project branch, per the issue's proposal: presence of `references.bib` + a `.qmd`/`.tex` main file (the issue cites `/savant:restore`'s own project-detection logic as an existing pattern to mirror — read that command/skill first to match its detection approach rather than inventing a new one).
- [ ] **Step 2:** If detected, additionally note: whether a notation/symbol glossary table exists in the main file, whether `docs/reviews/` (or equivalent) has prior review docs on the same topic, and whether `.flow/research-config.yml` exists.
- [ ] **Step 3:** Keep this read-only, matching Step 1's existing constraint — this is a wider file-check, not a new capability class.
- [ ] **Step 4:** Update the "Inputs" section's `context` bullet (lines 41-42) to document the new detection branch alongside the existing project-type/branch/`.STATUS` list, so the Inputs section stays an accurate summary of what Step 1 actually checks.

**Done when:** Step 1, when run in a repo with `references.bib` + `.qmd`/`.tex`, surfaces the additional manuscript-specific context items; when run in a software repo, behavior is unchanged from today.

---

### Task 3: #264 — Uniform 4-way confirm (supersedes the original standalone-only Task 3)

**Design source:** `docs/specs/BRAINSTORM-refine-flags-2026-07-01.md` (Recommended Next Step, §"The debate," Option A) — already approved, never implemented. This task builds it, closing #264 as a side effect ("Execute now" = the execute-offer #264 asked for). Grilled and extended with the user 2026-07-05: destination sub-options and the scope flag below are new decisions on top of the original brainstorm doc.

**Files:**

- Edit: `skills/workflow/prompt-refiner/SKILL.md` (replace step 4 of `## Procedure`, lines 61-67, and `## Standalone use`, lines 76-79)
- Edit: `commands/refine.md`, `commands/do.md`, `commands/brainstorm.md`, `commands/orch.md`, `commands/plan/feature.md`, `commands/arch/plan.md` — wherever each currently describes the Accept/Edit/Use-original interaction, per the brainstorm doc's own Documentation section
- Test: grep `tests/test_interactive_commands_e2e.py` (and similar) for the old option labels before implementing, per the brainstorm doc's own flagged risk

**Steps:**

- [ ] **Step 1:** Replace step 4's Accept/Edit/Use-original with the single 4-way `AskUserQuestion`: **Execute now** (Recommended when a clear action is implied) / **Copy for elsewhere** / **Edit first** / **Skip**. Applied uniformly — standalone AND every `--refine` caller, no special-casing by invocation path (this reverses the original Task 3's standalone-only scoping, per the brainstorm doc's own explicit reversal of that framing).
- [ ] **Step 2:** Wire the mapping onto the old 3-way exactly as the brainstorm doc specifies: Execute now ≈ old Accept, Edit first ≈ old Edit, Skip ≈ old Use original (proceed with raw text, not an abort). "Copy for elsewhere" is the new 4th option — print the fenced code block, take no action, and **short-circuit whatever called `--refine`** (if `brainstorm --refine` hits this branch, brainstorm's own downstream question flow must never start).
- [ ] **Step 3 (new, grilled 2026-07-05 — destination sub-options for "Copy for elsewhere"):** Extend "Copy for elsewhere" with named sub-destinations instead of only printing to the terminal: plain print (default, current behavior), a named Apple Note, or an Obsidian research-prompts folder. **Decided:** the skill itself does NOT call any Apple Notes/Obsidian MCP tool directly — doing so would violate this skill's own unconditional Constraint (line 72, "NEVER execute the prompt or call tools") and would couple craft's shipped, cross-session behavior to one user's local app connections. Instead, the skill's output for this branch is structured text: the refined prompt plus a stated destination intent (e.g. a suggested note title). The actual write happens one layer up — in the calling session/context, which may have the relevant MCP tools connected — never inside `prompt-refiner`'s own procedure. Document this boundary explicitly in the skill file so it isn't reinvented differently later.
- [ ] **Step 4 (new, grilled 2026-07-05 — global/project-agnostic scope):** Add a separate **rewrite-time** flag (not a 4-way checkbox option) controlling whether Step 1 (context-read, including the Task 2/#265 manuscript-detection branch) runs at all before the rewrite. Proposed name: `--scope global` (sibling to the already-proposed-but-unbuilt `--scope minimal|full` idea in the same brainstorm doc's "Flag ideas" section — consider unifying into one `--scope` flag with three values: `minimal`/`full`/`global`, rather than two separate flags, if that doesn't overcomplicate the interface). **Decided:** this must NOT be a 3rd option inside the Accept-time checkbox — by the time Accept fires, Step 1's context-read has already happened, too late to make the rewrite itself project-agnostic. This is a pre-Step-1 decision, not a post-rewrite one.
- [ ] **Step 5:** Update all 6 affected command/skill files per the brainstorm doc's own Documentation checklist, replacing every Accept/Edit/Use-original reference with the new 4-way vocabulary — single-source guard, no caller re-describing the interaction independently.
- [ ] **Step 6 (`--yes` composition — resolves former open item "C"):** Per `SPEC-interactive-commands-2026-06-25.md` D2/D3 (already binding, cite directly rather than re-deciding): `--yes` auto-accepts every Recommended answer and emits zero `AskUserQuestion` calls. Applied here: under `--yes`, the 4-way question does not appear at all — it auto-picks "Execute now" (the Recommended option) exactly as D2/D3 already require for every other AskUserQuestion in scope. This was previously an open question in the original Task 3; it is resolved by pointing at D2/D3 rather than deciding fresh.

**Done when:** all 5 callers plus standalone show the same 4-way question (verified via the brainstorm doc's own e2e test plan: assert old 3-way wording is absent, new 4-way is present); "Copy for elsewhere" prints the fenced block and, when a named destination is chosen, hands back structured destination intent without the skill itself calling any external tool; `--scope global` (or unified `--scope`) is confirmed to run before Step 1, not as a checkbox choice; `--yes` auto-picks Execute now with zero prompts.

---

### Task 4: #266 — Optional multi-round "grill" mode

**Files:**

- Edit: `skills/workflow/prompt-refiner/SKILL.md` (new section parallel to `## Optional: explain mode`, lines 81-86)
- Reference: `commands/grill.md` and its skill (confirmed to already exist as separate, fully-built infrastructure — this task wires prompt-refiner to it rather than reimplementing a per-claim loop)

**Steps:**

- [ ] **Step 1:** Check whether `craft:grill`'s existing mechanics ("adversarially interrogate a plan, spec, or topic one question at a time") can be delegated to directly for the per-unit loop this issue describes, rather than reinventing decomposition/loop logic inside `prompt-refiner`. This is the issue's own explicit suggestion — read `commands/grill.md` and its skill fully before deciding for-or-against delegation.
- [ ] **Step 2:** If delegation is viable, add a new `## Optional: grill mode` section triggered by phrasing like "grill this" / "interrogate this one at a time", which hands off to `craft:grill`'s existing per-unit `AskUserQuestion` loop rather than adding new loop logic to this file.
- [ ] **Step 3:** If delegation is NOT viable (shapes turn out to differ meaningfully — e.g. grill's target is typically a whole plan/spec, not an arbitrary paragraph/claim), document why in this skill file and scope a minimal standalone implementation instead: decompose target into checkable units, one `AskUserQuestion` per unit (issue + 2-3 options + a recommendation), apply immediately (not batched), loop until user signals done.
- [ ] **Step 4:** Whichever path is taken, this must remain **opt-in** and additive — it must not change the default single-round rewrite-then-confirm flow (steps 1-5 in `## Procedure`) for any caller that doesn't explicitly request grill mode.

**Done when:** a "grill this paragraph" (or similar) request triggers the new multi-round per-unit loop instead of the default single rewrite-then-confirm cycle; the default flow is demonstrated unchanged for a normal `--refine` invocation after this change.

---

### Task 5: D7 — Resolve dangling refine-candidate disposition (`smart-help`, `spec-review`)

**Not a new GitHub issue** — this closes an already-recommended, never-actioned item from `docs/specs/SPEC-interactive-commands-2026-06-25.md` §8 (D7's refine-candidate matrix), folded into this pass per user decision (2026-07-05) rather than left dangling any longer. Confirmed both target files exist: `commands/smart-help.md` and `commands/workflow/spec-review.md`.

**Files:**

- Edit: `commands/smart-help.md` (add `--refine` as a declared, opt-in, default-OFF flag)
- No edit to `commands/workflow/spec-review.md` — see Step 2 (explicitly held, not added)
- Update: `docs/specs/SPEC-interactive-commands-2026-06-25.md` §8 — mark D7 as executed, with a pointer to this spec, so the matrix stops reading as an open recommendation

**Steps:**

- [ ] **Step 1 — `smart-help`:** Add `--refine` per D7's own exact verdict: "Recommend add (opt-in), default-OFF." This is opt-in like the original 6 pre-D3 commands, NOT default-on like `do`/`brainstorm`/`plan:feature`/`grill` — do not conflate the two policy tiers (see the D6-vs-skip-gate terminology fix, Global Constraints above: this is a third, distinct case — opt-in and OFF, whereas D6's table only covers already-default-on-or-off commands). Declare the flag in `smart-help.md`'s frontmatter the same way the other 5 pre-existing `--refine` callers do.
- [ ] **Step 2 — `spec-review`:** Take no action. D7's verdict was **hold**, not silence-by-omission: "arg is usually a spec name/path, weak freetext; refine rarely helps. Revisit if used as freetext." Record this explicitly (in the SPEC-interactive-commands update, Step 3 below) as a deliberate, closed decision — not an oversight — so a future audit doesn't re-surface it as another dangling item.
- [ ] **Step 3:** Update `SPEC-interactive-commands-2026-06-25.md` §8's closing line ("Locked for this spec: grill (D6). Recommended add: smart-help (opt-in). Held: spec-review.") with a dated note: "`smart-help` executed 2026-07-05, see `SPEC-prompt-refiner-consolidated-improvements-2026-07-05.md` Task 5. `spec-review` remains held — no new information since 2026-06-25 changes the verdict."
- [ ] **Step 4:** Confirm this task doesn't touch `skills/workflow/prompt-refiner/SKILL.md` itself — D7 only adds a new *caller*, it doesn't change the shared Procedure block. No interaction with Tasks 1-4 above.

**Done when:** `smart-help.md` declares `--refine` as opt-in/default-OFF; `SPEC-interactive-commands-2026-06-25.md` §8 no longer reads as an open recommendation for either command; `spec-review`'s hold is recorded as a decision, not a gap.

---

## Recommended execution order

Tasks are independently shippable (see the table in Background — none touches another's target section), but Task 1 (#267) is recommended first since it's the smallest, most self-contained change and the one most likely to have follow-on interactions with the others' entry points (Standalone use, auto-accept) that are cheaper to resolve while the file is still simple. Task 4 (#266) is recommended last, since it's the only task with an open implementation question (delegate to `craft:grill` vs. build standalone) that needs its own investigation before estimating effort. Task 5 (D7) can run at any point — it touches a different file (`commands/smart-help.md`) and has no dependency on or interaction with Tasks 1-4.

Do not implement all four in one uninterrupted pass without testing each independently — per this skill's own dogfood-tested history (the `PLAN-refine-flag-2026-06-03.md` anti-drift test referenced for the shared Procedure block), changes to this file are exercised by multiple callers and a regression in one caller's flow is easy to miss if all four changes are bundled into a single untested diff.
