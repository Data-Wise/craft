# Tutorial: Badge Management Workflow

**Learn badge synchronization through hands-on scenarios**

## Overview

This tutorial walks through common badge management scenarios:

1. Version bump workflow
2. Adding CI workflow with badge
3. Fixing outdated badges
4. Multi-file sync
5. Troubleshooting badge issues

**Time**: 15-20 minutes
**Prerequisites**: Craft plugin installed, project with git repo

## Scenario 1: Version Bump Workflow

**Goal**: Update version from 2.9.0 to 2.10.0-dev and sync badges

### Step 1: Update Version File

```bash
cd your-project

# For craft plugin:
vim .claude-plugin/plugin.json
# Change: "version": "2.9.0" → "version": "2.10.0-dev"

# For Python project:
vim pyproject.toml
# Change: version = "2.9.0" → version = "2.10.0-dev"

# For Node project:
vim package.json
# Change: "version": "2.9.0" → "version": "2.10.0-dev"
```

### Step 2: Run Site Update

```bash
/craft:site:update
```

**Expected Output**:

```
Step 3.5: SYNCHRONIZING BADGES

Found 2 badge issues:

  README.md:
    • Update version badge: 2.9.0 → 2.10.0-dev

  docs/index.md:
    • Update version badge: 2.9.0 → 2.10.0-dev

Apply these updates? [y/N]: y

✓ Updated 2 badges
```

### Step 3: Verify Changes

```bash
# Check README.md
grep "version-2.10.0--dev" README.md

# Check docs/index.md
grep "version-2.10.0--dev" docs/index.md

# Both should show the updated badge
```

### What Happened

1. Site update detected version changed (Step 1)
2. Badge sync ran as Step 3.5
3. Detected version mismatch in both files
4. Prompted for approval
5. Updated both files atomically
6. Shields.io URL uses double-dash: `2.10.0--dev`

## Scenario 2: Adding CI Workflow with Badge

**Goal**: Create new CI workflow and add badge to README

### Step 1: Generate Workflow

```bash
/craft:ci:generate python
```

**Interactive prompts**:

- Python versions: `3.10, 3.11, 3.12`
- Enable linting: `yes`
- Enable type checking: `yes`

### Step 2: Badge Offer

After workflow creation:

```
╭─ CI Workflow Generated ─────────────────────────╮
│  ✅ Created: .github/workflows/ci.yml           │
│                                                 │
│  📛 Add CI badge to README.md? (y/n)            │
│                                                 │
│  Badge preview:                                 │
│  [![Craft CI](https://github.com/your-org/     │
│    your-repo/actions/workflows/ci.yml/          │
│    badge.svg?branch=dev)](...)                  │
│                                                 │
╰─────────────────────────────────────────────────╯

Add CI badge to README.md? [y/N]: y
```

### Step 3: Verify Badge Added

```bash
head -10 README.md
```

**Expected**:

```markdown
# Your Project

[![Version](...))](...)
[![Craft CI](https://github.com/your-org/your-repo/actions/workflows/ci.yml/badge.svg?branch=dev)](...)

> Project description
```

### What Happened

1. `ci:generate` created `.github/workflows/ci.yml`
2. Detected new workflow file
3. Generated CI badge with correct branch parameter (`dev`)
4. Offered to add badge to README
5. Inserted badge after title line

## Scenario 3: Fixing Outdated Badges

**Goal**: Fix badges with wrong branch parameter

### Step 1: Check Current Badges

```bash
grep "badge.svg" README.md
```

**Current state**:

```markdown
[![CI](https://github.com/org/repo/actions/workflows/ci.yml/badge.svg?branch=main)](...)
```

**Problem**: Badge uses `branch=main` but you're on `dev` branch

### Step 2: Validate CI Badges

```bash
/craft:ci:validate
```

**Output**:

```
╭─ CI Badge Validation ───────────────────────────╮
│                                                  │
│  📁 README.md                                    │
│                                                  │
│    ⚠️  Line 4: wrong_branch                     │
│       Badge uses 'main', expected 'dev'         │
│                                                  │
├──────────────────────────────────────────────────┤
│  Total: 1 warning                               │
│  Run with --fix to update badges                │
╰──────────────────────────────────────────────────╯
```

### Step 3: Apply Fix

**Option A**: Auto-fix via ci:validate

```bash
/craft:ci:validate --fix
```

**Option B**: Sync via site:update

```bash
/craft:site:update
# Step 3.5 will fix the branch parameter
```

### Step 4: Verify Fix

```bash
grep "badge.svg" README.md
```

**After fix**:

```markdown
[![CI](https://github.com/org/repo/actions/workflows/ci.yml/badge.svg?branch=dev)](...)
```

## Scenario 4: Multi-File Badge Sync

**Goal**: Ensure badges consistent across README.md and docs/index.md

### Step 1: Check Current State

```bash
# README version
grep "version-" README.md

# Docs version
grep "version-" docs/index.md
```

**Problem**: Different versions shown

- README.md: `version-2.10.0--dev`
- docs/index.md: `version-2.9.0`

### Step 2: Run Docs Update

```bash
/craft:docs:update
```

**Interactive mode**:

```
Documentation Update Plan:
  Categories detected:
  1. Badges — 1 badge outdated
  2. Version references — 3 files need updating

  Group 1: Metadata updates
    • badges (1 issue)
    • version_refs (3 issues)

How should I handle these updates?
  → Interactive - category by category

Update badges? (1 badge outdated in docs/index.md)
  [y/N]: y
```

### Step 3: Verify Sync

```bash
# Both should now match
grep "version-2.10.0--dev" README.md
grep "version-2.10.0--dev" docs/index.md
```

### What Happened

1. Docs update detected badge mismatch in metadata group
2. Grouped with version_refs for efficient prompting
3. Applied update to docs/index.md
4. Both files now show correct version

## Scenario 5: Troubleshooting Badge Issues

### Issue: Badge Parsing Fails

**Symptom**: Badge exists but detector returns empty list

**Debug**:

```python
# Step 1: Check file encoding
file README.md
# Should show: UTF-8 Unicode text

# Step 2: Test regex manually
python3 -c "
import re

content = open('README.md').read()
pattern = r'\[!\[([^\]]*)\]\(([^\)]+)\)\]\(([^\)]+)\)'
matches = re.findall(pattern, content)
print(f'Found {len(matches)} linked badges')
"

# Step 3: Check for unusual characters
grep -n "badge" README.md | cat -A
# Look for non-standard spaces, invisible chars
```

**Common fixes**:

- Remove non-breaking spaces around badge
- Ensure proper markdown formatting
- Check for unescaped characters in URLs

### Issue: Wrong Badge Type Detected

**Symptom**: Version badge classified as CUSTOM

**Debug**:

```python
from utils.badge_detector import BadgeDetector

detector = BadgeDetector()
badges = detector.parse_badges(Path('README.md'))

for badge in badges:
    print(f"Label: {badge.label}")
    print(f"URL: {badge.url}")
    print(f"Type: {badge.type}")
    print(f"Classification: {detector._classify_badge(badge.label, badge.url)}")
    print()
```

**Common fixes**:

- Add "version" to badge label
- Use shields.io `/badge/version-X.Y.Z` URL format
- Check URL contains classification keywords

### Issue: Sync Performance Slow

**Symptom**: Badge sync takes >5 seconds

**Debug**:

```python
import time
from utils.badge_syncer import BadgeSyncer

syncer = BadgeSyncer()

# Time each phase
start = time.time()
badges = syncer.detector.detect_all()
print(f"Detection: {time.time() - start:.3f}s")

start = time.time()
expected = syncer._generate_expected_badges(calculate_coverage=True)
print(f"Generation (with coverage): {time.time() - start:.3f}s")

start = time.time()
expected = syncer._generate_expected_badges(calculate_coverage=False)
print(f"Generation (no coverage): {time.time() - start:.3f}s")
```

**Common fixes**:

- Set `calculate_coverage=False` if coverage hasn't changed
- Limit files to only those that need updating
- Cache expected badges for repeated syncs

## Quick Reference

### Common Commands

```bash
# Auto-sync badges during site update
/craft:site:update

# Validate CI badges
/craft:ci:validate

# Fix CI badge issues
/craft:ci:validate --fix

# Interactive docs update (includes badges)
/craft:docs:update

# Generate workflow with badge offer
/craft:ci:generate python
```

### Python API

```python
# Detect badges
from utils.badge_detector import BadgeDetector
detector = BadgeDetector()
badges = detector.detect_all()

# Sync badges (dry-run)
from utils.badge_syncer import BadgeSyncer
syncer = BadgeSyncer()
mismatches = syncer.sync_badges(dry_run=True)

# Sync badges (apply)
mismatches = syncer.sync_badges(auto_confirm=True)

# Validate CI badges
from utils.ci_badge_validator import CIBadgeValidator
validator = CIBadgeValidator()
issues = validator.validate_badges()
```

### File Locations

| File | Purpose |
| ------ | --------- |
| `utils/badge_detector.py` | Badge parsing and classification |
| `utils/badge_syncer.py` | Badge synchronization orchestration |
| `utils/ci_badge_validator.py` | CI-specific validation |
| `tests/test_badge_*.py` | Test suite (98 tests) |

## Next Steps

After completing this tutorial:

1. **Explore**: Check badges in your own projects
2. **Experiment**: Try badge sync in different project types
3. **Customize**: Extend badge types for project-specific needs
4. **Automate**: Add badge sync to git pre-commit hooks (future)

## Resources

- [Badge Management Guide](../guide/badge-management.md) - Comprehensive reference
- [Site Commands](../commands/site.md) - Site update and deployment
- [CI Generate Command](../commands/ci/generate.md) - CI validation reference
- [SPEC: Badge System](../specs/_archive/SPEC-badge-system-2026-01-30.md) - Implementation spec
