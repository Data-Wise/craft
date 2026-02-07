# Teaching Configuration Schema

⏱️ **5 minutes** • 🟢 Beginner • ✓ Complete reference

> **TL;DR** (30 seconds)
>
> - **What:** YAML schema for teaching project configuration
> - **Why:** Enables automated course workflows, week tracking, and deployment
> - **Where:** `.flow/teach-config.yml` in your teaching project root
> - **Next:** Copy the [full example](#complete-example) and customize for your course

Teaching projects use `.flow/teach-config.yml` to configure course information, dates, breaks, instructor details, and deployment settings. This enables Craft's teaching commands to provide context-aware automation.

!!! tip "Quick Win: Auto-Week Calculation"
    Set `progress.current_week: auto` and Craft automatically calculates which week you're in based on your semester dates and break schedule - no manual updates needed!

!!! note "Flow-CLI Compatibility"
    If your config uses flow-cli's schema (`semester_info.start_date`, `course.name`, `branches.production`), Craft normalizes it automatically — no changes needed. See [Flow-CLI Config Compatibility](#flow-cli-config-compatibility) below.

## File Location

```
your-teaching-project/
├── .flow/
│   └── teach-config.yml    # Teaching configuration (this file)
├── syllabus/
├── lectures/
└── assignments/
```

## Schema Reference

### Course Information

Basic course metadata displayed across teaching workflows.

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `course.number` | string | ✓ | Course code or number | `"STAT 545"`, `"CS 101"` |
| `course.title` | string | ✓ | Full course title | `"Regression Analysis"` |
| `course.semester` | string | ✓ | Semester name | `"Spring"`, `"Fall"`, `"Winter"`, `"Summer"` |
| `course.year` | integer | ✓ | Four-digit year | `2026` |

**Example:**

```yaml
course:
  number: "STAT 545"
  title: "Regression Analysis"
  semester: "Spring"
  year: 2026
```

### Semester Dates

Define when your semester starts, ends, and breaks occur.

| Field | Type | Required | Description | Format |
|-------|------|----------|-------------|--------|
| `dates.start` | date | ✓ | First day of semester | `YYYY-MM-DD` |
| `dates.end` | date | ✓ | Last day of semester | `YYYY-MM-DD` |
| `dates.breaks` | array | - | Break periods (optional) | See below |

**Break Configuration:**

Each break in `dates.breaks` includes:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `name` | string | ✓ | Break name | `"Spring Break"`, `"MLK Day"` |
| `start` | date | ✓ | First day of break | `2026-03-16` |
| `end` | date | ✓ | Last day of break (can equal start for single-day breaks) | `2026-03-20` |

Single-day breaks (where `start == end`) are valid for holidays like MLK Day or Veterans Day.

**Example:**

```yaml
dates:
  start: "2026-01-19"
  end: "2026-05-08"
  breaks:
    - name: "MLK Day"
      start: "2026-01-20"
      end: "2026-01-20"        # Single-day break (start == end)
    - name: "Spring Break"
      start: "2026-03-16"
      end: "2026-03-20"
    - name: "Reading Week"
      start: "2026-04-13"
      end: "2026-04-14"
```

### Instructor Information

Optional instructor contact details for syllabus generation and student communication.

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `instructor.name` | string | - | Full name | `"Dr. Jane Smith"` |
| `instructor.email` | string | - | Contact email | `"jsmith@university.edu"` |
| `instructor.office_hours` | string | - | Office hours description | `"Tu/Th 2-3pm, Zoom"` |

**Example:**

```yaml
instructor:
  name: "Dr. Jane Smith"
  email: "jsmith@university.edu"
  office_hours: "Tuesday/Thursday 2-3pm, Zoom link on Canvas"
```

### Deployment Configuration

Controls how your course site is built and published.

| Field | Type | Required | Description | Default |
|-------|------|----------|-------------|---------|
| `deployment.production_branch` | string | - | Branch for published site | `"production"` |
| `deployment.draft_branch` | string | - | Branch for draft content | `"draft"` |
| `deployment.gh_pages_url` | string | - | GitHub Pages URL | - |

**Example:**

```yaml
deployment:
  production_branch: "production"
  draft_branch: "draft"
  gh_pages_url: "https://username.github.io/stat-545"
```

**How it works:**

- **Draft branch**: Work-in-progress content, visible to instructors only
- **Production branch**: Published content, visible to students
- **GitHub Pages**: Automatically deploys from production branch

### Progress Tracking

Track which week of the semester you're currently in.

| Field | Type | Required | Description | Options |
|-------|------|----------|-------------|---------|
| `progress.current_week` | string/integer | - | Current week number | `"auto"` or `1-16` |

**Automatic calculation (`auto`)**:

- Calculates week based on today's date
- Accounts for semester start/end dates
- Skips weeks with breaks
- Recommended for most courses

**Manual override (integer)**:

- Set specific week number (1-16)
- Useful for:
  - Testing future weeks
  - Non-standard schedules
  - Review weeks

**Example:**

```yaml
progress:
  current_week: auto  # Let Craft calculate based on dates

# Or manual override:
progress:
  current_week: 8     # Force week 8 (for testing/review)
```

**How automatic calculation works:**

1. Count weeks from `dates.start` to today
2. Skip any weeks that fall within `dates.breaks`
3. Cap at semester length (weeks between `start` and `end`)

### Validation Rules

Optional validation settings for quality control.

| Field | Type | Required | Description | Default |
|-------|------|----------|-------------|---------|
| `validation.required_sections` | array | - | Syllabus sections that must exist | `["grading", "policies", "objectives", "schedule"]` |
| `validation.strict_mode` | boolean | - | Errors block publishing | `true` |

**Strict Mode Behavior:**

| Mode | Missing Sections | Broken Links | Stale Content | Action |
|------|------------------|--------------|---------------|--------|
| `true` | ❌ Block | ❌ Block | ⚠️ Warn | Prevent publish |
| `false` | ⚠️ Warn | ⚠️ Warn | ⚠️ Warn | Allow publish |

**Example:**

```yaml
validation:
  required_sections:
    - grading
    - policies
    - objectives
    - schedule
    - textbook
    - accommodations
  strict_mode: true
```

## Complete Example

Full configuration for a typical Spring semester course:

```yaml
# .flow/teach-config.yml - STAT 545 Spring 2026

# ============================================================================
# Course Information
# ============================================================================
course:
  number: "STAT 545"
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

  # Break periods (Spring Break + Reading Week)
  breaks:
    - name: "Spring Break"
      start: "2026-03-16"
      end: "2026-03-20"

    - name: "Reading Week"
      start: "2026-04-13"
      end: "2026-04-14"

# ============================================================================
# Instructor Information (optional)
# ============================================================================
instructor:
  name: "Dr. Jane Smith"
  email: "jsmith@university.edu"
  office_hours: "Tuesday/Thursday 2-3pm, Zoom link on Canvas"

# ============================================================================
# Deployment Configuration (optional)
# ============================================================================
deployment:
  production_branch: "production"  # Students see this
  draft_branch: "draft"            # Instructors see this
  gh_pages_url: "https://jsmith.github.io/stat-545"

# ============================================================================
# Progress Tracking (optional)
# ============================================================================
progress:
  # Options:
  #   - "auto": Calculate based on dates and breaks (recommended)
  #   - 1-16: Manual override for specific week number
  current_week: auto

# ============================================================================
# Validation Rules (optional)
# ============================================================================
validation:
  # Sections that must exist in syllabus
  required_sections:
    - grading
    - policies
    - objectives
    - schedule

  # Strict mode: true = errors block publishing, false = warnings only
  strict_mode: true
```

## Usage Examples

### Example 1: Spring Semester with Spring Break

Typical 16-week Spring semester:

```yaml
course:
  number: "CS 240"
  title: "Data Structures"
  semester: "Spring"
  year: 2026

dates:
  start: "2026-01-12"
  end: "2026-05-01"
  breaks:
    - name: "Spring Break"
      start: "2026-03-09"
      end: "2026-03-13"

progress:
  current_week: auto
```

**Timeline:**

- Weeks 1-8: Jan 12 - Mar 6
- Spring Break: Mar 9-13 (skipped)
- Weeks 9-16: Mar 16 - May 1

### Example 2: Fall Semester with Thanksgiving

Fall semester with Thanksgiving break:

```yaml
course:
  number: "MATH 301"
  title: "Probability Theory"
  semester: "Fall"
  year: 2025

dates:
  start: "2025-08-25"
  end: "2025-12-12"
  breaks:
    - name: "Thanksgiving Break"
      start: "2025-11-24"
      end: "2025-11-28"

progress:
  current_week: auto
```

### Example 3: Summer Session (No Breaks)

Compressed 8-week summer session:

```yaml
course:
  number: "STAT 101"
  title: "Intro to Statistics"
  semester: "Summer"
  year: 2026

dates:
  start: "2026-06-01"
  end: "2026-07-24"
  # No breaks in summer session

progress:
  current_week: auto
```

### Example 4: Multi-Break Semester

Complex schedule with multiple breaks:

```yaml
course:
  number: "ECON 405"
  title: "Econometrics"
  semester: "Fall"
  year: 2025

dates:
  start: "2025-09-02"
  end: "2025-12-15"
  breaks:
    - name: "Fall Break"
      start: "2025-10-12"
      end: "2025-10-13"

    - name: "Thanksgiving"
      start: "2025-11-25"
      end: "2025-11-29"

    - name: "Reading Days"
      start: "2025-12-08"
      end: "2025-12-09"

progress:
  current_week: auto
```

## How Commands Use This Config

Teaching commands read `.flow/teach-config.yml` to provide context-aware automation:

| Command | Uses | Example |
|---------|------|---------|
| `/craft:teach:week` | `progress.current_week`, `dates` | Show current week info |
| `/craft:teach:status` | All fields | Teaching dashboard |
| `/craft:teach:publish` | `deployment`, `validation` | Publish to production |
| `/craft:teach:syllabus` | `course`, `instructor`, `dates` | Generate syllabus |
| `/craft:teach:schedule` | `dates`, `breaks` | Create semester calendar |

## Validation

### Validate Your Configuration

Use `/craft:teach:config` to validate your configuration:

```bash
/craft:teach:config validate
```

**Checks:**

- ✓ Required fields present
- ✓ Date formats correct (YYYY-MM-DD)
- ✓ Dates in logical order (start < end)
- ✓ Breaks fall within semester dates
- ✓ Semester/year combination valid
- ✓ Week calculation works correctly

**Example output:**

```
✓ Configuration valid
✓ Semester: Spring 2026 (16 weeks)
✓ Current week: 8 (auto-calculated)
✓ Breaks: 2 configured
  - Spring Break (5 days)
  - Reading Week (2 days)
```

### Common Validation Errors

| Error | Fix |
|-------|-----|
| Missing required field | Add `course.number`, `course.title`, etc. (or use flow-cli equivalents: `course.name`, `course.full_name`) |
| Invalid date format | Use `YYYY-MM-DD` format |
| Break outside semester | Adjust break dates to fall within `start`/`end` |
| Break start after end | Swap break `start` and `end` dates (single-day breaks where `start == end` are valid) |
| End before start | Swap semester `start` and `end` dates |
| Invalid semester | Use `"Spring"`, `"Fall"`, `"Winter"`, or `"Summer"` (lowercase auto-capitalized) |
| Invalid current_week | Use `"auto"` or integer 1-16 |

## Tips and Best Practices

!!! success "Recommended Settings"
    - Use `progress.current_week: auto` for automatic tracking
    - Set `validation.strict_mode: true` to catch errors early
    - Include all breaks (even 1-2 day breaks) for accurate week calculation
    - Use descriptive break names (`"Spring Break"` not `"Break 1"`)

!!! warning "Common Pitfalls"
    - Forgetting to update year when copying from previous semester
    - Break dates that don't account for weekends
    - Missing `deployment.gh_pages_url` prevents publish command from working
    - Setting `current_week` manually and forgetting to update it

!!! tip "Pro Tips"
    - **Test future weeks**: Temporarily set `current_week: 15` to preview end-of-semester content
    - **Multiple instructors**: Use `instructor.name: "Dr. Smith & Dr. Jones"` for co-taught courses
    - **Non-standard schedules**: Manual `current_week` override handles exam weeks, review sessions
    - **Version control**: Commit `.flow/teach-config.yml` - it's your course's source of truth

## Flow-CLI Config Compatibility

If your project uses [flow-cli](https://github.com/Data-Wise/flow-cli)'s `teach-config.yml` schema, Craft normalizes it automatically via `_normalize_config()` in `teach_config.py`. No migration needed — both schemas work transparently.

### Field Mappings

| Flow-CLI Schema | Craft-Native Schema | Behavior |
|-----------------|---------------------|----------|
| `course.name` | `course.number` | Mapped if `number` absent |
| `course.full_name` | `course.title` | Mapped if `title` absent |
| `course.semester: "spring"` | `course.semester: "Spring"` | Auto-capitalized |
| `semester_info.start_date` | `dates.start` | Mapped if `dates.start` absent |
| `semester_info.end_date` | `dates.end` | Mapped if `dates.end` absent |
| `semester_info.breaks` | `dates.breaks` | Mapped if `dates.breaks` absent |
| `branches.production` | `deployment.production_branch` | Mapped if `production_branch` absent |
| `branches.draft` | `deployment.draft_branch` | Mapped if `draft_branch` absent |

### Design Principles

- **Non-destructive**: Craft-native keys always win (never overwritten)
- **Silent**: No warnings or migration prompts
- **Idempotent**: Safe to normalize multiple times
- **Gap-filling**: Only adds missing fields, original keys preserved

### Example: Flow-CLI Config That Works in Craft

```yaml
# This flow-cli config works in Craft without changes
course:
  name: "STAT 545"                    # -> course.number
  full_name: "STAT 545 - ANOVA"      # -> course.title
  semester: "spring"                  # -> "Spring" (capitalized)
  year: 2026

semester_info:
  start_date: "2026-01-19"           # -> dates.start
  end_date: "2026-05-16"             # -> dates.end
  breaks:
    - name: "MLK Day"
      start: "2026-01-20"
      end: "2026-01-20"              # Single-day break OK
    - name: "Spring Break"
      start: "2026-03-15"
      end: "2026-03-22"

branches:
  production: "production"            # -> deployment.production_branch
  draft: "draft"                      # -> deployment.draft_branch
```

## Schema Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-02-06 | Flow-CLI config normalization, single-day breaks support |
| 1.0 | 2026-01-16 | Initial schema for teaching workflow |

## See Also

- **`/craft:site:publish`** - Publish teaching site with preview workflow
- **`utils/detect_teaching_mode.py`** - Teaching mode detection utility
- **`commands/utils/teaching_validation.py`** - Content validation utility
- **[Configuration Reference](reference/configuration.md)** - General Craft config
