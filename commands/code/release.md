---
description: Release Workflow
category: code
---

# Release Workflow

Guide through the package/project release process. For Craft plugin projects, delegates to the `/release` skill which provides a comprehensive 13-step pipeline.

## Craft Plugin Projects

For Craft plugins (detected by `.claude-plugin/plugin.json`), invoke the **release skill** which provides:

- 13-step automated pipeline (version detect → CI mirror → metadata check → bump → commit → PR → merge → GitHub release → docs deploy → Homebrew tap → dev sync → verify CI → downstream verification)
- `--dry-run` mode for previewing actions
- Pre-flight validation via `/craft:check --for release` + `pre-release-check.sh`

**Trigger:** Say "release", "ship it", "cut a release", or run `/release`

See `skills/release/SKILL.md` for the full pipeline specification.

## General Projects

For non-Craft projects, follow the project-type-specific checklists below.

### Pre-Release Checklist

1. **Version bump** — Update version in DESCRIPTION/package.json, CHANGELOG/NEWS.md, hardcoded versions
2. **Quality checks** — Full test suite, code coverage, linters, build documentation
3. **Documentation** — Update README, regenerate function docs, check examples
4. **Final verification** — R CMD check / npm test / build succeeds

### Release Steps

5. **Commit changes** — "Prepare for vX.Y.Z release"
6. **Tag release** — `git tag vX.Y.Z`
7. **Push** — `git push && git push --tags`
8. **Create GitHub release** — Use tag, add release notes
9. **Submit to repository** (if applicable) — CRAN submission / npm publish

## R Package Specifics

```r
usethis::use_version("minor")
usethis::use_news_md()
devtools::check()
devtools::check_win_devel()
devtools::check_rhub()
devtools::release()
```

## npm Package Specifics

```bash
npm version minor
npm publish
```

## Semantic Versioning

- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features, backward compatible
- **Patch** (0.0.X): Bug fixes, backward compatible

## Tips

- Never skip the check phase
- Write clear, user-focused release notes
- Test installation from fresh environment
- Have a rollback plan
