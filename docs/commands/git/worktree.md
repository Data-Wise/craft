# /craft:git:worktree

> **Git worktree management for parallel development without branch switching.**

---

## Synopsis

```bash
/craft:git:worktree <action> [branch]
```

**Quick examples:**

```bash
# First-time setup
/craft:git:worktree setup

# Create worktree for feature
/craft:git:worktree create feature/new-ui

# Move current branch to worktree
/craft:git:worktree move

# Complete feature workflow
/craft:git:worktree finish
```

---

## Description

Manage git worktrees to work on multiple branches simultaneously without switching. Each branch gets its own folder, eliminating stash juggling and context switching.

**Why worktrees?**

- **No branch switching** - Each branch has its own folder
- **Parallel development** - Work on feature + hotfix at same time
- **Claude Code friendly** - Each terminal/session stays on its branch
- **No stash juggling** - Uncommitted work stays put
- **Auto-setup** — detects scope and creates workflow files automatically (NEW)

---

## Actions

| Action | Description |
|--------|-------------|
| `setup` | First-time folder creation |
| `create` | Create worktree for new/existing branch |
| `move` | Move current branch (with uncommitted work!) to worktree |
| `list` | Show all worktrees |
| `clean` | Remove merged worktrees |
| `install` | Install dependencies in current worktree |
| `finish` | Complete feature: tests → changelog → PR |

---

## Examples

### setup - First-Time Configuration

```bash
/craft:git:worktree setup
```

Creates the worktree parent folder structure:

```
╭─ Worktree Setup ────────────────────────────────────╮
│ Project: craft                                      │
│ Main repo: ~/projects/dev-tools/craft               │
│ Worktree folder: ~/.git-worktrees/craft/            │
├─────────────────────────────────────────────────────┤
│ ✅ Created ~/.git-worktrees/craft/                  │
│                                                     │
│ Next steps:                                         │
│   /craft:git:worktree create feature/my-feature     │
╰─────────────────────────────────────────────────────╯
```

### create - Create New Worktree

```bash
/craft:git:worktree create feature/new-ui
```

Creates a worktree with step preview (NEW) and optional auto-setup:

```
Worktree Setup Plan:
  Project: craft
  Action: create
  Branch: feature/new-ui
  Location: ~/.git-worktrees/craft/feature-new-ui

  Steps:
  1. Create worktree directory
  2. Create branch from dev
  3. Install dependencies (Node.js detected)
  4. Auto-setup workflow files (scope: medium)

? Proceed with this worktree setup?
  › Yes - Create worktree (Recommended)
    Change base branch
    Change location
    Cancel

  [1/4] Creating directory... ✅
  [2/4] Creating branch from dev... ✅
  [3/4] Installing dependencies (npm install)... ✅
  [4/4] Creating ORCHESTRATE-new-ui.md... ✅

Worktree ready: ~/.git-worktrees/craft/feature-new-ui
Branch: feature/new-ui
Next: cd ~/.git-worktrees/craft/feature-new-ui && claude
```

### Auto-Setup After Create (NEW)

After creating a worktree, the command detects scope from the branch name and offers to create workflow files:

```
/craft:git:worktree create feature/v2.9.0

Step 1: Create worktree ✅
  Branch: feature/v2.9.0
  Location: ~/.git-worktrees/craft/feature-v2.9.0

Step 2: Scope detection
  Branch pattern: feature/* → Medium scope

? Branch 'feature/v2.9.0' detected as medium scope.
  What workflow files should I create?
  › Create ORCHESTRATE file (Recommended)
    Multi-phase project (ORCHESTRATE + SPEC + update .STATUS + CLAUDE.md)
    Minimal (no files)
    Custom

Step 3: Files created
  ✅ ORCHESTRATE-v2.9.0.md (plan template)

Ready! Start working:
  cd ~/.git-worktrees/craft/feature-v2.9.0
  claude
```

**Scope Detection:**

| Branch Pattern | Scope | Auto-Create |
|----------------|-------|-------------|
| `fix/*` | Small | No workflow files |
| `feature/*` | Medium | ORCHESTRATE file |
| `v*` (release) | Release | ORCHESTRATE + SPEC |
| User selects "multi-phase" | Large | ORCHESTRATE + SPEC + .STATUS + CLAUDE.md |

**Generated Files:**

- **ORCHESTRATE-\<name\>.md** — Task plan template with phases, acceptance criteria, and "how to start"
- **docs/specs/SPEC-\<name\>-\<date\>.md** — Requirements, design decisions, implementation plan (medium+ scope)
- **.STATUS** update — Marks branch as WIP in main repo (multi-phase only)
- **CLAUDE.md** update — Adds worktree to active table (multi-phase only)

---

### move - Move Current Branch to Worktree

**The killer feature!** Moves your current branch with uncommitted work:

```bash
/craft:git:worktree move
```

```
╭─ Move Branch to Worktree ───────────────────────────╮
│ Branch: feat/mission-control-hud                    │
│ Uncommitted files: 37                               │
├─────────────────────────────────────────────────────┤
│ Step 1/5: Stashing work...                          │
│   ✅ Stashed 37 files                               │
│                                                     │
│ Step 2/5: Switching main folder to 'main'...        │
│   ✅ Now on branch 'main'                           │
│                                                     │
│ Step 3/5: Creating worktree...                      │
│   ✅ Created at ~/.git-worktrees/scribe/feat-...    │
│                                                     │
│ Step 4/5: Restoring stashed work...                 │
│   ✅ Applied stash, 37 files restored               │
│                                                     │
│ Step 5/5: Installing dependencies...                │
│   📦 npm install                                    │
│   ✅ Dependencies installed                         │
├─────────────────────────────────────────────────────┤
│ DONE! Your setup is now:                            │
│                                                     │
│   ~/projects/dev-tools/scribe                       │
│     └── Branch: main (stable base)                  │
│                                                     │
│   ~/.git-worktrees/scribe/feat-mission-control-hud  │
│     └── Branch: feat/mission-control-hud            │
│     └── Your 37 uncommitted files are here!         │
╰─────────────────────────────────────────────────────╯
```

### finish - Complete Feature Workflow

```bash
/craft:git:worktree finish
```

Runs tests, generates changelog, and creates PR:

```
╭─ Finish Feature ────────────────────────────────────╮
│ Branch: feat/user-auth                              │
│ Commits: 7 since branching from main                │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Step 1/3: Running Tests                             │
│   📦 Detected: Python (pyproject.toml)              │
│   🧪 Running: pytest -v                             │
│   ✅ 47 tests passed                                │
│                                                     │
│ Step 2/3: Generating Changelog                      │
│   📝 Branch type: feat/* → "Added" section          │
│   📝 Entry generated                                │
│                                                     │
│ Step 3/3: Creating PR                               │
│   🎯 Target: dev                                    │
│   📋 Title: feat: Add user authentication system    │
│   ✅ PR created: https://github.com/.../pull/42     │
│                                                     │
├─────────────────────────────────────────────────────┤
│ DONE! Feature complete.                             │
│                                                     │
│ Next steps:                                         │
│   - Review PR: gh pr view 42                        │
│   - Clean worktree after merge:                     │
│     /craft:git:worktree clean                       │
╰─────────────────────────────────────────────────────╯
```

**Flags:**

```bash
/craft:git:worktree finish --skip-tests    # Skip test step
/craft:git:worktree finish --draft         # Create draft PR
/craft:git:worktree finish --target main   # Target main instead of dev
```

---

## Dependency Installation

Auto-detects project type and installs dependencies:

| Project Type | Detection | Install Command |
|--------------|-----------|-----------------|
| Node.js | `package.json` | `npm install` |
| Python (uv) | `pyproject.toml` | `uv venv && uv pip install -e .` |
| Python (pip) | `requirements.txt` | `pip install -r requirements.txt` |
| Rust | `Cargo.toml` | Nothing (global cache) |
| Go | `go.mod` | Nothing (global cache) |
| R | `DESCRIPTION` | Nothing (global library) |
| R (renv) | `renv.lock` | `R -e "renv::restore()"` |

---

## Worktree vs Branch Decision

```
Need to work on something else?
│
├─ Quick fix (< 1 hour)?
│   └─ Just switch branches
│
├─ Longer work + need to switch back?
│   └─ CREATE WORKTREE
│
├─ Running dev server that shouldn't stop?
│   └─ CREATE WORKTREE
│
├─ Using Claude Code in parallel?
│   └─ CREATE WORKTREE
│
└─ Not sure?
    └─ CREATE WORKTREE (safer)
```

---

## Best Practices

### DO

- Keep worktrees outside project folder (`~/.git-worktrees/`)
- Use consistent naming (`project/branch-name`)
- Install deps after creating worktree
- Start Claude Code IN the worktree folder
- Use different ports for dev servers (`PORT=3001 npm run dev`)

### DON'T

- Create worktrees inside the project folder
- Switch branches within a worktree (defeats the purpose!)
- Forget to install dependencies
- Leave stale worktrees around (use `clean`)

---

## Shell Aliases (Recommended)

```bash
# Add to ~/.zshrc
alias wt='cd ~/.git-worktrees'
alias wtl='git worktree list'

# Project-specific
alias craft-wt='cd ~/.git-worktrees/craft'
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Worktree already exists" | `git worktree remove <path>` or use different name |
| Rebase conflicts | `git rebase --abort && git merge origin/dev` |
| Branch not up to date | `git fetch origin dev && git rebase origin/dev` |
| Orphaned worktrees | `git worktree prune` |
| Can't delete branch | Check if worktree still exists for that branch |
| Dependencies missing | Run `/craft:git:worktree install` |

---

## Quick Reference

| Action | Command |
|--------|---------|
| Setup worktrees | `/craft:git:worktree setup` |
| Create worktree | `/craft:git:worktree create feature/name` |
| List worktrees | `git worktree list` |
| Clean merged | `/craft:git:worktree clean` |
| Complete feature | `/craft:git:worktree finish` |
| Remove worktree | `git worktree remove <path>` |

---

## See Also

- **Pre-flight check:** `/craft:check` - Validates before commit/PR
- **Branch cleanup:** `/craft:git:clean` - Clean merged branches
- **Workflow:** [Git Feature Workflow](../../workflows/git-feature-workflow.md)
