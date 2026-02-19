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
```

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
```

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
```

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
```

## Feature-Specific Mode

Scope to a specific feature:

```bash
# Document "sessions" feature
/craft:docs:update "sessions"

# Document "auth" system
/craft:docs:update "auth"
```

## Post-Merge Pipeline (NEW)

After merging a PR, use `--post-merge` to automatically update documentation:

```bash
# Full pipeline
/craft:docs:update --post-merge

# Preview only
/craft:docs:update --post-merge --dry-run
```

### The 5-Phase Pipeline

```text
Phase 1: Auto-detect (9 categories)
Phase 2: Auto-fix safe categories (no prompts)
Phase 3: Prompt for manual categories
Phase 4: Lint + validate
Phase 5: Summary
```

### Safe vs Manual Categories

| Category | Auto-Fix | Requires Prompt |
|----------|:--------:|:---------------:|
| Version references | ✅ | |
| Command counts | ✅ | |
| Navigation entries | ✅ | |
| Broken links | ✅ | |
| Help files | | ✅ |
| Tutorials | | ✅ |
| Changelog | | ✅ |
| GIF regeneration | | ✅ |
| Feature status | | ✅ |

### Post-Merge Workflow

```bash
# 1. Merge PR
gh pr merge 42

# 2. Pull changes
git checkout dev && git pull origin dev

# 3. Run post-merge pipeline
/craft:docs:update --post-merge

# 4. Review changes
git diff

# 5. Test docs build
mkdocs build

# 6. Commit
git commit -m "docs: post-merge updates for PR #42"

# 7. Deploy (optional)
/craft:site:deploy
```

### Sample Output

```text
Post-Merge Documentation Scan:
  Merge: PR #42 "feat: add auth system" → dev

  [AUTO] Version references — 12 files
  [AUTO] Command counts — 4 files
  [AUTO] Navigation entries — 2 pages
  [MANUAL] Help files — 3 commands
  [SKIP] GIF regeneration — no changed commands

Auto-fixing... ✅ (19 files changed)

? 3 new commands need help. How to handle?
  > Generate all (Recommended)

Generating... ✅ (3 files created)

Post-Merge Complete:
  Auto-fixed: 4 categories (19 files)
  Manual: 1 category (3 files)
  Total: 22 files changed
```

## Advanced Usage

### Preview + Apply Workflow

```bash
# 1. Preview all changes
/craft:docs:update --interactive --dry-run

# 2. Review output
# (shows what would change)

# 3. Apply if satisfied
/craft:docs:update --interactive
```

### Batch Mode

```bash
# Apply all updates without prompts
/craft:docs:update --auto-yes

# Combine with category filter
/craft:docs:update --auto-yes --category=version_refs
```

### Custom Generation

```bash
# Force specific doc types
/craft:docs:update "feature" --with-tutorial
/craft:docs:update --with-help --with-workflow

# Generate everything
/craft:docs:update --all

# Lower threshold for more docs
/craft:docs:update --threshold 2
```

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
│   2. Test: /craft:test                      │
│   3. Commit: git commit                         │
│                                                 │
╰─────────────────────────────────────────────────╯
```

## Utilities Used

### Detection System

```bash
# Standalone detection
python3 utils/docs_detector.py . v2.5.1

# Standalone validation
python3 utils/help_file_validator.py .
```

### Integration Tests

```bash
# Run utility tests
python3 tests/test_docs_utilities.py

# Expected: 7/7 tests passing
```

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
- [Implementation Summary](../specs/_archive/SPEC-docs-update-interactive-2026-01-22.md) - Technical details
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
