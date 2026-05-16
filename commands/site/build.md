---
description: Build documentation site (Quarto, pkgdown, MkDocs) with teaching mode support
category: site
arguments:
  - name: dry-run
    description: Preview build configuration without building
    required: false
    default: false
    alias: -n
deprecated: true
replaced-by: "skills/docs/site-management/"
---

# /craft:site:build - Build Documentation Site

Build static documentation sites based on detected project type. Automatically detects teaching mode and shows semester progress and validation.

## Usage

```bash
# Preview build plan
/craft:site:build --dry-run
/craft:site:build -n

# Build site
/craft:site:build
```

## Teaching Mode

When building a teaching project (detected via `.flow/teach-config.yml`, `_quarto.yml` metadata, or project structure), the command:

1. **Before Build**: Shows semester progress and runs content validation
2. **During Build**: Executes standard build process
3. **After Build**: Shows deployment URLs, progress summary, and suggested next steps

**Example Output (Teaching Mode)**:

```
┌─────────────────────────────────────────────┐
│ 📚 TEACHING MODE DETECTED                   │
├─────────────────────────────────────────────┤
│ Course: STAT 545 (Spring 2026)              │
│ Progress: Week 5/16 (31% complete)          │
│                                             │
│ 🔍 VALIDATION:                              │
│ ✅ Syllabus sections: complete              │
│ ✅ Schedule: 16/16 weeks                    │
│ ⚠️  Assignments: 2/3 found (hw-3 missing)   │
│                                             │
│ Status: Ready to build (warnings only)      │
└─────────────────────────────────────────────┘

[Build output...]

┌─────────────────────────────────────────────┐
│ ✅ BUILD COMPLETE                           │
├─────────────────────────────────────────────┤
│ 🌐 DEPLOYMENT URLS:                         │
│ • Draft: https://draft.example.com          │
│ • Production: https://course.example.com    │
│                                             │
│ 📊 SEMESTER PROGRESS:                       │
│ Week 5/16 · 31% complete                    │
│ Next: Spring Break in 18 days               │
│                                             │
│ 💡 NEXT STEPS:                              │
│ • Review build output above                 │
│ • Preview locally: /craft:site:preview      │
│ • Publish to production: /craft:site:publish│
│ • Check progress: /craft:site:progress      │
└─────────────────────────────────────────────┘
```

## Dry-Run Output

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Build Documentation Site                           │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Detection:                                                  │
│   - Type: MkDocs                                              │
│   - Config: mkdocs.yml                                        │
│   - Theme: material                                           │
│                                                               │
│ ✓ Build Plan:                                                 │
│   - Command: mkdocs build                                     │
│   - Output directory: site/                                   │
│   - Estimated files: ~450                                     │
│   - Estimated size: ~2.3 MB                                   │
│                                                               │
│ 📊 Summary: Build MkDocs site to site/ directory               │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

## Context Detection

Automatically detects documentation type:

| File | Type | Build Command |
|------|------|---------------|
| `mkdocs.yml` | MkDocs | `mkdocs build` |
| `_quarto.yml` | Quarto | `quarto render` |
| `_pkgdown.yml` | pkgdown | `pkgdown::build_site()` |

## Build Process

### MkDocs

```bash
mkdocs build
```

**Output**: `site/` directory

### Quarto

```bash
quarto render
```

**Output**: `_site/` or `docs/` (check `_quarto.yml`)

### pkgdown

```r
pkgdown::build_site()
```

**Output**: `docs/` directory

## Output

```
✅ SITE BUILT SUCCESSFULLY

Type: MkDocs
Output: site/
Files: 450 files generated
Size: 2.3 MB

Next steps:
• Preview locally: /craft:site:preview
• Deploy to GitHub Pages: /craft:site:deploy
• Check for issues: /craft:site:check
```

## Error Handling

If build fails:

1. Show the error message
2. Suggest common fixes
3. Offer to help debug

**Common issues:**

- Missing dependencies
- Broken links
- Invalid YAML
- Missing referenced files

## Implementation

The command uses the following utilities for teaching mode integration:

```python
#!/usr/bin/env python3
"""Build documentation site with teaching mode support."""

import os
import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "utils"))
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from detect_teaching_mode import detect_teaching_mode
from teach_config import load_teach_config
from teaching_validation import validate_teaching_content
from semester_progress import calculate_current_week

def show_teaching_context_before_build(cwd: str = "."):
    """Show teaching context before building."""
    try:
        config = load_teach_config(cwd)
        if not config:
            return  # Not teaching mode or config error

        # Get semester progress
        progress = calculate_current_week(config)

        # Run validation
        validation = validate_teaching_content(cwd)

        # Format course info
        course = config.get("course", {})
        course_name = f"{course.get('number', 'Course')} ({course.get('semester', '')} {course.get('year', '')})"

        # Build validation summary
        val_lines = []
        syllabus_ok = all(validation.checks.get(f"Syllabus: {s}", False)
                         for s in ["grading", "policies", "objectives", "schedule"])
        schedule_ok = validation.checks.get("Schedule: exists", False)

        if syllabus_ok:
            val_lines.append("✅ Syllabus sections: complete")
        else:
            missing = [s for s in ["grading", "policies", "objectives", "schedule"]
                      if not validation.checks.get(f"Syllabus: {s}", False)]
            val_lines.append(f"❌ Syllabus missing: {', '.join(missing)}")

        schedule_info = next((k for k in validation.checks.keys() if "weeks complete" in k), None)
        if schedule_info:
            val_lines.append(f"✅ Schedule: {schedule_info.split(':')[1].strip()}")
        elif not schedule_ok:
            val_lines.append("❌ Schedule: not found")

        # Assignment validation
        assignment_info = next((k for k in validation.checks.keys() if "Assignments:" in k), None)
        if assignment_info and "found" in assignment_info:
            parts = assignment_info.split(":")
            if len(parts) > 1:
                found_info = parts[1].strip()
                if "0/" not in found_info and found_info.endswith("found"):
                    # Extract missing assignment names from warnings
                    missing_names = []
                    for warning in validation.warnings:
                        if "Missing assignment files:" in warning:
                            missing_names = warning.split(": ")[1].split(", ")

                    if missing_names:
                        val_lines.append(f"⚠️  Assignments: {found_info} ({', '.join(missing_names)} missing)")
                    else:
                        val_lines.append(f"✅ Assignments: {found_info}")
                else:
                    val_lines.append(f"⚠️  Assignments: {found_info}")

        # Determine status
        if validation.can_publish():
            status = "Ready to build" + (" (warnings only)" if validation.warnings else "")
        else:
            status = f"{len(validation.errors)} error(s) found - build may fail"

        # Print formatted box
        print("┌─────────────────────────────────────────────┐")
        print("│ 📚 TEACHING MODE DETECTED                   │")
        print("├─────────────────────────────────────────────┤")
        print(f"│ Course: {course_name:<37}│")
        print(f"│ Progress: Week {progress['current_week']}/{progress['total_weeks']} ({progress['percent_complete']:.0f}% complete){' ' * (25 - len(f'Week {progress['current_week']}/{progress['total_weeks']} ({progress['percent_complete']:.0f}% complete)'))}│")
        print("│                                             │")
        print("│ 🔍 VALIDATION:                              │")
        for line in val_lines:
            # Pad line to 45 chars
            padded = line + " " * (45 - len(line))
            print(f"│ {padded}│")
        print("│                                             │")
        status_padded = f"Status: {status}" + " " * (45 - len(f"Status: {status}"))
        print(f"│ {status_padded}│")
        print("└─────────────────────────────────────────────┘")
        print()

        # Warn if errors (but don't block)
        if validation.errors:
            print("⚠️  WARNING: Validation found errors. Review them after the build.")
            print()

    except Exception as e:
        # Don't fail the build if teaching context fails
        print(f"Warning: Could not load teaching context: {e}", file=sys.stderr)


def show_teaching_context_after_build(cwd: str = "."):
    """Show teaching context after successful build."""
    try:
        config = load_teach_config(cwd)
        if not config:
            return  # Not teaching mode

        # Get semester progress
        progress = calculate_current_week(config)

        # Get deployment URLs
        deployment = config.get("deployment", {})
        draft_url = deployment.get("draft_url", "")
        production_url = deployment.get("production_url", "")

        # Calculate next milestone
        next_milestone = ""
        if progress["on_break"]:
            next_milestone = f"On {progress['break_name']}"
        else:
            # Find next break
            dates = config.get("dates", {})
            breaks = dates.get("breaks", [])
            if breaks:
                from datetime import datetime
                current = datetime.now().date()
                for brk in breaks:
                    break_start = datetime.fromisoformat(brk["start"]).date()
                    if break_start > current:
                        days_until = (break_start - current).days
                        next_milestone = f"Next: {brk['name']} in {days_until} day{'s' if days_until != 1 else ''}"
                        break

        # Print formatted box
        print()
        print("┌─────────────────────────────────────────────┐")
        print("│ ✅ BUILD COMPLETE                           │")
        print("├─────────────────────────────────────────────┤")

        if draft_url or production_url:
            print("│ 🌐 DEPLOYMENT URLS:                         │")
            if draft_url:
                url_line = f"• Draft: {draft_url}"
                padded = url_line + " " * (45 - len(url_line))
                print(f"│ {padded}│")
            if production_url:
                url_line = f"• Production: {production_url}"
                padded = url_line + " " * (45 - len(url_line))
                print(f"│ {padded}│")
            print("│                                             │")

        print("│ 📊 SEMESTER PROGRESS:                       │")
        progress_line = f"Week {progress['current_week']}/{progress['total_weeks']} · {progress['percent_complete']:.0f}% complete"
        padded = progress_line + " " * (45 - len(progress_line))
        print(f"│ {padded}│")

        if next_milestone:
            padded = next_milestone + " " * (45 - len(next_milestone))
            print(f"│ {padded}│")

        print("│                                             │")
        print("│ 💡 NEXT STEPS:                              │")
        print("│ • Review build output above                 │")
        print("│ • Preview locally: /craft:site:preview      │")
        print("│ • Publish to production: /craft:site:publish│")
        print("│ • Check progress: /craft:site:progress      │")
        print("└─────────────────────────────────────────────┘")
        print()

    except Exception as e:
        # Don't fail if teaching context fails
        print(f"Warning: Could not show teaching context: {e}", file=sys.stderr)


# Main build logic
def main():
    cwd = os.getcwd()

    # Check if teaching mode
    is_teaching, method = detect_teaching_mode(cwd)

    # Show teaching context before build
    if is_teaching:
        show_teaching_context_before_build(cwd)

    # Detect site type and build
    # (existing build logic here - MkDocs, Quarto, pkgdown detection)
    # For now, this is a placeholder
    print("Building site...")

    # Show teaching context after successful build
    if is_teaching:
        show_teaching_context_after_build(cwd)


if __name__ == "__main__":
    main()
```

### Integration Points

1. **Before Build**: Call `show_teaching_context_before_build()` after detecting teaching mode
2. **After Build**: Call `show_teaching_context_after_build()` after successful build
3. **Error Handling**: All teaching-specific code wrapped in try/except to prevent build failures

### Non-Teaching Projects

For non-teaching projects, the command behaves exactly as before with no changes to output or behavior.

## See Also

- `/craft:site:deploy` - Deploy to GitHub Pages
- `/craft:site:check` - Check site for issues
- `/craft:site:progress` - Show semester progress (teaching mode)
- `/craft:site:add` - Add Pages with Navigation Sync
- `/craft:site:audit` - Content Inventory & Audit
- `/craft:site:consolidate` - Merge Duplicate Content
- `/craft:site:create` - Full Documentation Site Wizard
- `/craft:site:nav` - Navigation Reorganization
- `/craft:site:status` - Documentation Site Dashboard
- `/craft:site:theme` - Quick Theme Changes
- Template: `templates/dry-run-pattern.md`
