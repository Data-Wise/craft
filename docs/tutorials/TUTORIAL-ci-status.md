# Tutorial: ci:status — CI Status Dashboard

By the end of this tutorial you will have:

- Viewed the CI status dashboard for your current repo
- Checked status across multiple repos
- Used the `--post-release` flag to verify a release

**Prerequisites:** craft installed, `gh` CLI authenticated.

---

## Step 1: View CI Status

```
/craft:ci:status
```

Displays a dashboard of recent workflow runs:

```
CI Status Dashboard — Data-Wise/craft
────────────────────────────────────────
Branch: dev

Workflow            Run       Status      Duration  Commit
──────────────────  ────────  ──────────  ────────  ──────────────────
Craft CI            #1234     ✅ success  2m 14s    chore: bump v2.41
Docs                #1233     ✅ success  45s       chore: bump v2.41
Validate Deps       #1232     ✅ success  1m 02s    chore: bump v2.41
Homebrew Release    #1231     ✅ success  3m 44s    chore: bump v2.41

All checks green.
```

---

## Step 2: Check a Specific Repo

```
/craft:ci:status --repo Data-Wise/homebrew-tap
```

Useful for monitoring sibling repositories after a release.

---

## Step 3: Post-Release Verification

After a release, run a multi-repo sweep:

```
/craft:ci:status --post-release
```

Checks: main branch CI, docs deploy, Homebrew tap, badge links. Reports any failures.

---

## Step 4: JSON Output

```
/craft:ci:status --json
```

Returns structured JSON with run IDs, statuses, and timestamps. Useful in scripts or for feeding into `ci:watch`.

---

## What's Next

- If any check is red, use `/craft:ci:triage` to classify and diagnose the failure
- Use `/craft:ci:watch` to poll a specific run to completion
- See [release pipeline](TUTORIAL-release-pipeline.md) for where status checks fit in the release flow
