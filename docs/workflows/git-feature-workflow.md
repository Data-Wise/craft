# Git Feature Development Workflow

> **Scenario:** Developing a new feature with proper isolation using worktrees and PR workflow
> **Time:** 15-30 minutes
> **Difficulty:** 🔧 Medium

---

## When to Use This Workflow

Use this workflow when you need to:

- Add a new feature to the codebase
- Work on isolated changes without affecting dev
- Collaborate via pull requests
- Work on multiple features simultaneously

**Example scenarios:**

- "I need to add user authentication"
- "Working on feature X while fixing bug Y"
- "Starting a new increment of work"

---

## Prerequisites

Before starting, ensure you have:

- [x] Git configured with remote
- [x] On `dev` branch and up to date
- [x] Worktree folder created (`/craft:git:worktree setup`)

**Quick check:**

```bash
git branch --show-current  # Should be: dev
git status                 # Should be: clean
git fetch origin dev && git log HEAD..origin/dev --oneline  # Should be empty
```

---

## Basic Workflow

```mermaid
flowchart LR
    A[1. Plan on dev] --> B[2. Create worktree]
    B --> C[3. Implement]
    C --> D[4. Test & validate]
    D --> E[5. Create PR]
    E --> F[6. Cleanup]
```

### Step 1: Plan on dev

Analyze requirements and get approval before coding.

```bash
# Ensure you're on dev and up to date
git checkout dev
git pull origin dev

# Analyze, plan, discuss
# Do NOT write feature code here
```

**Key rule:** Never write feature code directly on `dev`.

### Step 2: Create Worktree

Create an isolated workspace for your feature.

```bash
# Using Craft command (recommended)
/craft:git:worktree create feature/my-feature

# This does:
# 1. Creates ~/.git-worktrees/project/my-feature
# 2. Creates branch feature/my-feature from dev
# 3. Checks out the branch in the worktree

# Navigate to worktree
cd ~/.git-worktrees/craft/my-feature
```

**Output:**

```
╭─ Worktree Created ─────────────────────────────────────╮
│ Branch: feature/my-feature                             │
│ Location: ~/.git-worktrees/craft/my-feature            │
│ Based on: dev                                          │
├────────────────────────────────────────────────────────┤
│ Next: cd ~/.git-worktrees/craft/my-feature             │
╰────────────────────────────────────────────────────────╯
```

### Step 3: Implement with Atomic Commits

Write code with small, focused commits.

```bash
# Use Conventional Commits
git commit -m "feat: add user model"
git commit -m "feat: add auth endpoints"
git commit -m "test: add auth tests"
git commit -m "docs: add auth documentation"
```

**Commit types:**

| Prefix | Use for |
|--------|---------|
| `feat:` | New features |
| `fix:` | Bug fixes |
| `refactor:` | Code changes that don't add features or fix bugs |
| `test:` | Adding or updating tests |
| `docs:` | Documentation only |
| `chore:` | Maintenance tasks |

### Step 4: Test & Validate

Run checks before creating PR.

```bash
# Run pre-flight check
/craft:check --for pr

# Or manually:
python3 tests/test_craft_plugin.py  # Tests
./scripts/validate-counts.sh         # Validation

# Rebase onto latest dev
git fetch origin dev
git rebase origin/dev
```

### Step 5: Create PR

Push and create pull request.

```bash
# Push branch
git push -u origin feature/my-feature

# Create PR to dev
gh pr create --base dev --title "feat: add authentication" --body "## Summary
- Add user model and auth endpoints
- Add tests and documentation

## Test plan
- [x] All tests pass
- [x] Manual testing completed
"
```

### Step 6: Cleanup

After PR is merged, clean up the worktree.

```bash
# Remove worktree
git worktree remove ~/.git-worktrees/craft/my-feature

# Delete local branch
git branch -d feature/my-feature

# Or use Craft command to clean all merged branches
/craft:git:clean
```

---

## Variations

### Hotfix (from main)

For urgent fixes that need to go directly to production:

```bash
# Create hotfix from main
git checkout main
/craft:git:worktree create hotfix/critical-fix

# Fix, test, PR to main
cd ~/.git-worktrees/craft/critical-fix
# ... make fix ...
/craft:check --for pr
gh pr create --base main --title "fix: critical issue"

# After merge, cherry-pick to dev if needed
git checkout dev
git cherry-pick <commit-hash>
```

### Quick Fix (no worktree)

For trivial fixes that don't need isolation:

```bash
# Stay on dev, make small fix
git checkout dev
git checkout -b fix/typo
# ... fix ...
git commit -m "fix: typo in README"
git push -u origin fix/typo
gh pr create --base dev
```

### Release (dev → main)

When ready to release:

```bash
# Create release PR
git checkout dev
gh pr create --base main --head dev --title "Release v1.20.0"

# After merge, tag the release
git checkout main
git pull
git tag v1.20.0
git push --tags
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

---

## Quick Reference

| Action | Command |
|--------|---------|
| Setup worktrees | `/craft:git:worktree setup` |
| Create worktree | `/craft:git:worktree create feature/name` |
| List worktrees | `git worktree list` |
| Clean merged | `/craft:git:clean` |
| Pre-PR check | `/craft:check --for pr` |
| Create PR | `gh pr create --base dev` |
| Remove worktree | `git worktree remove <path>` |

---

## See Also

- **Help:** [/craft:git:worktree](../commands/git/worktree.md)
- **Help:** [/craft:check](../commands/check.md)
