# /craft:git:init - Complete Command Reference

**Status:** Production Ready
**Version:** 1.0
**Category:** Git Workflow
**Added:** v1.19.0

## Overview

Initialize a git repository with craft workflow patterns through an interactive wizard that handles repository setup, branch protection, CI configuration, and project file generation.

## Command Signature

```bash
/craft:git:init [OPTIONS]
```

## Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--remote` | string | No | - | GitHub repository (user/repo or full URL) |
| `--workflow` | enum | No | `main-dev` | Workflow pattern: `main-dev`, `simple`, or `gitflow` |
| `--dry-run` | boolean | No | `false` | Preview changes without executing |
| `--yes` | boolean | No | `false` | Skip interactive prompts, use defaults |

## Usage Examples

### Basic Usage

```bash
# Interactive wizard (recommended for first-time use)
/craft:git:init

# Preview what will happen without making changes
/craft:git:init --dry-run

# Specify GitHub remote upfront
/craft:git:init --remote user/repo

# Non-interactive with defaults
/craft:git:init --yes --remote user/repo

# Use simple workflow instead of main+dev
/craft:git:init --workflow simple
```

### Advanced Usage

```bash
# Dry-run with specific workflow
/craft:git:init --workflow gitflow --dry-run

# Quick setup for existing repo
/craft:git:init --remote myuser/myrepo --yes

# Local-only setup (no GitHub)
# (wizard will prompt for remote options)
/craft:git:init
```

## Workflow Patterns

### Pattern 1: Main + Dev (Default)

**Best For:** Most collaborative projects, production software

```
main (protected) ← PR only, never direct commits
  ↑
dev (integration) ← Start here, plan here, branch from here
  ↑
feature/* (worktrees) ← All implementation work
```

**Characteristics:**

- Main branch is protected (requires PR + CI)
- Dev branch for integration and planning
- Feature branches for isolated development
- Clear separation between production and development

**Branch Protection Settings:**

- ✅ Require pull requests before merge
- ✅ Require status checks (CI must pass)
- ✅ Block force pushes
- ✅ Allow admin bypass (emergency fixes)

### Pattern 2: Simple

**Best For:** Personal projects, experiments, quick prototypes

```
main ← Direct commits allowed
```

**Characteristics:**

- Single main branch
- Direct commits permitted
- Optional branch protection
- Minimal overhead

**Branch Protection Settings:**

- ⚠️ Optional (user decides)
- Can enable PR requirements later
- Suitable for solo development

### Pattern 3: GitFlow

**Best For:** Complex release management, versioned software

```
main (protected) ← Production releases
  ↑
release/* ← Release preparation
  ↑
develop ← Integration branch
  ↑
feature/* ← Feature development
```

**Characteristics:**

- Dedicated release branches
- Strict version management
- Multiple protected branches (main + develop)
- Release candidate workflow

**Branch Protection Settings:**

- ✅ Main and develop protected
- ✅ Release branches follow naming convention
- ✅ Hotfix workflow supported

## Interactive Wizard Flow

The command guides you through 9 steps:

### Step 1: Repository Check

**If `.git` exists:**

```
Question: "Git repo exists. What would you like to do?"
Options:
  ○ Add dev branch + branch protection
  ○ Fix/sync dev with main
  ○ Full re-init (requires --force)
  ○ Cancel
```

**If `.git` does not exist:**

- Automatically initializes new repository
- Proceeds to Step 2

### Step 2: Remote Setup

```
Question: "Where should the repository live?"
Options:
  ○ Local only (no remote)
  ○ Connect to existing GitHub repo
  ○ Create new GitHub repo (gh repo create)
```

**If creating new repo:**

```
Question: "Repository visibility?"
Options:
  ○ Public
  ○ Private (Recommended for new projects)

Input: Repository description (text)

Question: "Add repository topics?" (multi-select)
Options:
  □ claude-plugin
  □ cli-tool
  □ python
  □ typescript
  □ [Auto-detected options based on project]
```

### Step 3: Branch Structure

```
Status: Creating branch structure...
  ✓ Creating main branch...
  ✓ Creating dev branch...
  ✓ Setting dev as default for new work...
```

**Workflow-specific branches:**

- Main+Dev: `main`, `dev`
- Simple: `main`
- GitFlow: `main`, `develop`

### Step 4: Branch Protection

```
Question: "Enable branch protection on main?"
Options:
  ○ Yes (Recommended) - Requires PR + CI
  ○ No - Allow direct commits
```

**If enabled, configures:**

- Require pull requests before merge
- Require status checks to pass
- Block force pushes
- Allow admin bypass for emergencies

### Step 5: CI Workflow

```
Question: "Generate CI workflow?"
Options:
  ○ Yes (Recommended) - Auto-detect project type
  ○ Skip - Add CI manually later
```

**If yes, detects project type:**

```
Question: "Which CI template?"
Options:
  ○ [Auto-detected type] (Recommended)
  ○ Claude Code Plugin validation
  ○ Python (UV/Poetry/Pip)
  ○ Node.js
  ○ Rust
  ○ Go
```

**Generated file:** `.github/workflows/ci.yml`

### Step 6: Project Files

```
Question: "Create project tracking files?" (multi-select)
Options:
  □ .STATUS (minimal template)
  □ CLAUDE.md (craft-style)
  □ .github/pull_request_template.md
```

**Template files created:**

- `.STATUS` - Project status YAML
- `CLAUDE.md` - Workflow documentation
- `.github/pull_request_template.md` - PR template

### Step 7: Initial Commit

```
Question: "Create initial commit?"
Options:
  ○ Yes - Commit setup files
  ○ No - Leave staged
```

**If yes, creates commit:**

```
chore: initialize repository with craft workflow

- Set up main + dev branch structure
- Configure branch protection on main
- Add CI workflow (auto-detected)
- Add project tracking (.STATUS, CLAUDE.md)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### Step 8: Push to Remote

**If remote configured:**

```
Question: "Push to GitHub?"
Options:
  ○ Yes - Push main + dev branches
  ○ No - Keep local only
```

### Step 9: Validation

```
Question: "Run /craft:check to validate setup?"
Options:
  ○ Yes (Recommended)
  ○ Skip
```

**Validates:**

- Git structure
- Branch protection configuration
- CI workflow syntax
- Project files exist and are valid

## Template Files

### .STATUS Template

```yaml
status: Initial Setup
version: 0.1.0-dev
release_date: TBD
milestone: Project Initialization

progress: 0%

recent:
  - Repository initialized with craft workflow
  - Main + dev branch structure created
  - Branch protection enabled on main

next: Begin feature development
target: First release

install: See README.md
docs: https://github.com/{{USER}}/{{REPO}}
repo: https://github.com/{{USER}}/{{REPO}}
```

**Placeholders:**

- `{{USER}}` - GitHub username
- `{{REPO}}` - Repository name

### CLAUDE.md Template

**Sections included:**

- TL;DR with key workflow rules
- Git workflow diagram
- Workflow steps table
- Constraints (never commit to main)
- Quick commands table
- Project structure
- Troubleshooting guide

**Placeholders:**

- `{{PROJECT_NAME}}` - Project display name
- `{{USER}}` - GitHub username
- `{{REPO}}` - Repository name

### PR Template

**Sections included:**

- Summary with change list
- Test plan checklist
- Breaking changes section
- Documentation checklist
- General checklist (style, review, tests)
- Screenshots placeholder

## Dry-Run Mode

Preview all changes without executing:

```bash
/craft:git:init --dry-run
```

**Output format:**

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

### Rollback-on-Error Strategy

If any step fails, the command automatically rolls back completed steps:

| Failed Step | Rollback Actions |
|-------------|------------------|
| Git init | Remove `.git/` directory |
| Branch creation | Delete created branches |
| Remote add | Remove remote configuration |
| GitHub repo creation | Offer to delete repo (with confirmation) |
| Branch protection | Disable protection rules |
| File creation | Delete created files |
| Commits | Reset to pre-init state |

### Common Errors

#### gh CLI not found

**Error:**

```
Error: gh command not found
```

**Solution:**

```bash
# macOS
brew install gh

# Authenticate
gh auth login
```

#### Branch protection fails

**Error:**

```
Error: Failed to enable branch protection
Permission denied
```

**Solutions:**

1. Verify you have admin access to the repository
2. Check if repository exists on GitHub
3. Ensure CI workflow name matches protection rules
4. Use `--skip-protect` flag to skip protection setup

#### CI workflow generation skipped

**Reason:** Project type not detected

**Solutions:**

1. Run manually: `/craft:ci:generate`
2. Check for detectable project files:
   - `pyproject.toml` (Python)
   - `package.json` (Node.js)
   - `Cargo.toml` (Rust)
   - `go.mod` (Go)
3. Specify template explicitly: `/craft:ci:generate python`

#### Initial commit fails

**Error:**

```
Error: Cannot create commit
Uncommitted changes exist
```

**Solution:**

```bash
# Check status
git status

# Stash changes
git stash

# Re-run command
/craft:git:init
```

## Integration

### Smart Routing via /craft:do

The command is accessible through `/craft:do` with these phrases:

| Phrase | Result |
|--------|--------|
| "initialize project" | Runs `/craft:git:init` |
| "set up git" | Runs `/craft:git:init` |
| "create repository" | Runs `/craft:git:init` |
| "bootstrap project" | Runs `/craft:git:init` |
| "new project setup" | Runs `/craft:git:init` |

**Example:**

```bash
/craft:do "initialize project with GitHub"
# → Triggers /craft:git:init wizard
```

### Related Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/craft:git:worktree` | Create feature branch worktree | After init, for feature development |
| `/craft:git:branch` | Branch operations | Manage branches post-init |
| `/craft:git:clean` | Clean up merged branches | Periodic maintenance |
| `/craft:ci:generate` | Generate CI workflow | If skipped during init |
| `/craft:check` | Validate project structure | After init, before commits |

## Requirements

### System Dependencies

- **Git** 2.23+ (for worktree support)
- **GitHub CLI** (`gh`) - Optional, for GitHub integration
- **Python** 3.8+ - For CI template generation (optional)

### Permissions

- **Local:** Write access to directory
- **GitHub:** Admin access to repository (for branch protection)

## Best Practices

### When to Use Each Workflow

| Scenario | Recommended Workflow |
|----------|---------------------|
| Team collaboration | Main + Dev |
| Open source project | Main + Dev |
| Personal experiment | Simple |
| Quick prototype | Simple |
| Production software | Main + Dev or GitFlow |
| Versioned releases | GitFlow |
| Continuous deployment | Main + Dev |

### After Initialization

1. **Switch to dev branch:**

   ```bash
   git checkout dev
   ```

2. **Create first feature branch:**

   ```bash
   /craft:git:worktree feature/initial-setup
   ```

3. **Validate setup:**

   ```bash
   /craft:check
   ```

4. **Start development:**
   - Work on feature branches
   - Create PRs to dev
   - Merge dev to main for releases

### Branch Protection Benefits

- **Prevents accidents:** No direct commits to main
- **Enforces review:** All changes via PR
- **Ensures quality:** CI must pass
- **Maintains history:** Clean, linear history
- **Team coordination:** Clear integration points

## Troubleshooting

### Issue: "Repository already exists"

**Symptom:** Error when creating GitHub repository

**Solutions:**

1. Use "Connect to existing GitHub repo" option instead
2. Choose different repository name
3. Delete existing repository first (if intended)

### Issue: "Dev branch conflicts with main"

**Symptom:** Cannot sync dev with main

**Solution:**

```bash
# Reset dev to match main
git checkout dev
git reset --hard main
git push --force origin dev
```

### Issue: "Branch protection not working"

**Symptom:** Can still commit directly to main

**Checks:**

1. Verify on GitHub: Settings → Branches → Branch protection rules
2. Check CI workflow exists: `.github/workflows/ci.yml`
3. Ensure you're not an admin (admins bypass by default)

### Issue: "gh auth issues"

**Symptom:** Cannot create repository or enable protection

**Solution:**

```bash
# Re-authenticate with GitHub
gh auth logout
gh auth login

# Check authentication status
gh auth status
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User cancelled |
| 2 | Git error |
| 3 | GitHub error |
| 4 | CI generation error |
| 5 | File creation error |
| 6 | Validation failed |

## Performance

| Operation | Typical Duration |
|-----------|------------------|
| Local init only | 2-5 seconds |
| With GitHub repo | 5-15 seconds |
| With branch protection | 15-30 seconds |
| Full setup with CI | 30-60 seconds |

**Note:** Duration depends on network speed and GitHub API response times.

## Security Considerations

### Safe Defaults

- Branch protection enabled by default
- Private repositories recommended
- No sensitive data in templates
- Admin bypass available for emergencies

### Credential Handling

- Uses `gh` CLI for GitHub authentication
- No passwords stored in command
- OAuth tokens managed by GitHub CLI
- Repository access follows GitHub permissions

## See Also

- [Git Workflow Guide](../workflows/git-feature-workflow.md)
- [Branch Protection Guide](../workflows/pre-commit-workflow.md)
- [CI/CD Setup](../commands/ci/generate.md)
- [Getting Started Guide](../guide/getting-started.md)

---

**Command Version:** 1.0
**Last Updated:** 2025-01-15
**Maintainer:** craft plugin team
