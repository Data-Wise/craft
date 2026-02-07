# Teaching Workflow - Quick Reference

> **Preview → Validate → Publish** - Safe course site deployment

![Teaching Workflow Demo](../demos/teaching-workflow.gif)

## Essential Commands

```bash
/craft:site:build          # Build preview (current branch)
/craft:site:preview        # Open preview in browser
/craft:site:publish        # Validate → Switch to main → Deploy
/craft:site:progress       # Semester progress dashboard
/craft:git:status          # Teaching-aware git status
```

## Quick Start

```bash
# 1. Create config
cat > .flow/teach-config.yml << 'EOF'
teaching:
  enabled: true
  branches: { preview: dev, production: main }
  semester:
    name: "Fall 2024"
    start_date: "2024-08-26"
    end_date: "2024-12-13"
  content:
    schedule: "schedule.qmd"
    syllabus: "syllabus.qmd"
EOF

# 2. Test
/craft:git:status          # Should show teaching mode

# 3. Preview
/craft:site:build

# 4. Publish
/craft:site:publish
```

## Common Workflows

### Weekly Content Update

```bash
git checkout dev           # Start on preview
# ... edit content ...
/craft:site:build          # Preview changes
/craft:site:preview        # Check in browser
/craft:site:publish        # Deploy to production
```

### Check Progress

```bash
/craft:site:progress       # Semester dashboard
```

### Emergency Fix

```bash
git checkout main          # Go to production
# ... fix issue ...
/craft:site:build          # Build
git push origin main       # Deploy
git checkout dev           # Back to preview
```

## Validation

### Check Before Publish

```bash
/craft:site:publish --dry-run --validate-only
```

### Common Issues

| Issue | Fix |
|-------|-----|
| Missing week | Add to schedule.qmd |
| Date out of range | Check assignment due dates |
| Broken links | `/craft:docs:check-links` |
| Bad YAML | Validate teach-config.yml |

### Skip Validation (Emergency)

```bash
/craft:site:publish --skip-validation
```

## Branch Strategy

```
main (production) ← Students see this
  ↑
dev (preview) ← You edit here
```

**Rules:**

- Edit on `dev`
- Preview with `/craft:site:build`
- Publish with `/craft:site:publish` (auto-switches branches)
- `/craft:git:status` shows which branch you're on

## Configuration

### Minimal

```yaml
teaching:
  enabled: true
  branches: { preview: dev, production: main }
  semester:
    name: "Fall 2024"
    start_date: "2024-08-26"
    end_date: "2024-12-13"
  content:
    schedule: "schedule.qmd"
    syllabus: "syllabus.qmd"
```

### Standard

```yaml
teaching:
  enabled: true
  branches: { preview: dev, production: main }
  semester:
    name: "Fall 2024"
    start_date: "2024-08-26"
    end_date: "2024-12-13"
    weeks: 15
  content:
    schedule: "schedule.qmd"
    syllabus: "syllabus.qmd"
    assignments_dir: "assignments/"
  validation:
    strict: true
  publishing:
    auto_nav_update: true
```

## Flow-CLI Config Compatibility

If your project uses flow-cli's schema, Craft reads it natively — no migration needed:

| Flow-CLI | Craft reads as |
|----------|---------------|
| `course.name` | `course.number` |
| `course.full_name` | `course.title` |
| `course.semester: "spring"` | `course.semester: "Spring"` |
| `semester_info.start_date` | `dates.start` |
| `semester_info.end_date` | `dates.end` |
| `branches.production` | `deployment.production_branch` |

Single-day breaks (`start == end`) are supported for holidays like MLK Day.

See [Config Schema](../teaching-config-schema.md#flow-cli-config-compatibility) for details.

## Flags

### `/craft:site:build`

```bash
/craft:site:build              # Normal build
/craft:site:build --force      # Force rebuild
```

### `/craft:site:publish`

```bash
/craft:site:publish                    # Full workflow
/craft:site:publish --dry-run          # Preview what would happen
/craft:site:publish --validate-only    # Just run validation
/craft:site:publish --skip-validation  # Emergency publish
/craft:site:publish --force-rebuild    # Force site rebuild
```

### `/craft:site:progress`

```bash
/craft:site:progress           # Full dashboard
/craft:site:progress --json    # JSON output
```

## Troubleshooting

### Not Detecting Teaching Mode

```bash
# Check config exists
ls .flow/teach-config.yml

# Verify enabled
grep "enabled: true" .flow/teach-config.yml

# Test detection
/craft:git:status              # Should show teaching context
```

### Wrong Branch

```bash
/craft:git:status              # Shows current branch + context
git checkout dev               # Switch to preview
git checkout main              # Switch to production
```

### Validation Errors

```bash
# See what's wrong
/craft:site:publish --dry-run --validate-only

# Fix issues, then try again
/craft:site:publish
```

### Site Not Updating

```bash
# 1. Check GitHub Pages settings
# Repo → Settings → Pages

# 2. Force rebuild
git checkout main
/craft:site:build --force
git push origin main
```

## Impact

- ⏱️ **80% faster**: 15 min → 3 min per publish
- 🐛 **Zero bugs**: Validation catches issues
- 🎯 **100% confidence**: Preview before publish

## See Also

- [Full Guide](../guide/teaching-workflow.md)
- [Config Schema](../teaching-config-schema.md)
- [Migration Guide](../teaching-migration.md)
- [Setup Tutorial](../tutorials/teaching-mode-setup.md)
