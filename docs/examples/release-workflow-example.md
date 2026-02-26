# Release Workflow Example

This example demonstrates the `/release` pipeline from version detection through downstream verification.

## Initial State

```text
Branch: dev (clean working tree)
Current version: v2.27.0
Commits since last release: 15 (feat: 3, fix: 5, docs: 4, chore: 3)
```

## Step 1: Version Detection

```bash
/release
```

The pipeline analyzes commits since the last tag:

```text
┌─────────────────────────────────────────────────────────────┐
│ Release Pipeline                                            │
├─────────────────────────────────────────────────────────────┤
│ Current version: v2.27.0                                    │
│ Suggested bump: minor (feat: commits detected)              │
│ Next version: v2.28.0                                       │
└─────────────────────────────────────────────────────────────┘
```

## Step 2: Pre-Flight Checks

Two complementary validations run:

```text
[ 1/13] CI mirror check .................... PASSED
[ 2/13] Release metadata check ............. PASSED
```

**What runs:**

- Full pytest suite (unit + integration + e2e)
- `pre-release-check.sh` validates version consistency across 13 files

## Step 3: Version Bump

```bash
./scripts/bump-version.sh 2.28.0
```

Updates 13 files atomically: `plugin.json`, `marketplace.json`, `package.json`, `CLAUDE.md`, `README.md`, `docs/index.md`, `docs/REFCARD.md`, `mkdocs.yml`, `.STATUS`, and more.

## Steps 4-5: Commit, Push, Create PR

```text
[ 3/13] Version bump ....................... DONE
[ 4/13] Commit and push ................... DONE
[ 5/13] Release PR created ................. PR #111
```

## Steps 6-7: CI Monitoring and Merge

The pipeline polls CI every 30 seconds until checks pass, then merges:

```text
[ 6/13] CI monitoring ..................... GREEN (90s)
[ 7/13] PR merged .......................... DONE
```

## Steps 8-10: Release, Docs, Homebrew

```text
[ 8/13] GitHub release ..................... v2.28.0
[ 9/13] Docs deployed ..................... DONE
[10/13] Homebrew tap updated .............. DONE
```

## Steps 11-13: Sync and Verify

```text
[11/13] Dev synced ........................ DONE
[12/13] Verify CI on main ................. PASSED
[13/13] Downstream verification ........... ALL GREEN
```

Downstream checks verify: docs deploy workflow, Homebrew release workflow, live site version, formula content, and CI badge status.

## Common Issues

| Issue | Resolution |
|-------|------------|
| npm 403 in CI | Transient registry flake — re-run CI |
| Branch protection blocks merge | Use `--admin` after CI passes |
| Homebrew SHA mismatch | Wait for GitHub release tarball propagation |

## See Also

- [Release Pipeline Tutorial](../tutorials/TUTORIAL-release-pipeline.md) — Step-by-step learning guide
- [Release Pipeline Reference](../reference/REFCARD-RELEASE.md) — Quick reference card
- [Automate Release Workflow](../cookbook/common/automate-release-workflow.md) — Cookbook recipe
