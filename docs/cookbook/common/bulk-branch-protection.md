# Bulk Branch Protection Across Repos

> **Apply consistent GitHub branch protection to many repos at once**

---

## When to use this recipe

- You manage 5+ repos and want consistent protection
- You discovered some repos have no protection during an audit
- You're onboarding a new project area and want a baseline applied to all repos
- You want to standardize after a security review

This recipe is the natural follow-up to [`/craft:git:protect-baseline`](../../commands/git/protect-baseline.md) — that command protects one repo at a time. This recipe shows how to scale it.

---

## Quick recipe (single org, plain baseline)

```bash
# Set the org and the list of repos
ORG=Data-Wise
REPOS=(atlas dtslides scribe rforge regression)

# Apply baseline to each
for repo in "${REPOS[@]}"; do
  ./scripts/protect-baseline.sh --repo "$ORG/$repo"
done
```

---

## Audit-then-apply pattern

The safe pattern is: **audit first, decide what to apply, then loop**. Don't blanket-apply blind.

### Step 1: List candidate repos

```bash
ORG=Data-Wise
gh repo list "$ORG" --limit 100 --no-archived \
  --json name,defaultBranchRef,fork,pushedAt \
  -q '.[] | "\(.name)\t\(.defaultBranchRef.name)\t\(.fork)\t\(.pushedAt[:10])"'
```

### Step 2: Filter to active, owned repos

```bash
# Active in last 12 months, not a fork
CUTOFF=$(date -v-1y '+%Y-%m-%d' 2>/dev/null || date -d '12 months ago' '+%Y-%m-%d')
gh repo list "$ORG" --limit 100 --no-archived \
  --json name,defaultBranchRef,fork,pushedAt \
  -q --arg cutoff "$CUTOFF" '
    .[]
    | select(.fork == false)
    | select(.pushedAt > $cutoff)
    | "\(.name)\t\(.defaultBranchRef.name)"
  ' > /tmp/active-repos.tsv

wc -l /tmp/active-repos.tsv
```

### Step 3: Audit current protection state

```bash
while IFS=$'\t' read -r repo branch; do
  result=$(gh api "repos/$ORG/$repo/branches/$branch/protection" 2>&1 | head -c 100)
  if echo "$result" | grep -q "Branch not protected"; then
    state="NONE"
  elif echo "$result" | grep -q '"url"'; then
    state="HAS-PROTECTION"
  else
    state="ERROR"
  fi
  printf "%-40s %s\n" "$repo" "$state"
done < /tmp/active-repos.tsv
```

### Step 4: Apply baseline only to bare repos

```bash
while IFS=$'\t' read -r repo branch; do
  result=$(gh api "repos/$ORG/$repo/branches/$branch/protection" 2>&1)
  if echo "$result" | grep -q "Branch not protected"; then
    echo "Applying to $repo..."
    ./scripts/protect-baseline.sh --repo "$ORG/$repo"
  else
    echo "Skipping $repo (already has protection)"
  fi
done < /tmp/active-repos.tsv
```

### Step 5: Verify

```bash
while IFS=$'\t' read -r repo branch; do
  result=$(gh api "repos/$ORG/$repo/branches/$branch/protection" 2>&1)
  pr=$(echo "$result" | python3 -c "
import json,sys
try:
    d = json.load(sys.stdin)
    r = d.get('required_pull_request_reviews')
    print('PR(' + str(r.get('required_approving_review_count', '?')) + ')' if r else 'no-PR')
except:
    print('NONE')
" 2>/dev/null)
  printf "%-40s %s\n" "$repo" "$pr"
done < /tmp/active-repos.tsv
```

---

## Patterns to skip

Some repos legitimately need to remain unprotected. Common cases:

| Pattern | Why | Example |
|---------|-----|---------|
| Release CI does direct pushes | Workflow updates files on main automatically | `homebrew-tap`, `awesome-*` mirrors |
| Read-only mirrors | No human pushes happen | Imported docs, generated sites |
| Active forks you patch frequently | Your PR-required policy doesn't apply to fork edits | Public-source forks |

Maintain a skip list:

```bash
SKIP_REPOS=(homebrew-tap data-wise.github.io)

# In the loop:
if [[ " ${SKIP_REPOS[*]} " =~ " $repo " ]]; then
  echo "Skipping $repo (in skip list)"
  continue
fi
```

---

## With status checks (CI-aware repos)

If you have CI workflows that should gate merges, capture their context names first:

```bash
# Find what status checks are emitted by recent runs
gh run list -R "$ORG/$repo" --limit 5 --json name,conclusion -q '.[] | "\(.name)"' | sort -u
```

Then apply with `--check` for each:

```bash
./scripts/protect-baseline.sh --repo "$ORG/$repo" \
  --check "test" \
  --check "lint" \
  --strict
```

> **Caution:** Don't add a check that doesn't exist as a real workflow context — GitHub will block all merges since the check never reports.

---

## Dry-run before bulk apply

Always preview the payload first, especially across many repos:

```bash
for repo in "${REPOS[@]}"; do
  echo "=== $repo ==="
  ./scripts/protect-baseline.sh --repo "$ORG/$repo" --dry-run
done | tee /tmp/protection-dryrun.log
```

Inspect `/tmp/protection-dryrun.log`, then run for real.

---

## Common gotchas

### Default branch is `master`, not `main`

The script auto-detects via the GitHub API — no flag needed. If you want to override:

```bash
./scripts/protect-baseline.sh --repo "$ORG/$repo" --branch master
```

### GitHub Pages repos require PRs after this

If a repo deploys via GitHub Pages on push to `main`, applying baseline means every doc edit needs a PR. Verify this is acceptable for the repo, or add it to the skip list.

### Half-protected repos (status checks but no PR-required)

Re-applying baseline overwrites the existing config entirely. To **add** PR-required while **preserving** existing status checks:

```bash
EXISTING=$(./scripts/protect-baseline.sh --repo "$ORG/$repo" --show \
  | jq -r '.required_status_checks.contexts[]?')
ARGS=()
while IFS= read -r c; do ARGS+=(--check "$c"); done <<< "$EXISTING"
./scripts/protect-baseline.sh --repo "$ORG/$repo" "${ARGS[@]}" --strict
```

---

## Idempotency

The script is safe to re-run on already-protected repos — it just replaces the config with the same baseline. No accumulating state, no duplicate rules.

This means you can safely run the audit-then-apply pipeline on a schedule (e.g., weekly cron) to catch new repos that were added without protection.

---

## See Also

- [/craft:git:protect-baseline](../../commands/git/protect-baseline.md) — Single-repo command
- [REFCARD-PROTECT-BASELINE](../../reference/REFCARD-PROTECT-BASELINE.md) — Quick reference
- [TUTORIAL-protect-new-repo](../../tutorials/TUTORIAL-protect-new-repo.md) — Step-by-step single-repo walkthrough
- [Branch Protection Architecture](../../architecture.md#5-branch-protection-hooks) — Defense-in-depth model
