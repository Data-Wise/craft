---
description: Update CLAUDE.md from project state with validation and optimization
category: docs
arguments:
  - name: dry-run
    description: Preview changes without executing
    required: false
    default: false
    alias: -n
  - name: interactive
    description: Prompt for each section update
    required: false
    default: false
    alias: -i
  - name: optimize
    description: Also condense verbose sections
    required: false
    default: false
    alias: -o
  - name: section
    description: "Specific section to update: status, commands, architecture, all (default: all)"
    required: false
    default: all
  - name: validate
    description: Run audit after update to verify
    required: false
    default: true
tags: [documentation, claude-md, project-analysis]
version: 1.0.0
---

# /craft:docs:claude-md:update - Update CLAUDE.md

Update CLAUDE.md to reflect current project state with validation and optimization.

## Purpose

Synchronize CLAUDE.md with:

- Current version (from plugin.json/package.json/pyproject.toml/DESCRIPTION)
- New/changed commands, skills, agents (for craft plugins)
- Project structure changes
- Status updates from .STATUS file
- Test coverage changes

## When Invoked

This command follows the **"Show Steps First"** pattern from craft v2.9.0.

### Step 0: Detect and Analyze

```python
# Import detector utility
from utils.claude_md_detector import detect_project

# Detect project type
project_info = detect_project()

if not project_info:
    print("Could not detect project type")
    exit(1)

# Analyze current CLAUDE.md
claude_md_path = Path("CLAUDE.md")
if not claude_md_path.exists():
    print("No CLAUDE.md found - use /craft:docs:claude-md:scaffold instead")
    exit(1)

current_content = claude_md_path.read_text()
```

### Step 0.5: Show Update Plan

```
╭─ CLAUDE.md Update Plan ──────────────────────────────────╮
│ Project: craft (Craft Plugin)                            │
│ Type: craft-plugin                                       │
│ Mode: default                                            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ Changes Detected:                                        │
│                                                          │
│ 1. Version Mismatch                                      │
│    Current: v2.8.1                                       │
│    Actual:  v2.9.0 ⚠️                                     │
│    Source:  .claude-plugin/plugin.json                   │
│                                                          │
│ 2. New Commands (3)                                      │
│    + /craft:docs:claude-md:audit                         │
│    + /craft:docs:claude-md:fix                           │
│    + /craft:docs:claude-md:scaffold                      │
│                                                          │
│ 3. Test Count Update                                     │
│    Current: 770 tests                                    │
│    Actual:  847 tests (+77)                              │
│                                                          │
│ 4. Documentation Status                                  │
│    Current: 95% complete                                 │
│    Actual:  98% complete (+3%)                           │
│                                                          │
│ Net Changes: +18 lines, -5 lines                         │
│                                                          │
├──────────────────────────────────────────────────────────┤
│ ? Proceed with these updates?                            │
│   > Yes - Apply all changes (Recommended)                │
│     Interactive - Select which sections to update        │
│     Dry run - Show preview without applying              │
│     Cancel - Exit without changes                        │
╰──────────────────────────────────────────────────────────╯
```

### Step 1-N: Execute Updates

Based on user choice:

**Option: Apply all changes**

```
[1/4] Updating version... v2.8.1 → v2.9.0 ✓
[2/4] Adding new commands... +3 commands ✓
[3/4] Updating test count... 770 → 847 tests ✓
[4/4] Updating documentation status... 95% → 98% ✓
```

**Option: Interactive mode**

```
Section: Project Status (version mismatch)
  Update v2.8.1 → v2.9.0? (y/n/skip) >
```

**Option: Dry run**

```
┌─────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: /craft:docs:claude-md:update                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Would update: CLAUDE.md                                 │
│                                                         │
│ SYNC:                                                   │
│   • Version: v2.8.1 → v2.9.0                           │
│   • Commands: +3 new                                   │
│   • Tests: 770 → 847 (+77)                             │
│   • Docs: 95% → 98% (+3%)                              │
│                                                         │
│ VALIDATE:                                               │
│   • Template: Craft Plugin (matches)                   │
│   • Required sections: 5/5 ✓                           │
│   • Stale references: 0                                │
│                                                         │
│ Estimated: +18 lines, -5 lines                          │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ Run without --dry-run to apply                          │
└─────────────────────────────────────────────────────────┘
```

### Step N+1: Validation and Summary

```
✅ CLAUDE.MD UPDATED

Applied:
  • Synced version: v2.8.1 → v2.9.0
  • Added 3 new commands
  • Updated test count: 770 → 847
  • Updated documentation: 95% → 98%

File changes:
  Lines: 329 → 342 (+13)
  Sections: 8 (unchanged)

─── Post-Update Validation ────────────────────────

✓ All required sections present
✓ Version matches plugin.json
✓ All commands documented
✓ No broken links detected

Next steps:
  1. Review: git diff CLAUDE.md
  2. Commit: git add CLAUDE.md && git commit -m "docs: update CLAUDE.md for v2.9.0"
```

## Project Type Detection

Uses `utils/claude_md_detector.py` to detect:

| Type | Markers | Version Source |
|------|---------|----------------|
| **craft-plugin** | `.claude-plugin/plugin.json` | plugin.json |
| **teaching-site** | `_quarto.yml` + `course.yml` | _quarto.yml |
| **r-package** | `DESCRIPTION` + `NAMESPACE` | DESCRIPTION |
| **mcp-server** | `package.json` + mcp in name/deps | package.json |
| **generic-node** | `package.json` | package.json |
| **generic-python** | `pyproject.toml` | pyproject.toml |

## Sections Updated

### All Project Types

1. **Version** - Synced from version source
2. **Status** - Synced from .STATUS file (if exists)

### Craft Plugin Specific

3. **Commands** - Auto-discovered from `commands/` directory
4. **Skills** - Auto-discovered from `skills/` directory
5. **Agents** - Auto-discovered from `agents/` directory
6. **Test Count** - Counted from `tests/` directory
7. **Documentation Status** - Calculated from completeness

### Teaching Site Specific

3. **Course Info** - From _quarto.yml
4. **Weeks** - From weeks/ directory
5. **Assignments** - From filesystem scan

### R Package Specific

3. **Package Info** - From DESCRIPTION
4. **Functions** - From R/ directory scan
5. **Tests** - From tests/testthat/
6. **Documentation** - From man/ and pkgdown

## Section-Specific Updates

### Update only version/status

```bash
/craft:docs:claude-md:update status
```

Syncs version, progress, recent achievements from .STATUS.

### Update only commands

```bash
/craft:docs:claude-md:update commands
```

Scans for new/removed commands, updates Quick Reference section.

### Update only architecture

```bash
/craft:docs:claude-md:update architecture
```

Compares filesystem to documented structure, adds/removes directories.

## Optimization Mode

```bash
/craft:docs:claude-md:update --optimize
/craft:docs:claude-md:update -o
```

Also applies optimization to verbose sections:

```
📝 OPTIMIZATION APPLIED

Before: 329 lines
After: 287 lines (-42 lines, -13%)

Optimizations:
  • Architecture: condensed file listings
  • Quick Reference: grouped commands
  • Removed duplicate information
  • Tightened verbose descriptions

Quality maintained:
  ✅ All essential info preserved
  ✅ All links still valid
  ✅ Structure unchanged
```

## Interactive Mode

```bash
/craft:docs:claude-md:update --interactive
/craft:docs:claude-md:update -i
```

Prompts for confirmation on each section:

```
Update section: Project Status (version mismatch)
  Change: v2.8.1 → v2.9.0
  Apply? (y/n/skip) >

Update section: Quick Commands (3 new)
  Adding:
    - /craft:docs:claude-md:audit
    - /craft:docs:claude-md:fix
    - /craft:docs:claude-md:scaffold
  Apply? (y/n/skip) >
```

## Validation After Update

By default, runs validation after update (skip with `--validate=false`):

```
─── Post-Update Audit ────────────────────────

Checks:
  ✓ Version matches source
  ✓ All commands documented
  ✓ Required sections present
  ✓ No stale references
  ✓ Links valid

Results:
  🔴 Errors:   0
  ⚠️ Warnings: 0
  📝 Info:     1 (optimization available)
```

## Implementation Notes

### Wave 2 TODO (Full Implementation)

The following logic needs to be implemented in Wave 2:

1. **Change Detection**
   - Compare CLAUDE.md with project state
   - Identify version mismatches
   - Find new/removed commands
   - Detect structure changes

2. **Update Application**
   - Apply changes per section
   - Preserve user customizations
   - Maintain formatting consistency

3. **Validation**
   - Check template compliance
   - Verify all required sections
   - Validate links
   - Check for stale references

4. **Optimization**
   - Identify verbose sections
   - Apply safe condensation
   - Preserve essential information

### Dependencies

- `utils/claude_md_detector.py` - Project type detection (✓ Wave 1)
- `skills/ci/project-detector.md` - Extended detection patterns (existing)
- `.STATUS` file parsing - For status sync (TBD)
- Link validation - For verification (existing in craft)

## Related Commands

| Command | Purpose |
|---------|---------|
| `/craft:docs:claude-md:audit` | Validate CLAUDE.md (read-only) - Phase 2 |
| `/craft:docs:claude-md:fix` | Auto-fix common issues - Phase 2 |
| `/craft:docs:claude-md:scaffold` | Create from template - Phase 3 |
| `/craft:docs:claude-md:edit` | Interactive editing - Phase 3 |
| `/craft:docs:update` | Update all documentation |
| `/craft:check` | Pre-flight validation (includes CLAUDE.md) |

## Examples

### Quick update after adding commands

```bash
/craft:docs:claude-md:update
```

Shows plan, applies all changes, validates.

### Preview changes without applying

```bash
/craft:docs:claude-md:update --dry-run
```

Shows what would change, exits without modifying.

### Update with optimization

```bash
/craft:docs:claude-md:update --optimize
```

Updates AND condenses verbose sections.

### Interactive section selection

```bash
/craft:docs:claude-md:update --interactive
```

Prompts for each section change.

### Update specific section only

```bash
/craft:docs:claude-md:update commands
```

Only updates command list, skips other sections.

## See Also

- **Guide:** [Interactive Commands](../../guide/interactive-commands.md)
- **Spec:** [CLAUDE-MD Command Porting](../../specs/SPEC-claude-md-port.md)
- **Template:** Show Steps First pattern
- **Utility:** `utils/claude_md_detector.py`

---

## Execution (Phase 1 Implementation)

This command is now fully functional with core metric updates.

### Usage

```bash
# Basic update (shows preview, asks for confirmation)
/craft:docs:claude-md:update

# Dry-run mode (preview only, no changes)
/craft:docs:claude-md:update --dry-run
/craft:docs:claude-md:update -n

# Direct execution (for automation)
python3 utils/claude_md_updater_simple.py
python3 utils/claude_md_updater_simple.py --dry-run
```

### What Gets Updated

**Core Metrics (Phase 1):**

- Version number (from plugin.json/package.json/pyproject.toml/DESCRIPTION)
- Command count (**N commands**)
- Skill count (**N skills**)
- Agent count (**N agents**)
- Test count (**Tests: N passing**)
- Documentation percentage (from .STATUS file)

**Future (Phase 2+):**

- Individual command documentation
- Architecture section
- Section-specific updates
- Template validation
- Link checking

### Execution Flow

```python
#!/usr/bin/env python3
# This is the actual execution logic

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.claude_md_detector import detect_project
from utils.claude_md_updater_simple import update_claude_md

# Detect project
project_info = detect_project()
if not project_info:
    print("❌ Could not detect project type")
    sys.exit(1)

# Run updater (respects --dry-run flag)
changes, message = update_claude_md(
    dry_run="--dry-run" in sys.argv or "-n" in sys.argv
)

# Print result
print(message)

# Exit with success if changes found or up to date
sys.exit(0 if changes or "up to date" in message.lower() else 1)
```

### Integration Points

This command integrates with:

1. **Project Detector** (`utils/claude_md_detector.py`)
   - Detects 6 project types
   - Extracts version from 4 sources
   - Counts commands/skills/agents

2. **Simple Updater** (`utils/claude_md_updater_simple.py`)
   - Detects metric changes
   - Generates preview
   - Applies changes with confirmation

3. **Test Suite** (`tests/test_claude_md_phase1.py`)
   - 10 comprehensive tests
   - 100% passing
   - Covers detection and updates

### Phase 1 Status

**Complete:**

- ✅ Detector utility (craft-plugin, teaching, R package, MCP, generic)
- ✅ Simple updater (6 core metrics)
- ✅ Dry-run mode
- ✅ Preview generation
- ✅ Test suite (10/10 passing)

**Deferred to Phase 2:**

- Interactive mode (per-section prompts)
- Optimize mode (condense sections)
- Individual command tracking
- Template validation
- Link checking

### Testing

```bash
# Run Phase 1 tests
python3 tests/test_claude_md_phase1.py

# Test detector
python3 utils/claude_md_detector.py

# Test updater (dry-run)
python3 utils/claude_md_updater_simple.py --dry-run

# Test updater (apply)
python3 utils/claude_md_updater_simple.py
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "Could not detect project type" | Ensure .claude-plugin/plugin.json or DESCRIPTION exists |
| "CLAUDE.md not found" | Use `/craft:docs:claude-md:scaffold` to create |
| Version not updating | Check version source file exists and is readable |
| Test count wrong | Detector counts test_*.py files in tests/ |

---

**Version:** 1.0.0 (Phase 1 - Core Metrics)
**Status:** Fully Functional
**Coverage:** 10/10 tests passing (100%)
