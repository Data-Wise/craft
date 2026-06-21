# Plugin Release Runbook

A repeatable, copy-pasteable sequence for shipping a Data-Wise Claude-Code plugin so that **every
install surface actually serves the new version** — no silent drift. Works for any plugin
distributed via the Homebrew tap and/or a local marketplace (scholar, savant, craft, rforge).

> **One rule above all:** a *new version number* is the only thing that propagates. Re-tagging or
> re-publishing the *same* version with different content will **not** update installs, because the
> plugin system keys on the version string. When in doubt, **bump the version.**

## The chain (in order)

1. **Land the change on `dev`.** Feature → `dev` PR, CI green (tests + `version-sync --gate`).
2. **Bump the version** on a release branch. Edit the **authoritative source** (`package.json` for
   scholar; `.claude-plugin/plugin.json` / repo convention for others), then propagate:

   ```bash
   node scripts/version-sync.js          # propagate to README/CLAUDE/plugin.json/mkdocs/docs
   node scripts/version-sync.js --gate   # must report 0 errors
   ```

   Choose the bump by SemVer: a new skill/command = **minor**; fixes = **patch**.
3. **Finalize docs** (this is where drift hides — `version-sync` updates *numbers*, not *prose*):
   - Move `CHANGELOG [Unreleased]` → `[X.Y.Z]` with the date.
   - Add `docs/WHATS-NEW-vX.Y.Z.md` and put it in the mkdocs **Release Notes** nav.
   - Grep for stale current-state claims the sync can't know about
     (e.g. `grep -rn "0 skills" README.md docs/`), and fix them.
4. **Release to `main` + tag.** `dev → main` PR, merge, then:

   ```bash
   git tag vX.Y.Z && git push --tags     # creates the GitHub tarball the tap will hash
   ```

5. **Refresh every consumer** (this is the step most often skipped → drift):
   - **Homebrew tap** — bump `Formula/<plugin>.rb`:

     ```bash
     # url -> .../tags/vX.Y.Z.tar.gz, then:
     curl -sL https://github.com/Data-Wise/<plugin>/archive/refs/tags/vX.Y.Z.tar.gz | shasum -a 256
     # paste into sha256, open the tap PR, merge
     brew upgrade <plugin>
     ```

   - **Claude Code / Cowork** —

     ```bash
     claude plugin marketplace update <marketplace>
     claude plugin update <plugin>@<marketplace>   # restart to apply
     ```

     For the private path (PII plugins), the marketplace is the plugin's own private repo:
     `claude plugin marketplace add Data-Wise/<plugin>` then `plugin install <plugin>@<self-marketplace>`.
6. **Verify, then clean up.** `python3 ~/.claude/scripts/skills-audit.py` should show **0 red**
   (consumer pin == canon version). Archive any local duplicate that the plugin now serves.

## The version-collision pitfall (worked example: scholar 3.1.0)

scholar's first teaching skill, `statistical-pedagogy-framework`, merged to **`dev`** *after*
`v3.0.1` was tagged. The Homebrew bottle and the `claude plugin` cache were both built from the
`v3.0.1` tarball — which **predates the skill** — so the installed scholar kept shipping **0 skills**
even though the repo said `3.0.1`. Because installs key on the *number*, no `plugin update` could
ever fix it. The resolution was a clean **3.1.0** (escaping the `3.0.1` content-collision), tag, tap
sha refresh, and `brew upgrade`. The lesson is baked into step 2's rule.

## Guard rails

- **Drift doctor:** `~/.claude/scripts/skills-audit.py` (and the governance `run_rules.py`
  `R07-version-is-truth`) flag any consumer pin that lags the canon version.
- **Self-heal:** `~/.claude/scripts/fix-local-plugins.sh` auto-bumps release-versioned local
  plugins each session.
- **Automation gap:** making step 5 part of the release command (so installs can't lag) is tracked
  in craft issue #184. Until then, run step 5 by hand every release.

See also: [Homebrew Automation](homebrew-automation.md), [Marketplace
Distribution](marketplace-distribution.md), [Skill-Ecosystem Governance](governance.md).
