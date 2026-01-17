# Teaching Workflow Documentation Index

Complete documentation for Craft's teaching mode feature.

## Quick Start

**New to teaching mode?** Start here:

1. **[Teaching Mode Setup Tutorial](tutorials/teaching-mode-setup.md)** (25 min)
   - First-time setup guide
   - Step-by-step configuration
   - Complete with examples and troubleshooting

2. **[Teaching Config Schema](teaching-config-schema.md)** (5 min)
   - YAML reference guide
   - All configuration fields
   - Validation rules

3. **[Migration Guide](teaching-migration.md)** (15 min)
   - Migrate from manual workflows
   - Before/after patterns
   - Team migration checklist

## Documentation Structure

### Tutorials (Step-by-Step Guides)

| Document | Time | Level | Purpose |
|----------|------|-------|---------|
| [Teaching Mode Setup](tutorials/teaching-mode-setup.md) | 25 min | Beginner | First-time setup and configuration |

**What you'll learn:**
- Create `.flow/teach-config.yml` configuration
- Enable teaching mode auto-detection
- Run content validation
- Execute first publish workflow
- Track semester progress

### Reference Guides

| Document | Time | Level | Purpose |
|----------|------|-------|---------|
| [Teaching Config Schema](teaching-config-schema.md) | 5 min | Beginner | Complete YAML specification |

**Complete reference for:**
- Course information (number, title, semester, year)
- Semester dates (start, end, breaks)
- Instructor information (name, email, office hours)
- Deployment configuration (branches, GitHub Pages)
- Progress tracking (current week, auto-calculation)
- Validation rules (required sections, strict mode)

### Migration Guides

| Document | Time | Level | Purpose |
|----------|------|-------|---------|
| [Teaching Migration](teaching-migration.md) | 15 min | Intermediate | Transition from manual to automated workflows |

**Covers:**
- Before/after workflow comparison
- Step-by-step migration process
- Common migration patterns
- Troubleshooting migration issues
- Team migration checklist

### Command Reference

| Command | Description | Link |
|---------|-------------|------|
| `/craft:site:publish` | Publish draft → production with preview | [Documentation](../commands/site/publish.md) |
| `/craft:site:progress` | Semester progress dashboard | [Documentation](../commands/site/progress.md) |
| `/craft:site:validate` | Content validation (syllabus, schedule) | [Documentation](../commands/site/validate.md) |
| `/craft:site:build` | Build site with teaching mode support | [Documentation](../commands/site/build.md) |

## Documentation by Use Case

### I'm Setting Up for the First Time

**Start here:**
1. Read [README Teaching Mode section](../README.md#teaching-mode-new-in-v1180) (2 min)
2. Follow [Teaching Mode Setup Tutorial](tutorials/teaching-mode-setup.md) (25 min)
3. Bookmark [Config Schema](teaching-config-schema.md) for reference

**Key commands:**
```bash
# Setup
/craft:site:status      # Verify detection

# Validate
/craft:site:validate    # Check content

# Publish
/craft:site:publish     # Deploy to production
```

### I'm Migrating from Manual Workflows

**Start here:**
1. Review [Migration Guide](teaching-migration.md) (15 min)
2. Create config file following [Config Schema](teaching-config-schema.md)
3. Test workflows before retiring old scripts

**Migration checklist:**
- [ ] Create `.flow/teach-config.yml`
- [ ] Test detection with `/craft:site:status`
- [ ] Run validation and fix errors
- [ ] Test publish workflow on draft
- [ ] Archive old deployment scripts
- [ ] Update team documentation

### I Need to Configure Something

**Reference guides:**
- [Config Schema](teaching-config-schema.md) - All YAML fields and options
- [Validation Rules](teaching-config-schema.md#validation-rules) - Required sections, strict mode
- [Deployment Config](teaching-config-schema.md#deployment-configuration) - Branches, GitHub Pages

**Common configurations:**
```yaml
# Basic configuration
course:
  number: "STAT 440"
  title: "Regression Analysis"
  semester: "Spring"
  year: 2026

dates:
  start: "2026-01-19"
  end: "2026-05-08"

# Add breaks
dates:
  breaks:
    - name: "Spring Break"
      start: "2026-03-16"
      end: "2026-03-20"

# Configure validation
validation:
  required_sections:
    - grading
    - policies
  strict_mode: true
```

### I'm Having a Problem

**Troubleshooting resources:**

1. **Teaching mode not detected**
   - See: [Setup Tutorial - Step 2](tutorials/teaching-mode-setup.md#step-2-test-detection-2-min)
   - Check file location and YAML syntax

2. **Validation errors**
   - See: [Setup Tutorial - Step 3](tutorials/teaching-mode-setup.md#step-3-validate-content-3-min)
   - Fix missing sections or incomplete content

3. **Publish failures**
   - See: [Publish Command - Error Handling](../commands/site/publish.md#error-handling)
   - Review merge conflicts, network errors

4. **Progress calculation wrong**
   - See: [Progress Command - Troubleshooting](../commands/site/progress.md#troubleshooting)
   - Verify dates and breaks in config

5. **Migration issues**
   - See: [Migration Guide - Troubleshooting](teaching-migration.md#troubleshooting-migration-issues)
   - Handle existing content, branch names, team setup

### I Want to Understand How It Works

**Architecture and implementation:**

**Teaching mode detection:**
- Checks for `.flow/teach-config.yml` in project root
- Validates YAML schema
- Activates specialized workflows

**Validation system:**
- Parses syllabus for required sections
- Checks schedule completeness (all weeks have content)
- Verifies assignment files exist
- Reports errors (block publish) vs warnings (recommend fix)

**Publish workflow:**
1. Pre-publish validation
2. Categorized diff preview (critical, content, other)
3. User confirmation (yes, preview diff, cancel)
4. Backup branch creation
5. Fast-forward merge with rollback
6. Deployment verification

**Progress tracking:**
- Auto-calculates current week from semester dates
- Accounts for break periods
- Manual override with `--week` flag
- JSON output for scripting

## Cross-Reference Matrix

| From | To | Relationship |
|------|----|----|
| README | Setup Tutorial | Quick start → Full guide |
| README | Config Schema | Quick start → Reference |
| Setup Tutorial | Config Schema | Configuration → Specification |
| Setup Tutorial | Publish Command | Workflow → Command details |
| Setup Tutorial | Progress Command | Workflow → Dashboard |
| Setup Tutorial | Migration Guide | First-time → Advanced |
| Migration Guide | Setup Tutorial | Prerequisites |
| Migration Guide | Config Schema | Configuration |
| Config Schema | Setup Tutorial | Examples → Usage |
| Publish Command | Config Schema | Configuration reference |
| Progress Command | Config Schema | Configuration reference |

## Completeness Checklist

### Documentation Files

- [x] README section (Teaching Mode)
- [x] Setup tutorial (tutorials/teaching-mode-setup.md)
- [x] Config schema (teaching-config-schema.md)
- [x] Migration guide (teaching-migration.md)
- [x] Command updates (publish.md, progress.md, build.md)
- [x] Documentation index (this file)

### Content Coverage

- [x] Quick start (README)
- [x] First-time setup (tutorial)
- [x] Configuration reference (schema)
- [x] Migration from manual (migration guide)
- [x] Common workflows (tutorial + migration)
- [x] Troubleshooting (all documents)
- [x] Error messages (command docs)
- [x] Examples (all documents)

### Style Consistency

- [x] TL;DR sections
- [x] Time estimates
- [x] Difficulty levels
- [x] ADHD-friendly formatting
- [x] Code examples
- [x] Visual hierarchy
- [x] Scannable layout
- [x] Cross-references

### Cross-References

- [x] README → Tutorial
- [x] README → Schema
- [x] Tutorial → Schema
- [x] Tutorial → Commands
- [x] Tutorial → Migration
- [x] Migration → Tutorial
- [x] Migration → Schema
- [x] Commands → Tutorial
- [x] Commands → Schema
- [x] Commands → Migration

## Future Enhancements

**Not in v1.0, but planned:**

- [ ] LMS integration (Canvas, Moodle)
- [ ] Assignment due date parsing from schedule
- [ ] Lecture completion tracking
- [ ] Student progress analytics
- [ ] Email digest automation
- [ ] Multi-instructor workflows
- [ ] Course template library
- [ ] Semester rollover automation

## Feedback

**Help improve these docs:**
- [Open an issue](https://github.com/Data-Wise/craft/issues) with suggestions
- Share what worked well
- Report confusing sections
- Suggest additional examples

## Related Documentation

**General Craft documentation:**
- [Craft README](../README.md) - Full feature list
- [Quick Start](QUICK-START.md) - General Craft usage
- [ADHD Guide](ADHD-QUICK-START.md) - Neurodivergent-friendly workflows
- [Command Reference](REFCARD.md) - All 86+ commands

**Site commands:**
- [Site Create](../commands/site/create.md) - Documentation site wizard
- [Site Deploy](../commands/site/deploy.md) - Direct GitHub Pages deployment
- [Site Check](../commands/site/check.md) - Health validation

**Git workflows:**
- [Git Worktree](../commands/git/worktree.md) - Parallel development
- [Git Branch](../commands/git/branch.md) - Branch management
- [Git Sync](../commands/git/sync.md) - Smart synchronization
