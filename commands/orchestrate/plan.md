---
description: Generate ORCHESTRATE file from spec, with optional worktree creation and cross-repo detection
arguments:
  - name: spec-path
    description: Path to SPEC-*.md file (if omitted, scans docs/specs/ for available specs)
    required: false
  - name: output
    description: "Output mode: orchestrate-worktree (default), orchestrate-only"
    required: false
    default: orchestrate-worktree
---

# /craft:orchestrate:plan — Spec → ORCHESTRATE → Worktree Pipeline

Generate an ORCHESTRATE file from a spec document, optionally creating a worktree for isolated development.

## Usage

```bash
# Interactive: scan for specs and choose
/craft:orchestrate:plan

# Direct: specify spec path
/craft:orchestrate:plan docs/specs/SPEC-auth-2026-02-15.md

# ORCHESTRATE only (no worktree)
/craft:orchestrate:plan docs/specs/SPEC-auth.md --output orchestrate-only
```

## Execution Behavior (MANDATORY)

Follow these steps in order. Do NOT skip any step.

### Step 1: Discover Specs

If no `spec-path` argument provided:

1. Scan `docs/specs/` for `SPEC-*.md` files
2. For each spec, check if an `ORCHESTRATE-*.md` already exists (match by topic name)
3. Scan `docs/brainstorm/` and repo root for `BRAINSTORM-*.md` without matching specs
4. Display results:

```text
Available specs:
  1. SPEC-auth-2026-02-10.md (no ORCHESTRATE yet)
  2. SPEC-dashboard-2026-02-12.md (has ORCHESTRATE — skip or regenerate)

Brainstorms without specs:
  3. BRAINSTORM-caching-2026-02-14.md (create spec first?)
```

5. Ask user to choose:

```json
{
  "questions": [{
    "question": "Which spec should I create an ORCHESTRATE file from?",
    "header": "Spec",
    "multiSelect": false,
    "options": [
      {"label": "SPEC-auth-2026-02-10.md", "description": "No ORCHESTRATE exists yet. Ready for planning."},
      {"label": "SPEC-dashboard-2026-02-12.md", "description": "ORCHESTRATE exists. Will regenerate."},
      {"label": "BRAINSTORM-caching-2026-02-14.md", "description": "No spec yet. Will offer to create spec first."}
    ]
  }]
}
```

If user selects a brainstorm without a spec, suggest running `/brainstorm s "topic"` to capture the spec first. Do NOT auto-generate specs — the user should review brainstorm → spec capture interactively.

### Step 2: Parse Spec

Read the selected spec and extract:

1. **Title/topic** — from the first `#` heading or frontmatter
2. **Phases/increments** — look for `## Phase`, `## Increment`, `## Step`, numbered sections, or task lists
3. **Acceptance criteria** — look for `## Acceptance`, `## Done When`, `## Success Criteria`
4. **Technical details** — key files, dependencies, constraints
5. **Cross-repo references** — paths containing `~/projects/` or references to other repos

Display parsed results:

```text
Parsed from SPEC-auth-2026-02-15.md:
  Topic: user-authentication
  Phases: 3
    Phase 1: Setup auth middleware (3 tasks)
    Phase 2: Implement OAuth flow (5 tasks)
    Phase 3: Add tests and docs (4 tasks)
  Acceptance criteria: 6 items
  Cross-repo: None detected
```

### Step 3: Detect Cross-Repo Work

Scan the spec for paths referencing other repositories:

- Paths like `~/projects/dev-tools/<other-repo>/`
- References to packages in other repos
- Import paths from sibling projects

If cross-repo detected:

```text
Cross-repo work detected:
  Primary: craft (this repo)
  Secondary: mcp-servers (~/projects/dev-tools/mcp-servers/)

  Strategy: Same branch name enforced across repos.
  Both worktrees will use: feature/<topic>
```

### Step 4: Confirm Plan

```json
{
  "questions": [{
    "question": "Proceed with orchestration plan?",
    "header": "Continue",
    "multiSelect": false,
    "options": [
      {"label": "ORCHESTRATE + worktree (Recommended)", "description": "Generate ORCHESTRATE file and create worktree for isolated development."},
      {"label": "ORCHESTRATE only", "description": "Generate ORCHESTRATE file in current directory. No worktree."},
      {"label": "Modify phases", "description": "Adjust the parsed phases before generating."},
      {"label": "Cancel", "description": "Exit without changes."}
    ]
  }]
}
```

### Step 5: Generate ORCHESTRATE File

Create `ORCHESTRATE-<topic>.md` using the template below. Place it:

- In the **worktree root** if creating a worktree
- In the **repo root** if ORCHESTRATE only

#### ORCHESTRATE Template

```markdown
# <Topic> — Orchestration Plan

> **Branch:** `feature/<topic>`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/<project>/feature-<topic>`
> **Spec:** `<spec-path>`
> **Version Target:** <next version or TBD>

## Objective

<1-2 sentence summary from spec>

## Phase Overview

| Phase | Increment | Priority | Effort | Status |
|-------|----------|----------|--------|--------|
| 1 | <name> | High | <est> | |
| 2 | <name> | Medium | <est> | |

## Phase 1: <Name>

**Scope:** <brief scope description>

- [ ] 1.1 <task from spec>
- [ ] 1.2 <task from spec>

**Key files:**
- `<file>` (NEW or update)

## Phase N: <Name>

<repeat for each phase>

## Friction Prevention (from insights)

<If insights data available at ~/.claude/usage-data/facets/, analyze for project-specific friction patterns and add guardrails. Otherwise use defaults:>

- **Context first**: Read this ORCHESTRATE file and the spec BEFORE starting work
- **Verify location**: Confirm CWD is the worktree, not the main repo
- **No autonomous starts**: After each phase, STOP and confirm before proceeding
- **Test per phase**: Run tests after each phase to catch regressions

## Acceptance Criteria

<from spec, as checkboxes>

- [ ] <criterion 1>
- [ ] <criterion 2>

## Commit Strategy

- Conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`
- Phase 1: `docs(<topic>): <description>`
- Phase 2: `feat(<topic>): <description>`

## Verification

After each phase:

```bash
# Project-specific test command (auto-detected)
<test command>

# Link check (if docs modified)
<link check command>
```

## Session Instructions

### Context

You are in the **\<project\> repo worktree** for the \<topic\> feature. The spec has full design details.

### How to Start

```bash
cd <worktree-path>
claude
```

On session start, paste:

> Read `ORCHESTRATE-<topic>.md` and the spec at `<spec-path>`. Start Phase 1.

### Phase-by-Phase

1. Read current state of each file listed in the phase
2. Implement changes per the spec design
3. Run verification after each phase
4. Commit in logical groups
5. STOP and confirm before next phase

```

### Step 6: Create Worktree (if selected)

If "ORCHESTRATE + worktree" was selected:

1. Check if worktree already exists at `~/.git-worktrees/<project>/feature-<topic>`
2. Create branch from `dev`: `git worktree add ~/.git-worktrees/<project>/feature-<topic> -b feature/<topic> dev`
3. Copy ORCHESTRATE file to worktree root
4. For cross-repo: create paired worktree in secondary repo with same branch name

If worktree creation fails (branch exists, path exists), report the error and suggest resolution.

### Step 7: Update Project Tracking

1. Add `ORCHESTRATE-*.md` to `.gitignore` if not already present
2. Update `.STATUS` file with worktree entry (if `.STATUS` exists):

```

## Active Worktrees

- feature/\<topic\> — \<1-line summary\> (created \<date\>)

```

### Step 8: Summary

```text
Created:
  ORCHESTRATE-<topic>.md (in worktree root)
  Worktree at ~/.git-worktrees/<project>/feature-<topic>
  .STATUS updated

Next steps:
  cd ~/.git-worktrees/<project>/feature-<topic>
  claude
  → "Read ORCHESTRATE-<topic>.md and start Phase 1"
```

## Auto-Detection

### Test Commands

Detect project type and suggest verification commands:

| Detection | Test Command |
|-----------|-------------|
| `tests/test_craft_plugin.py` | `python3 tests/test_craft_plugin.py` |
| `package.json` with test script | `npm test` |
| `pytest.ini` or `pyproject.toml` | `pytest` |
| `Cargo.toml` | `cargo test` |
| `DESCRIPTION` (R) | `R CMD check` |

### Rebase Strategy

Check if the base branch (`dev`) has recent automated commits:

- If last 5 commits on `dev` include `chore:` or bot commits → suggest rebase before PR
- If clean history → standard merge workflow

## See Also

- [/craft:orchestrate](../orchestrate.md) — Launch orchestrator mode
- [/craft:orchestrate:resume](resume.md) — Resume sessions across devices
- [/craft:git:worktree](../git/worktree.md) — Manual worktree management
- [Worktree Tutorial](../../docs/tutorials/TUTORIAL-worktree-setup.md) — Step-by-step guide
