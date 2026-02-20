# Quick Reference: CLAUDE.md Commands

> **Fast lookup** for claude-md command syntax and common workflows.

**3 Commands** · **3 Templates** · **Show Steps First Pattern**

> **Note (v2.12.0):** Commands consolidated. `scaffold` -> `init`, `update`/`audit`/`fix` -> `sync`. Old names work as aliases until v2.13.0.

---

## Command Summary

| Command | Purpose | Interactive | Time |
|---------|---------|-------------|------|
| `init` | Create from template | Yes | ~2 min |
| `sync` | Unified sync pipeline (validate + update + fix) | Yes | ~1 min |
| `edit` | Section editing | Yes | ~2 min |

---

## Quick Start

```bash
# New project - create CLAUDE.md
/craft:docs:claude-md:init

# Existing project - sync and validate
/craft:docs:claude-md:sync

# Sync with auto-fix
/craft:docs:claude-md:sync --fix
```

---

## init - Create from Template

> Renamed from `scaffold` in v2.12.0. The `scaffold` alias works until v2.13.0.

### Basic Usage

```bash
# Auto-detect project type
/craft:docs:claude-md:init

# Force specific template
/craft:docs:claude-md:init --template=plugin
/craft:docs:claude-md:init --template=teaching
/craft:docs:claude-md:init --template=r-package

# Overwrite existing
/craft:docs:claude-md:init --force

# Preview without creating
/craft:docs:claude-md:init --dry-run
```

### Templates

| Template | For | Auto-Detected When |
|----------|-----|---------------------|
| `plugin` | Craft plugins | `.claude-plugin/plugin.json` exists |
| `teaching` | Quarto course sites | `_quarto.yml` + `course.yml` exist |
| `r-package` | R packages | `DESCRIPTION` + `NAMESPACE` exist |

### Auto-Populated Variables

**Plugin template (18 variables):**

- Name, version, description from `plugin.json`
- Command/skill/agent counts from directory scan
- Repository URL from git remote
- Documentation URL from `plugin.json`

**Teaching template (12 variables):**

- Course name/code from `course.yml`
- Semester, instructor from `course.yml`
- Week/assignment/exam counts from filesystem

**R package template (15 variables):**

- Package metadata from `DESCRIPTION`
- Function/test/vignette counts from directories
- Dependencies from `DESCRIPTION`

---

## sync - Unified Sync Pipeline

> Replaces `update`, `audit`, and `fix` (v2.12.0). Old names work as aliases until v2.13.0.

### Basic Usage

```bash
# Full sync (validate + update all sections)
/craft:docs:claude-md:sync

# Specific section only
/craft:docs:claude-md:sync status
/craft:docs:claude-md:sync commands
/craft:docs:claude-md:sync architecture

# Sync + optimize
/craft:docs:claude-md:sync --optimize

# Preview without applying
/craft:docs:claude-md:sync --dry-run

# Interactive section selection
/craft:docs:claude-md:sync --interactive
```

### What Gets Updated

**All project types:**

- Version (from plugin.json/package.json/pyproject.toml/DESCRIPTION)
- Status and progress (from .STATUS file)

**Craft plugins:**

- Command count and list
- Skill count and list
- Agent count and list
- Test count

**Teaching sites:**

- Week count
- Assignment count
- Course metadata

**R packages:**

- Function count
- Test count
- Vignette count
- Dependencies

---

## Validation (part of sync)

> The standalone `audit` command has been folded into `sync`. The `audit` alias works until v2.13.0.

### Basic Usage

```bash
# Validate CLAUDE.md (runs as part of sync)
/craft:docs:claude-md:sync

# Strict mode (exit 1 on errors)
/craft:docs:claude-md:sync --strict

# Specific scope
/craft:docs:claude-md:sync errors
/craft:docs:claude-md:sync warnings
/craft:docs:claude-md:sync all
```

### Checks Performed

| Check | Severity | Description |
|-------|----------|-------------|
| Version mismatch | Warning | CLAUDE.md version vs source |
| Stale commands | Error | Commands that no longer exist |
| Broken links | Error | Dead internal/external links |
| Missing sections | Warning | Required sections absent |
| Progress drift | Warning | Progress vs .STATUS mismatch |

### Output Format

```text
AUDIT RESULTS

File: CLAUDE.md (242 lines)
Last modified: 2 weeks ago

ERRORS (2):
  Line 45: Command /craft:old-command no longer exists
  Line 78: Broken link to docs/removed.md

WARNINGS (3):
  Version mismatch: v1.0.0 vs v1.2.0
  Progress drift: 60% vs 85%
  Missing: 3 new commands not documented

INFO (1):
  Optimization available (file length: 242 lines)

Status: FAILED (2 errors)
```

---

## Auto-Fix (part of sync --fix)

> The standalone `fix` command has been folded into `sync --fix`. The `fix` alias works until v2.13.0.

### Basic Usage

```bash
# Fix errors only
/craft:docs:claude-md:sync --fix

# Fix errors + warnings
/craft:docs:claude-md:sync --fix warnings

# Fix everything auto-fixable
/craft:docs:claude-md:sync --fix all

# Preview without applying
/craft:docs:claude-md:sync --fix --dry-run

# Interactive confirmation
/craft:docs:claude-md:sync --fix --interactive
```

### Auto-Fixable Issues

| Issue | Fix Action |
|-------|------------|
| Stale command reference | Remove from table |
| Broken link | Remove link reference |
| Version mismatch | Update to source version |
| Progress drift | Sync from .STATUS |

### Manual-Only Issues

- Missing sections (need content)
- New commands (use `update` instead)
- Template restructuring
- Custom content updates

### Output Format

```text
Auto-fixing issues...

Fix 1/4: Remove stale command
  Line 45: /craft:old-command
  Status: FIXED

Fix 2/4: Update version
  v1.0.0 → v1.2.0
  Status: FIXED

Fix 3/4: Sync progress
  60% → 85%
  Status: FIXED

Fix 4/4: Add new commands (MANUAL)
  Missing: 3 commands
  Status: SKIPPED

Summary:
  3 fixed automatically
  1 requires manual action
```

---

## edit - Section Editing

### Basic Usage

```bash
# Interactive section selection
/craft:docs:claude-md:edit

# Edit specific section by name
/craft:docs:claude-md:edit "Quick Commands"
/craft:docs:claude-md:edit troubleshooting

# Replace entire section
/craft:docs:claude-md:edit "Testing" --replace

# Delete section
/craft:docs:claude-md:edit "Deprecated" --delete
```

### Section Operations

| Operation | Command | Description |
|-----------|---------|-------------|
| **Edit** | `/craft:docs:claude-md:edit` | Modify section content |
| **Replace** | `--replace` | Replace entire section |
| **Delete** | `--delete` | Remove section |
| **Preview** | (automatic) | Show diff before applying |

### Interactive Flow

```text
1. List sections
2. Select section (1-8, all, cancel)
3. Open in editor (iA Writer default)
4. Make changes and save
5. Preview diff with change stats
6. Confirm (apply/edit more/discard/cancel)
7. Apply changes
8. Auto-backup created
```

---

## Common Workflows

### New Project Setup (5 min)

```bash
cd ~/projects/my-project
/craft:docs:claude-md:init
/craft:docs:claude-md:edit      # Customize
/craft:docs:claude-md:sync      # Validate
git add CLAUDE.md
git commit -m "docs: add CLAUDE.md"
```

### Weekly Maintenance (3 min)

```bash
/craft:docs:claude-md:sync --fix  # Validate + auto-fix
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md"
```

### Pre-Release Validation (2 min)

```bash
/craft:docs:claude-md:sync --optimize
/craft:docs:claude-md:sync --strict
/craft:docs:claude-md:sync --fix all
git add CLAUDE.md
git commit -m "docs: prepare CLAUDE.md for release"
```

### Quick Section Update (2 min)

```bash
/craft:docs:claude-md:edit       # Select section
# Edit in iA Writer
# Review diff
# Confirm and apply
git add CLAUDE.md
git commit -m "docs: update troubleshooting section"
```

---

## Flags & Options

### Common Flags

| Flag | Short | Commands | Purpose |
|------|-------|----------|---------|
| `--dry-run` | `-n` | sync, init | Preview without applying |
| `--interactive` | `-i` | sync | Prompt for each change |
| `--optimize` | `-o` | sync | Condense verbose sections |
| `--fix` | - | sync | Enable auto-fix mode |
| `--force` | `-f` | init | Overwrite existing file |
| `--strict` | - | sync | Exit 1 on errors (CI) |

### Template Selection

| Flag | Value | Purpose |
|------|-------|---------|
| `--template` | `plugin` | Force plugin template |
| `--template` | `teaching` | Force teaching template |
| `--template` | `r-package` | Force R package template |

### Section Scope

| Argument | Commands | Purpose |
|----------|----------|---------|
| `status` | sync | Update version/progress only |
| `commands` | sync | Update command list only |
| `architecture` | sync | Update structure only |
| `errors` | sync | Check errors only |
| `warnings` | sync | Check warnings only |
| `all` | sync | All checks/fixes |

---

## Project Type Detection

### Detection Priority

1. **Craft Plugin** - `.claude-plugin/plugin.json` exists
2. **Teaching Site** - `_quarto.yml` + `course.yml` exist
3. **R Package** - `DESCRIPTION` + `NAMESPACE` exist
4. **Generic** - Fallback if no specific indicators

### Override Detection

```bash
# Force template even if wrong type detected
/craft:docs:claude-md:init --template=plugin
```

---

## Layered Architecture (v2.22.0)

CLAUDE.md uses a layered system to minimize per-session token cost.

### Token Budget Breakdown

| Layer | Loaded | Lines | Purpose |
|-------|--------|-------|---------|
| `CLAUDE.md` | Always | ~82 | Quick commands, workflow constraints, troubleshooting |
| `~/.claude/rules/*.md` | Always | ~221 | Behavioral imperatives (spec-only-mode, brainstorm-mode, etc.) |
| `MEMORY.md` | Always | ~28 | Cross-session learnings (capped at 200 lines) |
| **Total always-loaded** | | **~330 lines** | **~4000 tokens/session** |

| Layer | Loaded | Purpose |
|-------|--------|---------|
| `~/.claude/reference/` | On-demand | Global: MCP servers, plugins, shell workflow, release automation |
| `.claude/reference/` | On-demand | Project: agents, test suite, project structure |

**On-demand loading trigger:** Claude Code loads reference files when it encounters a pointer in CLAUDE.md (e.g., "see `.claude/reference/`") and the user's question relates to that topic. The files are NOT loaded every session — only when contextually relevant.

### Budget Enforcement

The `scripts/claude-md-budget-check.sh` script (also runs as a pre-commit hook) enforces:

- CLAUDE.md stays under the configured line budget (default: 150 lines)
- Budget reads from `.claude-plugin/config.json` > `package.json` > default 150

### Generate Reference Files

```bash
# Auto-generate from filesystem state
PYTHONPATH=. python3 utils/claude_md_sync.py --generate-reference
```

Creates/refreshes `.claude/reference/` with current agent inventory, test file classification, and project structure counts.

### Session-End Auto-Sync

`/workflow:done` automatically:

1. Checks CLAUDE.md count accuracy (Step 1.7)
2. Auto-fixes stale counts in-place
3. Refreshes .STATUS timestamps (Step 1.8)

---

## Integration Points

### With craft:check

```bash
# Includes CLAUDE.md validation
/craft:check
```

### With craft:git:worktree

```bash
# After creating worktree
git worktree add ~/.git-worktrees/project/feature-xyz -b feature/xyz dev
cd ~/.git-worktrees/project/feature-xyz

# Init if missing
/craft:docs:claude-md:init
```

### With craft:docs:update

```bash
# Coordinate documentation updates
/craft:docs:update
/craft:docs:claude-md:sync
```

---

## Troubleshooting

| Issue | Quick Fix |
|-------|-----------|
| "Could not detect project type" | Use `--template=<type>` flag |
| "Version mismatch" | Run `/craft:docs:claude-md:sync --fix` |
| "Stale commands" | Run `/craft:docs:claude-md:sync --fix` |
| "File too long" | Run `/craft:docs:claude-md:sync --optimize` |
| "Template not detected" | Check indicator files exist |
| "Section not found" | Use `/craft:docs:claude-md:edit` to list |
| "Changes not applying" | Check file permissions |

---

## Keyboard Shortcuts

### In iA Writer (Default Editor)

| Key | Action |
|-----|--------|
| `⌘S` | Save file |
| `⌘W` | Close file |
| `⌘Q` | Quit iA Writer |

### Alternative Editors

```bash
# VS Code
/craft:docs:claude-md:edit -e code

# Sublime Text
/craft:docs:claude-md:edit -e sublime

# Cursor
/craft:docs:claude-md:edit -e cursor
```

---

## Tips & Best Practices

1. **Preview First** - Always use `--dry-run` before applying changes
2. **Frequent Syncs** - Run `sync` after major changes
3. **Validate Before Release** - Use `sync --strict` in CI
4. **Keep Concise** - Use `--optimize` flag to condense
5. **Section Editing** - Edit specific sections instead of entire file
6. **Template Customization** - Create org-specific templates
7. **Git Integration** - Commit CLAUDE.md changes separately

---

## See Also

- **Tutorial:** [CLAUDE.md Workflows](../tutorials/claude-md-workflows.md)
- **Commands:** [CLAUDE-MD Commands](../commands/docs/claude-md.md)
- **Guide:** [Interactive Commands](../guide/interactive-commands.md)
- **Templates:** `templates/claude-md/`

---

**Version:** 1.1.0
**Last Updated:** 2026-02-18
**Craft Version:** v2.22.0+
