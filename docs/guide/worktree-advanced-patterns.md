# Advanced Worktree Orchestration

> **Master complex multi-worktree scenarios** — Learn how to manage 3+ parallel worktrees, coordinate team workflows, and recover from edge cases.

---

## Overview

This guide covers advanced worktree patterns beyond the basics. If you're new to worktrees, start with the [Worktree Setup Tutorial](../tutorials/TUTORIAL-worktree-setup.md).

**What you'll learn:**

- Managing 3+ worktrees simultaneously
- Complex workflows (release + hotfix + feature)
- Advanced git operations (cherry-pick, rebase between worktrees)
- Team collaboration patterns
- Recovery from corrupted worktrees and sync conflicts

---

## Multi-Worktree Management

### Naming Conventions for 3+ Worktrees

When managing multiple worktrees, consistent naming prevents confusion:

**Pattern:** `~/.git-worktrees/<project>/<type>-<name>`

| Type Prefix | Purpose | Example |
|------------|---------|---------|
| `feature-` | New features | `feature-auth`, `feature-payments` |
| `fix-` | Bug fixes | `fix-login-timeout`, `fix-cors-error` |
| `hotfix-` | Urgent production fixes | `hotfix-security-patch` |
| `release-` | Release preparation | `release-v2.9.0` |
| `pr-` | PR reviews | `pr-42-review` |
| `test-` | Experimental work | `test-new-framework` |

**Example directory structure:**

```
~/.git-worktrees/craft/
├── feature-auth-backend/     ← Working on auth backend
├── feature-auth-frontend/    ← Working on auth frontend
├── feature-auth-tests/       ← Writing auth tests
├── hotfix-cors-error/        ← Urgent fix
└── pr-42-review/             ← Reviewing teammate's PR
```

### Dependency Coordination Patterns

**Scenario:** Three related features being developed in parallel

```bash
# Feature 1: Backend API
cd ~/.git-worktrees/craft/feature-auth-backend
git checkout -b feature/auth-backend
# Implement /auth/login, /auth/logout endpoints

# Feature 2: Frontend UI (depends on Feature 1)
cd ~/.git-worktrees/craft/feature-auth-frontend
git checkout -b feature/auth-frontend
# Wait for backend endpoints to be defined
# Then implement Login.tsx, Logout.tsx

# Feature 3: Integration tests (depends on both)
cd ~/.git-worktrees/craft/feature-auth-tests
git checkout -b feature/auth-tests
# Wait for both backend and frontend
# Then write end-to-end tests
```

**Coordination strategy:**

1. **Phase 1:** Backend completes first (merge PR #1)
2. **Phase 2:** Frontend develops against backend branch
3. **Phase 3:** Tests develop against both branches
4. **Phase 4:** Merge all to dev in dependency order

**Communication:**

```bash
# Terminal 1 (backend)
echo "Backend API complete" > ~/Desktop/auth-backend-done.txt

# Terminal 2 (frontend) - polls for completion
while [ ! -f ~/Desktop/auth-backend-done.txt ]; do sleep 10; done
echo "Backend ready, starting frontend work..."
```

### Terminal Multiplexing Strategies

**Using iTerm2 (macOS):**

```bash
# Create 3 panes in iTerm2
# Cmd+D (split vertically)
# Cmd+Shift+D (split horizontally)

# Pane 1: Backend worktree
cd ~/.git-worktrees/craft/feature-auth-backend
npm run dev -- --port 3001

# Pane 2: Frontend worktree
cd ~/.git-worktrees/craft/feature-auth-frontend
npm run dev -- --port 3000

# Pane 3: Tests worktree
cd ~/.git-worktrees/craft/feature-auth-tests
npm run test:watch
```

**Using tmux:**

```bash
# Create tmux session with 3 windows
tmux new-session -s craft

# Window 0: Backend
cd ~/.git-worktrees/craft/feature-auth-backend

# Ctrl+B C (create new window)
# Window 1: Frontend
cd ~/.git-worktrees/craft/feature-auth-frontend

# Ctrl+B C
# Window 2: Tests
cd ~/.git-worktrees/craft/feature-auth-tests

# Switch between windows: Ctrl+B 0/1/2
```

---

## Complex Workflows

### Workflow 1: Release + Hotfix + Feature

**Scenario:** You're preparing v2.9.0 release when a critical production bug is reported.

**Initial state:**

```
~/.git-worktrees/craft/
└── release-v2.9.0/          ← Preparing release
```

**Step 1: Create hotfix worktree**

```bash
# Create hotfix from main (production)
cd ~/projects/dev-tools/craft
/craft:git:worktree create hotfix/security-patch --base main
```

**Step 2: Work in parallel**

```bash
# Terminal 1: Continue release testing
cd ~/.git-worktrees/craft/release-v2.9.0
/craft:check thorough --for release

# Terminal 2: Fix critical bug
cd ~/.git-worktrees/craft/hotfix-security-patch
# Fix the security issue
git commit -m "fix: patch XSS vulnerability"
git push origin hotfix/security-patch
gh pr create --base main --head hotfix/security-patch
```

**Step 3: Coordinate merge order**

```bash
# 1. Merge hotfix to main first (urgent)
gh pr merge hotfix/security-patch

# 2. Pull hotfix into release branch
cd ~/.git-worktrees/craft/release-v2.9.0
git fetch origin main
git cherry-pick <hotfix-commit-sha>

# 3. Continue release preparation
/craft:check thorough --for release
```

**Step 4: Clean up**

```bash
# Hotfix merged, remove worktree
cd ~/projects/dev-tools/craft
git worktree remove ~/.git-worktrees/craft/hotfix-security-patch
```

### Workflow 2: Parallel Feature Development

**Scenario:** Building authentication system with backend, frontend, and tests in parallel.

**Setup:**

```bash
# Create 3 worktrees
/craft:git:worktree create feature/auth-backend
/craft:git:worktree create feature/auth-frontend
/craft:git:worktree create feature/auth-tests
```

**Shared dependencies:**

```bash
# Backend: Install once
cd ~/.git-worktrees/craft/feature-auth-backend
npm install  # Creates node_modules/

# Frontend: Symlink to backend's node_modules (saves disk space)
cd ~/.git-worktrees/craft/feature-auth-frontend
ln -s ../feature-auth-backend/node_modules node_modules

# Tests: Also symlink
cd ~/.git-worktrees/craft/feature-auth-tests
ln -s ../feature-auth-backend/node_modules node_modules
```

**Cross-worktree testing:**

```bash
# Terminal 1: Run backend server from backend worktree
cd ~/.git-worktrees/craft/feature-auth-backend
npm run dev -- --port 4000

# Terminal 2: Run frontend from frontend worktree
cd ~/.git-worktrees/craft/feature-auth-frontend
# Configure frontend to hit backend at http://localhost:4000
npm run dev -- --port 3000

# Terminal 3: Run tests from tests worktree
cd ~/.git-worktrees/craft/feature-auth-tests
# Tests hit frontend at http://localhost:3000
npm run test:e2e
```

**Integration strategy:**

```bash
# Merge order (reverse dependency)
# 1. Backend first
cd ~/.git-worktrees/craft/feature-auth-backend
/craft:git:worktree finish  # Creates PR #1

# 2. Frontend second (after backend PR merged)
cd ~/.git-worktrees/craft/feature-auth-frontend
git fetch origin dev
git rebase origin/dev  # Gets backend changes
/craft:git:worktree finish  # Creates PR #2

# 3. Tests last (after both PRs merged)
cd ~/.git-worktrees/craft/feature-auth-tests
git fetch origin dev
git rebase origin/dev  # Gets both backend and frontend changes
/craft:git:worktree finish  # Creates PR #3
```

### Workflow 3: PR Review Without Disruption

**Scenario:** Teammate asks you to review PR #42 while you're mid-feature.

**Without worktrees (painful):**

```bash
# You're working on feature/my-feature
git stash  # Stash 15 files
git checkout dev
git pull origin dev
gh pr checkout 42  # Switch to their branch
# Review code, test locally
git checkout feature/my-feature
git stash pop  # Hope no conflicts!
```

**With worktrees (seamless):**

```bash
# You're working in feature worktree
cd ~/.git-worktrees/craft/feature-my-feature

# Create PR review worktree (separate terminal)
cd ~/projects/dev-tools/craft
/craft:git:worktree create pr/42-review --base dev
gh pr checkout 42 --force  # Checkout PR into worktree

# Review in isolation
cd ~/.git-worktrees/craft/pr-42-review
npm install  # Install their dependencies
npm run dev  # Test their changes
# Leave feedback on PR

# Return to your work (exactly as you left it)
cd ~/.git-worktrees/craft/feature-my-feature
# Your 15 uncommitted files are still here!

# After review complete, remove review worktree
git worktree remove ~/.git-worktrees/craft/pr-42-review
```

---

## Advanced Git Operations

### Cherry-Picking Between Worktrees

**Scenario:** You implemented a fix in `hotfix-bug` but also need it in `feature-my-feature`.

**Step 1: Identify commit SHA**

```bash
cd ~/.git-worktrees/craft/hotfix-bug
git log -1
# commit abc123 (HEAD -> hotfix/bug)
# Author: You
# Date: Today
#
#     fix: resolve timeout issue
```

**Step 2: Cherry-pick into feature branch**

```bash
cd ~/.git-worktrees/craft/feature-my-feature
git cherry-pick abc123

# If conflicts occur:
# Auto-merging src/api.py
# CONFLICT (content): Merge conflict in src/api.py

# Resolve conflicts
code src/api.py  # Fix conflicts manually
git add src/api.py
git cherry-pick --continue
```

**Step 3: Verify**

```bash
git log -1
# commit def456 (HEAD -> feature/my-feature)
# Author: You
# Date: Today
#
#     fix: resolve timeout issue
#     (cherry picked from commit abc123)
```

### Rebase Strategies

#### Interactive Rebase Per Worktree

**Scenario:** Clean up commit history before creating PR.

```bash
cd ~/.git-worktrees/craft/feature-auth
git log --oneline
# abc123 feat: add auth
# def456 wip: debugging
# ghi789 fix: typo
# jkl012 feat: complete auth
# mno345 wip: more debugging

# Interactive rebase to squash "wip" commits
git rebase -i origin/dev

# In editor:
pick abc123 feat: add auth
squash def456 wip: debugging  # Squash into abc123
squash ghi789 fix: typo       # Squash into abc123
pick jkl012 feat: complete auth
squash mno345 wip: more debugging  # Squash into jkl012

# Result: 2 clean commits
# abc123 feat: add auth
# jkl012 feat: complete auth
```

#### Keeping Worktrees Synced with Base

**Scenario:** Long-running feature branch needs updates from dev.

```bash
# Daily sync routine
cd ~/.git-worktrees/craft/feature-long-running

# Fetch latest dev
git fetch origin dev

# Rebase onto latest dev
git rebase origin/dev

# If conflicts:
# CONFLICT (content): Merge conflict in src/app.py

# Resolve and continue
git add src/app.py
git rebase --continue

# Force push (since history changed)
git push origin feature/long-running --force-with-lease
```

### Stash Management

#### Per-Worktree Stashing

**Stashes are per-repository, NOT per-worktree.**

```bash
# Worktree 1: Create stash
cd ~/.git-worktrees/craft/feature-auth
git stash save "auth: WIP login form"

# Worktree 2: See the same stash!
cd ~/.git-worktrees/craft/feature-payments
git stash list
# stash@{0}: On feature/auth: auth: WIP login form

# Apply stash from other worktree (if needed)
git stash apply stash@{0}
```

**Best practice:** Use descriptive stash names with branch prefix.

```bash
# Good: Includes branch name
git stash save "feature/auth: WIP login validation"

# Bad: Unclear which branch
git stash save "WIP changes"
```

#### Moving Stashes Between Worktrees

**Scenario:** Started work in wrong worktree.

```bash
# Wrong worktree: feature-payments
cd ~/.git-worktrees/craft/feature-payments
git stash save "feature/auth: accidental work in wrong worktree"

# Right worktree: feature-auth
cd ~/.git-worktrees/craft/feature-auth
git stash list
# stash@{0}: On feature/payments: feature/auth: accidental work...

# Apply stash
git stash apply stash@{0}

# Drop stash (no longer needed)
git stash drop stash@{0}
```

---

## Team Collaboration Patterns

### Shared Worktree Locations (NFS Considerations)

**Scenario:** Team uses shared NFS mount for worktrees.

**Problem:** NFS locks cause "Text file busy" errors.

**Solution:** Use local worktrees, not shared.

```bash
# Bad: Shared NFS mount
export WORKTREE_DIR="/mnt/nfs/worktrees/craft"

# Good: Local per-user
export WORKTREE_DIR="$HOME/.git-worktrees/craft"
```

**If shared worktrees required:**

```bash
# Use user-specific subdirectories
export WORKTREE_DIR="/mnt/nfs/worktrees/$USER/craft"
```

### Pair Programming with Worktrees

**Scenario:** Two developers working together.

**Setup:**

```bash
# Developer 1 creates worktree
cd ~/projects/dev-tools/craft
/craft:git:worktree create feature/pair-session

cd ~/.git-worktrees/craft/feature-pair-session

# Start tmux session (allow attaching)
tmux new-session -s pair-session

# Developer 2 attaches to same tmux session
ssh dev1-machine
tmux attach-session -t pair-session

# Both see the same terminal, same worktree
```

**Benefits:**

- Both developers work in same environment
- No "wait, let me push my changes" delays
- Instant collaboration

### Code Review Workflows

**Reviewer workflow:**

```bash
# Reviewer creates PR worktree
cd ~/projects/dev-tools/craft
/craft:git:worktree create pr/42-review
cd ~/.git-worktrees/craft/pr-42-review
gh pr checkout 42

# Install dependencies
npm install

# Run tests
npm test

# Run locally
npm run dev

# Leave feedback
gh pr review 42 --comment -b "Looks good, minor suggestion on line 42"

# Clean up
cd ~/projects/dev-tools/craft
git worktree remove ~/.git-worktrees/craft/pr-42-review
```

**Author workflow (responding to feedback):**

```bash
# Author is in feature worktree
cd ~/.git-worktrees/craft/feature-auth

# See reviewer feedback
gh pr view 42

# Make changes
git add .
git commit -m "fix: address review feedback"
git push origin feature/auth

# Reviewer gets notification, can re-review without re-creating worktree
```

### Handoff Procedures

**Scenario:** Developer 1 goes on vacation, Developer 2 takes over.

**Developer 1 (before vacation):**

```bash
# Ensure all work is pushed
cd ~/.git-worktrees/craft/feature-complex
git status
# Should show: nothing to commit, working tree clean

git push origin feature/complex

# Document state
echo "Feature 60% complete. Next: implement payment flow. See ORCHESTRATE-complex.md" > .STATUS.txt
git add .STATUS.txt
git commit -m "docs: update status before handoff"
git push origin feature/complex
```

**Developer 2 (taking over):**

```bash
# Create worktree for same feature
cd ~/projects/dev-tools/craft
/craft:git:worktree create feature/complex --use-existing

cd ~/.git-worktrees/craft/feature-complex

# Read status
cat .STATUS.txt
# "Feature 60% complete. Next: implement payment flow..."

# Continue work
```

---

## Recovery Scenarios

### Corrupted Worktree

**Symptoms:**

- `git status` hangs indefinitely
- `.git` file points to non-existent location
- "Not a git repository" error

**Detection:**

```bash
git worktree list
# /Users/dt/projects/dev-tools/craft        abc123 [main]
# /Users/dt/.git-worktrees/craft/feature-auth  (detached HEAD)  ← Problem!
```

**Recovery:**

```bash
# Step 1: Prune invalid worktrees
git worktree prune

# Step 2: Verify removal
git worktree list
# Should no longer show corrupted worktree

# Step 3: Recreate worktree
/craft:git:worktree create feature/auth --use-existing

# Step 4: Restore work (if .git-worktrees folder still exists)
cd ~/.git-worktrees/craft/feature-auth
git status  # Should now work

# If work lost, recover from reflog
git reflog
# Find lost commit SHA
git cherry-pick <lost-commit-sha>
```

### Sync Conflicts

**Scenario:** Diverged branches across worktrees.

**Problem:**

```bash
# Worktree 1: feature-auth on commit A
cd ~/.git-worktrees/craft/feature-auth
git log -1
# commit aaa111

# Main repo: Same branch on commit B
cd ~/projects/dev-tools/craft
git log feature/auth -1
# commit bbb222
```

**This should never happen** (git prevents it), but if it does:

**Recovery:**

```bash
# Determine which commit is correct
cd ~/.git-worktrees/craft/feature-auth
git log --oneline
# See full history

cd ~/projects/dev-tools/craft
git log feature/auth --oneline
# Compare

# Force align (after backing up)
cd ~/.git-worktrees/craft/feature-auth
git reset --hard origin/feature/auth
```

### Orphaned References

**Scenario:** Worktree removed with `rm -rf` instead of `git worktree remove`.

**Detection:**

```bash
git worktree list
# /Users/dt/.git-worktrees/craft/feature-deleted  abc123 [feature/deleted]  ← Still listed

ls ~/.git-worktrees/craft/feature-deleted
# ls: cannot access '...': No such file or directory  ← But doesn't exist
```

**Recovery:**

```bash
# Prune orphaned references
git worktree prune

# Verify
git worktree list
# Should no longer show deleted worktree

# If branch still needed
git checkout -b feature/deleted abc123  # Recreate from SHA
/craft:git:worktree create feature/deleted --use-existing
```

---

## Performance Optimization

### Dependency Sharing Strategies

**Strategy 1: Symlinks (fastest, but risky)**

```bash
# Install in one worktree
cd ~/.git-worktrees/craft/feature-auth
npm install

# Symlink from others
cd ~/.git-worktrees/craft/feature-payments
ln -s ../feature-auth/node_modules node_modules
```

**Pros:**

- Disk space efficient
- No duplicate installs

**Cons:**

- Dependency conflicts if versions differ
- Breaks if source worktree removed

**Strategy 2: Copy (safest)**

```bash
# Install separately in each
cd ~/.git-worktrees/craft/feature-auth
npm install

cd ~/.git-worktrees/craft/feature-payments
npm install
```

**Pros:**

- No conflicts
- Each worktree independent

**Cons:**

- More disk space
- Slower initial setup

**Strategy 3: Hardlinks (best of both)**

```bash
# Use npm/pnpm with hardlinks
cd ~/.git-worktrees/craft/feature-auth
pnpm install  # pnpm uses content-addressable store

cd ~/.git-worktrees/craft/feature-payments
pnpm install  # Reuses existing packages via hardlinks
```

**Pros:**

- Disk space efficient
- Each worktree independent

**Cons:**

- Requires pnpm

### Build Cache Coordination

**Scenario:** Multiple worktrees building same project.

**Problem:** Each build from scratch (slow).

**Solution:** Shared build cache.

```bash
# Set cache directory (per project)
export BUILD_CACHE_DIR="$HOME/.cache/craft-builds"

# Worktree 1
cd ~/.git-worktrees/craft/feature-auth
npm run build -- --cache-dir "$BUILD_CACHE_DIR"

# Worktree 2 (reuses cache)
cd ~/.git-worktrees/craft/feature-payments
npm run build -- --cache-dir "$BUILD_CACHE_DIR"
```

### Minimizing Disk Usage

**Check disk usage:**

```bash
du -sh ~/.git-worktrees/craft/*
# 450M  feature-auth
# 420M  feature-payments
# 380M  pr-42-review
# Total: 1.25G
```

**Strategies:**

1. **Remove merged worktrees promptly**

```bash
/craft:git:worktree clean  # Auto-removes merged
```

2. **Use shallow clones for PR reviews**

```bash
git worktree add --detach ~/.git-worktrees/craft/pr-review
cd ~/.git-worktrees/craft/pr-review
gh pr checkout 42
```

3. **Compress old worktrees**

```bash
# Archive inactive worktree
cd ~/.git-worktrees/craft
tar -czf feature-old.tar.gz feature-old/
git worktree remove feature-old
```

---

## Monitoring and Maintenance

### Health Check Script

**File:** `~/bin/worktree-health-check.sh`

```bash
#!/bin/bash
# Check health of all worktrees for a project

PROJECT="craft"
WORKTREE_DIR="$HOME/.git-worktrees/$PROJECT"

echo "Checking worktrees for $PROJECT..."

# List all worktrees
git worktree list

# Check for orphaned references
echo -e "\nPruning orphaned references..."
git worktree prune

# Check disk usage
echo -e "\nDisk usage:"
du -sh "$WORKTREE_DIR"/*

# Check for uncommitted changes
echo -e "\nUncommitted changes:"
for wt in "$WORKTREE_DIR"/*; do
  cd "$wt" 2>/dev/null || continue
  if ! git diff-index --quiet HEAD --; then
    echo "  - $(basename "$wt"): $(git status -s | wc -l) uncommitted files"
  fi
done

# Check for unpushed commits
echo -e "\nUnpushed commits:"
for wt in "$WORKTREE_DIR"/*; do
  cd "$wt" 2>/dev/null || continue
  UNPUSHED=$(git log @{u}.. --oneline 2>/dev/null | wc -l)
  if [ "$UNPUSHED" -gt 0 ]; then
    echo "  - $(basename "$wt"): $UNPUSHED unpushed commits"
  fi
done
```

**Usage:**

```bash
chmod +x ~/bin/worktree-health-check.sh
~/bin/worktree-health-check.sh
```

### Automated Cleanup Routine

**Cron job:** Clean up merged worktrees weekly

```bash
# Add to crontab (crontab -e)
0 9 * * 1 cd ~/projects/dev-tools/craft && git worktree prune && /craft:git:worktree clean
# Runs every Monday at 9 AM
```

### Security Considerations

**Problem:** Secrets (API keys, passwords) in multiple worktree locations.

**Solution 1:** Use environment variables

```bash
# Don't commit .env files
# Store once in main repo
cp ~/projects/dev-tools/craft/.env ~/.git-worktrees/craft/feature-auth/
```

**Solution 2:** Symlink .env

```bash
cd ~/.git-worktrees/craft/feature-auth
ln -s ~/projects/dev-tools/craft/.env .env
```

**Solution 3:** Use secret management tool

```bash
# 1Password CLI
op inject -i .env.template -o .env
```

---

## Summary

**Key takeaways:**

1. **Naming conventions** prevent confusion with 3+ worktrees
2. **Dependency coordination** requires communication between parallel features
3. **Terminal multiplexing** (tmux/iTerm) essential for monitoring multiple worktrees
4. **Complex workflows** (release + hotfix + feature) are manageable with proper isolation
5. **Cherry-picking and rebasing** work across worktrees without conflicts
6. **Team collaboration** benefits from worktree-based PR reviews
7. **Recovery procedures** exist for corrupted worktrees and orphaned references
8. **Performance optimization** via shared dependencies and build caches
9. **Monitoring scripts** keep worktrees healthy over time
10. **Security** requires careful secret management across worktrees

---

## Next Steps

- **Tutorial:** [Worktree Setup Tutorial](../tutorials/TUTORIAL-worktree-setup.md) — Beginner guide
- **Quick reference:** [Worktree Refcard](../reference/REFCARD-GIT-WORKTREE.md) — Common commands
- **Command docs:** [/craft:git:worktree](../commands/git/worktree.md) — Full documentation
- **Workflow:** [Git Feature Workflow](../workflows/git-feature-workflow.md) — Complete git workflow
