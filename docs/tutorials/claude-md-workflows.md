# Tutorial: CLAUDE.md Management Workflows

> **Complete guide** to creating, maintaining, and optimizing CLAUDE.md files with craft's claude-md command suite.

**Table of Contents:**

1. [Getting Started](#getting-started)
2. [Workflow 1: New Project Setup](#workflow-1-new-project-setup)
3. [Workflow 2: Maintenance & Updates](#workflow-2-maintenance--updates)
4. [Workflow 3: Section Editing](#workflow-3-section-editing)
5. [Workflow 4: Template Customization](#workflow-4-template-customization)
6. [Advanced Patterns](#advanced-patterns)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### What is CLAUDE.md?

CLAUDE.md is a knowledge file that provides Claude Code with project-specific context:

- Project structure and key files
- Custom commands and workflows
- Development conventions
- Build/test/deployment instructions
- Current status and progress

### The claude-md Command Suite

Craft provides 5 specialized commands for CLAUDE.md management:

| Command | Purpose | Interactive |
|---------|---------|-------------|
| `/craft:docs:claude-md:scaffold` | Create from template | Yes |
| `/craft:docs:claude-md:update` | Sync with project state | Yes |
| `/craft:docs:claude-md:audit` | Validate (read-only) | No |
| `/craft:docs:claude-md:fix` | Auto-fix issues | Yes |
| `/craft:docs:claude-md:edit` | Section-by-section editing | Yes |

All commands follow the **"Show Steps First"** pattern - preview before executing.

---

## Workflow 1: New Project Setup

**Goal:** Create a well-structured CLAUDE.md from scratch in 5 minutes.

### Step 1: Navigate to Project

```bash
cd ~/projects/dev-tools/my-craft-plugin
```

### Step 2: Scaffold from Template

```bash
/craft:docs:claude-md:scaffold
```

**What happens:**

1. **Project Type Detection**

```text
Detecting project type...

Found indicators:
  .claude-plugin/plugin.json  (craft plugin)
  commands/ directory         (51 commands)
  skills/ directory           (8 skills)
  agents/ directory           (3 agents)
  tests/ directory            (127 test files)

Detected: craft-plugin

Template: plugin-template.md
```

2. **Variable Auto-Population**

```text
Extracting variables from project...

From plugin.json:
  name: my-craft-plugin
  version: 1.0.0
  description: Development workflow automation

From filesystem:
  commands: 51
  skills: 8
  agents: 3
  tests: 127

From git:
  repo: github.com/user/my-craft-plugin
  branch: main

Auto-populated: 18/18 variables (100%)
```

3. **Preview Generated File**

```text
Preview: CLAUDE.md (242 lines)

# CLAUDE.md - My Craft Plugin

> Development workflow automation

**51 commands** · **8 skills** · **3 agents** · [Docs](https://user.github.io/my-craft-plugin)

## Quick Commands

| Task | Shell | Craft |
|------|-------|-------|
| Run tests | `python3 -m pytest` | `/craft:test:run` |
| Lint code | `ruff check .` | `/craft:code:lint` |
...

  Proceed with file creation?
  > Yes - Create CLAUDE.md (Recommended)
    Customize - Edit before saving
    Dry run - Show full content without creating
    Cancel - Exit without changes
```

4. **Confirmation and Creation**

```text
Created: CLAUDE.md (242 lines)

Summary:
  18 variables populated automatically
  3 sections: Quick Commands, Project Structure, Git Workflow
  0 TODOs (all auto-filled)

Next steps:
  1. Review: cat CLAUDE.md
  2. Customize: /craft:docs:claude-md:edit
  3. Validate: /craft:docs:claude-md:audit
```

### Step 3: Customize Key Sections

```bash
/craft:docs:claude-md:edit
```

**Interactive section selection:**

```text
CLAUDE.md sections (8 total):

1. Quick Commands (12 commands)
2. Project Structure (5 directories)
3. Git Workflow (3 sections)
4. Development (2 sections)
5. Testing (1 section)
6. Troubleshooting (5 items)
7. Integration (2 sections)
8. Links (4 links)

Which section to edit? (1-8, all, cancel): 1
```

**Edit in preferred editor:**

```text
Opening section: Quick Commands

Editor: iA Writer (default)
Tip: Use -e code flag for VS Code

[Opens in iA Writer...]

When done:
  - Save file (⌘S)
  - Return to terminal
  - Press Enter
```

### Step 4: Validate

```bash
/craft:docs:claude-md:audit
```

**Validation results:**

```text
AUDIT RESULTS

File: CLAUDE.md (242 lines)
Last modified: 30 seconds ago

Checks:
  Version sync         (from plugin.json)
  Command coverage     (51/51 documented)
  Required sections    (8/8 present)
  Broken links         (0 found)
  Template compliance  (matches plugin-template)

Results:
  0 errors
  0 warnings
  1 info (optimization available)

Status: PASSED
```

### Step 5: Commit

```bash
git add CLAUDE.md
git commit -m "docs: add CLAUDE.md with auto-populated template"
```

**Complete workflow time:** ~5 minutes

---

## Workflow 2: Maintenance & Updates

**Goal:** Keep CLAUDE.md current as project evolves.

### When to Run

- After adding/removing commands
- After version bumps
- Before releases
- Weekly maintenance

### Step 1: Check Current Status

```bash
/craft:docs:claude-md:audit
```

**Typical results after active development:**

```text
AUDIT RESULTS

File: CLAUDE.md (242 lines)
Last modified: 2 weeks ago

Issues Found:

ERRORS (2):
  Line 45: Command `/craft:old-command` no longer exists
  Line 78: Broken link to docs/removed-guide.md

WARNINGS (3):
  Version mismatch: CLAUDE.md says v1.0.0, plugin.json says v1.2.0
  Progress drift: CLAUDE.md says 60%, .STATUS says 85%
  Missing commands: 3 new commands not documented

INFO (1):
  File length: 242 lines (optimization recommended if > 300)
```

### Step 2: Auto-Fix Common Issues

```bash
/craft:docs:claude-md:fix
```

**Fix process:**

```text
Auto-fixing issues...

Fix 1/5: Remove stale command reference
  Line 45: `/craft:old-command`
  Action: Remove from Quick Commands table
  Status: FIXED

Fix 2/5: Remove broken link
  Line 78: docs/removed-guide.md
  Action: Remove link reference
  Status: FIXED

Fix 3/5: Update version
  Current: v1.0.0
  Actual: v1.2.0 (from plugin.json)
  Action: Update version number
  Status: FIXED

Fix 4/5: Sync progress
  Current: 60%
  Actual: 85% (from .STATUS)
  Action: Update progress percentage
  Status: FIXED

Fix 5/5: Add new commands (MANUAL)
  Missing: /craft:new-feature, /craft:validate, /craft:analyze
  Action: Use /craft:docs:claude-md:update to add
  Status: SKIPPED (manual)

Summary:
  4 fixed automatically
  1 requires manual action
```

### Step 3: Update with New Commands

```bash
/craft:docs:claude-md:update
```

**Update process with preview:**

```text
CLAUDE.md Update Plan

Changes Detected:

1. Version Sync (already fixed)
   v1.0.0 → v1.2.0

2. New Commands (3)
   + /craft:new-feature
   + /craft:validate
   + /craft:analyze

3. Updated Metrics
   Commands: 51 → 54 (+3)
   Tests: 127 → 145 (+18)

4. Documentation Status
   Current: 85% complete
   Actual: 92% complete (+7%)

Net changes: +15 lines, -0 lines

  Proceed with updates?
  > Yes - Apply all changes (Recommended)
    Interactive - Choose which sections to update
    Dry run - Show preview without applying
    Cancel - Exit without changes
```

**After applying:**

```text
CLAUDE.MD UPDATED

Applied:
  Version synced: v1.0.0 → v1.2.0
  Added 3 new commands to Quick Commands table
  Updated command count: 51 → 54
  Updated test count: 127 → 145
  Updated documentation status: 85% → 92%

File changes:
  Lines: 242 → 257 (+15)
  Sections: 8 (unchanged)

Post-Update Validation:
  All required sections present
  Version matches plugin.json
  All commands documented
  No broken links detected

Next steps:
  1. Review: git diff CLAUDE.md
  2. Commit: git add CLAUDE.md && git commit -m "docs: update CLAUDE.md for v1.2.0"
```

### Step 4: Verify and Commit

```bash
# Review changes
git diff CLAUDE.md

# Verify with audit
/craft:docs:claude-md:audit

# Commit
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for v1.2.0"
```

**Complete workflow time:** ~3 minutes

---

## Workflow 3: Section Editing

**Goal:** Edit specific sections without touching entire file.

### Use Cases

- Update troubleshooting tips
- Add integration notes
- Refine command descriptions
- Update architecture diagrams

### Step 1: List Sections

```bash
/craft:docs:claude-md:edit
```

**Section overview:**

```text
CLAUDE.md sections (8 total):

1. Quick Commands           (45 lines, 12 commands)
2. Project Structure        (38 lines, 5 directories)
3. Git Workflow             (52 lines, 3 subsections)
4. Development              (34 lines, 2 subsections)
5. Testing                  (28 lines, 1 subsection)
6. Troubleshooting          (41 lines, 5 items)
7. Integration              (29 lines, 2 subsections)
8. Links                    (15 lines, 4 links)

Which section to edit? (1-8, all, cancel):
```

### Step 2: Select and Edit Section

**Input:** `6` (Troubleshooting)

```text
Selected: Section 6 - Troubleshooting (41 lines)

Current content preview:
  ## Troubleshooting

  | Issue | Solution |
  |-------|----------|
  | Tests failing | Run /craft:test:debug |
  | Lint errors | Run /craft:code:lint debug |
  | Build issues | Check dependencies with /craft:code:deps-check |
  ...

Opening in iA Writer...

Edit instructions:
  1. Make your changes
  2. Save (⌘S)
  3. Return to terminal
  4. Review diff before applying

[Opens iA Writer with section content...]
```

### Step 3: Preview Changes

**After editing and saving:**

```text
Changes detected in section: Troubleshooting

Diff preview:

  ## Troubleshooting

  | Issue | Solution |
  |-------|----------|
  | Tests failing | Run /craft:test:debug |
  | Lint errors | Run /craft:code:lint debug |
  | Build issues | Check dependencies with /craft:code:deps-check |
+ | Slow tests | Use /craft:test:run optimize for parallel execution |
+ | Coverage gaps | Run /craft:code:coverage to identify untested code |
  ...

Change statistics:
  Lines added: 2
  Lines removed: 0
  Net change: +2 lines

  Apply these changes?
  > Yes - Apply changes to CLAUDE.md
    Edit more - Continue editing section
    Discard - Abandon changes
    Cancel - Exit without applying
```

### Step 4: Apply and Validate

```text
Applied changes to section: Troubleshooting

Updated:
  CLAUDE.md (257 → 259 lines)
  Section 6: Troubleshooting (41 → 43 lines)

Backup created: .CLAUDE.md.backup

Validation:
  Structure intact
  No broken formatting
  All sections present

Next steps:
  1. Review full file: cat CLAUDE.md
  2. Edit another section: /craft:docs:claude-md:edit
  3. Validate: /craft:docs:claude-md:audit
  4. Commit: git add CLAUDE.md && git commit -m "docs: expand troubleshooting section"
```

**Complete workflow time:** ~2 minutes per section

---

## Workflow 4: Template Customization

**Goal:** Customize templates for organization-specific needs.

### When to Customize

- Organization has standard CLAUDE.md structure
- Need project-type-specific sections
- Want consistent branding/formatting

### Templates Location

```bash
ls templates/claude-md/
```

**Output:**

```text
plugin-template.md        (craft plugins)
teaching-template.md      (Quarto course sites)
r-package-template.md     (R packages)
```

### Step 1: Copy Template

```bash
# Copy existing template as starting point
cp templates/claude-md/plugin-template.md templates/claude-md/my-org-plugin.md
```

### Step 2: Edit Template

```bash
# Open in editor
code templates/claude-md/my-org-plugin.md
```

**Template structure with variables:**

```markdown
# CLAUDE.md - {{plugin_name}}

> {{tagline}}

**{{command_count}} commands** · **{{skill_count}} skills** · **{{agent_count}} agents**

## Quick Commands

{{command_table}}

## Organization Standards

### Code Review Process

All changes require:
- [ ] PR review by 2+ team members
- [ ] CI passing (lint + tests + security)
- [ ] Documentation updated
- [ ] CHANGELOG entry added

### Deployment Workflow

...
```

**Available variables:**

- `{{plugin_name}}` - From plugin.json
- `{{version}}` - From plugin.json
- `{{tagline}}` - From plugin.json description
- `{{command_count}}` - Auto-detected
- `{{skill_count}}` - Auto-detected
- `{{agent_count}}` - Auto-detected
- `{{test_count}}` - Auto-detected
- `{{command_table}}` - Auto-generated table
- `{{repo_url}}` - From git remote
- `{{docs_url}}` - From plugin.json

### Step 3: Use Custom Template

**Option 1: Default for project type**

Rename to match project type detection:

```bash
mv templates/claude-md/my-org-plugin.md templates/claude-md/craft-plugin.md
```

**Option 2: Explicit template selection**

```bash
# Force template when scaffolding
/craft:docs:claude-md:scaffold --template=my-org-plugin
```

### Step 4: Test Template

```bash
# Test in a sample project
cd ~/projects/test-plugin
/craft:docs:claude-md:scaffold

# Verify variables populated correctly
cat CLAUDE.md
```

**Complete workflow time:** ~15-30 minutes (one-time setup)

---

## Advanced Patterns

### Pattern 1: Dry-Run Before Commit

Always preview changes before committing:

```bash
# Update with dry-run first
/craft:docs:claude-md:update --dry-run

# Review what would change
# Then apply if satisfied
/craft:docs:claude-md:update
```

### Pattern 2: Interactive Section Updates

Selectively update only changed sections:

```bash
/craft:docs:claude-md:update --interactive
```

**Prompts for each section:**

```text
Section: Quick Commands (3 new commands detected)
  Add: /craft:new-feature, /craft:validate, /craft:analyze
  Apply? (y/n/skip): y

Section: Project Structure (no changes)
  Apply? (y/n/skip): skip

Section: Testing (test count changed)
  Update: 127 → 145 tests
  Apply? (y/n/skip): y
```

### Pattern 3: Optimization Pass

Condense verbose CLAUDE.md files:

```bash
# Update and optimize in one step
/craft:docs:claude-md:update --optimize
```

**Optimization actions:**

```text
OPTIMIZATION APPLIED

Condensed:
  Quick Commands: Shortened verbose descriptions
  Project Structure: Grouped related directories
  Code examples: Removed obvious comments

Before: 287 lines
After: 231 lines (-56 lines, -19%)

Quality maintained:
  All essential info preserved
  All links still valid
  Structure unchanged
```

### Pattern 4: Pre-Release Validation

Before releases, ensure CLAUDE.md is pristine:

```bash
# Comprehensive check
/craft:docs:claude-md:audit --strict

# Fix any issues
/craft:docs:claude-md:fix

# Update to latest
/craft:docs:claude-md:update

# Final validation
/craft:docs:claude-md:audit --strict
```

### Pattern 5: Cross-Project Consistency

For monorepo or multiple related projects:

**Create shared base template:**

```markdown
# templates/claude-md/org-base.md

## Organization Standards

[Shared content across all projects...]

## Project-Specific

{{project_specific_content}}
```

**Inherit in project templates:**

```markdown
# templates/claude-md/plugin-template.md

{{include:org-base.md}}

## Plugin-Specific Sections

...
```

### Pattern 6: Git Worktree Integration

When creating feature branches with worktrees:

```bash
# Create worktree
git worktree add ~/.git-worktrees/craft/feature-xyz -b feature/xyz dev

# Navigate to worktree
cd ~/.git-worktrees/craft/feature-xyz

# If no CLAUDE.md, scaffold offers to create
/craft:docs:claude-md:scaffold

# During development, keep updated
/craft:docs:claude-md:update

# Before merging, validate
/craft:docs:claude-md:audit --strict
```

---

## Troubleshooting

### Issue: "Could not detect project type"

**Symptoms:**

```text
/craft:docs:claude-md:scaffold

Error: Could not detect project type
No valid project indicators found
```

**Solutions:**

1. **Check for indicator files:**

```bash
# Craft plugin
ls .claude-plugin/plugin.json

# Teaching site
ls _quarto.yml course.yml

# R package
ls DESCRIPTION NAMESPACE
```

2. **Force template:**

```bash
/craft:docs:claude-md:scaffold --template=plugin
```

3. **Use generic template:**

```bash
/craft:docs:claude-md:scaffold --template=generic
```

### Issue: "Version mismatch not auto-fixing"

**Symptoms:**

```text
/craft:docs:claude-md:fix

Warning: Version mismatch
  CLAUDE.md: v1.0.0
  plugin.json: v1.2.0
  Status: NOT FIXED (file not found)
```

**Solutions:**

1. **Check version source exists:**

```bash
# For plugins
cat .claude-plugin/plugin.json | grep version

# For Node
cat package.json | grep version

# For Python
cat pyproject.toml | grep version
```

2. **Manual update:**

```bash
# Edit directly
/craft:docs:claude-md:edit

# Or use update command
/craft:docs:claude-md:update status
```

### Issue: "New commands not being added"

**Symptoms:**

```text
/craft:docs:claude-md:update

Detected 3 new commands:
  /craft:new-feature
  /craft:validate
  /craft:analyze

But Quick Commands table not updated
```

**Solutions:**

1. **Check command detection:**

```bash
# Verify commands exist
ls commands/new-feature.md
ls commands/validate.md
ls commands/analyze.md
```

2. **Check frontmatter:**

```yaml
# Each command file needs frontmatter
---
description: Command description
category: code
---
```

3. **Force full update:**

```bash
/craft:docs:claude-md:update commands
```

### Issue: "Section editing changes entire file"

**Symptoms:**

```text
/craft:docs:claude-md:edit

Selected section: Quick Commands
But diff shows changes across entire file
```

**Solutions:**

1. **Check section headers:**

```markdown
# Must use top-level headers (##) for sections
## Quick Commands   ← Correct
### Quick Commands  ← Wrong (subsection)
```

2. **Verify section boundaries:**

```bash
# List all sections
grep "^## " CLAUDE.md
```

3. **Re-scaffold if structure broken:**

```bash
# Backup first
cp CLAUDE.md CLAUDE.md.manual-backup

# Re-scaffold
/craft:docs:claude-md:scaffold --force

# Merge manual changes back
```

### Issue: "Template variables not populating"

**Symptoms:**

```text
/craft:docs:claude-md:scaffold

Created CLAUDE.md with TODOs:
  {{plugin_name}} not populated
  {{version}} not populated
```

**Solutions:**

1. **Check source files exist:**

```bash
# For plugin template
cat .claude-plugin/plugin.json

# For teaching template
cat _quarto.yml

# For R package template
cat DESCRIPTION
```

2. **Check file format:**

```json
// plugin.json must be valid JSON
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "Plugin description"
}
```

3. **Manual population:**

```bash
# Edit template variables directly
/craft:docs:claude-md:edit
```

---

## See Also

- **Command Reference:** [CLAUDE-MD Commands](../commands/docs/claude-md.md)
- **Quick Reference:** [REFCARD-CLAUDE-MD](../reference/REFCARD-CLAUDE-MD.md)
- **Interactive Commands Guide:** [Interactive Commands](../guide/interactive-commands.md)
- **Templates:** `templates/claude-md/`

---

**Tutorial Version:** 1.0.0
**Last Updated:** 2026-01-29
**Craft Version:** v2.9.0+
