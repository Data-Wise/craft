---
description: Interactive section-by-section CLAUDE.md editing with preview
category: docs
arguments:
  - name: section
    description: "Specific section to edit (auto-detected if not specified)"
    required: false
  - name: optimize
    description: Have Claude suggest optimizations after editing
    required: false
    default: false
    alias: -o
  - name: editor
    description: "Editor to use: ia, code, sublime, cursor (default: ia)"
    required: false
    default: ia
    alias: -e
tags: [documentation, claude-md, editing, interactive]
version: 1.0.0
---

# /craft:docs:claude-md:edit - Interactive CLAUDE.md Editing

Edit CLAUDE.md sections interactively with optional Claude optimization suggestions.

**This command follows the "Show Steps First" pattern** - it shows available sections and lets you choose what to edit.

## What It Does

1. Parses CLAUDE.md structure
2. Shows available sections
3. Prompts for section selection
4. Opens section for editing
5. Optionally suggests optimizations
6. Previews changes before applying

## Show Steps First Pattern

This command ALWAYS shows available sections before editing.

### Step 1: Parse Document Structure

```
CLAUDE.md Structure Analysis

File: $(pwd)/CLAUDE.md
Lines: 329
Last modified: 2 days ago

Sections detected (8):
  1. Header + Metadata (lines 1-8)
  2. Quick Commands (lines 10-25)
  3. Project Structure (lines 27-45)
  4. Key Files (lines 47-58)
  5. Development Workflow (lines 60-75)
  6. Testing (lines 77-92)
  7. Git Workflow (lines 94-130)
  8. Links (lines 132-145)

Which section would you like to edit? [1-8/all/cancel]
```

### Step 2: User Selection

Options after seeing sections:

- **1-8** - Edit specific section
- **all** - Review/edit all sections sequentially
- **cancel** - Exit without editing

### Step 3: Show Section Content

```
Selected: Section 2 - Quick Commands

Current content (16 lines):
─────────────────────────────────────────
## Quick Commands

| Task | Command |
|------|---------|
| Run tests | `/craft:test:run` |
| Validate | `/craft:check` |
| Build docs | `/craft:docs:update` |
| Lint code | `/craft:code:lint` |
| Git status | `/craft:git:status` |

─────────────────────────────────────────

Actions:
  [e] Edit this section
  [r] Replace this section
  [d] Delete this section
  [s] Skip to next section
  [c] Cancel

Choice:
```

### Step 4: Edit Mode

When user selects "Edit":

```
Edit Mode - Quick Commands

Opening in iA Writer...
File: /tmp/claude-md-section-quick-commands.md

Edit the content, save (⌘S), and return here.

[Press Enter when done editing...]
```

### Step 5: Preview Changes

```
Preview Changes - Quick Commands

BEFORE (16 lines):
─────────────────────────────────────────
## Quick Commands

| Task | Command |
|------|---------|
| Run tests | `/craft:test:run` |
[... rest of before content ...]
─────────────────────────────────────────

AFTER (20 lines, +4):
─────────────────────────────────────────
## Quick Commands

| Task | Command | Description |
|------|---------|-------------|
| Run tests | `/craft:test:run` | Execute test suite |
| Validate | `/craft:check` | Pre-commit validation |
[... rest of after content ...]
─────────────────────────────────────────

Changes:
  + Added "Description" column to table
  + Added descriptions for each command
  + Net: +4 lines

Apply these changes? [y/n/edit-again]
```

### Step 6: Optimization (Optional)

If `--optimize` flag used:

```
Optimization Suggestions - Quick Commands

Claude's analysis:

1. Table Formatting
   Current: 3 columns (Task, Command, Description)
   Suggestion: Consider condensing to 2 columns
   Reason: Description adds verbosity, command names are self-explanatory

   BEFORE:
   | Task | Command | Description |
   | Run tests | `/craft:test:run` | Execute test suite |

   AFTER:
   | Task | Command |
   | Run tests | `/craft:test:run` |

   Saves: 15 characters per row
   Readability: Improved (less noise)

Apply optimization? [y/n/keep-original]
```

### Step 7: Apply and Confirm

```
✅ Changes Applied

Section: Quick Commands
Lines changed: 16 → 20 (+4)
File: $(pwd)/CLAUDE.md

Next steps:
  1. Review: git diff CLAUDE.md
  2. Continue editing: Select another section
  3. Validate: /craft:docs:claude-md:audit
  4. Commit if satisfied
```

## Section Detection

Sections auto-detected by:

1. **Top-level headers** - `## Section Name`
2. **Horizontal rules** - `---` separators
3. **Standard sections** - Quick Commands, Architecture, etc.

### Common Sections

| Section | Purpose |
|---------|---------|
| Header + Metadata | Title, version, stats |
| Quick Commands | Essential commands table |
| Project Structure | Directory tree |
| Key Files | Important files list |
| Development Workflow | How to contribute |
| Testing | How to run tests |
| Git Workflow | Branch strategy |
| Links | External references |

## Specific Section Targeting

Edit specific section directly:

```bash
# Edit Quick Commands section
/craft:docs:claude-md:edit --section "quick commands"

# Edit Git Workflow section
/craft:docs:claude-md:edit --section "git workflow"

# Edit with optimization
/craft:docs:claude-md:edit --section testing --optimize
```

## Editor Support

| Editor | Flag | Opens File In |
|--------|------|---------------|
| iA Writer | `ia` (default) | Markdown-focused app |
| VS Code | `code` | Full IDE |
| Sublime Text | `sublime` | Text editor |
| Cursor | `cursor` | AI-enhanced editor |

### Change Default Editor

```bash
# Use VS Code
/craft:docs:claude-md:edit --editor code

# Use Cursor
/craft:docs:claude-md:edit -e cursor
```

## Optimization Mode

When `--optimize` flag is set, Claude analyzes your edits and suggests:

### Optimization Types

| Type | What It Checks |
|------|----------------|
| **Verbosity** | Can descriptions be shortened? |
| **Formatting** | Are tables/lists consistent? |
| **Completeness** | Are all commands documented? |
| **Accuracy** | Do commands match source? |
| **Structure** | Is organization logical? |

### Example Optimizations

**1. Table Condensing:**

```markdown
BEFORE:
| Command | Full Description of What It Does |
|---------|----------------------------------|
| `/craft:test:run` | Executes the full test suite with coverage |

AFTER:
| Command | Description |
|---------|-------------|
| `/craft:test:run` | Run tests with coverage |
```

**2. List Simplification:**

```markdown
BEFORE:
- This is the first item that does something
- This is the second item that does another thing

AFTER:
- First item functionality
- Second item functionality
```

**3. Section Reordering:**

```markdown
SUGGESTION: Move "Testing" section before "Git Workflow"
Reason: Developers test before committing
```

## Multi-Section Editing

Edit multiple sections in sequence:

```
Multi-Section Edit Mode

Sections to edit: 3 selected
1. Quick Commands [pending]
2. Testing [pending]
3. Git Workflow [pending]

Starting with section 1...

[Edit → Preview → Apply for each section]

Progress: 1/3 complete
Continue to section 2? [y/n]
```

## Replace vs Edit

**Edit Mode:**

- Opens existing content
- You modify what's there
- Preserves structure

**Replace Mode:**

- Provides template
- You write from scratch
- Can change structure

```
Replace Mode - Quick Commands

Current content will be replaced.
Template provided:

─────────────────────────────────────────
## Quick Commands

| Task | Command |
|------|---------|
| [Add commands here] | [Add paths here] |

─────────────────────────────────────────

Open for editing? [y/n]
```

## Integration

### After Scaffolding

Scaffold creates template, edit fills gaps:

```bash
# Step 1: Create from template
/craft:docs:claude-md:scaffold

# Step 2: Edit unpopulated sections
/craft:docs:claude-md:edit --section "quick commands"
```

### Before Committing

Edit to ensure accuracy:

```bash
# Update before commit
/craft:docs:claude-md:edit --optimize

# Validate
/craft:docs:claude-md:audit

# Commit
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md sections"
```

### With CI Integration

Edit after fix suggestions:

```bash
# CI suggests improvements
/craft:docs:claude-md:audit

# Edit flagged sections
/craft:docs:claude-md:edit --section "testing"

# Re-validate
/craft:docs:claude-md:audit
```

## Error Handling

### Section Not Found

```
⚠️ Section Not Found

Requested: "installation"
Available sections (8):
  1. Header + Metadata
  2. Quick Commands
  3. Project Structure
  4. Key Files
  5. Development Workflow
  6. Testing
  7. Git Workflow
  8. Links

Did you mean: "Development Workflow"? [y/n]
```

### No Sections Detected

```
⚠️ Unable to Parse Sections

CLAUDE.md appears to have non-standard structure.

Options:
  [1] Edit full file (no section selection)
  [2] Cancel and fix structure manually
  [3] Scaffold fresh CLAUDE.md

Recommendation: Option 3 (scaffold fresh with template)
```

### Editor Not Available

```
⚠️ Editor Not Available

Requested: sublime
Status: Not installed

Available editors:
  ✓ ia (iA Writer)
  ✓ code (VS Code)
  ✗ sublime (not installed)
  ✓ cursor (Cursor)

Use different editor? [ia/code/cursor/cancel]
```

## Related Commands

| Command | Purpose |
|---------|---------|
| `/craft:docs:claude-md:scaffold` | Create from template |
| `/craft:docs:claude-md:update` | Auto-update sections |
| `/craft:docs:claude-md:audit` | Validate completeness |
| `/craft:docs:claude-md:fix` | Auto-fix issues |

## Examples

### Example 1: Interactive Section Selection

```bash
cd ~/projects/dev-tools/my-plugin
/craft:docs:claude-md:edit
# Shows 8 sections
# Select "2" for Quick Commands
# Edit in iA Writer
# Preview changes
# Apply
```

### Example 2: Direct Section Edit

```bash
/craft:docs:claude-md:edit --section "testing"
# Opens Testing section directly
# Edit content
# Preview
# Apply
```

### Example 3: Edit with Optimization

```bash
/craft:docs:claude-md:edit --optimize
# Select section
# Edit content
# Claude suggests optimizations
# Apply optimizations
# Save
```

### Example 4: Use Different Editor

```bash
/craft:docs:claude-md:edit --editor code
# Opens in VS Code instead of iA Writer
```

## Technical Notes

**Implementation:**

- Section detection via regex parsing
- Temporary file editing in `/tmp/`
- Diff preview via unified diff
- Optimization via Claude analysis

**Performance:**

- Section parsing: < 500ms
- Editor launch: 1-2 seconds
- Optimization analysis: 3-5 seconds

**File Safety:**

- Original backed up to `.CLAUDE.md.bak`
- Changes previewed before applying
- Can revert via git if needed

## Success Criteria

After editing, verify:

- [ ] Changes applied correctly
- [ ] Section structure maintained
- [ ] No broken formatting
- [ ] Audit passes: `/craft:docs:claude-md:audit`
