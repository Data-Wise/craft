# /craft:docs:update - Smart Documentation Generator

You are an ADHD-friendly documentation generator. Detect what's needed, generate it all, validate, done.

## Purpose

**The ONE command for documentation:**
- Detects what changed in your code
- Figures out what docs are needed (guide? refcard? demo?)
- Generates everything automatically
- Validates and fixes issues
- Updates changelog if commits present

## Philosophy

> **"Just run it. It figures out what's needed, then does it."**

```
┌─────────────────────────────────────────────────────────────┐
│  /craft:docs:update                                         │
│                                                             │
│  1. sync (detect changes, classify docs needed)             │
│  2. generate (guide, demo, refcard - as needed)             │
│  3. check (validate + auto-fix)                             │
│  4. changelog (if commits present)                          │
│  5. summary                                                 │
└─────────────────────────────────────────────────────────────┘
```

## Usage

```bash
# DEFAULT: Smart detection → Full execution of what's needed
/craft:docs:update                    # Detect changes → generate all needed docs

# FEATURE-SPECIFIC: Full cycle scoped to a feature
/craft:docs:update "sessions"         # Document the "sessions" feature
/craft:docs:update "auth system"      # Document the "auth system" feature

# FORCE: Do everything regardless of detection
/craft:docs:update --force            # Full cycle even if nothing changed

# DRY-RUN: Preview what would happen
/craft:docs:update --dry-run          # Show plan without executing

# SKIP PHASES
/craft:docs:update --no-check         # Skip validation phase
/craft:docs:update --no-changelog     # Skip changelog update
```

## When Invoked

### Step 1: Smart Detection (sync)

```bash
# Analyze recent changes
git diff --name-only HEAD~10
git log --oneline -10

# Classify what docs are needed
# (uses scoring algorithm from doc-classifier)
```

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1/5: DETECTING CHANGES                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Analyzing 15 recent commits...                              │
│                                                             │
│ Detected:                                                   │
│   • 5 new CLI commands (src/aiterm/cli/sessions.py)         │
│   • 2 new hooks (session-register, session-cleanup)         │
│   • 1 new module (src/aiterm/sessions/)                     │
│                                                             │
│ Classification:                                             │
│   Guide needed:   ✓ (score: 8) - New module with commands   │
│   Refcard needed: ✓ (score: 5) - 5 new commands             │
│   Demo needed:    ✓ (score: 6) - User-facing CLI workflow   │
│   Mermaid needed: ✓ (score: 7) - Hook-based event system    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: Generate Documentation

For each doc type that scored >= 3:

```
┌─────────────────────────────────────────────────────────────┐
│ Step 2/5: GENERATING DOCS                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ✓ Guide: docs/guide/sessions.md (275 lines)                 │
│   - Overview, Quick Start, How It Works                     │
│   - Commands (5), Configuration, Troubleshooting            │
│                                                             │
│ ✓ Refcard: docs/reference/REFCARD-SESSIONS.md (85 lines)    │
│   - Essential commands, Common workflows                    │
│                                                             │
│ ✓ Demo: docs/demos/sessions.tape (34 lines)                 │
│   - VHS tape for GIF recording                              │
│                                                             │
│ ✓ Mermaid: embedded in guide                                │
│   - Hook workflow diagram                                   │
│                                                             │
│ ✓ CLI epilogs: Updated 5 commands                           │
│ ✓ commands.md: +45 lines                                    │
│ ✓ REFCARD.md: +8 lines (sessions section)                   │
│ ✓ README.md: Added to features list                         │
│ ✓ CLAUDE.md: Updated "Just Completed"                       │
│ ✓ mkdocs.yml: Added 2 nav entries                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: Validate & Fix (check)

```
┌─────────────────────────────────────────────────────────────┐
│ Step 3/5: CHECKING DOCS                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ✓ Fixed: 2 broken links (auto-fixed)                        │
│ ✓ Fixed: 1 nav entry (auto-added)                           │
│ ✓ All new docs validated                                    │
│                                                             │
│ No manual fixes needed.                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step 4: Update Changelog (if commits)

```
┌─────────────────────────────────────────────────────────────┐
│ Step 4/5: UPDATING CHANGELOG                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Found 15 commits since last changelog update.               │
│                                                             │
│ Added to CHANGELOG.md:                                      │
│   ### Added                                                 │
│   - Session coordination feature                            │
│   - `ait sessions live/current/task/conflicts/history`      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step 5: Summary

```
┌─────────────────────────────────────────────────────────────┐
│ ✅ DOCUMENTATION UPDATE COMPLETE                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Feature: Session Tracking                                   │
│                                                             │
│ Generated:                                                  │
│   • docs/guide/sessions.md (NEW - 275 lines)                │
│   • docs/reference/REFCARD-SESSIONS.md (NEW - 85 lines)     │
│   • docs/demos/sessions.tape (NEW - VHS demo)               │
│                                                             │
│ Updated:                                                    │
│   • docs/reference/commands.md (+45 lines)                  │
│   • docs/REFCARD.md (+8 lines)                              │
│   • README.md (features list)                               │
│   • CLAUDE.md (status)                                      │
│   • mkdocs.yml (navigation)                                 │
│   • CHANGELOG.md (session coordination)                     │
│                                                             │
│ Validated:                                                  │
│   • 3 issues auto-fixed                                     │
│   • 0 manual fixes needed                                   │
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ NEXT STEPS:                                                 │
│                                                             │
│ 1. Generate GIF (if demo created):                          │
│    cd docs/demos && vhs sessions.tape                       │
│                                                             │
│ 2. Preview docs:                                            │
│    mkdocs serve                                             │
│                                                             │
│ 3. Commit:                                                  │
│    git add docs/ mkdocs.yml CLAUDE.md README.md CHANGELOG.md│
│    git commit -m "docs: add session tracking documentation" │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Feature-Specific Mode

When a feature name is provided, the cycle is scoped:

```bash
/craft:docs:update "auth"
```

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:update "auth"                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Feature: Authentication                                     │
│                                                             │
│ Scope: Files matching "auth" in name/path                   │
│   • src/auth/                                               │
│   • src/**/auth*                                            │
│   • tests/**/test_auth*                                     │
│                                                             │
│ Detected: 3 commands, 1 module, OAuth integration           │
│                                                             │
│ Generated:                                                  │
│   • docs/guide/auth.md (NEW)                                │
│   • docs/reference/REFCARD-AUTH.md (NEW)                    │
│   • Updated 4 existing docs                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Flags Reference

| Flag | Effect |
|------|--------|
| (none) | Smart detection → generate needed → check → changelog |
| `"feature"` | Scope to specific feature |
| `--force` | Full cycle regardless of detection |
| `--dry-run` | Preview plan without executing |
| `--no-check` | Skip validation phase |
| `--no-changelog` | Skip changelog update |
| `--no-guide` | Skip guide generation |
| `--no-demo` | Skip VHS demo generation |
| `--verbose` | Detailed output |
| `--json` | JSON output |

### Force Generation Flags

Force specific doc types regardless of scoring:

| Flag | Effect |
|------|--------|
| `--with-tutorial` | Force tutorial generation |
| `--with-help` | Force help page generation |
| `--with-workflow` | Force workflow doc generation |
| `--with-quickstart` | Force quickstart generation |
| `--all` | Generate all doc types |
| `--threshold N` | Override scoring threshold (default: 3) |

**Example:**
```bash
/craft:docs:update "auth" --with-tutorial    # Auth docs + forced tutorial
/craft:docs:update --all                      # Generate everything
/craft:docs:update --threshold 2              # Lower threshold for more docs
```

## Scoring Algorithm

Doc types are generated based on classification scores:

| Factor | Guide | Refcard | Demo | Mermaid | Tutorial | Help | Workflow |
|--------|-------|---------|------|---------|----------|------|----------|
| New command (each) | +1 | +1 | +0.5 | +0 | +1 | +2 | +0.5 |
| New module | +3 | +1 | +1 | +2 | +2 | +1 | +1 |
| New hook | +2 | +1 | +1 | +3 | +1 | +0 | +2 |
| Multi-step workflow | +2 | +0 | +3 | +2 | +3 | +0 | +4 |
| Config changes | +0 | +2 | +0 | +0 | +1 | +1 | +0 |
| Architecture change | +1 | +0 | +0 | +3 | +0 | +0 | +1 |
| User-facing CLI | +1 | +1 | +2 | +0 | +2 | +1 | +2 |
| Complex setup | +0 | +0 | +0 | +0 | +3 | +2 | +0 |

**Thresholds:**
- Guide, Refcard, Demo, Mermaid: Score >= 3
- Tutorial, Help, Workflow: Score >= 2 (lower for better coverage)

## Integration

**Orchestrates these commands internally:**
- `/craft:docs:sync` - Change detection and classification
- `/craft:docs:guide` - Guide generation
- `/craft:docs:tutorial` - Tutorial generation
- `/craft:docs:demo` - VHS tape generation
- `/craft:docs:mermaid` - Diagram generation
- `/craft:docs:check` - Validation and auto-fix
- `/craft:docs:changelog` - Changelog updates
- `/craft:docs:claude-md` - CLAUDE.md updates
- `/craft:docs:nav-update` - mkdocs navigation

**Uses templates from:** `templates/docs/`
- `TUTORIAL-TEMPLATE.md` - Progressive learning structure
- `WORKFLOW-TEMPLATE.md` - Multi-step process docs
- `HELP-PAGE-TEMPLATE.md` - Command help pages
- `QUICK-START-TEMPLATE.md` - 5-minute quickstart
- `REFCARD-TEMPLATE.md` - Quick reference cards
- `GETTING-STARTED-TEMPLATE.md` - First-time setup
- `GIF-GUIDELINES.md` - Terminal recording standards

**Replaces:**
- `/craft:docs:feature` - Use `update "feature-name"` instead
- `/craft:docs:generate` - Use `update --force` instead

## ADHD-Friendly Design

1. **One command** - No multi-step process to remember
2. **Smart defaults** - Detects what's needed automatically
3. **Visual progress** - See each phase completing
4. **Clear summary** - Know exactly what was done
5. **Next steps** - Always shows what to do next
