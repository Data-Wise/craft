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
8. Branch on `output`:
   - `orchestrate-worktree` (default) or `orchestrate-only` → instruct the user to `cd` into the
     worktree and start a new session — do NOT begin implementation (STOP-new-session mode).
   - `orchestrate-dispatch` → skip the STOP instruction; instead run the confirm-before-dispatch
     gate (below), then dispatch a background `Agent` call from this same live session. See
     "`orchestrate-dispatch` mode" below for the full flow.

**Key constraint:** ORCHESTRATE file lives in the **worktree root**, never the main repo.

### `orchestrate-dispatch` mode

A third `output` value. Same self-containment guarantee as STOP-new-session mode, but execution
happens via a background `Agent` call dispatched from the live planning session instead of a
fresh human session opening a new terminal. Use this when the token/attention cost of a
cold-started human session outweighs the extra safety mechanisms below (see "When to use which"
in the pipeline-orchestrate guide).

**GRILL-file precondition (warn-only, not a hard block):** if no `GRILL-*.md` exists for the
spec's topic, print an advisory warning and proceed anyway — grilling resolves judgment calls
before dispatch, but a well-scoped, low-ambiguity spec doesn't strictly require it. The backstop
below (ungrilled-ambiguity handling) covers the case where it turns out an unresolved judgment
call was needed after all.

**Confirm-before-dispatch gate:** after the ORCHESTRATE file and worktree are generated
(steps 5-7), before calling `Agent`, run an `AskUserQuestion` gate — not a suppressible prompt.
Show the generated ORCHESTRATE summary (Phase Overview table) and the worktree path. Options:

- **dispatch-now** — call `Agent` immediately with the self-containment prompt (below).
- **review-first** — pause; let the user inspect/edit the ORCHESTRATE file before dispatching.
- **cancel** — stop; ORCHESTRATE file and worktree remain, no dispatch.

This gate fires unconditionally. `--yes` auto-accepts other prompts in this skill but does **not**
suppress this one — it is a design requirement, not a prompt-refiner echo, because dispatch hands
off execution to an unsupervised agent and deserves an explicit human checkpoint every time.

**Self-containment prompt shape:** the dispatched `Agent`'s entire prompt is exactly:

> "Read `ORCHESTRATE-<topic>.md` in full, then execute it."

No other context is passed — no summary, no paraphrase, no conversation history. This is the same
durable artifact a fresh human session would read under STOP-new-session mode; self-containment
becomes structural (inherited from the ORCHESTRATE file's own required completeness) rather than
a discipline checklist.

**Ungrilled-ambiguity backstop:** if the dispatched agent hits genuine unresolved ambiguity
(whether or not a GRILL file existed), it must leave that phase's checkbox unchecked, add a
one-line blocker note directly in the ORCHESTRATE file, and stop — never guess.

**Concurrency cap (scoped to `orchestrate-dispatch` only):** soft cap of 2 concurrent
`orchestrate-dispatch` dispatches per session. A 3rd+ concurrent dispatch requires an explicit
`AskUserQuestion` confirmation before calling `Agent`. **Scoping rule (the part most likely to be
silently gotten wrong):** the counter tracks ONLY background `Agent` calls made via this
`orchestrate-dispatch` flow — it does NOT count unrelated background `Agent` calls the session may
also have running for other purposes (research agents, doc agents, etc.). Maintain the count as an
explicit running tally of dispatches labeled `orchestrate-dispatch` (e.g. tag each dispatch's
`description` so it's identifiable), not a raw count of "all currently-running background agents."
This is not a hard block — a deliberate larger fan-out is still possible, just confirmed.

**Failure/hang detection:** never trust the `Agent` tool's completion notification alone — cross-
check it against the dispatched ORCHESTRATE file's own checkboxes and Phase Overview status
column.

- Notification fires, but re-reading the ORCHESTRATE file shows no checkboxes moved since dispatch
  → flag as a suspected silent failure. Do not offer merge. Surface this to the user explicitly.
- No completion notification within the hang-detection window (below) → surface the crash/hang
  case explicitly. Do not wait silently past the window.

**Hang-detection window formula:** `2 × the dispatched ORCHESTRATE file's own stated phase-effort
estimate` — not a fixed wall-clock constant. The effort estimate comes from the Phase Overview
table's `Effort` column, which Mode 1's existing template already requires for every phase. Example:
a phase overview row stating `Effort: Med` for the currently-dispatched phase sets the flag-as-hung
threshold at 2× whatever wall-clock duration this session maps `Med` effort to for this project —
reuse the same effort→duration mapping the session already uses elsewhere, don't invent a new one
here.

**Confirmed-failure disposition:** on a confirmed silent-failure or hang (per the detection rule
above), never auto-delete the worktree or branch — leave both in place for inspection. Add a
`.STATUS` note in the same HELD style already used for prior held work in this repo (factual: what
was dispatched, what was observed, that it's paused pending manual inspection — not narrative
guesswork about the cause).

**Resumability:** re-dispatching against the SAME ORCHESTRATE file must be idempotent. Before
dispatch, read the file's Phase Overview status column and per-phase checkboxes (the same
tracking this mode already requires agents to maintain). If any phases are already checked, the
new dispatch's self-containment prompt still stays exactly "read `ORCHESTRATE-<topic>.md` in full,
then execute it" — resumption is driven by the file's own content (an agent reading a file with
Phase 1 fully checked off naturally continues from the first unchecked phase), not by a modified
or parameterized prompt. Never restart from Phase 1 on a resume; never invent a second tracking
mechanism alongside the checkboxes.

**`.STATUS` auto-write scoping:** at dispatch time, auto-write only the factual fields to the
Active Worktrees entry — branch name, worktree path, and PR link once one is opened. All of that
data already exists at dispatch time; no new logic is needed to produce it. The narrative/purpose
prose column stays manual — do not attempt to auto-generate it (auto-generated prose reads worse
than hand-written, per this skill's own `.STATUS` history).

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
- Scaffold templates live in [`../../workflow/brainstorm-insights/references/scaffold-templates.md`](../../workflow/brainstorm-insights/references/scaffold-templates.md); point to that file — do not duplicate templates inline.

### `--yes` non-suppression

`--yes` auto-accepts prompts only; the test-plan and Documentation sections are CONTENT and are still emitted under `--yes`. Only `--no-tests`/`--no-docs` remove them.

### Opt-out

`--no-tests` suppresses the entire test-plan section. Default is **on**.

## Documentation scaffolding (default-on)

When this skill emits an ORCHESTRATE artifact, it also emits a Documentation section **by default**. Pass `--no-docs` to suppress the section.

### Which docs to emit

Derive which documentation artifacts are needed by running the existing doc-scorer rubric from `commands/docs/sync.md` (tiered thresholds — see that file for the current type list, per-type weights, and threshold rule). Do **not** invent a new rubric, and do **not** hardcode a parallel type list here — always defer to `commands/docs/sync.md` as the single source of truth for which types exist and what their thresholds are.

For each doc type the scorer evaluates, pre-check (`[x]`) boxes that meet that type's threshold, and mark the rest `N/A — score <N>`. The template for the Documentation section — including the Site Consistency checklist — lives in [`../../workflow/brainstorm-insights/references/scaffold-templates.md`](../../workflow/brainstorm-insights/references/scaffold-templates.md).

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
