# Orchestrate-Worktree Pipeline — Orchestration Plan

> **Branch:** `feature/orchestrate-pipeline`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-orchestrate-pipeline`
> **Spec:** `docs/specs/SPEC-orchestrate-worktree-pipeline-2026-02-15.md`
> **Version Target:** v2.20.0

## Objective

Four connected improvements: (1) revise docs/guides/refcards to clarify orchestrate, swarm, and ORCHESTRATE files, (2) add interactive pipeline from brainstorm → ORCHESTRATE → worktree, (3) clarify swarm + worktree integration, (4) integrate insights workflow with brainstorm/orchestrate and document the full insights lifecycle.

## Phase Overview

| Phase | Increment | Priority | Effort | Status |
|-------|----------|----------|--------|--------|
| 1 | Doc Revisions | High | 2-3h | |
| 2 | Spec → ORCHESTRATE → Worktree Pipeline | High | 4-6h | |
| 3 | Swarm + Worktree Clarity | Medium | 2-3h | |
| 4 | Insights Workflow Integration | Medium | 3-4h | |

## Phase 1: Doc Revisions

**Scope:** Update existing docs only — no command/skill changes.

**Note:** These are .md file edits. They CAN land on dev directly, but since we have a worktree, we'll develop them here and merge via PR for clean history.

- [ ] 1.1 **REFCARD.md**: Add "Orchestrate + Worktree Pipeline" section with Mermaid diagram
- [ ] 1.2 **REFCARD.md**: Clarify `--swarm` vs manual worktrees with comparison table
- [ ] 1.3 **getting-started.md**: Add "Complex Feature Workflow" section showing the pipeline
- [ ] 1.4 **orchestrate.md (docs/guide/)**: Add "When to Use What" comparison table
- [ ] 1.5 **REFCARD-GIT-WORKTREE.md**: Add "Worktree Types" section (manual vs swarm vs cross-repo)
- [ ] 1.6 **interactive-orchestration.md**: Add practical end-to-end example
- [ ] 1.7 **TUTORIAL-worktree-setup.md**: Add "After Brainstorm" section showing ORCHESTRATE file creation

**Key content to add across all docs:**

Worktree Types Table (use consistently everywhere):

| Type | Created By | Lifetime | Branch Pattern | ORCHESTRATE |
|------|-----------|----------|---------------|-------------|
| **Manual** | `/craft:git:worktree create` | Long-lived | `feature/*` | Optional |
| **Pipeline** | `/craft:orchestrate:plan` or brainstorm | Long-lived | `feature/*` | Always |
| **Swarm** | `/craft:orchestrate --swarm` | Short-lived | `swarm-*` | Reads existing |
| **Cross-Repo** | Pipeline (multi-repo spec) | Long-lived | `feature/*` (same name) | Scoped per-repo |

Pipeline Mermaid (end-to-end):

```
brainstorm → spec → ORCHESTRATE → worktree → implement → PR
```

## Phase 2: Spec → ORCHESTRATE → Worktree Pipeline

**Scope:** New command + brainstorm integration. Touches craft plugin AND workflow plugin.

### 2a: `/craft:orchestrate:plan` standalone command

- [ ] 2.1 Create `commands/orchestrate/plan.md` with frontmatter and execution behavior
- [ ] 2.2 Scan `docs/specs/` for SPEC-*.md files, show list with dates and status
- [ ] 2.3 Also scan for BRAINSTORM-*.md without matching specs, offer to generate spec first
- [ ] 2.4 Accept path argument: `/craft:orchestrate:plan docs/specs/SPEC-auth.md`
- [ ] 2.5 Parse spec for phases/increments (interactive: show parsed phases, let user adjust)
- [ ] 2.6 Generate ORCHESTRATE file with full session instructions (template sections 1-10)
- [ ] 2.7 Detect cross-repo work (paths referencing `~/projects/dev-tools/<other-repo>/`)
- [ ] 2.8 For cross-repo: enforce same branch name, create paired worktrees with bidirectional references
- [ ] 2.9 Auto-detect rebase strategy: check if base branch has recent automated commits
- [ ] 2.10 Auto-update `.STATUS` in main repo with worktree entry
- [ ] 2.11 Add `ORCHESTRATE-*.md` to `.gitignore` in main repo

### 2b: Brainstorm integration (workflow plugin)

- [ ] 2.12 Add Step 6 to brainstorm skill: "Create Orchestration?" prompt after spec capture
- [ ] 2.13 When "ORCHESTRATE + worktree" selected, invoke `/craft:orchestrate:plan` with spec path
- [ ] 2.14 When "ORCHESTRATE only" selected, save to `docs/orchestrate/` directory
- [ ] 2.15 Update brainstorm SKILL.md documentation with new Step 6

**Key files:**

- `commands/orchestrate/plan.md` (NEW)
- `skills/workflow/brainstorm/SKILL.md` (in workflow plugin at `~/.claude/plugins/workflow/`)

## Phase 3: Swarm + Worktree Clarity

**Scope:** Update orchestrate command with worktree types and swarm integration.

- [ ] 3.1 Add "Worktree Types" taxonomy to `commands/orchestrate.md`
- [ ] 3.2 Update swarm mode to read ORCHESTRATE file if present (map agents to phases)
- [ ] 3.3 Add `--swarm` practical example with ORCHESTRATE agent-to-file mapping
- [ ] 3.4 Document when to use swarm vs manual worktrees vs cross-repo worktrees
- [ ] 3.5 Add swarm dry-run example showing worktree creation plan

**Key files:**

- `commands/orchestrate.md`

## Phase 4: Insights Workflow Integration

**Scope:** New command + cross-command integration. Independent of Phases 2-3.

### 4a: `/craft:insights` command

- [ ] 4.1 Create `commands/workflow/insights.md` — generates insights report
- [ ] 4.2 Aggregate session facets: friction patterns, goal categories, outcomes
- [ ] 4.3 Output formatted report (friction summary, top patterns, CLAUDE.md suggestions)
- [ ] 4.4 Support `--format html|terminal|json` and `--since <days>`

### 4b: Insights → ORCHESTRATE integration

- [ ] 4.5 When generating ORCHESTRATE (Phase 2), check insights for project-specific friction
- [ ] 4.6 Auto-add "Friction Prevention" section with context-setting guardrails
- [ ] 4.7 Map friction types → guardrail rules (wrong_approach → CWD verify, etc.)

### 4c: Insights → Brainstorm integration

- [ ] 4.8 When brainstorm starts, check insights for relevant past session patterns
- [ ] 4.9 Show "Previous session insights" summary if related sessions exist
- [ ] 4.10 Factor friction patterns into spec generation

### 4d: Documentation + Cross-command

- [ ] 4.11 Add `/craft:insights` to REFCARD.md workflow commands section
- [ ] 4.12 Add "Insights Lifecycle" section to getting-started.md
- [ ] 4.13 Update insights-improvements-guide.md with new command and integration flow
- [ ] 4.14 Add Mermaid diagram: session → insights → CLAUDE.md + ORCHESTRATE + brainstorm
- [ ] 4.15 Update `/craft:do` routing, `/craft:hub` discovery, `/craft:check --context`

**Key files:**

- `commands/workflow/insights.md` (NEW)
- `skills/insights-apply/SKILL.md` (update)
- `commands/do.md`, `commands/hub.md`, `commands/check.md` (updates)

## Friction Prevention (from insights)

Based on 82 analyzed sessions (21 wrong-approach events):

- **Context first**: Read this ORCHESTRATE file and the spec BEFORE starting work
- **Verify location**: Confirm CWD is the worktree (`~/.git-worktrees/craft/feature-orchestrate-pipeline`), not the main repo
- **No autonomous starts**: After each phase, STOP and confirm before proceeding to next
- **Test per phase**: Run `./scripts/validate-counts.sh` after each phase to catch count drift
- **Doc links**: Run `python3 tests/test_craft_plugin.py -k "broken_links"` after doc changes

## Acceptance Criteria

- [ ] REFCARD explains the full pipeline with Mermaid diagram (end-to-end)
- [ ] "When to use what" is clear: swarm vs manual worktree vs pipeline vs cross-repo
- [ ] After `/brainstorm save`, user is offered ORCHESTRATE + worktree creation
- [ ] `/craft:orchestrate:plan` discovers specs/brainstorms, generates ORCHESTRATE + worktree
- [ ] Cross-repo specs auto-detect, enforce same branch name, create paired worktrees
- [ ] Generated ORCHESTRATE files have full session instructions
- [ ] `/craft:insights` command generates report from facets data
- [ ] ORCHESTRATE files include "Friction Prevention" section from insights
- [ ] Insights lifecycle documented end-to-end
- [ ] All doc links valid, no duplication between REFCARD and guides

## Commit Strategy

- Conventional commits: `docs:`, `feat:`, `refactor:`
- Phase 1 gets grouped doc commits: `docs(refcard): add orchestrate pipeline section`
- Phase 2 gets per-task commits: `feat(orchestrate): add plan command`
- Phase 3: `feat(orchestrate): add worktree types to swarm mode`
- Phase 4: `feat(insights): add /craft:insights command`

## Verification

After each phase:

```bash
# Validate counts haven't drifted
./scripts/validate-counts.sh

# Check doc links
python3 tests/test_craft_plugin.py -k "broken_links"

# Full test suite
python3 tests/test_craft_plugin.py
```

## Session Instructions

### Context

You are in the **craft repo worktree** for the orchestrate-pipeline feature. All 4 phases happen here. The spec has full design details including Mermaid diagrams, AskUserQuestion JSON, and pseudocode.

### How to Start

```bash
cd ~/.git-worktrees/craft/feature-orchestrate-pipeline
claude
```

On session start, paste:

> Read `ORCHESTRATE-orchestrate-pipeline.md` and the spec at `docs/specs/SPEC-orchestrate-worktree-pipeline-2026-02-15.md`. Start Phase 1 — doc revisions across REFCARD, guides, and tutorials.

### Phase 1 Step-by-Step

1. Read current state of each doc file listed in 1.1-1.7
2. Add sections per the spec's design (Worktree Types table, Pipeline Mermaid, comparison tables)
3. Ensure consistency — the Worktree Types table must be identical in all docs that include it
4. Run link checker after each doc: `python3 tests/test_craft_plugin.py -k "broken_links"`
5. Commit per-doc or in logical groups

### Phase 2 Step-by-Step

1. Read existing `commands/orchestrate.md` and `commands/orchestrate/resume.md` for patterns
2. Create `commands/orchestrate/plan.md` following the same frontmatter format
3. Implement spec scanning, phase parsing, ORCHESTRATE generation per spec design
4. For brainstorm integration: read `~/.claude/plugins/workflow/skills/brainstorm/SKILL.md`
5. Add Step 6 after the existing spec capture step
6. Test: run `/craft:orchestrate:plan` on an existing spec to verify output

### Phase 3 Step-by-Step

1. Read `commands/orchestrate.md` swarm section (lines ~460-580)
2. Add Worktree Types taxonomy section
3. Add practical --swarm example with ORCHESTRATE mapping
4. Add when-to-use-what guidance

### Phase 4 Step-by-Step

1. Read `skills/insights-apply/SKILL.md` for current insights workflow
2. Create `commands/workflow/insights.md` following existing workflow command patterns
3. Read sample facets at `~/.claude/usage-data/facets/` to understand data structure
4. Implement aggregation and report formatting
5. Wire up cross-command integration (do.md, hub.md, check.md)
6. Update docs (REFCARD, getting-started, insights guide, tutorial)
