---
name: brainstorm
description: This skill should be used when the user asks to "brainstorm", "explore ideas", "design a feature", "draft a spec", "capture a spec", or mentions ideation, requirements gathering, spec capture, or brainstorming depth/focus modes. Generates BRAINSTORM/SPEC documents from project + conversation context. Replaces the deprecated /craft:workflow:brainstorm command. For session-facet friction or pattern analysis across past sessions, use the brainstorm-insights skill instead.
---

# Brainstorm

ADHD-friendly ideation with two decision points (not four) and one escape
hatch (not a "switch depth" tree). Transforms a topic + project/git context
into a `BRAINSTORM-<topic>-<date>.md` or, with the save action, a
`docs/specs/SPEC-<topic>-<date>.md`.

## Boundary With Adjacent Skills

| Skill | Role |
|-------|------|
| **brainstorm** (this) | Generates BRAINSTORM/SPEC documents from topic + context |
| `brainstorm-insights` | Aggregates session facet history into a friction/goals report — unrelated input, unrelated output, split out into its own concern (kept the directory name for path stability; only the Insights operation remains there) |
| `insights-apply` | Consumes a brainstorm-insights report; writes suggestions into CLAUDE.md |
| `adhd-workflow` | Session boundary ops (done, recap, next, focus, stuck, spec-review) |
| `project-planner` | Project-scope planning after a SPEC exists |
| `plan-orchestrator` / `--orch` flag | Multi-agent implementation planning — see "Going deeper" below |

Typical chain: `brainstorm` → SPEC → `project-planner` (breakdown) → `adhd-workflow` (spec-review/done).

## Inputs

- **Topic** — explicit argument, or inferred from conversation / `.STATUS` / git branch / recent commits.
- **Depth** (quick | default | deep) — controls question count. No "max" tier — see "Going deeper" below for why.
- **Focus** (feat | arch | ux | api | ui | ops) — shapes output sections.
- **Action** (optional `save`) — capture as `SPEC-<topic>-<date>.md`.

## Depth Budgets

| Depth | Time | Expert Questions |
|-------|------|-------------------|
| quick | < 1 min | 0 |
| default | < 5 min | 2 |
| deep | < 10 min | 6 |

Two decision points total per session: **(1) depth+focus**, asked together in
one `AskUserQuestion` call when not provided as arguments; **(2) one optional
follow-up** — "anything else before I generate this?" — offered once, after
the expert questions, regardless of depth. No per-depth escape-hatch menus,
no "switch depth mid-flow," no milestone re-prompting every N questions.
If the user wants more, they ask; don't build a state machine for it.

## Flow

1. **Parse args / detect topic.** If no topic, scan conversation, `.STATUS`,
   git branch, recent commits. 1 topic → use it; 2+ → one `AskUserQuestion`;
   none → ask free-form.
2. **Pick depth + focus** (if not provided as arguments) — single
   `AskUserQuestion` call combining both, not two sequential menus.
3. **Context scan.** Check for an existing SPEC or prior brainstorm on the
   topic, project type, `.STATUS` version, recent test failures. Pre-fill
   answers where project state already answers a question.
4. **Expert questions.** Per-depth count (0/2/6), from the question bank
   ([full text and selection logic](../../../docs/specs/_archive/SPEC-brainstorm-question-bank.md)).
   8 categories × 2 questions = 16 base questions, plus 6 project-type
   extensions (auto-detected via `utils/claude_md_detector.py`). Use
   `AskUserQuestion`.
5. **One follow-up offer.** After the questions: "Anything else to add, or
   ready to generate?" — single yes/no-shaped prompt, not a menu of depth
   switches.
6. **Generate output.** Focus-specific sections (user stories for `feat`,
   Mermaid diagram for `arch`, API endpoints for `api`, etc.). Save to
   `BRAINSTORM-<topic>-<date>.md`.
7. **Spec capture** (action=save, or prompted for feat/arch/api). Ask
   user-story + acceptance criteria, render full SPEC template, write to
   `docs/specs/SPEC-<topic>-<date>.md`.
8. **Going-deeper offer** (optional, post-spec only) — see below.

## Going Deeper: No In-Skill Agent Delegation

This skill does **not** spawn subagents itself. The pre-redesign version had
a "max" depth that launched 1-2 background agents directly from inside
brainstorm — duplicating what `orchestrator-v2` already does (wave
checkpoints, file-based results, explicit model routing, `AskUserQuestion`
confirmation before spawning), but without those safeguards. It also
referenced agent type names that didn't exist (`backend-architect`,
`product-strategist`, etc.), which silently fell back to `general-purpose`
with no model pin — see `agents/orchestrator-v2.md` BEHAVIOR 2.

Instead: after a spec is captured (Step 7), offer to hand off to the
orchestrator via the existing `--orch` flag / `plan-orchestrator` skill /
`/craft:orchestrate:plan <spec-path>`. One delegation mechanism, already
hardened, instead of two.

## Mandatory Interactive Steps

Even when all arguments are provided as flags, the per-depth expert-question
count (0/2/6) is never skipped. Skipping silently is a known regression
pattern. The depth/focus *menu* may be skipped when args supply them — the
questions themselves may not.

## Removed: Per-Invocation Question-Count Override

The pre-redesign version supported colon notation (`d:5`, `m:12`, `q:0`) to override the
per-depth expert-question count on a single invocation. This is intentionally not carried
forward — the fixed per-depth counts (0/2/6) are part of the same two-decision-point
simplification described above ("Going Deeper"); a per-call override reintroduces the kind of
escape-hatch menu this redesign removed. If a specific topic genuinely needs more than 6
expert questions, run `/brainstorm` at `deep`, then use the "anything else before I generate
this?" follow-up offer (Flow step 5) to add more — don't request a count override.

## Outputs

- `BRAINSTORM-<topic>-<date>.md` (always — even when also saving a spec).
- `docs/specs/SPEC-<topic>-<date>.md` (when `save` action selected).
- Terminal summary with paths and suggested next command.

## Test-Plan Scaffolding (default-on)

When this skill emits a BRAINSTORM or SPEC artifact, it also emits a
test-plan scaffold by default. Pass `--no-tests` to suppress the section.

### Tier-inference rule

Infer tiers from the shape of the artifact/change being scoped:

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
- Scaffold templates live in
  [`../brainstorm-insights/references/scaffold-templates.md`](../brainstorm-insights/references/scaffold-templates.md)
  (shared with `orchestrate`) — point to that file, do not duplicate templates inline.

### `--yes` non-suppression

`--yes` auto-accepts prompts only; the test-plan and Documentation sections
are **content** and are still emitted under `--yes`. Only `--no-tests` /
`--no-docs` remove them.

## Documentation Scaffolding (default-on)

When this skill emits a BRAINSTORM or SPEC artifact, it also emits a
Documentation section by default. Pass `--no-docs` to suppress the section.

### Which docs to emit

Derive which documentation artifacts are needed by running the existing
doc-scorer rubric from `commands/docs/sync.md` (threshold ≥3). Do **not**
invent a new rubric — reuse the scorer as the single source of truth. For
each doc type the scorer evaluates (guide, refcard, demo, mermaid),
pre-check (`[x]`) boxes that meet the threshold, mark the rest
`N/A — score <N>`.

### Count-cascade exclusion

Auto-docs emission touches **only semantic docs** — CHANGELOG `[Unreleased]`
mirror, guide/refcard/tutorial prose. It **never** touches version or count
lines; those are excluded and stay in `bump-version.sh`.

## Related Skills

- `brainstorm-insights` — friction/goals reporting from session history (was bundled with this skill; now separate, directory name kept for path stability).
- `project-planner` — breakdown after a SPEC exists.
- `plan-orchestrator` / `--orch` — multi-agent implementation, post-spec.
