# Tutorial: Protect a New Repo with Craft

> **15-minute walkthrough — install both layers of branch protection on a fresh GitHub repo**

---

## What you'll learn

By the end of this tutorial you will have:

1. A fresh GitHub repo with **GitHub-side branch protection** (PR required, no force-push, no delete)
2. The **local hook** (`branch-guard.sh`) installed and active on your machine
3. A working understanding of which layer catches what
4. A test PR demonstrating the workflow end-to-end

---

## Prerequisites

| Tool | Check it works | Install if missing |
|------|----------------|-------------------|
| `gh` CLI | `gh auth status` | `brew install gh && gh auth login` |
| `git` | `git --version` | Comes with macOS Xcode CLI tools |
| `craft` plugin | `/craft:git:status` runs | See [installation guide](../guide/getting-started.md) |

---

## Step 1: Create the repo

```bash
# Replace OWNER and NAME with your values
OWNER=your-username
NAME=protection-tutorial

gh repo create "$OWNER/$NAME" --public --add-readme
gh repo clone "$OWNER/$NAME"
cd "$NAME"
```

What you should see:

```text
✓ Created repository OWNER/protection-tutorial on GitHub
✓ Added README.md
Cloning into 'protection-tutorial'...
```

> **Tip:** If you'd rather use an existing repo, just `cd` into it and skip ahead to Step 2. The command works the same.

---

## Step 2: Inspect current state

Before applying anything, see what's there:

```bash
/craft:git:protect-baseline --show
```

You should see:

```text
Repo:   OWNER/protection-tutorial
Branch: main
Status: NONE (unprotected)
```

A brand-new repo has no protection — anyone with write access can push directly to `main`. That's what we'll fix.

---

## Step 3: Apply the GitHub-side baseline

```bash
/craft:git:protect-baseline
```

What you should see:

```text
Repo:   OWNER/protection-tutorial
Branch: main
Action: APPLY baseline protection
  PR required:    yes (0 reviews)
  Force push:     blocked
  Delete:         blocked
  Status checks:  none
Applied successfully.
```

**What just happened?** The script called `gh api -X PUT repos/OWNER/NAME/branches/main/protection` with the craft baseline JSON. The baseline is solo-dev friendly: PR required with **zero** required review approvals — enough to catch accidental direct pushes without forcing you to wait for a phantom reviewer.

### Verify

```bash
/craft:git:protect-baseline --show
```

You should now see the full protection JSON:

```text
Repo:   OWNER/protection-tutorial
Branch: main
{
    "url": "https://api.github.com/repos/...",
    "required_pull_request_reviews": {
        "required_approving_review_count": 0,
        ...
    },
    "allow_force_pushes": { "enabled": false },
    "allow_deletions": { "enabled": false },
    ...
}
```

---

## Step 4: Test that direct pushes are blocked

Try the push that branch protection should now block:

```bash
echo "edit" >> README.md
git add README.md
git -c commit.gpgsign=false commit -m "test: direct push attempt"
git push origin main
```

You should see GitHub reject the push:

```text
remote: error: GH006: Protected branch update failed for refs/heads/main.
remote: error: At least 1 approving review is required by reviewers...
```

Wait — but we set `required_approving_review_count: 0`. Why is GitHub asking for 1?

> **Gotcha:** Even with 0 required reviews, GitHub blocks **direct pushes** when `required_pull_request_reviews` is enabled. The "0 reviews" means PRs can be merged immediately; it doesn't mean direct pushes are allowed. This is exactly what we want — accidents prevented, friction minimized.

Reset the local commit so we can do it properly:

```bash
git reset --soft HEAD~1
```

---

## Step 5: Use the PR workflow instead

```bash
git checkout -b feature/test-protection
git push -u origin feature/test-protection

gh pr create --base main --title "test: validate protection workflow" \
  --body "Demonstrates the PR-required workflow."
```

You should see:

```text
https://github.com/OWNER/NAME/pull/1
```

Check that it's mergeable:

```bash
gh pr view 1 --json mergeable,mergeStateStatus
```

Output:

```json
{"mergeStateStatus":"CLEAN","mergeable":"MERGEABLE"}
```

Merge it:

```bash
gh pr merge 1 --squash
```

Done — the change landed via the PR-required workflow.

---

## Step 6: Install the local hook layer

GitHub-side protection catches anything that reaches the remote. The **local hook** catches accidents earlier — before they leave your machine.

```bash
/craft:git:protect --show
```

If you see "Branch protection is already active," you're good. Otherwise, the hook is installed via the craft installer and runs as a `PreToolUse` hook in Claude Code.

The local hook treats branches by name:

| Branch | Behavior |
|--------|----------|
| `main` | Hard-block all writes (BLOCKED) |
| `dev` | Smart mode — confirm new code, allow edits to existing files |
| `feature/*` | No restrictions |

The two layers cover different failure modes:

| Layer | Catches | Misses |
|-------|---------|--------|
| **Local hook** | Accidental edits/writes from this machine | Pushes from other machines, web UI commits, CI bots |
| **GitHub-side** | Direct pushes from any source | Anything before the push |

---

## Step 7: Add status checks (optional)

If your repo has CI workflows, gate merges on them:

```bash
# Find what your workflows actually emit
gh run list --limit 5 --json name -q '.[] | .name' | sort -u

# Then apply with --check
/craft:git:protect-baseline --check "test" --check "lint" --strict
```

> **Warning:** Don't add a `--check` for a workflow that doesn't exist or hasn't run yet — GitHub will block all merges since the check never reports success.

---

## Step 8: Cleanup

If this was a tutorial repo you don't want to keep:

```bash
gh repo delete "$OWNER/$NAME" --yes
```

If you want to remove protection (e.g., before reverting to a different workflow):

```bash
/craft:git:protect-baseline --remove
```

---

## What you've learned

- **Two complementary layers**: local hook (machine-level shield) + GitHub-side (remote-level shield)
- **PR-required ≠ approval-required**: 0 reviews still blocks direct pushes
- **`--show` and `--dry-run`** let you inspect and preview before changing anything
- **`/craft:git:unprotect` only affects the local hook** — to remove GitHub-side rules use `--remove`

---

## Common follow-ups

| Goal | Command / Recipe |
|------|------------------|
| Apply this to many repos | [Bulk Branch Protection cookbook](../cookbook/common/bulk-branch-protection.md) |
| Audit which repos already have protection | See cookbook Step 3 |
| Quick-reference card | [REFCARD-PROTECT-BASELINE](../reference/REFCARD-PROTECT-BASELINE.md) |
| Understand the architecture | [Branch Protection Hooks](../architecture.md#5-branch-protection-hooks) |

---

## Troubleshooting

### "gh: command not found"

Install via Homebrew: `brew install gh && gh auth login`

### "Branch not found" on `--show`

The repo's default branch isn't `main`. Either pass `--branch master` (or whatever) or check `gh api repos/OWNER/NAME --jq .default_branch`.

### "Resource not accessible by integration"

Your `gh` CLI lacks the right scope. Re-authenticate with `gh auth refresh -s repo`.

### Status check name has spaces / special chars / commas

Use the **repeatable** `--check` flag, not comma-separated:

```bash
# Good
--check "test (ubuntu-latest, 3.12)" --check "lint"

# Bad — would split on the comma inside parens
--with-checks "test (ubuntu-latest, 3.12),lint"
```

---

## See Also

- [/craft:git:protect-baseline](../commands/git/protect-baseline.md) — Full command reference
- [/craft:git:protect](../commands/git/protect.md) — Local hook companion
- [/craft:git:unprotect](../commands/git/unprotect.md) — Local hook bypass
- [REFCARD-PROTECT-BASELINE](../reference/REFCARD-PROTECT-BASELINE.md) — Quick reference
- [Bulk Branch Protection](../cookbook/common/bulk-branch-protection.md) — Apply to many repos at once
