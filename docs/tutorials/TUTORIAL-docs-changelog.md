# Tutorial: docs:changelog — Auto-Update CHANGELOG.md

By the end of this tutorial you will have:

- Generated a CHANGELOG entry from recent git commits
- Previewed the entry before writing
- Understood the format used and how to customize it

**Prerequisites:** craft installed, a git repository with conventional commits.

---

## Step 1: Generate a Changelog Entry

```
/craft:docs:changelog
```

Analyzes commits since the last version tag and drafts a CHANGELOG entry:

```
Changelog Update — my-project
───────────────────────────────
Commits since v2.40.0: 12

Drafted entry for ## [2.41.0] — 2026-06-19:

### Added
- `/craft:quota` — pre-flight token quota gate with SAFE/TIGHT/DEFER advisory
- `--engine=workflow|fanout` flag on `/craft:orchestrate`

### Changed
- Expanded `git:guard` skill with `explain` and `profile` subcommands

### Fixed
- BSD sed no-op on CI (bump-version.sh portability)
- validate-counts.sh SKILL breakdown over-count

Write to CHANGELOG.md? [y/N/preview]
```

---

## Step 2: Preview Without Writing

```
/craft:docs:changelog --dry-run
```

Shows the drafted entry without touching `CHANGELOG.md`.

---

## Step 3: Limit the Commit Range

```
/craft:docs:changelog --since v2.40.0
/craft:docs:changelog --since 2026-06-01
```

Defaults to the most recent version tag if `--since` is omitted.

---

## Step 4: The Format Used

craft uses [Keep a Changelog](https://keepachangelog.com) format:

```
## [VERSION] — DATE
### Added
### Changed
### Fixed
### Deprecated
### Removed
```

The command maps conventional commit types automatically:

- `feat:` → Added
- `fix:` → Fixed
- `refactor:` → Changed
- `docs:` → omitted (documentation-only changes)
- `chore:` → omitted unless version bump

---

## What's Next

- Use as Step 3b of the release pipeline to populate `CHANGELOG.md`
- Both `CHANGELOG.md` (root) and `docs/CHANGELOG.md` must stay in sync — update both
- See [release pipeline tutorial](TUTORIAL-release-pipeline.md) for where changelog fits
