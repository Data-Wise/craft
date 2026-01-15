# CLAUDE.md - Craft Plugin

## Project Overview

Craft is a full-stack developer toolkit plugin for Claude Code featuring 86 commands, 21 skills, and 8 agents for smart orchestration, ADHD-friendly workflows, and multi-agent coordination.

## Git Workflow & Standards

### Branch Architecture

| Branch | Purpose | Protection |
|--------|---------|------------|
| `main` | Production releases | **PROTECTED** - No direct commits |
| `dev` | Planning & integration hub | All features branch from here |
| `feature/*` | Isolated implementation | Created via worktrees |

### Mandatory Workflow

```
main (protected)
  ↑
  │ PR/Merge only
  │
dev (integration)
  ↑
  │ Rebase + merge
  │
feature/* (worktrees)
```

#### 1. Plan on `dev`

Before coding, analyze requirements on `dev`. Summarize the plan and **wait for approval**.

```bash
git checkout dev
# Analyze, plan, discuss
# Do NOT write feature code here
```

#### 2. Isolate via Worktree

Once approved, create a worktree for isolated development:

```bash
git worktree add ~/.git-worktrees/craft/<branch-name> -b feature/<branch-name> dev
```

**Constraint**: Never write feature code directly on `dev`.

#### 3. Atomic Development

- Use **Conventional Commits**: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`
- Commits must be small and functional
- Each commit should be independently deployable

#### 4. Integration (feature → dev)

```bash
# In worktree: run tests/linters
python3 tests/test_craft_plugin.py

# Rebase onto dev for linear history
git fetch origin dev
git rebase origin/dev

# Push and create PR to dev
git push -u origin feature/<branch-name>
gh pr create --base dev

# After merge, cleanup
git worktree remove ~/.git-worktrees/craft/<branch-name>
git branch -d feature/<branch-name>
```

#### 5. Release (dev → main)

```bash
# Create PR from dev to main
gh pr create --base main --head dev --title "Release vX.Y.Z"

# Never bypass this step
# Never commit directly to main
```

### Tool Usage Constraints

1. **Always verify branch** before any git operation:
   ```bash
   git branch --show-current
   ```

2. **ABORT if on `main`**: If about to commit to `main`, stop immediately and redirect to PR workflow.

3. **Worktree awareness**: Check if in worktree:
   ```bash
   git rev-parse --git-dir  # Shows .git/worktrees/<name> if in worktree
   ```

## Quick Commands

| Task | Command |
|------|---------|
| Run tests | `python3 tests/test_craft_plugin.py` |
| Validate counts | `./scripts/validate-counts.sh` |
| Build docs | `mkdocs build` |
| Serve docs | `mkdocs serve` |

## Project Structure

```
craft/
├── .claude-plugin/     # Plugin manifest
├── commands/           # 86 command definitions
│   ├── arch/          # Architecture commands
│   ├── ci/            # CI commands
│   ├── code/          # Code quality commands
│   ├── docs/          # Documentation commands
│   ├── git/           # Git workflow commands
│   ├── site/          # Site generation commands
│   ├── test/          # Testing commands
│   └── workflow/      # ADHD-friendly workflow commands
├── skills/            # 21 specialized skills
├── agents/            # 8 agents (orchestrator-v2, etc.)
├── tests/             # Python test suite
└── docs/              # MkDocs documentation
```

## Key Files

- `commands/do.md` - Universal smart routing command
- `commands/check.md` - Pre-flight validation
- `commands/orchestrate.md` - Multi-agent coordination
- `agents/orchestrator-v2.md` - Enhanced agent coordinator
- `commands/workflow/brainstorm.md` - ADHD-friendly brainstorming
