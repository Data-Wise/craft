# Documentation & Website Pre-flight Check

Perform comprehensive documentation validation before deployment for any project in `~/projects/`.

## Project Type Detection

First, detect the project type by examining:

- `package.json` → npm/Node.js project
- `DESCRIPTION` → R package (use pkgdown)
- `mkdocs.yml` → MkDocs documentation site
- `_quarto.yml` → Quarto project
- `pyproject.toml` or `setup.py` → Python project

## Validation Workflow

### Phase 1: Version Sync Check

Check version consistency across files based on project type:

**npm/Node.js projects:**

- `package.json` version
- `src/index.ts` or `src/index.js` VERSION constant (if exists)
- `CLAUDE.md` version reference
- Extension files (e.g., `_extensions/*/extension.yml`)

**R packages:**

- `DESCRIPTION` Version field
- `NEWS.md` version entries
- `CLAUDE.md` version reference
- `_pkgdown.yml` if exists

**All projects:**

- Report any version mismatches
- Suggest which file to update

### Phase 2: Badge Validation

Scan README.md for badges and validate:

**Dynamic badges (GOOD):**

```markdown
![npm version](https://img.shields.io/npm/v/PACKAGE)
![CI](https://img.shields.io/github/actions/workflow/status/...)
![Coverage](https://codecov.io/gh/...)
```

**Static badges (FLAG THESE):**

```markdown
![version](https://img.shields.io/badge/version-X.Y.Z-blue)
```

Report:

- List all badges found
- Flag any static version badges that should be dynamic
- Verify badge URLs are valid (use WebFetch to check)

### Phase 3: Link Validation

Scan documentation files for broken links:

**Internal links:**

- `[text](page.md)` - verify file exists
- `[text](#anchor)` - verify anchor exists
- `[text](../path)` - verify relative path resolves

**GitHub links:**

- `github.com/OWNER/REPO/blob/main/PATH` - verify path exists in repo
- `github.com/OWNER/REPO/tree/main/PATH` - verify directory exists

**External links:**

- Check reachability with WebFetch (sample, not exhaustive)

Report all broken links with file:line references.

### Phase 4: mkdocs.yml / _pkgdown.yml Validation

**For MkDocs projects:**

- Verify all `nav:` entries point to existing files
- Check for orphan pages (files in docs/ not in nav)
- Validate required sections exist per Data-Wise standards
- Check theme configuration

**For R packages with pkgdown:**

- Verify `_pkgdown.yml` structure
- Check reference organization
- Validate article paths

### Phase 5: Build Test

Run the appropriate build command:

**MkDocs:**

```bash
mkdocs build --strict
```

**pkgdown:**

```bash
Rscript -e "pkgdown::build_site()"
```

**npm with docs:**

```bash
npm run build  # if build script exists
```

Report any build errors or warnings.

### Phase 6: Local Preview

Start local server for user review:

**MkDocs:**

```bash
mkdocs serve  # http://localhost:8000
```

**pkgdown:**

```bash
Rscript -e "pkgdown::preview_site()"
```

Tell user: "Preview available at [URL]. Review and confirm when ready."

### Phase 7: User Confirmation

Use AskUserQuestion to ask:

- "Does the preview look correct?"
- "Ready to deploy?"

Options:

1. "Yes, deploy now"
2. "No, I need to fix something"
3. "Skip deployment, just show report"

### Phase 8: Deploy (if confirmed)

**Git workflow:**

```bash
git add -A
git status  # Show what will be committed
git commit -m "docs: [auto-generated summary]"
git push origin main
```

**Monitor deployment:**

- Start `gh run list` monitoring in background
- Check workflow status every 10 seconds
- Report when deployment completes

### Phase 9: Verification

After deployment:

- Wait for GitHub Actions to complete
- Fetch live site with WebFetch to verify deployment
- Compare key content to ensure updates are live
- Report success with live URL

## Output Format

```markdown
## Documentation Check Report
**Project**: [name] ([type])
**Path**: [path]
**Date**: [timestamp]

### Version Sync
| File | Version | Status |
|------|---------|--------|
| package.json | 0.6.6 | ✓ |
| CLAUDE.md | 0.6.6 | ✓ |

### Badges
- ✓ npm version (dynamic)
- ✓ CI status (dynamic)
- ⚠ License badge (static but OK)

### Links
- ✓ 45 internal links valid
- ✗ 2 broken links found:
  - docs/guide.md:23 → [missing.md](missing.md)
  - README.md:45 → https://old-url.com

### Build
- ✓ mkdocs build successful (0.8s)
- ⚠ 1 warning: [warning text]

### Deployment Status
- [ ] Pending user confirmation
- [ ] Git commit
- [ ] Push to origin
- [ ] GitHub Actions
- [ ] Live verification

### Actions Required
1. Fix broken link in docs/guide.md:23
2. Update old URL in README.md:45
```

## Skills Integration

This command integrates with existing skills:

- `doc-management` - For commit message standards
- `data-wise-documentation` - For Data-Wise specific checks

## Notes

- Run from project root directory
- Requires: git, mkdocs (for MkDocs projects), R + pkgdown (for R packages)
- GitHub CLI (`gh`) required for deployment monitoring
- Use `--skip-deploy` argument to only run validation without deployment
- Use `--quick` argument to skip link validation and preview

## Example Usage

```
/docs-check              # Full check with deployment
/docs-check --quick      # Quick validation only
/docs-check --skip-deploy # Validate but don't deploy
```
