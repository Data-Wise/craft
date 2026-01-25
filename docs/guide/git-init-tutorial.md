# Tutorial: Initialize Your Project with /craft:git:init

⏱️ **15 minutes** • 🟢 Beginner Friendly • ✓ Step-by-step

> **TL;DR** (30 seconds)
>
> - **What:** Interactive wizard to set up git repository with best practices
> - **Why:** Automates branch structure, protection, CI, and project files
> - **How:** Run `/craft:git:init` and answer prompts
> - **Next:** Start developing on feature branches with `/craft:git:worktree`

## What You'll Learn

By the end of this tutorial, you'll know how to:

- ✅ Initialize a git repository with craft workflow
- ✅ Set up GitHub integration and branch protection
- ✅ Generate CI workflows automatically
- ✅ Create project tracking files
- ✅ Choose the right workflow pattern for your project

## Prerequisites

### Required

- **Git** installed (check with `git --version`)
- **Claude Code** with craft plugin installed
- **Basic git knowledge** (commit, branch, push)

### Optional (for GitHub features)

- **GitHub CLI** (`gh`) - [Installation guide](https://cli.github.com/)
- **GitHub account** with repository access

## Tutorial Path

Choose your starting point:

| Scenario | Jump To |
|----------|---------|
| 🆕 Brand new project, no code yet | [Section 1](#section-1-brand-new-project) |
| 📁 Have code but no git yet | [Section 2](#section-2-existing-code-no-git) |
| 🔧 Have git, want craft workflow | [Section 3](#section-3-existing-repository) |
| 👀 Just want to see what happens | [Section 4](#section-4-dry-run-preview) |

---

## Section 1: Brand New Project

**Starting point:** Empty directory, no code yet

### Step 1.1: Create Project Directory

```bash
# Create and enter your project directory
mkdir my-awesome-project
cd my-awesome-project
```

### Step 1.2: Run the Wizard

```bash
/craft:git:init
```

You'll see:

```
🔍 Checking for existing repository...
   No .git found - initializing new repository
```

### Step 1.3: Configure GitHub Remote

```
Question: "Where should the repository live?"
Options:
  ○ Local only (no remote)
  ● Create new GitHub repo (gh repo create)  ← Select this
  ○ Connect to existing GitHub repo
```

**Select:** "Create new GitHub repo"

### Step 1.4: Repository Settings

```
Question: "Repository visibility?"
Options:
  ○ Public
  ● Private (Recommended for new projects)  ← Select this
```

**Enter description:**

```
Description: My awesome new project
```

**Select topics** (optional):

```
Question: "Add repository topics?" (multi-select)
Options:
  □ python
  □ typescript
  □ cli-tool
  □ [space to select, enter to continue]
```

### Step 1.5: Choose Workflow Pattern

```
Workflow: main + dev
  ✓ Creating main branch...
  ✓ Creating dev branch...
  ✓ Setting dev as default for new work...
```

**Workflow selected:** main-dev (default, recommended)

### Step 1.6: Enable Branch Protection

```
Question: "Enable branch protection on main?"
Options:
  ● Yes (Recommended) - Requires PR + CI  ← Select this
  ○ No - Allow direct commits
```

**Result:**

```
  ✓ Branch protection enabled on main
  - Require pull requests before merge
  - Require status checks to pass
  - Block force pushes
```

### Step 1.7: Generate CI Workflow

```
Question: "Generate CI workflow?"
Options:
  ● Yes (Recommended) - Auto-detect project type  ← Select this
  ○ Skip - Add CI manually later
```

**Auto-detection:**

```
🔍 Detecting project type...
   No project files found yet

Question: "Which CI template?"
Options:
  ○ Python (UV/Poetry/Pip)
  ○ Node.js
  ● Generic (shell commands)  ← Select for new project
```

### Step 1.8: Create Project Files

```
Question: "Create project tracking files?" (multi-select)
Options:
  ☑ .STATUS (minimal template)
  ☑ CLAUDE.md (craft-style)
  ☑ .github/pull_request_template.md
```

**Select all** (recommended)

**Result:**

```
  ✓ Created .STATUS
  ✓ Created CLAUDE.md
  ✓ Created .github/pull_request_template.md
```

### Step 1.9: Initial Commit

```
Question: "Create initial commit?"
Options:
  ● Yes - Commit setup files  ← Select this
  ○ No - Leave staged
```

**Commit created:**

```
[main abc1234] chore: initialize repository with craft workflow
 4 files changed, 127 insertions(+)
 create mode 100644 .STATUS
 create mode 100644 CLAUDE.md
 create mode 100644 .github/pull_request_template.md
 create mode 100644 .github/workflows/ci.yml
```

### Step 1.10: Push to GitHub

```
Question: "Push to GitHub?"
Options:
  ● Yes - Push main + dev branches  ← Select this
  ○ No - Keep local only
```

**Pushing:**

```
  ✓ Pushed main to origin
  ✓ Pushed dev to origin
```

### Step 1.11: Validation

```
Question: "Run /craft:check to validate setup?"
Options:
  ● Yes (Recommended)  ← Select this
  ○ Skip
```

**Validation results:**

```
Running /craft:check...

✓ Git structure valid
✓ Branch protection configured
✓ CI workflow valid
✓ Project files present

All checks passed!
```

### ✅ Success

```
┌─────────────────────────────────────────────────┐
│ ✓ Repository initialized successfully!         │
├─────────────────────────────────────────────────┤
│                                                 │
│ Your project is ready:                          │
│   • Git repository: ✓                           │
│   • GitHub remote: user/my-awesome-project      │
│   • Branch structure: main (protected) + dev    │
│   • CI workflow: .github/workflows/ci.yml       │
│   • Project files: 4 files created              │
│                                                 │
│ Next steps:                                     │
│   1. Switch to dev: git checkout dev            │
│   2. Create feature: /craft:git:worktree feat   │
│   3. Start coding!                              │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Your repository:** `https://github.com/user/my-awesome-project`

---

## Section 2: Existing Code, No Git

**Starting point:** Directory with code, but no `.git` folder

### Step 2.1: Navigate to Project

```bash
cd /path/to/your/existing/project
```

### Step 2.2: Check Current State

```bash
# Verify no git repository exists
ls -la | grep .git
# Should show nothing
```

### Step 2.3: Run Wizard

```bash
/craft:git:init
```

**Detection:**

```
🔍 Checking for existing repository...
   No .git found - initializing new repository

🔍 Detecting project type...
   Found: pyproject.toml → Python project
```

### Step 2.4: Follow Wizard

Same flow as Section 1, but with auto-detected project type:

```
Question: "Which CI template?"
Options:
  ● Python (UV) (Recommended)  ← Auto-selected
  ○ Python (Poetry)
  ○ Python (Pip)
  ○ Generic
```

### Step 2.5: Commit Existing Code

After wizard completes:

```bash
# Check what's staged
git status

# The wizard already committed tracking files
# Now commit your existing code
git add .
git commit -m "feat: add initial project code

Existing codebase with:
- Core functionality
- Initial tests
- Documentation

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push all changes
git push origin main dev
```

---

## Section 3: Existing Repository

**Starting point:** Already have `.git`, want to add craft workflow

### Step 3.1: Check Current State

```bash
# Check current branches
git branch -a

# Check if you have dev branch
git branch | grep dev
```

### Step 3.2: Run Wizard

```bash
/craft:git:init
```

**Detection:**

```
🔍 Checking for existing repository...
   .git found - existing repository detected
```

### Step 3.3: Choose Action

```
Question: "Git repo exists. What would you like to do?"
Options:
  ● Add dev branch + branch protection  ← Select this
  ○ Fix/sync dev with main
  ○ Full re-init (requires --force)
  ○ Cancel
```

### Step 3.4: Add Dev Branch

```
Creating dev branch from main...
  ✓ Created dev branch
  ✓ Pushed to origin
```

### Step 3.5: Enable Protection

Follow steps from Section 1 (Branch Protection onwards)

---

## Section 4: Dry-Run Preview

**Goal:** See what the command will do without making changes

### Step 4.1: Run Dry-Run

```bash
/craft:git:init --dry-run
```

### Step 4.2: Review Preview

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
│                                                             │
│ ✓ Branch Protection                                         │
│   - Protect main: require PR + CI                           │
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
├─────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                            │
└─────────────────────────────────────────────────────────────┘
```

### Step 4.3: Decide

- **Looks good?** Run without `--dry-run`
- **Need changes?** Adjust arguments and try again
- **Not sure?** Review the [Command Reference](../commands/git-init-reference.md)

---

## Common Workflows

### Quick Setup (Non-Interactive)

For experienced users who want defaults:

```bash
/craft:git:init --yes --remote myuser/myrepo
```

This:

- ✅ Uses all default choices
- ✅ Skips interactive prompts
- ✅ Creates GitHub repository
- ✅ Enables branch protection
- ✅ Generates CI workflow
- ✅ Creates all project files
- ✅ Commits and pushes

**Duration:** ~30 seconds

### Local-Only Setup

No GitHub integration:

```bash
/craft:git:init
```

**When prompted for remote:**

```
Select: "Local only (no remote)"
```

**Result:**

- Git repository initialized
- Local branches created
- No branch protection (local only)
- Project files created
- No push step

### Add to Existing Repo

Already have git, want craft workflow:

```bash
/craft:git:init
```

**When prompted:**

```
Select: "Add dev branch + branch protection"
```

---

## After Initialization

### Verify Setup

```bash
# Check branches
git branch -a
# Should see: main, dev, remotes/origin/main, remotes/origin/dev

# Check remote
git remote -v
# Should see: origin https://github.com/user/repo (fetch/push)

# Check protection (on GitHub)
# Visit: https://github.com/user/repo/settings/branches
```

### Start Development

```bash
# 1. Switch to dev branch
git checkout dev

# 2. Create a feature branch
/craft:git:worktree feature/my-first-feature

# 3. Start coding!
cd ../my-awesome-project-feature-my-first-feature

# 4. Make changes
echo "# My Project" > README.md
git add README.md
git commit -m "docs: add README"

# 5. Push and create PR
git push origin feature/my-first-feature
gh pr create --base dev --title "Add README" --body "Initial documentation"
```

### Update Documentation

```bash
# Update .STATUS as you make progress
# Edit: .STATUS
status: In Development  # was: Initial Setup
progress: 15%           # was: 0%
next: Implement core features  # was: Begin feature development
```

---

## Troubleshooting

### Problem: "gh command not found"

**Solution:**

```bash
# macOS
brew install gh

# Authenticate
gh auth login

# Verify
gh --version
```

### Problem: "Permission denied when enabling branch protection"

**Cause:** You don't have admin access to the repository

**Solutions:**

1. Ask repository owner to grant you admin access
2. Skip branch protection during setup
3. Enable manually later with admin account

### Problem: "Failed to push to origin"

**Cause:** Remote doesn't exist or authentication failed

**Solution:**

```bash
# Check remote exists
gh repo view user/repo

# Check authentication
gh auth status

# Re-authenticate if needed
gh auth logout
gh auth login
```

### Problem: "Project type not detected"

**Cause:** No recognizable project files yet

**Solution:**

1. Select "Generic" CI template during setup
2. Create project files first (package.json, pyproject.toml, etc.)
3. Run `/craft:ci:generate` later to regenerate CI

### Problem: "Cannot create commit - dirty working tree"

**Cause:** Uncommitted changes exist

**Solution:**

```bash
# Option 1: Stash changes
git stash
/craft:git:init
git stash pop

# Option 2: Commit changes first
git add -A
git commit -m "WIP: changes before craft init"
/craft:git:init
```

---

## Tips & Best Practices

### ✅ DO

- **Use main+dev workflow** for team projects
- **Enable branch protection** for production code
- **Run validation** after setup (`/craft:check`)
- **Switch to dev** immediately after init
- **Use feature branches** for all development
- **Keep .STATUS updated** as project progresses

### ❌ DON'T

- **Don't commit directly to main** (branch protection prevents this)
- **Don't skip branch protection** unless solo project
- **Don't forget to push** dev branch to GitHub
- **Don't ignore validation warnings**
- **Don't use simple workflow** for team projects

### 💡 Pro Tips

1. **Preview first:** Always run `--dry-run` before actual init
2. **Document decisions:** The wizard creates CLAUDE.md automatically
3. **CI early:** Enable CI from the start, not later
4. **Status tracking:** Use .STATUS file for project tracking
5. **PR templates:** Customize `.github/pull_request_template.md` for your team

---

## Next Steps

### Immediate (< 5 minutes)

1. ✅ Run `/craft:check` to verify setup
2. ✅ Switch to dev branch: `git checkout dev`
3. ✅ Create first feature: `/craft:git:worktree feature/initial-work`

### Short Term (< 1 hour)

1. 📝 Customize CLAUDE.md with project-specific info
2. 📝 Update .STATUS with current project status
3. 🔧 Add project-specific code to codebase
4. ✅ Create first real commit

### Long Term

1. 🎯 Set up project-specific CI tests
2. 📚 Add comprehensive README
3. 🔐 Configure additional GitHub settings
4. 👥 Invite team members and share workflow

---

## Related Resources

- [Command Reference](../commands/git-init-reference.md) - Complete command documentation
- [Architecture Diagrams](../architecture/git-init-flow.md) - Technical flows
- [Git Workflow Guide](../workflows/git-feature-workflow.md) - Feature development
- [Branch Protection Guide](../workflows/pre-commit-workflow.md) - Protection best practices

---

**Tutorial Version:** 1.0
**Last Updated:** 2025-01-15
**Difficulty:** 🟢 Beginner Friendly
