---
description: Create CLAUDE.md from lean project-type template with auto-population
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
  - name: global
    description: Target ~/.claude/CLAUDE.md instead of project
    required: false
    default: false
    alias: -g
tags: [documentation, claude-md, scaffolding, templates]
version: 2.0.0
---

# /craft:docs:claude-md:init - Create Lean CLAUDE.md

Generate a new CLAUDE.md file tailored to your project type with auto-populated values. Enforces < 150 line budget using lean templates and pointer architecture.

**This command follows the "Show Steps First" pattern** - it always previews the generated content before creating the file.

## What It Does

1. Detects project type (craft plugin, teaching site, R package)
2. Scans project structure for metadata
3. Populates lean template with discovered values (< 150 lines)
4. Shows preview of generated CLAUDE.md
5. Creates file after confirmation
6. Runs post-creation audit to validate

## --global Flag

When `--global` is passed, targets `~/.claude/CLAUDE.md` instead of the project-local file.

```python
import os
from pathlib import Path

if "--global" in args or "-g" in args:
    target_path = Path.home() / ".claude" / "CLAUDE.md"
    project_root = Path.home() / ".claude"
else:
    target_path = Path.cwd() / "CLAUDE.md"
    project_root = Path.cwd()
```

## Show Steps First Pattern

This command ALWAYS shows a preview before creating files.

### Step 1: Detect Project Type

```
Project Type Detection

Directory: $(pwd)
Analyzing project structure...

Detected indicators:
  ✓ .claude-plugin/plugin.json exists
  ✓ commands/ directory (108 commands)
  ✓ skills/ directory (25 skills)
  ✓ agents/ directory (8 agents)

Project type: Craft Plugin
Template: lean-plugin-template (< 150 lines)

Proceed with detection? [y/n]
```

### Step 2: Gather Project Metadata

```
Scanning Project Metadata

From .claude-plugin/plugin.json:
  name: craft
  version: 2.12.0

From filesystem:
  commands: 108
  skills: 21
  agents: 8
  tests: 1432

From git:
  repository: https://github.com/Data-Wise/craft
  branch: main

Estimated template population: 90%
Budget: 150 lines

Continue to template generation? [y/n]
```

### Step 3: Preview Generated Template

```
Generated CLAUDE.md Preview
─────────────────────────────────────────

# CLAUDE.md - craft

> **TL;DR**: Development workflow orchestration plugin

**108 commands** · **25 skills** · **8 agents**
**Version:** v2.16.0 | **Tests:** 1432 passing

## Git Workflow
[...]

## Quick Commands
[...]

## References
-> Release history: [VERSION-HISTORY.md](docs/VERSION-HISTORY.md)
-> Architecture: [ARCHITECTURE.md](docs/ARCHITECTURE.md)
-> Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
-> Command reference: [COMMANDS.md](docs/COMMANDS.md)

─────────────────────────────────────────
Lines: 127 (budget: 150) ✅
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

File: $(pwd)/CLAUDE.md
Lines: 127 (budget: 150 ✅)
Template: lean-plugin-template
Variables populated: 18/20 (90%)

Unpopulated variables (manual editing needed):
  - tagline (line 3)

Next steps:
  1. Edit unpopulated: /craft:docs:claude-md:edit
  2. Validate: /craft:docs:claude-md:sync
  3. Commit: git add CLAUDE.md
```

## Lean Template Design

Templates enforce < 150 line budget with pointer architecture:

### Pointer Lines (Bottom of Template)

Every template ends with a References section containing pointers to detail files:

```markdown
## References

-> Release history: [VERSION-HISTORY.md](docs/VERSION-HISTORY.md)
-> Architecture: [ARCHITECTURE.md](docs/ARCHITECTURE.md)
-> Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
-> Command reference: [COMMANDS.md](docs/COMMANDS.md)
```

### Section Priority

Templates only include P0 sections (always present):

| Section | Lines | Content |
|---------|-------|---------|
| Header/TL;DR | 5 | Name, version, one-liner, key stats |
| Git Workflow | 15 | Branch strategy, commit conventions |
| Quick Commands | 15 | Daily-use commands table |
| Project Structure | 15 | Directory layout |
| Key Files | 15 | Most-referenced files |
| Troubleshooting | 10 | Top issues and fixes |
| References/Pointers | 10 | Links to detail files |

P1 sections (agents, execution modes) are included only if under budget.
P2 sections (release history, feature matrices) are never included in templates.

## Available Templates

| Type | Detection | Auto-populated Fields | Target Lines |
|------|-----------|----------------------|--------------|
| **plugin** | .claude-plugin/plugin.json | name, version, counts, repo_url | ~120 |
| **teaching** | _quarto.yml + course.yml | course info, weeks, assignments | ~100 |
| **r-package** | DESCRIPTION + Package: | package info, version, functions | ~110 |

## Refuses When Exists

If CLAUDE.md already exists and `--force` is not set:

```
⚠️ CLAUDE.md Already Exists

File: $(pwd)/CLAUDE.md
Lines: 329

Use --force to overwrite, or use /craft:docs:claude-md:sync to update.
```

The init command does NOT update existing files. Use `/craft:docs:claude-md:sync` instead.

## Force Overwrite

```bash
/craft:docs:claude-md:init --force
```

Creates a backup at `.CLAUDE.md.backup` before overwriting.

## Dry-Run Mode

Preview template without creating file:

```bash
/craft:docs:claude-md:init --dry-run
```

## Detection Priority

If multiple project types detected, uses highest confidence match:

```
Multiple Project Types Detected

Found indicators for:
  1. Craft Plugin (.claude-plugin/plugin.json) [confidence: 95%]
  2. R Package (DESCRIPTION) [confidence: 70%]

Using: Craft Plugin (highest confidence)
Override with: /craft:docs:claude-md:init --type r-package
```

## Integration

### After Init

```bash
# Step 1: Create from lean template
/craft:docs:claude-md:init

# Step 2: Edit any gaps
/craft:docs:claude-md:edit

# Step 3: Sync and validate
/craft:docs:claude-md:sync

# Step 4: Commit
git add CLAUDE.md && git commit -m "docs: init CLAUDE.md from template"
```

### With Git Worktree

When creating new worktree, init auto-runs if no CLAUDE.md:

```bash
/craft:git:worktree feature/new-feature
# Detects no CLAUDE.md in worktree
# Offers: "Init CLAUDE.md? [y/n]"
```

## Error Handling

### No Project Type Detected

```
⚠️ Unable to Detect Project Type

Options:
  [1] Use generic template
  [2] Specify type: --type [plugin|teaching|r-package]
  [3] Cancel
```

## Technical Notes

**Implementation:**

- Uses `utils/claude_md_detector.py` for project detection
- Uses `utils/claude_md_template_populator.py` for variable substitution
- Uses `utils/claude_md_optimizer.py` for budget validation
- Lean templates in `templates/claude-md/` directory

**Budget Validation:**

- Post-creation check: if generated file > 150 lines, warns user
- Suggests running `/craft:docs:claude-md:sync --optimize`

## Related Commands

| Command | Purpose |
|---------|---------|
| `/craft:docs:claude-md:sync` | Update existing CLAUDE.md + audit + fix |
| `/craft:docs:claude-md:edit` | Interactive editing with iA Writer |

## Migration Note

This command replaces `/craft:docs:claude-md:scaffold`. The old command still works as a deprecation alias but will be removed in v2.13.0.
