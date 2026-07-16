# Teaching Workflow - Quick Reference

> **Preview → Validate → Publish** - Safe course site deployment

![Teaching Workflow Demo](../demos/teaching-workflow.gif)

## Essential Commands

> Site/docs commands below moved to the `folio` plugin.

```bash
/folio:site:build          # Build preview (current branch)
/folio:site:publish        # Validate → Switch to main → Deploy
/folio:site:progress       # Semester progress dashboard
ask "git status" (dev/git skill) # Teaching-aware git status
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
ask "git status" (dev/git skill) # Should show teaching mode

# 3. Preview
/folio:site:build

# 4. Publish
/folio:site:publish
```

## Common Workflows

### Weekly Content Update

```bash
git checkout dev           # Start on preview
# ... edit content ...
/folio:site:build          # Preview changes
/folio:site:publish        # Deploy to production
```

### Check Progress

```bash
/folio:site:progress       # Semester dashboard
```

### Emergency Fix

```bash
git checkout main          # Go to production
# ... fix issue ...
/folio:site:build          # Build
git push origin main       # Deploy
git checkout dev           # Back to preview
```

## Validation

### Check Before Publish

```bash
/folio:site:publish --dry-run --validate-only
```

### Common Issues

| Issue | Fix |
|-------|-----|
| Missing week | Add to schedule.qmd |
| Date out of range | Check assignment due dates |
| Broken links | `/folio:docs:check-links` |
| Bad YAML | Validate teach-config.yml |

### Skip Validation (Emergency)

```bash
/folio:site:publish --skip-validation
```

## Branch Strategy

```
main (production) ← Students see this
  ↑
dev (preview) ← You edit here
```

**Rules:**

- Edit on `dev`
- Preview with `/folio:site:build`
- Publish with `/folio:site:publish` (auto-switches branches)
- Asking "git status" (dev/git skill) shows which branch you're on

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

### `/folio:site:build`

```bash
/folio:site:build              # Normal build
/folio:site:build --force      # Force rebuild
```

### `/folio:site:publish`

```bash
/folio:site:publish                    # Full workflow
/folio:site:publish --dry-run          # Preview what would happen
/folio:site:publish --validate-only    # Just run validation
/folio:site:publish --skip-validation  # Emergency publish
/folio:site:publish --force-rebuild    # Force site rebuild
```

### `/folio:site:progress`

```bash
/folio:site:progress           # Full dashboard
/folio:site:progress --json    # JSON output
```

## Troubleshooting

### Not Detecting Teaching Mode

```bash
# Check config exists
ls .flow/teach-config.yml

# Verify enabled
grep "enabled: true" .flow/teach-config.yml

# Test detection
ask "git status" (dev/git skill) # Should show teaching context
```

### Wrong Branch

```bash
ask "git status" (dev/git skill) # Shows current branch + context
git checkout dev               # Switch to preview
git checkout main              # Switch to production
```

### Validation Errors

```bash
# See what's wrong
/folio:site:publish --dry-run --validate-only

# Fix issues, then try again
/folio:site:publish
```

### Site Not Updating

```bash
# 1. Check GitHub Pages settings
# Repo → Settings → Pages

# 2. Force rebuild
git checkout main
/folio:site:build --force
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
