# Quick Reference: Git Worktree

**Work on multiple branches simultaneously without switching — each branch gets its own folder.**

## Quick Decision Tree

```text
Need to work on something else?
│
├─ Quick fix (< 1 hour)?
│   └─ Just switch branches: git checkout fix/bug
│
├─ Longer work + need to switch back?
│   └─ CREATE WORKTREE
│
├─ Running dev server that shouldn't stop?
│   └─ CREATE WORKTREE
│
├─ Multiple Claude Code sessions?
│   └─ CREATE WORKTREE
│
└─ Already working on feature in main repo?
    └─ Use /craft:git:worktree move
```

## Common Commands

### Setup and Create

```bash
# First-time setup (once per project)
/craft:git:worktree setup

# Create worktree for new branch
/craft:git:worktree create feature/new-ui

# Create worktree for existing branch
/craft:git:worktree create feature/existing --use-existing

# Move current branch to worktree (with uncommitted work!)
/craft:git:worktree move
```

### List and Cleanup

```bash
# List all worktrees
git worktree list

# Clean merged worktrees
/craft:git:worktree clean

# Remove specific worktree
git worktree remove ~/.git-worktrees/project/feature-name

# Force remove (with uncommitted changes)
git worktree remove ~/.git-worktrees/project/feature-name --force

# Prune orphaned worktrees
git worktree prune
```

### Complete Feature

```bash
# Run tests, generate changelog, create PR
/craft:git:worktree finish

# Skip tests (faster)
/craft:git:worktree finish --skip-tests

# Create draft PR
/craft:git:worktree finish --draft

# Target main instead of dev
/craft:git:worktree finish --target main
```

## Scope Detection and Auto-Setup

When creating a worktree, craft detects scope from branch pattern and offers to create workflow files:

| Branch Pattern | Scope | Auto-Creates | Use Case |
|----------------|-------|--------------|----------|
| `fix/*` | Small | Nothing | Quick bug fixes (< 2 hours) |
| `feature/*` | Medium | ORCHESTRATE file | New features (2-8 hours) |
| `v*` | Release | ORCHESTRATE + SPEC | Version releases |
| User selects "multi-phase" | Large | All files | Complex projects (> 8 hours) |

### Auto-Created Files

| File | Created When | Purpose |
|------|-------------|---------|
| **ORCHESTRATE-\<name\>.md** | Medium+ scope | Task plan with phases and acceptance criteria |
| **docs/specs/SPEC-\<name\>-\<date\>.md** | Release or multi-phase | Requirements and design decisions |
| **.STATUS** update | Multi-phase only | Marks branch as WIP in project status |
| **CLAUDE.md** update | Multi-phase only | Adds worktree to active development table |

## Interactive Workflow

### Create Worktree Flow

```text
1. Show plan         → Branch, location, steps, scope
2. Confirm           → "Proceed?" (yes/change base/change location/cancel)
3. Create directory  → ~/.git-worktrees/project/branch-name
4. Create branch     → Branches from dev (or specified base)
5. Install deps      → Auto-detects project type
6. Scope detection   → "What files to create?"
7. Summary           → Location, next steps
```

### Scope Detection Prompt

```text
? What workflow files should I create?
  > Create ORCHESTRATE file (Recommended)
    Multi-phase project (ORCHESTRATE + SPEC + .STATUS + CLAUDE.md)
    Minimal (no files)
    Custom
```

## Dependency Installation

Auto-detects project type and installs dependencies:

| Project Type | Detection File | Install Command |
|--------------|---------------|-----------------|
| Node.js | `package.json` | `npm install` |
| Python (uv) | `pyproject.toml` | `uv venv && uv pip install -e .` |
| Python (pip) | `requirements.txt` | `pip install -r requirements.txt` |
| Rust | `Cargo.toml` | Nothing (global cache) |
| Go | `go.mod` | Nothing (global cache) |
| R | `DESCRIPTION` | Nothing (global library) |
| R (renv) | `renv.lock` | `R -e "renv::restore()"` |

## Typical Workflows

### Workflow 1: Simple Feature

```bash
# 1. Create worktree
/craft:git:worktree create feature/add-auth

# 2. Navigate to worktree
cd ~/.git-worktrees/craft/feature-add-auth

# 3. Customize ORCHESTRATE file (if created)
code ORCHESTRATE-add-auth.md

# 4. Start working
claude  # or work manually

# 5. Commit as you work
git add .
git commit -m "feat: add OAuth login"

# 6. Pre-flight check
/craft:check

# 7. Finish (tests + changelog + PR)
/craft:git:worktree finish

# 8. After PR merge, clean up
cd ~/projects/dev-tools/craft
/craft:git:worktree clean
```

### Workflow 2: Urgent Hotfix Mid-Feature

```bash
# You're working in feature worktree
cd ~/.git-worktrees/craft/feature-add-auth

# Urgent bug reported — create hotfix worktree
cd ~/projects/dev-tools/craft
/craft:git:worktree create fix/urgent-login-bug

# Fix in separate folder
cd ~/.git-worktrees/craft/fix-urgent-login-bug
# Make fix, commit, create PR

# Return to feature work (exactly as you left it)
cd ~/.git-worktrees/craft/feature-add-auth
```

### Workflow 3: Parallel Dev Servers

```bash
# Terminal 1: Frontend server
cd ~/.git-worktrees/craft/feature-frontend-redesign
npm run dev -- --port 3000

# Terminal 2: Backend server
cd ~/.git-worktrees/craft/feature-api-v2
npm run dev -- --port 4000

# Terminal 3: Work on either
cd ~/.git-worktrees/craft/feature-frontend-redesign
claude
```

## Troubleshooting Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| "Branch already exists" | `/craft:git:worktree create branch-name --use-existing` |
| Dependencies missing | `cd worktree && /craft:git:worktree install` |
| Can't remove worktree | `git worktree remove path --force` |
| Orphaned worktrees | `git worktree prune` |
| Rebase conflicts | `git rebase --abort && git merge origin/dev` |
| Wrong base branch | Create new worktree with `--base main` |
| Path too long (macOS) | Use shorter branch names |
| Main repo on wrong branch | `cd main-repo && git checkout main` |

## Best Practices

### DO

- ✅ Keep worktrees outside project folder (`~/.git-worktrees/`)
- ✅ Use consistent naming (`project/feature-name`)
- ✅ Install dependencies after creating worktree
- ✅ Start Claude Code IN the worktree folder
- ✅ Use different ports for dev servers (`PORT=3001`)
- ✅ Keep main repo on `main` or `dev` (never feature branches)
- ✅ Run `/craft:git:worktree clean` after merging PRs
- ✅ Use `/craft:git:worktree move` if you forget to create worktree first

### DON'T

- ❌ Create worktrees inside the project folder
- ❌ Switch branches within a worktree (defeats the purpose!)
- ❌ Forget to install dependencies
- ❌ Leave stale worktrees around
- ❌ Work on features in the main repo
- ❌ Use same port for multiple dev servers
- ❌ Delete worktrees with uncommitted work (unless using `--force`)

## Shell Aliases (Recommended)

```bash
# Add to ~/.zshrc or ~/.bashrc

# Navigate to worktrees folder
alias wt='cd ~/.git-worktrees'

# List all worktrees
alias wtl='git worktree list'

# Project-specific (customize for your projects)
alias craft-wt='cd ~/.git-worktrees/craft'
alias myapp-wt='cd ~/.git-worktrees/myapp'

# Cleanup merged worktrees shortcut
alias wt-clean='git worktree prune && git branch -d $(git branch --merged | grep -v "\*" | grep -v "main" | grep -v "dev")'
```

## Common Patterns

### Pattern 1: Review PR in Separate Worktree

```bash
# Someone asks you to review their PR #42
gh pr checkout 42 --worktree
# Creates worktree at ~/.git-worktrees/project/pr-42

cd ~/.git-worktrees/project/pr-42
# Review code, run tests
/craft:check

# Done reviewing
cd ~/projects/dev-tools/project
git worktree remove ~/.git-worktrees/project/pr-42
```

### Pattern 2: Multiple Related Features

```bash
# Create worktrees for related features
/craft:git:worktree create feature/auth-backend
/craft:git:worktree create feature/auth-frontend
/craft:git:worktree create feature/auth-tests

# Work on all three in parallel
# Terminal 1: Backend
cd ~/.git-worktrees/craft/feature-auth-backend

# Terminal 2: Frontend
cd ~/.git-worktrees/craft/feature-auth-frontend

# Terminal 3: Tests
cd ~/.git-worktrees/craft/feature-auth-tests
```

### Pattern 3: Long-Running Development

```bash
# Create worktree for multi-week feature
/craft:git:worktree create feature/v2.9.0

# Choose "Multi-phase project"
# → Creates ORCHESTRATE, SPEC, updates .STATUS and CLAUDE.md

# Work for days/weeks, commit frequently
cd ~/.git-worktrees/craft/feature-v2.9.0

# Stay synced with dev
git fetch origin dev
git rebase origin/dev

# When complete
/craft:git:worktree finish
```

## Location Conventions

| Location | Pattern | Example |
|----------|---------|---------|
| **Worktree folder** | `~/.git-worktrees/<project>/` | `~/.git-worktrees/craft/` |
| **Feature branch** | `<folder>/feature-<name>/` | `.git-worktrees/craft/feature-auth/` |
| **Fix branch** | `<folder>/fix-<name>/` | `.git-worktrees/craft/fix-login-bug/` |
| **Release branch** | `<folder>/v<version>/` | `.git-worktrees/craft/v2.9.0/` |
| **Main repo** | `~/projects/<category>/<project>/` | `~/projects/dev-tools/craft/` |

## Quick Checks

### Verify Main Repo Branch

```bash
cd ~/projects/dev-tools/craft
git branch --show-current
# Should output: main (or dev)
# If not: git checkout main
```

### List Active Worktrees

```bash
git worktree list
# Output:
# /Users/you/projects/dev-tools/craft        93a10ad [main]
# /Users/you/.git-worktrees/craft/feature-auth  8bf5444 [feature/auth]
```

### Check Worktree Dependencies

```bash
cd ~/.git-worktrees/craft/feature-name

# Node.js
[ -d node_modules ] && echo "✅ Dependencies installed" || echo "❌ Run: npm install"

# Python
python -c "import pkg" 2>/dev/null && echo "✅ Package installed" || echo "❌ Run: pip install -e ."
```

## See Also

- **Tutorial:** [Worktree Setup Tutorial](../tutorials/TUTORIAL-worktree-setup.md) — Step-by-step guide
- **Command docs:** [/craft:git:worktree](../commands/git/worktree.md) — Full documentation
- **Workflow:** [Git Feature Workflow](../workflows/git-feature-workflow.md) — Complete workflow
- **Pattern guide:** [Interactive Commands Guide](../guide/interactive-commands.md) — How the pattern works
