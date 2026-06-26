# Downstream Verification Reference (Steps 13+)

Full implementation for Steps 13a–13.7: downstream workflow verification, doc coverage gate,
post-release sweep, surface assertion, and version cache pruning.

## Table of Contents

- [Step 13: Verify Downstream Workflows](#step-13-verify-downstream-workflows-mandatory)
- [Step 13.4: Doc Coverage Gate](#step-134-doc-coverage-gate-mandatory)
- [Step 13.5: Post-Release Sweep](#step-135-post-release-sweep-recommended)
- [Step 13.6: Surface Registry Phase](#step-136-surface-registry-phase)
- [Step 13.7: Prune Version Cache](#step-137-prune-version-cache-maintenance)

## Step 13: Verify Downstream Workflows (MANDATORY)

After CI passes on main, verify all downstream workflows and artifacts are correct. This catches silent failures in deploy pipelines, Homebrew distribution, and badge rendering.

#### 13a: Deploy Documentation Workflow

```bash
# Check the latest docs deploy workflow run
gh run list --workflow=docs.yml --limit 1 \
  --json status,conclusion,createdAt --jq '.[0]'
```

If `conclusion` is not `success`, check logs with `gh run view <id> --log-failed`.

#### 13b: Homebrew Release Workflow

```bash
# Check the latest homebrew-release workflow run
gh run list --workflow=homebrew-release.yml --limit 1 \
  --json status,conclusion,createdAt --jq '.[0]'
```

If `conclusion` is not `success`, check with `/craft:ci:status` for diagnosis.

#### 13c: Live Site Version

```bash
# Verify the live docs site shows the new version
curl -sL https://data-wise.github.io/craft/ | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+'
```

Compare the extracted version string against the release version. If stale, the docs workflow may have failed silently.

#### 13d: Formula Content Verification

```bash
# Fetch formula from the tap repo and verify version + SHA
gh api repos/Data-Wise/homebrew-tap/contents/Formula/craft.rb \
  --jq '.content' | base64 -D | grep -E '(version|sha256|desc)'

# Also verify via brew info
brew info data-wise/tap/craft
```

Confirm: version matches release, SHA256 is non-empty and 64 chars, description is present.

#### 13e: Badge Validation

```bash
# Fetch the main CI badge and check for "passing"
curl -sL "https://github.com/Data-Wise/craft/actions/workflows/ci.yml/badge.svg" | grep -q "passing" \
  && echo "Badge: PASSING" || echo "Badge: NOT PASSING"
```

If the badge does not show "passing", CI may still be running or may have failed. Wait and re-check.

#### 13f: Cask Verification (Tauri projects only)

If Step 10b was executed (desktop app release), verify the cask was updated correctly:

```bash
# Refresh tap data
brew update

# Verify cask version matches release
CASK_VERSION=$(brew info --cask "$TAP/$FORMULA_NAME" 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
if [ "$CASK_VERSION" = "$VERSION" ]; then
    echo "Cask version: CORRECT ($CASK_VERSION)"
else
    echo "Cask version: MISMATCH (expected $VERSION, got $CASK_VERSION)"
fi

# Verify SHA256 in cask file matches what we computed
CASK_FILE_CONTENT=$(gh api "repos/${TAP_ORG}/homebrew-${TAP_NAME}/contents/Casks/${FORMULA_NAME}.rb" \
  --jq '.content' | base64 -D)

# Check ARM SHA256
if echo "$CASK_FILE_CONTENT" | grep -q "$SHA256_ARM"; then
    echo "SHA256 (ARM): CORRECT"
else
    echo "SHA256 (ARM): MISMATCH — cask may have stale hash"
fi

# Check Intel SHA256
if echo "$CASK_FILE_CONTENT" | grep -q "$SHA256_INTEL"; then
    echo "SHA256 (Intel): CORRECT"
else
    echo "SHA256 (Intel): MISMATCH — cask may have stale hash"
fi

# Report install command for manual verification
echo ""
echo "Manual verification:"
echo "  brew install --cask $TAP/$FORMULA_NAME"
echo "  brew upgrade --cask $TAP/$FORMULA_NAME"
```

**What this catches:**

- Tap push failed silently (version mismatch)
- SHA256 was overwritten by a conflicting push (hash mismatch)
- `brew update` cache issues (stale version)

## Step 13.4: Doc Coverage Gate (MANDATORY)

Before sweeping for drift, verify all commands shipped in this release have their doc surfaces. This check is performed by `pre-release-check.sh` (Task 5 above already wired it in). If you skipped `pre-release-check.sh`, run manually:

```bash
bash scripts/doc-coverage-check.sh
```

**Blocking:** Missing REFCARD rows or mkdocs nav entries → fix before continuing.
**Warning:** Missing tutorials (commands with `arguments:`) → add tutorial before next release but does not block.

If gaps found, fix them:

1. Add missing REFCARD rows: `bash scripts/refcard-gen.sh --category <cat>`  (copy rows to docs/REFCARD.md)
2. Add missing nav entries to `mkdocs.yml`
3. Re-run `bash scripts/doc-coverage-check.sh` until exit 0

```bash
git add docs/REFCARD.md mkdocs.yml
git commit -m "docs: add doc surfaces for newly shipped commands"
```

## Step 13.5: Post-Release Sweep (RECOMMENDED)

After downstream verification passes, run the post-release sweep to catch Tier 2+ drift — secondary version references, stale counts, and content staleness that `bump-version.sh` doesn't manage.

```bash
# Normal mode: auto-fix mechanical items, commit if changes made
./scripts/post-release-sweep.sh --fix
# If fixes were applied:
git add -u && git commit -m "chore: fix post-release drift detected by sweep"
git push
```

**Dry-run mode:** Run report-only (no changes):

```bash
./scripts/post-release-sweep.sh
```

**Autonomous mode:** Same as normal mode — auto-fix is safe for mechanical items (version string replacements in secondary docs).

**What it catches:**

| Tier | Scope | Fix Mode |
|------|-------|----------|
| 1 | Core files (via `bump-version.sh --verify`) | Auto |
| 2 | Secondary docs (REFCARD-RELEASE, guides, etc.) | Auto (`--fix`) |
| 2 | Stale test/command counts in docs | Manual review |
| 3 | Content staleness (CHANGELOG vs index.md) | Manual review |

If `--fix` makes changes, commit them before completing the release.

## Step 13.6: Surface Registry Phase

After the sweep, propagate the release through the surface registry and assert that ONE version
landed on every registered surface. The registry (`scripts/surfaces/registry.json`) is the
source of truth for which surfaces exist and what gate they carry.

### Registry-driven propagation

**Step 13.6a — Aggregator CI action (BLOCK gate, craft#218):**

The `aggregator-sync.yml` GitHub Actions workflow fires automatically on `release: published`.
It:

1. Opens a version-bump PR in `Data-Wise/claude-plugins` (the aggregator marketplace repo)
2. Merges the PR with `gh pr merge --admin --squash`
3. Verifies `state == "MERGED"` — if not merged, exits 1 (fail-loud)

If the workflow fails: check `gh run list --workflow=aggregator-sync.yml` and verify the GitHub
App has `contents: write` and `pull-requests: write` on `Data-Wise/claude-plugins`.

**Step 13.6b — Advisory pins (WARN only, non-blocking):**

After a successful release, the pipeline emits reminder output for manual-only surfaces:

```
⚠️  Advisory: brew upgrade craft  (brew-installed surface)
⚠️  Advisory: claude plugin update craft@local-plugins  (Code-registered surface)
```

These are informational — they are recorded in the `.STATUS` surfaces matrix via
`--write-status` but do NOT block completion.

**Step 13.6c — Cowork surface (WARN only, non-blocking):**

The Cowork surface tracks craft via its own plugin registry (separate GUI store). The pipeline
generates a Cowork report and queues a remind. A mismatch here is WARN only — the Cowork store
requires a manual `claude plugin marketplace add` update outside the automated pipeline.

**Pre-ship gate (manual, one-time per App setup):**

Before shipping any release that uses the aggregator CI action, verify:

- The GitHub App is installed on `Data-Wise/claude-plugins`
- The App has `contents: write` and `pull-requests: write` permissions
- The `APP_ID` and `APP_PRIVATE_KEY` secrets are set in the source repo

Run this check once; App permissions persist until explicitly changed.

### Verify half (run after propagation)

```bash
# Auto-runs when this repo ships a plugin; --skip-surfaces bypasses.
if [[ -f .claude-plugin/plugin.json && "$SKIP_SURFACES" != true ]]; then
  NAME=$(python3 -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['name'])")
  VER=$(python3 -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['version'])")

  # Aggregator sync happens via the CI action (aggregator-sync.yml) on release: published.
  # If running verify manually post-release, you may pass an aggregator file to check the leg:
  AGG="${DATA_WISE_AGGREGATOR_FILE:-}"
  ./scripts/verify-surfaces.sh --write-status \
    --aggregator Data-Wise/claude-plugins \
    ${AGG:+--aggregator-file "$AGG"}
fi
```

**Surface matrix — gate levels and verify behavior:**

| Surface | Gate | Source | On mismatch | Injectable override |
|---------|------|--------|-------------|---------------------|
| marketplace.json | BLOCK | `.claude-plugin/marketplace.json` | exit 1 | — |
| git tag | BLOCK | `git describe` | exit 1 | `SURFACES_GIT_TAG` |
| tap formula | BLOCK | `Formula/<name>.rb` | exit 1 | `SURFACES_TAP_FORMULA` |
| brew-installed | WARN | `brew list --versions <name>` | warn only | `SURFACES_BREW_VERSION` |
| Code-registered | WARN | `~/.claude/plugins/installed_plugins.json` | warn only | `SURFACES_INSTALLED_PLUGINS` |
| aggregator | BLOCK | aggregator `marketplace.json` entry | exit 1 | `--aggregator-file` |
| Cowork | WARN | `cowork_plugins/` store | warn only | `SURFACES_COWORK_STORE` |
| Desktop | INFO | DXT store | info only | — |

An **absent/unreadable** source is `⚠️ not verified` — it does NOT block. Only a
**present-but-mismatched** craft-controlled BLOCK surface fails the release (exit 1).

**Bypass:** `--skip-surfaces` skips the entire Step 13.6 (e.g. a non-plugin release or
deliberate partial publish). The `/craft:dist:surfaces` command provides a read-only view of
the registry and current gate states at any time.

## Step 13.7: Prune Version Cache (maintenance)

Claude Code never garbage-collects old plugin versions under
`~/.claude/plugins/cache/local-plugins/<name>/<version>/`, so they accumulate. After a successful
release, prune them — keeping **current + 2 most recent** per plugin (D7). Always dry-run first;
the prune step reports every directory it removes (never a silent delete).

```bash
./scripts/cache-prune.sh            # dry-run: report what would be removed
./scripts/cache-prune.sh --prune    # actually remove old version dirs
```

Maintenance only — never blocks the release (exit 0 always). Distinct from `claude plugin prune`,
which GCs unused *dependency* plugins rather than the per-version cache.
