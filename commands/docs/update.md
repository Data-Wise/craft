# /craft:docs:update - Smart Documentation Generator

You are an ADHD-friendly documentation generator. Detect what's needed, generate it all, validate, done.

## Purpose

**The ONE command for documentation:**

- Detects what changed in your code
- Figures out what docs are needed (guide? refcard? demo?)
- Generates everything automatically
- Validates and fixes issues
- Updates changelog if commits present
- **NEW:** Interactive category-level prompts for precise control

## Philosophy

> **"Just run it. It figures out what's needed, then does it."**

```text
┌─────────────────────────────────────────────────────────────┐
│  /craft:docs:update                                         │
│                                                             │
│  1. sync (detect changes, classify docs needed)             │
│  2. generate (guide, demo, refcard - as needed)             │
│  3. check (validate + auto-fix)                             │
│  4. changelog (if commits present)                          │
│  5. summary                                                 │
└─────────────────────────────────────────────────────────────┘
```text

## Usage

```bash
# DEFAULT: Smart detection → Full execution of what's needed
/craft:docs:update                    # Detect changes → generate all needed docs

# INTERACTIVE: Category-level prompts for each update type
/craft:docs:update --interactive      # Prompt for version refs, counts, links, etc.
/craft:docs:update -i                 # Short form

# CATEGORY-SPECIFIC: Update only specific categories
/craft:docs:update --category=version_refs    # Only version references
/craft:docs:update --category=broken_links    # Only fix broken links
/craft:docs:update -C help_files              # Only help file updates

# FEATURE-SPECIFIC: Full cycle scoped to a feature
/craft:docs:update "sessions"         # Document the "sessions" feature
/craft:docs:update "auth system"      # Document the "auth system" feature

# FORCE: Do everything regardless of detection
/craft:docs:update --force            # Full cycle even if nothing changed

# DRY-RUN: Preview what would happen
/craft:docs:update --dry-run          # Show plan without executing
/craft:docs:update --interactive --dry-run   # Preview interactive prompts

# SKIP PHASES
/craft:docs:update --no-check         # Skip validation phase
/craft:docs:update --no-changelog     # Skip changelog update

# AUTO-YES: Non-interactive mode (apply all updates)
/craft:docs:update --auto-yes         # Auto-approve all updates (use with caution)
```text

## Interactive Mode (NEW in v2.6.0)

Interactive mode provides category-level control over documentation updates:

### Detection Categories

| Category | What It Updates | Example |
|----------|-----------------|---------|
| **version_refs** | Version numbers in docs (v2.5.0 → v2.6.0) | 12 files need version update |
| **command_counts** | "99 commands" → "101 commands" | 4 files with outdated counts |
| **feature_status** | Feature matrix, completion % | 3 features marked complete |
| **broken_links** | Internal links, file refs | 47 broken internal links |
| **gif_regen** | Outdated demo GIFs | 3 GIFs with changed commands |
| **changelog** | Release notes for new version | Add v2.6.0 changelog entry |
| **navigation** | mkdocs.yml, table of contents | 2 new pages to add |
| **help_files** | Command YAML frontmatter | 5 commands need help updates |
| **tutorial_updates** | Existing tutorial files | 2 tutorials need updates |

### Interactive Workflow

```text
╭─────────────────────────────────────────────────────────────╮
│ Step 1/5: DETECTING CHANGES (Interactive Mode)              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Scanning documentation for outdated content...             │
│                                                             │
│ Found:                                                      │
│   • 12 version references (v2.5.1 → v2.6.0)                 │
│   • 4 command count updates (99 → 101 commands)             │
│   • 3 broken internal links                                 │
│   • 2 GIFs with changed commands                            │
│   • 5 commands missing help documentation                   │
│                                                             │
│ ───────────────────────────────────────────────────────────│
│                                                             │
│ Category 1/5: Version References (12 items)                 │
│                                                             │
│ Update version from v2.5.1 to v2.6.0 in:                    │
│   • README.md (line 8)                                      │
│   • CLAUDE.md (line 4)                                      │
│   • docs/guide/installation.md (line 15)                    │
│   ... and 9 more files                                      │
│                                                             │
│ Apply these updates? [y/N/preview]                          │
│ > y                                                         │
│                                                             │
│ ✓ Updated 12 version references                             │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```text

### Interactive Prompts

Each category gets a single prompt with options:

- **y** - Apply all updates in this category
- **N** - Skip this category (default, silent skip)
- **preview** - Show detailed preview before deciding
- **details** - Show detailed file list and changes

### GIF Regeneration Workflow

When outdated GIFs are detected:

```text
╭─────────────────────────────────────────────────────────────╮
│ Category: GIF Regeneration (2 items)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ hub-demo.gif (outdated)                                     │
│   Command changed:                                          │
│   OLD: /craft:do "task"                                     │
│   NEW: /craft:do "task" --orch=default                      │
│   Last updated: 2026-01-15                                  │
│                                                             │
│ brainstorm-demo.gif (outdated)                              │
│   Command changed:                                          │
│   OLD: /craft:workflow:brainstorm d:3 m:5                   │
│   NEW: /craft:workflow:brainstorm --categories d:3 m:5      │
│   Last updated: 2026-01-18                                  │
│                                                             │
│ Regenerate these GIFs? [y/N/one-by-one]                     │
│ > one-by-one                                                │
│                                                             │
│ GIF 1/2: hub-demo.gif                                       │
│ Regenerate this GIF? [y/N]                                  │
│ > y                                                         │
│                                                             │
│ Recording... (press Ctrl+D when done)                       │
│ ✓ GIF saved: docs/demos/hub-demo.gif                        │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```text

### Help File Validation

Comprehensive validation with per-command prompts:

```text
╭─────────────────────────────────────────────────────────────╮
│ Category: Help Files (5 commands with issues)               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Issue 1/5: Missing Flag Documentation                       │
│                                                             │
│ Command: /craft:do                                          │
│ File: commands/do.md                                        │
│                                                             │
│ Flag in code but not documented:                            │
│   --orch-mode                                               │
│                                                             │
│ Detected from implementation:                               │
│   Name: orch-mode                                           │
│   Type: string                                              │
│   Options: default|debug|optimize|release                   │
│   Default: null                                             │
│                                                             │
│ Suggested YAML:                                             │
│   - name: orch-mode                                         │
│     description: "Orchestration mode selection"             │
│     required: false                                         │
│     default: null                                           │
│                                                             │
│ Add this flag to arguments array? [y/N/edit]                │
│ > y                                                         │
│                                                             │
│ ✓ Updated commands/do.md                                    │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```text

### Lint Integration

Auto-triggered after updates:

```text
╭─────────────────────────────────────────────────────────────╮
│ Step 3/5: LINTING (Auto-triggered)                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Running markdown linter on updated files...                 │
│                                                             │
│ Found violations in 3 files:                                │
│                                                             │
│ File 1/3: CLAUDE.md                                         │
│   • 2 MD030 violations (list spacing)                       │
│   • 1 MD004 violation (list style)                          │
│                                                             │
│ Auto-fix these violations? [y/N/preview]                    │
│ > y                                                         │
│                                                             │
│ ✓ Fixed CLAUDE.md (3 violations)                            │
│                                                             │
│ File 2/3: README.md                                         │
│   • 1 MD032 violation (blank lines around lists)            │
│                                                             │
│ Auto-fix this violation? [y/N]                              │
│ > N                                                         │
│                                                             │
│ Skipped README.md                                           │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```text

## When Invoked

### Step 1: Smart Detection (sync)

**Standard Mode:**

```bash
# Analyze recent changes
git diff --name-only HEAD~10
git log --oneline -10

# Classify what docs are needed
# (uses scoring algorithm from doc-classifier)
```text

**Interactive Mode:**

```bash
# Run all 9 detection categories
python3 utils/docs_detector.py
python3 utils/help_file_validator.py

# Group results by category
# Prepare prompts with counts and examples
```text

```text
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
```text

### Step 2: Generate Documentation

For each doc type that scored >= 3:

```text
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
```text

### Step 3: Validate & Fix (check)

```text
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
```text

### Step 4: Update Changelog (if commits)

```text
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
```text

### Step 5: Summary

```text
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
│ Interactive Updates (Category-level):                       │
│   • Version refs: 12 updated                                │
│   • Command counts: 4 updated                               │
│   • Broken links: 3 fixed                                   │
│   • GIFs: 2 regenerated                                     │
│   • Help files: 5 updated                                   │
│                                                             │
│ Validated:                                                  │
│   • 3 issues auto-fixed                                     │
│   • 0 manual fixes needed                                   │
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ NEXT STEPS:                                                 │
│                                                             │
│ 1. Review changes:                                          │
│    git diff                                                 │
│                                                             │
│ 2. Preview docs:                                            │
│    mkdocs serve                                             │
│                                                             │
│ 3. Commit:                                                  │
│    git add docs/ mkdocs.yml CLAUDE.md README.md CHANGELOG.md│
│    git commit -m "docs: add session tracking documentation" │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```text

## Feature-Specific Mode

When a feature name is provided, the cycle is scoped:

```bash
/craft:docs:update "auth"
```text

```text
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
```text

## Flags Reference

| Flag | Effect |
|------|--------|
| (none) | Smart detection → generate needed → check → changelog |
| `"feature"` | Scope to specific feature |
| `--interactive`, `-i` | **NEW:** Category-level prompts for each update type |
| `--category=NAME`, `-C` | **NEW:** Update only specific category (see categories above) |
| `--auto-yes` | **NEW:** Non-interactive, auto-approve all updates |
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
/craft:docs:update --interactive --category=help_files  # Only help file prompts
```text

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
- `/craft:docs:lint` - **NEW:** Markdown linting with auto-fix
- `/craft:docs:changelog` - Changelog updates
- `/craft:docs:claude-md` - CLAUDE.md updates
- `/craft:docs:nav-update` - mkdocs navigation

**Uses utilities:**

- `utils/docs_detector.py` - **NEW:** 9 category detection system
- `utils/help_file_validator.py` - **NEW:** Comprehensive help validation
- `utils/complexity_scorer.py` - Task complexity scoring

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
6. **Interactive control** - **NEW:** Category-level prompts for transparency
7. **Batch operations** - **NEW:** Group identical changes, single prompt per category
8. **Preview mode** - **NEW:** See changes before applying

---

## Implementation Instructions

When this command is invoked with `--interactive` or `-i`:

### Phase 1: Detection

Run both utilities to detect issues:

```bash
# Run detector
python3 utils/docs_detector.py . v2.5.1

# Run validator
python3 utils/help_file_validator.py .
```text

Or use Python API:

```python
from utils.docs_detector import DocsDetector
from utils.help_file_validator import HelpFileValidator, IssueType

# Initialize
detector = DocsDetector('.')
validator = HelpFileValidator('.')

# Run detection
current_version = "v2.5.1"  # Get from .STATUS or args
detection_results = detector.detect_all(current_version)
validation_issues = validator.validate_all()
```text

### Phase 2: Group Categories

Group detected issues for interactive prompts:

```python
# Detection results structure:
# detection_results = {
#     'version_refs': DetectionResult(...),
#     'command_counts': DetectionResult(...),
#     'broken_links': DetectionResult(...),
#     'stale_examples': DetectionResult(...),
#     'missing_help': DetectionResult(...),
#     'outdated_status': DetectionResult(...),
#     'inconsistent_terms': DetectionResult(...),
#     'missing_xrefs': DetectionResult(...),
#     'outdated_diagrams': DetectionResult(...)
# }

# Group by priority
high_priority = ['version_refs', 'command_counts', 'broken_links']
medium_priority = ['missing_help', 'outdated_status', 'inconsistent_terms']
low_priority = ['stale_examples', 'missing_xrefs', 'outdated_diagrams']

# Filter categories with issues
categories_with_issues = [
    (key, result) for key, result in detection_results.items()
    if result.found and result.count > 0
]
```text

### Phase 3: Interactive Prompts

Use `AskUserQuestion` for each category group (max 4 questions per prompt):

```python
# Example: Version references category
version_result = detection_results['version_refs']

if version_result.found:
    # Prepare summary
    summary = f"Found {version_result.count} version references to update"
    examples = version_result.items[:3]  # Show first 3

    # Build question
    question = f"{summary}\n\nUpdate version from X to {current_version} in:\n"
    for item in examples:
        question += f"  • {item['file']} (line {item['line']})\n"
    if version_result.count > 3:
        question += f"  ... and {version_result.count - 3} more files\n"

    # Use AskUserQuestion tool
    response = AskUserQuestion({
        "questions": [{
            "question": "Should I update these version references?",
            "header": "Version Refs",
            "multiSelect": false,
            "options": [
                {
                    "label": "Yes, update all",
                    "description": f"Update {version_result.count} files to {current_version}"
                },
                {
                    "label": "Preview changes first",
                    "description": "Show detailed diff before applying"
                },
                {
                    "label": "Skip this category",
                    "description": "Leave version references unchanged"
                }
            ]
        }]
    })
```text

**Grouping Strategy:**

Group related categories into single prompts (max 4 questions):

- **Prompt 1:** Version refs + Command counts (metadata updates)
- **Prompt 2:** Broken links + Missing cross-refs (link issues)
- **Prompt 3:** Missing help + Outdated status (documentation completeness)
- **Prompt 4:** Stale examples + Inconsistent terminology (content quality)

### Phase 4: Apply Updates

Based on user responses, apply selected updates:

```python
# Example: Apply version reference updates
if user_selected_version_refs:
    for item in version_result.items:
        file_path = item['file']
        old_version = item['old_version']
        new_version = item['new_version']

        # Read file
        content = read_file(file_path)

        # Replace old version with new
        updated = content.replace(old_version, new_version)

        # Write back
        write_file(file_path, updated)
```text

**Update Strategies by Category:**

| Category | Update Method |
|----------|---------------|
| `version_refs` | String replacement (regex: `v?\d+\.\d+\.\d+`) |
| `command_counts` | String replacement (e.g., "99 commands" → "101 commands") |
| `broken_links` | Fix file paths, update anchors |
| `missing_help` | Add YAML frontmatter to command files |
| `outdated_status` | Change status markers (WIP → Complete) |
| `inconsistent_terms` | Replace with canonical form |
| `missing_xrefs` | Add related command links |
| `stale_examples` | Update code snippets |
| `outdated_diagrams` | Regenerate Mermaid diagrams |

### Phase 5: Summary Report

Generate ADHD-friendly summary:

```text
╭─────────────────────────────────────────────────────────────╮
│ ✅ DOCUMENTATION UPDATE COMPLETE (Interactive Mode)         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Categories Updated:                                         │
│   ✓ Version references: 12 files updated                    │
│   ✓ Command counts: 4 files updated                         │
│   ✓ Broken links: 3 fixed                                   │
│   ⊘ Missing help: Skipped by user                           │
│                                                             │
│ Files Modified: 19                                          │
│ Total Changes: 35 updates                                   │
│                                                             │
│ Next Steps:                                                 │
│   1. Review changes: git diff                               │
│   2. Run tests: /craft:test:run                             │
│   3. Commit: git add . && git commit                        │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```text

### Flags Handling

- `--interactive`, `-i`: Enable interactive mode (described above)
- `--category=NAME`, `-C NAME`: Filter to single category
- `--auto-yes`: Skip prompts, apply all updates
- `--dry-run`: Show what would be updated without applying

### Error Handling

```python
try:
    # Run detection
    results = detector.detect_all(current_version)
except Exception as e:
    print(f"⚠️ Detection failed: {e}")
    print("Run manually: python3 utils/docs_detector.py . v2.5.1")
    return

# Validate results
if not results:
    print("✅ No documentation issues found")
    return

# Continue with interactive prompts...
```text

### Testing

Before deploying, test with:

```bash
# Test detection
python3 utils/docs_detector.py . v2.5.1

# Test validation
python3 utils/help_file_validator.py .

# Test integration
python3 tests/test_docs_utilities.py
```text

All 7 integration tests should pass.
