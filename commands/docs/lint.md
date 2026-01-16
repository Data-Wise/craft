---
description: Markdown quality and error detection with auto-fix
category: docs
arguments:
  - name: mode
    description: Execution mode (default|debug|optimize|release)
    required: false
    default: default
  - name: path
    description: Specific file or directory to lint
    required: false
  - name: fix
    description: Auto-fix safe issues
    required: false
    default: false
  - name: dry-run
    description: Preview checks without executing them
    required: false
    default: false
    alias: -n
---

# /craft:docs:lint - Markdown Quality Checks

Detect and fix markdown formatting errors with embedded rules and auto-fix capability.

## Purpose

**Error detection focus, not style enforcement:**
- List formatting (blank lines before lists) - CRITICAL
- Code fence formatting (missing language tags)
- Link formatting consistency
- Structural issues that break rendering

## Philosophy

> **"Auto-fix what's safe, prompt for what matters."**

## Usage

```bash
# DEFAULT: Detect errors (no auto-fix)
/craft:docs:lint

# AUTO-FIX: Fix safe issues automatically
/craft:docs:lint --fix

# MODES: Different thoroughness levels
/craft:docs:lint default        # Quick error check (< 10s)
/craft:docs:lint debug          # Verbose with context (< 120s)
/craft:docs:lint optimize       # Parallel checking (< 180s)
/craft:docs:lint release --fix  # Comprehensive + auto-fix (< 300s)

# SPECIFIC PATH
/craft:docs:lint docs/guide/    # Check specific directory
/craft:docs:lint README.md      # Check specific file

# DRY-RUN: Preview what will be checked
/craft:docs:lint --dry-run
/craft:docs:lint release -n
```

## Modes

| Mode | Time | Focus | Use Case |
|------|------|-------|----------|
| **default** | < 10s | Critical errors only | Quick pre-commit check |
| **debug** | < 120s | + Context + suggestions | Troubleshooting issues |
| **optimize** | < 180s | + Parallel processing | Large doc sets |
| **release** | < 300s | + All rules + strict | Pre-release validation |

## Embedded Rules Configuration

**No separate config file** - rules are embedded in the command for consistency.

### Critical Rules (Always Enabled)

```javascript
const criticalRules = {
  // List formatting - CRITICAL (breaks rendering)
  "MD032": true,  // Blank lines around lists

  // Code fence formatting
  "MD040": true,  // Code fence language tag required

  // Link formatting
  "MD011": true,  // Reversed link syntax [](text)[url]
  "MD042": true,  // No empty links
  "MD051": true,  // Link fragments should be valid

  // Trailing whitespace
  "MD009": true,  // No trailing spaces
  "MD010": true,  // No hard tabs
};
```

### Relaxed Rules (Craft-Specific)

```javascript
const relaxedRules = {
  // Line length - disabled (long command examples)
  "MD013": false,

  // Inline HTML - allowed (skill/agent tags: <*>, <commentary>)
  "MD033": {
    "allowed_elements": ["antml:*", "commentary", "example", "user", "response"]
  },

  // Duplicate headers - siblings only (multiple "Examples" sections valid)
  "MD024": { "siblings_only": true },

  // First line heading - disabled (frontmatter in commands/skills/agents)
  "MD041": false,

  // Emphasis style - disabled (mixed *italic* and **bold** is fine)
  "MD049": false,
  "MD050": false,
};
```

## When Invoked

### Step 1: Detect Scope

```bash
# Determine what to check
if [ -n "$path" ]; then
  # Specific path provided
  if [ -f "$path" ]; then
    FILES="$path"
  elif [ -d "$path" ]; then
    FILES=$(find "$path" -name "*.md" -type f)
  fi
else
  # Default: all docs
  FILES=$(find docs/ -name "*.md" -type f 2>/dev/null)
  FILES+=" "$(ls *.md CLAUDE.md 2>/dev/null)
fi

echo "Checking ${#FILES[@]} markdown files..."
```

### Step 2: Run Linting (Mode-Specific)

#### Default Mode: Critical Errors Only

```
🔍 LINTING MARKDOWN (Critical errors only)...

docs/test-violations.md:
  ✗ Line 21: MD032 - Missing blank line before list
    19: ## Test Case 3: Markdown Linting Issues
    20: Some text without blank line before list:
    21: - Item 1
    22: - Item 2

  ✗ Line 26: MD040 - Code fence missing language tag
    25: ### Code Fence Without Language Tag
    26: ```
    27: This code fence has no language tag

docs/guide/setup.md:
  ✗ Line 45: MD009 - Trailing spaces detected
    45: Follow these steps carefully.

Summary:
  Files checked: 48
  Issues found: 3
  Auto-fixable: 3
  Manual fix needed: 0
```

#### Debug Mode: + Verbose Context

```
🔍 DEBUG: Markdown Linting with Context

docs/test-violations.md:21 (MD032):
  Rule: Lists should be surrounded by blank lines
  Severity: Error
  Auto-fixable: Yes

  Context (lines 19-24):
    19: ## Test Case 3: Markdown Linting Issues
    20:
    21: Some text without blank line before list:
    22: - Item 1
    23: - Item 2
    24: - Item 3

  Fix:
    Add blank line after line 21:

    21: Some text without blank line before list:
    22:
    23: - Item 1

docs/test-violations.md:26 (MD040):
  Rule: Code fences should have a language tag
  Severity: Error
  Auto-fixable: Yes

  Context (lines 25-29):
    25: ### Code Fence Without Language Tag
    26:
    27: ```
    28: This code fence has no language tag
    29: def example():

  Suggestion:
    Language appears to be: python (detected from content)

  Fix:
    27: ```python
    28: This code fence has no language tag
    29: def example():
```

#### Optimize Mode: + Parallel Processing

```
⚡ OPTIMIZE: Parallel Markdown Linting

Processing batches of 10 files concurrently...

[Batch 1/5] Checking 10 files... ✓ (0.8s)
[Batch 2/5] Checking 10 files... ✗ 2 issues (0.9s)
[Batch 3/5] Checking 10 files... ✓ (0.7s)
[Batch 4/5] Checking 10 files... ✓ (0.8s)
[Batch 5/5] Checking 8 files... ✗ 1 issue (0.6s)

Total time: 3.8 seconds (vs ~10s sequential)

Issues found:
  docs/test-violations.md:21 → MD032 (auto-fixable)
  docs/test-violations.md:26 → MD040 (auto-fixable)
  docs/guide/setup.md:45 → MD009 (auto-fixable)
```

#### Release Mode: + All Rules Strict

```
🎯 RELEASE: Comprehensive Markdown Validation

Phase 1: Critical errors... ✗ 3 issues found
Phase 2: Code quality...

Checking code block consistency...
  ⚠ docs/commands/index.md:45 - Inconsistent fence style
    Uses ``` and ~~~ in same file (prefer ```)

Checking heading hierarchy...
  ⚠ docs/guide/setup.md:78 - Skipped heading level
    ## Level 2 → #### Level 4 (should be ### Level 3)

Phase 3: Link style consistency...
  ⚠ Mixed link reference styles detected
    - docs/index.md: Uses inline links
    - docs/guide/: Uses reference links
    Recommendation: Choose one style for consistency

Summary:
  Critical errors: 3 (auto-fixable)
  Quality warnings: 3 (manual review recommended)
  Total issues: 6
```

### Step 3: Auto-Fix (If --fix Flag)

```
🔧 AUTO-FIXING SAFE ISSUES...

docs/test-violations.md:
  ✓ Fixed: MD032 - Added blank line before list (line 21)
  ✓ Fixed: MD040 - Added language tag 'python' (line 27)

docs/guide/setup.md:
  ✓ Fixed: MD009 - Removed trailing spaces (line 45)

Auto-fixed: 3 issues in 2 files

⚠ Manual Review Needed (3 warnings):
  1. docs/commands/index.md:45 - Inconsistent fence style
  2. docs/guide/setup.md:78 - Skipped heading level
  3. Multiple files - Mixed link reference styles

Run without --fix to see details of manual fixes needed.
```

### Step 4: Interactive Prompts (Complex Issues)

When auto-fix encounters complex issues requiring decisions:

```
🤔 COMPLEX ISSUE: Manual decision required

File: docs/guide/setup.md:78
Issue: Heading hierarchy skip (## → ####)

Current:
  76: ## Installation
  77:
  78: #### Advanced Options
  79:

Options:
  1. Change to ### (h3) - Recommended
  2. Add intermediate heading
  3. Skip this fix

Your choice (1-3, or 'a' to abort): _
```

## Auto-Fix Rules

### Automatically Fixed (Safe)

| Issue | Rule | Fix Applied |
|-------|------|-------------|
| Trailing spaces | MD009 | Remove spaces at line end |
| Hard tabs | MD010 | Convert to spaces |
| Blank lines around lists | MD032 | Add blank line before/after |
| Code fence language | MD040 | Detect & add language tag |
| Multiple blank lines | MD012 | Reduce to single blank line |

### Prompt for Decision (Complex)

| Issue | Rule | Action Required |
|-------|------|----------------|
| Heading hierarchy | MD001 | Choose level or restructure |
| Inconsistent fence style | MD048 | Choose ``` or ~~~ |
| Link style mixed | N/A | Choose inline or reference |
| Emphasis style | MD049/MD050 | Choose * or _ |

## Language Detection (MD040 Auto-Fix)

When code fence has no language tag, detect from content:

```bash
detect_language() {
  local content=$1

  # Python indicators
  if echo "$content" | grep -qE '(def |import |from .* import|class .*:)'; then
    echo "python"
  # JavaScript/TypeScript
  elif echo "$content" | grep -qE '(function |const |let |var |=>|import .* from)'; then
    echo "javascript"
  # Bash/Shell
  elif echo "$content" | grep -qE '(#!/bin/bash|echo |grep |sed |awk )'; then
    echo "bash"
  # JSON
  elif echo "$content" | grep -qE '^\s*[\{\[].*[\}\]]\s*$'; then
    echo "json"
  # YAML
  elif echo "$content" | grep -qE '^[a-z_]+:\s'; then
    echo "yaml"
  # Fallback
  else
    echo "text"
  fi
}
```

## Output Format

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:lint (default mode)                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ✓ Checked: 48 markdown files                                │
│                                                             │
│ ✗ Issues Found (3):                                         │
│   1. docs/test-violations.md:21 [MD032]                     │
│      Missing blank line before list                         │
│      Auto-fixable: Yes                                      │
│                                                             │
│   2. docs/test-violations.md:26 [MD040]                     │
│      Code fence missing language tag                        │
│      Auto-fixable: Yes (detected: python)                   │
│                                                             │
│   3. docs/guide/setup.md:45 [MD009]                         │
│      Trailing spaces                                        │
│      Auto-fixable: Yes                                      │
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ All issues are auto-fixable!                                │
│                                                             │
│ Run with --fix to apply fixes:                              │
│   /craft:docs:lint --fix                                    │
│                                                             │
│ Exit code: 0 (auto-fixable)                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**VS Code Integration (file:line:col format):**
```
docs/test-violations.md:21:1: MD032 - Missing blank line before list (auto-fixable)
docs/test-violations.md:26:1: MD040 - Code fence missing language tag (auto-fixable)
docs/guide/setup.md:45:30: MD009 - Trailing spaces (auto-fixable)
```

## Dry-Run Mode

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Markdown Linting                                  │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Mode: default (Critical errors only)                        │
│   Time budget: < 10 seconds                                   │
│   Focus: List formatting, code fences, trailing spaces       │
│                                                               │
│ ✓ Scope Detection:                                            │
│   - docs/ directory: 45 markdown files                        │
│   - Root level: 3 files (README.md, CLAUDE.md, CHANGELOG.md) │
│   - Total: 48 files to check                                  │
│                                                               │
│ ✓ Rules Enabled (Critical):                                   │
│   • MD032: Blank lines around lists                           │
│   • MD040: Code fence language tags                           │
│   • MD011: Reversed link syntax                               │
│   • MD042: No empty links                                     │
│   • MD009: No trailing spaces                                 │
│   • MD010: No hard tabs                                       │
│                                                               │
│ ✓ Rules Relaxed (Craft-specific):                             │
│   • MD013: Line length (disabled - long examples)            │
│   • MD033: Inline HTML (allowed - skill tags)                │
│   • MD024: Duplicate headers (siblings only)                  │
│   • MD041: First line heading (disabled - frontmatter)       │
│                                                               │
│ ✓ Auto-Fix Behavior:                                          │
│   • Without --fix: Report issues only                         │
│   • With --fix: Auto-fix safe issues                          │
│   • Complex issues: Interactive prompt                        │
│   • Exit code: 0 if auto-fixable, 1 if manual fix needed    │
│                                                               │
│ ⚠ Estimated Time: ~4 seconds (48 files)                       │
│                                                               │
│ 📊 Summary: 48 files, 6 critical rules, ~4s                   │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

### Release Mode Dry-Run

```bash
/craft:docs:lint release --dry-run
```

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Markdown Linting (Release Mode)                   │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Mode: release (Comprehensive validation)                    │
│   Time budget: < 300 seconds                                  │
│   Focus: All rules + strict checking                          │
│                                                               │
│ ✓ Validation Phases (3):                                      │
│                                                               │
│   Phase 1: Critical errors                                    │
│     • All critical rules from default mode                    │
│     • Estimated: ~4 seconds                                   │
│                                                               │
│   Phase 2: Code quality                                       │
│     • Code block consistency                                  │
│     • Heading hierarchy validation                            │
│     • Emphasis style consistency                              │
│     • Estimated: ~6 seconds                                   │
│                                                               │
│   Phase 3: Link style consistency                             │
│     • Inline vs reference link usage                          │
│     • URL consistency patterns                                │
│     • Estimated: ~3 seconds                                   │
│                                                               │
│ ✓ Total Estimated Time: ~13 seconds                           │
│                                                               │
│ ⚠ Strict Mode:                                                │
│   • Critical errors block release                             │
│   • Quality warnings reported but don't block                 │
│   • Auto-fix available for safe issues                        │
│                                                               │
│ 📊 Summary: 3 phases, comprehensive checks, ~13s              │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | All issues auto-fixable | ✓ Run with --fix to resolve |
| 1 | Manual fixes needed | ✗ Review and fix manually |
| 2 | Linting error | ✗ Check command syntax |

## Integration

**Called by:**
- `/craft:check` - Pre-flight validation
- Pre-commit hooks - Prevent broken markdown

**Works with:**
- `/craft:docs:check-links` - Link validation
- `/craft:site:check` - Site validation
- `/craft:ci:validate` - CI pipeline validation

## CI Pipeline Usage

```yaml
# .github/workflows/docs-quality.yml
- name: Lint Markdown Documentation
  run: |
    claude "/craft:docs:lint"
    # Exit code 0: auto-fixable
    # Exit code 1: manual fixes needed
```

## Examples

```bash
# Quick check before commit
/craft:docs:lint
# → Reports issues, suggests --fix

# Auto-fix safe issues
/craft:docs:lint --fix
# → Fixes trailing spaces, blank lines, code fences

# Debug specific file
/craft:docs:lint debug docs/guide/setup.md
# → Verbose output with suggestions

# Release validation
/craft:docs:lint release --fix
# → Comprehensive check + auto-fix

# Preview without executing
/craft:docs:lint --dry-run
# → Shows what will be checked
```

## Performance

| Files | Mode | Time |
|-------|------|------|
| 50 | default | ~4s |
| 50 | debug | ~12s |
| 50 | optimize | ~5s (parallel) |
| 50 | release | ~13s (+ quality checks) |

**Optimization Tips:**
- Use `optimize` mode for large doc sets (100+ files)
- Use specific paths for quick checks: `/craft:docs:lint docs/guide/`
- Default mode focuses on critical errors only

## Troubleshooting

### False Positives

**Issue:** Rule reports issue but it's intentional

```bash
# Disable specific rule for one section (inline comment)
<!-- markdownlint-disable MD033 -->
<invoke name="tool">
  This HTML is intentional for Claude Code
</invoke>
<!-- markdownlint-enable MD033 -->
```

### Auto-Fix Changed Too Much

**Issue:** Auto-fix modified something incorrectly

```bash
# Review changes before committing
git diff

# Revert specific file
git checkout -- docs/file.md

# Or revert all changes
git reset --hard HEAD
```

### Language Detection Wrong

**Issue:** Code fence language auto-detected incorrectly

```bash
# Debug mode shows detection
/craft:docs:lint debug file.md

# Manually correct in file
# Before: ```python (incorrect)
# After:  ```javascript (correct)
```

## See Also

- `/craft:docs:check-links` - Documentation link validation
- `/craft:docs:check` - Full documentation health check
- `/craft:code:lint` - Code linting (similar pattern)
- Template: `templates/dry-run-pattern.md`
