# Release Workflow

Guide through the package/project release process.

## Purpose

Manage releases for:
- R packages (CRAN submission)
- npm packages
- GitHub releases
- Internal versioning

## Required Input

- **Project type**: R package, npm, general
- **Release type**: Major, minor, patch
- **Current version**: Or let me detect it
- **Changes**: What's new in this release

## Process

### Pre-Release Checklist

1. **Version bump**
   - Update version in DESCRIPTION/package.json
   - Update CHANGELOG/NEWS.md
   - Update any hardcoded versions

2. **Quality checks**
   - Run full test suite
   - Check code coverage
   - Run linters/style checks
   - Build documentation

3. **Documentation**
   - Update README if needed
   - Regenerate function docs
   - Check all examples work

4. **Final verification**
   - R CMD check (for R packages)
   - npm test (for npm packages)
   - Build succeeds

### Release Steps

5. **Commit changes**
   - "Prepare for vX.Y.Z release"

6. **Tag release**
   - `git tag vX.Y.Z`

7. **Push**
   - `git push && git push --tags`

8. **Create GitHub release**
   - Use tag
   - Add release notes

9. **Submit to repository** (if applicable)
   - CRAN submission
   - npm publish

## Output Format

```markdown
## Release Checklist: v[X.Y.Z]

### Pre-Release
- [ ] Version bumped in [files]
- [ ] NEWS.md/CHANGELOG updated
- [ ] Tests passing
- [ ] R CMD check: 0 errors, 0 warnings, 0 notes
- [ ] Documentation updated
- [ ] Examples verified

### Release
- [ ] Changes committed
- [ ] Tag created: vX.Y.Z
- [ ] Pushed to remote
- [ ] GitHub release created
- [ ] [CRAN/npm] submission completed

### Post-Release
- [ ] Bump to development version (X.Y.Z.9000)
- [ ] Announce release (if applicable)
```

## R Package Specifics

```r
# Version bump
usethis::use_version("minor")

# Update NEWS
usethis::use_news_md()

# Final checks
devtools::check()
devtools::check_win_devel()
devtools::check_rhub()

# Submit to CRAN
devtools::release()
```

## npm Package Specifics

```bash
# Version bump
npm version minor

# Publish
npm publish
```

## MCP Integration

Uses these tools when available:
- `r_check` - Run R CMD check
- `r_test` - Run test suite
- `r_coverage` - Check coverage

## Examples

**Request**: "Help me release v1.2.0 of my R package"

**Request**: "Create a patch release for a bug fix"

**Request**: "Guide me through CRAN submission checklist"

**Request**: "Prepare release notes from recent commits"

## Semantic Versioning

- **Major** (1.0.0): Breaking changes
- **Minor** (0.1.0): New features, backward compatible
- **Patch** (0.0.1): Bug fixes, backward compatible

## Tips

- Never skip the check phase
- Write clear, user-focused release notes
- Test installation from fresh environment
- Have a rollback plan
