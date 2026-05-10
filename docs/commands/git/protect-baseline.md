# /craft:git:protect-baseline

> **Apply craft's standard GitHub-side branch protection to any repo**

---

## Synopsis

```bash
/craft:git:protect-baseline                                   # Current repo, default branch
/craft:git:protect-baseline --repo OWNER/REPO                 # Explicit repo
/craft:git:protect-baseline --branch master                   # Different branch
/craft:git:protect-baseline --check "test" --check "lint"     # Add status checks (repeatable)
/craft:git:protect-baseline --strict                          # Require up-to-date branches
/craft:git:protect-baseline --show                            # Display current protection
/craft:git:protect-baseline --dry-run                         # Preview payload, no API call
/craft:git:protect-baseline --remove                          # Remove protection
```

---

## Description

Applies a consistent baseline of GitHub branch protection rules via the GitHub REST API. The baseline is solo-developer friendly: PR required with **0 review approvals**, force-pushes blocked, deletions blocked.

This is the GitHub-side companion to [`/craft:git:protect`](protect.md), which manages the local `branch-guard.sh` hook. Together they provide defense-in-depth: the local hook stops accidental writes before they leave your machine; GitHub-side protection stops anything that slips through.

---

## Behavior

1. Resolves the target repo (from `--repo` or `git remote get-url origin`)
2. Resolves the target branch (from `--branch` or the repo's `default_branch`)
3. Builds the protection JSON payload with the requested settings
4. Calls `gh api -X PUT repos/$REPO/branches/$BRANCH/protection`
5. Reports success or the API error

---

## Options

| Flag | Description |
|------|-------------|
| `--repo OWNER/REPO` | GitHub repo (default: current `origin`) |
| `--branch NAME` | Branch to protect (default: repo's default branch) |
| `--check NAME` | Required status check (repeatable; safe with names containing commas) |
| `--strict` | Require branches to be up-to-date with base before merge |
| `--dry-run` | Print the payload, don't call the API |
| `--remove` | Remove protection from the branch |
| `--show` | Display the current protection config |

---

## Baseline Protection

| Setting | Value | Why |
|---------|-------|-----|
| `required_pull_request_reviews.required_approving_review_count` | 0 | Solo-dev friendly --- blocks accidental direct pushes without forcing a phantom reviewer |
| `allow_force_pushes` | false | History rewrites on `main` are always destructive |
| `allow_deletions` | false | Branch deletion would lose all history |
| `enforce_admins` | false | Admin can still bypass if absolutely needed |
| `required_status_checks` | null (unless `--check`) | Adding a non-existent check would block all merges |
| `restrictions` | null | Anyone with write access can open PRs |

---

## Examples

**Apply to current repo:**

```bash
/craft:git:protect-baseline
# → Repo:   Data-Wise/myrepo
# → Branch: main
# → Action: APPLY baseline protection
# →   PR required:    yes (0 reviews)
# →   Force push:     blocked
# →   Delete:         blocked
# →   Status checks:  none
# → Applied successfully.
```

**Apply with status checks (note repeatable flag handles names with commas):**

```bash
/craft:git:protect-baseline \
  --repo Data-Wise/nexus-cli \
  --check "test (ubuntu-latest, 3.11)" \
  --check "test (ubuntu-latest, 3.12)" \
  --check "lint" \
  --strict
```

**Preview without applying:**

```bash
/craft:git:protect-baseline --repo Data-Wise/myrepo --dry-run
# Prints full JSON payload, no API call
```

**Inspect current state:**

```bash
/craft:git:protect-baseline --show
# Prints the active protection config (or "NONE" if unprotected)
```

**Remove protection:**

```bash
/craft:git:protect-baseline --repo Data-Wise/myrepo --remove
```

---

## Common Patterns

**Bulk apply across many repos** (loop in shell):

```bash
for repo in atlas dtslides scribe; do
  ./scripts/protect-baseline.sh --repo Data-Wise/$repo
done
```

**Preserve existing checks** (manual two-step):

```bash
# 1. Capture existing checks
EXISTING=$(./scripts/protect-baseline.sh --repo OWNER/REPO --show \
  | jq -r '.required_status_checks.contexts[]?')

# 2. Re-apply with same names
ARGS=()
while IFS= read -r c; do ARGS+=(--check "$c"); done <<< "$EXISTING"
./scripts/protect-baseline.sh --repo OWNER/REPO "${ARGS[@]}"
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Protection applied, removed, or shown successfully |
| 1 | API failure or missing prerequisite (`gh` not installed/authenticated) |
| 2 | Unknown argument |

---

## See Also

- [/craft:git:protect](protect.md) --- Local hook (`branch-guard.sh`) management
- [/craft:git:unprotect](unprotect.md) --- Bypass local hook for a session
- [/craft:git:status](status.md) --- Shows protection indicators
- [Branch Protection Architecture](../../architecture.md#5-branch-protection-hooks) --- How the local hook works
