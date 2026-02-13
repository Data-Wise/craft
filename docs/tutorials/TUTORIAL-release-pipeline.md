# Tutorial: Release Pipeline

Learn how to use `/craft:release` to automate the full release lifecycle.

**Time:** 10 minutes | **Level:** Intermediate | **Skill:** `skills/release/SKILL.md`

---

## Prerequisites

Before running a release:

1. You are on the `dev` branch
2. All feature work is merged to dev via PRs
3. Working tree is clean (`git status` shows no changes)
4. Tests are passing

---

## Step 1: Preview with Dry-Run

Always start with a dry-run to see the full plan:

```text
/release --dry-run
```

This shows:

- Current and suggested next version
- Every step that will execute
- Files that will be modified
- PRs that will be created

No changes are made. Review the output before proceeding.

---

## Step 2: Run Your First Release

When you are ready:

```text
/release
```

The skill will:

1. **Detect your current version** from plugin.json, package.json, or git tags
2. **Suggest the next version** based on commit history (patch, minor, or major)
3. **Ask for confirmation** before proceeding

If you already know the version:

```text
/release v2.18.0
```

---

## Step 3: Follow the Pipeline

The release executes 8 steps sequentially:

| Step | What Happens | You Need To |
|------|-------------|-------------|
| CI mirror | `/craft:check --for release` (full test suite) | Fix any failures |
| Metadata check | `pre-release-check.sh` (version/counts) | Fix any mismatches |
| Version bump | Updates version files | Review changes |
| Commit and push | Creates release commit | Nothing (automatic) |
| Release PR | Creates dev to main PR | Nothing (automatic) |
| Merge PR | Merges the PR | Confirm if admin needed |
| GitHub release | Creates tag and release | Nothing (automatic) |
| Docs deploy | Publishes docs site | Nothing (automatic) |
| Dev sync | Pulls main into dev | Nothing (automatic) |

If any step fails, the pipeline stops and reports the error.

---

## Using Dry-Run Mode

Dry-run is useful for:

- **First-time releases** — understand what will happen
- **Verifying version detection** — confirm the right version is picked up
- **Checking prerequisites** — see if anything would block the release
- **Documentation** — share the release plan with teammates

The `-n` alias works too:

```text
/release -n
```

---

## Handling Common Errors

### Pre-Flight Fails

The most common issue. Fix the reported problems and re-run:

```text
# Common fixes:
# - Update version in plugin.json
# - Update version references in CLAUDE.md
# - Commit any uncommitted changes
```

### Branch Guard Blocks PR Creation

If the PR body contains literal destructive git command strings, branch guard may block PR creation. The skill already handles this by using indirect language in PR descriptions.

### Branch Protection Blocks Merge

If the repository has branch protection rules, the skill will ask for confirmation before using `--admin`:

```text
Branch protection is blocking the merge. Use --admin? (y/n)
```

### Tag Already Exists

If a tag for the target version already exists:

```text
# Verify the tag is stale
git tag -l "v2.18.0"

# Delete if confirmed stale
git tag -d v2.18.0
git push origin :refs/tags/v2.18.0
```

---

## Customizing for Different Project Types

The release skill adapts to your project type:

### Craft Plugin

- Version source: `.claude-plugin/plugin.json`
- Pre-flight: `scripts/pre-release-check.sh`
- Docs deploy: `mkdocs gh-deploy`

### Python Package

- Version source: `pyproject.toml`
- Pre-flight: `pytest`
- Post-release: PyPI publish via GitHub Actions

### Node Package

- Version source: `package.json`
- Pre-flight: `npm test`
- Post-release: `npm publish`

### R Package

- Version source: `DESCRIPTION`
- Pre-flight: `R CMD check`
- Post-release: CRAN submission

---

## See Also

- [Release Quick Reference](../reference/REFCARD-RELEASE.md) - Compact reference card
- [Release Checklist](../../skills/release/references/release-checklist.md) - Detailed per-project checklists
- [Release Workflow](../workflows/release-workflow.md) - Full workflow documentation
