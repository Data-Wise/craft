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
# Using Craft command (recommended)
/craft:git:worktree feature/<branch-name>

# Or manually
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

### Shell Commands

| Task | Command |
|------|---------|
| Run tests | `python3 tests/test_craft_plugin.py` |
| Validate counts | `./scripts/validate-counts.sh` |
| Build docs | `mkdocs build` |
| Serve docs | `mkdocs serve` |

### Craft Commands

| Task | Command |
|------|---------|
| Pre-flight check | `/craft:check` |
| Run tests | `/craft:test:run` |
| Code linting | `/craft:code:lint` |
| Analyze architecture | `/craft:arch:analyze` |
| Create worktree | `/craft:git:worktree <branch>` |
| Clean merged branches | `/craft:git:clean` |
| Generate CI workflow | `/craft:ci:generate` |
| Validate CI config | `/craft:ci:validate` |
| Smart routing | `/craft:do <task>` |
| Brainstorm ideas | `/craft:workflow:brainstorm` |
| Launch orchestrator | `/craft:orchestrate` |

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

## Execution Modes

Commands support 4 execution modes for different use cases:

| Mode | Time Budget | Use Case |
|------|-------------|----------|
| **default** | < 10s | Quick tasks, day-to-day operations |
| **debug** | < 120s | Problem solving, verbose traces |
| **optimize** | < 180s | Performance profiling, benchmarks |
| **release** | < 300s | Pre-release validation, thorough checks |

### Usage

```bash
/craft:code:lint              # default mode
/craft:code:lint debug        # verbose output, fix suggestions
/craft:code:lint optimize     # performance-focused rules
/craft:code:lint release      # all rules + strict validation
```

### Mode Selection Logic

```
If user specifies mode → use that mode
Else if error/bug context → debug mode
Else if performance context → optimize mode
Else if release/deploy context → release mode
Else → default mode
```

## Agents

8 specialized agents for different documentation and orchestration tasks:

| Agent | Model | Purpose |
|-------|-------|---------|
| **orchestrator-v2** | - | Task decomposition, subagent coordination, context monitoring |
| **orchestrator** | - | Basic workflow automation and delegation |
| **docs-architect** | sonnet | Long-form technical documentation, architecture guides |
| **api-documenter** | sonnet | OpenAPI specs, interactive API docs, SDK generation |
| **tutorial-engineer** | sonnet | Step-by-step tutorials, onboarding guides |
| **reference-builder** | haiku | Parameter listings, configuration references |
| **mermaid-expert** | haiku | Flowcharts, sequence diagrams, ERDs |
| **demo-engineer** | - | VHS tape files for terminal GIF demos |

### When to Use Agents

- **orchestrator-v2**: Complex multi-step tasks requiring parallel execution
- **docs-architect**: Creating comprehensive system documentation
- **api-documenter**: API documentation with OpenAPI 3.1
- **tutorial-engineer**: User-facing tutorials and guides
- **reference-builder**: Exhaustive technical references
- **mermaid-expert**: Visual diagrams for documentation

## Troubleshooting

### Tests Failing

```bash
# Run full test suite
python3 tests/test_craft_plugin.py

# Check for broken links
python3 tests/test_craft_plugin.py -k "broken_links"

# Validate command/skill/agent counts
./scripts/validate-counts.sh
```

### Worktree Issues

```bash
# List all worktrees
git worktree list

# Remove stale worktree
git worktree remove ~/.git-worktrees/craft/<name> --force

# Prune orphaned worktrees
git worktree prune
```

### Branch Conflicts

```bash
# Sync with remote dev
git fetch origin dev
git rebase origin/dev

# If rebase fails, abort and merge instead
git rebase --abort
git merge origin/dev
```

### Plugin Not Loading

1. Check plugin manifest: `.claude-plugin/plugin.json`
2. Verify command syntax in frontmatter
3. Run validation: `/craft:check`

### Common Fixes

| Issue | Fix |
|-------|-----|
| Outdated counts in README | Run `./scripts/validate-counts.sh` |
| Broken internal links | Check paths relative to `docs/` |
| Command not found | Verify file is in `commands/` with valid frontmatter |
| Agent not triggering | Check triggers list in agent frontmatter |
