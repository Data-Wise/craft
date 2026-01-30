---
description: Create CLAUDE.md from project-type template with auto-population
category: docs
arguments:
  - name: type
    description: "Template type: plugin, teaching, r-package (auto-detected if not specified)"
    required: false
  - name: force
    description: Overwrite existing CLAUDE.md
    required: false
    default: false
    alias: -f
  - name: dry-run
    description: Preview template without creating file
    required: false
    default: false
    alias: -n
tags: [documentation, claude-md, scaffolding, templates]
version: 1.0.0
---

# /craft:docs:claude-md:scaffold - Create CLAUDE.md from Template

Generate a new CLAUDE.md file tailored to your project type with auto-populated values from project analysis.

**This command follows the "Show Steps First" pattern** - it always previews the generated content before creating the file.

## What It Does

1. Detects project type (craft plugin, teaching site, R package)
2. Scans project structure for metadata
3. Populates template with discovered values
4. Shows preview of generated CLAUDE.md
5. Creates file after confirmation

## Show Steps First Pattern

This command ALWAYS shows a preview before creating files.

### Step 1: Detect Project Type

```
Project Type Detection

Directory: /Users/dt/projects/dev-tools/craft
Analyzing project structure...

Detected indicators:
  ✓ .claude-plugin/plugin.json exists
  ✓ commands/ directory (100 commands)
  ✓ skills/ directory (21 skills)
  ✓ agents/ directory (8 agents)
  ✓ tests/ directory

Project type: Craft Plugin
Template: plugin-template.md

Proceed with detection? [y/n]
```

### Step 2: Gather Project Metadata

```
Scanning Project Metadata

From .claude-plugin/plugin.json:
  name: craft
  version: 2.9.0
  description: Development workflow orchestration

From filesystem:
  commands: 100
  skills: 21
  agents: 8
  tests: 847

From git:
  repository: https://github.com/Data-Wise/craft
  branch: main

Estimated template population: 85%

Continue to template generation? [y/n]
```

### Step 3: Preview Generated Template

```
Generated CLAUDE.md Preview
─────────────────────────────────────────

# CLAUDE.md - craft

> **TL;DR**: Development workflow orchestration plugin

**100 commands** · **21 skills** · **8 agents**
**Current Version:** v2.9.0
**Tests:** 847 passing

## Quick Commands

| Task | Command |
|------|---------|
| Run tests | `/craft:test:run` |
| Validate | `/craft:check` |
| Build docs | `/craft:docs:update` |

[... 67 more lines ...]

─────────────────────────────────────────
Lines: 329
Template variables populated: 18/20 (90%)

Create this file? [y/n/edit/preview-full]
```

### Step 4: User Decision

Options after preview:

- **y** - Create file with preview content
- **n** - Cancel without creating
- **edit** - Modify template before creating
- **preview-full** - Show complete generated content

### Step 5: Create and Confirm

```
✅ CLAUDE.md Created

File: /Users/dt/projects/dev-tools/craft/CLAUDE.md
Lines: 329
Template: plugin-template.md
Variables populated: 18/20 (90%)

Unpopulated variables (manual editing needed):
  - tagline (line 3)
  - docs_percent (line 7)

Next steps:
  1. Review: open CLAUDE.md
  2. Edit unpopulated: /craft:docs:claude-md:edit
  3. Validate: /craft:docs:claude-md:audit
  4. Commit: git add CLAUDE.md
```

## Available Templates

| Type | Detection | Auto-populated Fields |
|------|-----------|----------------------|
| **plugin** | .claude-plugin/plugin.json | name, version, command_count, skill_count, agent_count, test_count, repo_url |
| **teaching** | _quarto.yml + course.yml | course_name, course_code, semester, week_count, assignment_count |
| **r-package** | DESCRIPTION + Package: | package_name, version, title, r_version, functions, dependencies |

## Template Variable Substitution

Templates use `{variable_name}` syntax for auto-population:

```markdown
# CLAUDE.md - {plugin_name}

**Current Version:** v{version}
**{command_count} commands** · **{skill_count} skills**
```

### Plugin Template Variables

| Variable | Source | Example |
|----------|--------|---------|
| `plugin_name` | plugin.json → name | "craft" |
| `version` | plugin.json → version | "2.9.0" |
| `command_count` | commands/ directory scan | 100 |
| `skill_count` | skills/ directory scan | 21 |
| `agent_count` | agents/ directory scan | 8 |
| `test_count` | tests/ count passing | 847 |
| `docs_url` | plugin.json → repository.docs | "https://..." |
| `repo_url` | plugin.json → repository.url | "https://..." |
| `command_table` | Generated from commands/ | "\| Task \| Cmd \|" |
| `command_dirs` | Directory tree | "├── docs/" |

### Teaching Template Variables

| Variable | Source | Example |
|----------|--------|---------|
| `course_name` | _quarto.yml → title | "Regression Analysis" |
| `course_code` | course.yml → code | "STAT 440" |
| `semester` | course.yml → semester | "Spring 2026" |
| `week_count` | weeks/ directory scan | 15 |
| `assignment_count` | assignments/ scan | 8 |
| `exam_count` | exams/ scan | 3 |

### R Package Template Variables

| Variable | Source | Example |
|----------|--------|---------|
| `package_name` | DESCRIPTION → Package | "medci" |
| `version` | DESCRIPTION → Version | "0.2.0" |
| `package_title` | DESCRIPTION → Title | "Confidence Intervals" |
| `r_version` | DESCRIPTION → Depends | "4.1.0" |
| `function_count` | R/ directory scan | 24 |

## Force Overwrite

If CLAUDE.md exists:

```
⚠️ CLAUDE.md Already Exists

File: /Users/dt/projects/dev-tools/craft/CLAUDE.md
Lines: 329
Last modified: 2 days ago

Options:
  [1] Cancel (default)
  [2] Overwrite completely (--force)
  [3] Preview diff first

Or use: /craft:docs:claude-md:scaffold --force
```

## Dry-Run Mode

Preview template without creating file:

```bash
/craft:docs:claude-md:scaffold --dry-run
```

Output:

```
Dry-Run Mode (No files will be created)

Project type: Craft Plugin
Template: plugin-template.md

Generated content preview:
─────────────────────────────────────────
[... full template output ...]
─────────────────────────────────────────

To create this file:
  /craft:docs:claude-md:scaffold
```

## Manual Type Override

Auto-detection can be overridden:

```bash
# Force teaching template
/craft:docs:claude-md:scaffold --type teaching

# Force plugin template
/craft:docs:claude-md:scaffold --type plugin

# Force R package template
/craft:docs:claude-md:scaffold --type r-package
```

## Detection Priority

If multiple project types detected:

```
Multiple Project Types Detected

Found indicators for:
  1. Craft Plugin (.claude-plugin/plugin.json) [confidence: 95%]
  2. R Package (DESCRIPTION) [confidence: 70%]

Select template:
  [1] plugin (recommended)
  [2] r-package
  [auto] Use highest confidence (1)

Or specify: /craft:docs:claude-md:scaffold --type plugin
```

## Integration

### After Scaffolding

Recommended next steps:

1. **Edit unpopulated variables**:

   ```bash
   /craft:docs:claude-md:edit
   ```

2. **Validate completeness**:

   ```bash
   /craft:docs:claude-md:audit
   ```

3. **Fix any issues**:

   ```bash
   /craft:docs:claude-md:fix
   ```

4. **Commit**:

   ```bash
   git add CLAUDE.md
   git commit -m "docs: scaffold CLAUDE.md from template"
   ```

### With Git Worktree

When creating new worktree, scaffold auto-runs if no CLAUDE.md:

```bash
/craft:git:worktree feature/new-feature
# Detects no CLAUDE.md in worktree
# Offers: "Scaffold CLAUDE.md? [y/n]"
```

## Error Handling

### No Project Type Detected

```
⚠️ Unable to Detect Project Type

Could not find indicators for:
  - Craft Plugin (.claude-plugin/plugin.json)
  - Teaching Site (_quarto.yml)
  - R Package (DESCRIPTION)

Options:
  [1] Use generic template
  [2] Specify type: --type [plugin|teaching|r-package]
  [3] Cancel

Recommendation: Use generic template with manual editing
```

### Missing Template

```
⚠️ Template Not Found

Template path: templates/claude-md/plugin-template.md
Status: File does not exist

This may be a craft plugin installation issue.

Fix:
  1. Reinstall craft plugin
  2. Or use generic template: --type generic
```

## Related Commands

| Command | Purpose |
|---------|---------|
| `/craft:docs:claude-md:edit` | Edit sections after scaffolding |
| `/craft:docs:claude-md:update` | Update existing CLAUDE.md |
| `/craft:docs:claude-md:audit` | Validate generated file |
| `/craft:docs:claude-md:fix` | Auto-fix issues |

## Examples

### Example 1: Scaffold for Craft Plugin

```bash
cd ~/projects/dev-tools/my-plugin
/craft:docs:claude-md:scaffold
# Detects plugin type
# Shows preview
# Creates CLAUDE.md
```

### Example 2: Scaffold for Teaching Site

```bash
cd ~/teaching/stat-440
/craft:docs:claude-md:scaffold
# Detects Quarto + course.yml
# Populates course metadata
# Creates CLAUDE.md
```

### Example 3: Force Overwrite

```bash
/craft:docs:claude-md:scaffold --force
# Overwrites existing CLAUDE.md
# Shows preview first
# Asks for confirmation
```

### Example 4: Dry-Run Preview

```bash
/craft:docs:claude-md:scaffold --dry-run
# Shows what would be created
# No files modified
# Exit without creating
```

## Template Customization

Templates located in: `templates/claude-md/`

To customize:

1. Copy template to project: `cp templates/claude-md/plugin-template.md .claude-md-template.md`
2. Edit `.claude-md-template.md`
3. Scaffold will use local template if found

## Success Criteria

After scaffolding, verify:

- [ ] File created with correct template
- [ ] 80%+ variables auto-populated
- [ ] No syntax errors
- [ ] Audit passes: `/craft:docs:claude-md:audit`

## Technical Notes

**Implementation**:

- Uses `utils/claude_md_detector.py` for project detection
- Templates in `templates/claude-md/` directory
- Variable substitution via Python string formatting
- Preview always shown before file creation

**Performance**:

- Project detection: < 1 second
- Template population: < 2 seconds
- Total time: 3-5 seconds

**Template Format**:

- Markdown with `{variable}` placeholders
- Variables populated from project analysis
- Unpopulated variables left as `{variable}` for manual editing
