# Release Checklist Reference

## Craft Plugin Release Checklist

### Pre-Release

- [ ] `/craft:check --for release` passes (full CI mirror: tests, lint, security, coverage)
- [ ] `./scripts/pre-release-check.sh <version>` passes (metadata: version, counts)
- [ ] plugin.json version matches target
- [ ] CLAUDE.md version references updated
- [ ] CLAUDE.md test counts accurate
- [ ] Working tree clean
- [ ] Dev branch up to date with remote

### Release

- [ ] Version bumped in plugin.json
- [ ] Version bumped in CLAUDE.md (header + test table)
- [ ] README.md updated (version badge, skill/test counts, tagline)
- [ ] docs/index.md updated (latest release info box title and description)
- [ ] mkdocs.yml updated (site_description tagline for new release)
- [ ] docs/REFCARD.md updated (version, skill count, test count)
- [ ] Commit: `chore: bump version to v<version> for release`
- [ ] Push to dev
- [ ] PR created: dev -> main
- [ ] PR merged (NO --delete-branch)
- [ ] GitHub release created with --target main
- [ ] Release notes include highlights, changes, test stats

### Post-Release

- [ ] Docs site deployed (mkdocs gh-deploy)
- [ ] Dev synced with main
- [ ] .STATUS file updated (optional)
- [ ] CI passes on main
- [ ] Deploy Documentation workflow succeeds
- [ ] Homebrew Release workflow succeeds
- [ ] Live site shows new version
- [ ] Formula content verified (version, SHA, desc counts)
- [ ] `brew info` shows new version
- [ ] Main and dev CI badges show passing

## Python Package Release Checklist

### Pre-Release

- [ ] All tests passing
- [ ] pyproject.toml version matches target
- [ ] CHANGELOG.md updated
- [ ] Working tree clean

### Release

- [ ] Version bumped in pyproject.toml
- [ ] Version bumped in __init__.py (if applicable)
- [ ] Commit and push
- [ ] PR merged to main
- [ ] GitHub release created
- [ ] PyPI publish via GitHub Actions (trusted publishing)

### Post-Release

- [ ] Verify PyPI page shows new version
- [ ] Update Homebrew formula if applicable

## Node Package Release Checklist

### Pre-Release

- [ ] All tests passing (npm test)
- [ ] package.json version matches target
- [ ] CHANGELOG.md updated
- [ ] package-lock.json up to date

### Release

- [ ] npm version <patch|minor|major>
- [ ] Push with tags
- [ ] GitHub release created
- [ ] npm publish

## Common Edge Cases

### Branch Guard False Positives

PR body text containing literal destructive git commands (like reset, clean, rm) triggers branch guard hooks. Rephrase descriptions to use indirect language:

- Instead of: "blocks git reset --hard"
- Write: "blocks dangerous git operations that discard changes"

### --delete-branch Danger

NEVER use `gh pr merge --delete-branch` on release PRs where head branch is `dev`. This deletes dev from the remote. Reserve --delete-branch for feature branch PRs only.

### Admin Merge Override

When branch protection blocks `gh pr merge`, use `--admin` flag. This requires:

1. User has admin access to the repository
2. Explicit user confirmation before running

### Version Detection Priority

1. `.claude-plugin/plugin.json` (Craft plugins)
2. `package.json` (Node projects)
3. `pyproject.toml` (Python projects)
4. `DESCRIPTION` (R packages)
5. Latest git tag (fallback)

### Semver Decision Guide

- **patch** (0.0.X): Bug fixes, documentation updates, test improvements
- **minor** (0.X.0): New features, new commands, new skills, non-breaking enhancements
- **major** (X.0.0): Breaking changes, API changes, major rewrites
