# Interactive Documentation Update - Example Walkthrough

This example demonstrates the `/craft:docs:update --interactive` workflow from detection through completion.

## Initial State

Project: craft v2.5.1
Recent changes:

- Added 2 new commands
- Updated orchestrator mode selection
- Fixed 3 broken links

## Step 1: User Invocation

```bash
/craft:docs:update --interactive
```text

## Step 2: Detection Phase

Claude runs both utilities:

```python
from utils.docs_detector import DocsDetector
from utils.help_file_validator import HelpFileValidator

detector = DocsDetector('.')
validator = HelpFileValidator('.')

detection_results = detector.detect_all("v2.5.1")
validation_issues = validator.validate_all()
```text

**Detection Results:**

```text
Version References: 12 items need updating
Command Counts: 4 items need updating
Broken Links: 3 items need fixing
Missing Help: 5 commands need help
Outdated Status: 2 items need updating
```text

## Step 3: Interactive Prompts

### Prompt 1: Metadata Updates

Claude uses `AskUserQuestion`:

```text
╭─────────────────────────────────────────────────────────────╮
│ Documentation Updates Available                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Question 1/4: Version References (12 items)                 │
│                                                             │
│ Should I update version references?                         │
│   Option A: Yes, update all (12 files → v2.5.1)            │
│   Option B: Preview changes first                           │
│   Option C: Skip this category                              │
│                                                             │
│ Question 2/4: Command Counts (4 items)                      │
│                                                             │
│ Should I update command counts?                             │
│   Option A: Yes, update all (99 → 101 commands)            │
│   Option B: Preview changes first                           │
│   Option C: Skip this category                              │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```text

**User Response:** A, A (update both)

### Prompt 2: Link Issues

```text
╭─────────────────────────────────────────────────────────────╮
│ Link Validation Issues                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Question 1/2: Broken Links (3 items)                        │
│                                                             │
│ Should I fix these broken links?                            │
│   • docs/guide/old-feature.md → guide/features.md           │
│   • commands/legacy.md (file doesn't exist)                 │
│   • README.md → #missing-anchor                             │
│                                                             │
│   Option A: Yes, fix all (3 broken links)                   │
│   Option B: Fix one-by-one                                  │
│   Option C: Skip this category                              │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```text

**User Response:** A (fix all)

### Prompt 3: Documentation Completeness

```text
╭─────────────────────────────────────────────────────────────╮
│ Documentation Completeness                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Question 1/2: Missing Help (5 commands)                     │
│                                                             │
│ Should I add help documentation?                            │
│   Commands without help:                                    │
│   • /craft:test:debug                                       │
│   • /craft:test:watch                                       │
│   • /craft:git:worktree                                     │
│   • /craft:hub                                              │
│   • /craft:discovery-usage                                  │
│                                                             │
│   Option A: Yes, add all (5 commands)                       │
│   Option B: Select specific commands                        │
│   Option C: Skip this category                              │
│                                                             │
│ Question 2/2: Outdated Status (2 items)                     │
│                                                             │
│ Should I update status markers?                             │
│   • Feature X: WIP → Complete                               │
│   • Feature Y: Draft → Active                               │
│                                                             │
│   Option A: Yes, update all                                 │
│   Option B: Skip this category                              │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```text

**User Response:** C, A (skip help, update status)

## Step 4: Applying Updates

Claude applies selected updates:

```text
╭─────────────────────────────────────────────────────────────╮
│ Applying Updates...                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ✓ Version References: 12 files updated                      │
│   README.md, CLAUDE.md, docs/guide/installation.md, ...     │
│                                                             │
│ ✓ Command Counts: 4 files updated                           │
│   README.md, CLAUDE.md, docs/architecture.md, ...           │
│                                                             │
│ ✓ Broken Links: 3 fixed                                     │
│   docs/guide/old-feature.md → guide/features.md             │
│   commands/legacy.md → commands/current.md                  │
│   README.md anchor fixed                                    │
│                                                             │
│ ⊘ Missing Help: Skipped by user                             │
│                                                             │
│ ✓ Outdated Status: 2 updated                                │
│   Feature X: WIP → Complete                                 │
│   Feature Y: Draft → Active                                 │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```text

## Step 5: Summary Report

```text
╭─────────────────────────────────────────────────────────────╮
│ ✅ DOCUMENTATION UPDATE COMPLETE                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Interactive Mode Summary:                                   │
│                                                             │
│ Categories Processed:                                       │
│   ✓ Version references: 12 files updated                    │
│   ✓ Command counts: 4 files updated                         │
│   ✓ Broken links: 3 fixed                                   │
│   ⊘ Missing help: Skipped by user                           │
│   ✓ Outdated status: 2 updated                              │
│                                                             │
│ Files Modified: 21                                          │
│ Total Changes: 41 updates                                   │
│ Time: 2.3 seconds                                           │
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ NEXT STEPS:                                                 │
│                                                             │
│ 1. Review changes:                                          │
│    git diff                                                 │
│                                                             │
│ 2. Run tests:                                               │
│    /craft:test:run                                          │
│                                                             │
│ 3. Commit:                                                  │
│    git add .                                                │
│    git commit -m "docs: update version refs, counts, links" │
│                                                             │
│ 4. Remaining tasks:                                         │
│    • 5 commands still need help documentation               │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```text

## Alternative Scenarios

### Scenario A: Category-Specific Update

```bash
/craft:docs:update --interactive --category=broken_links
```text

Only prompts for broken links category, skips others.

### Scenario B: Auto-Yes Mode

```bash
/craft:docs:update --auto-yes
```text

Applies all updates without prompts (use with caution).

### Scenario C: Dry-Run Preview

```bash
/craft:docs:update --interactive --dry-run
```text

Shows what would be updated without applying changes.

## Implementation Notes

1. **Grouping Logic:** Related categories are grouped into single prompts (max 4 questions each)
2. **Preview Support:** Users can request detailed preview before applying
3. **Selective Updates:** Users can choose specific items within categories
4. **Error Handling:** Failed updates are reported but don't block other categories
5. **Rollback:** Changes are applied atomically per category (can revert if needed)

## Testing

Validate the workflow:

```bash
# Test utilities
python3 tests/test_docs_utilities.py

# Test interactive command (dry-run)
/craft:docs:update --interactive --dry-run

# Test specific category
/craft:docs:update --interactive --category=version_refs

# Test auto-yes
/craft:docs:update --auto-yes --dry-run
```text

All 7 integration tests should pass before deployment.
