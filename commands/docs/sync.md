---
description: Detect code changes and classify documentation needs
category: docs
arguments:
  - name: verbose
    description: Detailed change analysis
    required: false
    default: false
  - name: json
    description: Machine-readable output
    required: false
    default: false
  - name: since
    description: Commit range (defaults to HEAD~10)
    required: false
  - name: dry-run
    description: Preview detection plan without analyzing files
    required: false
    default: false
    alias: -n
  - name: headless
    description: Non-interactive mode - auto-approve all changes and commit (NEW in v2.22.0)
    required: false
    default: false
  - name: orch
    description: Enable orchestration mode (NEW in v2.5.0)
    required: false
    default: false
  - name: orch-mode
    description: "Orchestration mode: default|debug|optimize|release (NEW in v2.5.0)"
    required: false
    default: null
---

# /craft:docs:sync - Smart Documentation Detection

You are a documentation needs detector. Analyze changes and classify what documentation is needed.

## Purpose

**Smart detection and classification in one command:**

- Detect code changes (what files changed)
- Classify documentation needs (guide? refcard? demo?)
- Report stale docs
- Recommend next actions

## Philosophy

> **"What needs documenting?"**

Quick by default. Run it often. Get a summary of doc status.

## Usage

```bash
# DEFAULT: Quick detection + classification + summary
/craft:docs:sync                      # "3 docs stale, guide recommended (score: 7)"

# OPTIONS
/craft:docs:sync --verbose            # Detailed change analysis
/craft:docs:sync --json               # Machine-readable output
/craft:docs:sync "feature-name"       # Analyze specific feature
/craft:docs:sync --since HEAD~20      # Custom commit range

# Preview detection plan
/craft:docs:sync --dry-run
/craft:docs:sync -n

# Non-interactive (NEW in v2.22.0)
/craft:docs:sync --headless           # Auto-approve all, commit changes
/craft:docs:sync --headless --dry-run # Show what would change without modifying
```

## Dry-Run Mode

Preview what files will be analyzed without reading them:

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Documentation Sync                                 │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Analysis Plan:                                              │
│   - Commit range: HEAD~10..HEAD                               │
│   - Files to check: ~25 changed files                         │
│   - Documentation to review: docs/*.md                        │
│                                                               │
│ ✓ Detection Steps:                                            │
│   1. Gather change data (git log, git diff)                   │
│   2. Classify documentation needs                             │
│   3. Identify stale documentation                             │
│   4. Recommend next actions                                   │
│                                                               │
│ 📊 Summary: Read-only analysis of code changes                 │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

**Note**: This is a read-only command, so dry-run mainly shows what will be analyzed.

## Headless Mode (NEW in v2.22.0)

Non-interactive mode for CI automation and scripted workflows.

### Behavior

| Flag | Behavior |
|------|----------|
| (none) | Interactive — shows changes, asks for approval before each update |
| `--headless` | Auto-approve all changes, commit with standard message |
| `--headless --dry-run` | Show what would change without modifying any files |

### When `--headless` is passed

1. Run Steps 1-3 (gather, classify, detect stale) silently
2. For each recommended action, **auto-approve** without prompting
3. Apply all documentation updates
4. Commit changes with: `docs: auto-sync documentation`
5. Output summary of what was updated

```text
┌───────────────────────────────────────────────────────────────┐
│ /craft:docs:sync --headless                                   │
├───────────────────────────────────────────────────────────────┤
│ Mode: Headless (non-interactive)                              │
│                                                               │
│ Updated:                                                      │
│   ✅ docs/commands/check.md (version sync section added)      │
│   ✅ docs/REFCARD.md (3 new entries)                           │
│   ✅ docs/guide/version-sync.md (created)                     │
│                                                               │
│ Skipped (no changes needed):                                  │
│   ─ docs/commands/workflow/done.md                            │
│   ─ docs/tutorials/getting-started.md                        │
│                                                               │
│ Committed: "docs: auto-sync documentation"                   │
└───────────────────────────────────────────────────────────────┘
```

### When `--headless --dry-run` is passed

Shows what would be updated without modifying files:

```text
┌───────────────────────────────────────────────────────────────┐
│ /craft:docs:sync --headless --dry-run                         │
├───────────────────────────────────────────────────────────────┤
│ Mode: Headless DRY RUN (no changes)                           │
│                                                               │
│ Would update:                                                 │
│   → docs/commands/check.md (version sync section)             │
│   → docs/REFCARD.md (3 new entries)                           │
│   → docs/guide/version-sync.md (create new)                  │
│                                                               │
│ No changes needed:                                            │
│   ─ docs/commands/workflow/done.md                            │
│                                                               │
│ Run without --dry-run to apply changes.                       │
└───────────────────────────────────────────────────────────────┘
```

### CI Usage

The `--headless` flag enables CI automation via GitHub Actions. See `.github/workflows/docs-sync.yml`.

## Orchestration Mode (NEW in v2.5.0)

Use `--orch` flag for orchestrated documentation updates:

```bash
/craft:docs:sync --orch                 # Orchestrated documentation workflow
/craft:docs:sync --orch=optimize        # Fast parallel doc updates
/craft:docs:sync --orch=release --dry-run   # Preview orchestrated workflow
```

### Orchestration Flow

```python
from utils.orch_flag_handler import handle_orch_flag, show_orchestration_preview, spawn_orchestrator

orch_flag = args.orch
mode_flag = args.orch_mode
dry_run = args.dry_run

if orch_flag:
    should_orchestrate, mode = handle_orch_flag(
        "documentation sync and update workflow",
        orch_flag,
        mode_flag
    )

    if dry_run:
        show_orchestration_preview(
            "documentation sync with changes from recent commits",
            mode
        )
        return

    spawn_orchestrator(
        "analyze code changes and update all affected documentation",
        mode
    )
    return

# Otherwise, continue with normal sync flow...
```

## When Invoked

### Step 1: Gather Change Data

```bash
# Recent commits (default: last 10)
git log --oneline -10

# Changed files
git diff --name-only HEAD~10

# New files specifically
git diff --name-only --diff-filter=A HEAD~10

# Detect feature name from commit messages
git log --format="%s" -10 | grep -E "^feat|^fix|^refactor"
```

### Step 2: Classify Documentation Needs

Apply scoring algorithm to determine what docs are needed:

| Factor | Guide | Refcard | Demo | Mermaid |
|--------|-------|---------|------|---------|
| New command (each) | +1 | +1 | +0.5 | +0 |
| New module | +3 | +1 | +1 | +2 |
| New hook | +2 | +1 | +1 | +3 |
| Multi-step workflow | +2 | +0 | +3 | +2 |
| Config changes | +0 | +2 | +0 | +0 |
| Architecture change | +1 | +0 | +0 | +3 |
| User-facing CLI | +1 | +1 | +2 | +0 |

**Threshold:** Score >= 3 triggers recommendation

### Step 3: Check Stale Docs

```bash
# Find docs not updated recently
find docs/ -name "*.md" -mtime +30

# Compare doc timestamps with related code
# docs/guide/auth.md → src/auth/
```

### Step 4: Output Summary

#### Default Output (Quick)

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:sync                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 📊 DOCUMENTATION STATUS                                     │
│                                                             │
│ Recent changes: 15 commits, 23 files                        │
│ Feature detected: "session tracking"                        │
│                                                             │
│ Classification (scores):                                    │
│   Guide:   ✓ 8  (threshold: 3)                              │
│   Refcard: ✓ 5  (threshold: 3)                              │
│   Demo:    ✓ 6  (threshold: 3)                              │
│   Mermaid: ✓ 7  (threshold: 3)                              │
│                                                             │
│ Stale docs: 2                                               │
│   - docs/guide/auth.md (45 days)                            │
│   - docs/reference/api.md (32 days)                         │
│                                                             │
│ Suggested: /craft:docs:update "session tracking"            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Verbose Output (--verbose)

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:sync --verbose                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 📊 DOCUMENTATION ANALYSIS                                   │
│                                                             │
│ Feature: Session Tracking                                   │
│ Commits: 15 (over 2 days)                                   │
│ Files changed: 23                                           │
│                                                             │
│ ──────────────────────────────────────────────────────────  │
│                                                             │
│ DETECTED COMPONENTS:                                        │
│                                                             │
│ Commands (5):                                               │
│   - ait sessions live                                       │
│   - ait sessions current                                    │
│   - ait sessions task                                       │
│   - ait sessions conflicts                                  │
│   - ait sessions history                                    │
│                                                             │
│ Modules (1):                                                │
│   - src/aiterm/sessions/                                    │
│                                                             │
│ Hooks (2):                                                  │
│   - session-register.sh                                     │
│   - session-cleanup.sh                                      │
│                                                             │
│ ──────────────────────────────────────────────────────────  │
│                                                             │
│ CLASSIFICATION:                                             │
│                                                             │
│ ✓ GUIDE (score: 8)                                          │
│   Triggers: New module (+3), 5 commands (+5)                │
│   → docs/guide/sessions.md                                  │
│                                                             │
│ ✓ REFCARD (score: 5)                                        │
│   Triggers: 5 commands (+5)                                 │
│   → docs/reference/REFCARD-SESSIONS.md                      │
│                                                             │
│ ✓ DEMO (score: 6)                                           │
│   Triggers: User-facing CLI (+2), multi-step (+3), module   │
│   → docs/demos/sessions.tape                                │
│                                                             │
│ ✓ MERMAID (score: 7)                                        │
│   Triggers: Hooks (+3), workflow (+2), module (+2)          │
│   → Embed in guide                                          │
│                                                             │
│ ──────────────────────────────────────────────────────────  │
│                                                             │
│ STALE DOCS:                                                 │
│                                                             │
│ ⚠ docs/guide/auth.md                                        │
│   Last updated: 45 days ago                                 │
│   Related code changed: 12 days ago                         │
│                                                             │
│ ⚠ docs/reference/api.md                                     │
│   Last updated: 32 days ago                                 │
│   Related code changed: 5 days ago                          │
│                                                             │
│ ──────────────────────────────────────────────────────────  │
│                                                             │
│ RECOMMENDED ACTIONS:                                        │
│                                                             │
│   1. /craft:docs:update "session tracking"                  │
│      (generates guide, refcard, demo automatically)         │
│                                                             │
│   2. Review stale docs manually                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### JSON Output (--json)

```json
{
  "feature_name": "session tracking",
  "analysis": {
    "commits": 15,
    "files_changed": 23,
    "new_commands": ["sessions live", "sessions current", "sessions task", "sessions conflicts", "sessions history"],
    "new_modules": ["src/aiterm/sessions/"],
    "new_hooks": ["session-register", "session-cleanup"],
    "date_range": "2025-12-25 to 2025-12-26"
  },
  "classification": {
    "guide": { "score": 8, "needed": true, "path": "docs/guide/sessions.md" },
    "refcard": { "score": 5, "needed": true, "path": "docs/reference/REFCARD-SESSIONS.md" },
    "demo": { "score": 6, "needed": true, "path": "docs/demos/sessions.tape" },
    "mermaid": { "score": 7, "needed": true, "embed_in": "docs/guide/sessions.md" }
  },
  "stale_docs": [
    { "path": "docs/guide/auth.md", "days": 45, "code_changed": true },
    { "path": "docs/reference/api.md", "days": 32, "code_changed": true }
  ],
  "suggested_action": "/craft:docs:update \"session tracking\""
}
```

## Detection Logic

### Command Detection

```bash
# Find commands in Python CLI files
grep -E "@app\.command|@.*_app\.command" src/*/cli/*.py

# Parse command names
grep -A1 "@app.command" src/*/cli/*.py | grep "def "
```

### Module Detection

```bash
# New directories with __init__.py
git diff --diff-filter=A HEAD~10 --name-only | grep "__init__.py"
```

### Hook Detection

```bash
# Hook-related files
git diff HEAD~10 --name-only | grep -E "hook|event"

# Claude Code hook settings
grep -E "SessionStart|Stop|PreToolUse" ~/.claude/settings.json
```

### Stale Detection

```bash
# Find old docs
find docs/ -name "*.md" -mtime +30

# Check if related code changed
# Maps: docs/guide/auth.md → src/auth/, src/**/auth*
```

## Flags Reference

| Flag | Effect |
|------|--------|
| (none) | Quick detection + classification summary |
| `"feature"` | Scope to specific feature |
| `--verbose` | Detailed analysis output |
| `--json` | JSON output for scripting |
| `--since COMMIT` | Custom commit range |
| `--no-stale` | Skip stale detection |

## Integration

**Called by:**

- `/craft:docs:update` - First step of update cycle

**Replaces:**

- `/craft:docs:analyze` - Classification merged into sync
- `/craft:docs:done` - Lightweight mode is now the default

**Works with:**

- `/craft:docs:update` - Run sync first, then update generates
- `/craft:docs:check` - Sync detects, check validates

## ADHD-Friendly Design

1. **Quick by default** - Summary output, no overload
2. **One command** - Detection + classification combined
3. **Clear recommendations** - What to do next
4. **Verbose when needed** - Details on demand
5. **JSON for automation** - Script-friendly output

## Orchestration Examples (v2.5.0)

```
User: /craft:docs:sync --orch=optimize

→ ORCHESTRATOR v2.1 — OPTIMIZE MODE
Spawning orchestrator...
   Task: analyze code changes and update all affected documentation
   Mode: optimize

Executing: /craft:orchestrate 'analyze code changes and update all affected documentation' optimize
```

```
User: /craft:docs:sync --orch=release --dry-run

+---------------------------------------------------------------------+
| DRY RUN: Orchestration Preview                                      |
+---------------------------------------------------------------------+
| Task: documentation sync with changes from recent commits           |
| Mode: release                                                       |
| Max Agents: 4                                                       |
| Compression: 85%                                                    |
+---------------------------------------------------------------------+
| This would spawn the orchestrator with the above settings.          |
| Remove --dry-run to execute.                                        |
+---------------------------------------------------------------------+
```
