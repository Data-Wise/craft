# /craft:do Token-Efficiency Audit — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Status:** **GATED — do not execute Task 2 (extraction) until the 2026-07-14 `/usage` checkpoint closes.** Task 1 (classification, read-only) may proceed now. See "Gate" below — this SPEC's premise (splitting a command's body into a skill reduces always-loaded cost) is exactly the question `GRILL-craft-bloat-strategy-2026-07-01.md` found unresolved and explicitly put on HOLD pending real measurement.

**Goal:** Apply the `command-skill-token-efficiency` skill's classification test to `commands/do.md` (1044 lines, the single largest always-loaded command file in the repo — roughly 3.3x the next largest, `agents/orchestrator.md` at 299 lines is the next agent-side comparator, but among commands specifically `do.md` dwarfs everything else). Determine which sections are genuinely invocation-specific (must stay) versus procedural content that could load conditionally as a skill instead, measure the result with `scripts/token-probe.py`, and either execute the split or record why not, with evidence.

**Background:** Raised as Repo Task R1 in the 2026-07-01 usage-report proposal (session artifact `token_efficiency_proposal_2026w27`), itself grounded in the existing `command-skill-token-efficiency` skill (`skills/code/command-skill-token-efficiency/SKILL.md`, built on PR #232's methodology) and `scripts/token-probe.py` (built per `docs/specs/SPEC-token-efficiency-and-context-tooling-2026-07-01.md` Task 2). This SPEC does not invent new methodology — it applies existing, already-validated tools to a file that hasn't been audited with them yet.

**Gate (added 2026-07-01, after cross-referencing `GRILL-craft-bloat-strategy-2026-07-01.md`):** That grill session measured, at rest, that craft's 43 skill descriptions already cost *more* in always-loaded tokens (~3,858) than all 115 command descriptions combined (~1,613) — because skills need verbose auto-fire trigger language where commands get terse one-liners. It found form-conversion (command body → skill) likely *increases* resting cost rather than decreasing it, and locked in a pre-committed criterion: **pursue command↔skill conversion only if the ~2026-07-14 `/usage` checkpoint shows command *bodies* (not just descriptions) actually preload.** `do.md` is a command body — this SPEC's Task 2 is precisely the kind of conversion that gate covers. Task 1 (pure classification, no file edits) is unaffected and can run now; it produces the evidence needed to act fast once the gate lifts, either direction.

**Architecture:** No new tooling. Read `do.md`, classify each section per the skill's stays-in-command vs. belongs-in-skill test, extract what qualifies into a skill (or skills, if the content splits along natural lines — e.g. Agent Delegation Workflow vs. Branch-Aware Routing may not belong together), leave `do.md` as a thin router pointing at the extracted skill(s), then verify nothing was silently dropped.

**Tech stack:** Markdown editing, `scripts/audit-deprecated-commands.py --pair`, `scripts/token-probe.py`, `pytest`. No code changes outside `commands/`, `skills/`, and test files.

## Global Constraints

- **Extract, don't summarize.** Per the token-efficiency skill's explicit rule: if a section moves to a skill, move the actual content, not a condensed paraphrase. Compression can happen later once nothing is confirmed to depend on exact wording.
- **`do.md` must remain self-describing without the skill loaded.** Per the skill's own test: "if you deleted the skill, would the command still make sense as a pointer to it?" If a reviewer can't tell what `/craft:do` does from `do.md` alone (even briefly), the split isn't right yet.
- **Branch-Aware Routing (lines ~138-182) is a strong candidate to STAY in the command**, not extract — it's invocation-specific behavior (what happens depends on which branch the user is on right now), not shared procedure. Don't extract it reflexively just because it's long; apply the actual test from the skill, not a line-count heuristic alone.
- **Do not run the full pytest suite in a way that silently skips files** — per the skill's own cautionary note, a scoped check missed three real regressions on the original PR #232 split. This audit must run the full suite before being called done, not a targeted subset.

---

### Task 1: Classify `do.md`'s sections

**Files:**

- Read: `commands/do.md` (full file, not excerpts — 1044 lines)
- Reference: `skills/code/command-skill-token-efficiency/SKILL.md` (the classification test)

**Steps:**

- [ ] **Step 1:** Read `do.md` top to bottom. For each `##`/`###` section (already enumerated via `grep -n "^#\|^##"` — Usage, `--refine`/`--no-refine`, Dry-Run Mode, Branch-Aware Routing, `--plan` sugar-forwarding, How It Works, Agent Delegation Workflow (4 steps), Agent Delegation Rules, Examples (5 subsections)), tag it: **stays** (invocation-specific — flags, frontmatter, branch-dependent behavior) or **candidate** (procedure — same regardless of invocation context, could load conditionally).
- [ ] **Step 2:** For each **candidate** section, apply the "delete the skill, does the command still make sense as a pointer" test from the skill. Note pass/fail per section.
- [ ] **Step 3:** Group the sections that pass Step 2 into one or more coherent skills — don't force everything into a single skill if the content splits along natural lines (e.g. "Agent Delegation Workflow + Rules" is one coherent procedure; "Examples" may be better left inline as brief illustrations rather than extracted, since examples are arguably invocation-adjacent documentation, not procedure — apply the test, don't assume).
- [ ] **Step 4:** Write the classification as a table (section → stays/candidate → target skill name if candidate) at the top of a scratch file before touching `do.md` itself, so the plan is reviewable before execution.

**Done when:** Every section in `do.md` has a stays/candidate tag and candidates have a proposed destination skill, written down before any file is edited.

---

### Task 2: Execute the extraction

**BLOCKED until the 2026-07-14 `/usage` checkpoint confirms command bodies preload (see Gate, top of file). Do not run this task before then without re-confirming the gate is lifted.**

**Files:**

- Edit: `commands/do.md` (thin down to stays-sections + pointer to new skill(s))
- Create: one or more `skills/<area>/<name>/SKILL.md` (per Task 1's grouping)

**Steps:**

- [ ] **Step 1:** For each candidate group from Task 1, scaffold a new skill following existing convention (frontmatter with a triggering `description`, structured per `command-skill-token-efficiency`'s own layout as a template for structure, not content).
- [ ] **Step 2:** Move (not copy-and-trim) the actual section content into the new skill(s). Verify nothing was paraphrased away — a line-by-line diff against the original section is the check, not a read-through.
- [ ] **Step 3:** Replace each moved section in `do.md` with a short pointer (matching the existing `deprecated`/`replaced-by` thin-shim convention used elsewhere in the repo, e.g. ADR-002's `/done` precedent) — a sentence or two saying what the skill covers, not a summary of its content.
- [ ] **Step 4:** Check the new skill's `description` against all existing skill descriptions for a trigger-phrase collision (a quoted phrase another skill already claims) — this is the exact class of regression that broke silently on PR #232's original split.

**Done when:** `do.md` contains only stays-sections plus pointers; new skill(s) contain the full original content of every candidate section, verified via diff.

---

### Task 3: Measure and verify

**Files:**

- Run: `scripts/token-probe.py`
- Run: `scripts/audit-deprecated-commands.py --pair`
- Run: `pytest tests/` (full suite)

**Steps:**

- [ ] **Step 1:** `python3 scripts/token-probe.py --before <path to a saved pre-edit copy of do.md> --after commands/do.md` — get a real, measured token delta on the always-loaded path, not an eyeballed line-count estimate. State the cl100k_base-vs-Claude's-tokenizer caveat per the script's own docstring when reporting the number.
- [ ] **Step 2:** `python3 scripts/audit-deprecated-commands.py --pair commands/do.md skills/<new-skill-path>/SKILL.md` for each new skill — confirm the line-count ratio is under the 2.0 threshold, or explain why not if it's justifiably over (the check is WARN-only, not a hard gate).
- [ ] **Step 3:** Run the full test suite (`python3 -m pytest tests/`, not a scoped subset) per the skill's explicit warning about what a scoped check misses. Specifically check for: trigger-phrase collisions (skill-uniqueness test), any test asserting a specific string existed in `do.md` that the extraction may have moved, and any sibling command (if others share `do.md`'s `--refine`/`--plan` patterns) that expected something `do.md` no longer documents inline.
- [ ] **Step 4:** If any test fails, diagnose whether it's a genuine regression (content lost) or a stale test that needs updating to reflect the new, correct structure — per the skill's framing, a token-reduction edit that silently drops capability is a regression, not a win.

**Done when:** Token-probe result recorded, ratio-check passed or justified, full suite green (or failures triaged and resolved, not ignored).

---

### Task 4: Record the result

**Files:**

- Update: `docs/internal/TOKEN-EFFICIENCY-craft.md` (add this audit as a second instance of the pattern, alongside the original `/refine`/`/brainstorm` work)
- Update: `.STATUS` (session summary, per repo convention)

**Steps:**

- [ ] **Step 1:** Add a section to `TOKEN-EFFICIENCY-craft.md` documenting the before/after line counts and the measured token-probe delta for `do.md`, in the same file-by-file table format the doc already uses for `/refine` and `/brainstorm`.
- [ ] **Step 2:** If the audit concluded no extraction was warranted (e.g., most of `do.md` turned out to be genuinely invocation-specific per Task 1), record that explicitly as a finding too — "audited, no action" is a valid and useful outcome, not a failure to report quietly.
- [ ] **Step 3:** Update `.STATUS` per the repo's existing per-session convention.

**Done when:** The audit's outcome (extraction executed, or explicitly declined with reasoning) is documented in the same place future contributors would look for the original PR #232 record.

---

## Recommended execution order

Task 1 → Task 2 → Task 3 → Task 4, strictly sequential. Do not skip Task 1's written classification table before editing `do.md` directly — the original PR #232 regressions all trace back to moving content before fully accounting for what depended on it staying put.
