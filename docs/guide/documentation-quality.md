# Documentation Quality User Guide

> **TL;DR** (2 minutes)
>
> - **Step 1**: Run `/craft:docs:lint --fix` to auto-fix markdown issues
> - **Step 2**: Run `/craft:docs:check-links` to validate all links
> - **Step 3**: Enable pre-commit hooks with `/craft:git:init` for automatic validation
> - **Goal**: Zero broken links and consistent markdown quality

Complete tutorial for using Craft's documentation quality automation system.

!!! info "Related Documentation"
    - **[API Reference](../reference/documentation-quality.md)** - Technical details of quality checks and validation rules
    - **[Development Guide](documentation-quality-development.md)** - Contributing to the quality system

## What You'll Learn

By the end of this guide, you'll know how to:

1. ✅ Validate markdown quality and auto-fix common issues
2. ✅ Check for broken internal links
3. ✅ Set up pre-commit hooks for automatic validation
4. ✅ Integrate documentation checks into your workflow
5. ✅ Troubleshoot common documentation errors

**Time estimate:** 15 minutes

---

## Prerequisites

### Required

- Craft plugin installed and configured
- Documentation in `docs/` directory
- Node.js 16+ (for markdown tooling)

### Installation

```bash
# Install pinned markdown dependencies from lockfile (recommended)
npm ci

# Or install manually
npm install --save-dev markdown-link-check markdownlint-cli2

# Or let Craft install them when first used
/craft:docs:lint  # Auto-installs if missing
```

### Check Installation

```bash
# Verify tools are available
npx markdownlint-cli2 --version
npx markdown-link-check --version
```

---

## Getting Started

### Step 1: Understand Your Documentation Quality

Let's start by checking the current state of your documentation.

#### Run Initial Lint Check

```bash
/craft:docs:lint
```

**What to expect:**

- List of markdown quality issues
- Error locations (file:line:col format)
- Suggestions for fixes

**Example output:**

```
docs/guide/tutorial.md:23:1: MD032 - Blank lines around lists required
docs/commands/git.md:67:1: MD040 - Code fence missing language tag
Found 12 issues (8 auto-fixable)
```

#### Run Initial Link Check

```bash
/craft:docs:check-links
```

**What to expect:**

- Validation of all internal links
- List of broken links (if any)
- File and line numbers for errors

**Example output:**

```
Checking docs/guide/tutorial.md...
Checking docs/commands/git.md...
✅ Link validation passed (47 links checked)
```

---

## Auto-fixing Common Issues

### Step 2: Auto-fix Safe Issues

Many markdown quality issues can be fixed automatically:

```bash
/craft:docs:lint --fix
```

**Auto-fixed issues include:**

- ✅ Trailing spaces removed
- ✅ Hard tabs converted to spaces
- ✅ Multiple blank lines reduced
- ✅ Code fence language tags added (with smart detection)
- ✅ Indentation normalized
- ✅ **List spacing normalized to 1 space after markers** (MD030)
- ✅ **List markers changed to dash consistently** (MD004)

**Example output:**

```
Fixing docs/guide/tutorial.md...
  → Removed 4 trailing spaces
  → Added language tag to 2 code blocks (detected: bash, python)

Fixing docs/commands/git.md...
  → Converted 1 hard tab to spaces

✅ Auto-fixed 7 issues across 2 files
```

### Preview Before Fixing

Want to see what would be changed without actually modifying files?

```bash
/craft:docs:lint --fix --dry-run
```

**Output shows:**

- Files that would be modified
- Specific changes that would be made
- Issues requiring manual intervention

---

## Fixing Manual Issues

### Step 3: Address Remaining Issues

Some issues require manual fixes because they depend on context:

#### MD032: Blank Lines Around Lists

**Error:**

```
docs/guide/tutorial.md:23:1: MD032 - Blank lines around lists
```

**Fix:** Add blank line before and after list:

**Before:**

```markdown
Here's what you need:
- Item 1
- Item 2
Then do this...
```

**After:**

```markdown
Here's what you need:

- Item 1
- Item 2

Then do this...
```

#### MD011: Reversed Link Syntax

**Error:**

```
docs/commands/git.md:15:45: MD011 - Reversed link syntax
```

**Fix:** Correct link format:

**Before:**

```markdown
See (advanced usage)[./guide.md] for details
```

**After:**

```markdown
See [advanced usage](./guide.md) for details
```

#### MD042: Empty Links

**Error:**

```
docs/guide/tutorial.md:67:12: MD042 - Empty link URL
```

**Fix:** Add URL or remove link:

**Before:**

```markdown
Check the [documentation]() for more info
```

**After:**

```markdown
Check the [documentation](./reference.md) for more info
```

#### MD030: List Marker Spacing

**Error:**

```
docs/guide/tutorial.md:45:1: MD030 - Spaces after list markers
```

**Fix:** Use exactly 1 space after list markers:

**Before:**

```markdown
-  Item with 2 spaces
1.  Ordered with 2 spaces
```

**After:**

```markdown
- Item with 1 space
1. Ordered with 1 space
```

**Auto-fix:** Run `/craft:docs:lint --fix` to automatically normalize spacing.

---

#### MD004: Consistent List Markers

**Error:**

```
docs/guide/tutorial.md:67:1: MD004 - Unordered list style
```

**Fix:** Use `-` (dash) consistently, not `*` (asterisk) or `+` (plus):

**Before:**

```markdown
* Item with asterisk
+ Item with plus
- Item with dash
```

**After:**

```markdown
- Item with dash
- Item with dash
- Item with dash
```

**Auto-fix:** Run `/craft:docs:lint --fix` to automatically change markers to `-`.

---

## Validating Internal Links

### Step 4: Check All Links

Ensure all internal documentation links work:

```bash
/craft:docs:check-links
```

#### Understanding Link Validation

**Links checked:**

- ✅ Relative paths: `./other.md`, `../parent.md`
- ✅ Absolute paths: `/docs/commands/git.md`
- ✅ File existence
- ❌ External URLs (skipped by default)

**Example output:**

```
Checking docs/guide/tutorial.md... ✓
  → 12 links valid
Checking docs/commands/git.md... ✓
  → 8 links valid

✅ All links valid (47 links checked across 15 files)
```

### Fixing Broken Links

#### Scenario 1: File Moved or Renamed

**Error:**

```
docs/guide/tutorial.md:15:1: Broken link → ../commands/old-name.md
```

**Fix:**

1. Find the file's new location
2. Update the link path
3. Re-run validation

```bash
# After fixing
/craft:docs:check-links docs/guide/tutorial.md
```

#### Scenario 2: Broken Anchor

**Error:**

```
docs/commands/git.md:42:3: Broken anchor → tutorial.md#getting-started
```

**Fix:**

1. Open target file (`tutorial.md`)
2. Find the correct heading
3. Update anchor (use lowercase with hyphens)

**Example:**

```markdown
# Getting Started with Craft  →  #getting-started-with-craft
## Quick Start              →  #quick-start
### Step 1: Install        →  #step-1-install
```

### Comprehensive Link Check (Before Release)

Include anchor validation:

```bash
/craft:docs:check-links release
```

**Additional checks:**

- ✅ Anchor validation (header existence)
- ✅ Case-sensitive matching
- ✅ Fragment-only links (`#section`)

---

## Workflow Integration

### Step 5: Integrate with /craft:check

The `/craft:check` command automatically runs documentation validation when docs change:

```bash
/craft:check
```

**When docs/ files are modified:**

```
📚 Docs changed, running validation...
  → Checking markdown quality...
  ✅ No issues found

  → Checking links...
  ✅ All links valid (32 links checked)
```

**Benefits:**

- Automatic validation before commits
- Catches issues early in development
- No need to remember separate commands

### Daily Workflow

**Recommended workflow:**

```bash
# 1. Edit documentation
vim docs/guide/tutorial.md

# 2. Auto-fix issues
/craft:docs:lint --fix

# 3. Validate links
/craft:docs:check-links

# 4. Commit changes
git add docs/
git commit -m "docs: update tutorial guide"
```

---

## Pre-commit Hook Automation

### Step 6: Enable Pre-commit Hooks

Automate documentation validation before every commit:

```bash
/craft:git:init
```

**During setup, choose Step 6.5:**

```
Step 6.5: Pre-commit Hooks
Would you like to auto-validate docs before commits? (y/n): y

✅ Created .git/hooks/pre-commit
   → Auto-lint with --fix on staged docs
   → Validate links before commit
   → Abort commit if errors found
```

### How Pre-commit Hooks Work

**When you commit:**

```bash
git commit -m "docs: add new guide"
```

**Hook automatically runs:**

```
📚 Checking documentation quality...

  → Running markdown lint...
  ✅ Auto-fixed 3 issues (trailing spaces)

  → Checking links...
  ✅ All links valid

✅ Documentation quality checks passed!
[main a1b2c3d] docs: add new guide
 1 file changed, 45 insertions(+)
```

### If Errors Are Found

**Hook blocks commit:**

```
📚 Checking documentation quality...

  → Running markdown lint...
  ❌ Found 2 issues requiring manual fix:
     docs/guide/tutorial.md:23:1: MD032 - Blank lines around lists

  → Checking links...
  ❌ Broken link found:
     docs/guide/tutorial.md:15:1 → ../missing.md

❌ Commit blocked. Fix issues and try again.
```

**Fix issues and retry:**

```bash
# Fix the issues
vim docs/guide/tutorial.md

# Stage fixes
git add docs/guide/tutorial.md

# Retry commit
git commit -m "docs: add new guide"
```

### Bypass Hooks (Emergency Only)

**Skip validation (not recommended):**

```bash
git commit --no-verify -m "docs: emergency fix"
```

⚠️ **Warning**: Only use `--no-verify` in emergencies. Pre-commit hooks prevent broken docs from entering your history.

---

## CI/CD Integration

### Step 7: Add GitHub Actions Workflow

Validate documentation in pull requests automatically.

#### Create Workflow File

Create `.github/workflows/docs-quality.yml`:

```yaml
name: Documentation Quality

on:
  pull_request:
    paths:
      - 'docs/**/*.md'
      - 'README.md'
      - 'CLAUDE.md'
  push:
    branches: [main, dev]

jobs:
  markdown-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Lint markdown files
        run: npx markdownlint-cli2 "docs/**/*.md" "*.md"

  link-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check documentation links
        uses: lycheeverse/lychee-action@v1
        with:
          args: --verbose --no-progress docs/**/*.md README.md
          fail: true

  summary:
    runs-on: ubuntu-latest
    needs: [markdown-lint, link-check]
    if: always()
    steps:
      - name: Documentation quality summary
        run: |
          echo "✅ Documentation quality checks complete"
```

#### What This Does

**On every PR:**

- ✅ Lints all markdown files
- ✅ Checks all links (including external)
- ✅ Blocks merge if errors found
- ✅ Shows errors in PR checks

**Benefit:** Catch documentation issues before they reach main branch.

---

## Advanced Usage

### Check Specific Files

```bash
# Single file
/craft:docs:lint docs/guide/tutorial.md

# Directory
/craft:docs:check-links docs/commands/

# Multiple files with glob
/craft:docs:lint docs/**/*.md
```

### Debug Mode

Get detailed information about checks:

```bash
/craft:docs:lint debug docs/guide/tutorial.md
/craft:docs:check-links debug
```

**Output includes:**

- Verbose logging
- Rule explanations
- Fix suggestions
- Processing traces

### Optimize Mode (CI/CD)

Fast validation for automated pipelines:

```bash
/craft:docs:lint optimize --fix
/craft:docs:check-links optimize
```

**Features:**

- Parallel processing
- Minimal output
- Optimized performance

### Release Mode (Comprehensive)

Thorough validation before releases:

```bash
/craft:docs:lint release
/craft:docs:check-links release
```

**Additional checks:**

- Style rules
- Accessibility
- Anchor validation
- Best practices

---

## Testing Your Setup

### Step 8: Test with Violations File

Craft includes a test file with known violations:

```bash
# View test file
cat docs/test-violations.md

# Test lint detection
/craft:docs:lint docs/test-violations.md

# Test link detection
/craft:docs:check-links docs/test-violations.md
```

**Expected output:**

```
docs/test-violations.md:15:1: MD040 - Code fence missing language
docs/test-violations.md:23:1: Broken link → ./missing-file.md
docs/test-violations.md:27:3: Broken anchor → commands.md#invalid-section
```

### Verify Auto-fix

```bash
# Test auto-fix on violations file
/craft:docs:lint docs/test-violations.md --fix --dry-run

# Should show what would be fixed
```

---

## Troubleshooting

### Common Issues

#### "Command not found: markdownlint-cli2"

**Solution:**

```bash
npm ci  # Install from lockfile (recommended)
# Or: npm install --save-dev markdownlint-cli2
```

#### "Link validation passing locally but failing in CI"

**Cause:** Case sensitivity (macOS vs Linux)

**Solution:** Use exact case in file names and paths:

```markdown
# Wrong (if file is Readme.md)
[link](readme.md)

# Correct
[link](Readme.md)
```

#### "Auto-fix not working on specific issue"

**Cause:** Issue requires manual intervention

**Solution:** Read error message and fix manually:

```bash
/craft:docs:lint debug docs/file.md  # Get detailed explanation
```

#### "Pre-commit hook blocking all commits"

**Temporary solution:**

```bash
git commit --no-verify -m "message"
```

**Permanent solution:** Fix documentation issues or disable hooks:

```bash
chmod -x .git/hooks/pre-commit  # Disable
chmod +x .git/hooks/pre-commit  # Re-enable
```

---

## Best Practices

### Daily Development

```bash
# Before starting work
/craft:check

# While writing
/craft:docs:lint --fix  # Run frequently

# Before committing
/craft:docs:check-links
```

### Before Pull Requests

```bash
# Comprehensive check
/craft:docs:lint release
/craft:docs:check-links release

# If all passes, create PR
gh pr create
```

### Team Workflow

1. **Enable pre-commit hooks** on all machines
2. **Add CI workflow** to repository
3. **Document conventions** in CONTRIBUTING.md
4. **Review docs changes** in PRs carefully

### Performance Tips

- Use `default` mode during development (fast)
- Use `release` mode before PRs (thorough)
- Use `optimize` mode in CI (efficient)
- Enable pre-commit hooks (catch early)

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Quick lint check | `/craft:docs:lint` |
| Auto-fix safe issues | `/craft:docs:lint --fix` |
| Check all links | `/craft:docs:check-links` |
| Comprehensive check | `/craft:docs:lint release && /craft:docs:check-links release` |
| Enable pre-commit hooks | `/craft:git:init` (choose Step 6.5) |
| Test with violations | `/craft:docs:lint docs/test-violations.md` |
| Debug specific file | `/craft:docs:lint debug docs/file.md` |
| Preview auto-fixes | `/craft:docs:lint --fix --dry-run` |
| Check specific directory | `/craft:docs:check-links docs/commands/` |
| Integrated validation | `/craft:check` (auto-runs when docs change) |

---

## Next Steps

### Learn More

- [API Reference](../reference/documentation-quality.md) - Complete command reference
- [Developer Guide](./documentation-quality-development.md) - Extend the system
- [Git Init Tutorial](./git-init-tutorial.md) - Pre-commit hook setup

### Get Help

```bash
# View command help
/craft:docs:lint --help
/craft:docs:check-links --help

# Check command documentation
claude "Read commands/docs/lint.md"
```

### Provide Feedback

Found a bug or have a suggestion?

- Open an issue on GitHub
- Contribute improvements via PR
- Share your use cases

---

## Summary

You've learned how to:

✅ **Validate markdown quality** with `/craft:docs:lint`
✅ **Auto-fix common issues** with `--fix` flag
✅ **Check internal links** with `/craft:docs:check-links`
✅ **Set up pre-commit hooks** for automatic validation
✅ **Integrate with CI/CD** for PR validation
✅ **Troubleshoot common issues** effectively

**Your documentation quality is now automated!** 🎉
