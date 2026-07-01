# doc-impact scaffolding — Orchestration Plan

> **Branch:** `feature/doc-impact-scaffolding`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-doc-impact-scaffolding`
> **Spec:** [`docs/specs/SPEC-doc-impact-scaffolding-2026-07-01.md`](../specs/SPEC-doc-impact-scaffolding-2026-07-01.md)
> **Grill (decisions locked):** [`docs/specs/GRILL-doc-impact-scaffolding-2026-07-01.md`](../specs/GRILL-doc-impact-scaffolding-2026-07-01.md) — 3 branches, 2 open questions (both resolved in the SPEC)
> **Version Target:** next minor (no count-cascade expected — rubric/template extension, not a new command/skill/agent)

> **This file is self-contained.** An implementer (a fresh session or a background agent) should
> be able to execute it by reading only this file + the two linked docs above.

---

## How to start

```bash
cd ~/.git-worktrees/craft/feature-doc-impact-scaffolding
# then: "Read docs/plans/ORCHESTRATE-doc-impact-scaffolding-2026-07-01.md and start Phase 1"
```

---

## Objective

Extend the doc-scorer rubric (`commands/docs/sync.md`) to cover Tutorial/API/Cookbook/
Architecture-doc content types with tiered, spawn-cost-aware thresholds, add a Site-Consistency
checklist for structural checks (mkdocs nav/index/site-update), and propagate both to every
spec-producer for free by extending the single shared scorer — no new skill.

## Phase Overview

| Phase | Increment | Priority | Effort | Status |
|-------|-----------|----------|--------|--------|
| 1 | Rubric extension: 4 new types, tiered thresholds, arch-doc double-count fix | High | Med | ☐ not started |
| 2 | Site-Consistency checklist + wiring to existing tooling | Medium | Low | ☐ not started |
| 3 | Documentation & Discoverability | Medium | Low | ☐ not started |

---

## Phase 1 — Rubric extension

**Scope:** add the 4 missing content types to the single-source-of-truth rubric, with tiered
thresholds and the arch-doc double-count fix.

- [ ] 1.1 In `commands/docs/sync.md`, add Tutorial, API, Cookbook, Architecture-doc rows to the
      rubric table (SPEC §3.2).
- [ ] 1.2 Set tiered thresholds: cheap in-context types (Refcard, Mermaid, index/nav tweak) stay
      at `score ≥3`; heavy agent-authored types (Tutorial, API, Cookbook, Architecture-doc) get
      `score ≥5` OR a concrete "new user-facing surface" trigger. Document the trigger definition
      explicitly, not just the number.
- [ ] 1.3 Implement the arch-doc double-count subtraction rule (SPEC §3.3): when computing the
      Architecture-doc type's score, subtract the Mermaid factor's contribution from the shared
      "architecture change" signal before applying the ≥5 threshold. Document this next to the
      rubric table.
- [ ] 1.4 Update the doc-scorer type-list mention in `skills/orchestration/plan-orchestrator/SKILL.md`
      (Documentation scaffolding section) — must reference the scorer, never hardcode a parallel
      type list (single-source guard, SPEC §3.6).

**Key files:**

- `commands/docs/sync.md` (update — rubric table + threshold + subtraction-rule documentation)
- `skills/orchestration/plan-orchestrator/SKILL.md` (update — type-list mention only, no duplication)

**Acceptance:** rubric covers 8 types total (4 existing + 4 new) with tiered thresholds
documented; arch-doc subtraction rule is explicit, not implicit; no parallel type list introduced.

---

## Phase 2 — Site-Consistency checklist

**Scope:** a boolean, advisory checklist wired to existing tooling — not a new drift-detection
implementation, not mixed into the numeric score.

- [ ] 2.1 Add a `## Site Consistency` block to `references/scaffold-templates.md` with 3
      checkboxes (SPEC §3.5): mkdocs nav updated?, index file updated?, `/craft:site:update` /
      `docs-staleness-check.sh` run? Each checkbox references the real command/script by name.
- [ ] 2.2 Confirm this block is **advisory, not a per-spec hard gate** (SPEC §3.5) — the release
      pipeline already hard-gates `docs-staleness-check.sh --non-interactive` at Step 3b; do not
      add a second hard gate here.

**Key files:**

- `references/scaffold-templates.md` (update — new Site Consistency block)

**Acceptance:** block present with exactly 3 checkboxes, each naming the real tool it invokes;
confirmed advisory (no new hard-block logic added anywhere).

---

## Phase 3 — Documentation & Discoverability (REQUIRED — final phase)

- [ ] 3.1 REFCARD entry for the expanded doc-impact section (`docs/REFCARD.md` or a dedicated
      `docs/reference/REFCARD-DOC-IMPACT.md` if the section is large enough per existing convention).
- [ ] 3.2 Help hub / discovery — verify no new command exists, so `/craft:hub` needs no new entry;
      mark N/A explicitly.
- [ ] 3.3 Website — run `mkdocs build --strict` to confirm no new nav gap from the REFCARD change.
- [ ] 3.4 Catalog — `docs/skills-agents.md`: no new skill/command row expected; confirm.
- [ ] 3.5 CHANGELOG `[Unreleased]` entry describing the rubric extension + Site-Consistency block.
- [ ] 3.6 `./scripts/validate-counts.sh` clean (expect **no count changes**).
- [ ] 3.7 `./scripts/docs-staleness-check.sh` clean.

---

## Test Plan (from SPEC §6 — emit as red-first stubs; tier-inferred: prose/rubric-table change → e2e + dogfood)

### e2e

- [ ] An ORCHESTRATE emitted for an architecture change pre-checks Architecture-doc + Mermaid
      correctly (not double-counted per Phase 1's subtraction rule). `# TODO(author): delete if not contract-bearing`
- [ ] The Site-Consistency block is present with exactly 3 unchecked boxes on a fresh ORCHESTRATE
      emission. `# TODO(author): delete if not contract-bearing`
- [ ] **Audit-path e2e (closes the original gap):** inject a deliberate mkdocs-nav drift into a
      fixture site (a page not in `mkdocs.yml` nav), run `docs-staleness-check.sh`, and assert the
      Site-Consistency mechanism's underlying tooling actually surfaces that drift — not just that
      the checkbox exists in the template. `# TODO(author): delete if not contract-bearing`

### dogfood

- [ ] Single-source guard: grep `references/scaffold-templates.md` and
      `skills/orchestration/plan-orchestrator/SKILL.md` for a hardcoded type list matching the
      rubric's type names; fail if found outside a cross-reference to `commands/docs/sync.md`.
      `# TODO(author): delete if not contract-bearing`
- [ ] The Documentation section references existing agents by name (`api-documenter`,
      `tutorial-engineer`, `docs-architect`, `reference-builder`, `mermaid-expert`) — assert no new
      `skills/docs-*` directory exists. `# TODO(author): delete if not contract-bearing`

Unselected tiers (unit, integration, dependency, count-cascade): **N/A** — prose/rubric-table
extension in existing files, no new parser, script, cross-command data flow, external dependency,
or new command/skill/agent.

---

## Friction Prevention

- **Context first**: read this ORCHESTRATE file and the SPEC + GRILL before starting work.
- **Verify location**: confirm CWD is the worktree, not the main repo.
- **No autonomous starts**: STOP and confirm before proceeding to the next phase.
- **Test per phase**: run the Verification section's commands after each phase.
- **Single-source discipline is the main risk here** — every phase's acceptance criterion includes
  a "no parallel copy created" check. This class of bug (duplicate rubric/template drift) is
  exactly what the grill's Open Question #2 flagged; don't let it slip through unverified.

## Acceptance Criteria

- [ ] Rubric extended with 4 new types + tiered thresholds + arch-doc subtraction rule, documented
      in `commands/docs/sync.md`.
- [ ] Site-Consistency checklist added to `references/scaffold-templates.md`, advisory not
      hard-gated.
- [ ] No new skill/command/agent created.
- [ ] Single-source guard dogfood test passes (no parallel type list anywhere).
- [ ] Audit-path e2e test passes (real injected drift is actually caught, not just checkbox
      presence).
- [ ] Documentation & Discoverability phase complete.

## Commit Strategy

Conventional commits, one per phase:

- `feat(docs-scorer): extend rubric with tutorial/api/cookbook/arch-doc types (Phase 1)`
- `feat(docs-scorer): add Site Consistency checklist to scaffold template (Phase 2)`
- `docs(doc-impact-scaffolding): documentation + discoverability sweep (Phase 3)`

Then `gh pr create --base dev`. Commit as you go.

**Review gate:** under this session's standing authorization (see main repo `.STATUS`), the
dispatching session pushes/opens the PR/merges directly once CI is green (or confirmed-benign per
the documented `Validate Plugin Structure` pattern) and the checkboxes + Verification section have
been re-run and confirmed. Post-merge, run the applicable check (`validate-counts.sh` /
`docs-staleness-check.sh`).

## Verification

```bash
/opt/homebrew/bin/python3.13 -m pytest tests/ -q
# Baseline at time of writing: 2072 passed / 7 failed / 13 errors (documented, pre-existing —
# NOT regressions; compare against this exact count, not zero)

./scripts/validate-counts.sh          # expect: no count changes
./scripts/docs-staleness-check.sh     # expect: green
mkdocs build --strict                 # expect: 0 warnings
```

## Session Instructions

### Context

You are in the **craft repo worktree** for the `doc-impact-scaffolding` feature. This is a
rubric/template extension to existing files (`commands/docs/sync.md`,
`references/scaffold-templates.md`, `skills/orchestration/plan-orchestrator/SKILL.md`) — no new
command, skill, or agent file. The SPEC has full design details; the GRILL has the resolved
decision ledger.

### How to Start

```bash
cd ~/.git-worktrees/craft/feature-doc-impact-scaffolding
claude
```

On session start, paste:

> Read `docs/plans/ORCHESTRATE-doc-impact-scaffolding-2026-07-01.md` and the linked SPEC + GRILL.
> Start Phase 1.

### Phase-by-Phase

1. Read current state of each file listed in the phase.
2. Implement changes per the SPEC's design (cross-referenced to grill branch numbers).
3. Run verification after each phase.
4. Commit in logical groups.
5. STOP and confirm before next phase.

## .STATUS + tracking

- Add an Active Worktrees row for `feature/doc-impact-scaffolding` when the worktree is created
  (factual fields only — branch, path, purpose one-liner).
- Update each Phase Overview status cell (☐ → ⏳ → ✅) as phases complete.
