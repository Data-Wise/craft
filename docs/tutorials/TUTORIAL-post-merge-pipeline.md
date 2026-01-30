# Tutorial: Post-Merge Documentation Pipeline

> **What you'll learn:** How to use the `--post-merge` flag to automatically update documentation after merging a PR.
>
> **Level:** Intermediate
>
> **Time:** 10-15 minutes
>
> **Prerequisites:** Basic understanding of git workflows and PR merging

---

## What You'll Learn

1. When to use the post-merge pipeline
2. What gets auto-fixed vs what requires manual input
3. How to handle each of the 9 detection categories
4. How to validate results and commit changes
5. Troubleshooting common issues

---

## Overview

After merging a feature PR, documentation often needs updates across multiple files: version numbers, command counts, navigation entries, help files, and more. The post-merge pipeline automates 90% of this work.

**The 5-Phase Pipeline:**

```
Phase 1: Auto-detect (9 categories)
Phase 2: Auto-fix safe categories (no prompts)
Phase 3: Prompt for manual categories
Phase 4: Lint + validate
Phase 5: Summary
```

---

## Part 1: When to Use --post-merge

### Scenario: You Just Merged a PR

```bash
# You just merged PR #42 "feat: add authentication system"
git checkout dev
git pull origin dev

# Run the post-merge pipeline
/craft:docs:update --post-merge
```

### What Triggers Auto-Detection

The pipeline scans the merge commit and detects:

- **Version references** — Mentions of old version numbers
- **Command counts** — "97 commands" when you now have 100
- **Navigation entries** — New pages not in mkdocs.yml
- **Broken links** — Changed file paths
- **Help files** — New commands without help docs
- **Tutorials** — Features without step-by-step guides
- **Changelog** — PR description should be in CHANGELOG.md
- **GIF regeneration** — Changed commands need new GIF demos
- **Feature status** — New features to add to status matrix

---

## Part 2: Phase 1 - Detection

### Step 2.1: Read the Detection Report

After running `/craft:docs:update --post-merge`, you'll see a categorized report:

```
Post-Merge Documentation Scan:
  Merge: PR #42 "feat: add auth system" → dev
  Changed files: 15
  New commands: 3
  Commits analyzed: 8

  Detected categories:

  [AUTO]   Version references — 12 files need "v2.8.1" → "v2.9.0"
  [AUTO]   Command counts — 4 files have outdated "97 commands"
  [AUTO]   Navigation entries — 2 new pages need mkdocs.yml entries
  [AUTO]   Broken links — 1 link to renamed file

  [MANUAL] Help files — 3 new commands need documentation
  [MANUAL] Changelog draft — PR description → CHANGELOG.md

  [SKIP]   GIF regeneration — no changed commands with GIFs
  [SKIP]   Tutorials — feature already has tutorial
  [SKIP]   Feature status — not a new feature category
```

**Key insight:** `[AUTO]` categories will be fixed automatically in Phase 2. `[MANUAL]` categories will prompt you in Phase 3.

---

## Part 3: Phase 2 - Auto-Fix

### Step 3.1: Auto-Fix Runs Silently

No prompts are shown for safe categories:

```
Auto-fixing safe categories...

  Version references:
    ✓ docs/index.md: v2.8.1 → v2.9.0
    ✓ CLAUDE.md: v2.8.1 → v2.9.0
    ✓ mkdocs.yml: v2.8.1 → v2.9.0
    ... 9 more files

  Command counts:
    ✓ docs/index.md: 97 → 100 commands
    ✓ CLAUDE.md: 97 → 100 commands
    ✓ README.md: 97 → 100 commands
    ✓ mkdocs.yml site description: 97 → 100

  Navigation entries:
    ✓ mkdocs.yml: Added docs/commands/auth/login.md
    ✓ mkdocs.yml: Added docs/commands/auth/logout.md

  Broken links:
    ✓ docs/guide/workflows.md: old-name.md → new-name.md

  Auto-fixed: 4 categories (19 files changed)
```

**What's happening behind the scenes:**

| Category | How it works |
|----------|--------------|
| **Version references** | Regex find-replace across all markdown files |
| **Command counts** | Count `commands/**/*.md` files, update all mentions |
| **Navigation entries** | Parse mkdocs.yml, insert new entries in sorted order |
| **Broken links** | Track file renames in git, update all references |

---

## Part 4: Phase 3 - Manual Categories

### Step 4.1: Help File Generation

Now you're prompted for categories requiring judgment:

```
? 3 new commands need help documentation. How should I handle them?
  > Generate all (Recommended)
    Generate one at a time
    Show me the commands first
    Skip for now
```

**Recommendation:** Choose "Generate all" for consistency.

If you select "Generate all":

```
Generating help files...
  ✓ docs/commands/auth/login.md (185 lines)
  ✓ docs/commands/auth/logout.md (142 lines)
  ✓ docs/commands/auth/status.md (167 lines)

Template used: templates/docs/HELP-PAGE-TEMPLATE.md
Generated: 3 files (494 lines total)
```

### Step 4.2: Changelog Update

```
? PR #42 description contains changelog-worthy content. Add to CHANGELOG.md?
  > Yes - Add to Unreleased section (Recommended)
    Yes - Add to v2.9.0 section
    Let me review PR description first
    Skip
```

**What happens:**

```
Updating CHANGELOG.md...
  ✓ Extracted from PR #42 description
  ✓ Added to ## [Unreleased] section
  ✓ Formatted as markdown list

Added:
  - **Authentication System** - OAuth 2.0 support with PKCE
    - New commands: /craft:auth:login, /craft:auth:logout, /craft:auth:status
    - JWT token management with refresh
    - Session persistence
```

### Step 4.3: Tutorial Generation

If the feature is complex enough:

```
? "Authentication System" scores 8/10 for tutorial need. Generate tutorial?
  > Yes - Create step-by-step tutorial (Recommended)
    No - Feature is self-explanatory
    Let me see the score breakdown
```

If you choose "Yes":

```
Generating tutorial...
  Analyzing: commands/auth/*.md
  Template: templates/docs/TUTORIAL-TEMPLATE.md

  ✓ docs/tutorials/TUTORIAL-auth-setup.md (850 lines)
    - What you'll learn section
    - Prerequisites
    - 6-part progressive tutorial
    - Troubleshooting
    - Next steps

Generated: 1 tutorial (850 lines)
```

---

## Part 5: Phases 4-5 - Validation and Summary

### Step 5.1: Validation

```
Validating changes...

  Markdown lint:
    ✓ Checked 25 files
    ✓ Fixed 3 MD032 violations (list spacing)
    ✓ 0 unfixable issues

  Internal links:
    ✓ Checked 847 links
    ✓ All internal links resolve
    ✓ 2 external links skipped

  Count validation:
    ✓ Command count matches filesystem (100)
    ✓ Agent count matches (8)
    ✓ Skill count matches (21)

Validation: PASS
```

### Step 5.2: Final Summary

```
┌─────────────────────────────────────────────────────────────┐
│ ✅ POST-MERGE DOCUMENTATION COMPLETE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Auto-fixed: 4 categories (19 files)                         │
│   • Version references (12 files)                           │
│   • Command counts (4 files)                                │
│   • Navigation entries (2 additions)                        │
│   • Broken links (1 fix)                                    │
│                                                             │
│ Manual: 2 categories (4 files)                              │
│   • Help files (3 new)                                      │
│   • Changelog (1 update)                                    │
│                                                             │
│ Skipped: 3 categories                                       │
│   • GIF regeneration (no changed commands)                  │
│   • Tutorials (feature has tutorial)                        │
│   • Feature status (not a feature category)                 │
│                                                             │
│ Total: 23 files changed                                     │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ NEXT STEPS:                                                 │
│                                                             │
│ 1. Review changes:                                          │
│    git diff                                                 │
│                                                             │
│ 2. Test docs build:                                         │
│    mkdocs build                                             │
│                                                             │
│ 3. Commit:                                                  │
│    git commit -m "docs: post-merge updates for PR #42"      │
│                                                             │
│ 4. Deploy (optional):                                       │
│    /craft:site:deploy                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Part 6: Dry Run Mode

### Step 6.1: Preview Before Applying

Want to see what would change without actually changing it?

```bash
/craft:docs:update --post-merge --dry-run
```

**Output:**

```
[DRY RUN] Post-Merge Documentation Scan:

  Would auto-fix:
    • 12 version references
    • 4 command count mentions
    • 2 navigation entries
    • 1 broken link

  Would prompt for:
    • 3 help files
    • 1 changelog update

  Would skip:
    • GIF regeneration
    • Tutorials
    • Feature status

No files were modified. Re-run without --dry-run to apply.
```

---

## Part 7: Troubleshooting

### Issue: "No changes detected"

**Cause:** The merge commit didn't introduce detectable changes.

**Solution:**

```bash
# Force detection with explicit file scanning
/craft:docs:update --post-merge --force

# Or manually specify categories
/craft:docs:update --category=version_refs --category=command_counts
```

### Issue: "Auto-fix failed for version references"

**Cause:** Ambiguous version strings or non-standard formatting.

**Solution:**

```bash
# Check what it tried to replace
git diff

# Manually fix any missed occurrences, then re-run
/craft:docs:update --post-merge --category=version_refs
```

### Issue: "Help file generation created duplicates"

**Cause:** Command already had a help file.

**Solution:**

```bash
# Revert the duplicates
git checkout -- docs/commands/duplicate.md

# Skip help file generation
# Next time, choose "Skip for now" when prompted
```

---

## Part 8: Category Reference

### Safe Categories (Auto-Fix)

These are always safe to auto-fix without prompts:

| Category | What changes | Risk |
|----------|-------------|------|
| **Version references** | v2.8.1 → v2.9.0 across all docs | None — simple string replace |
| **Command counts** | "97 commands" → "100 commands" | None — calculated from filesystem |
| **Navigation entries** | Add new pages to mkdocs.yml | None — alphabetically inserted |
| **Broken links** | Fix renamed file references | None — tracked via git |

### Manual Categories (Require Prompts)

These need human judgment:

| Category | Why manual | Example |
|----------|-----------|---------|
| **Help files** | Template choice, content structure | Use short or long template? |
| **Tutorials** | Scope and depth | 5 steps or 10 steps? |
| **Changelog** | Categorization, wording | Feature or enhancement? |
| **GIF regeneration** | Which commands, recording setup | Need terminal setup first |
| **Feature status** | Completeness percentage, notes | 80% or 90% complete? |

---

## Summary

You've learned:

- When to run `--post-merge` (after merging a PR to dev)
- What the 5-phase pipeline does (detect, auto-fix, prompt, validate, summarize)
- Which categories are safe for auto-fix (version, counts, nav, links)
- How to handle manual categories (help, changelog, tutorials)
- How to use dry-run mode to preview changes
- How to troubleshoot common issues

---

## Next Steps

- **Command reference:** [/craft:docs:update](../commands/docs/update.md) — Full flag documentation
- **Pattern guide:** [Interactive Commands Guide](../guide/interactive-commands.md) — How this pattern works across all commands
- **Advanced:** [Documentation Quality Guide](../guide/documentation-quality.md) — Best practices for documentation
- **Quick reference:** [Docs Update Refcard](../reference/REFCARD-DOCS-UPDATE.md) — All flags and options
