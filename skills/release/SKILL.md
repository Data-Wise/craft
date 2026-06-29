---
name: release
description: This skill should be used when the user asks to "release", "create a release", "ship it", "publish a new version", "bump version and release", "cut a release", or mentions releasing to GitHub/npm/PyPI. Orchestrates the full release pipeline from pre-flight checks through GitHub release creation.
---

# Release Pipeline

Orchestrate end-to-end releases with pre-flight validation, version bumping, PR creation, merge, and GitHub release — all in one flow.

## When to Use

- User says "release", "ship it", "cut a release", or similar
- User wants to publish a new version to GitHub/npm/PyPI
- User is ready to merge dev to main and tag a release

## Prerequisites

- Must be on `dev` branch (or have dev up to date)
- All feature work merged to dev via PRs
- Working tree clean (no uncommitted changes)

## Arguments

| Argument | Alias | Description | Default |
|----------|-------|-------------|---------|
| `--dry-run` | `-n` | Preview release plan without executing | `false` |
| `--autonomous` | `--auto` | Run without user prompts, auto-resolve where possible | `false` |
| `--skip-surfaces` | — | Skip Step 13.6 surface registry phase (propagation + verify) | `false` |

## Dry-Run Mode

When `--dry-run` or `-n` is passed, execute **only** Step 1 (version detection), then display a preview of every remaining step and exit. No mutations occur.

**Risk Level:** HIGH (modifies git history, creates PRs, publishes releases)

### Dry-Run Output

After detecting the current and next version, display:

```text
┌─────────────────────────────────────────────────────────────┐
│ /release --dry-run                                          │
├─────────────────────────────────────────────────────────────┤
│ Current version: v2.17.0                                    │
│ Next version:    v2.18.0 (minor — feat: commits detected)   │
├─────────────────────────────────────────────────────────────┤
│ Actions that WOULD be taken:                                │
│                                                             │
│  1. ✓ /craft:check --for release (full CI mirror)            │
│  2. ✓ Run pre-release-check.sh v2.18.0 (metadata)           │
│  3. ✓ Bump version in plugin.json, CLAUDE.md                │
│  3b. ✓ /craft:docs:update --post-merge (semantic doc sync)  │
│  3b.5 ✓ docs-staleness-check.sh --non-interactive (gate)   │
│  4. ✓ Commit: "chore: bump version to v2.18.0 for release"  │
│  5. ✓ Push to dev                                           │
│  6. ✓ Create PR: dev → main                                 │
│  6.5 ✓ CI monitoring (poll → diagnose → fix → retry)        │
│  7. ✓ Merge PR (--merge, NO --delete-branch)                │
│  8. ✓ Create GitHub release v2.18.0 on main                 │
│  9. ✓ mkdocs build --strict && mkdocs gh-deploy              │
│ 10. ✓ Update Homebrew tap (formula or cask)                 │
│      (10b if Tauri: build → upload → SHA256 → cask → tap)   │
│      (10b verify_caveats.py — advisory caveats gate)         │
│      (10c post_install_check.py — advisory structural gate)  │
│      (10d aggregator-sync.yml CI action — BLOCKING on unmerged PR)  │
│ 11. ✓ Sync dev with main                                    │
│ 12. ✓ Verify CI on main                                     │
│ 13. ✓ Verify downstream (docs, brew, badges, cask)          │
│ 13.5 ✓ Post-release sweep (Tier 2+ drift detection)        │
├─────────────────────────────────────────────────────────────┤
│ ⚠ Risk: HIGH — modifies git history, creates PRs            │
│ ⚠ No changes were made. Run without --dry-run to execute.   │
└─────────────────────────────────────────────────────────────┘
```

### Dry-Run Guarantees

- No commits, tags, or pushes
- No PRs created or merged
- No GitHub releases published
- No docs deployed
- Exit code 0

## Autonomous Mode (--autonomous)

When `--autonomous` or `--auto` is passed, the release pipeline runs without user interaction:

| Step | Normal | Autonomous |
|------|--------|------------|
| Step 1 (version) | AskUserQuestion to confirm | Auto-select from commit analysis, show decision |
| Step 2 (pre-flight) | Same | Same (fail = abort, no retry) |
| Step 3-5 (bump, commit, PR) | Same | Same (deterministic) |
| Step 7 (merge) | User confirms --admin if blocked | Auto-use --admin, log the override |
| Step 8-13 (release, deploy, verify) | Same | Same (deterministic) |
| Errors | Stop and report | Retry once (step-level), then abort with report |

Full detail — safety checks, version-detection script, admin-override warning, error-recovery
box, and flag combinations — is in
[`references/autonomous-mode.md`](references/autonomous-mode.md).

## Release Pipeline

Execute these steps in order. Stop and report if any step fails. Full command-level detail for
Steps 1–9 and 11–12 is in [`references/pipeline-steps.md`](references/pipeline-steps.md).

### Step 1: Determine Version

Detect current version from `plugin.json` / `package.json` / `git describe`. Analyze commits to
suggest patch / minor / major bump. Ask user to confirm (skipped in autonomous mode).

### Step 2: Pre-Flight Checks

**2a** `/craft:check --for release` — full CI mirror (tests, lint, security, docs, 90% coverage).
**2b** `./scripts/pre-release-check.sh <version>` — release metadata consistency (craft projects).
**2c** `claude plugin validate .` — marketplace validation (if `marketplace.json` exists).
Both must pass before proceeding. See pipeline-steps.md for fix guidance.

### Step 3: Version Bump

```bash
./scripts/bump-version.sh <version>   # craft projects: updates 13 files atomically
./scripts/bump-version.sh --verify    # confirm consistency
```

For Python / Node / R projects, update manifest files manually.

### Step 3b: Semantic Doc Updates

```bash
/craft:docs:update --post-merge
```

Updates CHANGELOG.md, VERSION-HISTORY.md, README.md, docs/index.md, docs/REFCARD.md,
mkdocs.yml, commands/hub.md, and docs/commands/hub.md with release-specific content.
Full table of what to update is in pipeline-steps.md.

### Step 3b.5: Staleness Gate

```bash
./scripts/docs-staleness-check.sh --non-interactive
```

RED findings block; YELLOW findings warn but allow proceed. Fix any RED before Step 4.
Run `./scripts/docs-staleness-check.sh --fix` to auto-resolve mechanical staleness.

### Step 4: Commit & Push

```bash
git add <changed-files>
git commit -m "chore: bump version to v<version> for release"
git push
```

Never use `git add -A` or `git add .` for release commits.

### Step 5: Create Release PR

```bash
gh pr create --base main --head dev \
  --title "Release: v<version> — <title>" \
  --body "<release-notes>"
```

Avoid literal destructive git command strings in the PR body (branch guard scans them).

### Step 6: Monitor CI on PR (MANDATORY)

Poll `gh run list --branch dev` every 30s until success or failure. Fix failures before merging.
Full polling script and escalation path in pipeline-steps.md.

### Step 6.5: CI Monitoring (NEW in v2.22.0)

`bash scripts/ci-monitor.sh <pr-number>` — polls, auto-fixes safe categories
(`version_mismatch`, `lint_failure`, `changelog_format`), asks before risky ones. Configuration
via `.claude/release-config.json`. Full category table and output format in pipeline-steps.md.

### Step 7: Merge Release PR

```bash
gh pr merge <number> --merge
```

**NEVER use `--delete-branch`** — `dev` must not be deleted.
Use `--admin` only after user confirmation if branch protection blocks.
Autonomous mode: auto-uses `--admin`, logs a WARNING.

### Step 8: Create GitHub Release

```bash
git pull origin main
gh release create v<version> --target main \
  --title "v<version> — <title>" \
  --notes "<release-notes>"
```

Include highlights, grouped changes, test count, and changelog comparison link.

### Step 9: Post-Release (if applicable)

If docs site exists (`mkdocs.yml`, `_quarto.yml`, or `docs/`):

```bash
mkdocs build --strict && mkdocs gh-deploy  # or /craft:site:deploy
```

`mkdocs build --strict` fails on broken links and Jinja errors. Fix before deploying — a
broken deploy is harder to roll back than a local build failure.

### Step 10: Update Homebrew Tap (if applicable)

If the project has a Homebrew formula or cask in the `data-wise/tap`, update it with the new version.
Detects formula vs. cask from `.craft/homebrew.json` → Tauri → git remote → basename fallback.
Full detection script, Step 10a (formula update), and Step 10b (Tauri cask pipeline) are in
[`references/homebrew.md`](references/homebrew.md).

### Step 11: Sync Dev with Main

```bash
git checkout dev && git pull origin main
git push  # sync origin/dev
```

### Step 12: Verify CI on Main (MANDATORY)

Poll `gh run list --branch main` after merge. Fix immediately if CI fails — the tag points to
broken code. Full polling commands in pipeline-steps.md.

### Step 13: Verify Downstream Workflows (MANDATORY)

Verify docs deploy, homebrew-release workflow, live site version, formula content, CI badge,
and (if 10b ran) cask SHA256. Full scripts for 13a–13f are in
[`references/downstream-verification.md`](references/downstream-verification.md).

**Live-site version check (run after docs deploy):**

```bash
curl -s https://data-wise.github.io/craft/ | grep -o 'v[0-9]\+\.[0-9]\+\.[0-9]\+' | head -1
```

Must match the just-released version. If stale, wait 60s and retry (GitHub Pages CDN lag);
if still wrong after 3 retries, redeploy with `mkdocs gh-deploy`.

### Step 13.4: Doc Coverage Gate (MANDATORY)

`bash scripts/doc-coverage-check.sh` — blocks on missing REFCARD rows or mkdocs nav entries.
Fix with `refcard-gen.sh` and `mkdocs.yml` edits. Full guidance in downstream-verification.md.

### Step 13.5: Post-Release Sweep (RECOMMENDED)

`./scripts/post-release-sweep.sh --fix` — catches Tier 2+ version drift not managed by
bump-version.sh. Commit any changes. Full tier table in downstream-verification.md.

### Step 13.6: Surface Registry Phase

Auto-runs when `.claude-plugin/plugin.json` is present. Propagates the release across the
surface registry and asserts ONE version across every registered surface.

**Registry-driven propagation (runs before verify):**

1. **Aggregator CI action** — the `aggregator-sync.yml` workflow fires on `release: published`
   and opens + auto-merges a PR in `Data-Wise/claude-plugins`. If the PR is not merged within
   the timeout the action exits 1 (fail-loud: blocking — craft#218 Q2 gate).
2. **Advisory pins** — `brew upgrade craft` and `claude plugin update craft@local-plugins`
   are emitted as one-time advisory reminders (WARN; not blocking).
3. **Cowork surface** — a Cowork report is generated and a remind is queued (WARN; manual
   `claude plugin marketplace add`; non-blocking).

**Pre-ship gate (manual, before release):** verify the GitHub App has `contents: write` and
`pull-requests: write` permissions on `Data-Wise/claude-plugins`. Without these permissions the
aggregator CI action cannot open or merge PRs and will fail at runtime.

**Surface matrix:**

| Surface | Gate | Propagation |
|---------|------|-------------|
| git-tag | BLOCK | `gh release create` (existing) |
| marketplace.json | BLOCK | `bump-version.sh` (existing) |
| tap formula | BLOCK | `homebrew-release` workflow |
| brew-installed | WARN | advisory `brew upgrade` reminder |
| Code-registered | WARN | advisory `plugin update` reminder |
| aggregator | BLOCK | `aggregator-sync.yml` CI action (auto-merge PR) |
| Cowork | WARN | Cowork report + remind (manual store) |
| Desktop | INFO | DXT store; report only |

**Verify half (retained from prior behavior):** After propagation, `scripts/verify-surfaces.sh`
asserts each BLOCK surface has landed the expected version. Injectable overrides (`SURFACES_*`
env vars) allow surface verification in test/CI without live machine state. Bypass the entire
step with `--skip-surfaces` (e.g. a non-plugin release or deliberate partial publish).

Full implementation — trigger condition, aggregator snippet, BLOCK/WARN table, and absent-leg
handling — is in [`references/downstream-verification.md`](references/downstream-verification.md).

### Step 13.7: Prune Version Cache (maintenance)

`./scripts/cache-prune.sh` (dry-run) then `--prune`. Keeps current + 2 most recent plugin
version dirs. Never blocks release. Detail in downstream-verification.md.

## Output Format

Display progress using box-drawing:

```
┌─────────────────────────────────────────────────────────────┐
│ /release v2.17.0                                            │
├─────────────────────────────────────────────────────────────┤
│ [ 1/13] CI mirror check .................... PASSED          │
│ [ 2/13] Release metadata check ............. PASSED          │
│ [ 3/13] Version bump ....................... DONE             │
│ [ 4/13] Commit and push ................... DONE              │
│ [ 5/13] Release PR created ................. PR #70          │
│ [ 6/13] CI monitoring ..................... GREEN (90s)       │
│ [ 7/13] PR merged .......................... DONE             │
│ [ 8/13] GitHub release ..................... v2.17.0          │
│ [ 9/13] Docs deployed ..................... DONE              │
│ [10/13] Homebrew tap updated .............. DONE              │
│ [11/13] Dev synced ........................ DONE               │
│ [12/13] Verify CI on main ................. PASSED            │
│ [13/13] Downstream verification ........... ALL GREEN         │
├─────────────────────────────────────────────────────────────┤
│ Release URL: https://github.com/.../releases/tag/v2.17.0   │
└─────────────────────────────────────────────────────────────┘
```

## Error Recovery

| Error | Recovery |
|-------|----------|
| Pre-flight fails | Fix issues, re-run check |
| PR body triggers branch guard | Rephrase to avoid literal command strings |
| Branch protection blocks merge | Use `--admin` with user confirmation |
| Tag already exists | Verify correct version, delete stale tag if needed |
| Docs deploy fails | Run `mkdocs build` first to check for errors |

Step 10b (desktop app) error recovery table is in
[`references/homebrew.md`](references/homebrew.md).

## Additional Resources

### Reference Files

- **`references/pipeline-steps.md`** — Full command detail for Steps 1–9 and 11–12
- **`references/autonomous-mode.md`** — Autonomous mode safety checks, scripts, and error boxes
- **`references/homebrew.md`** — Step 10 complete: formula update, Tauri cask pipeline, error recovery
- **`references/downstream-verification.md`** — Steps 13a–13.7: downstream checks, sweep, surfaces
- **`references/release-checklist.md`** — Detailed per-project-type checklists and edge cases
