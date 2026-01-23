# Quick Reference: /craft:docs:update

**One command for all documentation updates** - Smart detection, interactive prompts, automatic fixes.

## Quick Start

```bash
# Interactive mode (recommended for first use)
/craft:docs:update --interactive

# Preview before applying
/craft:docs:update --interactive --dry-run

# Update specific category
/craft:docs:update --category=version_refs

# Auto-apply everything (use with caution)
/craft:docs:update --auto-yes
```text

## Detection Categories (9 Total)

| Category | What It Detects | Example |
|----------|-----------------|---------|
| `version_refs` | Old version numbers | v1.24.0 → v2.5.1 |
| `command_counts` | Outdated counts | "99 commands" → "101 commands" |
| `broken_links` | Dead internal links | docs/old.md → docs/new.md |
| `stale_examples` | Outdated code snippets | API calls with old syntax |
| `missing_help` | Commands without YAML | 60 commands need frontmatter |
| `outdated_status` | Wrong status markers | WIP → Complete |
| `inconsistent_terms` | Terminology mismatches | craft vs Craft |
| `missing_xrefs` | Missing cross-refs | No "See also" sections |
| `outdated_diagrams` | Stale Mermaid diagrams | Architecture changed |

## Interactive Mode

### Workflow

```text
1. Detection    → Scan 9 categories
2. Prompts      → Group into 2-4 questions each
3. Preview      → Show what would change
4. Apply        → Update approved categories
5. Summary      → Report changes made
```text

### Sample Prompt

```text
╭─────────────────────────────────────────────────╮
│ Documentation Updates Available                 │
├─────────────────────────────────────────────────┤
│                                                 │
│ Version References (545 items)                  │
│ Should I update version references?             │
│                                                 │
│   A) Yes, update all (545 files → v2.5.1)      │
│   B) Preview changes first                      │
│   C) Skip this category                         │
│                                                 │
╰─────────────────────────────────────────────────╯
```text

## Common Flags

| Flag | Effect | When to Use |
|------|--------|-------------|
| `--interactive` | Category-level prompts | First time, want control |
| `--dry-run` | Preview without changes | Verify before applying |
| `--category=NAME` | Update one category | Focus on specific issue |
| `--auto-yes` | Skip all prompts | Confident, batch mode |
| `--force` | Generate all docs | After major changes |
| `--no-check` | Skip validation | Speed over safety |

## Category-Specific Mode

Update individual categories:

```bash
# Version references only
/craft:docs:update --category=version_refs

# Help files only
/craft:docs:update --category=missing_help

# Command counts only
/craft:docs:update --category=command_counts
```text

## Feature-Specific Mode

Scope to a specific feature:

```bash
# Document "sessions" feature
/craft:docs:update "sessions"

# Document "auth" system
/craft:docs:update "auth"
```text

## Advanced Usage

### Preview + Apply Workflow

```bash
# 1. Preview all changes
/craft:docs:update --interactive --dry-run

# 2. Review output
# (shows what would change)

# 3. Apply if satisfied
/craft:docs:update --interactive
```text

### Batch Mode

```bash
# Apply all updates without prompts
/craft:docs:update --auto-yes

# Combine with category filter
/craft:docs:update --auto-yes --category=version_refs
```text

### Custom Generation

```bash
# Force specific doc types
/craft:docs:update "feature" --with-tutorial
/craft:docs:update --with-help --with-workflow

# Generate everything
/craft:docs:update --all

# Lower threshold for more docs
/craft:docs:update --threshold 2
```text

## Output Example

```text
╭─────────────────────────────────────────────────╮
│ ✅ DOCUMENTATION UPDATE COMPLETE                │
├─────────────────────────────────────────────────┤
│                                                 │
│ Interactive Mode Summary:                       │
│                                                 │
│ Categories Processed:                           │
│   ✓ Version references: 12 files updated        │
│   ✓ Command counts: 4 files updated             │
│   ✓ Broken links: 3 fixed                       │
│   ⊘ Missing help: Skipped by user               │
│                                                 │
│ Files Modified: 19                              │
│ Total Changes: 35 updates                       │
│ Time: 2.3 seconds                               │
│                                                 │
│ Next Steps:                                     │
│   1. Review: git diff                           │
│   2. Test: /craft:test:run                      │
│   3. Commit: git commit                         │
│                                                 │
╰─────────────────────────────────────────────────╯
```text

## Utilities Used

### Detection System

```bash
# Standalone detection
python3 utils/docs_detector.py . v2.5.1

# Standalone validation
python3 utils/help_file_validator.py .
```text

### Integration Tests

```bash
# Run utility tests
python3 tests/test_docs_utilities.py

# Expected: 7/7 tests passing
```text

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Detection | ~2s | Scans entire project |
| Prompts | ~30s | User-dependent |
| Apply (545 updates) | ~3s | String replacements |
| **Total** | **~35s** | For interactive mode |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Too many changes | Use `--category` to focus |
| Not sure what changed | Use `--dry-run` first |
| Want to undo | Use git to revert: `git checkout .` |
| Missing utilities | Check: `ls utils/docs_detector.py` |
| Tests failing | Run: `python3 tests/test_docs_utilities.py` |

## Integration

**Works with:**

- `/craft:docs:sync` - Change detection
- `/craft:docs:check` - Validation
- `/craft:docs:lint` - Markdown linting
- `/craft:check` - Pre-flight validation

**Orchestrated internally:**

- `/craft:docs:guide` - Guide generation
- `/craft:docs:changelog` - Changelog updates
- `/craft:docs:claude-md` - CLAUDE.md updates
- `/craft:docs:nav-update` - Navigation updates

## See Also

- [Full Documentation](../commands/docs/update.md) - Complete command reference
- [Example Walkthrough](../examples/docs-update-interactive-example.md) - Step-by-step example
- [Implementation Summary](../specs/IMPLEMENTATION-SUMMARY-docs-update-interactive.md) - Technical details
- [Teaching Workflow Guide](../guide/teaching-workflow.md) - Teaching mode integration

## Quick Tips

1. **First time?** Use `--interactive --dry-run` to preview
2. **Not sure?** Start with one category: `--category=version_refs`
3. **Confident?** Use `--auto-yes` for batch updates
4. **Want control?** Interactive mode prompts for each category
5. **Made mistake?** Git can revert: `git checkout <file>`

---

**Version:** 2.6.0
**Status:** Production Ready
**Test Coverage:** 7/7 integration tests passing
**Real Issues Found:** 1,331 documentation problems detected
