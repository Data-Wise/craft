---
title: "Troubleshooting: Broken Links After Update"
description: "Fix broken links reported by mkdocs build or /craft:docs:check-links after documentation changes"
category: "cookbook"
level: "beginner"
time_estimate: "5 minutes"
related:
  - ../../commands/docs.md
  - ../../guide/documentation-quality.md
---

# Troubleshooting: Broken Links After Update

**Level:** Beginner

## Problem

After updating documentation, `mkdocs build` or `/craft:docs:check-links` reports broken links:

```
WARNING - Doc file 'guide/my-guide.md' contains a link
  'tutorials/deleted-page.md', but the target is not found.
```

## Common Causes & Solutions

### 1. File Renamed Without Updating References

**Issue:** A file was renamed or moved, but other files still link to the old path.

**Solution:**

```bash
grep -r "old-name.md" docs/    # find all references
# Update each one to the new filename
```

**Why:** Markdown links use relative paths. When a file moves, every link to its old location breaks.

### 2. Deleted Page Still Referenced

**Issue:** A page was deleted but remains in `mkdocs.yml` nav or is linked from other pages.

**Solution:**

```bash
grep "deleted-page" mkdocs.yml   # check nav
grep -r "deleted-page.md" docs/  # check cross-references
# Remove or update each stale reference
```

**Why:** MkDocs validates that every nav entry and cross-reference resolves to an existing file.

### 3. Wrong Relative Path

**Issue:** The link uses an incorrect number of `../` levels.

**Solution:**

```bash
# From docs/guide/my-guide.md linking to docs/commands/do.md:
# Wrong:  [Do Command](commands/do.md)        -- missing ../
# Wrong:  [Do Command](../../commands/do.md)   -- too many levels
# Right:  [Do Command](../commands/do.md)      -- one level up
```

**Why:** Relative paths resolve from the directory of the file containing the link.

### 4. Expected Broken Links Not in Ignore List

**Issue:** Some links are intentionally broken (test fixtures, brainstorm drafts) but not in `.linkcheck-ignore`.

**Solution:**

```bash
echo "docs/brainstorm/draft-*.md" >> .linkcheck-ignore
```

### 5. Missing Nav Entry

**Issue:** A new page exists but is not in the `nav` section of `mkdocs.yml`.

**Solution:** Run `mkdocs build 2>&1 | grep "not in the nav"` and add the page to the correct nav section.

## Verification Steps

```bash
mkdocs build --strict 2>&1 | grep -i "warning"
/craft:docs:check-links
python3 tests/test_craft_plugin.py -k "broken_links"
```

A clean `--strict` build with zero warnings confirms all links are valid.

## Related

- [Documentation Commands](../../commands/docs.md) -- All docs-related commands
- [Documentation Quality Guide](../../guide/documentation-quality.md) -- Best practices for link management
- [Docs Update Reference](../../reference/REFCARD-DOCS-UPDATE.md) -- Quick reference for docs updates
