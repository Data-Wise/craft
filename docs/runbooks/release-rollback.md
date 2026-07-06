# Release Rollback — Manual Undo Runbook

## Purpose

A bad release has shipped — wrong version, broken artifact, or a surface that
disagrees with the rest (tag, GitHub release, Homebrew formula, docs site). This
runbook is the manual, per-surface undo procedure for that situation.

This is deliberately **not automated**. Per the locked GRILL/SPEC decision for this
runbook (see `docs/specs/SPEC-craft-review-followups-2026-07-06.md`), only the
*diagnostic* step below is automated — deciding what to undo, and actually undoing
it, stays manual and human-reviewed. Rollback touches published, externally-visible
artifacts (tags other people have pulled, a published GitHub release, a Homebrew
formula serving `brew install`); an automated undo risks compounding the mistake.

---

## How do I know if I need to do any of this?

Run the diagnostic first, don't guess:

```bash
./scripts/verify-surfaces.sh --report-only --version vX.Y.Z
```

This prints `ALIGNED`/`DRIFTED` per surface (marketplace.json, git tag, tap Formula,
brew-installed, Code-registered, GitHub release, docs-site version) for the release
in question, without blocking or exiting 1. Use it to scope the problem — a
`DRIFTED` GitHub-release leg only needs the GitHub Release section below, not a full
rollback across every surface. Re-run it after each undo step to confirm the surface
you touched is back to `ALIGNED`.

If `verify-surfaces.sh` itself isn't reachable (older checkout, script not yet
present), fall back to eyeballing each surface using the manual checks embedded in
the sections below.

---

## Git Tag

**Symptom:** the tag points at the wrong commit, or a tag was created for a release
that should not have shipped.

```bash
# Delete locally
git tag -d vX.Y.Z

# Delete on the remote
git push origin :refs/tags/vX.Y.Z
```

**Risk:** if anyone (a contributor, CI, a downstream consumer) has already fetched
the tag, deleting it on the remote does not remove it from their local clone or any
cache that resolved it (e.g. a Homebrew formula's `url` pinned to that tag's tarball,
a `go.mod` checksum, a pre-warmed CDN mirror of the GitHub archive). Treat tag
deletion as best-effort cleanup, not a guarantee the bad ref disappears everywhere.
If the tag has been out for more than a few minutes, prefer **moving forward** with a
new patch tag over deleting and reusing the same tag name — reusing a tag name after
deletion is confusing for anyone who already has the old commit cached under that
name.

To move the tag instead of deleting it (only if nobody downstream depends on the old
commit yet):

```bash
git tag -f vX.Y.Z <good-commit-sha>
git push --force origin refs/tags/vX.Y.Z
```

Force-pushing a tag is a shared-history rewrite — confirm no automation (release
workflow, tap sync) is mid-run against the old tag before doing this.

---

## GitHub Release

**Symptom:** the published GitHub release has the wrong notes, wrong artifacts, or
was cut from a bad tag.

Delete it:

```bash
gh release delete vX.Y.Z
```

Or, to keep the release visible but stop it from looking current, edit it in place
instead of deleting:

```bash
gh release edit vX.Y.Z --draft          # unpublish, keep as draft
# or
gh release edit vX.Y.Z --prerelease     # mark as pre-release, keeps it public but flagged
```

**Tag or release, or both?** `gh release delete` does not delete the underlying git
tag by default — the release and the tag are separate objects. Decide based on why
you're rolling back:

- Release notes/artifacts wrong, tag itself is fine → delete/edit the release only,
  leave the tag.
- The commit tagged was wrong → delete both (release first, then the tag per the
  section above) so a new release can reuse the version number cleanly.

---

## Homebrew Formula

**Symptom:** `brew install <plugin>` or `brew upgrade` installs the bad version.

The formula lives in the sibling `homebrew-tap` repo
(`~/projects/dev-tools/homebrew-tap`), not in this repo. Craft's release pipeline
pushes formula updates there as a separate commit.

1. In the tap repo, find the commit that bumped the formula to the bad version:

   ```bash
   cd ~/projects/dev-tools/homebrew-tap
   git log --oneline -- Formula/<plugin>.rb
   ```

2. Revert that commit (preferred over hand-editing — keeps history honest):

   ```bash
   git revert <bad-commit-sha>
   git push origin main
   ```

   If the tap's default branch is protected (PR-only), open a revert PR instead of
   pushing directly — see this workspace's standard PR flow (`gh pr create`).

3. Re-trigger the tap's own CI/verification so the reverted formula is confirmed
   installable before anyone else pulls it:

   ```bash
   gh workflow run <tap-ci-workflow>.yml   # or: gh run rerun --repo data-wise/homebrew-tap <run-id>
   ```

   Confirm the workflow name via `gh workflow list --repo data-wise/homebrew-tap` if
   unsure — tap CI workflow names can differ from this repo's.

4. Verify locally once CI is green:

   ```bash
   brew update
   brew upgrade <plugin>
   brew audit <plugin>
   ```

---

## Docs Site

**Symptom:** the deployed docs site (GitHub Pages, built by `mkdocs gh-deploy`)
shows content or a version string from the bad release.

Per this repo's `CLAUDE.md`, docs deploy is automatic: `docs.yml` triggers
`mkdocs gh-deploy` on every push to `main`. There is no separate manual deploy step
in the normal flow — rollback means getting a *good* commit back onto `main` and
letting the existing trigger redeploy from it.

**Preferred — revert on `main` and let CI redeploy:**

```bash
git revert <bad-commit-sha>   # on a PR branch, then merge to main per normal branch protection
```

Once the revert lands on `main`, `docs.yml` fires automatically and redeploys from
the reverted state. No manual `gh-deploy` call needed.

**Manual fallback — force a redeploy from a specific known-good commit** (use only
if you need the site fixed before a revert PR can merge, e.g. a security-sensitive
doc leak):

```bash
git checkout <last-good-commit-sha>
mkdocs gh-deploy --force
git checkout main   # return to normal branch state immediately after
```

`mkdocs gh-deploy --force` pushes straight to the `gh-pages` branch, bypassing the
normal `main`-triggered flow. Follow up with the proper revert PR on `main` so the
next automatic deploy doesn't undo the manual fix.

---

## After Rollback

Re-run the diagnostic to confirm every touched surface is back to `ALIGNED`:

```bash
./scripts/verify-surfaces.sh --report-only --version <last-good-version>
```

Record what happened and why in `CHANGELOG.md` (a `### Notes` or `### Fixed` entry
depending on severity) and in `.STATUS` if the rollback affected in-flight release
state.
