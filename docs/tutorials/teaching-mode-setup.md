<!-- markdownlint-disable MD046 -->
# Teaching Mode Setup

⏱️ **25 minutes** • 🟢 Beginner • ✓ Complete first-time setup

> **TL;DR** (30 seconds)
>
> - **What:** Set up Craft's teaching workflows for your course
> - **Why:** Automated validation, safe publishing, progress tracking
> - **How:** Create config file → Test detection → Validate → Publish
> - **Next:** Use `/craft:site:progress` weekly, `/craft:site:publish` for releases

Teaching Mode transforms Craft into a comprehensive teaching workflow automation tool. This tutorial walks you through first-time setup for a Quarto-based course website.

!!! note "Already using flow-cli?"
    If your project already has a `.flow/teach-config.yml` from flow-cli (with `semester_info`, `course.name`, `branches`), Craft reads it directly — no separate config needed. See the [Config Schema Reference](../teaching-config-schema.md#flow-cli-config-compatibility) for details.

!!! tip "Before You Start"
    You need:

    - A Quarto project for your teaching content
    - Git repository with draft/production branches (or willing to create them)
    - GitHub Pages or similar deployment target
    - Basic familiarity with YAML and Git

## What You'll Learn

By the end of this tutorial, you'll have:

- ✓ Teaching mode enabled with auto-detection
- ✓ Content validation catching missing syllabus sections
- ✓ Preview-before-publish workflow preventing errors
- ✓ Automatic semester progress tracking
- ✓ Safe deployment to production

## Step 1: Create Config File (5 min)

Teaching mode activates when Craft detects `.flow/teach-config.yml` in your project root.

### 1.1 Create Directory

```bash
# In your teaching project root
mkdir -p .flow
```

### 1.2 Create Configuration

Create `.flow/teach-config.yml` with your course details:

```yaml
# .flow/teach-config.yml - STAT 440 Spring 2026

# ============================================================================
# Course Information
# ============================================================================
course:
  number: "STAT 440"
  title: "Regression Analysis"
  semester: "Spring"
  year: 2026

# ============================================================================
# Semester Dates
# ============================================================================
dates:
  # Semester runs January 19 - May 8
  start: "2026-01-19"
  end: "2026-05-08"

  # Break periods (holidays + Spring Break)
  breaks:
    - name: "MLK Day"
      start: "2026-01-20"
      end: "2026-01-20"        # Single-day breaks are supported
    - name: "Spring Break"
      start: "2026-03-16"
      end: "2026-03-20"

# ============================================================================
# Deployment Configuration
# ============================================================================
deployment:
  production_branch: "production"  # Students see this
  draft_branch: "draft"            # Instructors see this
  gh_pages_url: "https://yourname.github.io/stat-440"

# ============================================================================
# Progress Tracking
# ============================================================================
progress:
  # "auto" calculates based on dates and breaks (recommended)
  current_week: auto

# ============================================================================
# Validation Rules
# ============================================================================
validation:
  # Sections that must exist in syllabus
  required_sections:
    - grading
    - policies
    - objectives
    - schedule

  # Strict mode: true = errors block publishing
  strict_mode: true
```

**Customize for your course:**

- Replace `STAT 440` with your course number
- Update semester dates to match your academic calendar
- Add all break periods (even 1-2 day breaks)
- Set your GitHub Pages URL

!!! warning "Common Mistake"
    Don't forget to update the **year** field. Copy-paste errors from previous semesters are common!

### 1.3 Validate Configuration

Test that your config file is valid:

```bash
# In Claude Code
/craft:site:status
```

**Expected output:**

```
✓ Teaching mode detected
✓ Configuration valid
✓ Semester: Spring 2026 (16 weeks)
✓ Current week: 1 (auto-calculated)
```

**If you see errors**, check:

- Date format is `YYYY-MM-DD`
- Dates are in logical order (start < end)
- Breaks fall within semester dates
- All required fields present

## Step 2: Test Detection (2 min)

Verify that Craft recognizes your project as a teaching project.

### 2.1 Check Status

```bash
/craft:site:status
```

**What to look for:**

```
┌─────────────────────────────────────────────────────────┐
│ 📚 TEACHING PROJECT STATUS                              │
├─────────────────────────────────────────────────────────┤
│ ✓ Mode: Teaching (detected via .flow/teach-config.yml) │
│ ✓ Course: STAT 440 - Regression Analysis               │
│ ✓ Semester: Spring 2026                                 │
│ ✓ Current Week: 1 of 16                                 │
└─────────────────────────────────────────────────────────┘
```

If teaching mode is **NOT** detected, check:

1. File location: Must be `.flow/teach-config.yml` in project root
2. File permissions: Must be readable
3. YAML syntax: Use a validator if needed

## Step 3: Validate Content (3 min)

Run content validation to check for missing or incomplete sections.

### 3.1 Run Validation

```bash
/craft:site:validate
```

### 3.2 Understand Validation Output

**Example output with errors:**

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

**Clean output (all checks pass):**

```
============================================================
TEACHING CONTENT VALIDATION: ✅ PASSED
============================================================

✅ ALL CHECKS PASSED

📋 DETAILED CHECKS:
  [✓] Syllabus: grading
  [✓] Syllabus: policies
  [✓] Syllabus: objectives
  [✓] Syllabus: schedule
  [✓] Schedule: exists
  [✓] Schedule: 4/4 weeks complete
  [✓] Assignments: 3/3 found

============================================================
Summary: 7/7 checks passed
Status: Ready to publish ✅
============================================================
```

### 3.3 Fix Validation Errors

**Missing syllabus sections:**

- Add headings in your `syllabus/index.qmd` or `syllabus.qmd`
- Required sections (default): grading, policies, objectives, schedule
- Can customize in `validation.required_sections`

**Incomplete schedule:**

- Check your `schedule.qmd` for missing weeks
- Validation expects content for each week (lectures, readings, or assignments)

**Missing assignment files:**

- Validation checks that assignments referenced in schedule exist
- Add missing files or update references

!!! tip "Pro Tip: Use Warnings"
    Warnings don't block publishing - they're helpful reminders. Errors MUST be fixed (unless you use `--skip-validation`).

## Step 4: First Publish (10 min)

Publish your content from draft to production with preview and safety checks.

### 4.1 Ensure You're on Draft Branch

```bash
# Check current branch
git branch --show-current

# Switch to draft if needed
git checkout draft
```

### 4.2 Run Publish Command

```bash
/craft:site:publish
```

### 4.3 Review Preview

The command shows a categorized diff:

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

- **CRITICAL**: syllabus*, schedule*, assignments/
- **CONTENT**: lectures/, readings/, resources/
- **OTHER**: All other files

### 4.4 Confirm Publish

You'll be prompted with 3 options:

1. **"Yes - Merge and deploy (Recommended)"** - Proceed
2. **"Preview full diff first"** - See detailed `git diff`
3. **"Cancel"** - Abort

Choose option 1 to proceed.

### 4.5 Monitor Deployment

The command will:

1. Create backup branch (`production-backup-<timestamp>`)
2. Checkout production branch
3. Fast-forward merge from draft
4. Push to remote
5. Verify deployment (if `gh_pages_url` configured)

**Success output:**

```
✅ PUBLISH SUCCESSFUL

🌐 Live Site: https://yourname.github.io/stat-440/

📊 Changes Published:
   - 8 files modified
   - +335 lines added
   - -14 lines removed

💡 Next Steps:
   • Review the live site: https://yourname.github.io/stat-440/
   • Clean up worktree with /craft:git:clean
   • Continue editing on draft branch

⏱ Deployment may take 1-2 minutes to fully propagate.
```

### 4.6 Verify Live Site

Wait 1-2 minutes, then visit your GitHub Pages URL:

```
https://yourname.github.io/stat-440/
```

**Check:**

- Syllabus displays correctly
- Schedule shows all weeks
- Assignments are linked properly

!!! success "Congratulations!"
    You've successfully published your first teaching site with Craft's safety workflow!

## Step 5: Track Progress (2 min)

Use the progress dashboard to monitor semester status.

### 5.1 Run Progress Command

```bash
/craft:site:progress
```

**Example output:**

```
┌─────────────────────────────────────────────────────────┐
│ 📚 STAT 440: Regression Analysis                        │
│ Spring 2026 · Week 1 of 16 (6% complete)                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 📅 CURRENT WEEK: Week 1                                 │
│ Date Range: Jan 19-25                                   │
│                                                         │
│ 📊 PROGRESS:                                            │
│ ▓░░░░░░░░░░░░░░░ 6% complete                           │
│                                                         │
│ 📌 UPCOMING MILESTONES:                                 │
│ • Spring Break: Mar 16-20 (57 days)                     │
│                                                         │
│ ⏰ NEXT BREAK: Spring Break in 57 days                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Key information:**

- Current week (auto-calculated from dates and breaks)
- Visual progress bar
- Upcoming break countdown
- Date range for current week

### 5.2 Weekly Check-In

Run `/craft:site:progress` at the start of each week to:

- Confirm current week is correct
- Plan upcoming content
- Track progress toward semester goals

!!! tip "Manual Override"
    Need to test future weeks? Use `--week` flag:
    ```bash
    /craft:site:progress --week 8
    ```

## Common Workflows

### Weekly Content Updates

```bash
# 1. Edit content on draft branch
# (edit lectures, assignments, etc.)

# 2. Validate before publishing
/craft:site:validate

# 3. Publish to production
/craft:site:publish
```

### Assignment Releases

```bash
# 1. Add assignment files
# assignments/hw-02.qmd

# 2. Update schedule
# schedule.qmd (add HW 2 due date)

# 3. Validate
/craft:site:validate

# 4. Publish
/craft:site:publish
```

### Schedule Changes

```bash
# 1. Edit schedule.qmd
# (move due dates, adjust topics)

# 2. Validate completeness
/craft:site:validate

# 3. Preview changes
/craft:site:publish
# (review CRITICAL CHANGES section carefully)

# 4. Confirm and publish
```

## Troubleshooting

### Teaching Mode Not Detected

**Symptom:** `/craft:site:status` doesn't show teaching mode

**Solution:**

1. Check file location: `.flow/teach-config.yml` in project root
2. Verify YAML syntax with validator
3. Ensure file is readable (`ls -la .flow/`)

### Validation Errors Block Publishing

**Symptom:** Errors prevent `/craft:site:publish` from proceeding

**Solution:**

1. Read error messages carefully
2. Fix missing sections or incomplete content
3. Run `/craft:site:validate` to verify fixes
4. **Emergency bypass** (not recommended): `--skip-validation`

### Merge Conflicts During Publish

**Symptom:** "Cannot fast-forward" error

**Solution:**

```bash
# Production branch has diverged from draft
git checkout production
git merge draft
# Resolve conflicts
git commit
/craft:site:publish  # Try again
```

### Progress Inaccurate

**Symptom:** Current week calculation is wrong

**Solution:**

1. Verify `dates.start` and `dates.end` in config
2. Check break dates are correct
3. Ensure breaks don't overlap
4. Use `--week` flag for manual override

### Deployment Not Live After 5 Minutes

**Symptom:** GitHub Pages not updating

**Solution:**

1. Check GitHub Actions: `gh run list --limit 5`
2. Verify branch in Settings → Pages (should be "production")
3. Check build logs for errors
4. Wait up to 10 minutes for first deployment

## Next Steps

Now that teaching mode is set up:

**Weekly tasks:**

- [ ] Run `/craft:site:progress` each Monday
- [ ] Update content on `draft` branch
- [ ] Validate with `/craft:site:validate`
- [ ] Publish with `/craft:site:publish`

**Semester tasks:**

- [ ] Add assignment files before due dates
- [ ] Update syllabus when policies change
- [ ] Keep schedule current (adjust for snow days, etc.)

**Advanced features:**

- [ ] Explore `--json` output for scripting
- [ ] Set up CI/CD to auto-validate on push
- [ ] Create custom validation rules
- [ ] Integrate with LMS (future enhancement)

## Additional Resources

- **[Config Schema Reference](../teaching-config-schema.md)** - Complete YAML specification (includes flow-cli compatibility)
- **[Teaching Workflow Guide](../guide/teaching-workflow.md)** - Ecosystem overview (Craft vs Scholar vs flow-cli)
- **[Migration Guide](../teaching-migration.md)** - From manual to Craft workflows
- **[Site Commands Reference](../commands/site.md)** - All site commands including publish, progress, and validate

## Help and Support

**Questions or issues?**

- Check troubleshooting section above
- Review [Teaching Config Schema](../teaching-config-schema.md)
- Open an issue: [GitHub Issues](https://github.com/Data-Wise/craft/issues)

**Feedback welcome!** Teaching mode is actively developed. Share your experiences and suggestions.
