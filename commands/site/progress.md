---
description: Display comprehensive semester progress dashboard
category: site
arguments:
  - name: week
    description: Override current week (manual)
    required: false
    alias: -w
  - name: json
    description: Output JSON for scripting
    required: false
    default: false
deprecated: true
replaced-by: "skills/docs/site-management/"
---

# /craft:site:progress - Semester Progress Dashboard

You are an ADHD-friendly semester progress dashboard generator. Display a comprehensive, visually structured overview of semester progress for teaching projects.

## Purpose

**At a glance, show:**

- Current week and semester progress
- Visual progress bar
- Upcoming milestones
- Next break countdown
- Week status and activities

## When Invoked

### Step 1: Detect Teaching Mode

Use the teaching mode detection utility:

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.detect_teaching_mode import detect_teaching_mode

is_teaching, method = detect_teaching_mode()

if not is_teaching:
    print("This project is not in teaching mode.")
    print("\nTo enable teaching mode, create .flow/teach-config.yml")
    print("Run /craft:site:init to set up teaching configuration.")
    sys.exit(1)
```

### Step 2: Load Teaching Configuration

```python
from commands.utils.teach_config import load_teach_config

try:
    config = load_teach_config()
    if not config:
        print("Error: teach-config.yml not found.")
        print("\nRun /craft:site:init to create configuration file.")
        sys.exit(1)
except ValueError as e:
    print(f"Error: Invalid configuration\n{e}")
    sys.exit(1)
```

### Step 3: Calculate Progress

```python
from commands.utils.semester_progress import (
    calculate_current_week,
    format_date_range,
    is_on_break
)
from datetime import datetime

# Check for manual week override
manual_week = None
if args.week:
    try:
        manual_week = int(args.week)
        # Update config with manual override
        config['progress']['current_week'] = manual_week
    except ValueError:
        print(f"Error: --week must be an integer (got '{args.week}')")
        sys.exit(1)

# Calculate progress
progress = calculate_current_week(config)

# Extract info
current_week = progress['current_week']
total_weeks = progress['total_weeks']
percent = progress['percent_complete']
on_break = progress['on_break']
break_name = progress.get('break_name')
week_range = format_date_range(progress['week_start'], progress['week_end'])
```

### Step 4: Format Dashboard

#### JSON Output (`--json` flag)

```python
if args.json:
    import json

    output = {
        "course": {
            "number": config['course']['number'],
            "title": config['course']['title']
        },
        "semester": {
            "name": config['course']['semester'],
            "year": config['course']['year']
        },
        "progress": {
            "current_week": current_week,
            "total_weeks": total_weeks,
            "percent_complete": round(percent, 2),
            "on_break": on_break,
            "week_range": week_range
        },
        "upcoming": [],  # Populated below
        "next_break": None  # Populated below
    }

    # Add upcoming milestones (parse from schedule.qmd if exists)
    # This is optional - simplified version just shows breaks

    # Find next break
    breaks = config['dates'].get('breaks', [])
    current_date = datetime.now().date()
    for brk in breaks:
        from datetime import datetime as dt
        break_start = dt.fromisoformat(brk['start']).date()
        if break_start > current_date:
            days_until = (break_start - current_date).days
            output['next_break'] = {
                "name": brk['name'],
                "days_until": days_until
            }
            break

    print(json.dumps(output, indent=2))
    sys.exit(0)
```

#### ADHD-Friendly Dashboard (Default)

```python
# Build visual progress bar
bar_width = 16
filled = int((current_week / total_weeks) * bar_width) if total_weeks > 0 else 0
empty = bar_width - filled
progress_bar = "▓" * filled + "░" * empty

# Course header
course_num = config['course']['number']
course_title = config['course']['title']
semester = config['course']['semester']
year = config['course']['year']

print("┌─────────────────────────────────────────────────────────┐")
print(f"│ 📚 {course_num}: {course_title[:40].ljust(40)} │")
print(f"│ {semester} {year} · Week {current_week} of {total_weeks} ({int(percent)}% complete)".ljust(60) + "│")
print("├─────────────────────────────────────────────────────────┤")
print("│                                                         │")

# Current week status
if on_break and break_name:
    print(f"│ 🏖️  CURRENT STATUS: {break_name}".ljust(60) + "│")
    print(f"│ Date Range: {week_range}".ljust(60) + "│")
else:
    print(f"│ 📅 CURRENT WEEK: Week {current_week}".ljust(60) + "│")
    print(f"│ Date Range: {week_range}".ljust(60) + "│")

print("│                                                         │")

# Progress bar
print(f"│ 📊 PROGRESS:".ljust(60) + "│")
print(f"│ {progress_bar} {int(percent)}% complete".ljust(60) + "│")
print("│                                                         │")
```

### Step 5: Show Upcoming Milestones (Optional)

```python
# Parse schedule.qmd for upcoming items (if exists)
import os
schedule_path = os.path.join(os.getcwd(), "schedule.qmd")

if os.path.exists(schedule_path):
    print("│ 📌 UPCOMING MILESTONES:".ljust(60) + "│")

    # Simple parsing - look for assignment due dates in next 3 weeks
    # This is a simplified version - full implementation would parse Quarto properly

    # For now, just show next break if available
    breaks = config['dates'].get('breaks', [])
    current_date = datetime.now().date()

    upcoming_shown = False
    for brk in breaks:
        break_start = datetime.fromisoformat(brk['start']).date()
        break_end = datetime.fromisoformat(brk['end']).date()
        if break_start > current_date:
            days_until = (break_start - current_date).days
            date_str = format_date_range(brk['start'], brk['end'])
            print(f"│ • {brk['name']}: {date_str} ({days_until} days)".ljust(60) + "│")
            upcoming_shown = True
            break  # Only show next break

    if not upcoming_shown:
        print("│ • No upcoming breaks scheduled".ljust(60) + "│")

    print("│                                                         │")
```

### Step 6: Show Next Break Countdown

```python
# Find next break
breaks = config['dates'].get('breaks', [])
current_date = datetime.now().date()

next_break_found = False
for brk in breaks:
    break_start = datetime.fromisoformat(brk['start']).date()
    if break_start > current_date:
        days_until = (break_start - current_date).days
        print(f"│ ⏰ NEXT BREAK: {brk['name']} in {days_until} days".ljust(60) + "│")
        next_break_found = True
        break

if not next_break_found:
    print("│ ⏰ NEXT BREAK: No breaks scheduled".ljust(60) + "│")

print("│                                                         │")
print("└─────────────────────────────────────────────────────────┘")
```

### Step 7: Show Manual Override Notice

```python
if manual_week:
    print("\n⚠️  Manual week override active (--week flag)")
    print(f"   Current week set to: {manual_week}")
```

## Complete Example Output

```
┌─────────────────────────────────────────────────────────┐
│ 📚 STAT 545: Data Science                               │
│ Spring 2026 · Week 5 of 16 (31% complete)               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 📅 CURRENT WEEK: Week 5                                 │
│ Date Range: Feb 24-Mar 2                                │
│                                                         │
│ 📊 PROGRESS:                                            │
│ ▓▓▓▓▓░░░░░░░░░░░ 31% complete                          │
│                                                         │
│ 📌 UPCOMING MILESTONES:                                 │
│ • Spring Break: Mar 20-27 (18 days)                     │
│                                                         │
│ ⏰ NEXT BREAK: Spring Break in 18 days                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Break Display Format

When on break:

```
┌─────────────────────────────────────────────────────────┐
│ 📚 STAT 545: Data Science                               │
│ Spring 2026 · Week 5 of 16 (31% complete)               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 🏖️  CURRENT STATUS: Spring Break                        │
│ Date Range: Mar 20-27                                   │
│                                                         │
│ 📊 PROGRESS:                                            │
│ ▓▓▓▓▓░░░░░░░░░░░ 31% complete                          │
│                                                         │
│ 📌 UPCOMING MILESTONES:                                 │
│ • No upcoming breaks scheduled                          │
│                                                         │
│ ⏰ NEXT BREAK: No breaks scheduled                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Error Handling

### Not in Teaching Mode

```
This project is not in teaching mode.

To enable teaching mode, create .flow/teach-config.yml
Run /craft:site:init to set up teaching configuration.
```

### Config Not Found

```
Error: teach-config.yml not found.

Run /craft:site:init to create configuration file.
```

### Invalid Config

```
Error: Invalid configuration
  - Missing required field: 'course.number'
  - Invalid date format: 'dates.start' (expected YYYY-MM-DD)

Fix these issues in .flow/teach-config.yml and try again.
```

### Invalid Week Override

```
Error: --week must be an integer (got 'five')
```

## Troubleshooting

### Week Calculation Issues

**Problem:** Current week is wrong

**Solution:**

1. Verify `dates.start` is correct in config
2. Check that breaks are properly defined
3. Ensure dates don't overlap
4. Use `--week` for manual override

**Example:**

```bash
# Test specific week
/craft:site:progress --week 8

# Compare with auto-calculation
/craft:site:progress
```

### JSON Output for Scripting

Use `--json` flag for programmatic access:

```bash
/craft:site:progress --json > progress.json
```

**Output schema:**

```json
{
  "course": {"number": "STAT 440", "title": "..."},
  "semester": {"name": "Spring", "year": 2026},
  "progress": {
    "current_week": 5,
    "total_weeks": 16,
    "percent_complete": 31.25,
    "on_break": false,
    "week_range": "Feb 24-Mar 2"
  },
  "next_break": {
    "name": "Spring Break",
    "days_until": 18
  }
}
```

## Integration

**Related commands:**

- `/craft:site:validate` - Validate course content before publishing
- `/craft:site:publish` - Deploy content to production
- `/craft:site:build` - Build site with teaching context
- `/craft:site:add` - Add Pages with Navigation Sync
- `/craft:site:audit` - Content Inventory & Audit
- `/craft:site:check` - Validate documentation site for broken links
- `/craft:site:consolidate` - Merge Duplicate Content
- `/craft:site:create` - Full Documentation Site Wizard
- `/craft:site:deploy` - Deploy documentation site to GitHub Pages
- `/craft:site:nav` - Navigation Reorganization
- `/craft:site:status` - Documentation Site Dashboard
- `/craft:site:theme` - Quick Theme Changes

**Use cases:**

- Weekly check-in on semester progress
- Planning upcoming content
- Status updates in meetings
- Scripting with `--json` output
- Dashboard widgets (parse JSON)

## ADHD-Friendly Features

1. **Visual hierarchy** - Box structure with clear sections
2. **Progress bar** - Visual representation of completion
3. **Icon usage** - Quick visual parsing (📚, 📅, 📊, 📌, ⏰, 🏖️)
4. **Scannable layout** - Key info stands out
5. **Compact display** - All info in one screen
6. **No jargon** - Plain language throughout

## Implementation Notes

**Dependencies:**

- `utils/detect_teaching_mode.py` - Teaching mode detection
- `commands/utils/teach_config.py` - Config parser
- `commands/utils/semester_progress.py` - Progress calculation

**Exit codes:**

- `0` - Success
- `1` - Not in teaching mode or config error
- `2` - Invalid arguments

**Performance:**

- Target: < 200ms for dashboard generation
- Config loading: < 50ms
- Progress calculation: < 100ms

## Future Enhancements (Not v1.0)

- Parse schedule.qmd for assignment due dates
- Show lecture completion status
- Integration with LMS (Canvas, Moodle)
- Export progress to CSV/Excel
- Weekly email digest option
