# Migrating to Craft Teaching Workflows

⏱️ **15 minutes** • 🟡 Intermediate • ✓ From manual to automated workflows

> **TL;DR** (30 seconds)
> - **What:** Migrate from manual teaching site deployment to Craft automation
> - **Why:** Eliminate errors, save time, gain confidence in publishing
> - **How:** Add config file → Test workflows → Retire old scripts
> - **Benefit:** 5-step safety workflow replaces fragile shell scripts

This guide helps you transition from manual teaching site workflows to Craft's automated teaching mode.

## Before and After

### Old Manual Workflow

```bash
# 1. Remember which branch is production
git branch --show-current  # Am I on draft or production?

# 2. Manually switch branches
git checkout production

# 3. Hope the merge works
git merge draft  # Fingers crossed!

# 4. Fix conflicts (no preview, just hope)
# ... manual conflict resolution ...

# 5. Push and pray
git push origin production

# 6. Wait 5 minutes and manually check site
# Is it live? Did it break? Who knows!

# 7. Realize you forgot to validate syllabus
# Too late - it's already published!
```

**Problems with manual workflow:**
- No pre-publish validation (catch errors AFTER students see them)
- No preview of changes (surprises after deployment)
- Manual branch management (easy to mess up)
- No rollback on failure (broken site = panic)
- No verification (did it actually deploy?)
- Cognitive load (remember all steps, every time)

### New Craft Workflow

```bash
# One command does everything
/craft:site:publish
```

**What happens automatically:**
1. ✓ Validates content (syllabus, schedule, assignments)
2. ✓ Shows preview with categorized changes
3. ✓ Asks for confirmation
4. ✓ Creates backup branch
5. ✓ Safe merge with rollback on failure
6. ✓ Verifies deployment
7. ✓ Returns to original branch

**Benefits:**
- Errors caught BEFORE publishing
- Preview changes before students see them
- Automatic branch management
- Automatic rollback on failure
- Deployment verification
- Zero cognitive load (just run the command)

## Migration Steps

### Step 1: Add Configuration File (5 min)

Create `.flow/teach-config.yml` with your course details:

```yaml
# .flow/teach-config.yml

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
  gh_pages_url: "https://yourname.github.io/stat-440"

validation:
  required_sections:
    - grading
    - policies
    - objectives
    - schedule
  strict_mode: true

progress:
  current_week: auto
```

**Customize:**
- Course number and title
- Semester dates (start, end, breaks)
- GitHub Pages URL
- Required syllabus sections

**Test configuration:**
```bash
/craft:site:status
```

**Expected output:**
```
✓ Teaching mode detected
✓ Configuration valid
```

### Step 2: Test Validation (3 min)

Before using the publish workflow, test content validation:

```bash
/craft:site:validate
```

**First run will likely show errors:**
```
🚫 ERRORS (must fix before publishing):
  1. Syllabus missing required sections: policies
  2. Schedule has incomplete weeks: Week 2, 4
```

**Fix these errors:**
- Add missing syllabus sections
- Complete schedule for all weeks
- Fix any broken assignment references

**Validate again until clean:**
```
✅ ALL CHECKS PASSED
Status: Ready to publish ✅
```

### Step 3: Test Progress Tracking (1 min)

Verify semester progress calculation:

```bash
/craft:site:progress
```

**Check output:**
- Current week matches calendar
- Progress bar is accurate
- Break countdown is correct

**If week is wrong:**
- Verify `dates.start` in config
- Check break dates
- Use `--week` for manual override

### Step 4: First Craft Publish (5 min)

Run your first automated publish:

```bash
# Make sure you're on draft branch
git checkout draft

# Run publish workflow
/craft:site:publish
```

**What to expect:**
1. Validation runs automatically
2. Preview shows categorized changes
3. Confirmation prompt (3 options)
4. Safe merge and push
5. Deployment verification

**Review the preview carefully:**
```
CRITICAL CHANGES:
⚠️  syllabus/index.qmd      +15  -3

CONTENT CHANGES:
✓  lectures/week-01.qmd     +120 -0
```

**Confirm publish:**
- Choose "Yes - Merge and deploy (Recommended)"
- Monitor output for errors
- Verify live site after deployment

### Step 5: Retire Old Scripts (1 min)

Once Craft workflows are working, retire your old deployment scripts:

```bash
# Archive old scripts
mkdir -p archive/
mv deploy.sh archive/
mv publish.sh archive/
mv validate-syllabus.sh archive/

# Update team documentation
# Replace manual steps with /craft:site:publish
```

**Update `.gitignore` (optional):**
```
# Old deployment scripts (archived)
archive/
```

## Common Migration Patterns

### Pattern 1: Weekly Content Updates

**Old workflow:**
```bash
# Edit content (draft branch)
vim lectures/week-05.qmd

# Commit changes
git add lectures/week-05.qmd
git commit -m "Add week 5 lecture"

# Switch to production
git checkout production

# Merge (hope it works)
git merge draft

# Push (hope it deploys)
git push origin production

# Wait and manually check
# Open browser, reload, verify
```

**New workflow:**
```bash
# Edit content (draft branch)
vim lectures/week-05.qmd

# Commit changes
git add lectures/week-05.qmd
git commit -m "Add week 5 lecture"

# Publish with safety checks
/craft:site:publish
```

### Pattern 2: Assignment Releases

**Old workflow:**
```bash
# Add assignment file
vim assignments/hw-05.qmd

# Update schedule manually
vim schedule.qmd
# Add due date, hope you didn't typo

# Commit
git add assignments/hw-05.qmd schedule.qmd
git commit -m "Add HW 5"

# Manual publish (cross fingers)
git checkout production
git merge draft
git push origin production

# Realize later you forgot to link it
# Students can't find assignment
# Emergency fix required
```

**New workflow:**
```bash
# Add assignment file
vim assignments/hw-05.qmd

# Update schedule
vim schedule.qmd

# Commit
git add assignments/hw-05.qmd schedule.qmd
git commit -m "Add HW 5"

# Validate catches missing links
/craft:site:validate
# Shows: "Assignment HW 5 referenced but file missing link"

# Fix link, then publish
/craft:site:publish
# Preview shows assignment in CRITICAL CHANGES
# Verify before students see it
```

### Pattern 3: Schedule Changes

**Old workflow:**
```bash
# Change due dates (high risk!)
vim schedule.qmd
# Move HW 3 from Week 5 to Week 6

# Commit and publish immediately
git add schedule.qmd
git commit -m "Move HW 3 due date"
git checkout production
git merge draft
git push origin production

# Students confused (no notification)
# Canvas still shows old date
# Email apology required
```

**New workflow:**
```bash
# Change due dates
vim schedule.qmd

# Commit
git add schedule.qmd
git commit -m "Move HW 3 due date"

# Preview shows CRITICAL CHANGE
/craft:site:publish
# Highlights: schedule.qmd in CRITICAL section
# Review diff before confirming

# After publish, update Canvas manually
# Send announcement to students
```

### Pattern 4: Semester Progress Check

**Old workflow:**
```bash
# Mentally calculate: "What week is it?"
# Check calendar, count weeks manually
# Account for spring break... or did I?
# Confusion about whether we're on Week 7 or 8

# Update syllabus manually
vim syllabus.qmd
# Change "Current week: 7" to "Current week: 8"
# Commit, publish, hope it's right
```

**New workflow:**
```bash
# One command shows everything
/craft:site:progress

# Output:
# Week 8 of 16 (50% complete)
# Next break: Spring Break in 12 days

# No manual updates needed
# Auto-calculated, always accurate
```

## What to Do with Old Scripts

### Review and Archive

Before deleting old scripts, review them for:

1. **Environment-specific configuration**
   - Server URLs
   - API keys
   - Paths

2. **Custom validation logic**
   - Unique checks for your course
   - Can be added to Craft config

3. **Deployment hooks**
   - Pre/post-deploy actions
   - May need custom integration

**Archive, don't delete:**
```bash
mkdir -p docs/archive/old-workflows/
mv *.sh docs/archive/old-workflows/
git add docs/archive/
git commit -m "Archive old deployment scripts"
```

### Update Team Documentation

Update your teaching team's workflow documentation:

**Before:**
```markdown
## Publishing to Production

1. Switch to production branch: `git checkout production`
2. Merge from draft: `git merge draft`
3. Resolve conflicts if any
4. Push: `git push origin production`
5. Wait 5 minutes
6. Manually verify site is live
```

**After:**
```markdown
## Publishing to Production

Run the publish command:
```bash
/craft:site:publish
```

The command will:
- Validate content automatically
- Show preview of changes
- Ask for confirmation
- Deploy with rollback on failure
- Verify site is live
```

### Notify Your Team

**Email template:**
```
Subject: New Teaching Site Workflow - Craft Automation

We've migrated to Craft for automated teaching site deployment.

What changed:
- Old: Manual branch switching, merge, push (error-prone)
- New: One command with validation and preview

New workflow:
1. Edit content on draft branch
2. Run: /craft:site:publish
3. Review preview and confirm

Benefits:
- Catches errors BEFORE students see them
- Preview changes before publishing
- Automatic rollback on failure
- No more manual branch management

Documentation:
https://data-wise.github.io/craft/tutorials/teaching-mode-setup/

Questions? Reply to this email.
```

## Troubleshooting Migration Issues

### Existing Content Fails Validation

**Problem:** Old content doesn't meet Craft's validation rules

**Solution:**
```bash
# See what's wrong
/craft:site:validate

# Fix issues one by one
# OR adjust validation rules

# Edit config to relax rules temporarily
vim .flow/teach-config.yml
```

```yaml
validation:
  required_sections:
    - grading  # Only require grading for now
  strict_mode: false  # Warnings only
```

**Gradually tighten rules:**
- Start with relaxed validation
- Fix content over time
- Add sections to `required_sections`
- Enable `strict_mode` when ready

### Branch Names Don't Match

**Problem:** You use `main` and `dev` instead of `production` and `draft`

**Solution:** Update config to match your branches

```yaml
deployment:
  production_branch: "main"  # Your production branch
  draft_branch: "dev"        # Your draft branch
```

### Merge Conflicts During Migration

**Problem:** Production and draft have diverged significantly

**Solution:**
```bash
# Option 1: Force sync (if production is outdated)
git checkout production
git reset --hard draft
git push --force origin production

# Option 2: Merge manually first
git checkout production
git merge draft
# Resolve conflicts
git commit
# Then use Craft for future publishes
```

### GitHub Pages Not Deploying

**Problem:** Site doesn't update after publish

**Solution:**
1. Check GitHub Actions: `gh run list --limit 5`
2. Verify branch in Settings → Pages
3. Check `gh_pages_url` in config matches actual URL
4. Wait up to 10 minutes for first deploy

### Team Members Don't Have Craft

**Problem:** Only you have Craft installed

**Solution:**
```bash
# Share installation instructions
# Homebrew (recommended)
brew tap data-wise/tap
brew install craft

# Or curl
curl -fsSL https://raw.githubusercontent.com/Data-Wise/craft/main/install.sh | bash
```

**Document in team README:**
```markdown
## Setup

Install Craft:
```bash
brew install craft
```

Then use teaching workflows:
```bash
/craft:site:publish
/craft:site:progress
/craft:site:validate
```
```

## Migration Checklist

Use this checklist to track migration progress:

**Pre-migration:**
- [ ] Review old deployment scripts
- [ ] Document current workflow
- [ ] Identify custom validation logic
- [ ] List all team members who deploy

**Configuration:**
- [ ] Create `.flow/teach-config.yml`
- [ ] Set course info (number, title, semester)
- [ ] Add semester dates (start, end, breaks)
- [ ] Configure deployment (branches, URL)
- [ ] Set validation rules
- [ ] Test config with `/craft:site:status`

**Validation:**
- [ ] Run `/craft:site:validate`
- [ ] Fix all validation errors
- [ ] Test with incomplete content (intentionally break validation)
- [ ] Verify error messages are clear

**Publishing:**
- [ ] Test `/craft:site:publish` on draft branch
- [ ] Review preview output carefully
- [ ] Confirm publish and monitor deployment
- [ ] Verify live site is correct
- [ ] Test rollback (create a failure scenario)

**Progress Tracking:**
- [ ] Run `/craft:site:progress`
- [ ] Verify current week calculation
- [ ] Check break countdown accuracy
- [ ] Test `--week` manual override

**Team Migration:**
- [ ] Install Craft for all team members
- [ ] Update team workflow documentation
- [ ] Send migration announcement email
- [ ] Hold training session (optional)
- [ ] Archive old deployment scripts

**Post-migration:**
- [ ] Monitor first 3 publishes for issues
- [ ] Collect team feedback
- [ ] Adjust validation rules if needed
- [ ] Update issue templates to reference new workflow

## Success Metrics

Track these to measure migration success:

**Before Craft (baseline):**
- Time to publish: ~15 minutes (manual steps)
- Publishing errors: ~20% of publishes have issues
- Broken link incidents: ~2 per semester
- Rollback required: ~10% of publishes

**After Craft (target):**
- Time to publish: ~3 minutes (one command)
- Publishing errors: <5% (caught by validation)
- Broken link incidents: 0 (validation catches them)
- Rollback required: 0 (automatic on failure)

**Measure at 4 weeks, 8 weeks, and end of semester.**

## Next Steps

After successful migration:

1. **Explore advanced features:**
   - Custom validation rules
   - JSON output for scripting
   - CI/CD integration

2. **Share experience:**
   - Write blog post about migration
   - Share config with other instructors
   - Contribute validation patterns

3. **Provide feedback:**
   - What worked well?
   - What was confusing?
   - What features are missing?

4. **Help others migrate:**
   - Share this guide with colleagues
   - Offer to help with their migration
   - Build a community of practice

## Resources

- **[Teaching Mode Setup Tutorial](teaching-mode-setup.md)** - First-time setup guide
- **[Config Schema](teaching-config-schema.md)** - Complete YAML reference
- **[Command Reference: `/craft:site:publish`](../commands/site/publish.md)** - Publishing workflow
- **[Command Reference: `/craft:site:validate`](../commands/site/validate.md)** - Content validation
- **[GitHub Issues](https://github.com/Data-Wise/craft/issues)** - Report problems or suggest features

## Get Help

**Questions during migration?**
- Review troubleshooting section above
- Check [Teaching Config Schema](teaching-config-schema.md)
- Open an issue: [GitHub Issues](https://github.com/Data-Wise/craft/issues)

**Feedback welcome!** Share your migration experience to help improve this guide.
