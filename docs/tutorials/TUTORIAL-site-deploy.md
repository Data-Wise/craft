# Tutorial: site:deploy — Deploy Docs to GitHub Pages

By the end of this tutorial you will have:

- Previewed a deployment with `--dry-run` before touching the live site
- Deployed a MkDocs/Quarto/pkgdown site to GitHub Pages
- Understood the pre-deployment checks that gate a real push

**Prerequisites:** craft installed, a docs site (MkDocs/Quarto/pkgdown) configured, GitHub Pages enabled on the repo.

---

## Step 1: Preview Before Deploying

Always dry-run first — this is a live-site push, not a local build:

```
/craft:site:deploy --dry-run
/craft:site:deploy -n
```

Example output:

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Deploy to GitHub Pages                             │
├───────────────────────────────────────────────────────────────┤
│ ✓ Detection:                                                  │
│   - Type: MkDocs                                              │
│   - Config: mkdocs.yml                                        │
│   - Site built: Yes (docs/ directory exists)                  │
│                                                               │
│ ✓ Deployment Plan:                                            │
│   - Command: mkdocs gh-deploy                                 │
│   - Target branch: gh-pages                                   │
│   - Will push: ~450 files (~2.3 MB)                           │
│                                                               │
│ ✓ Pre-deployment Checks:                                      │
│   - Git status: Clean                                         │
│   - Remote exists: Yes                                        │
│   - GitHub Pages: Enabled (deploy from gh-pages)              │
│                                                               │
│ ⚠ Warnings:                                                   │
│   • This will update the live site immediately                │
└───────────────────────────────────────────────────────────────┘
```

The dry run auto-detects the site generator (MkDocs, Quarto, or pkgdown) and reports what would happen without pushing anything.

---

## Step 2: Deploy for Real

Once the preview looks right:

```
/craft:site:deploy
```

This runs the generator's deploy command (`mkdocs gh-deploy`, Quarto's publish step, or pkgdown's equivalent) and pushes the built site to the `gh-pages` branch.

---

## Step 3: Know What Blocks a Deploy

The pre-deployment checks fail closed — a dirty git tree, a missing remote, or GitHub Pages not enabled will stop the deploy before anything is pushed. Resolve the reported issue and re-run.

---

## What's Next

- Run `/craft:site:deploy --dry-run` as a habit before any deploy — it's cheap and catches drift early.
- Pair with `/craft:docs:changelog` before a release deploy so the changelog and the live site move together.
- If the deploy is triggered automatically by CI on push to `main` (check `.github/workflows/docs.yml`), this command is for manual/local deploys only — don't run both for the same change.
