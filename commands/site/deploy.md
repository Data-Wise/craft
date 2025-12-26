# /site-deploy - Deploy to GitHub Pages

You are a documentation deployment assistant. Deploy the documentation site to GitHub Pages.

## Context Detection

Detect documentation type:

```
Detection Rules:
1. _quarto.yml exists → Quarto site
2. _pkgdown.yml exists → pkgdown site
3. mkdocs.yml exists → MkDocs site
```

## Pre-deployment Checks

1. Ensure site is built
2. Check git status (uncommitted changes?)
3. Verify remote repository exists

## For Quarto Sites

```bash
# Build and deploy
quarto publish gh-pages
```

Or push `docs/` directory if configured.

## For pkgdown Sites

```r
# Build site
pkgdown::build_site()

# Deploy (option 1: push docs/)
# Ensure GitHub Pages is set to deploy from docs/ folder

# Deploy (option 2: use usethis)
usethis::use_pkgdown_github_pages()
```

## For MkDocs Sites

```bash
mkdocs gh-deploy
```

This command:
1. Builds the site
2. Creates/updates `gh-pages` branch
3. Pushes to GitHub
4. GitHub Pages serves from that branch

## Output

```
🚀 DEPLOYING TO GITHUB PAGES

Type: [Quarto/pkgdown/MkDocs]
Branch: gh-pages
Repository: [repo URL]

Deployment started...

✅ DEPLOYED SUCCESSFULLY

Live site: https://[username].github.io/[repo]/

Note: It may take a few minutes to update.

💡 Check deployment status: /github/ci-status
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

Common issues:
- 404 error: Wait a few minutes, or check base URL
- Build failed: Check GitHub Actions logs
- Permission denied: Check repository permissions
