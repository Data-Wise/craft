# Badge Management Guide

**Automatic badge synchronization for README.md and docs/index.md**

## Overview

The badge management system ensures version, CI status, and documentation coverage badges stay in sync across README.md and docs/index.md. Badge sync integrates into existing commands (`/craft:site:update`, `/craft:docs:update`) and provides CI-specific validation.

### Key Features

- **Auto-sync during site updates** - Step 3.5 in `/craft:site:update`
- **Version badge generation** - Extracts from plugin.json, package.json, pyproject.toml
- **CI badge generation** - Scans `.github/workflows/*.yml` files
- **Coverage badges** - Calculates from `.STATUS` file
- **Branch-aware validation** - Checks badge branch parameters match current branch
- **Multi-file sync** - Updates README.md and docs/index.md together
- **4 project types** - Craft plugins, Python CLI, Node CLI, teaching sites

## Badge Types

| Type | Generated From | Example |
|------|----------------|---------|
| **Version** | plugin.json, package.json, pyproject.toml | `[![Version](https://img.shields.io/badge/version-2.10.0--dev-blue.svg)](...)` |
| **CI Status** | `.github/workflows/*.yml` files | `[![CI](https://github.com/user/repo/actions/workflows/ci.yml/badge.svg?branch=dev)](...)` |
| **Docs Coverage** | `.STATUS` file "Documentation: XX%" | `[![Documentation](https://img.shields.io/badge/docs-98%25%20complete-brightgreen.svg)](...)` |
| **Test Coverage** | External service (codecov, coveralls) | `[![Coverage](https://codecov.io/gh/user/repo/badge.svg)](...)` |
| **Custom** | User-defined badges | Any other badge format |

## Integration Points

### 1. Site Update (Primary Integration)

Badge sync runs automatically during `/craft:site:update` as **Step 3.5**:

```bash
/craft:site:update
```

#### Flow

```text
Step 1: Detect Changes
Step 2: Update Detection Matrix
Step 3: Execute Updates
  ├─ Update REFCARD.md
  ├─ Update commands.md
  ├─ Update index.md
  └─ Update Configuration Reference

Step 3.5: Synchronize Badges  ← NEW
  ├─ Detect badge mismatches
  ├─ Show diff (version, CI, coverage)
  ├─ Prompt for approval
  └─ Apply updates

Step 4: Validate
Step 5: Show Results
```

#### Output Example

```
┌─────────────────────────────────────────────────────────────┐
│ Step 3.5: SYNCHRONIZING BADGES                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Found 3 badge issues:                                       │
│                                                             │
│   README.md:                                                │
│     • Update version badge: 2.9.1 → 2.10.0-dev              │
│     • Fix CI badge branch: main → dev                       │
│                                                             │
│   docs/index.md:                                            │
│     • Update version badge: 2.9.1 → 2.10.0-dev              │
│                                                             │
│ Apply these updates? [y/N]: y                               │
│                                                             │
│ ✓ Updated 3 badges                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. Docs Update (Detection Integration)

Badge issues are detected as a **metadata category** alongside version_refs and command_counts:

```bash
/craft:docs:update
```

```
Documentation Update Plan:
  Categories detected:
  1. Badges — 3 badges outdated (version, branch)
  2. Version references — 12 files need updating
  3. Command counts — 4 files with outdated counts

  Group 1: Metadata updates
    • badges (3 issues)
    • version_refs (12 issues)
    • command_counts (4 issues)

  How should I handle these updates?
    → Interactive - category by category (Recommended)
```

### 3. CI Validate (Badge Checks)

CI badge validation checks workflow existence and branch parameters:

```bash
/craft:ci:validate
```

#### Validation Checks

| Check | Description | Severity |
|-------|-------------|----------|
| **Workflow Exists** | Badge points to actual `.github/workflows/*.yml` file | Error |
| **Branch Correct** | Badge `?branch=` parameter matches current branch | Warning |
| **URL Format** | Badge follows GitHub Actions URL pattern | Warning |

#### Output Example

```
╭─ CI Badge Validation ───────────────────────────╮
│                                                  │
│  📁 README.md                                    │
│                                                  │
│    ❌ Line 3: missing_workflow                  │
│       Badge points to non-existent workflow     │
│                                                  │
│    ⚠️  Line 4: wrong_branch                     │
│       Badge uses 'main', expected 'dev'         │
│                                                  │
├──────────────────────────────────────────────────┤
│  Total: 1 error, 1 warning                      │
│  Run with --fix to update badges                │
╰──────────────────────────────────────────────────╯
```

### 4. CI Generate (Badge Offer)

After creating a workflow, offer to add CI badge:

```bash
/craft:ci:generate python
```

```
╭─ CI Workflow Generated ─────────────────────────╮
│  ✅ Created: .github/workflows/ci.yml           │
│                                                 │
│  📛 Add CI badge to README.md? (y/n)            │
│                                                 │
│  Badge preview:                                 │
│  [![Craft CI](https://github.com/user/repo/    │
│    actions/workflows/ci.yml/badge.svg?          │
│    branch=dev)](https://github.com/user/repo/   │
│    actions/workflows/ci.yml)                    │
│                                                 │
╰─────────────────────────────────────────────────╯
```

## Command Reference

### Manual Badge Sync

While badge sync integrates into existing commands, you can also run it standalone:

```python
from utils.badge_syncer import BadgeSyncer
from pathlib import Path

syncer = BadgeSyncer(Path.cwd())

# Dry-run (preview only)
mismatches = syncer.sync_badges(dry_run=True)

# Apply updates (with prompt)
mismatches = syncer.sync_badges(auto_confirm=False)

# Auto-apply (no prompt)
mismatches = syncer.sync_badges(auto_confirm=True)
```

### Badge Detection

Detect badges without syncing:

```python
from utils.badge_detector import BadgeDetector, BadgeType
from pathlib import Path

detector = BadgeDetector(Path.cwd())

# Detect all badges
badges = detector.detect_all()

# Filter by type
version_badges = detector.get_badges_by_type(BadgeType.VERSION, badges)
ci_badges = detector.get_badges_by_type(BadgeType.CI_STATUS, badges)

# Show summary
print(detector.format_badge_summary(badges))
```

### CI Badge Validation

Validate CI badges independently:

```python
from utils.ci_badge_validator import CIBadgeValidator, format_issues_report
import subprocess

validator = CIBadgeValidator(Path.cwd())
branch = subprocess.run(['git', 'branch', '--show-current'], ...).stdout.strip()

issues = validator.validate_badges(branch=branch)

if issues:
    print(format_issues_report(issues))
```

## Architecture

### Component Overview

```
utils/
├── badge_detector.py         # Parse badges from markdown
├── badge_syncer.py            # Orchestrate synchronization
└── ci_badge_validator.py      # Validate CI badges

commands/
├── site/update.md             # Step 3.5: Badge sync
├── docs/update.md             # Badges in metadata group
├── ci/validate.md             # Badge URL validation
└── ci/generate.md             # Badge generation offer

Integration:
- docs_update_orchestrator.py  # Badge detection category
- claude_md_detector.py        # Version extraction (reused)
```

### Data Flow

```
1. Detection
   ├─ badge_detector.parse_badges() → List[Badge]
   └─ badge_syncer._generate_expected_badges() → Dict[str, Badge]

2. Comparison
   └─ badge_syncer._find_mismatches() → List[BadgeMismatch]

3. Display
   └─ badge_syncer._show_diff() → Console output

4. Apply
   └─ badge_syncer._apply_updates() → Update files
```

## Project Type Support

### Craft Plugin

```
.claude-plugin/plugin.json   → Version badge
.github/workflows/*.yml       → CI badges
.STATUS                       → Docs coverage badge
```

### Python CLI

```
pyproject.toml                → Version badge
.github/workflows/*.yml       → CI badges
```

### Node CLI

```
package.json                  → Version badge
.github/workflows/*.yml       → CI badges
```

### Teaching Site

```
package.json or _quarto.yml   → Version badge
.github/workflows/*.yml       → CI badges (if present)
```

## Mismatch Severity

### Critical (Red ❌)

- Version number incorrect (e.g., 2.9.0 when should be 2.10.0-dev)
- Badge completely missing

**Action Required**: Must fix before release

### Warning (Yellow ⚠️)

- CI badge branch parameter wrong (e.g., `?branch=main` when on `dev`)
- Workflow file changed but badge not updated

**Recommended**: Fix to prevent confusion

### Info (Blue ℹ️)

- Docs coverage percentage changed (95% → 98%)
- Badge color cosmetic difference

**Optional**: Update when convenient

## Badge URL Format

### Version Badge

```
Format:
https://img.shields.io/badge/version-<VERSION>-<COLOR>.svg

Example:
https://img.shields.io/badge/version-2.10.0--dev-blue.svg
                                        ^^^ (double dash escapes single dash)

Colors:
- blue: Development versions (dev, alpha, beta)
- brightgreen: Release versions (1.0.0, 2.5.1)
```

### CI Badge

```
Format:
https://github.com/<OWNER>/<REPO>/actions/workflows/<WORKFLOW>/badge.svg?branch=<BRANCH>

Example:
https://github.com/Data-Wise/craft/actions/workflows/ci.yml/badge.svg?branch=dev

Linked:
[![Craft CI](BADGE_URL)](WORKFLOW_URL)
```

### Coverage Badge

```
Format:
https://img.shields.io/badge/docs-<PERCENT>%25%20complete-<COLOR>.svg
                                         ^^^ (URL-encoded %)

Colors:
- brightgreen: ≥95%
- green: 85-94%
- yellowgreen: 75-84%
- yellow: <75%
```

## Error Handling

### Non-Blocking Errors

Badge sync failures don't stop site/docs updates:

```python
try:
    mismatches = syncer.sync_badges(...)
except Exception as e:
    print(f"⚠️  Badge sync failed: {e}")
    print("Continuing with site update...")
    # Site update continues
```

### Graceful Degradation

Missing dependencies are handled gracefully:

```python
try:
    from badge_syncer import BadgeSyncer
    # ... badge sync logic
except ImportError:
    print("⚠️  Badge utilities not available, skipping")
    # Continue without badge sync
```

### Permission Errors

File write failures are caught and reported:

```python
try:
    file_path.write_text(updated_content)
    print(f"✅ Updated {file_path.name}")
except OSError as e:
    print(f"❌ Failed to update {file_path.name}: {e}")
    # Continue with other files
```

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Badge detection | <1ms | Regex-based, single pass |
| Version extraction | <1ms | Cached by CLAUDEMDDetector |
| CI badge generation | 5-10ms | Scans workflow directory |
| Coverage calculation | 1-5ms | Reads .STATUS file |
| Full sync (2 files) | <50ms | Includes detection + updates |

### Optimization Tips

1. **Skip coverage calculation** when not needed:

   ```python
   syncer.sync_badges(calculate_coverage=False)
   ```

2. **Use dry-run** for preview:

   ```python
   mismatches = syncer.sync_badges(dry_run=True)
   # Files not modified, fast preview
   ```

3. **Limit files** to only what needs updating:

   ```python
   syncer.sync_badges(files=['README.md'])  # Skip docs/index.md
   ```

## Troubleshooting

### Badge Not Detected

**Symptom**: Badge exists but not found by detector

**Causes**:

- Malformed markdown syntax
- Badge on line with other complex markdown
- Unusual URL format

**Fix**:

```bash
# Test badge parsing
cd ~/.git-worktrees/craft/feature-badge-management
python3 -c "
from utils.badge_detector import BadgeDetector
from pathlib import Path

detector = BadgeDetector()
badges = detector.parse_badges(Path('README.md'))
for b in badges:
    print(f'Line {b.line_number}: {b.label} ({b.type.value})')
"
```

### Version Not Extracted

**Symptom**: Badge sync shows "None → None" for version

**Causes**:

- Version file not in expected location
- Unusual version format
- Regex doesn't match version pattern

**Fix**:

```python
# Test version extraction
from utils.badge_detector import Badge, BadgeType
from pathlib import Path

badge = Badge(
    type=BadgeType.VERSION,
    label="Version",
    url="https://img.shields.io/badge/version-2.10.0--dev-blue.svg",
    link_url=None,
    raw_markdown="",
    file_path=Path("README.md"),
    line_number=1
)

detector = BadgeDetector()
version = detector.extract_version_from_badge(badge)
print(f"Extracted: {version}")  # Should show "2.10.0-dev"
```

### Badge Updates Not Applied

**Symptom**: Dry-run shows mismatches but files not updated

**Causes**:

- Using `dry_run=True` (intentional)
- User declined prompt (`auto_confirm=False`)
- File permissions issue

**Fix**:

```python
# Force apply with auto-confirm
syncer.sync_badges(auto_confirm=True, dry_run=False)
```

### CI Badge Branch Wrong

**Symptom**: Badge shows `?branch=main` but you're on `dev`

**This is EXPECTED behavior** when:

- Working on feature branch
- Badge should point to main branch for stability

**Fix (if needed)**:

```bash
/craft:ci:validate --fix
# Or
/craft:site:update  # Step 3.5 will fix
```

### Coverage Not Calculated

**Symptom**: Docs coverage badge missing

**Causes**:

- No `.STATUS` file
- `.STATUS` missing "Documentation: XX%" line
- `calculate_coverage=False` in sync call

**Fix**:

```bash
# Add to .STATUS file
echo "Documentation: 95% complete" >> .STATUS

# Or manually calculate
# Count documented commands / total commands * 100
```

## Testing

### Unit Tests

```bash
# Badge detector (35 tests)
python3 tests/test_badge_detector.py -v

# Badge syncer (30 tests)
python3 tests/test_badge_syncer.py -v

# CI badge validator (16 tests)
python3 tests/test_ci_badge_validator.py -v

# Integration tests (17 tests)
python3 tests/test_badge_syncer_integration.py -v
```

### Coverage

```bash
python3 -m pytest tests/test_badge_*.py \
    --cov=utils.badge_detector \
    --cov=utils.badge_syncer \
    --cov=utils.ci_badge_validator \
    --cov-report=term-missing

# Target: 90%+ coverage
```

### Manual Testing

```bash
# Test badge detection
cd your-project
python3 -c "
from utils.badge_detector import BadgeDetector
detector = BadgeDetector()
badges = detector.detect_all()
print(detector.format_badge_summary(badges))
"

# Test badge sync (dry-run)
python3 -c "
from utils.badge_syncer import BadgeSyncer
syncer = BadgeSyncer()
mismatches = syncer.sync_badges(dry_run=True)
print(f'{len(mismatches)} badges need updating')
"

# Test CI validation
python3 -c "
from utils.ci_badge_validator import CIBadgeValidator, format_issues_report
validator = CIBadgeValidator()
issues = validator.validate_badges()
if issues:
    print(format_issues_report(issues))
"
```

## Best Practices

### When to Sync Badges

✅ **Sync automatically during**:

- Site updates (`/craft:site:update`)
- Version bumps (changing plugin.json/package.json)
- CI workflow changes (adding/modifying workflows)
- Documentation updates (`/craft:docs:update`)

❌ **Don't sync during**:

- Feature branch work (badges should point to stable branches)
- Temporary experiments
- Draft documentation

### Branch Strategy

**Main branch** (`main`):

- Badges should use `?branch=main`
- Represents stable, production-ready code

**Dev branch** (`dev`):

- Badges should use `?branch=dev`
- Shows current development status

**Feature branches** (`feature/*`):

- Badges inherited from parent branch
- Don't update badges on feature branches (wait for merge)

### Badge Placement

Recommended order in README.md:

```markdown
# Project Title

[![Version](...))](...)
[![CI Status](...))](...)
[![Documentation Quality](...))](...)
[![Documentation](...))](...)

> Project description
```

### Version Badge Colors

Follow semantic coloring:

```python
# badge_syncer.py logic:
if '-dev' in version or '-alpha' in version or '-beta' in version:
    color = 'blue'          # Development/pre-release
else:
    color = 'brightgreen'   # Stable release
```

## Advanced Usage

### Custom Badge Detection

Extend badge classification for project-specific badges:

```python
class CustomBadgeDetector(BadgeDetector):
    def _classify_badge(self, label: str, url: str) -> BadgeType:
        # Custom logic
        if 'my-custom-badge' in url:
            return BadgeType.CUSTOM

        # Fall back to default
        return super()._classify_badge(label, url)
```

### Selective File Sync

Update only specific files:

```python
# Only update README
syncer.sync_badges(files=['README.md'])

# Only update docs
syncer.sync_badges(files=['docs/index.md'])
```

### Skip Coverage Calculation

For faster sync when coverage hasn't changed:

```python
syncer.sync_badges(calculate_coverage=False)
```

## Related Commands

| Command | Badge Integration |
|---------|-------------------|
| `/craft:site:update` | Step 3.5: Badge sync |
| `/craft:docs:update` | Badges in metadata group |
| `/craft:ci:validate` | CI badge validation |
| `/craft:ci:generate` | CI badge generation offer |
| `/craft:check` | Future: Pre-commit badge check |

## See Also

- [Site Update Command](../commands/site/update.md) - Step 3.5 documentation
- [Docs Update Command](../commands/docs/update.md) - Interactive category workflow
- [CI Validate Command](../commands/ci/validate.md) - Badge validation details
- [CI Generate Command](../commands/ci/generate.md) - Badge generation workflow
- [SPEC: Badge System](../specs/SPEC-badge-system-2026-01-30.md) - Implementation spec
