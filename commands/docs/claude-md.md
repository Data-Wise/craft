# /craft:docs:claude-md - Update CLAUDE.md

You are a CLAUDE.md maintenance assistant. Keep project instructions current.

## Purpose

Update CLAUDE.md files to reflect:
- Current project status
- New features/commands
- Changed architecture
- Updated dependencies
- New workflows

## When Invoked

### Step 1: Analyze Project State

```bash
# Check project type
ls -la DESCRIPTION pyproject.toml package.json 2>/dev/null

# Check recent changes
git log --oneline -20

# Check current CLAUDE.md
cat CLAUDE.md | head -100
```

### Step 2: Identify Updates Needed

Compare CLAUDE.md against:

| Source | Check For |
|--------|-----------|
| `git log` | New features not documented |
| `pyproject.toml` | Version mismatch |
| `.STATUS` | Progress updates |
| `src/` structure | Architecture changes |
| `docs/` | New documentation |
| `tests/` | Test coverage changes |

### Step 3: Show Update Plan

```
📄 CLAUDE.MD UPDATE ANALYSIS

Current state:
  Version in CLAUDE.md: v0.2.0
  Actual version: v0.2.1 ⚠️ Mismatch

Sections needing updates:

1. Project Status
   Current: "v0.2.0 in development"
   Should be: "v0.2.1 ✅ RELEASED"

2. Quick Reference
   Missing: `ait opencode` commands
   Missing: `ait mcp` commands

3. Key Files
   Missing: `src/aiterm/opencode/` module

4. Recent Changes
   Add: PyPI publishing
   Add: OpenCode integration

Proceed with updates? (y/n/select)
```

### Step 4: Generate Updates

For each section:
1. Read current content
2. Generate updated content
3. Show diff
4. Apply with confirmation

## Sections to Maintain

### Standard CLAUDE.md Structure

```markdown
# CLAUDE.md

## Project Overview
- What it does
- Target users
- Tech stack

## Project Status
- Current version
- Phase/milestone
- Recent achievements

## Quick Reference
- Key commands
- Important files
- Common workflows

## Architecture
- Directory structure
- Key modules
- Design decisions

## Development
- Setup instructions
- Testing
- Contributing
```

### Section-Specific Updates

**Project Status:**
```markdown
## Project Status: v0.2.1 ✅ RELEASED

**Current Phase:** Distribution complete, planning v0.3.0

**v0.2.1 Release (Dec 26, 2025):**
- [x] PyPI Published
- [x] Homebrew Fixed
- [x] Documentation Updated
```

**Quick Reference:**
```markdown
## Quick Reference

### Commands
| Command | Description |
|---------|-------------|
| `ait doctor` | Check installation |
| `ait detect` | Show project context |
| `ait opencode` | OpenCode integration | ← NEW
```

## Output Format

```
✅ CLAUDE.MD UPDATED

Updated sections:
  • Project Status (version bump)
  • Quick Reference (+3 commands)
  • Architecture (+1 module)

Changes:
  +15 lines, -8 lines

Next steps:
  1. Review: git diff CLAUDE.md
  2. Commit: git add CLAUDE.md && git commit -m "docs: update CLAUDE.md for v0.2.1"
```

## Smart Features

### 1. Version Sync
Automatically sync version from:
- `pyproject.toml` (Python)
- `package.json` (Node)
- `DESCRIPTION` (R)

### 2. Command Discovery
Scan for new commands in:
- `src/*/cli/*.py`
- `commands/*.md`
- CLI help output

### 3. Status File Integration
Read `.STATUS` file for:
- Current progress
- Next steps
- Recent session notes

### 4. Architecture Detection
Detect new modules/files:
```
New directories detected:
  • src/aiterm/opencode/ (new module)

Add to Architecture section? (y/n)
```

## Integration

Works with:
- `/craft:docs:sync` - Part of doc sync workflow
- `/craft:code:release` - Update before release
- `/workflow:done` - Update at session end
