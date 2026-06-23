# SPEC — `/craft:orchestrate` Clarify Step + Optimization Refactor

> **Repo:** `~/projects/dev-tools/craft` · **Branch:** `dev` · **Date:** 2026-06-22
> **Status:** Design. Implementation requires a worktree (changes command behavior).
> **Source:** review of `commands/orchestrate.md` (842 lines) during the planning-refactor pass.

---

## 0. Objective

Two changes to `/craft:orchestrate`:

1. **Add a default Clarify step** — orchestrate currently *confirms* a plan but never *grills*
   an ambiguous task before building it. Add interactive gap-surfacing (AskUserQuestion) as a
   DEFAULT pre-planning step.
2. **Optimize the file** — split the ~130-line MANDATORY launch contract from ~700 lines of
   reference/mockups; move reference to `commands/orchestrate/docs/`, cutting per-invocation
   token cost.

## 1. The gap (Clarify)

Current flow (`commands/orchestrate.md` §"Execution Behavior"):

```
Step 0  Mode selection            (asks)
Step 1  Task Analysis — build plan (NO validation of assumptions)
        Engine selection
Step 2  Confirm Before Execution  (asks proceed/modify/cancel)
Steps 3-N Execute
```

The plan in Step 1 is built on **unvalidated assumptions**. Step 2's "Modify steps" is a
*reactive* escape after a possibly-wrong plan already exists. There is no default step that
**clarifies an underspecified task before planning** — the gap-surfacing AskUserQuestion pattern
is absent. (`grep` confirms: orchestrate has confirm gates, no clarify gate.)

## 2. Decisions

| # | Decision | Choice |
|---|---|---|
| O1 | Clarify default | **ON by default.** Suppress with `--yes` / `--no-clarify`, or auto-skip when the task is unambiguous or spec/ORCHESTRATE-derived. |
| O2 | Placement | New **Step 0.5: Clarify**, between mode-select (Step 0) and task-analysis (Step 1). Clarify BEFORE the plan exists. |
| O3 | Form | **Invoke `/craft:grill`** as the interrogation impl (one interrogation engine, reused — SPEC-grill-command / G8). For a quick ambiguity gate, grill runs in a short bounded pass (≤2 branches) rather than full deep interrogation; the lighter AskUserQuestion batch remains the fallback when grill is unavailable. |
| O4 | Trigger test | Fire Clarify when the task has multiple valid interpretations, missing scope/constraints, or undefined success criteria. Skip when a matching SPEC/ORCHESTRATE/WORKFLOW file already pins the decisions. |
| O5 | Refactor | Move reference + mockups to `commands/orchestrate/docs/orchestrate-reference.md`; keep the lean contract in `orchestrate.md`. |

## 3. Step 0.5 — Clarify (new)

```
### Step 0.5: Clarify (default ON)

Before building any plan, assess task ambiguity. If the task is underspecified or
admits multiple valid interpretations, invoke /craft:grill in a bounded pass to LOCK
the decisions that change the plan — one question at a time, recommended answer per
question, codebase-first. Then build Step 1 on the locked answers. (Fallback when
grill is unavailable: 1–2 AskUserQuestion rounds, recommended-option-first.)

SKIP this step when:
  - the user passed --yes or --no-clarify, OR
  - a SPEC-*/ORCHESTRATE-*/WORKFLOW-* file matching the task pins the decisions, OR
  - the task is unambiguous (single interpretation, clear scope + success criteria).

Ask only about decisions that CHANGE THE PLAN (scope boundaries, target surface,
sequencing, success criteria). Never ask what you can detect from the repo. Mark one
option (Recommended) first with a one-line reason. Max 2 rounds — then proceed.
```

Add `--no-clarify` (and honor existing `--yes`) to frontmatter arguments.

## 4. Optimization refactor (O5)

| Keep in `orchestrate.md` (lean contract, ~250 ln) | Move to `commands/orchestrate/docs/orchestrate-reference.md` |
|---|---|
| frontmatter, Usage, --refine | status / timeline / context-budget / compression mockups |
| Modes table | session-management commands + history mockup |
| **Steps 0 → 0.5 → 1 → Engine → 2 → 3-N** | worktree types + decision tree |
| Engine selection rules | swarm deep config + swarm dry-run mockup |
| Swarm: one-paragraph summary + pointer | performance tips, token instrumentation |
| See Also → reference doc | control-commands catalog |

Rationale: every invocation currently loads all 842 lines (~12 ASCII mockups). The MANDATORY
behavior is ~130 lines; the rest is reference a human reads occasionally. Splitting serves the
token-efficiency direction (`SPEC-orchestrate-token-efficiency-2026-06-17`). Producer/consumer
discipline: the command is the contract; the reference is the manual.

## 5. Tests (PR gate)

- Clarify fires on an ambiguous task; is skipped under `--yes`, `--no-clarify`, and when a
  matching spec file is present.
- The lean `orchestrate.md` still contains the full Step 0→3-N contract (no behavior dropped in
  the move).
- Reference doc is reachable (link-check) and not double-counted as a command by discovery
  (`_discovery.py` excludes `docs/` — verify).

## 6. Migration & rollback

- Pure craft-repo change → `git revert <impl-commit>` restores.
- The reference doc is new but lives under `commands/orchestrate/docs/` (`.md`, not a command) —
  confirm `validate-counts.sh` does not count it.

## 7. Effort

~2–3 hours: Step 0.5 wording + arg + trigger logic, the content move (mechanical but large),
link/nav updates, tests. Behavior change → **worktree required** (not on `dev`).
