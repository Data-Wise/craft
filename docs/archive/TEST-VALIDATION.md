# Documentation Quality Commands - Test Validation

Test validation for `/craft:docs:check-links` and `/craft:docs:lint` commands using `docs/test-violations.md`.

## Test File Overview

The `docs/test-violations.md` file contains 6 test cases:

1. **Broken Internal Links** - 4 broken links (relative + absolute)
2. **Valid Internal Links** - 4 working links for verification
3. **Markdown Linting Issues** - Missing blank line, unlabeled code fence
4. **Mixed Link Styles** - Relative vs absolute paths
5. **External Links** - Should be skipped in MVP
6. **Anchor Links** - For release mode testing

---

## Test 1: Link Checking (Default Mode)

### Command

```bash
/craft:docs:check-links docs/test-violations.md
```

### Expected Output

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:check-links (default mode)                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ✓ Checked: 13 internal links in 1 file                      │
│                                                             │
│ ✗ Broken Links (4):                                         │
│   1. docs/test-violations.md:8                              │
│      [missing file](nonexistent.md)                         │
│      → File not found: docs/nonexistent.md                  │
│                                                             │
│   2. docs/test-violations.md:10                             │
│      [another broken link](../missing-directory/file.md)    │
│      → File not found: missing-directory/file.md            │
│                                                             │
│   3. docs/test-violations.md:13                             │
│      [configuration guide](/docs/missing-config.md)         │
│      → File not found: /docs/missing-config.md              │
│                                                             │
│   4. docs/test-violations.md:15                             │
│      [API reference](/docs/reference/nonexistent-api.md)    │
│      → File not found: /docs/reference/nonexistent-api.md   │
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ ✓ Valid Links (4):                                          │
│   - Line 20: index.md ✓                                     │
│   - Line 22: commands/index.md ✓                            │
│   - Line 25: /docs/index.md ✓                               │
│   - Line 58: /docs/commands/index.md ✓                      │
│                                                             │
│ ℹ Skipped (5):                                              │
│   - 3 external links (https://, mailto:)                    │
│   - 2 anchor-only links (default mode doesn't check)       │
│                                                             │
│ Exit code: 1 (broken links found)                           │
│                                                             │
│ Fix these links before deployment to prevent 404 errors.    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### VS Code Integration Format

```
docs/test-violations.md:8:11: [missing file](nonexistent.md) → File not found
docs/test-violations.md:10:11: [another broken link](../missing-directory/file.md) → File not found
docs/test-violations.md:13:7: [configuration guide](/docs/missing-config.md) → File not found
docs/test-violations.md:15:6: [API reference](/docs/reference/nonexistent-api.md) → File not found
```

### Validation Checklist

- [ ] Detects all 4 broken links
- [ ] Validates 4 valid internal links
- [ ] Skips 3 external links (https://, mailto:)
- [ ] Skips anchor links in default mode
- [ ] Exit code = 1 (errors found)
- [ ] Output in file:line:col format for VS Code

---

## Test 2: Markdown Linting (Default Mode)

### Command

```bash
/craft:docs:lint docs/test-violations.md
```

### Expected Output

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:lint (default mode)                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ✓ Checked: 1 markdown file                                  │
│                                                             │
│ ✗ Issues Found (2):                                         │
│   1. docs/test-violations.md:30 [MD032]                     │
│      Missing blank line before list                         │
│      Auto-fixable: Yes                                      │
│                                                             │
│      Context:                                               │
│      29: ### Missing Blank Line Before List                 │
│      30: Some text without blank line before list:          │
│      31: - Item 1                                           │
│                                                             │
│      Fix: Add blank line between line 30 and 31             │
│                                                             │
│   2. docs/test-violations.md:37 [MD040]                     │
│      Code fence missing language tag                        │
│      Auto-fixable: Yes (detected language: python)          │
│                                                             │
│      Context:                                               │
│      36:                                                    │
│      37: ```                                                │
│      38: This code fence has no language tag                │
│      39: def example():                                     │
│                                                             │
│      Fix: Add 'python' language tag to code fence           │
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ All issues are auto-fixable!                                │
│                                                             │
│ Run with --fix to apply fixes:                              │
│   /craft:docs:lint --fix docs/test-violations.md            │
│                                                             │
│ Exit code: 0 (auto-fixable)                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### VS Code Integration Format

```
docs/test-violations.md:30:1: MD032 - Missing blank line before list (auto-fixable)
docs/test-violations.md:37:1: MD040 - Code fence missing language tag (auto-fixable)
```

### Validation Checklist

- [ ] Detects missing blank line before list (line 30)
- [ ] Detects code fence without language tag (line 37)
- [ ] Correctly identifies both as auto-fixable
- [ ] Detects language as Python from code content
- [ ] Exit code = 0 (auto-fixable issues only)
- [ ] Suggests --fix flag
- [ ] Output in file:line:col format for VS Code

---

## Test 3: Markdown Linting with Auto-Fix

### Command

```bash
/craft:docs:lint --fix docs/test-violations.md
```

### Expected Output

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:lint --fix (default mode)                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 🔧 AUTO-FIXING SAFE ISSUES...                               │
│                                                             │
│ docs/test-violations.md:                                    │
│   ✓ Fixed: MD032 - Added blank line before list (line 30)  │
│   ✓ Fixed: MD040 - Added language tag 'python' (line 37)   │
│                                                             │
│ Auto-fixed: 2 issues in 1 file                              │
│                                                             │
│ ✓ No manual fixes needed!                                   │
│                                                             │
│ Exit code: 0 (all issues resolved)                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### File Changes After Auto-Fix

**Before (line 30-31):**

```markdown
Some text without blank line before list:
- Item 1
```

**After (line 30-32):**

```markdown
Some text without blank line before list:

- Item 1
```

**Before (line 37):**

```markdown
```

```

**After (line 37):**
```markdown
```python
```

### Validation Checklist

- [ ] Adds blank line before list
- [ ] Adds 'python' language tag to code fence
- [ ] File is modified in place
- [ ] Exit code = 0 (success)
- [ ] Reports 2 issues fixed
- [ ] No manual intervention needed

---

## Test 4: Link Checking (Release Mode)

### Command

```bash
/craft:docs:check-links release docs/test-violations.md
```

### Expected Output (Additional Checks)

```
🎯 RELEASE: Comprehensive Link Validation

Phase 1: Internal file links... ✗ 4 broken (as expected)

Phase 2: Anchor validation...

Checking anchor targets...

  ✓ Line 71: [Test Case 1](#test-case-1-broken-internal-links)
    → Heading exists in same file

  ✓ Line 72: [Test Case 2](#test-case-2-valid-internal-links)
    → Heading exists in same file

  ✗ Line 73: [Nonexistent Heading](#this-heading-does-not-exist)
    → Heading not found in file
    Available headings:
      - #test-violations-file
      - #test-case-1-broken-internal-links
      - #test-case-2-valid-internal-links
      - #test-case-3-markdown-linting-issues
      - #test-case-4-mixed-link-styles
      - #test-case-5-external-links-skipped-in-mvp
      - #test-case-6-anchor-links-release-mode-only

  ? Line 76: [Index intro](index.md#overview)
    → Cannot verify: index.md not found

Phase 3: Link consistency...

  ⚠ Mixed link reference styles detected:
    - Lines 20, 22: Relative links
    - Lines 25, 58, 59: Absolute links (/docs/...)
    Recommendation: Use relative paths for portability

Summary:
  File links: 4/8 valid (4 broken)
  Anchor links: 2/3 valid (1 broken)
  Consistency: 1 warning
  Total issues: 5
```

### Validation Checklist

- [ ] Validates anchor links within file
- [ ] Detects broken anchor (#this-heading-does-not-exist)
- [ ] Shows available headings as suggestions
- [ ] Detects mixed link styles (relative vs absolute)
- [ ] Exit code = 1 (errors found)

---

## Test 5: Markdown Linting (Debug Mode)

### Command

```bash
/craft:docs:lint debug docs/test-violations.md
```

### Expected Output (Verbose)

```
🔍 DEBUG: Markdown Linting with Context

docs/test-violations.md:30 (MD032):
  Rule: Lists should be surrounded by blank lines
  Severity: Error
  Auto-fixable: Yes

  Context (lines 28-34):
    28:
    29: ### Missing Blank Line Before List
    30: Some text without blank line before list:
    31: - Item 1
    32: - Item 2
    33: - Item 3
    34:

  Fix:
    Add blank line after line 30:

    30: Some text without blank line before list:
    31:
    32: - Item 1

  Why this matters:
    Missing blank lines before lists can cause rendering issues
    in some markdown processors. Some may render the list as
    plain text instead of formatted list items.

docs/test-violations.md:37 (MD040):
  Rule: Code fences should have a language tag
  Severity: Error
  Auto-fixable: Yes

  Context (lines 35-42):
    35:
    36: ### Code Fence Without Language Tag
    37:
    38: ```
    39: This code fence has no language tag
    40: def example():
    41:     pass
    42: ```

  Language Detection:
    Detected: Python
    Confidence: High
    Indicators: 'def', 'pass' keywords

  Suggestion:
    37: ```python
    38: This code fence has no language tag

  Why this matters:
    Language tags enable syntax highlighting and improve
    readability. They're especially important for technical
    documentation where code examples are common.

Summary: 2 errors found (all auto-fixable)
Run with --fix to apply changes.
```

### Validation Checklist

- [ ] Shows detailed context (lines before/after)
- [ ] Explains why each rule matters
- [ ] Shows suggested fixes with line numbers
- [ ] Displays language detection reasoning
- [ ] More verbose than default mode

---

## Test 6: Pre-commit Hook Simulation

### Scenario

```bash
# Stage test file with violations
git add docs/test-violations.md

# Attempt commit (hook runs automatically)
git commit -m "docs: add test file"
```

### Expected Hook Behavior

```
📚 Checking documentation quality...
  → Running markdown lint...

🔧 AUTO-FIXING SAFE ISSUES...
docs/test-violations.md:
  ✓ Fixed: MD032 - Added blank line before list (line 30)
  ✓ Fixed: MD040 - Added language tag 'python' (line 37)

Auto-fixed: 2 issues in 1 file

  → Checking links...

✗ Broken links found in documentation:
  docs/test-violations.md:8 → nonexistent.md (File not found)
  docs/test-violations.md:10 → ../missing-directory/file.md (File not found)
  docs/test-violations.md:13 → /docs/missing-config.md (File not found)
  docs/test-violations.md:15 → /docs/reference/nonexistent-api.md (File not found)

❌ Broken links found in documentation
   Fix the broken links above, then try again.
```

**Commit blocked - exit code 1**

### After Fixing Links

User fixes the broken links, then:

```bash
git add docs/test-violations.md
git commit -m "docs: add test file"
```

```
📚 Checking documentation quality...
  → Running markdown lint...

✅ No markdown issues found!

  → Checking links...

✅ All links valid!

✅ Documentation quality checks passed!

[feature/docs-quality abc1234] docs: add test file
 1 file changed, 114 insertions(+)
 create mode 100644 docs/test-violations.md
```

**Commit succeeds - exit code 0**

### Validation Checklist

- [ ] Hook runs automatically on commit
- [ ] Auto-fixes markdown issues
- [ ] Re-stages fixed files
- [ ] Blocks commit if links broken
- [ ] Allows commit after fixes applied
- [ ] Shows clear error messages

---

## Integration Test: /craft:check

### Scenario

Working directory has docs changes.

### Command

```bash
/craft:check
```

### Expected Output (Docs Section)

```
╭─ /craft:check ──────────────────────────────────────╮
│ Project: craft (Claude Code Plugin)                │
│ Time: 8.4s                                         │
├─────────────────────────────────────────────────────┤
│ ✓ Lint         0 issues                            │
│ ✓ Tests        30/30 passed                        │
│ ✓ Types        No errors                           │
│                                                     │
│ 📚 Docs Changed: Running validation...             │
│   → Checking markdown quality...                   │
│   ✗ docs/test-violations.md: 2 issues (auto-fixable)│
│                                                     │
│   → Checking links...                               │
│   ✗ docs/test-violations.md: 4 broken links        │
│                                                     │
│ ✗ Git          Uncommitted changes                 │
├─────────────────────────────────────────────────────┤
│ STATUS: 2 ISSUES FOUND                             │
│ Fix docs issues:                                    │
│   /craft:docs:lint --fix                           │
│   /craft:docs:check-links                          │
╰─────────────────────────────────────────────────────╯
```

### Validation Checklist

- [ ] Detects docs/ changes
- [ ] Runs both lint and link checks
- [ ] Reports issues in summary format
- [ ] Suggests fix commands
- [ ] Exit code = 1 (issues found)

---

## Summary of Test Results

### Expected Detections

| Test | Command | Issues Found | Auto-fixable |
|------|---------|--------------|--------------|
| Link checking | check-links default | 4 broken links | No |
| Markdown linting | lint default | 2 issues | Yes |
| Link checking (release) | check-links release | 5 issues (4 links + 1 anchor) | No |
| Markdown linting (debug) | lint debug | 2 issues (verbose) | Yes |
| Auto-fix | lint --fix | 2 issues fixed | Yes |
| Pre-commit hook | git commit | Blocks if issues | Partial |
| Integration | check | All issues | Partial |

### Performance Expectations

| Command | Mode | Time Estimate |
|---------|------|---------------|
| check-links | default | < 1s (1 file) |
| check-links | release | < 2s (+ anchors) |
| lint | default | < 1s (1 file) |
| lint | debug | < 2s (verbose) |
| lint --fix | default | < 1s (auto-fix) |
| Pre-commit hook | - | < 6s (both checks) |

### Exit Codes

| Scenario | Exit Code | Meaning |
|----------|-----------|---------|
| No issues | 0 | Success |
| Auto-fixable only | 0 | Success (with --fix) |
| Manual fixes needed | 1 | Failure |
| Command error | 2 | Validation error |

---

## Manual Testing Procedure

To validate the commands work as documented:

1. **Test link checking:**

   ```bash
   /craft:docs:check-links docs/test-violations.md
   # Expect: 4 broken links detected
   ```

2. **Test markdown linting:**

   ```bash
   /craft:docs:lint docs/test-violations.md
   # Expect: 2 issues (MD032, MD040)
   ```

3. **Test auto-fix:**

   ```bash
   /craft:docs:lint --fix docs/test-violations.md
   # Expect: Both issues auto-fixed
   git diff docs/test-violations.md
   # Verify: Blank line added, language tag added
   ```

4. **Test pre-commit hook:**

   ```bash
   /craft:git:init
   # Select "Yes" for pre-commit hooks

   # Create test change
   echo "Test" >> docs/test-violations.md
   git add docs/test-violations.md
   git commit -m "test"
   # Expect: Hook runs and validates docs
   ```

5. **Test integration:**

   ```bash
   # Make docs change
   echo "Test" >> docs/test-violations.md
   git add docs/test-violations.md

   /craft:check
   # Expect: Docs validation runs automatically
   ```

---

## Cleanup

After testing, revert test changes:

```bash
# Revert file modifications
git checkout docs/test-violations.md

# Or remove entirely (if committed)
git rm docs/test-violations.md
git commit -m "chore: remove test violations file"
```

---

**Test Document Created:** 2026-01-15
**Related Commands:** /craft:docs:check-links, /craft:docs:lint, /craft:git:init, /craft:check
**PR:** #11
