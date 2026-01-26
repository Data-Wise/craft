# Markdown List Spacing Best Practices

> **TL;DR** (5 minutes)
>
> - Use `-` (dash) for all unordered list markers
> - Use exactly 1 space after markers (`- Item`, not `-  Item`)
> - Add blank line before and after lists
> - Goal: Consistent rendering everywhere

Complete guide for maintaining list formatting standards across Craft documentation.

!!! info "Related Documentation"
    - **[Command Reference](../commands/docs.md)** - `/craft:docs:lint` command details
    - **[Quality Guide](documentation-quality.md)** - Complete markdown quality workflow

## What You'll Learn

By the end of this guide, you'll know how to:

1. ✅ Use consistent list marker style (`-`)
2. ✅ Maintain proper spacing after list markers
3. ✅ Add blank lines around lists for readability
4. ✅ Fix violations manually or with auto-fix
5. ✅ Understand why these rules matter

**Time estimate:** 5 minutes

---

## Why List Spacing Matters

### Consistent Rendering

Different markdown renderers handle list spacing differently:

```markdown
-  Item with 2 spaces
```

**GitHub:** `-` Item with 2 spaces` (renders literally)
**MkDocs:** `- Item with 2 spaces` (may look wrong)
**VS Code:** `- Item with 2 spaces` (may break preview)

**Correct:**

```markdown
- Item with 1 space
```

**All renderers:** `- Item with 1 space` (consistent!)

### Portable Documentation

When your markdown works everywhere, you avoid:

- Broken rendering in different platforms
- Inconsistent spacing in generated docs
- Confusion about "correct" format
- Rendering surprises in PR previews

### Auto-fix Capability

With consistent rules, you can:

- Fix issues automatically: `/craft:docs:lint --fix`
- Prevent new violations with pre-commit hooks
- Focus on content, not formatting
- Save time on manual cleanup

---

## The Three List Rules

### Rule 1: MD030 - List Marker Spacing

**Requirement:** Exactly 1 space after list markers.

**Unordered lists:**

```markdown
✅ Correct: - Item with 1 space
❌ Wrong:  - Item with 2 spaces
❌ Wrong: -Item with 0 spaces
```

**Ordered lists:**

```markdown
✅ Correct: 1. Item with 1 space
❌ Wrong: 1.  Item with 2 spaces
❌ Wrong: 1.Item with 0 spaces
```

**Nested lists:**

```markdown
✅ Correct:
- Parent item
  - Child item with 1 space
  - Another child

❌ Wrong:
- Parent item
  -  Child with 2 spaces
  - Another child
```

### Rule 2: MD004 - Consistent List Markers

**Requirement:** Use `-` (dash) for all unordered list markers.

**Never mix:**

```markdown
❌ Wrong:
- First item
* Second item
+ Third item
```

**Always consistent:**

```markdown
✅ Correct:
- First item
- Second item
- Third item
```

**Why dash?**

- Most common convention
- Renders consistently
- Easy to type
- Widely adopted standard

### Rule 3: MD032 - Blank Lines Around Lists

**Requirement:** Blank line before and after lists.

**Missing blank line before:**

```markdown
❌ Wrong:
## Section Title
- First item
- Second item

✅ Correct:
## Section Title

- First item
- Second item
```

**Missing blank line after:**

```markdown
❌ Wrong:
- First item
- Second item
## Next Section

✅ Correct:
- First item
- Second item

## Next Section
```

---

## Common Mistakes

### Mistake 1: Extra Spaces After Markers

**Symptom:** List items have uneven spacing or look misaligned.

**Example:**

```markdown
-  First item
- Second item
- Third item
```

**Fix:** Use exactly 1 space.

```markdown
- First item
- Second item
- Third item
```

### Mistake 2: Mixed List Markers

**Symptom:** Inconsistent list markers throughout document.

**Example:**

```markdown
## Features
- Feature 1
* Feature 2
- Feature 3
```

**Fix:** Use `-` everywhere.

```markdown
## Features
- Feature 1
- Feature 2
- Feature 3
```

### Mistake 3: Missing Blank Lines

**Symptom:** Lists merge with surrounding text, poor readability.

**Example:**

```markdown
## Getting Started
First, install the package:
- Download from npm
- Extract archive
Then run the setup script.
```

**Fix:** Add blank lines.

```markdown
## Getting Started

First, install the package:

- Download from npm
- Extract archive

Then run the setup script.
```

### Mistake 4: Ignoring Code Blocks

**Symptom:** Lists inside code blocks flagged as violations.

**Example:**

```markdown
## Installation

```bash
# Code blocks with lists are OK
-  This is not a markdown list
*  This is a code block
```

**Fix:** Nothing! Code blocks are exempt from list rules.

---

## Fixing Violations

### Auto-Fix (Recommended)

Run the auto-fix command:

```bash
/craft:docs:lint --fix
```

**What it does:**

- Normalizes spacing to 1 space
- Changes all markers to `-`
- Adds missing blank lines
- Preserves content (only fixes formatting)

**Preview first:**

```bash
/craft:docs:lint --fix --dry-run
```

### Manual Fixes

**If auto-fix doesn't work or you prefer manual editing:**

1. **Find violations:**

   ```bash
   /craft:docs:lint
   ```

2. **Locate each issue:**

   ```
   docs/guide/tutorial.md:45:1: MD030 - Spaces after list markers
   ```

3. **Fix manually:**
   - Remove extra spaces after markers
   - Change `*` or `+` to `-`
   - Add blank lines before/after lists

4. **Verify fix:**

   ```bash
   /craft:docs:lint docs/guide/tutorial.md
   ```

---

## Prevention

### Pre-commit Hooks

Enable automatic validation before commits:

```bash
# Already installed in main repo
# Hooks run automatically on: git commit
```

**What hooks do:**

- Check staged `.md` files for violations
- Offer interactive auto-fix (`y/n`)
- Block commits with unfixed issues
- Skip if no markdown files staged

**Pre-commit workflow:**

```bash
# Stage markdown files
git add docs/guide/tutorial.md

# Try to commit
git commit -m "docs: update tutorial"

# Hook runs: 🔍 Checking markdown list spacing...

# If violations found:
❌ Markdown linting failed!
Would you like to auto-fix these issues? (y/n)
```

### Habit Formation

**Develop these habits:**

1. **Use `-` consistently** - Always type dash for list markers
2. **Type 1 space** - Always type exactly one space after `-`
3. **Add blank lines** - Always press Enter before and after lists
4. **Run lint regularly** - Check with `/craft:docs:lint` as you work
5. **Fix immediately** - Don't let violations accumulate

---

## Testing Your Changes

### Validation

Always validate before committing:

```bash
# Check specific file
/craft:docs:lint docs/guide/new-feature.md

# Check all markdown
/craft:docs:lint "docs/**/*.md" "commands/**/*.md"
```

### Preview Rendering

Check how it looks in different platforms:

1. **VS Code:** Open file, check preview panel
2. **GitHub:** Push to PR, check rendered markdown
3. **MkDocs:** Run `mkdocs serve`, check generated docs

### Compare Before/After

Documenting changes helps:

```markdown
Before:
-  Item with 2 spaces
* Another item

After:
- Item with 1 space
- Another item
```

---

## Examples

### Good Examples

#### Simple List

```markdown
## Getting Started

Follow these steps:

1. Install the package
2. Configure settings
3. Run the application

**That's it!**
```

**Why good:**

- Blank line before list
- 1 space after numbers
- Blank line after list

#### Nested List

```markdown
## Features

- Core features
  - Fast performance
  - Easy to use
  - Reliable

- Advanced features
  - API integration
  - Custom plugins
  - Enterprise support
```

**Why good:**

- Consistent `-` markers
- Proper indentation (2 spaces)
- 1 space after markers at all levels

#### Mixed Lists

```markdown
## Installation

Requirements:

- Node.js 18+
- npm or yarn

Steps:

1. Clone the repository
2. Install dependencies
3. Build the project

**Note:** Follow the README for additional details.
```

**Why good:**

- Blank lines between sections
- Consistent ordered list format
- Clear separation of list types

### Bad Examples

#### Inconsistent Markers

```markdown
## Features

- Feature 1
* Feature 2
+ Feature 3
```

**Why bad:** Mixed markers confuse readers and renderers.

**Fix:** Use `-` everywhere.

#### Extra Spaces

```markdown
## Steps

-  First step
- Second step
- Third step
```

**Why bad:** Extra spaces look like typos.

**Fix:** Use 1 space after `-`.

#### Missing Blank Lines

```markdown
## Overview
This is an overview.
- Item 1
- Item 2
## Details
This is details.
```

**Why bad:** Poor readability, looks rushed.

**Fix:** Add blank lines before/after lists.

---

## Troubleshooting

### Issue: Auto-fix not working

**Problem:** `/craft:docs:lint --fix` doesn't fix violations.

**Possible causes:**

1. **File not saved** - Save before running
2. **Wrong file format** - Check it's `.md`, not `.md.txt`
3. **Permission issues** - Check file is writable

**Solution:**

```bash
# Save file
# Verify it's markdown
ls -la docs/guide/tutorial.md

# Run auto-fix with verbose output
/craft:docs:lint --fix docs/guide/tutorial.md
```

### Issue: Too many violations

**Problem:** `/craft:docs:lint` shows hundreds of violations.

**Solution:** Fix gradually, not all at once.

```bash
# Start with critical files
/craft:docs:lint README.md CLAUDE.md

# Fix those, then move on
/craft:docs:lint --fix README.md
/craft:docs:lint --fix CLAUDE.md

# Repeat for other files
```

### Issue: False positives

**Problem:** Code blocks flagged as list violations.

**Solution:** Nothing to fix! Code blocks are exempt.

**Example:**

```markdown
```bash
# This is fine
- ls -la
* grep "pattern"
```

```

---

## Advanced Topics

### Multi-line List Items

Maintain 1 space even with multi-line items:

```markdown
- First item continues
  on the next line with indentation
- Second item with
  multiple lines
```

**Key:** Indent continuation lines with 2+ spaces, but still 1 space after marker.

### Code in Lists

Code within list items:

```markdown
- Run this command:
  `npm install`
- Or use yarn:
  `yarn install`
```

**Key:** Use backticks for inline code within lists.

### Definition Lists

Definition lists (`:` syntax) have different rules:

```markdown
- **Term**: Definition
- **Another term**: Another definition
```

**Note:** These follow different formatting rules than standard lists.

---

## References

### Command Documentation

- **[`/craft:docs:lint`](../commands/docs.md)** - Markdown quality command
- **[`/craft:check`](../commands/check.md)** - Pre-flight validation

### Guides

- **[Documentation Quality Guide](documentation-quality.md)** - Complete markdown quality workflow
- **[Getting Started](getting-started.md)** - Plugin installation and setup

### Specs

- **[List Spacing Spec](../specs/SPEC-markdownlint-list-spacing-2026-01-19.md)** - Technical specification

### Tests

- **[List Spacing Tests](https://github.com/Data-Wise/craft/blob/main/tests/README.md)** - 78 tests, 100% passing

---

## Quick Reference

| Rule | Description | Auto-fix |
|-------|-------------|----------|
| **MD030** | 1 space after list markers | ✅ Yes |
| **MD004** | Use `-` (dash) markers only | ✅ Yes |
| **MD032** | Blank lines around lists | ✅ Yes |

**Common Patterns:**

```bash
# Check all markdown
/craft:docs:lint

# Auto-fix issues
/craft:docs:lint --fix

# Check specific file
/craft:docs:lint README.md

# Preview changes
/craft:docs:lint --fix --dry-run
```

---

## Summary

**Key takeaways:**

1. Always use `-` for list markers
2. Always use exactly 1 space after markers
3. Always add blank lines around lists
4. Use `/craft:docs:lint --fix` to automate fixes
5. Pre-commit hooks prevent new violations

**Benefits:**

- ✅ Consistent rendering everywhere
- ✅ Portable documentation
- ✅ Auto-fix capability
- ✅ Pre-commit prevention
- ✅ Focus on content, not formatting

**Next steps:**

- Review [Documentation Quality Guide](documentation-quality.md) for complete workflow
- Check [Command Reference](../commands/docs.md) for all linting options
- See [Spec](../specs/SPEC-markdownlint-list-spacing-2026-01-19.md) for technical details
