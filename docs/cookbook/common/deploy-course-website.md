---
title: "Recipe: Deploy Course Website"
description: "Safely publish course site updates with preview-before-publish workflow"
category: "cookbook"
level: "beginner"
time_estimate: "3 minutes"
related:
  - ../../../commands/site/deploy.md
  - ../../../commands/site/build.md
  - ../../../commands/site/check.md
---

# Recipe: Deploy Course Website

**Time:** 3 minutes
**Level:** Beginner
**Prerequisites:** Teaching mode detected (course site with Quarto/MkDocs/pkgdown)

## Problem

I want to safely publish course website updates to GitHub Pages without breaking existing content.

## Solution

1. **Preview changes locally**

   ```bash
   /craft:site:build
   ```

   Why: Builds the site locally so you can review changes before publishing

2. **Check for issues**

   ```bash
   /craft:site:check
   ```

   Why: Validates links, images, and common issues that could break the site

3. **Deploy to GitHub Pages**

   ```bash
   /craft:site:deploy
   ```

   Why: Publishes to `gh-pages` branch with automatic backup and rollback support

4. **Verify deployment**
   - Check the deployment URL (shown in output)
   - Verify all pages load correctly
   - Test navigation and links

## Explanation

`/craft:site:deploy` implements a safe deployment workflow:

1. **Pre-deployment checks:**
   - Validates all internal links are not broken
   - Checks that build succeeds without errors
   - Verifies git working directory is clean (no uncommitted changes)

2. **Backup current state:**
   - Creates a backup tag: `backup-gh-pages-YYYY-MM-DD-HHMMSS`
   - Allows quick rollback if deployment fails

3. **Build and deploy:**
   - Detects site type (Quarto, MkDocs, pkgdown)
   - Runs appropriate build command
   - Pushes to `gh-pages` branch with force-with-lease (safe force push)

4. **Post-deployment verification:**
   - Checks that GitHub Pages build succeeds
   - Provides deployment URL
   - Suggests verification steps

5. **Rollback on failure:**
   - If deployment fails, automatically reverts to backup
   - Shows rollback instructions

## Variations

- **Preview without deploying:**

  ```bash
  /craft:site:build && /craft:site:check
  ```

  Use when you want to review changes but not publish yet

- **Deploy with custom message:**

  ```bash
  /craft:site:deploy "Update Week 3 materials"
  ```

  Adds a descriptive commit message to `gh-pages` branch

- **Skip validation (not recommended):**

  ```bash
  /craft:site:deploy --skip-checks
  ```

  Use only if you're confident the site is valid and need to deploy urgently

- **Deploy to custom branch:**

  ```bash
  /craft:site:deploy --branch docs
  ```

  Use if your GitHub Pages serves from a branch other than `gh-pages`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Broken links detected" | Run `/craft:site:check` to see which links are broken, fix them, then retry |
| "Working directory not clean" | Commit or stash your changes before deploying |
| "Build failed" | Check build output for errors, fix issues, then retry |
| "Permission denied (GitHub Pages)" | Verify repository settings: Settings → Pages → Source is set to `gh-pages` branch |
| "404 after deployment" | GitHub Pages can take 1-2 minutes to update; wait and refresh |
| "Old content still showing" | Clear browser cache or try incognito mode |

## Related

- [Site Deploy Command](../../../commands/site/deploy.md) — Full command reference
- [Site Build Command](../../../commands/site/build.md) — Local preview workflow
- [Site Check Command](../../../commands/site/check.md) — Validation details
- [Teaching Workflow Guide](../../guide/teaching-workflow.md) — Complete teaching mode features
