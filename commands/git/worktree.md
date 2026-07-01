---
description: Git worktree management for parallel development workflows
category: git
arguments:
  - name: action
    description: Action to perform (setup|create|move|list|clean|install|finish|validate)
    required: true
  - name: branch
    description: Branch name (for create/move actions)
    required: false
  - name: dry-run
    description: Preview changes without executing (for setup/create/move/clean/finish actions)
    required: false
    default: false
    alias: -n
deprecated: true
replaced-by: "skills/dev/git/"
---

# /craft:git:worktree - Parallel Development with Git Worktrees

> **This command is a thin(ner) shim.** The canonical operation logic —
> what each action does, dependency auto-detection, scope-based
> workflow-file creation — lives in the `git-workflow` skill
> (`skills/dev/git/SKILL.md`, Operation 5: Worktree Management). This file
> keeps the flag contract and the exact LLM-executable interaction
> contract (Step 0/0.5, `AskUserQuestion` prompts, branch-guard hard block)
> that Claude must follow regardless of skill-routing.
>
> **Scope note:** the pre-consolidation version also carried a full
> shell-aliases-for-`~/.zshrc` section, a decision-tree ASCII diagram,
> per-action dry-run mockups, and duplicated box-drawing output for every
> action. That's illustrative, not unique behavior — dropped rather than
> ported. See the skill for the operation list if something looks missing.

Manage git worktrees for working on multiple branches simultaneously without switching.

## Craft Worktrees vs Claude Code Native Isolation

| Aspect | Craft (`/craft:git:worktree`) | Claude Code Native (`isolation: worktree`) |
|--------|-------------------------------|-------------------------------------------|
| Location | `~/.git-worktrees/<project>/<branch>` | `.claude/worktrees/<hash>/` |
| Lifetime | Persistent until manually removed | Temporary, auto-cleaned after agent finishes |
| Branch naming | `feature/<name>` from `dev` | Agent-generated temporary branch |
| Use case | Feature development workflow | Agent isolation during subagent execution |

Craft's worktrees are long-lived and user-managed, integrated into the
`dev → feature/* → PR` workflow. Claude Code's native isolation is
agent-scoped and auto-cleaned. A craft worktree can itself host subagent
execution with `isolation: worktree` if needed — the two are complementary,
not competing.

## Execution Behavior (MANDATORY)

When this command runs, Claude MUST follow these steps in order. Do NOT skip
the setup plan or proceed without confirming with the user.

### Step 0: Show Setup Plan

Before making ANY changes (creating directories, branches, or files), display
what will happen:

```text
Worktree Setup Plan:
  Project: <project-name>
  Action: <create|move|clean|finish>
  Branch: <branch-name>
  Location: ~/.git-worktrees/<project>/<folder-name>

  Steps:
  1. <first action> (e.g., Create worktree directory)
  2. <second action> (e.g., Create branch from dev)
  3. <third action> (e.g., Install dependencies)
  ...
```

### Step 0.5: Confirm Before Executing

After showing the plan, ask before proceeding (via `AskUserQuestion`):

```json
{
  "questions": [{
    "question": "Proceed with this worktree setup?",
    "header": "Worktree",
    "multiSelect": false,
    "options": [
      {
        "label": "Yes - Create worktree (Recommended)",
        "description": "Execute the <N> steps shown above."
      },
      {
        "label": "Change base branch",
        "description": "Branch from a different base (currently: dev)."
      },
      {
        "label": "Change location",
        "description": "Use a different worktree directory."
      },
      {
        "label": "Cancel",
        "description": "Exit without creating anything."
      }
    ]
  }]
}
```

### Steps 1-N: Execute with Progress, Then Summary

```text
  [1/N] Creating directory... ✅
  [2/N] Creating branch... ✅
  [3/N] Installing dependencies... ✅
  ...

  Worktree ready: ~/.git-worktrees/<project>/<folder>
  Branch: <branch-name>
  Next: cd <path> && claude
```

**Exception:** the `list`, `install`, and `validate` actions are read-only
— no confirmation needed, no changes made.

## Usage

```bash
/craft:git:worktree setup              # First-time folder creation
/craft:git:worktree create <branch>    # Create worktree for branch
/craft:git:worktree move <branch>      # Move current branch to worktree
/craft:git:worktree list               # Show all worktrees
/craft:git:worktree clean              # Remove merged worktrees
/craft:git:worktree install            # Install deps in current worktree
/craft:git:worktree finish             # Complete feature: tests → changelog → cleanup ORCHESTRATE → PR
/craft:git:worktree validate           # Verify CWD matches expected worktree
```

## Branch Guard (create)

Worktrees must be created from `dev`, never from `main`. Hard block, no
override:

```
Cannot create worktree from main.
Worktrees must branch from dev.

Switch to dev first:
  git checkout dev
```

## Auto-Setup After Create: Scope Detection

After creating a worktree, detect scope from the branch name and offer to
create workflow files (`ORCHESTRATE-<name>.md`, and for larger scope a
`SPEC-<name>-<date>.md`, `.STATUS` entry, `CLAUDE.md` row):

| Branch Pattern | Scope | Auto-Create |
|----------------|-------|-------------|
| `fix/*` | Small | No workflow files |
| `feature/*` | Medium | ORCHESTRATE file |
| `v*` (release) | Release | ORCHESTRATE + SPEC |
| User selects "multi-phase" | Large | ORCHESTRATE + SPEC + .STATUS + CLAUDE.md |
| User selects "custom" | Custom | Ask what to create |

Confirm the detected scope via `AskUserQuestion` before creating any file —
full operation detail (exact templates, flow) lives in
[`skills/dev/git/SKILL.md`](../../skills/dev/git/SKILL.md), Operation 5.

## move - Move Current Branch to Worktree

**The killer feature.** Moves your current branch (with uncommitted work,
via stash/pop) to a worktree so the main folder can return to a stable
branch. See the skill for the full stash → switch → worktree-add → restore
→ install sequence.

## finish - Complete Feature Workflow

Runs tests (auto-detected by project type), generates a changelog entry,
removes stray `ORCHESTRATE-*.md` working artifacts, and opens a PR:

```bash
/craft:git:worktree finish --skip-tests    # Skip test step
/craft:git:worktree finish --draft         # Create draft PR
/craft:git:worktree finish --target main   # Target main instead of dev
```

Full step-by-step (test-command detection table, changelog section
inference, PR body template) lives in the skill.

## install - Install Dependencies

Auto-detects project type (`package.json`, `pyproject.toml`,
`requirements.txt`, `Cargo.toml`, `go.mod`, `DESCRIPTION`/`renv.lock`) and
runs the matching install command. Read-only otherwise (Rust/Go use global
caches).

## validate - Verify Worktree Environment

Read-only check that CWD is inside the expected `~/.git-worktrees/<project>/<branch>`
worktree and the branch matches the folder name. No confirmation needed.

## clean - Remove Merged Worktrees

Finds worktrees for branches merged into `main`/`dev`, confirms per-branch
removal, then runs `git worktree prune` for stale references.

## Best Practices

- Keep worktrees outside the project folder (`~/.git-worktrees/`)
- Use consistent naming (`project/branch-name`)
- Start Claude Code IN the worktree folder
- Don't switch branches within a worktree — create a new one instead
- Don't leave stale worktrees around — run `clean` after merge

## Integration

**Related commands:**

- `/craft:check` - Detects worktree context
- `/craft:git:sync` - Works in worktrees too
- `/craft:git:clean` - Cleans branches (not worktrees)

**Workflow summary:**

```
/craft:git:worktree create feat/my-feature   # Start
        ↓
   [do your work]
        ↓
/craft:git:worktree finish                   # Complete: tests → changelog → cleanup ORCHESTRATE → PR
        ↓
/craft:git:worktree clean                    # Cleanup after merge
```

## Dry-Run Mode

Every state-changing action (`setup`, `create`, `move`, `clean`, `finish`)
supports `--dry-run`/`-n` — preview the plan without executing. `list`,
`install`, and `validate` are already read-only and don't need it.

## See Also

- `skills/dev/git/SKILL.md` — canonical operation logic (Operation 5)
- `/craft:git:branch` - Interactive git branch management assistant
- `/craft:git:status` - Enhanced git status with teaching-specific context
- `/craft:git:unprotect` - Session-scoped bypass for branch protection with reason logging
- `/craft:git:protect-baseline` - Apply GitHub-side branch protection (PR required, no force-push, no delete) to any repo
