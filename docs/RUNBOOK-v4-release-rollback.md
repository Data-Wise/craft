# Runbook: v4.0.0 Train Rollback (craft + folio)

**Written:** 2026-07-16, BEFORE any v4.0.0 or folio v1.0.0 tag exists (per T4.2's own
dependency-free scheduling — this runs ahead of T4.3, not after).
**Plan of record:** `ORCHESTRATE-folio-split.md` · `tasks/plan.md` (Risks table) ·
`docs/specs/SPEC-v4-rollback-runbook-2026-07-16.md`

**Sequencing invariant (state this before touching anything):** craft's `dev→main` PR (T4.4)
must not be opened until folio's T4.3 is fully released — tag pushed, GitHub release published,
`brew install data-wise/tap/folio` verified working. If folio's release fails or stalls partway,
craft MUST NOT tag v4.0.0. There is no valid state where craft ships v4.0.0 while folio's
v1.0.0 is broken or absent.

## Current state (as of this writing — verify again before acting, don't trust this doc)

- craft: latest tag `v2.61.2`, latest GitHub release `v2.61.2` (2026-07-09). No `v4.0.0` tag
  exists yet. `.claude-plugin/plugin.json` version bump to `v4.0.0` is T4.4, not yet started.
- folio: `origin/main` has no release at all — the extraction landed on `origin/dev` only
  (PR #1). `homebrew-tap/Formula/` has no `folio.rb` yet — it's created fresh in T4.3, not
  updated from a prior version.
- `homebrew-tap`'s release automation (`.github/workflows/homebrew-release.yml`) pushes
  **directly to `homebrew-tap`'s `main` branch** via a GitHub App token (App ID stored in
  `APP_ID`/`APP_PRIVATE_KEY` secrets) — there is no PR review step in that path. A rollback of
  the tap formula means reverting a direct commit on `main`, not closing a PR.

---

## Path A: Roll back craft's v4.0.0

Applies once craft has tagged/released v4.0.0 and it turns out to be bad (broken commands,
CI regression discovered post-release, etc.).

### A1. Identify the revert target

```bash
git -C ~/projects/dev-tools/craft log --oneline -5 main
# The dev→main merge commit for the v4.0.0 release PR is the revert target.
# It will be the merge-commit style PR from T4.4 (NOT squash — dev→main releases use
# merge-commit per this repo's own convention, so the individual feature commits are visible).
```

### A2. Revert on `main`

```bash
# CONFIRM WITH USER FIRST — this is a push to a protected branch.
git -C ~/projects/dev-tools/craft checkout main
git -C ~/projects/dev-tools/craft revert -m 1 <merge-commit-sha>
git -C ~/projects/dev-tools/craft push origin main   # requires PR per branch protection —
                                                       # open a revert PR, do not push directly
```

craft's `main` is PR-only (branch protection, 0 required reviewers, required status checks
apply) — the revert itself must go through a PR like any other change to `main`, it does not
bypass protection just because it's a rollback.

### A3. Re-point Homebrew

```bash
# CONFIRM WITH USER FIRST — direct push to homebrew-tap's main.
cd ~/projects/dev-tools/homebrew-tap
git checkout main && git pull
# Edit Formula/craft.rb: url -> the v2.61.2 tag tarball, sha256 -> its real sha256
#   (get via: curl -sL https://github.com/Data-Wise/craft/archive/refs/tags/v2.61.2.tar.gz | shasum -a 256)
git add Formula/craft.rb
git commit -m "revert: craft formula back to v2.61.2 (v4.0.0 rollback)"
git push origin main
brew update && brew upgrade craft   # verify the rollback actually installs
```

### A4. GitHub release / tag

Do NOT delete the `v4.0.0` tag or its GitHub release — leave it visible with a note
("superseded, see rollback") rather than erasing history. Deleting a published release/tag
that others may have already pulled creates more confusion than it resolves.

```bash
gh release edit v4.0.0 --repo Data-Wise/craft --notes "SUPERSEDED — rolled back due to <reason>. Use v2.61.2."
```

### A5. Secrets / App installation

No action needed — `APP_ID`/`APP_PRIVATE_KEY` and the GitHub App installation are shared
infrastructure, not release-specific. Idempotent; nothing to reverse.

---

## Path B: Roll back folio's v1.0.0

Applies once folio has released v1.0.0 (T4.3) and it turns out to be bad. This is folio's FIRST
real release — `origin/main` has never had a release before, so "rollback" here really means
"undo the very first release," not "revert to a prior version."

### B1. Yank the GitHub release + tag

```bash
# CONFIRM WITH USER FIRST.
gh release delete v1.0.0 --repo Data-Wise/folio --yes
git -C ~/projects/dev-tools/folio push origin :refs/tags/v1.0.0   # delete the remote tag
```

Unlike craft (Path A4), deleting rather than just annotating is appropriate here specifically
because this is folio's first-ever release — there's no prior version for users to have adopted
instead, so there's nothing a "superseded" note would be pointing them toward.

### B2. Revert `origin/main`

```bash
# CONFIRM WITH USER FIRST — push to a protected branch (once main-protection is configured
# per T4.3's own sub-step).
git -C ~/projects/dev-tools/folio checkout main
git -C ~/projects/dev-tools/folio revert -m 1 <the-dev-to-main-merge-commit>
# Open a revert PR — same branch-protection discipline as craft Path A2.
```

### B3. Remove the Homebrew formula entry

folio's formula (`homebrew-tap/Formula/folio.rb`) is CREATED FRESH in T4.3 — there is no prior
version to revert to. Rollback means removing it entirely, not downgrading it.

```bash
# CONFIRM WITH USER FIRST — direct push to homebrew-tap's main (same automation path as A3).
cd ~/projects/dev-tools/homebrew-tap
git checkout main && git pull
git rm Formula/folio.rb
git commit -m "revert: remove folio formula (v1.0.0 rollback)"
git push origin main
```

### B4. Unpublish from the marketplace

folio's marketplace entry (aggregator `marketplace.json`, propagated via folio's own
`aggregator-sync.yml`) needs its entry removed or reverted. **Verify the exact file path and
propagation mechanism at execution time** — this runbook was written before that entry existed
(T4.3 creates it), so don't trust a hardcoded path here; find it via `folio-split` plan docs'
references to the aggregator repo, or ask if unclear.

---

## Path C: Partial rollback — folio ships, craft doesn't

**This is the one case this runbook does NOT resolve — it needs a human decision, not an
assumption.**

> **Historical note (2026-07-19):** the v4.0.0 train completed without ever triggering this
> scenario — folio v1.0.0 released 2026-07-16 20:44, craft v4.0.0 released the same day at
> 15:57, and craft has since progressed to v4.2.0. The question below is dead-letter for the
> v4.0.0 train specifically, but stays here as a template for any future coordinated cross-repo
> release, where it remains open in principle.

Scenario: folio's T4.3 completes successfully (tagged, released, installable) — but craft's
T4.4 (the `dev→main` PR, tag, release) then fails, stalls, or is deliberately paused for an
extended period. At that point:

- folio v1.0.0 is live and usable on its own (it has no runtime dependency on craft's v4.0.0 —
  the split was designed as a clean extraction, not a versioned pair).
- craft is still at v2.61.2, with the folio-split code already merged to `dev` but not yet
  tagged/released to `main`.

**Open question, unresolved as of this writing:** is that a stable, acceptable end-state on its
own — folio out ahead, craft catching up later on its own schedule — or does folio need some
signal (a README note, a version-compat marker, a "craft v4.0.0 pending" flag) that the pairing
isn't complete yet?

Arguments for "stable, no signal needed": folio was deliberately designed with no cross-plugin
dependency on craft (see folio's own `CLAUDE.md`: "no cross-plugin dispatch in either
direction") — nothing about folio's functionality actually requires craft's v4.0.0 to exist.
A user who installs folio v1.0.0 today gets a fully working docs-authoring plugin regardless of
craft's version.

Arguments for "needs a signal": the two releases were planned and communicated (in commit
messages, PR descriptions, `.STATUS`) as one coordinated "v4.0.0 train" — a user who only reads
craft's side might reasonably expect folio and craft v4.0.0 to have shipped together, and be
confused finding folio available weeks before craft's matching release.

**Do not pick one of these and proceed silently if this scenario arises — surface this exact
question to the user first.**
