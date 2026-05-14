---
description: Apply craft's GitHub-side baseline branch protection (PR required, no force-push, no delete) to any repo
category: git
tags: [git, branch-protection, github, security]
arguments:
  - name: repo
    description: GitHub repo as OWNER/REPO (defaults to current repo's origin)
    required: false
  - name: branch
    description: Branch to protect (defaults to repo's default branch)
    required: false
  - name: check
    description: Required status check name (repeatable, e.g. --check "test" --check "lint")
    required: false
  - name: strict
    description: Require branches to be up-to-date with base before merge
    required: false
    default: false
  - name: dry-run
    description: Show payload without calling the API
    required: false
    default: false
  - name: remove
    description: Remove branch protection instead of applying
    required: false
    default: false
  - name: show
    description: Display current protection config without changes
    required: false
    default: false
deprecated: true
replaced-by: "skills/dev/git/"
---

# /craft:git:protect-baseline - GitHub-side Branch Protection

Applies a consistent baseline of GitHub branch protection rules to a repo's main (or specified) branch:

- **PR required** with 0 review approvals (solo-dev friendly)
- **Force-pushes blocked**
- **Deletions blocked**
- **Optional**: required status checks with optional `strict` mode

This is the GitHub-side companion to `/craft:git:protect`, which manages the local hook (`branch-guard.sh`).

## Usage

```bash
/craft:git:protect-baseline                                 # Apply to current repo's default branch
/craft:git:protect-baseline --repo OWNER/REPO               # Apply to a specific repo
/craft:git:protect-baseline --branch master                 # Protect a different branch
/craft:git:protect-baseline --check "test" --check "lint"   # Add required status checks
/craft:git:protect-baseline --check "test" --strict         # Also require up-to-date branches
/craft:git:protect-baseline --show                          # Display current protection
/craft:git:protect-baseline --dry-run                       # Preview payload, no API call
/craft:git:protect-baseline --remove                        # Remove protection
```

## Execution Behavior (MANDATORY)

### Step 1: Verify Prerequisites

```bash
# gh CLI must be installed and authenticated
gh auth status >/dev/null 2>&1 || { echo "Run: gh auth login"; exit 1; }
```

### Step 2: Resolve Repo and Branch

If `--repo` not given, derive from `git remote get-url origin`. If `--branch` not given, query `gh api repos/$REPO --jq .default_branch`. The script (`scripts/protect-baseline.sh`) handles this.

### Step 3: Run the Script

```bash
SCRIPT="${CLAUDE_PLUGIN_ROOT}/scripts/protect-baseline.sh"
"$SCRIPT" "$@"
```

The script:

1. Builds the protection JSON payload (with or without status checks)
2. Calls `gh api -X PUT repos/$REPO/branches/$BRANCH/protection --input <payload>`
3. Reports success or the API error

### Step 4: Confirm Result

After applying, the script prints what was set. Optionally, run `--show` afterward to verify:

```bash
./scripts/protect-baseline.sh --repo OWNER/REPO --show
```

## Baseline Defaults

| Setting | Value | Why |
|---------|-------|-----|
| `required_pull_request_reviews.required_approving_review_count` | 0 | Solo-dev friendly — blocks accidental direct pushes without forcing a phantom reviewer |
| `allow_force_pushes` | false | History rewrites on `main` are always destructive |
| `allow_deletions` | false | Branch deletion would lose all history |
| `enforce_admins` | false | Admin can still bypass if absolutely needed |
| `required_status_checks` | null (unless `--check` given) | Adding a non-existent check would block all merges |
| `restrictions` | null | Anyone with write access can open PRs |

## Common Patterns

**Bare repo with no CI:**

```bash
/craft:git:protect-baseline --repo Data-Wise/myrepo
```

**Repo with test/lint workflows:**

```bash
/craft:git:protect-baseline \
  --repo Data-Wise/myrepo \
  --check "test" \
  --check "lint" \
  --strict
```

**Preserve existing status checks while adding baseline (manual two-step):**

```bash
# 1. Read current checks
/craft:git:protect-baseline --repo OWNER/REPO --show | jq '.required_status_checks.contexts'

# 2. Apply with same check names
/craft:git:protect-baseline --repo OWNER/REPO --check "..." --check "..."
```

## Safety

- `--dry-run` shows the exact payload without calling the API
- The API call replaces protection entirely — `--show` first to capture existing config if you need to preserve status checks
- `--remove` requires explicit flag (no accidental wipes from bare commands)

## See Also

- `/craft:git:protect` — Local hook (`branch-guard.sh`) management
- `/craft:git:unprotect` — Bypass local hook for a session
- `/craft:git:status` — Shows protection indicators
