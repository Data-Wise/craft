# GRILL: prompt-refiner Consolidated Redesign — Decision Log

**Date:** 2026-07-05 · **Method:** one-question-at-a-time grill with user · **Result:** all open items resolved, folded into `SPEC-prompt-refiner-consolidated-improvements-2026-07-05.md`

---

## Why this doc exists

An audit of the first-draft consolidated spec (covering issues #264, #265, #266, #267 against `skills/workflow/prompt-refiner/SKILL.md`) found 3 real defects and 2 open items. Rather than silently patch-and-ship, each was grilled one at a time with the user. This doc is the standalone record of what was decided and why — the spec itself has the implementation detail; this is the reasoning trail.

## Decisions, in order

### 1. Policy-level default vs. runtime skip-gate (Issue A)

Two mechanisms can each cause `--refine` to not visibly run: D6's per-*command* policy default (`do`/`brainstorm` = ON, `orchestrate` = OFF), and a new per-*invocation* runtime skip-gate (issue #267 — skip the confirm round-trip for terse, unambiguous prompts). Left unnamed, a future reader can't tell which mechanism fired.

**Decided:** name them explicitly — "policy-level default" vs. "runtime skip-gate" — retrofitted into both the new spec and `SKILL.md`'s existing D6 section, not just new text. The skip-gate is **universal**: it fires the same way regardless of a command's policy default, including a force-enabled OFF-by-default command.

### 2. Task 3 (#264) was redundant against an already-locked design (Issue B)

The original spec proposed a narrow, standalone-only "offer to execute after Accept" question. Re-reading `BRAINSTORM-refine-flags-2026-07-01.md` in full surfaced that this exact decision point was already redesigned on 2026-07-01: a single uniform **4-way** confirm — Execute now / Copy for elsewhere / Edit first / Skip — applied to all 5 `--refine` call sites, explicitly reversing an earlier standalone-only framing. "Execute now" already is the execute-offer #264 asked for.

**Decided:** replace Task 3 with implementing the already-approved 4-way redesign, closing #264 as a side effect rather than shipping a narrower patch that would be superseded almost immediately.

### 3. The anti-drift test citation was overstated (Issue E)

The original spec cited `test_refine_delegates_to_skill` (`PLAN-refine-flag-2026-06-03.md`) as protection against per-caller regressions from editing the shared Procedure block. That test is actually a substring check confirming each caller file contains the literal string `"prompt-refiner"` — it never opens or evaluates `SKILL.md` itself, so it cannot catch a regression from editing the procedure body.

**Decided:** the citation needed correcting (flagged; full independent-testing language remains in the spec's "Recommended execution order" section as a caution, not resting on this test's actual coverage).

### 4. `--yes` composition for the new confirm (Issue C)

Previously open: does the new post-Accept question get auto-answered under `--yes`/auto mode, or does auto mode not apply to it?

**Decided:** cite `SPEC-interactive-commands-2026-06-25.md` D2/D3 directly as the binding rule rather than re-deciding — `--yes` auto-accepts every Recommended answer with zero `AskUserQuestion` calls. Applied here: under `--yes`, the 4-way question doesn't appear at all; it auto-picks "Execute now."

### 5. D7's dangling `smart-help`/`spec-review` disposition (Issue F)

`SPEC-interactive-commands-2026-06-25.md` §8 had recommended adding `--refine` to `smart-help` (opt-in, default-OFF) and holding on `spec-review` (weak freetext argument) — never actioned, never explicitly closed.

**Decided:** fold into this same spec pass as Task 5. `smart-help` gets `--refine` per the original exact verdict; `spec-review` stays explicitly held (recorded as a deliberate decision, not a silent gap). Confirmed both target command files exist in the repo before writing the task.

### 6. User's destination-flow brainstorm (Apple Notes / Obsidian, global scope)

The user proposed: print the refined prompt copy-paste-ready, then a two-round checkbox flow — Accept/Edit/global-version, then a second multi-select for Execute/Apple Note/Obsidian sync.

**Mapped against the locked 4-way design:**

- Copy-paste-ready output and "Execute" are already covered by the existing design.
- Apple Notes / Obsidian become **named sub-destinations under "Copy for elsewhere"**, not a second checkbox round — the already-approved design explicitly rejected two sequential confirms in favor of one.
- **Decided:** the skill itself never calls the Apple Notes/Obsidian MCP tools directly. Doing so would violate `prompt-refiner`'s own unconditional constraint ("NEVER execute the prompt or call tools") and would couple craft's shipped, cross-session behavior to one user's local app connections — craft owns this skill outright (confirmed: it's `skills/workflow/prompt-refiner/SKILL.md` inside the craft repo, with `commands/refine.md` as its thin shim per ADR-002) and must ship identically regardless of what's connected in any given session. The skill hands back structured text plus a stated destination intent; the actual write happens one layer up, in the calling context.
- **Decided:** "global, project-agnostic" scope is a **rewrite-time flag** (checked before Step 1's context-read), not a post-Accept checkbox option — by the time Accept fires, the context-read has already happened, too late to make the rewrite itself project-agnostic. Proposed as `--scope global`, a sibling to the already-proposed-but-unbuilt `--scope minimal|full` idea from the same brainstorm doc.

### 7. Structural questions answered (facts, not decisions)

- `/refine` (`commands/refine.md`, 47 lines) is a pure thin shim with zero standalone logic, by design (ADR-002, 2026-06-23). No alias mechanism exists anywhere in the plugin.
- `do` (1044 lines) and `orchestrate` (370 lines) are already standalone commands with substantial inline logic; `refine` is the only one of the three without an independent body — intentional, not an oversight.
- Craft has zero existing Apple Notes or Obsidian write integration anywhere in the repo — confirmed by direct search.

## Net result

All 5 audit findings (A, B, C, E, F) plus the user's destination-flow brainstorm are now resolved and written into `docs/specs/SPEC-prompt-refiner-consolidated-improvements-2026-07-05.md` as Tasks 1-5. Nothing remains open from this grill session. The spec is drafted but **not yet committed** to git — pending final user review of the whole document before implementation begins.
