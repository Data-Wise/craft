---
description: Deploy documentation site to GitHub Pages
category: site
arguments:
  - name: dry-run
    description: Preview deployment without pushing to GitHub Pages
    required: false
    default: false
    alias: -n
deprecated: true
replaced-by: "skills/docs/site-management/"
---

# /craft:site:deploy - Deploy to GitHub Pages

Deploy documentation sites (Quarto, pkgdown, MkDocs) to GitHub Pages.

## Usage

```bash
# Preview deployment
/craft:site:deploy --dry-run
/craft:site:deploy -n

# Execute deployment
/craft:site:deploy
```

## Dry-Run Mode

Preview what will be deployed without actually pushing to GitHub Pages:

```bash
/craft:site:deploy --dry-run
/craft:site:deploy -n
```

### Example Output: MkDocs

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Deploy to GitHub Pages                             │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Detection:                                                  │
│   - Type: MkDocs                                              │
│   - Config: mkdocs.yml                                        │
│   - Site built: Yes (docs/ directory exists)                  │
│                                                               │
│ ✓ Deployment Plan:                                            │
│   - Command: mkdocs gh-deploy                                 │
│   - Target branch: gh-pages                                   │
│   - Repository: https://github.com/Data-Wise/craft            │
│   - Will push: ~450 files (~2.3 MB)                           │
│                                                               │
│ ✓ Pre-deployment Checks:                                      │
│   - Git status: Clean                                         │
│   - Remote exists: Yes                                        │
│   - GitHub Pages: Enabled (deploy from gh-pages)              │
│                                                               │
│ ⚠ Warnings:                                                   │
│   • This will update the live site immediately                 │
│   • Changes may take 1-2 minutes to appear                    │
│                                                               │
│ 📊 Summary: Deploy MkDocs site to gh-pages branch              │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

### Example Output: Quarto

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Deploy to GitHub Pages                             │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Detection:                                                  │
│   - Type: Quarto                                              │
│   - Config: _quarto.yml                                       │
│   - Output directory: _site/                                  │
│                                                               │
│ ✓ Deployment Plan:                                            │
│   - Command: quarto publish gh-pages                          │
│   - Target branch: gh-pages                                   │
│   - Repository: https://github.com/user/project               │
│                                                               │
│ ⚠ Warnings:                                                   │
│   • Site not built yet (will build before deployment)          │
│   • GitHub Pages not configured - will prompt for setup       │
│                                                               │
│ 📊 Summary: Build and deploy Quarto site                       │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

## Context Detection

Automatically detects documentation type:

| File | Type | Deploy Command |
|------|------|----------------|
| `mkdocs.yml` | MkDocs | `mkdocs gh-deploy` |
| `_quarto.yml` | Quarto | `quarto publish gh-pages` |
| `_pkgdown.yml` | pkgdown | Push `docs/` folder |

## Pre-deployment Checks

1. **Site Built** - Verifies output directory exists
2. **Git Status** - Checks for uncommitted changes
3. **Remote Repository** - Ensures remote is configured
4. **GitHub Pages** - Checks if Pages is enabled

## Deployment Process

### For MkDocs Sites

```bash
mkdocs gh-deploy
```

**What it does:**

1. Builds the site (`mkdocs build`)
2. Creates/updates `gh-pages` branch
3. Pushes to GitHub
4. GitHub Pages serves from that branch

### For Quarto Sites

```bash
quarto publish gh-pages
```

**What it does:**

1. Renders the site
2. Pushes to `gh-pages` branch
3. Configures GitHub Pages if needed

### For pkgdown Sites

```r
# Option 1: Push docs/ folder
pkgdown::build_site()
# Ensure GitHub Pages deploys from docs/ folder in Settings

# Option 2: Use usethis (recommended)
usethis::use_pkgdown_github_pages()
```

## Output

```
🚀 DEPLOYING TO GITHUB PAGES

Type: MkDocs
Branch: gh-pages
Repository: https://github.com/Data-Wise/craft

Building site...
✅ Site built

Deploying to gh-pages...
✅ Pushed to remote

✅ DEPLOYED SUCCESSFULLY

Live site: https://data-wise.github.io/craft/

Note: It may take 1-2 minutes to update.

💡 Check deployment status: /craft:code:ci-local
```

## GitHub Pages Setup

If GitHub Pages is not configured:

```
⚠️ GitHub Pages may not be configured

To enable:
1. Go to repository Settings
2. Click Pages (left sidebar)
3. Source: Deploy from branch
4. Branch: gh-pages / (root)
5. Save

Or run: gh repo edit --enable-pages
```

## Troubleshooting

**404 error after deployment:**

- Wait 1-2 minutes for Pages to update
- Check base URL in site config
- Verify GitHub Pages is enabled

**Build failed:**

- Check GitHub Actions logs
- Verify all dependencies are installed
- Check for broken links or invalid syntax

**Permission denied:**

- Check repository permissions
- Verify GitHub token has write access
- Check if branch protection rules block gh-pages

## See Also

- `/craft:site:build` - Build site locally
- `/craft:site:check` - Check site for issues
- `/craft:site:add` - Add Pages with Navigation Sync
- `/craft:site:audit` - Content Inventory & Audit
- `/craft:site:consolidate` - Merge Duplicate Content
- `/craft:site:create` - Full Documentation Site Wizard
- `/craft:site:nav` - Navigation Reorganization
- `/craft:site:progress` - Display comprehensive semester progress dashboard
- `/craft:site:publish` - Publish teaching site with preview workflow
- `/craft:site:status` - Documentation Site Dashboard
- `/craft:site:theme` - Quick Theme Changes
- Template: `templates/dry-run-pattern.md`
- Utility: `utils/dry_run_output.py`
- Specification: `docs/specs/SPEC-dry-run-feature-2026-01-15.md`
