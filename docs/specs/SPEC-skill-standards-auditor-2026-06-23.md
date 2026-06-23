# SPEC: Skill Standards Auditor (`/craft:code:skill-standards`)

**Status:** APPROVED (future sprint — not yet implemented)
**Date:** 2026-06-23
**Origin:** follow-on from the `/done` consolidation ([ADR-002](../adr/ADR-002-done-command-skill-consolidation.md)) + a skill audit against Anthropic's latest standards

---

## Context

The `adhd-workflow` skill was audited against Anthropic's current SKILL.md standards (`code.claude.com/docs/en/skills.md`) via `plugin-dev:skill-reviewer`, and two findings were fixed (over-stuffed description; command-body framing in `references/done.md`). That audit was **manual and one-skill-at-a-time**. craft has **39 skills**, and nothing scans them as a set for authoring-standards drift.

Investigation confirmed the gap and the surrounding tools:

- **`skill-creator`** (official Anthropic plugin, installed) **creates + optimizes + evals** skills one at a time — bundles the authoritative "Skill Writing Guide" + `quick_validate.py` + `run_loop.py` (description-triggering optimizer). Per-skill optimization, **not** batch compliance scanning.
- **`anthropic-agent-skills` marketplace** (17 skills) has **no** skill-linting / compliance skill. Confirmed gap.
- **`plugin-dev:skill-reviewer`** = qualitative per-skill auditor.
- **craft `governance/`** enforces skill **location/canon/privacy** (R01–R08) — **not** authoring **quality**. This feature is adjacent and new.

**Goal:** a craft command that keeps a vendored copy of Anthropic's SKILL.md standards current, scans all craft skills against it, reports gaps, and applies only *safe* mechanical fixes — delegating deep work to the existing `skill-creator` and `plugin-dev:skill-reviewer`.

**Decisions locked** (AskUserQuestion, 2026-06-23): (1) standalone command mirroring `command-audit.sh`; (2) report-only default, `--fix` opt-in; (3) vendored standards doc, manual refresh (no scan-time network dependency).

---

## Files to create / modify

| File | Action | Notes |
|------|--------|-------|
| `commands/code/skill-standards.md` | NEW | command; house style of `commands/code/command-audit.md` |
| `docs/reference/SKILL-STANDARDS.md` | NEW | vendored checklist (provenance header: source URLs + sync date) |
| `scripts/skill_standards_audit.py` | NEW | scanner — **new `.py` ⇒ `feature/skill-standards` worktree** |
| `tests/test_skill_standards.py` | NEW | structural + scanner-unit — **new `.py` ⇒ worktree** |
| `docs/tutorials/TUTORIAL-skill-standards.md` | NEW | tutorial |
| `ROADMAP.md` | DONE | Ideas-Backlog entry added 2026-06-23 |
| `CHANGELOG.md` / `mkdocs.yml` / `docs/REFCARD.md` | MODIFY | standard doc surfaces at build time |

**Branch note:** the two `.py` files are new code files ⇒ build in a `feature/skill-standards` worktree (branch-guard blocks new code on `dev`).

## Standards checklist (`docs/reference/SKILL-STANDARDS.md`)

The rules the scanner enforces, synthesized from `skill-creator`'s guide + `code.claude.com/docs/en/skills.md`:

- **Frontmatter:** `name` present + kebab-case; `description` present, third-person, names concrete trigger intents, combined with optional `when_to_use` ≤ **1536 chars**; no unrecognized keys.
- **Size / progressive disclosure:** `SKILL.md` ≤ **~500 lines**; heavy detail in `references/`; any reference file > **300 lines** must carry a TOC / "when to read" guidance.
- **Reference hygiene:** no rot-prone version tags (`(NEW in vX.Y.Z)`, `(Phase N)`) in headers; no second-person command framing in reference bodies.
- **Advisory:** flag opportunities to adopt newer optional keys (`when_to_use`, `allowed-tools`, `paths`) — never required.

Refresh mechanism (the "keep standards current" half): `--refresh-standards` re-synthesizes the doc from the installed `skill-creator` guide + a maintainer-supplied docs snapshot, stamping a new provenance date. Manual, deterministic.

## Scanner (`scripts/skill_standards_audit.py`)

Mirror `command-audit.sh`: scan `skills/**/SKILL.md` (+ `references/*.md`) → per-file checks → accumulate by category → score (`100 − errors*5 − warnings*2`) → exit `0`/`1`/`2`. Output: terminal (boxed), `--json`, `--markdown`. Reuse the hand-rolled frontmatter parser in `commands/_discovery.py` (no new YAML dependency).

## `--fix` safe-fix scope (opt-in)

Mechanical, reversible only: strip version tags from headers, normalize frontmatter field order/casing, insert TOC stubs into oversized references. **Never** rewrite a `description` or restructure prose — instead hand off:

- description triggering → `skill-creator`'s `run_loop.py`
- qualitative depth review → `plugin-dev:skill-reviewer`

---

## Verification

1. Run the scanner against craft's 39 skills. `adhd-workflow` + `references/done.md` should **pass** (fixed in [ADR-002](../adr/ADR-002-done-command-skill-consolidation.md)); legacy skills will surface real gaps — triage.
2. `--fix` on a copy → only safe edits applied; descriptions untouched; re-run clears those categories.
3. `--json` parses; exit codes correct.
4. `pytest tests/test_skill_standards.py` green; `validate-counts.sh` reflects +1 command; `docs-staleness-check.sh` GREEN.
5. Dogfood the >300-line reference rule on `references/done.md` → decide whether to extract its 3 worked examples into `references/done-examples.md` (the one optional `/done` follow-up refactor, intentionally gated on this scanner).

## Documentation & Discoverability

- [ ] Tutorial `docs/tutorials/TUTORIAL-skill-standards.md`
- [ ] Reference `docs/reference/SKILL-STANDARDS.md` + REFCARD entry
- [ ] Command auto-surfaces in `/craft:hub` via frontmatter
- [ ] `mkdocs.yml` nav (tutorial + reference)
- [ ] CHANGELOG `[Unreleased]` + `validate-counts.sh` (+1 command) + `docs-staleness-check.sh` clean

## Out of scope / deferred

- Auto-rewriting descriptions (delegate to `skill-creator`).
- Live network fetch of standards at scan time (chosen: vendored doc).
- Merging into `governance/` now (start standalone; revisit as a "quality" rule-class).
- Cross-repo skill scanning (rforge/scholar/etc.) — craft-only first.
