# Tutorial: Interactive Documentation Updates

**Learn how to use `/craft:docs:update --interactive` to fix documentation issues across your project.**

**Time:** 10-15 minutes
**Difficulty:** Beginner
**Prerequisites:** craft plugin installed

## What You'll Learn

- How to detect documentation issues automatically
- How to use interactive prompts to choose what to fix
- How to preview changes before applying them
- How to update specific categories independently

## Why Interactive Mode?

Traditional documentation updates require:

1. Manually finding issues
2. Deciding what to fix
3. Editing files one by one
4. Hoping you didn't break anything

**Interactive mode does all of this automatically** while giving you control at each step.

## Tutorial Overview

```text
Step 1: Preview (Dry-Run)        [5 min]
Step 2: Interactive Update       [5 min]
Step 3: Verify Changes           [3 min]
Step 4: Category-Specific Mode   [3 min]
```

---

## Step 1: Preview What Would Change (Dry-Run)

First, let's see what documentation issues exist **without making any changes**.

### Run the Command

```bash
/craft:docs:update --interactive --dry-run
```

### What Happens

The system runs two detection utilities:

```text
╭─────────────────────────────────────────────────╮
│ DETECTING CHANGES                               │
├─────────────────────────────────────────────────┤
│                                                 │
│ Running detection utilities...                  │
│   ✓ docs_detector.py - Scanned 9 categories     │
│   ✓ help_file_validator.py - Validated help     │
│                                                 │
╰─────────────────────────────────────────────────╯
```

### Detection Results

You'll see issues grouped by category:

```text
Found issues in 6 categories:

  📦 Version References        545 items
  📊 Command Counts            289 items
  📝 Missing Help               60 items
  🏷️  Outdated Status            27 items
  📖 Inconsistent Terminology   44 items
  🔗 Missing Cross-References  366 items

Categories with no issues:
  ✓ Broken Links
  ✓ Stale Examples
  ✓ Outdated Diagrams
```

### Interactive Prompts (Preview)

You'll be prompted for each category group:

**Prompt 1: Metadata Updates**

```text
╭─────────────────────────────────────────────────╮
│ Version References (545 items)                  │
│ Should I update version references?             │
│                                                 │
│   A) Yes, update all (545 files → v2.5.1)      │
│   B) Preview changes first                      │
│   C) Skip this category                         │
╰─────────────────────────────────────────────────╯
```

**Try selecting different options** to see what each does:

- **Option A:** Shows what would be updated
- **Option B:** Shows detailed file list
- **Option C:** Skips to next category

### Preview Summary

At the end, you'll see:

```text
DRY RUN COMPLETE
Summary of Changes (No files modified)

Total Changes: 1,331 updates across 6 categories
Files That Would Be Modified: ~180 files

To apply these changes (without --dry-run):
  /craft:docs:update --interactive
```

**Key Point:** Nothing was changed! This was just a preview.

---

## Step 2: Apply Updates Interactively

Now let's actually fix some documentation issues.

### Run the Command (No --dry-run)

```bash
/craft:docs:update --interactive
```

### Choose What to Fix

This time, your selections will actually apply updates.

**Example Session:**

```text
Prompt 1: Version References
  Your answer: A (Yes, update all)
  ✓ Updated 545 version references

Prompt 2: Command Counts
  Your answer: A (Yes, update all)
  ✓ Updated 289 command counts

Prompt 3: Missing Help
  Your answer: C (Skip this category)
  ⊘ Skipped by user

... (other categories)
```

### Watch It Work

As each category is applied, you'll see progress:

```text
╭─────────────────────────────────────────────────╮
│ APPLYING UPDATES                                │
├─────────────────────────────────────────────────┤
│                                                 │
│ ✓ Version References (545 updates)              │
│   Updated files:                                │
│   • docs/VERSION-HISTORY.md (63 changes)        │
│   • README.md (35 changes)                      │
│   • CLAUDE.md (23 changes)                      │
│   ... and 64 more files                         │
│                                                 │
│ ✓ Command Counts (289 updates)                  │
│   Updated files:                                │
│   • CLAUDE.md (2 changes)                       │
│   • docs/architecture.md (4 changes)            │
│   ... and 30 more files                         │
│                                                 │
╰─────────────────────────────────────────────────╯
```

### Final Summary

```text
╭─────────────────────────────────────────────────╮
│ ✅ DOCUMENTATION UPDATE COMPLETE                │
├─────────────────────────────────────────────────┤
│                                                 │
│ Categories Updated:                             │
│   ✓ Version references: 545 updates             │
│   ✓ Command counts: 289 updates                 │
│   ⊘ Missing help: Skipped                       │
│                                                 │
│ Files Modified: 67                              │
│ Total Changes: 834 updates                      │
│ Time: 3.2 seconds                               │
│                                                 │
│ Next Steps:                                     │
│   1. Review: git diff                           │
│   2. Test: /craft:test:run                      │
│   3. Commit: git add . && git commit            │
│                                                 │
╰─────────────────────────────────────────────────╯
```

---

## Step 3: Verify Changes

Always review what was changed before committing.

### Check What Files Changed

```bash
git status
```

Output:

```text
modified:   README.md
modified:   CLAUDE.md
modified:   docs/VERSION-HISTORY.md
... (64 more files)
```

### Review Specific Changes

```bash
# See all changes
git diff

# See changes in one file
git diff README.md

# Count changes
git diff --stat
```

### Example Diff

```diff
- **Version:** v1.24.0
+ **Version:** v2.5.1

- craft has 99 commands
+ craft has 101 commands
```

### If Everything Looks Good

```bash
git add .
git commit -m "docs: update version refs and counts via interactive mode"
```

### If You Made a Mistake

```bash
# Undo all changes
git checkout .

# Undo changes in one file
git checkout README.md

# Then run interactive mode again
```

---

## Step 4: Category-Specific Updates

Sometimes you only want to fix one type of issue.

### Update Just Version References

```bash
/craft:docs:update --interactive --category=version_refs
```

**Benefits:**

- Faster (only scans one category)
- Focused (easier to review changes)
- Safer (less chance of unexpected changes)

### Example Output

```text
╭─────────────────────────────────────────────────╮
│ Category-Specific Mode: version_refs            │
├─────────────────────────────────────────────────┤
│                                                 │
│ Found: 545 version references to update         │
│ Target version: v2.5.1                          │
│                                                 │
│ Top files affected:                             │
│   • docs/VERSION-HISTORY.md (63 changes)        │
│   • README.md (35 changes)                      │
│   • CLAUDE.md (23 changes)                      │
│   ... and 64 more files                         │
│                                                 │
╰─────────────────────────────────────────────────╯
```

**Then you get a single prompt:**

```text
Apply 545 version reference updates to v2.5.1?

  A) Yes, update all
  B) Show detailed file list first
  C) Cancel - don't apply updates
```

### Try Other Categories

```bash
# Fix command counts
/craft:docs:update --category=command_counts

# Add missing help
/craft:docs:update --category=missing_help

# Fix broken links
/craft:docs:update --category=broken_links
```

---

## Advanced Tips

### Preview a Specific Category

Combine `--dry-run` with `--category`:

```bash
/craft:docs:update --interactive --category=version_refs --dry-run
```

This shows what would change for just version references.

### Auto-Apply (No Prompts)

If you're confident, skip all prompts:

```bash
/craft:docs:update --auto-yes
```

**⚠️ Warning:** This applies ALL updates without asking!

Better approach:

```bash
# Dry-run first
/craft:docs:update --dry-run

# Then auto-apply if it looks good
/craft:docs:update --auto-yes
```

### Batch Update Multiple Categories

Update several categories at once:

```bash
# Update metadata categories
/craft:docs:update --interactive --category=version_refs
/craft:docs:update --interactive --category=command_counts

# Review changes
git diff

# Commit both
git commit -m "docs: update metadata (versions and counts)"
```

---

## Common Scenarios

### Scenario 1: After Version Bump

You just released v2.5.1 and need to update all docs:

```bash
# Update version references
/craft:docs:update --category=version_refs --auto-yes

# Update command counts (if commands added)
/craft:docs:update --category=command_counts --auto-yes
```

### Scenario 2: Documentation Audit

You want to fix all documentation issues:

```bash
# Preview everything first
/craft:docs:update --interactive --dry-run

# Review what would change

# Apply interactively
/craft:docs:update --interactive
```

### Scenario 3: Specific Issue

You know there are broken links:

```bash
/craft:docs:update --category=broken_links
```

### Scenario 4: New Commands Added

You added commands and they need help:

```bash
/craft:docs:update --category=missing_help
```

---

## Troubleshooting

### "Too Many Changes!"

Start with one category:

```bash
/craft:docs:update --category=version_refs
```

### "I'm Not Sure What Changed"

Always use dry-run first:

```bash
/craft:docs:update --interactive --dry-run
```

### "I Made a Mistake!"

Revert with git:

```bash
git checkout .  # Undo all changes
```

### "Utilities Not Found"

Check installation:

```bash
ls utils/docs_detector.py
ls utils/help_file_validator.py
```

If missing, you're on the wrong branch.

---

## What You've Learned

✅ How to preview documentation issues (dry-run)
✅ How to use interactive prompts to choose fixes
✅ How to verify changes before committing
✅ How to update specific categories
✅ How to handle common scenarios

## Next Steps

1. **Try it yourself:** Run `/craft:docs:update --interactive --dry-run`
2. **Fix real issues:** Apply updates you approved
3. **Explore categories:** Try category-specific mode
4. **Read the reference:** See [REFCARD-DOCS-UPDATE.md](../reference/REFCARD-DOCS-UPDATE.md)

---

**Need help?** Check the [full documentation](../commands/docs/update.md) or run `/craft:help docs:update`.
