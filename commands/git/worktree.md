---
description: Git worktree management for parallel development workflows
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
---

# /craft:git:worktree - Parallel Development with Git Worktrees

Manage git worktrees for working on multiple branches simultaneously without switching.

## Why Worktrees?

- **No branch switching** - Each branch has its own folder
- **Parallel development** - Work on feature + hotfix at same time
- **Claude Code friendly** - Each terminal/session stays on its branch
- **No stash juggling** - Uncommitted work stays put

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

After showing the plan, ask before proceeding:

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

### Steps 1-N: Execute with Progress

Show each step as it completes:

```text
  [1/N] Creating directory... ✅
  [2/N] Creating branch... ✅
  [3/N] Installing dependencies... ✅
  ...
```

### Step N+1: Summary with Next Steps

```text
  Worktree ready: ~/.git-worktrees/<project>/<folder>
  Branch: <branch-name>
  Next: cd <path> && claude
```

**Exception:** The `list` action does not require confirmation — it's read-only.

## Usage

```bash
/craft:git:worktree setup              # First-time folder creation
/craft:git:worktree create <branch>    # Create worktree for branch
/craft:git:worktree move <branch>      # Move current branch to worktree
/craft:git:worktree list               # Show all worktrees
/craft:git:worktree clean              # Remove merged worktrees
/craft:git:worktree install            # Install deps in current worktree
/craft:git:worktree finish             # Complete feature: tests → changelog → PR
/craft:git:worktree validate          # Verify CWD matches expected worktree
```

## Actions

### setup - First-Time Configuration

Creates the worktree parent folder structure:

```bash
/craft:git:worktree setup
```

**What it does:**

```bash
# Get project name from git remote or folder
project=$(basename $(git rev-parse --show-toplevel))

# Create worktree parent folder
mkdir -p ~/.git-worktrees/$project

echo "✅ Worktree folder ready: ~/.git-worktrees/$project"
echo ""
echo "Next: /craft:git:worktree create <branch-name>"
```

**Output:**

```
╭─ Worktree Setup ────────────────────────────────────╮
│ Project: aiterm                                     │
│ Main repo: ~/projects/dev-tools/aiterm              │
│ Worktree folder: ~/.git-worktrees/aiterm/           │
├─────────────────────────────────────────────────────┤
│ ✅ Created ~/.git-worktrees/aiterm/                 │
│                                                     │
│ Next steps:                                         │
│   /craft:git:worktree create feature/my-feature     │
╰─────────────────────────────────────────────────────╯
```

### create - Create New Worktree

Creates a worktree for an existing or new branch.

**Branch Guard (NEW in v2.16.0):** Worktrees must be created from `dev`, never from `main`. If on `main`:

```
Cannot create worktree from main.
Worktrees must branch from dev.

Switch to dev first:
  git checkout dev

Then retry:
  /craft:git:worktree create feature/your-feature
```

No options to override. Hard block.

```bash
/craft:git:worktree create feature/new-ui
/craft:git:worktree create hotfix/urgent-fix
```

**What it does:**

```bash
# Step 0: Branch guard check (belt-and-suspenders with PreToolUse hook)
# The branch-guard.sh hook blocks edits on main, but this command-level
# check gives a clearer error message specific to worktree creation.
current_branch=$(git branch --show-current)
if [[ "$current_branch" == "main" ]]; then
    echo "Cannot create worktree from main. Switch to dev first."
    exit 1
fi

project=$(basename $(git rev-parse --show-toplevel))
branch=$1
folder_name=$(echo $branch | tr '/' '-')  # feature/new-ui → feature-new-ui

# Ensure parent exists
mkdir -p ~/.git-worktrees/$project

# Create worktree
git worktree add ~/.git-worktrees/$project/$folder_name $branch

# Detect project type and install dependencies
cd ~/.git-worktrees/$project/$folder_name
if [ -f package.json ]; then
    echo "📦 Installing npm dependencies..."
    npm install
elif [ -f pyproject.toml ]; then
    echo "🐍 Setting up Python environment..."
    uv venv && source .venv/bin/activate && uv pip install -e .
elif [ -f requirements.txt ]; then
    echo "🐍 Installing Python dependencies..."
    pip install -r requirements.txt
fi

echo "✅ Worktree ready at ~/.git-worktrees/$project/$folder_name"
```

**Output:**

```
╭─ Create Worktree ───────────────────────────────────╮
│ Branch: feature/new-ui                              │
│ Location: ~/.git-worktrees/aiterm/feature-new-ui    │
├─────────────────────────────────────────────────────┤
│ Creating worktree...                                │
│ ✅ Worktree created                                 │
│                                                     │
│ Installing dependencies...                          │
│ 📦 Detected: Node.js (package.json)                 │
│ ✅ npm install complete                             │
├─────────────────────────────────────────────────────┤
│ Ready! Start working:                               │
│   cd ~/.git-worktrees/aiterm/feature-new-ui         │
│   claude                                            │
╰─────────────────────────────────────────────────────╯
```

### Auto-Setup After Create (NEW)

After creating a worktree, the command automatically detects scope from the
branch name and offers to create workflow files.

#### Scope Detection

| Branch Pattern | Scope | Auto-Create |
|----------------|-------|-------------|
| `fix/*` | Small | No workflow files |
| `feature/*` | Medium | ORCHESTRATE file |
| `v*` (release) | Release | ORCHESTRATE + SPEC |
| User selects "multi-phase" | Large | ORCHESTRATE + SPEC + .STATUS + CLAUDE.md |
| User selects "custom" | Custom | Ask what to create |

#### Scope Confirmation

After detecting scope, confirm with the user:

```json
{
  "questions": [{
    "question": "Branch '<branch>' detected as <scope> scope. What workflow files should I create?",
    "header": "Scope",
    "multiSelect": false,
    "options": [
      {
        "label": "<auto-detected option> (Recommended)",
        "description": "Based on branch pattern '<pattern>'."
      },
      {
        "label": "Multi-phase project",
        "description": "ORCHESTRATE + SPEC + update .STATUS + update CLAUDE.md."
      },
      {
        "label": "Minimal (no files)",
        "description": "Skip workflow file creation."
      },
      {
        "label": "Custom",
        "description": "Choose exactly which files to create."
      }
    ]
  }]
}
```

#### Files Created

**ORCHESTRATE file** (`ORCHESTRATE-<name>.md`):

```markdown
# <Name> Orchestration Plan

> **Branch:** `<branch>`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/<project>/<folder>`

## Objective

[Describe the goal of this work]

## Phase Overview

| Phase | Task | Priority | Status |
| ----- | ---- | -------- | ------ |
| 1     |      | High     |        |

## Acceptance Criteria

- [ ] ...

## How to Start

\`\`\`bash
cd <worktree-path>
claude
\`\`\`
```

**SPEC file** (`docs/specs/SPEC-<name>-<date>.md`) — for medium+ scope:

```markdown
# SPEC: <Name>

> **Date:** <YYYY-MM-DD>
> **Branch:** `<branch>`
> **Status:** Draft

## Summary

[1-2 sentence summary]

## Requirements

- ...

## Design

[Architecture decisions, trade-offs]

## Implementation Plan

| Step | Description | Files |
| ---- | ----------- | ----- |
| 1    |             |       |
```

**Main repo updates** — for multi-phase scope only:

- `.STATUS`: Add worktree entry with `status: WIP`
- `CLAUDE.md`: Add row to Active Worktrees table

#### Auto-Setup Flow

```text
create worktree
  → detect scope from branch name
  → AskUserQuestion: confirm scope
  → create ORCHESTRATE file (if medium+)
  → create SPEC file (if release/multi-phase)
  → update .STATUS in main repo (if multi-phase)
  → update CLAUDE.md in main repo (if multi-phase)
  → show summary of created files
```

### move - Move Current Branch to Worktree

**The killer feature!** Moves your current branch (with uncommitted work) to a worktree:

```bash
/craft:git:worktree move
```

**Use case:** You're working on a feature in the main folder but want to move it to a worktree so main folder can stay on `main` branch.

**What it does:**

```bash
project=$(basename $(git rev-parse --show-toplevel))
current_branch=$(git branch --show-current)
folder_name=$(echo $current_branch | tr '/' '-')

# Step 1: Stash uncommitted work (CRITICAL!)
echo "📦 Stashing uncommitted work..."
git stash push --include-untracked -m "WIP before moving to worktree"

# Step 2: Switch main folder to stable branch
echo "🔀 Switching to main branch..."
git checkout main || git checkout master

# Step 3: Create worktree for the feature branch
echo "🌳 Creating worktree..."
mkdir -p ~/.git-worktrees/$project
git worktree add ~/.git-worktrees/$project/$folder_name $current_branch

# Step 4: Go to worktree and restore work
cd ~/.git-worktrees/$project/$folder_name
echo "📦 Restoring stashed work..."
git stash pop

# Step 5: Install dependencies
if [ -f package.json ]; then
    echo "📦 Installing npm dependencies..."
    npm install
elif [ -f pyproject.toml ]; then
    echo "🐍 Setting up Python environment..."
    uv venv && source .venv/bin/activate && uv pip install -e .
fi

echo "✅ Branch moved to worktree!"
```

**Output:**

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
│                                                     │
│ Start Claude Code in the worktree:                  │
│   cd ~/.git-worktrees/scribe/feat-mission-control-hud
│   claude                                            │
╰─────────────────────────────────────────────────────╯
```

### validate - Verify Worktree Environment

Validates that the current working directory matches the expected worktree for the active branch:

```bash
/craft:git:worktree validate
```

**What it checks:**

1. Is CWD inside a git worktree? (`git rev-parse --show-toplevel`)
2. Does the worktree path match `~/.git-worktrees/<project>/<branch>`?
3. Is the branch name consistent with the folder name?
4. Are there file writes targeting outside the worktree?

**Detection logic:**

```bash
# Check if in a worktree
git_dir=$(git rev-parse --git-dir 2>/dev/null)
toplevel=$(git rev-parse --show-toplevel 2>/dev/null)
branch=$(git branch --show-current)
cwd=$(pwd)

is_worktree=false
if [[ "$git_dir" == *".git/worktrees/"* ]]; then
    is_worktree=true
fi

# Check branch-folder consistency
folder_name=$(basename "$cwd")
expected_folder=$(echo "$branch" | tr '/' '-')

# Find main repo
if $is_worktree; then
    main_repo=$(git worktree list | head -1 | awk '{print $1}')
fi
```

**Output (all passing):**

```
┌───────────────────────────────────────────────────────────────┐
│ WORKTREE VALIDATION                                           │
├───────────────────────────────────────────────────────────────┤
│ CWD:       ~/.git-worktrees/craft/feature-auth                │
│ Branch:    feature/auth                                       │
│ Toplevel:  ~/.git-worktrees/craft/feature-auth                │
│ Main repo: ~/projects/dev-tools/craft                         │
├───────────────────────────────────────────────────────────────┤
│ ✅ CWD is inside expected worktree                             │
│ ✅ Branch matches folder name                                  │
│ ✅ No writes detected outside worktree                         │
└───────────────────────────────────────────────────────────────┘
```

**Output (issues found):**

```
┌───────────────────────────────────────────────────────────────┐
│ WORKTREE VALIDATION                                           │
├───────────────────────────────────────────────────────────────┤
│ CWD:       ~/projects/dev-tools/craft                         │
│ Branch:    feature/auth                                       │
│ Toplevel:  ~/projects/dev-tools/craft                         │
│ Main repo: ~/projects/dev-tools/craft                         │
├───────────────────────────────────────────────────────────────┤
│ ⚠️  CWD is the main repo, not the worktree                    │
│ ⚠️  Expected: ~/.git-worktrees/craft/feature-auth              │
│ ✅ Branch matches folder name                                  │
│                                                               │
│ FIX: cd ~/.git-worktrees/craft/feature-auth                   │
└───────────────────────────────────────────────────────────────┘
```

**Note:** This is a read-only action — no confirmation needed, no changes made.

### list - Show All Worktrees

```bash
/craft:git:worktree list
```

**What it does:**

```bash
git worktree list --porcelain | while read line; do
    # Parse and display nicely
done
```

**Output:**

```
╭─ Git Worktrees ─────────────────────────────────────╮
│ Project: scribe                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 📁 ~/projects/dev-tools/scribe                      │
│    Branch: main                                     │
│    Status: clean                                    │
│    Type: Main repository                            │
│                                                     │
│ 🌳 ~/.git-worktrees/scribe/mission-control-hud      │
│    Branch: feat/mission-control-hud                 │
│    Status: 3 uncommitted changes                    │
│    Type: Worktree                                   │
│                                                     │
│ 🌳 ~/.git-worktrees/scribe/wonderful-wilson         │
│    Branch: wonderful-wilson                         │
│    Status: clean                                    │
│    Type: Worktree                                   │
│                                                     │
├─────────────────────────────────────────────────────┤
│ Total: 3 (1 main + 2 worktrees)                     │
╰─────────────────────────────────────────────────────╯
```

### clean - Remove Merged Worktrees

Safely removes worktrees for branches that have been merged:

```bash
/craft:git:worktree clean
```

**What it does:**

```bash
# Find merged branches
merged=$(git branch --merged main | grep -v "main\|master\|\*")

for branch in $merged; do
    # Check if branch has a worktree
    worktree_path=$(git worktree list | grep "$branch" | awk '{print $1}')
    if [ -n "$worktree_path" ]; then
        echo "Remove worktree for merged branch '$branch'? (y/n)"
        # Interactive removal
    fi
done

# Prune broken references
git worktree prune
```

**Output:**

```
╭─ Clean Worktrees ───────────────────────────────────╮
│ Scanning for merged branches with worktrees...      │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Found 2 worktrees for merged branches:              │
│                                                     │
│ ⚠️  feat/old-feature (merged 3 days ago)            │
│     Worktree: ~/.git-worktrees/aiterm/feat-old-...  │
│     [Remove? y/n]                                   │
│                                                     │
│ ⚠️  fix/typo (merged 1 week ago)                    │
│     Worktree: ~/.git-worktrees/aiterm/fix-typo      │
│     [Remove? y/n]                                   │
│                                                     │
├─────────────────────────────────────────────────────┤
│ Also running: git worktree prune                    │
│ ✅ Cleaned up broken references                     │
╰─────────────────────────────────────────────────────╯
```

### install - Install Dependencies

Install dependencies for the current worktree based on project type:

```bash
/craft:git:worktree install
```

**Auto-detection:**

| Project Type | Detection | Install Command |
|--------------|-----------|-----------------|
| Node.js | `package.json` | `npm install` |
| Python (uv) | `pyproject.toml` | `uv venv && uv pip install -e .` |
| Python (pip) | `requirements.txt` | `pip install -r requirements.txt` |
| Rust | `Cargo.toml` | Nothing (global cache) |
| Go | `go.mod` | Nothing (global cache) |
| R | `DESCRIPTION` | Nothing (global library) |
| R (renv) | `renv.lock` | `R -e "renv::restore()"` |

### finish - Complete Feature Workflow

**The AI-assisted workflow!** Runs tests, generates changelog, and creates a PR:

```bash
/craft:git:worktree finish
```

**Use case:** You've completed work on a feature in a worktree and want to:

1. Verify tests pass
2. Document the changes
3. Create a PR for review

**What it does:**

#### Step 1: Run Tests (Auto-Detected)

```bash
# Detect project type and run appropriate tests
if [ -f package.json ]; then
    echo "🧪 Running: npm test"
    npm test
elif [ -f pyproject.toml ] || [ -f setup.py ]; then
    echo "🧪 Running: pytest"
    pytest -v
elif [ -f DESCRIPTION ]; then
    echo "🧪 Running: R CMD check"
    R CMD check . --no-manual
elif [ -f Cargo.toml ]; then
    echo "🧪 Running: cargo test"
    cargo test
elif [ -f go.mod ]; then
    echo "🧪 Running: go test"
    go test ./...
fi
```

#### Step 2: Generate Changelog Entry

```bash
# Get branch info
branch=$(git branch --show-current)
base_branch=$(git merge-base main HEAD)

# Extract commits since branching
commits=$(git log --oneline $base_branch..HEAD)

# Determine change type from branch name
if [[ "$branch" == feat/* ]]; then
    section="### Added"
elif [[ "$branch" == fix/* ]]; then
    section="### Fixed"
elif [[ "$branch" == docs/* ]]; then
    section="### Documentation"
else
    section="### Changed"
fi

# Generate entry (Claude fills in the summary)
echo "
$section
- **$branch**: [AI generates summary from commits]
  - $(echo "$commits" | head -5)
"
```

#### Step 3: Create PR

```bash
# Get target branch (usually dev or main)
target="dev"
if ! git rev-parse --verify dev &>/dev/null; then
    target="main"
fi

# Create PR with AI-generated description
gh pr create \
    --base "$target" \
    --title "[AI generates from branch name + commits]" \
    --body "[AI generates from commit history + changes]"
```

**Output:**

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
│   📝 Entry generated:                               │
│                                                     │
│   ### Added                                         │
│   - **User Authentication**: JWT-based auth system  │
│     with login, logout, and session management.     │
│     Includes password hashing and token refresh.    │
│                                                     │
│   ✏️  Review and edit CHANGELOG.md? [Y/n]           │
│                                                     │
│ Step 3/3: Creating PR                               │
│   🎯 Target: dev                                    │
│   📋 Title: feat: Add user authentication system    │
│   📋 Body: (AI-generated from 7 commits)            │
│                                                     │
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

**Flags (optional):**

```bash
/craft:git:worktree finish --skip-tests    # Skip test step
/craft:git:worktree finish --draft         # Create draft PR
/craft:git:worktree finish --target main   # Target main instead of dev
```

**AI-Generated Content:**

The `finish` action uses Claude to generate:

1. **Changelog entry**: Summarizes commits into a clear, user-facing description
2. **PR title**: Concise title following conventional commit style
3. **PR body**: Structured description with:
   - Summary of changes
   - Key implementation details
   - Testing notes
   - Screenshots (if applicable)

**Example PR Body Generated:**

```markdown
## Summary
Adds JWT-based user authentication with login, logout, and session management.

## Changes
- Add `/auth/login` and `/auth/logout` endpoints
- Implement JWT token generation and validation
- Add password hashing with bcrypt
- Create auth middleware for protected routes
- Add token refresh mechanism

## Testing
- 47 unit tests added for auth module
- Manual testing completed for login flow

## Checklist
- [x] Tests pass
- [x] Changelog updated
- [x] Documentation updated
```

## Shell Aliases (Recommended)

Add these to `~/.zshrc` for quick navigation:

```bash
# General worktree navigation
alias wt='cd ~/.git-worktrees'
alias wtl='git worktree list'

# Project-specific (customize for your projects)
alias aiterm-wt='cd ~/.git-worktrees/aiterm'
alias scribe-hud='cd ~/.git-worktrees/scribe/mission-control-hud'
alias scribe-alt='cd ~/.git-worktrees/scribe/wonderful-wilson'
```

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

## Integration

**Related commands:**

- `/craft:check` - Now detects worktree context
- `/craft:git:sync` - Works in worktrees too
- `/craft:git:clean` - Cleans branches (not worktrees)
- `/craft:git:feature` - Feature branch workflow (start/promote/release)

**aiterm integration:**

- `ait sessions` - Tracks sessions per worktree
- `ait detect` - Identifies worktree context
- `ait feature status` - Rich pipeline visualization

**Workflow summary:**

```
/craft:git:worktree create feat/my-feature   # Start
        ↓
   [do your work]
        ↓
/craft:git:worktree finish                   # Complete: tests → changelog → PR
        ↓
/craft:git:worktree clean                    # Cleanup after merge
```

## Dry-Run Mode

Preview what each action will do without executing it:

```bash
# Preview worktree creation
/craft:git:worktree create feature/my-feature --dry-run

# Preview cleanup
/craft:git:worktree clean -n

# Preview setup
/craft:git:worktree setup --dry-run

# Preview finish workflow
/craft:git:worktree finish -n
```

### Example Output: Create

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Create Worktree                                    │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Operations:                                                 │
│   - Create worktree at ~/.git-worktrees/craft/feature-auth    │
│   - Checkout branch: feature/auth                             │
│   - Detect project type: Node.js                              │
│   - Run npm install (auto-detected)                           │
│                                                               │
│ 📊 Summary: 1 worktree to create, auto-install enabled        │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

### Example Output: Clean

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Clean Worktrees                                    │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Worktrees to remove (2):                                    │
│   - ~/.git-worktrees/craft/feature-old (merged to dev)        │
│   - ~/.git-worktrees/craft/fix-bug (merged to main)           │
│                                                               │
│ ⊘ Skip (1):                                                   │
│   - ~/.git-worktrees/craft/feature-wip (not merged)           │
│                                                               │
│ ⚠ Warnings:                                                   │
│   • feature-wip is not merged to any branch                    │
│                                                               │
│ 📊 Summary: 2 worktrees to remove, 1 skipped                   │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

### Supported Actions

| Action | Dry-Run Support | What It Shows |
|--------|----------------|---------------|
| `setup` | ✅ Yes | Directory creation, project detection |
| `create` | ✅ Yes | Worktree path, branch, auto-install plan |
| `move` | ✅ Yes | Source/target paths, branch operations |
| `list` | ⊘ N/A | Read-only (no preview needed) |
| `clean` | ✅ Yes | Worktrees to remove, merge status |
| `install` | ⊘ N/A | Read-only analysis, safe to run |
| `finish` | ✅ Yes | Test commands, changelog, PR details |
| `validate` | ⊘ N/A | Read-only (no preview needed) |

## See Also

- Template: `templates/dry-run-pattern.md`
- Utility: `utils/dry_run_output.py`
- Related: `/craft:git:clean` (branch cleanup)
- Specification: `docs/specs/_archive/SPEC-dry-run-feature-2026-01-15.md`
