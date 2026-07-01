---
name: plan-orchestrator
description: This skill should be used when the user asks to "generate an ORCHESTRATE file", "turn a spec into a plan", "scaffold a feature breakdown", "scaffold a sprint backlog", "generate roadmap artifacts", "create an implementation plan from SPEC", or needs to produce concrete planning artifacts (ORCHESTRATE-*.md, feature breakdowns with task estimates, sprint backlogs, milestone roadmaps). Differs from `project-planner` (high-level strategy/advice) by producing committed, actionable artifacts tied to specs and worktrees.
category: orchestration
---

# Plan Orchestrator Skill

Produces **concrete planning artifacts** from specs and feature requests. Where `project-planner` advises on strategy ("how should we estimate?"), this skill emits files and structured backlogs ready to drive implementation: `ORCHESTRATE-<topic>.md`, feature task trees, sprint commitments, and visual roadmaps.

## When to Use

Activate when the user wants a **deliverable** (file, backlog, milestone list), not just guidance:

- "Generate ORCHESTRATE from `docs/specs/SPEC-auth-*.md`"
- "Break this feature into tasks with estimates"
- "Plan next sprint, 80 hours capacity"
- "Generate a 6-month roadmap as mermaid"
- "Turn this brainstorm into a planning doc"

Do **not** use for: routing a single task to a command (use `task-analyzer`), saving session state (use `session-state`), or general "how do I plan?" advice (use `project-planner`).

## Differentiation Map

| Need | Skill |
|------|-------|
| "What command should I run for X?" | `task-analyzer` |
| "Save / resume my orchestrator session" | `session-state` |
| "Coach me on estimation / agile practices" | `project-planner` |
| "**Generate the actual plan file**" | **`plan-orchestrator`** (this) |

## Four Planning Modes

This skill consolidates four commands. The user's phrasing selects the mode:

### 1. Spec → ORCHESTRATE (`orchestrate:plan`)

**Trigger:** spec file mentioned, or "implementation plan from SPEC".

**Flow:**

1. Discover specs in `docs/specs/SPEC-*.md` (and `BRAINSTORM-*.md` lacking specs).
2. Parse selected spec: title, phases/increments, acceptance criteria, key files, cross-repo references.
3. Detect cross-repo work (paths under `~/projects/<other>/`); enforce same branch name across repos.
4. Confirm plan with user (ORCHESTRATE+worktree / ORCHESTRATE-only / modify / cancel).
5. Generate `ORCHESTRATE-<topic>.md` with sections: Objective, Phase Overview, Phase 1..N, Friction Prevention, Acceptance Criteria, Commit Strategy, Verification, Session Instructions.
6. Create worktree at `~/.git-worktrees/<project>/feature-<topic>` from `dev` if selected.
7. Update `.STATUS` and `.gitignore`.

**Key constraint:** ORCHESTRATE file lives in the **worktree root**, never the main repo. After generation, instruct the user to `cd` into the worktree and start a new session — do NOT begin implementation.

### 2. Feature Plan (`plan:feature`)

**Trigger:** "plan feature", "break down", "scope this feature".

**Output:** user stories → task tree grouped by layer (backend/frontend/infra) → time estimates → dependencies → risks → acceptance criteria → total estimate.

**Options:** `--scope mvp|full|enterprise`, `--format markdown|jira|github`, `--include-tests`, `--output <file>`.

### 3. Sprint Plan (`plan:sprint`)

**Trigger:** "plan sprint", "next sprint", capacity/duration mentions.

**Flow:** gather backlog → prioritize → fit to capacity → name sprint goal → commit + stretch items → highlight dependencies and risks.

**Options:** `--duration <days>` (default 14), `--capacity <hours>`, `--goal <text>`, `--from github|jira`.

### 4. Roadmap (`plan:roadmap`)

**Trigger:** "roadmap", "quarterly plan", "milestone view".

**Output:** phased milestones with progress bars, dependency callouts, timeline gantt-style strip.

**Options:** `--horizon <months>` (default 6), `--format mermaid|markdown|html`, `--output <file>`, `--update` to refresh existing roadmap.

## ORCHESTRATE Template (Canonical)

```markdown
# <Topic> — Orchestration Plan

> **Branch:** `feature/<topic>`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/<project>/feature-<topic>`
> **Spec:** `<spec-path>`

## Objective
<1-2 sentences from spec>

## Phase Overview
| Phase | Increment | Priority | Effort | Status |

## Phase 1..N: <Name>
**Scope:** ...
- [ ] 1.1 <task>
**Key files:** `<file>` (NEW or update)

## Friction Prevention
- Context first, verify CWD, no autonomous starts, test per phase.

## Acceptance Criteria
- [ ] <from spec>

## Commit Strategy
Conventional commits per phase.

## Verification
<auto-detected test command>

## Session Instructions
cd <worktree-path> && claude
> "Read ORCHESTRATE-<topic>.md and start Phase 1."
```

## Auto-Detection

| Detection | Verification Command |
|-----------|---------------------|
| `tests/test_craft_plugin.py` | `python3 tests/test_craft_plugin.py` |
| `package.json` test script | `npm test` |
| `pytest.ini` / `pyproject.toml` | `pytest` |
| `Cargo.toml` | `cargo test` |
| `DESCRIPTION` (R) | `R CMD check` |

### Rebase Strategy (Spec → ORCHESTRATE mode)

Before finalizing the worktree, check whether the base branch (`dev`) has recent automated
commits:

- If the last 5 commits on `dev` include `chore:` or bot commits → suggest a rebase before PR.
- If the history is clean → standard merge workflow, no rebase suggestion needed.

## Cross-Repo Detection

Scan spec for paths under `~/projects/dev-tools/<other>/`. If detected:

- Primary repo + secondary repo(s) listed.
- Same branch name (`feature/<topic>`) enforced across all worktrees.
- Generate paired worktrees on confirmation.

## ADHD-Friendly Outputs

- Visual hierarchy: headers, tables, progress bars, checkboxes.
- Quick-wins vs long-term clearly labeled.
- Numbered next steps at end of every artifact.
- Total estimate always surfaced (no "TBD" without a placeholder).

## Integration

| With | How |
|------|-----|
| `task-analyzer` | Receives a routed task that needs a plan artifact. |
| `session-state` | Plans persist into orchestrator session state. |
| `project-planner` | Strategic advice upstream; this skill writes the file. |
| `/craft:git:worktree` | Creates the worktree for ORCHESTRATE mode. |
| `/craft:orchestrate` | Launches orchestrator after plan exists. |
| `/craft:docs:sync` | Refreshes roadmap docs on `--update`. |

## Test-plan scaffolding (default-on)

When this skill emits an ORCHESTRATE artifact, it also emits a test-plan scaffold **by default**. Pass `--no-tests` to suppress the section.

### Tier-inference rule

Infer tiers from the shape of the artifact/change being planned:

| Change shape | Tiers to emit |
|---|---|
| Flag / frontmatter / prose only | `e2e` + `dogfood` |
| + new parser or script | + `unit` |
| + cross-command data flow | + `integration` |
| + external dependency change | + `dependency` |
| + new command / skill / agent | + `count-cascade` dogfood |

Unselected tiers print as `N/A — <reason>` (never empty stubs).

### Emission rules

- Emit test stubs **red-first** (failing placeholder, not passing no-op).
- Each stub carries `# TODO(author): delete if not contract-bearing` until the author confirms the contract.
- Scaffold templates live in `references/scaffold-templates.md`; point to that file — do not duplicate templates inline.

### `--yes` non-suppression

`--yes` auto-accepts prompts only; the test-plan and Documentation sections are CONTENT and are still emitted under `--yes`. Only `--no-tests`/`--no-docs` remove them.

### Opt-out

`--no-tests` suppresses the entire test-plan section. Default is **on**.

## Documentation scaffolding (default-on)

When this skill emits an ORCHESTRATE artifact, it also emits a Documentation section **by default**. Pass `--no-docs` to suppress the section.

### Which docs to emit

Derive which documentation artifacts are needed by running the existing doc-scorer rubric from `commands/docs/sync.md` (threshold ≥3). Do **not** invent a new rubric — reuse the scorer as the single source of truth.

For each doc type the scorer evaluates (guide, refcard, demo, mermaid), pre-check (`[x]`) boxes that meet the threshold, and mark the rest `N/A — score <N>`. The template for the Documentation section lives in `references/scaffold-templates.md`.

### Lifecycle split

| Phase | Action |
|-------|--------|
| **Spec-time** | Read-only emit + pre-derive: render the Documentation section with pre-checked boxes. No file edits. |
| **Impl/post-merge** | Real edits via `/craft:docs:update --post-merge`. Diff-confirm gated before applying. |

### Count-cascade exclusion

Auto-docs emission touches **only semantic docs** — CHANGELOG `[Unreleased]` ×2 mirror, guide/refcard/tutorial prose. It **never** touches version or count lines. Version/count updates stay in `bump-version.sh`.

### Opt-out

`--no-docs` suppresses the entire Documentation section. Default is **on**.

## Common Pitfalls

- **Writing ORCHESTRATE to the main repo** — always worktree root.
- **Auto-starting implementation** after generating ORCHESTRATE — STOP; new session required.
- **Generating spec from brainstorm silently** — offer `/brainstorm s` instead; let user capture spec interactively.
- **Overwriting existing ORCHESTRATE without confirmation** — detect and ask before regenerating.
- **Cross-repo branch name drift** — enforce identical `feature/<topic>` across paired worktrees.

## Example Invocations

```
"Generate ORCHESTRATE from docs/specs/SPEC-auth-2026-02-15.md"
"Break down 'avatar upload' as MVP-scope feature plan"
"Plan a 7-day sprint, 40 hours capacity, goal: ship OAuth"
"Generate quarterly roadmap as mermaid, save to ROADMAP.md"
```
