# Proposal: Superpowers Scoping Correction, claude-context Pilot, Reusable Token Probe

**Status:** Ready to implement
**Date:** 2026-07-01
**Related:** `docs/internal/TOKEN-EFFICIENCY-craft.md`, `docs/specs/SPEC-token-efficiency-research-2026-06-30.md`, PR #232, `docs/plans/2026-06-30-namespace-token-probe.md`, outputs/report/`Token-Efficiency-Report-and-Proposal.docx` (external deliverable — Section 3.3/C1 needs correction per Finding 1)

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement Task 2 and Task 3 below task-by-task. Task 1 and Task 4 are small enough to do directly.

---

## Context (read before starting)

Two established findings anchor this proposal. Both were verified directly against repo state, not inferred from external research.

**Finding 1 — Superpowers is not a competitor to craft; `subagent-driven-development` is craft's execution engine.**

Every file under `docs/plans/*.md` requires `superpowers:subagent-driven-development` (or `superpowers:executing-plans`) as a sub-skill. `.STATUS` documents multiple shipped releases built exactly this way (v2.52.0: "spec→grill→plan→subagent-driven-TDD"; v2.49.x: "craft:grill → superpowers writing-plans → 2 dynamic Workflows"). `.superpowers/sdd/` contains 39 real review-diff artifacts — active use, not a dormant dependency.

A previously delivered external report (`Token-Efficiency-Report-and-Proposal.docx`, Section 3.3/C1) recommended blanket non-adoption of Superpowers. That call is correct only for Superpowers' orchestrate/brainstorm/clarify-design-plan-code-verify layer, which genuinely overlaps with `/craft:orchestrate` + `/craft:grill`. It's wrong for `subagent-driven-development`, which craft's own plan template already requires. The corrected, scoped verdict:

| Superpowers component | Verdict |
|---|---|
| `subagent-driven-development` | Keep — load-bearing, no craft replacement exists |
| `executing-plans` | Keep as documented fallback — usage vs. `subagent-driven-development` unconfirmed (see Task 4) |
| orchestrate/brainstorm/clarify-design-plan-code-verify layer | Do not adopt — redundant with `/craft:orchestrate` + `/craft:grill` |

**Finding 2 — claude-context has zero namespace clashes with craft or savant.**

`craft/.mcp.json` registers only `mcp-mermaid`. `savant/.claude-plugin/plugin.json` registers no MCP servers at all (commands + skills only). Adding claude-context's MCP server introduces no tool-name collisions. It is a parallel, opt-in semantic-search path for large/fuzzy queries — not a replacement for `Grep`/`Glob`, which stays correct and cheaper for exact-match lookups. Best-fit pilot surface: `~/projects/r-packages/` (6-package MediationVerse ecosystem) — large enough that a vague query can pull 10k+ irrelevant tokens via grep today. Not craft itself (too small to need it).

---

## Task 1: Correct the delivered report's Superpowers section

**Effort: ~15 min. No sub-skill required — do directly.**

**Files:**

- Edit: `outputs/report/Token-Efficiency-Report-and-Proposal.docx` (or wherever this file lives when the session starts — locate via `find . -iname "Token-Efficiency-Report*"` if the path above is stale)

**Steps:**

- [ ] Open the docx skill (`docx` — read/edit existing document workflow) and locate Section 3.3 / recommendation C1 ("Do not adopt Superpowers").
- [ ] Replace the blanket verdict with the scoped table from Finding 1 above (three rows: `subagent-driven-development` / `executing-plans` / orchestrate-brainstorm layer).
- [ ] Add a visible correction marker, e.g. italic note: "Corrected 2026-07-01: this recommendation originally applied to the whole Superpowers plugin; scoped down after direct repo inspection found `subagent-driven-development` already required by craft's plan template."
- [ ] Re-validate the docx (`scripts/office/validate.py` per the docx skill) and re-save.

**Done when:** Section 3.3 reflects the three-row scoped table, not a single up/down call.

---

## Task 2: Build a reusable token-probe script

**Effort: ~30-45 min. Do this before Task 3 — it makes the claude-context pilot measurable instead of anecdotal.**

**Files:**

- Create: `scripts/token-probe.py`
- Reference: `docs/plans/2026-06-30-namespace-token-probe.md` (source methodology — disposable `scratch/namespace-probe/` script, `tiktoken` cl100k_base, measured 68.3% reduction on the namespace-consolidation question)
- Delete when done: any leftover `scratch/namespace-probe/*` files if still present

**Steps:**

- [ ] **Step 1:** Read the existing disposable probe at `docs/plans/2026-06-30-namespace-token-probe.md` in full to recover its comparison logic (synthetic before/after fixture generation, `tiktoken` counting, printed diff).
- [ ] **Step 2:** Generalize it into `scripts/token-probe.py` — parameterize on two file-set globs (`--before <glob>` / `--after <glob>`) instead of hardcoded namespace fixtures, so it works for any future "should we merge/split X" question, not just the namespace refactor.
- [ ] **Step 3:** Keep the cl100k_base-vs-Claude's-real-tokenizer caveat, stated once in the script's module docstring (it's a relative-comparison tool, not an exact Claude token count).
- [ ] **Step 4:** Add a `--help` usage example and a one-line entry in the relevant docs table (check `docs/REFCARD.md` or wherever `scripts/` utilities are indexed — search for `audit-deprecated-commands.py`'s entry as a pattern to follow).
- [ ] **Step 5:** Run it once against a real before/after pair to confirm it reproduces (approximately) the original 68.3% namespace-refactor figure, as a sanity check.

**Done when:** `python3 scripts/token-probe.py --before <glob> --after <glob>` runs standalone and produces a token-count comparison with no hardcoded fixture data.

---

## Task 3: Draft the claude-context pilot skill

**Effort: ~1-2 hrs including before/after measurement via Task 2's script.**

**Files:**

- Create: `skills/code/semantic-code-search/SKILL.md`
- Reference/template: `skills/code/command-skill-token-efficiency/SKILL.md` (existing skill already encoding the thin-command/fat-skill authoring convention — copy its structure, not its content)

**Steps:**

- [ ] **Step 1:** Scaffold `skills/code/semantic-code-search/SKILL.md` using `command-skill-token-efficiency`'s frontmatter/structure as the template.
- [ ] **Step 2:** Define trigger conditions — requests like "find where X is defined across the R packages," "search the MediationVerse codebase for Y," or similar cross-package/fuzzy lookups. Avoid triggering on requests better served by exact-match `Grep` (a literal string, a known symbol name).
- [ ] **Step 3:** Implement the MCP-availability fallback: call claude-context's tools (e.g. `search_code`) when its MCP server is connected; silently fall back to `Grep`/`Glob` if not connected. No hard dependency — the skill must not error or block when claude-context isn't configured on a given machine.
- [ ] **Step 4:** Pilot against one MediationVerse package — use `medfit` (P0, CRAN-bound, most real usage history to search against; path `~/projects/r-packages/active/medfit`, per the user's global project map — read `medfit/CLAUDE.md` first for upstream context, per standing convention).
- [ ] **Step 5:** Run 3-5 representative fuzzy queries against `medfit` both with and without the skill active; measure token cost via `scripts/token-probe.py` (Task 2) rather than a qualitative "feels faster" judgment.
- [ ] **Step 6:** Write up the pilot result (adopt / expand to other packages / abandon) as a short addendum to this proposal or a new `docs/specs/SPEC-claude-context-pilot-<date>.md`, following the SPEC-naming convention already in use.

**Done when:** The skill exists, has a fallback path, and the pilot produces a measured (not estimated) before/after token comparison on `medfit`.

---

## Task 4: Resolve `executing-plans` vs `subagent-driven-development` usage

**Effort: ~10 min. No sub-skill required — do directly, any time, doesn't block Tasks 1-3.**

**Steps:**

- [ ] Search git history and `.superpowers/` state for evidence of which of the two documented options (`subagent-driven-development` vs `executing-plans`) has actually been invoked across past releases — e.g. `git log --all --grep="executing-plans"` and inspect `.superpowers/` subdirectories beyond `sdd/` for an `executing-plans`-specific state path.
- [ ] If `executing-plans` shows zero real usage, simplify the required-sub-skill line in the `docs/plans/*.md` template (and any generator that stamps it) to name only `subagent-driven-development`, dropping the redundant "or executing-plans" alternative.
- [ ] If `executing-plans` has real usage, leave the template as-is and note the split in this file's Context section for future reference.

**Done when:** The plan-template's required-sub-skill line either stays as documented or is simplified, with the decision backed by actual git/state evidence — not left as an open question.

---

## Recommended execution order

**Task 1 → Task 2 → Task 3 → Task 4**

Task 1 is cheap and closes a factual gap in an already-delivered external document — do it first regardless of what else happens this session. Task 2 must precede Task 3 if you want the pilot to produce a real measurement rather than a subjective impression. Task 4 is independent and can slot in anywhere, including a different session entirely.
