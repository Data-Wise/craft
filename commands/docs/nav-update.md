---
description: Update mkdocs.yml navigation from directory structure
category: docs
arguments:
  - name: dry-run
    description: Preview changes without executing
    required: false
    default: false
    alias: -n
deprecated: true
replaced-by: "skills/docs/navigation/"
---

# /craft:docs:nav-update - Update MkDocs Navigation

You are a navigation maintenance assistant. Keep mkdocs.yml nav in sync with docs.

## Purpose

Automatically update mkdocs.yml navigation:

- Add new documentation files
- Remove deleted files
- Reorganize structure
- Maintain consistent ordering

## When Invoked

### Step 1: Scan Documentation

```bash
# Find all docs
find docs/ -name "*.md" -type f | sort

# Read current nav
cat mkdocs.yml | grep -A 100 "^nav:"
```

### Step 2: Compare State

```
📊 NAVIGATION ANALYSIS

Current nav entries: 24
Actual doc files: 28

New files not in nav:
  + docs/guide/opencode.md
  + docs/reference/mcp-commands.md
  + docs/troubleshooting/common-issues.md
  + docs/api/opencode-config.md

Files in nav but missing:
  - docs/deprecated/old-feature.md

Orphan files (exist but not in nav):
  ? docs/drafts/wip-feature.md
```

### Step 3: Show Update Plan

```
📝 NAVIGATION UPDATE PLAN

Additions:
  Guide:
    + opencode.md → "OpenCode Integration"

  Reference:
    + mcp-commands.md → "MCP Commands"

  API:
    + opencode-config.md → "OpenCode Configuration"

  Troubleshooting:
    + common-issues.md → "Common Issues"

Removals:
  - deprecated/old-feature.md (file deleted)

Suggested nav structure:

nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Quick Start: getting-started/quickstart.md
  - Guide:
    - Overview: guide/overview.md
    - OpenCode Integration: guide/opencode.md  # NEW
  - Reference:
    - Commands: reference/commands.md
    - MCP Commands: reference/mcp-commands.md  # NEW
    - Configuration: reference/configuration.md
  - API:
    - Overview: api/index.md
    - OpenCode Config: api/opencode-config.md  # NEW
  - Troubleshooting:
    - Common Issues: troubleshooting/common-issues.md  # NEW

Apply changes? (y/n/edit)
```

### Step 4: Update mkdocs.yml

```yaml
# Updated nav section
nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Quick Start: getting-started/quickstart.md
  - Guide:
    - Overview: guide/overview.md
    - OpenCode Integration: guide/opencode.md
  - Reference:
    - Commands: reference/commands.md
    - MCP Commands: reference/mcp-commands.md
    - Configuration: reference/configuration.md
  - API:
    - Overview: api/index.md
    - OpenCode Config: api/opencode-config.md
  - Troubleshooting:
    - Common Issues: troubleshooting/common-issues.md
```

## Output Format

```
✅ NAVIGATION UPDATED

File: mkdocs.yml

Changes:
  + 4 new entries added
  - 1 dead entry removed
  ~ 0 entries reorganized

Nav structure:
  • Home (1)
  • Getting Started (2)
  • Guide (2)
  • Reference (3)
  • API (2)
  • Troubleshooting (1)

Total: 11 navigation entries

Next steps:
  1. Preview: /craft:site:preview
  2. Validate: /craft:docs:validate
  3. Commit: git add mkdocs.yml && git commit -m "docs: update navigation"
```

## Smart Features

### 1. Title Inference

```
File: docs/guide/opencode-integration.md
Inferred title: "OpenCode Integration"

Based on:
  1. First H1 heading in file
  2. Filename conversion (kebab → Title Case)
  3. YAML frontmatter title
```

### 2. Section Detection

```
New file: docs/reference/new-feature.md

Suggested section: Reference
Reason: Located in docs/reference/

Place after: docs/reference/commands.md
Reason: Alphabetical ordering
```

### 3. Orphan Handling

```
⚠️ ORPHAN FILES DETECTED

These files exist but are not in nav:
  • docs/drafts/wip.md
  • docs/internal/notes.md

Options:
  1. Add to nav
  2. Move to _drafts/ (excluded from build)
  3. Delete files
  4. Ignore (keep as orphans)
```

### 4. Structure Validation

```
🔍 STRUCTURE RECOMMENDATIONS

Current: Flat structure (all in root)
Recommended: Nested by category

Suggested reorganization:
  docs/
  ├── getting-started/
  ├── guide/
  ├── reference/
  ├── api/
  └── troubleshooting/

Apply reorganization? (y/n)
```

## Integration

Works with:

- `/craft:site:build` - Run before build
- `/craft:docs:sync` - Part of sync workflow
- `/craft:docs:validate` - Validate nav entries exist

## Dry-Run Mode

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Update Navigation                                  │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Detection:                                                  │
│   - Config: mkdocs.yml                                        │
│   - Docs directory: docs/                                     │
│   - Files found: 45 markdown files                            │
│                                                               │
│ ✓ Navigation Changes:                                         │
│   - Add: docs/new-guide.md (missing from nav)                 │
│   - Remove: docs/old-api.md (file doesn't exist)              │
│   - Reorder: Move "Installation" before "Quick Start"        │
│                                                               │
│ ✓ File to Update:                                             │
│   - mkdocs.yml (nav section)                                  │
│                                                               │
│ 📊 Summary: 3 navigation changes                               │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

## See Also

- `/craft:site:check` - Validate documentation
- Template: `templates/dry-run-pattern.md`
- `/craft:docs:api` - OpenAPI/Swagger documentation generator
- `/craft:docs:changelog` - Auto-update CHANGELOG.md based on git commits
- `/craft:docs:check` - Documentation health check (links, staleness, navigation)
- `/craft:docs:check-links` - Internal link validation for documentation
- `/craft:docs:demo` - Terminal recording and GIF generator with dependency management
- `/craft:docs:guide` - Orchestrated guide generator
- `/craft:docs:help` - Help page generator
- `/craft:docs:lint` - Markdown quality and error detection with auto-fix
- `/craft:docs:prompt` - Generate documentation prompts
- `/craft:docs:quickstart` - Quick start generator
- `/craft:docs:site` - Website documentation focus
- `/craft:docs:tutorial` - Interactive tutorial generator
- `/craft:docs:website` - ADHD-friendly website enhancement
- `/craft:docs:workflow` - Workflow documentation generator
