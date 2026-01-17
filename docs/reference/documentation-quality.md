# Documentation Quality API Reference

> **TL;DR** (30 seconds)
>
> - **Commands**: `/craft:docs:check-links`, `/craft:docs:lint`
> - **Purpose**: Validate markdown quality and internal links automatically
> - **Exit Codes**: 0 (success/auto-fixed), 1 (manual fix needed), 2 (validation error)
> - **Integration**: Pre-commit hooks, CI/CD, `/craft:check` command

Complete API reference for Craft's documentation quality automation system.

!!! info "Related Documentation"
    - **[User Guide](../guide/documentation-quality.md)** - Step-by-step tutorial for using quality commands
    - **[Development Guide](../guide/documentation-quality-development.md)** - Contributing to the quality system

## Commands Overview

| Command | Purpose | Modes | Dry-run | Auto-fix |
|---------|---------|-------|---------|----------|
| `/craft:docs:check-links` | Validate internal links and anchors | 4 | ✅ | ❌ |
| `/craft:docs:lint` | Check markdown quality and style | 4 | ✅ | ✅ |

## /craft:docs:check-links

Validates internal documentation links (relative and absolute paths) with optional anchor checking.

### Syntax

```bash
/craft:docs:check-links [mode] [path] [--dry-run]
```

### Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `mode` | string | No | `default` | Execution mode: `default`, `debug`, `optimize`, `release` |
| `path` | string | No | `docs/` | Specific file or directory to check |
| `--dry-run`, `-n` | flag | No | `false` | Preview checks without executing |

### Execution Modes

#### default (< 10s)

Quick validation of internal links only. Best for development workflow.

```bash
/craft:docs:check-links
/craft:docs:check-links default
```

**Checks:**

- ✅ Relative path links (`[text](../file.md)`)
- ✅ Absolute path links (`[text](/docs/file.md)`)
- ✅ File existence validation
- ❌ Anchor validation (skipped)

#### debug (< 120s)

Verbose output with detailed traces. Use when debugging link issues.

```bash
/craft:docs:check-links debug
/craft:docs:check-links debug docs/commands/
```

**Features:**

- Verbose logging of each check
- Detailed error messages with file paths
- Link resolution traces
- Skipped file reporting

#### optimize (< 180s)

Optimized for CI/CD with performance tuning.

```bash
/craft:docs:check-links optimize --dry-run
```

**Features:**

- Parallel processing where possible
- Minimal output (errors only)
- Performance optimizations
- CI-friendly formatting

#### release (< 300s)

Comprehensive validation including anchor checking. Use before releases.

```bash
/craft:docs:check-links release
```

**Checks:**

- ✅ All default mode checks
- ✅ **Anchor validation** (`[text](file.md#section)`)
- ✅ Header existence in target files
- ✅ Case-sensitive anchor matching

### Exit Codes

| Code | Meaning | Action Required |
|------|---------|-----------------|
| 0 | All links valid | None - success |
| 1 | Broken links found | Fix broken links manually |
| 2 | Invalid arguments | Check command syntax |

### Output Format

**Success:**

```
✅ Link validation passed (32 links checked)
```

**Errors (VS Code clickable format):**

```
docs/commands/git.md:15:1: Broken link → ../missing-file.md
docs/guide/tutorial.md:42:3: Broken anchor → guide.md#non-existent
```

### Link Types Validated

#### Relative Links

```markdown
[Link to sibling](./other-file.md)
[Link to parent](../parent-file.md)
[Link with anchor](./file.md#section)
```

#### Absolute Links

```markdown
[Root link](/docs/commands/git.md)
[Root with anchor](/docs/guide/tutorial.md#getting-started)
```

#### Links NOT Checked

- External URLs (`https://`, `http://`)
- Mailto links (`mailto:`)
- Protocol-relative URLs (`//example.com`)
- Fragment-only anchors (`#section`) - checked in release mode within same file

### Configuration

Link checking behavior is configured via `.markdown-link-check.json`:

```json
{
  "ignorePatterns": [
    { "pattern": "^https://example.com" },
    { "pattern": "^http://localhost" }
  ],
  "timeout": "10s",
  "retryOn429": true,
  "retryCount": 3
}
```

### Examples

#### Check all documentation

```bash
/craft:docs:check-links
```

#### Check specific file

```bash
/craft:docs:check-links default docs/commands/git.md
```

#### Preview checks without execution

```bash
/craft:docs:check-links --dry-run
```

#### Comprehensive validation before release

```bash
/craft:docs:check-links release
```

#### Debug link issues

```bash
/craft:docs:check-links debug docs/guide/
```

### Integration with Other Commands

#### /craft:check

Automatically runs link validation when docs/ changes detected:

```bash
/craft:check  # Includes link validation if docs modified
```

#### /craft:git:init

Pre-commit hooks can auto-validate links:

```bash
/craft:git:init  # Step 6.5: Enable pre-commit hooks
```

#### CI/CD

GitHub Actions workflow (`.github/workflows/docs-quality.yml`):

```yaml
- name: Check documentation links
  run: |
    npx markdown-link-check docs/**/*.md
```

---

## /craft:docs:lint

Validates markdown quality with auto-fix capability for safe issues.

### Syntax

```bash
/craft:docs:lint [mode] [path] [--fix] [--dry-run]
```

### Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `mode` | string | No | `default` | Execution mode: `default`, `debug`, `optimize`, `release` |
| `path` | string | No | `docs/` | Specific file or directory to lint |
| `--fix` | flag | No | `false` | Automatically fix safe issues |
| `--dry-run`, `-n` | flag | No | `false` | Preview linting without execution |

### Execution Modes

#### default (< 10s)

Quick quality check focusing on critical errors.

```bash
/craft:docs:lint
/craft:docs:lint default --fix
```

**Checks:**

- ✅ Critical markdown errors (MD032, MD040, MD009)
- ✅ Basic formatting issues
- ❌ Style preferences (skipped)

#### debug (< 120s)

Verbose output with rule explanations.

```bash
/craft:docs:lint debug docs/guide/tutorial.md
```

**Features:**

- Detailed rule violation explanations
- Line-by-line analysis
- Fix suggestions for each error
- Rule reference links

#### optimize (< 180s)

Optimized for CI/CD performance.

```bash
/craft:docs:lint optimize --fix
```

**Features:**

- Parallel file processing
- Minimal output
- Fast rule evaluation
- CI-friendly exit codes

#### release (< 300s)

Comprehensive validation including style checks.

```bash
/craft:docs:lint release
```

**Checks:**

- ✅ All critical and moderate rules
- ✅ Style consistency (line length, spacing)
- ✅ Accessibility requirements
- ✅ Best practices validation

### Auto-fix Capability

The `--fix` flag automatically corrects safe issues:

#### Auto-fixable Issues ✅

```markdown
# MD009: Trailing spaces removed
Line with trailing spaces   →  Line with trailing spaces

# MD010: Hard tabs converted to spaces
 Indented with tab  →      Indented with spaces

# MD012: Multiple blank lines reduced
Line 1

Line 2  →  Line 1

Line 2

# MD040: Code fence language tags added
```

code here
```→```bash
code here

```
```

#### Manual Fix Required ❌

```markdown
# MD032: Blank lines around lists (context-dependent)
# MD011: Reversed link syntax [link](text) vs (text)[link]
# MD042: Empty links [text]()
```

### Exit Codes

| Code | Meaning | Action Required |
|------|---------|-----------------|
| 0 | No errors or all auto-fixed | None - success |
| 1 | Manual fixes required | Review and fix reported issues |
| 2 | Configuration/syntax error | Check command arguments |

### Output Format

**Success with auto-fix:**

```
✅ Markdown quality passed (12 issues auto-fixed)
   → Removed 8 trailing spaces
   → Fixed 4 code fence language tags
```

**Manual fixes required:**

```
docs/guide/tutorial.md:23:1: MD032 - Blank lines around lists
docs/commands/git.md:15:45: MD011 - Reversed link syntax
```

### Linting Rules

#### Critical Rules (Always Checked)

| Rule | Name | Auto-fix | Description |
|------|------|----------|-------------|
| MD032 | blanks-around-lists | ❌ | Blank lines required around lists |
| MD040 | fenced-code-language | ✅ | Code fences must specify language |
| MD011 | no-reversed-links | ❌ | Link syntax must be `[text](url)` |
| MD042 | no-empty-links | ❌ | Links must have non-empty URLs |
| MD009 | no-trailing-spaces | ✅ | No trailing spaces on lines |
| MD010 | no-hard-tabs | ✅ | Use spaces instead of tabs |

#### Language Detection

Auto-fix intelligently detects code fence languages:

```javascript
// Pattern matching for language detection
if (/^(function|const|let|var|=>)/.test(code)) return 'javascript';
if (/^(def |import |class |from )/.test(code)) return 'python';
if (/^(echo|cd|ls|git|npm|#!/bin)/.test(code)) return 'bash';
if (/^[{[]/.test(code) && /[}\]]$/.test(code)) return 'json';
```

#### Moderate Rules (Release Mode)

| Rule | Name | Auto-fix | Description |
|------|------|----------|-------------|
| MD013 | line-length | ❌ | Line length limits |
| MD024 | no-duplicate-headings | ❌ | Unique heading text |
| MD033 | no-inline-html | ❌ | Restrict HTML elements |

### Configuration

Linting rules embedded in command, but can be customized via `.markdownlint.json`:

```json
{
  "default": true,
  "MD013": false,
  "MD033": {
    "allowed_elements": ["antml:*", "commentary", "example"]
  },
  "MD024": {
    "siblings_only": true
  }
}
```

### Examples

#### Lint all documentation

```bash
/craft:docs:lint
```

#### Auto-fix safe issues

```bash
/craft:docs:lint --fix
```

#### Lint specific file

```bash
/craft:docs:lint default docs/guide/tutorial.md
```

#### Preview auto-fixes

```bash
/craft:docs:lint --fix --dry-run
```

#### Debug linting issues

```bash
/craft:docs:lint debug docs/commands/ --fix
```

#### Comprehensive pre-release check

```bash
/craft:docs:lint release
```

### Integration with Other Commands

#### /craft:check

Automatically runs linting when docs/ changes detected:

```bash
/craft:check  # Includes lint validation if docs modified
```

#### Pre-commit Hooks

Auto-lint and fix before each commit:

```bash
# .git/hooks/pre-commit
if [ -n "$STAGED_MD" ]; then
  claude "/craft:docs:lint --fix"
  git add $STAGED_MD  # Re-stage auto-fixed files
fi
```

#### CI/CD

GitHub Actions workflow:

```yaml
- name: Lint documentation
  run: markdownlint-cli2 "docs/**/*.md"
```

---

## Combined Workflow

### Development Cycle

```mermaid
graph LR
    A[Edit Docs] --> B{Run /craft:check}
    B -->|Docs Changed| C[/craft:docs:lint --fix]
    C --> D[/craft:docs:check-links]
    D -->|Pass| E[Commit]
    D -->|Fail| F[Fix Issues]
    F --> A
    E --> G[Pre-commit Hook]
    G -->|Auto-fix| H[Staged]
    G -->|Errors| I[Abort Commit]
    I --> F
```

### Pre-commit Hook Flow

```bash
#!/bin/bash
# .git/hooks/pre-commit (auto-generated by /craft:git:init)

STAGED_MD=$(git diff --cached --name-only | grep '^docs/.*\.md$')

if [ -n "$STAGED_MD" ]; then
  echo "📚 Checking documentation quality..."

  # Step 1: Lint with auto-fix
  claude "/craft:docs:lint --fix" || exit 1

  # Step 2: Validate links
  claude "/craft:docs:check-links default" || exit 1

  # Re-stage auto-fixed files
  git add $STAGED_MD
fi
```

### CI/CD Pipeline

```yaml
name: Documentation Quality

on:
  pull_request:
    paths: ['docs/**/*.md']

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Lint markdown
        run: markdownlint-cli2 "docs/**/*.md"

  links:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check links
        uses: lycheeverse/lychee-action@v1
        with:
          args: --verbose docs/**/*.md
```

---

## Error Reference

### Common Errors

#### Broken Link Errors

```
docs/guide/tutorial.md:15:1: Broken link → ../missing.md
```

**Cause**: Target file does not exist
**Fix**: Update link path or create missing file

```
docs/commands/git.md:42:3: Broken anchor → guide.md#invalid
```

**Cause**: Target file exists but anchor/header not found
**Fix**: Update anchor to match existing header ID

#### Linting Errors

```
docs/guide/tutorial.md:23:1: MD032 - Blank lines around lists
```

**Cause**: Missing blank line before or after list
**Fix**: Add blank line (manual fix required)

```
docs/commands/git.md:67:1: MD040 - Code fence language missing
```

**Cause**: Code block without language tag
**Fix**: Run with `--fix` flag (auto-fixable)

### Troubleshooting

#### Link validation passing locally but failing in CI

**Cause**: Case sensitivity differences (macOS vs Linux)
**Solution**: Use exact case in file paths and anchors

#### Auto-fix not working

**Cause**: Complex context requires manual intervention
**Solution**: Review error message and fix manually

#### Pre-commit hook blocking commits

**Cause**: Documentation errors detected
**Solution**: Fix reported issues or skip with `git commit --no-verify` (not recommended)

---

## Best Practices

### 1. Run During Development

```bash
# Quick check during writing
/craft:docs:lint --fix
/craft:docs:check-links

# Comprehensive check before PR
/craft:docs:check-links release
/craft:docs:lint release
```

### 2. Enable Pre-commit Hooks

```bash
/craft:git:init  # Enable in Step 6.5
```

Benefits:

- Catch errors before commit
- Auto-fix safe issues automatically
- Prevent broken links from entering history

### 3. Integrate with /craft:check

```bash
/craft:check  # Runs docs validation when docs/ changed
```

### 4. Use CI/CD Validation

Add `.github/workflows/docs-quality.yml` to catch issues in PRs.

### 5. Test with Violations File

```bash
# Use docs/test-violations.md for testing
/craft:docs:lint docs/test-violations.md
/craft:docs:check-links docs/test-violations.md
```

---

## See Also

- [User Guide: Documentation Quality](../guide/documentation-quality.md) - Step-by-step tutorial
- [Developer Guide: Extending Documentation Quality](../guide/documentation-quality-development.md) - Customization guide
- [Commands: Documentation](../commands/docs.md) - All docs commands
- [Pre-commit Hook Integration](../guide/git-init-tutorial.md#pre-commit-hooks) - Setup guide
