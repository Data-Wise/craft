---
description: Markdown quality and error detection with auto-fix
category: docs
arguments:
  - name: path
    description: "Specific file or directory to lint (default: .)"
    required: false
    default: .
  - name: fix
    description: "Auto-fix safe issues (--fix flag)"
    required: false
    default: false
    alias: --fix
---

# /craft:docs:lint - Markdown Quality Checks

Detect and fix markdown formatting errors with embedded rules and auto-fix capability.

## Purpose

**Error detection focus, not style enforcement:**

- List formatting (blank lines before lists) - CRITICAL
- Code fence formatting (missing language tags)
- Link formatting consistency
- Structural issues that break rendering

## Execution

**v2.8.0:** The command now executes via `scripts/docs-lint.sh`, which delegates to `markdownlint-cli2`.

```bash
# Basic check
bash scripts/docs-lint.sh

# Auto-fix with confirmation
bash scripts/docs-lint.sh --fix

# Check specific path
bash scripts/docs-lint.sh docs/guide/
```

**Tool Detection (resolution order):**

- Local install: `./node_modules/.bin/markdownlint-cli2` (preferred, from `npm ci`)
- Global install: `markdownlint-cli2` (fast)
- Fallback: `npx markdownlint-cli2` (auto-downloads, slower first run)

**Installation:** `npm ci` (uses pinned version from `package-lock.json`)

## Philosophy

> **"Auto-fix what's safe, prompt for what matters."**

## Feature Status (v2.8.0 MVP)

| Feature | Status | Details |
|---------|--------|---------|
| Basic linting | ✅ v2.8.0 | Check markdown against 30+ rules |
| Auto-fix (--fix) | ✅ v2.8.0 | Apply fixes for safe issues |
| Config (.markdownlint.json) | ✅ v2.8.0 | 30 rules already configured |
| Pre-commit hook | ✅ v2.8.0 | Auto-fix on staged markdown |
| Modes (debug/optimize/release) | 📝 v2.9.0 | Planned with enhanced output |
| Styled output boxes | 📝 v2.9.0 | Planned for better readability |
| Interactive prompts | 📝 v2.9.0 | Planned for complex issues |
| Language detection (MD040) | 📝 v2.9.0 | Planned for code fences |
| Rule expansion (30 → 42) | 📝 v2.9.0 | Planned additional rules |

## Tool Installation

**Primary Tool:** `markdownlint-cli2`

### Recommended: Global Install (Faster)

```bash
npm install -g markdownlint-cli2

# Verify
markdownlint-cli2 --help
```

### Fallback: npx (Auto-downloads)

If not installed globally, the command automatically falls back to npx:

```bash
# This happens automatically if markdownlint-cli2 not found
npx markdownlint-cli2 "**/*.md" --config .markdownlint.json
```

## Usage

**Current (v2.8.0 - MVP):**

```bash
# Check markdown files
/craft:docs:lint

# Check with auto-fix
/craft:docs:lint --fix

# Check specific path
/craft:docs:lint docs/guide/
```

**Future (planned for v2.9.0+):**

```bash
# Advanced modes: debug, optimize, release
/craft:docs:lint debug          # Verbose with context
/craft:docs:lint optimize       # Parallel processing
/craft:docs:lint release --fix  # Comprehensive + auto-fix

# Raw output
/craft:docs:lint --verbose

# Dry-run preview
/craft:docs:lint --dry-run
```

## Modes

| Mode | Time | Focus | Use Case |
|------|------|-------|----------|
| **default** | < 10s | Critical errors only | Quick pre-commit check |
| **debug** | < 120s | + Context + suggestions | Troubleshooting issues |
| **optimize** | < 180s | + Parallel processing | Large doc sets |
| **release** | < 300s | + All rules + strict | Pre-release validation |

## When Invoked

### Step 0: Detect Tool Availability

```bash
# Check for global install first (faster)
if command -v markdownlint-cli2 &>/dev/null; then
  LINT_CMD="markdownlint-cli2"
  echo "Using global markdownlint-cli2"
else
  LINT_CMD="npx markdownlint-cli2"
  echo "Using npx (install globally for faster runs: npm i -g markdownlint-cli2)"
fi
```

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

**Styled Output (default):**

```text
╭─ /craft:docs:lint ──────────────────────────────────────────╮
│                                                             │
│ docs/test-violations.md:                                    │
│   Line 21: MD032 - Missing blank line before list           │
│   Line 26: MD040 - Code fence missing language tag          │
│                                                             │
│ docs/guide/setup.md:                                        │
│   Line 45: MD009 - Trailing spaces detected                 │
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│ Files checked: 48 | Issues found: 3 | Auto-fixable: 3       │
│                                                             │
│ Run with --fix to apply fixes                               │
╰─────────────────────────────────────────────────────────────╯
```

**Verbose Output (--verbose flag):**

```text
docs/test-violations.md:21:1 MD032/blanks-around-lists Lists should be surrounded by blank lines [Context: "- Item 1"]
docs/test-violations.md:26:1 MD040/fenced-code-language Fenced code blocks should have a language specified [Context: "```"]
docs/guide/setup.md:45:30 MD009/no-trailing-spaces Trailing spaces [Expected: 0 or 2; Actual: 3]
```

#### Debug Mode: + Verbose Context

```text
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

```text
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

```text
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

### Step 3: Preview Before Fix (--fix Flag)

**CRITICAL:** Always show preview before applying fixes.

```text
╭─ Preview: 5 files will be modified ─────────────────────────╮
│                                                             │
│ docs/guide/setup.md:                                        │
│   Line 21: Add blank line before list (MD032)               │
│   Line 45: Remove trailing space (MD009)                    │
│                                                             │
│ docs/reference/api.md:                                      │
│   Line 15: Change '* ' to '- ' (MD004)                      │
│                                                             │
│ README.md:                                                  │
│   Line 8: Convert bare URL to <url> (MD034)                 │
│   Line 42: Add language tag 'bash' (MD040)                  │
│                                                             │
╰─────────────────────────────────────────────────────────────╯

Apply these 5 fixes? [y/N]: _
```

**If confirmed (y):**

```text
🔧 Applying fixes...

✓ docs/guide/setup.md: 2 fixes applied
✓ docs/reference/api.md: 1 fix applied
✓ README.md: 2 fixes applied

Total: 5 fixes applied in 3 files

Re-running lint check...
╭─ /craft:docs:lint ──────────────────────────────────────────╮
│ ✓ All checks passed! 48 files, 0 issues                     │
╰─────────────────────────────────────────────────────────────╯
```

### Step 4: Interactive Prompts (Complex Issues)

When auto-fix encounters complex issues requiring decisions:

#### MD040: Unknown Code Fence Language

```text
🤔 COMPLEX ISSUE: Code fence language unknown

File: docs/examples.md:45
Issue: Code fence has no language tag and content is ambiguous

Context:
  44:
  45: ```
  46: CREATE TABLE users (id INT, name VARCHAR(255));
  47: SELECT * FROM users WHERE id = 1;
  48: ```

Which language should this be?
  1. sql (Recommended - detected SQL keywords)
  2. text (Plain text, no highlighting)
  3. Enter custom language
  4. Skip this fix

Your choice (1-4): _
```

#### MD001: Heading Hierarchy Skip

```text
🤔 COMPLEX ISSUE: Heading hierarchy skip

File: docs/guide/setup.md:78
Issue: Heading levels skip from ## to ####

Current:
  76: ## Installation
  77:
  78: #### Advanced Options
  79:

Options:
  1. Change #### to ### (Recommended - adjust level)
  2. Add intermediate ### heading before line 78
  3. Skip this fix

Your choice (1-3): _
```

## Embedded Rules Configuration

**No separate config file** - rules are embedded in the command for consistency.

### Critical Rules (Always Enabled)

```javascript
const criticalRules = {
  // List formatting - CRITICAL (breaks rendering)
  "MD030": {          // Spaces after list marker
    "ul_single": 1,   // Unordered: exactly 1 space
    "ol_single": 1,   // Ordered: exactly 1 space
    "ul_multi": 1,    // Multi-paragraph: 1 space
    "ol_multi": 1     // Multi-ordered: 1 space
  },
  "MD032": true,      // Blank lines around lists
  "MD004": {          // Consistent list marker style
    "style": "dash"   // Use '-' not '*' or '+'
  },
  "MD005": true,      // Consistent list indentation
  "MD007": {          // Unordered list indentation
    "indent": 2       // 2-space indent
  },
  "MD029": {          // Ordered list prefix
    "style": "one_or_ordered"
  },
  "MD031": true,      // Blank lines inside code blocks

  // Code fence formatting
  "MD040": true,      // Code fence language tag required
  "MD046": {          // Code block style
    "style": "fenced"
  },
  "MD048": {          // Code fence style
    "style": "backtick"
  },

  // Heading formatting
  "MD003": {          // Heading style
    "style": "atx"    // # style headings
  },
  "MD022": true,      // Blank lines around headings
  "MD023": true,      // Headings start at line beginning
  "MD036": true,      // No emphasis as heading

  // Link formatting
  "MD011": true,      // Reversed link syntax [](text)[url]
  "MD042": true,      // No empty links
  "MD045": true,      // Image alt text required
  "MD052": true,      // Reference links use references
  "MD056": true,      // Table column count

  // Whitespace
  "MD009": true,      // No trailing spaces
  "MD010": true,      // No hard tabs
  "MD012": true,      // No multiple blank lines

  // Inline
  "MD034": true,      // No bare URLs (auto-convert to <url>)
};
```

### Relaxed Rules (Craft-Specific)

```javascript
const relaxedRules = {
  // Line length - disabled (long command examples)
  "MD013": false,

  // Inline HTML - allowed (skill/agent tags: <*>, <commentary>)
  "MD033": {
    "allowed_elements": [
      "antml:*", "commentary", "example", "user", "response",
      "antml:function_calls", "antml:invoke", "antml:parameter"
    ]
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

## Auto-Fix Rules

### Automatically Fixed (Safe - No Confirmation)

| Issue | Rule | Fix Applied |
|-------|------|-------------|
| Trailing spaces | MD009 | Remove spaces at line end |
| Hard tabs | MD010 | Convert to spaces |
| Multiple blank lines | MD012 | Reduce to single blank line |
| Blank lines around lists | MD032 | Add blank line before/after |
| **List spacing** | **MD030** | **Normalize to 1 space after marker** |
| **Inconsistent marker** | **MD004** | **Change to '-' consistently** |
| **Bare URLs** | **MD034** | **Convert to `<url>` format** |
| **Emoji-attribute spacing** | **CRAFT-001** | **Remove space between `:emoji:` and `{`** |

### Auto-Fix with Language Detection (MD040)

| Content Pattern | Detected Language |
|-----------------|-------------------|
| `def`, `import`, `class X:` | python |
| `function`, `const`, `=>` | javascript |
| `#!/bin/bash`, `echo`, `grep` | bash |
| `{`, `[`, JSON structure | json |
| `key: value` pattern | yaml |
| SQL keywords | sql |
| Fallback | text |

### Prompt for Decision (Complex)

| Issue | Rule | Action Required |
|-------|------|-----------------|
| Heading hierarchy skip | MD001 | Choose level or restructure |
| Unknown code language | MD040 | Select from options or enter custom |
| Inconsistent fence style | MD048 | Choose ``` or ~~~ |

## Emoji-Attribute Spacing (CRAFT-001)

**What it catches:**

MkDocs `attr_list` extension requires attributes to be directly adjacent to the preceding element. A space between an emoji shortcode and its attribute list causes literal text rendering:

```markdown
<!-- BROKEN: space before { — renders as literal "{ .lg .middle }" text -->
:rocket: { .lg .middle }

<!-- CORRECT: no space — attr_list attaches classes to the emoji SVG -->
:rocket:{ .lg .middle }
```

**Why it matters:**

- Prettier and other formatters may insert a space before `{` automatically
- The `attr_list` extension silently fails — no build error, just broken rendering
- Affects grid cards, icon sizing, and any emoji with CSS class attributes

**Rule ID:** `CRAFT-001` (custom — not a markdownlint rule)

**Auto-fix:** Removes space(s) between `:emoji:` and `{` when run with `--fix`

## List Spacing Enforcement (v2.5.1)

**What it catches:**

- Extra spaces after list markers: `-  Item` → `- Item`
- Inconsistent markers: `* Item` → `- Item`
- Missing blank lines before/after lists

**Why it matters:**

- Consistent rendering across GitHub, MkDocs, VS Code
- Portable documentation (works everywhere)
- Follows markdown best practices

**Auto-fix examples:**

```markdown
<!-- Before -->
Some text
- Item with 2 spaces
* Different marker

<!-- After -->
Some text

- Item with 1 space
- Consistent marker
```

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
  # SQL
  elif echo "$content" | grep -qiE '(SELECT |INSERT |UPDATE |DELETE |CREATE TABLE|DROP )'; then
    echo "sql"
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

### Styled Output (Default)

```text
╭─ /craft:docs:lint (default mode) ───────────────────────────╮
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
╰─────────────────────────────────────────────────────────────╯
```

### Verbose Output (--verbose)

```text
docs/test-violations.md:21:1: MD032 - Missing blank line before list (auto-fixable)
docs/test-violations.md:26:1: MD040 - Code fence missing language tag (auto-fixable)
docs/guide/setup.md:45:30: MD009 - Trailing spaces (auto-fixable)
```

## Dry-Run Mode

```text
╭─ DRY RUN: Markdown Linting ─────────────────────────────────╮
│                                                             │
│ ✓ Tool Detection:                                           │
│   - markdownlint-cli2: Global install detected              │
│   - Command: markdownlint-cli2 "**/*.md" --config ...       │
│                                                             │
│ ✓ Mode: default (Critical errors only)                      │
│   Time budget: < 10 seconds                                 │
│   Focus: List formatting, code fences, trailing spaces      │
│                                                             │
│ ✓ Scope Detection:                                          │
│   - docs/ directory: 45 markdown files                      │
│   - Root level: 3 files (README.md, CLAUDE.md, CHANGELOG.md)│
│   - Total: 48 files to check                                │
│                                                             │
│ ✓ Rules Enabled (30 rules in .markdownlint.json):           │
│   Critical: MD004, MD005, MD007, MD009, MD010, MD012,       │
│             MD029, MD030, MD031, MD032, MD034, MD040        │
│   Headings: MD003, MD022, MD023, MD024, MD036               │
│   Code: MD046, MD048                                        │
│   Links: MD011, MD042, MD045, MD052, MD056                  │
│                                                             │
│ ✓ Rules Relaxed (Craft-specific):                           │
│   • MD013: Line length (disabled - long examples)           │
│   • MD033: Inline HTML (allowed - skill tags)               │
│   • MD041: First line heading (disabled - frontmatter)      │
│   • MD049/MD050: Emphasis style (disabled)                  │
│                                                             │
│ ✓ Auto-Fix Behavior:                                        │
│   • Without --fix: Report issues only                       │
│   • With --fix: Preview first, then apply with confirmation │
│   • Complex issues: Interactive prompt                      │
│   • Exit code: 0 if auto-fixable, 1 if manual fix needed    │
│                                                             │
│ ⚠ Estimated Time: ~4 seconds (48 files)                     │
│                                                             │
│ 📊 Summary: 48 files, 30 rules, ~4s                         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                            │
╰─────────────────────────────────────────────────────────────╯
```

### Release Mode Dry-Run

```bash
/craft:docs:lint release --dry-run
```

```text
╭─ DRY RUN: Markdown Linting (Release Mode) ──────────────────╮
│                                                             │
│ ✓ Mode: release (Comprehensive validation)                  │
│   Time budget: < 300 seconds                                │
│   Focus: All rules + strict checking                        │
│                                                             │
│ ✓ Validation Phases (3):                                    │
│                                                             │
│   Phase 1: Critical errors                                  │
│     • All critical rules from default mode                  │
│     • Estimated: ~4 seconds                                 │
│                                                             │
│   Phase 2: Code quality                                     │
│     • Code block consistency                                │
│     • Heading hierarchy validation                          │
│     • Emphasis style consistency                            │
│     • Estimated: ~6 seconds                                 │
│                                                             │
│   Phase 3: Link style consistency                           │
│     • Inline vs reference link usage                        │
│     • URL consistency patterns                              │
│     • Estimated: ~3 seconds                                 │
│                                                             │
│ ✓ Total Estimated Time: ~13 seconds                         │
│                                                             │
│ ⚠ Strict Mode:                                              │
│   • Critical errors block release                           │
│   • Quality warnings reported but don't block               │
│   • Auto-fix available for safe issues                      │
│                                                             │
│ 📊 Summary: 3 phases, comprehensive checks, ~13s            │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                            │
╰─────────────────────────────────────────────────────────────╯
```

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | All issues auto-fixable or no issues | ✓ Run with --fix to resolve |
| 1 | Manual fixes needed | ✗ Review and fix manually |
| 2 | Linting error | ✗ Check command syntax |

## Integration

**Called by:**

- `/craft:check` - Pre-flight validation
- `/craft:code:lint` - Delegates markdown files here
- Pre-commit hooks - Prevent broken markdown

**Works with:**

- `/craft:docs:check-links` - Link validation
- `/craft:site:check` - Site validation (calls lint before build)
- `/craft:ci:validate` - CI pipeline validation

## CI Pipeline Usage

```yaml
# .github/workflows/docs-quality.yml
- name: Lint Markdown Documentation
  run: |
    npx markdownlint-cli2 "**/*.md" --config .markdownlint.json
    # Exit code 0: no issues
    # Exit code 1: issues found
```

## Examples

```bash
# Quick check before commit
/craft:docs:lint
# → Reports issues with styled output

# Raw output for piping/scripting
/craft:docs:lint --verbose
# → Raw markdownlint output

# Preview and apply fixes
/craft:docs:lint --fix
# → Shows preview, asks confirmation, applies fixes

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

- Install globally: `npm i -g markdownlint-cli2` (faster than npx)
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

### Tool Not Found

**Issue:** markdownlint-cli2 not installed

```bash
# Install globally (recommended)
npm install -g markdownlint-cli2

# Or use npx (slower, auto-downloads)
npx markdownlint-cli2 --help
```

## See Also

- `/craft:docs:check-links` - Documentation link validation
- `/craft:docs:check` - Full documentation health check
- `/craft:code:lint` - Code linting (delegates markdown here)
- `/craft:site:check` - Site validation (includes lint step)
- Template: `templates/dry-run-pattern.md`
