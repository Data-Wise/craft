---
description: Initialize git repository with craft workflow patterns
arguments:
  - name: remote
    description: GitHub repository (user/repo or full URL)
    required: false
  - name: workflow
    description: Workflow pattern (main-dev|simple|gitflow)
    required: false
    default: main-dev
  - name: dry-run
    description: Preview changes without executing
    required: false
    default: false
  - name: yes
    description: Skip interactive prompts, use defaults
    required: false
    default: false
---

# /craft:git:init - Initialize Repository

Bootstrap a new git repository with craft workflow patterns.

## Quick Start

```bash
# Interactive wizard (recommended)
/craft:git:init

# Preview without executing
/craft:git:init --dry-run

# Specify remote upfront
/craft:git:init --remote user/repo

# Use defaults, skip prompts
/craft:git:init --yes --remote user/repo
```

## What It Does

The command guides you through an interactive wizard to:

1. **Initialize Git** - Create repository if needed
2. **Create branches** - Set up main + dev workflow
3. **Configure remote** - Connect or create GitHub repo
4. **Enable protection** - Protect main branch (PR + CI required)
5. **Generate CI** - Auto-detect and create workflow
6. **Add project files** - .STATUS, CLAUDE.md, PR template
7. **Initial commit** - Commit setup with conventional message
8. **Push to GitHub** - Sync branches to remote
9. **Validate setup** - Run /craft:check

## Workflow Patterns

### Main + Dev (Default)

```
main (protected) ← PR only, never direct commits
  ↑
dev (integration) ← Start here, plan here, branch from here
  ↑
feature/* (worktrees) ← All implementation work
```

**When to use:** Most projects, especially collaborative work
**Branch protection:** Enabled on main by default
**Start work from:** `git checkout dev`

### Simple

```
main ← Direct commits allowed
```

**When to use:** Personal experiments, quick prototypes
**Branch protection:** Optional
**Start work from:** `git checkout main`

### GitFlow

```
main (protected) ← Production releases
  ↑
release/* ← Release preparation
  ↑
develop ← Integration branch
  ↑
feature/* ← Feature development
```

**When to use:** Complex release management
**Branch protection:** main + develop
**Start work from:** `git checkout develop`

## Interactive Wizard

### Step 1: Repository Check

If `.git` exists:

```
AskUserQuestion: "Git repo exists. What would you like to do?"
  ○ Add dev branch + branch protection
  ○ Fix/sync dev with main
  ○ Full re-init (requires --force)
  ○ Cancel
```

### Step 2: Remote Setup

```
AskUserQuestion: "Where should the repository live?"
  ○ Local only (no remote)
  ○ Connect to existing GitHub repo
  ○ Create new GitHub repo (gh repo create)
```

If creating new repo:

```
AskUserQuestion: "Repository visibility?"
  ○ Public
  ○ Private (Recommended for new projects)

[Text input: Repository description]

AskUserQuestion: "Add repository topics?" (multi-select)
  □ claude-plugin
  □ cli-tool
  □ python
  □ typescript
  □ [Other options based on project detection]
```

### Step 3: Branch Structure

```
Workflow: main + dev
  ✓ Creating main branch...
  ✓ Creating dev branch...
  ✓ Setting dev as default for new work...
```

### Step 4: Branch Protection

```
AskUserQuestion: "Enable branch protection on main?"
  ○ Yes (Recommended) - Requires PR + CI
  ○ No - Allow direct commits
```

If enabled:
- ✅ Require pull requests before merge
- ✅ Require status checks (CI must pass)
- ✅ Block force pushes
- ✅ Allow admin bypass (emergency fixes)

### Step 5: CI Workflow

```
AskUserQuestion: "Generate CI workflow?"
  ○ Yes (Recommended) - Auto-detect project type
  ○ Skip - Add CI manually later
```

If yes, runs `/craft:ci:detect` then:

```
AskUserQuestion: "Which CI template?"
  ○ [Detected type] (Recommended)
  ○ Claude Code Plugin validation
  ○ Python (UV/Poetry/Pip)
  ○ Node.js
  ○ Rust
  ○ Go
```

Generates `.github/workflows/ci.yml` based on selection.

### Step 6: Project Files

```
AskUserQuestion: "Create project tracking files?" (multi-select)
  □ .STATUS (minimal template)
  □ CLAUDE.md (craft-style)
  □ .github/pull_request_template.md
```

Templates:

**`.STATUS`:**
```yaml
status: Initial Setup
version: 0.1.0-dev
progress: 0%

next: Begin feature development
target: First release

install: See README.md
docs: https://github.com/user/repo
repo: https://github.com/user/repo
```

**`CLAUDE.md`:**
- Craft workflow pattern
- Git constraints
- Quick commands
- Project structure

**PR Template:**
- Summary section
- Test plan
- Breaking changes checklist
- Claude Code footer

### Step 7: Initial Commit

```
AskUserQuestion: "Create initial commit?"
  ○ Yes - Commit setup files
  ○ No - Leave staged
```

If yes:
```bash
git add -A
git commit -m "chore: initialize repository with craft workflow

- Set up main + dev branch structure
- Configure branch protection on main
- Add CI workflow (auto-detected)
- Add project tracking (.STATUS, CLAUDE.md)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Step 8: Push to Remote

If remote configured:

```
AskUserQuestion: "Push to GitHub?"
  ○ Yes - Push main + dev branches
  ○ No - Keep local only
```

### Step 9: Validation

```
AskUserQuestion: "Run /craft:check to validate setup?"
  ○ Yes (Recommended)
  ○ Skip
```

Validates:
- Git structure
- Branch protection
- CI workflow
- Project files

## Dry-Run Mode

Preview changes without executing:

```bash
/craft:git:init --dry-run
```

Output:

```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Git Repository Initialization                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ The following changes would be made:                        │
│                                                             │
│ ✓ Git Repository                                            │
│   - Initialize: git init                                    │
│   - Create branch: main                                     │
│   - Create branch: dev                                      │
│                                                             │
│ ✓ Remote                                                    │
│   - Create repo: gh repo create user/repo --private         │
│   - Add remote: git remote add origin ...                   │
│   - Topics: claude-plugin, cli-tool                         │
│                                                             │
│ ✓ Branch Protection                                         │
│   - Protect main: require PR + CI                           │
│   - Allow admin bypass: yes                                 │
│                                                             │
│ ✓ CI Workflow                                               │
│   - Generate: .github/workflows/ci.yml (Python UV)          │
│                                                             │
│ ✓ Project Files                                             │
│   - .STATUS (minimal template)                              │
│   - CLAUDE.md (craft pattern)                               │
│   - .github/pull_request_template.md                        │
│                                                             │
│ ✓ Initial Commit                                            │
│   - Message: "chore: initialize repository..."             │
│   - Files: 4 files staged                                   │
│                                                             │
│ ✓ Push to Remote                                            │
│   - Push main + dev to origin                               │
│                                                             │
│ ✓ Validation                                                │
│   - Run /craft:check                                        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                            │
└─────────────────────────────────────────────────────────────┘
```

## Error Handling

The command uses **rollback-on-error** strategy:

| Step | Rollback Action |
|------|-----------------|
| Git init | Remove `.git/` directory |
| Branch creation | Delete created branches |
| Remote add | Remove remote configuration |
| GitHub repo | Offer to delete repo (with confirmation) |
| Branch protection | Disable protection rules |
| File creation | Delete created files |
| Commits | Reset to pre-init state |

If any step fails:
1. Show error message with context
2. Automatically rollback completed steps
3. Leave repository in original state
4. Suggest fixes or alternatives

## Integration

### Smart Routing

`/craft:do` recognizes these phrases:
- "initialize project"
- "set up git"
- "create repository"
- "bootstrap project"
- "new project setup"

### Related Commands

- `/craft:git:worktree` - Create feature branch worktree
- `/craft:git:branch` - Branch operations
- `/craft:git:clean` - Clean up merged branches
- `/craft:ci:generate` - Generate CI workflow
- `/craft:check` - Validate project structure

## Examples

### Example 1: New Project

```bash
# Start interactive wizard
/craft:git:init

# Wizard flow:
1. No .git found → Initialize new repo
2. "Create new GitHub repo" → user/my-project
3. "Private" visibility
4. main + dev branches created
5. Branch protection enabled
6. CI workflow generated (Python detected)
7. .STATUS, CLAUDE.md created
8. Initial commit created
9. Pushed to GitHub
10. Validation passed

✅ Repository initialized successfully!
```

### Example 2: Existing Repo (Fix)

```bash
# Existing repo without dev branch
/craft:git:init

# Wizard flow:
1. .git exists → "What would you like to do?"
2. Select "Add dev branch + branch protection"
3. dev branch created from main
4. Branch protection enabled on main
5. Optional: Add .STATUS, CLAUDE.md

✅ Repository updated with craft workflow!
```

### Example 3: Quick Setup

```bash
# Skip prompts, use defaults
/craft:git:init --yes --remote user/repo

# Executes:
- Initialize git
- Create main + dev
- Add remote
- Enable branch protection
- Generate CI (auto-detect)
- Create all project files
- Commit and push

✅ Done in 15 seconds!
```

### Example 4: Preview Only

```bash
# See what would happen
/craft:git:init --dry-run

# Shows:
- All steps that would be executed
- Files that would be created
- Settings that would be configured
- Commands that would run

# No changes made
```

## Tips

- **Always start from dev**: After init, `git checkout dev` before creating features
- **Use worktrees**: `/craft:git:worktree feature/name` for isolated work
- **Enable protection**: Protects against accidental main commits
- **Run check**: `/craft:check` validates your setup
- **Customize templates**: Edit `.claude/templates/` for your team's standards

## Troubleshooting

### gh CLI not found

```bash
# Install GitHub CLI
brew install gh

# Authenticate
gh auth login
```

### Branch protection fails

- Check you have admin access to the repository
- Verify CI workflow name matches protection rules
- Use `--no-protect` flag to skip protection setup

### CI workflow generation skipped

- Run manually: `/craft:ci:generate`
- Check project has detectable structure (pyproject.toml, package.json, etc.)
- Specify template explicitly: `/craft:ci:generate python`

### Initial commit fails

- Check for uncommitted changes: `git status`
- Stash changes first: `git stash`
- Run with clean working directory

---

**See Also:**
- [Git Workflow Guide](../docs/workflows/git-feature-workflow.md)
- [Branch Protection](../docs/workflows/pre-commit-workflow.md)
- [CI/CD Setup](ci/generate.md)
