# Quick Reference: Protect-Baseline (dev/git skill)

**GitHub-side branch protection** — companion to the local hook (`branch-guard.sh`).

> **Folded into the `dev/git` skill (2026-07 v4 consolidation).** `/craft:git:protect-baseline`
> is no longer a separate slash command — ask "protect-baseline ..." naturally
> and the skill runs the underlying script. See
> [`skills/dev/git/SKILL.md`](https://github.com/Data-Wise/craft/blob/dev/skills/dev/git/SKILL.md).

**Ask:** `"protect-baseline"` (dev/git skill) | **Script:** `scripts/protect-baseline.sh`

---

## TL;DR

```text
ask "protect-baseline"                                          # Current repo, default branch
ask "protect-baseline --repo OWNER/REPO"                        # Any repo
ask 'protect-baseline --check "test" --check "lint"'            # With status checks
ask "protect-baseline --show"                                   # Inspect current state
ask "protect-baseline --dry-run"                                # Preview, no API call
ask "protect-baseline --remove"                                 # Remove protection
```

Or invoke the script directly: `./scripts/protect-baseline.sh [flags]` — same flags apply.

---

## Baseline Settings Applied

| Setting | Value | Why |
|---------|-------|-----|
| `required_pull_request_reviews.required_approving_review_count` | 0 | Solo-dev friendly — blocks accidental direct pushes without forcing a phantom reviewer |
| `allow_force_pushes` | false | History rewrites on `main` are always destructive |
| `allow_deletions` | false | Branch deletion would lose all history |
| `enforce_admins` | false | Admin can still bypass when truly needed |
| `required_status_checks` | null (unless `--check`) | Adding a non-existent check would block all merges |
| `restrictions` | null | Anyone with write access can open PRs |

---

## Flags at a Glance

| Flag | Effect |
|------|--------|
| `--repo OWNER/REPO` | Target repo (default: current `origin`) |
| `--branch NAME` | Target branch (default: repo's `default_branch`) |
| `--check NAME` | Required status check (repeatable, safe with commas in names) |
| `--strict` | Require branches to be up-to-date with base before merge |
| `--show` | Print current protection JSON; no changes |
| `--dry-run` | Print payload that would be sent; no API call |
| `--remove` | Delete protection from the branch |
| `--help`, `-h` | Show help |

---

## Decision Tree

```text
What do you need to do?
│
├─ Protect a brand-new repo?
│   └─ ask "protect-baseline"
│
├─ Protect a repo with existing CI?
│   └─ ask 'protect-baseline --check "your-check-name"'
│
├─ Inspect current state before changing?
│   └─ ask "protect-baseline --show"
│
├─ See what would happen without changing?
│   └─ ask "protect-baseline --dry-run"
│
├─ Bulk-protect many repos?
│   └─ Loop in shell — see Cookbook recipe
│
├─ Remove protection (release CI repo, etc.)?
│   └─ ask "protect-baseline --remove"
│
└─ Repo uses `master` instead of `main`?
    └─ Auto-detected from default_branch — no flag needed
```

---

## Common Patterns

### Brand-new repo, no CI

```bash
./scripts/protect-baseline.sh --repo Data-Wise/myrepo
```

### Repo with test/lint CI workflows

```bash
./scripts/protect-baseline.sh \
  --repo Data-Wise/myrepo \
  --check "test" \
  --check "lint" \
  --strict
```

### Status check names with commas

GitHub check names like `test (ubuntu-latest, 3.12)` contain commas. The repeatable `--check` flag handles these safely (comma-separated values would corrupt them):

```bash
./scripts/protect-baseline.sh \
  --repo Data-Wise/nexus-cli \
  --check "test (ubuntu-latest, 3.11)" \
  --check "test (ubuntu-latest, 3.12)" \
  --check "test (ubuntu-latest, 3.13)" \
  --check "lint"
```

### Preserve existing checks while changing PR settings

```bash
# 1. Capture existing
EXISTING=$(./scripts/protect-baseline.sh --repo OWNER/REPO --show \
  | jq -r '.required_status_checks.contexts[]?')

# 2. Re-apply with same names
ARGS=()
while IFS= read -r c; do ARGS+=(--check "$c"); done <<< "$EXISTING"
./scripts/protect-baseline.sh --repo OWNER/REPO "${ARGS[@]}"
```

### Bulk-protect many repos

```bash
for repo in atlas dtslides scribe rforge; do
  ./scripts/protect-baseline.sh --repo Data-Wise/$repo
done
```

See the [Cookbook recipe](../cookbook/common/bulk-branch-protection.md) for a more complete bulk workflow.

---

## Relationship to Local Hook

The local hook (`branch-guard.sh`) and GitHub-side protection cover different failure modes:

| Layer | Catches | Misses |
|-------|---------|--------|
| **Local hook** | Accidental edits/writes/force-pushes from this machine | Pushes from other machines, web UI commits, CI bots |
| **GitHub-side** | Direct pushes from any source, force-pushes, deletions | Anything that happens before the push |

Apply both for full coverage:

```text
ask "protect"              # Local hook (per-machine)
ask "protect-baseline"     # GitHub-side (per-repo)
```

**Important:** asking "unprotect" only bypasses the local hook. To remove GitHub-side protection, ask "protect-baseline --remove".

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Protection applied, removed, or shown successfully |
| 1 | API failure or missing prerequisite (`gh` not installed/authenticated) |
| 2 | Unknown argument |

---

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth status`)
- Write access to the target repo
- For private repos: token with `repo` scope (gh handles this)

---

## See Also

- **Skill:** [dev/git](https://github.com/Data-Wise/craft/blob/dev/skills/dev/git/SKILL.md) --- protect-baseline, protect, unprotect operations (folded from `/craft:git:*`, 2026-07 v4 consolidation)
- **Refcard:** [REFCARD-BRANCH-GUARD](REFCARD-BRANCH-GUARD.md) --- Local hook quick reference
- **Cookbook:** [Bulk Branch Protection](../cookbook/common/bulk-branch-protection.md) --- Apply across many repos
- **Tutorial:** [TUTORIAL-protect-new-repo](../tutorials/TUTORIAL-protect-new-repo.md) --- Step-by-step walkthrough
- **Architecture:** [Branch Protection Hooks](../architecture.md#5-branch-protection-hooks) --- Defense-in-depth model
