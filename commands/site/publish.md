---
description: Publish teaching site with preview workflow (draft → production)
category: site
arguments:
  - name: skip-validation
    description: Skip teaching content validation
    required: false
    default: false
    alias: -s
---

# /craft:site:publish - Publish Teaching Site

Publish teaching site changes from draft to production with comprehensive preview and validation workflow.

## Usage

```bash
# Full workflow with validation and preview
/craft:site:publish

# Skip validation (not recommended)
/craft:site:publish --skip-validation
/craft:site:publish -s
```

## Teaching Mode

Teaching mode is automatically enabled when Craft detects `.flow/teach-config.yml` in your project. This provides specialized publishing workflows for course websites with enhanced safety and validation.

**Benefits:**
- Content validation before publishing (syllabus, schedule, assignments)
- Preview changes with categorized diff (critical, content, other)
- Safe merge with automatic rollback on failure
- Deployment verification (confirms site is live)
- Branch management (draft → production workflow)

**See:** [Teaching Mode Setup Tutorial](../../docs/tutorials/teaching-mode-setup.md)

## Teaching Mode Workflow

For teaching projects, this command provides a 5-step safety workflow:

### Step 1: Validate Draft Branch

Checks teaching content for completeness:
- **Syllabus sections**: Grading, policies, objectives, schedule
- **Schedule completeness**: All weeks have content
- **Assignment files**: Referenced assignments exist

**Example validation output:**

```
============================================================
TEACHING CONTENT VALIDATION: ❌ BLOCKED
============================================================

🚫 ERRORS (must fix before publishing):
  1. Syllabus missing required sections: policies, objectives
  2. Schedule has incomplete weeks (no content): Week 2, 4

⚠️  WARNINGS (recommended to fix):
  1. Missing assignment files: HW 2

📋 DETAILED CHECKS:
  [✓] Syllabus: grading
  [✗] Syllabus: policies
  [✗] Syllabus: objectives
  [✓] Syllabus: schedule
  [✓] Schedule: exists
  [✗] Schedule: 2/4 weeks complete
  [✗] Assignments: 2/3 found

============================================================
Summary: 3/7 checks passed
Status: 2 error(s) blocking publish ❌
============================================================
```

**If errors found:** Prompts to continue or fix first.

**If warnings only:** Shows them but proceeds.

### Step 2: Preview Changes

Shows diff statistics between draft and production branches with ADHD-friendly categorization:

```
┌─────────────────────────────────────────────┐
│ 📋 PUBLISH PREVIEW                          │
├─────────────────────────────────────────────┤
│ CRITICAL CHANGES:                           │
│ ⚠️  syllabus/index.qmd      +15  -3        │
│ ⚠️  schedule.qmd            +42  -8        │
│                                             │
│ CONTENT CHANGES:                            │
│ ✓  lectures/week-01.qmd     +120 -0        │
│ ✓  lectures/week-02.qmd     +95  -0        │
│ ✓  readings/chapter-1.qmd   +58  -2        │
│                                             │
│ OTHER CHANGES:                              │
│    _quarto.yml              +2   -1        │
│    .gitignore               +3   -0        │
│                                             │
│ Summary: 8 files, +335 lines, -14 lines    │
└─────────────────────────────────────────────┘
```

**File categories:**
- **Critical**: syllabus*, schedule*, assignments/
- **Content**: lectures/, readings/, resources/
- **Other**: All other files

### Step 3: Confirm Publish

Presents 3 options via AskUserQuestion:

1. **"Yes - Merge and deploy (Recommended)"** - Proceed with publish
2. **"Preview full diff first"** - Show detailed `git diff` then loop back
3. **"Cancel"** - Abort and preserve current state

### Step 4: Execute Publish

Safe publish sequence with automatic rollback on failure:

1. **Create backup branch**
   ```bash
   git branch production-backup-20260116-143022
   ```

2. **Checkout production**
   ```bash
   git checkout production
   ```

3. **Fast-forward merge**
   ```bash
   git merge draft --ff-only
   ```
   - **On conflict**: Shows error, suggests manual resolution, aborts
   - **On success**: Continues to push

4. **Push to remote**
   ```bash
   git push origin production
   ```
   - Handles auth errors
   - Handles network errors

5. **Verify deployment** (optional)
   - Reads `gh_pages_url` from `.flow/teach-config.yml`
   - Sends HTTP GET to verify site is live
   - Timeout after 5 minutes
   - Non-blocking (warns but doesn't rollback)

6. **Rollback on failure**
   - If merge OR push fails:
     ```bash
     git reset --hard production-backup-20260116-143022
     ```
   - Preserves backup branch
   - Shows clear error message

### Step 5: Cleanup

Returns to original branch and shows completion:

```
✅ PUBLISH SUCCESSFUL

🌐 Live Site: https://data-wise.github.io/stat-440/

📊 Changes Published:
   - 8 files modified
   - +335 lines added
   - -14 lines removed

💡 Next Steps:
   • Review the live site: https://data-wise.github.io/stat-440/
   • Clean up worktree with /craft:git:clean
   • Continue editing on draft branch

⏱ Deployment may take 1-2 minutes to fully propagate.
```

## Non-Teaching Mode

For non-teaching projects, uses simplified workflow:

1. Detect site type (Quarto, MkDocs, pkgdown)
2. Show preview of changes
3. Confirm publish
4. Deploy using appropriate command

**Example for Quarto:**
```bash
quarto publish gh-pages
```

**Example for MkDocs:**
```bash
mkdocs gh-deploy
```

## Teaching Configuration

The command reads `.flow/teach-config.yml` for deployment settings.

**Minimal configuration:**
```yaml
course:
  number: "STAT 440"
  title: "Regression Analysis"
  semester: "Spring"
  year: 2026

dates:
  start: "2026-01-19"
  end: "2026-05-08"

deployment:
  production_branch: "production"  # Students see this
  draft_branch: "draft"            # Instructors work here
```

**Full configuration with optional fields:**
```yaml
course:
  number: "STAT 440"
  title: "Regression Analysis"
  semester: "Spring"
  year: 2026

dates:
  start: "2026-01-19"
  end: "2026-05-08"
  breaks:
    - name: "Spring Break"
      start: "2026-03-16"
      end: "2026-03-20"

deployment:
  production_branch: "production"
  draft_branch: "draft"
  gh_pages_url: "https://data-wise.github.io/stat-440/"

validation:
  required_sections:
    - grading
    - policies
    - objectives
    - schedule
  strict_mode: true
```

**See:** [Complete Config Schema](../../docs/teaching-config-schema.md) for all fields and validation rules.

## Error Handling

### Validation Errors
```
❌ BLOCKED: Cannot publish with validation errors

Errors found:
  1. Syllabus missing required sections: policies, objectives
  2. Schedule has incomplete weeks: Week 2, 4

Fix these issues before publishing, or use --skip-validation to override.
```

### Merge Conflicts
```
❌ MERGE FAILED: Cannot fast-forward

The production branch has diverged from draft.
This requires manual resolution.

Manual steps:
  1. git checkout production
  2. git merge draft
  3. Resolve conflicts
  4. git commit
  5. Run /craft:site:publish again

Your changes are safe - no modifications were made.
```

### Network Errors
```
❌ PUSH FAILED: Could not push to remote

Error: Permission denied (publickey)

Possible causes:
  - GitHub authentication expired
  - No internet connection
  - Repository permissions changed

Your local changes were rolled back.
The backup branch 'production-backup-20260116-143022' was preserved.
```

## Troubleshooting

**Validation blocking publish:**
- Fix the errors shown in validation report
- Or use `--skip-validation` to override (not recommended)

**Merge conflicts:**
- Production branch has diverged from draft
- Merge manually or rebase draft onto production
- Then run publish again

**Deployment not live after 5 minutes:**
- Check GitHub Actions: `gh run list --limit 5`
- Check GitHub Pages settings: Repository → Settings → Pages
- Verify branch is set to production (or gh-pages)

**Need to undo publish:**
- The backup branch is preserved
- Reset production: `git checkout production && git reset --hard production-backup-<timestamp>`
- Force push: `git push origin production --force`

## See Also

- `/craft:site:deploy` - Direct GitHub Pages deployment (no draft/production workflow)
- `/craft:site:build` - Build site locally
- `/craft:site:check` - Validate site health
- `/craft:git:worktree` - Manage worktrees for draft/production
- Utility: `utils/detect_teaching_mode.py` - Teaching mode detection
- Utility: `commands/utils/teaching_validation.py` - Content validation
- Specification: `docs/teaching-config-schema.md` - Config file format
