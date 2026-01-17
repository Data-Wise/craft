# Documentation Quality Development Guide

> **TL;DR** (2 minutes)
>
> - **Customize**: Add rules via `.markdownlint.json` and `.markdown-link-check.json`
> - **Extend**: Modify command files in `commands/docs/`
> - **Test**: Use `docs/test-violations.md` for validation
> - **Contribute**: Follow conventional commits and add tests

Developer guide for extending and customizing Craft's documentation quality automation system.

!!! info "Related Documentation"
    - **[User Guide](documentation-quality.md)** - Step-by-step tutorial for using quality commands
    - **[API Reference](../reference/documentation-quality.md)** - Technical details and command syntax

## What You'll Learn

By the end of this guide, you'll know how to:

1. ✅ Customize linting rules for your project
2. ✅ Add new markdown quality checks
3. ✅ Extend link validation patterns
4. ✅ Create custom auto-fix routines
5. ✅ Test your changes effectively
6. ✅ Contribute improvements back to Craft

**Time estimate:** 30 minutes

---

## Architecture Overview

### System Components

```mermaid
graph TB
    A[User Command] --> B{Command Router}
    B -->|lint| C[/craft:docs:lint]
    B -->|check-links| D[/craft:docs:check-links]
    C --> E[markdownlint-cli2]
    D --> F[markdown-link-check]
    E --> G[Auto-fix Engine]
    G --> H[Language Detector]
    C --> I[Exit Code Handler]
    D --> I
    I --> J[VS Code Output]
```

### File Structure

```
craft/
├── commands/docs/
│   ├── lint.md                    # Markdown linting command
│   ├── check-links.md             # Link validation command
│   └── check.md                   # (modified) Integration
├── commands/git/
│   └── init.md                    # (modified) Pre-commit hooks
├── .markdownlint.json             # Linting rules config
├── .markdown-link-check.json      # Link check config
└── docs/
    └── test-violations.md         # Test cases
```

---

## Customizing Linting Rules

### Understanding Rule Configuration

The linting system uses `markdownlint-cli2` with embedded rules that can be overridden.

#### Default Rules (Embedded in Command)

```javascript
// From commands/docs/lint.md
const criticalRules = {
  "MD032": true,  // Blank lines around lists
  "MD040": true,  // Code fence language required
  "MD011": true,  // Reversed link syntax
  "MD042": true,  // No empty links
  "MD009": true,  // No trailing spaces
  "MD010": true,  // No hard tabs
};
```

### Override with .markdownlint.json

Create project-specific rules:

```json
{
  "default": true,
  "MD013": {
    "line_length": 120,
    "code_blocks": false
  },
  "MD033": {
    "allowed_elements": ["antml:*", "commentary", "example", "details", "summary"]
  },
  "MD024": {
    "siblings_only": true,
    "allow_different_nesting": true
  },
  "MD041": false
}
```

**Rule reference:**

- `MD013`: Line length limits
- `MD033`: Allowed HTML elements
- `MD024`: Duplicate heading restrictions
- `MD041`: First line must be heading

### Add Custom Rules

#### Example: Enforce Heading Case

Create `.markdownlint-custom.js`:

```javascript
module.exports = {
  "names": ["heading-case"],
  "description": "Headings must be sentence case",
  "tags": ["headings"],
  "function": function rule(params, onError) {
    params.tokens.filter(token => token.type === "heading_open")
      .forEach(heading => {
        const content = params.lines[heading.lineNumber - 1];
        const match = content.match(/^#+\s+(.+)$/);

        if (match) {
          const text = match[1];
          // Check if heading starts with capital
          if (text[0] !== text[0].toUpperCase()) {
            onError({
              lineNumber: heading.lineNumber,
              detail: "Heading must start with capital letter",
              context: content
            });
          }
        }
      });
  }
};
```

**Use in .markdownlint.json:**

```json
{
  "default": true,
  "customRules": [".markdownlint-custom.js"],
  "heading-case": true
}
```

---

## Customizing Link Validation

### Default Ignore Patterns

```json
// .markdown-link-check.json
{
  "ignorePatterns": [
    { "pattern": "^https://example.com" },
    { "pattern": "^http://localhost" },
    { "pattern": "^https://github.com/.*/pull/" },
    { "pattern": "^https://github.com/.*/issues/" }
  ],
  "timeout": "10s",
  "retryOn429": true,
  "retryCount": 3
}
```

### Add Project-Specific Patterns

#### Ignore Development URLs

```json
{
  "ignorePatterns": [
    { "pattern": "^http://localhost:\\d+" },
    { "pattern": "^https://dev\\." },
    { "pattern": "^https://staging\\." }
  ]
}
```

#### Ignore Placeholder Links

```json
{
  "ignorePatterns": [
    { "pattern": "^#$" },
    { "pattern": "^#todo$" },
    { "pattern": "^/docs/.*\\.wip\\.md$" }
  ]
}
```

### Custom Link Validation Logic

Extend `commands/docs/check-links.md` to add custom checks:

```bash
# Add after line 150 (within MODE_HANDLERS)
# Custom check for external links in CI
if [[ "$MODE" == "release" ]] && [[ "$CHECK_EXTERNAL" == "true" ]]; then
  echo "🌐 Checking external links..."

  # Use lychee for faster external link checking
  if command -v lychee &> /dev/null; then
    lychee --exclude-loopback --exclude-private \
      --max-concurrency 10 "$DOCS_PATH"
  fi
fi
```

---

## Extending Auto-fix Capabilities

### Current Auto-fix Features

The auto-fix engine handles:

1. **Trailing spaces** (MD009) - Remove spaces at line end
2. **Hard tabs** (MD010) - Convert to spaces
3. **Multiple blank lines** (MD012) - Reduce to single blank line
4. **Code fence language** (MD040) - Add language tag with detection

### Add New Auto-fix Routine

#### Example: Auto-fix List Indentation

Add to `commands/docs/lint.md` (around line 300):

```bash
# Function: fix_list_indentation
fix_list_indentation() {
  local file="$1"
  local temp_file="${file}.tmp"

  awk '
    /^[[:space:]]*[-*+][[:space:]]/ {
      # Get current indentation
      match($0, /^[[:space:]]*/);
      indent = RLENGTH;

      # Ensure 2-space indentation for nested lists
      if (indent > 0) {
        level = int(indent / 2);
        correct_indent = level * 2;

        if (indent != correct_indent) {
          sub(/^[[:space:]]*/, sprintf("%*s", correct_indent, ""));
          print $0 " # FIXED: list indentation";
          next;
        }
      }
    }
    { print }
  ' "$file" > "$temp_file"

  mv "$temp_file" "$file"
}

# Add to auto-fix workflow
if [[ "$AUTO_FIX" == "true" ]]; then
  fix_trailing_spaces "$FILE"
  fix_hard_tabs "$FILE"
  fix_multiple_blank_lines "$FILE"
  fix_code_fence_language "$FILE"
  fix_list_indentation "$FILE"  # NEW
fi
```

### Improve Language Detection

Extend the language detector with new patterns:

```bash
# Function: detect_language (extend around line 250)
detect_language() {
  local code="$1"

  # Existing detections...

  # Add Go detection
  if echo "$code" | grep -qE "^(package |func |import |type )"; then
    echo "go"
    return
  fi

  # Add Rust detection
  if echo "$code" | grep -qE "^(fn |use |mod |pub )"; then
    echo "rust"
    return
  fi

  # Add SQL detection
  if echo "$code" | grep -qiE "^(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER) "; then
    echo "sql"
    return
  fi

  # Add TypeScript detection
  if echo "$code" | grep -qE "(: .*\|.*|interface |type .*= )"; then
    echo "typescript"
    return
  fi

  # Fallback
  echo "text"
}
```

---

## Adding New Documentation Commands

### Command Template

Create `commands/docs/my-command.md`:

```markdown
---
description: Brief description of command
category: docs
arguments:
  - name: mode
    description: Execution mode
    required: false
    default: default
  - name: --dry-run
    description: Preview without executing
    required: false
    default: false
    alias: -n
---

# /craft:docs:my-command

Command implementation goes here.

## Modes

- **default**: Quick check
- **debug**: Verbose output
- **optimize**: CI/CD optimized
- **release**: Comprehensive validation

## Implementation

```bash
#!/bin/bash

# Parse arguments
MODE="${1:-default}"
DRY_RUN=false

for arg in "$@"; do
  case "$arg" in
    --dry-run|-n) DRY_RUN=true ;;
  esac
done

# Mode-specific behavior
case "$MODE" in
  default)
    # Quick validation
    ;;
  debug)
    # Verbose output
    ;;
  optimize)
    # CI/CD optimized
    ;;
  release)
    # Comprehensive check
    ;;
  *)
    echo "❌ Invalid mode: $MODE"
    exit 2
    ;;
esac

# Exit codes:
# 0 = success
# 1 = issues found requiring manual fix
# 2 = invalid arguments/configuration error
exit 0
```

\```

## Documentation

### Usage

\```bash
/craft:docs:my-command
/craft:docs:my-command debug
/craft:docs:my-command --dry-run
\```

### Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | None |
| 1 | Issues found | Fix manually |
| 2 | Configuration error | Check arguments |
\```

```

### Register Command

Update `.claude-plugin/plugin.json`:

```json
{
  "commands": [
    {
      "name": "docs:my-command",
      "file": "commands/docs/my-command.md",
      "description": "Brief description",
      "category": "docs"
    }
  ]
}
```

### Add to Documentation

Update `docs/commands/docs.md`:

```markdown
### /craft:docs:my-command

Brief description and usage example.

\```bash
/craft:docs:my-command
\```
```

---

## Testing Your Changes

### Use Test Violations File

The `docs/test-violations.md` file contains known violations for testing:

```bash
# Test your linting changes
/craft:docs:lint docs/test-violations.md

# Test link checking changes
/craft:docs:check-links docs/test-violations.md
```

### Add Test Cases

Extend `docs/test-violations.md`:

```markdown
## Test Case 7: Your New Check

Description of what you're testing.

### Violation Example

\```markdown
<!-- Your violation example -->
\```

### Expected Behavior

- Should detect X
- Should report Y
- Should fix Z (if auto-fixable)
```

### Automated Testing

Create test script `tests/test_docs_quality.sh`:

```bash
#!/bin/bash
set -e

echo "Testing documentation quality commands..."

# Test 1: Lint should detect violations
echo "Test 1: Lint detection"
if /craft:docs:lint docs/test-violations.md 2>&1 | grep -q "MD040"; then
  echo "✅ Lint detection works"
else
  echo "❌ Lint detection failed"
  exit 1
fi

# Test 2: Link check should find broken links
echo "Test 2: Link check"
if /craft:docs:check-links docs/test-violations.md 2>&1 | grep -q "Broken link"; then
  echo "✅ Link check works"
else
  echo "❌ Link check failed"
  exit 1
fi

# Test 3: Auto-fix should work
echo "Test 3: Auto-fix"
cp docs/test-violations.md /tmp/test-violations.md
if /craft:docs:lint /tmp/test-violations.md --fix; then
  echo "✅ Auto-fix works"
else
  echo "❌ Auto-fix failed"
  exit 1
fi

echo "✅ All tests passed"
```

### Run Tests

```bash
chmod +x tests/test_docs_quality.sh
./tests/test_docs_quality.sh
```

---

## Integration with Existing Commands

### Extend /craft:check

Add your new check to `/craft:check` integration:

```bash
# In commands/check.md (around line 210)
if [ -d "docs/" ]; then
  if git diff --name-only | grep -q "^docs/"; then
    echo "📚 Docs changed, running validation..."

    # Existing checks
    claude "/craft:docs:lint default"
    claude "/craft:docs:check-links default"

    # Your new check
    claude "/craft:docs:my-command default"
  fi
fi
```

### Extend Pre-commit Hooks

Add to `/craft:git:init` hook template:

```bash
# In commands/git/init.md (around line 250)
if [ -n "$STAGED_MD" ]; then
  echo "📚 Checking documentation quality..."

  # Existing hooks
  claude "/craft:docs:lint --fix" || exit 1
  claude "/craft:docs:check-links default" || exit 1

  # Your new check
  claude "/craft:docs:my-command default" || exit 1

  git add $STAGED_MD
fi
```

### Extend CI Workflow

Add to `.github/workflows/docs-quality.yml`:

```yaml
jobs:
  custom-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run custom documentation check
        run: |
          # Your custom validation
          ./scripts/my-docs-check.sh
```

---

## Performance Optimization

### Parallel Processing

Use GNU Parallel for faster processing:

```bash
# Process multiple files in parallel
find docs/ -name "*.md" -print0 | \
  parallel -0 -j 4 "/craft:docs:lint {}"
```

### Caching Results

Cache validation results to avoid redundant checks:

```bash
# Create cache directory
CACHE_DIR=".cache/docs-quality"
mkdir -p "$CACHE_DIR"

# Generate file hash
FILE_HASH=$(md5sum "$FILE" | cut -d' ' -f1)
CACHE_FILE="$CACHE_DIR/$FILE_HASH"

# Check cache
if [ -f "$CACHE_FILE" ]; then
  CACHED_RESULT=$(cat "$CACHE_FILE")
  echo "✅ Using cached result: $CACHED_RESULT"
  exit 0
fi

# Run validation and cache result
validate_file "$FILE"
RESULT=$?
echo "$RESULT" > "$CACHE_FILE"
exit $RESULT
```

### Incremental Validation

Only check changed files:

```bash
# Get changed files
CHANGED_FILES=$(git diff --name-only --diff-filter=ACM docs/)

# Validate only changed files
for file in $CHANGED_FILES; do
  /craft:docs:lint "$file"
  /craft:docs:check-links "$file"
done
```

---

## Debugging

### Enable Verbose Logging

```bash
# Set debug mode
DEBUG=true /craft:docs:lint debug docs/file.md

# Or add to command
set -x  # Enable bash tracing
```

### Output Intermediate Results

```bash
# Save intermediate results
/craft:docs:lint docs/file.md > /tmp/lint-output.txt 2>&1

# Analyze output
cat /tmp/lint-output.txt
```

### Test Individual Functions

Extract and test functions independently:

```bash
# Source the command to get functions
source commands/docs/lint.md

# Test specific function
detect_language "def main():"  # Should output: python
detect_language "function foo() {"  # Should output: javascript
```

---

## Contributing Back to Craft

### Development Workflow

1. **Fork** the Craft repository
2. **Create feature branch** from `dev`:

   ```bash
   git checkout dev
   git checkout -b feature/improved-docs-validation
   ```

3. **Make changes** following conventions:
   - Use conventional commits: `feat:`, `fix:`, `docs:`
   - Add tests for new features
   - Update documentation

4. **Test thoroughly**:

   ```bash
   ./tests/test_docs_quality.sh
   /craft:check
   ```

5. **Create PR** to `dev` branch:

   ```bash
   gh pr create --base dev --title "feat(docs): improve validation"
   ```

### Conventional Commits

```bash
# New feature
git commit -m "feat(docs): add external link validation"

# Bug fix
git commit -m "fix(docs): correct anchor case sensitivity"

# Documentation
git commit -m "docs(guide): add customization examples"

# Performance
git commit -m "perf(docs): parallelize link checking"

# Testing
git commit -m "test(docs): add coverage for edge cases"
```

### Pull Request Checklist

- [ ] Tests pass (`./tests/test_docs_quality.sh`)
- [ ] Documentation updated
- [ ] CHANGELOG.md entry added
- [ ] No broken links (`/craft:docs:check-links release`)
- [ ] Code follows project conventions
- [ ] Commit messages follow conventional commits
- [ ] PR targets `dev` branch (not `main`)

---

## Advanced Customization

### Custom Mode Handlers

Add custom execution modes:

```bash
# In commands/docs/lint.md
MODE_HANDLERS["custom"]() {
  echo "Running custom validation..."

  # Your custom logic
  markdownlint-cli2 \
    --config .markdownlint-custom.json \
    --customRules ./rules/*.js \
    "$@"
}

# Usage
/craft:docs:lint custom
```

### Plugin Architecture

Create reusable validation plugins:

```bash
# plugins/docs-quality/heading-validator.sh
#!/bin/bash

validate_headings() {
  local file="$1"

  # Extract all headings
  grep "^#" "$file" | while read -r heading; do
    # Custom validation logic
    if ! validate_heading_format "$heading"; then
      echo "Invalid heading: $heading"
      return 1
    fi
  done
}

# Load in main command
source plugins/docs-quality/heading-validator.sh
validate_headings "$FILE"
```

### Configuration Presets

Create project-specific presets:

```bash
# .craft/docs-quality-preset.sh
export LINT_MODE="release"
export CHECK_EXTERNAL_LINKS="true"
export AUTO_FIX_ENABLED="true"
export IGNORE_PATTERNS="*.wip.md"

# Load preset
source .craft/docs-quality-preset.sh
/craft:docs:lint
```

---

## API for Automation

### Programmatic Usage

Call commands from scripts:

```bash
#!/bin/bash
# scripts/validate-docs.sh

# Validate all docs
if ! /craft:docs:lint release; then
  echo "❌ Linting failed"
  exit 1
fi

if ! /craft:docs:check-links release; then
  echo "❌ Link check failed"
  exit 1
fi

echo "✅ Documentation quality validated"
```

### Exit Code Handling

```bash
# Capture exit codes
/craft:docs:lint
LINT_CODE=$?

/craft:docs:check-links
LINK_CODE=$?

# Combine results
if [ $LINT_CODE -ne 0 ] || [ $LINK_CODE -ne 0 ]; then
  echo "❌ Validation failed"
  exit 1
fi
```

### JSON Output (Future Enhancement)

```bash
# Generate JSON report
/craft:docs:lint --format json > report.json

# Parse with jq
jq '.errors[] | select(.severity == "error")' report.json
```

---

## Resources

### Documentation

- [markdownlint-cli2 docs](https://github.com/DavidAnson/markdownlint-cli2)
- [markdown-link-check docs](https://github.com/tcort/markdown-link-check)
- [lychee docs](https://github.com/lycheeverse/lychee)

### Rule References

- [markdownlint rules](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md)
- [CommonMark spec](https://spec.commonmark.org/)
- [GitHub Flavored Markdown](https://github.github.com/gfm/)

### Testing Tools

- [bats](https://github.com/bats-core/bats-core) - Bash testing framework
- [shellcheck](https://www.shellcheck.net/) - Shell script linter
- [shfmt](https://github.com/mvdan/sh) - Shell script formatter

---

## Summary

You've learned how to:

✅ **Customize linting rules** with `.markdownlint.json`
✅ **Extend link validation** with ignore patterns
✅ **Add auto-fix routines** for new issues
✅ **Create new documentation commands**
✅ **Test changes effectively** with test cases
✅ **Contribute improvements** back to Craft

**You're now ready to extend and customize the documentation quality system!** 🚀

## Next Steps

- Implement a custom validation rule
- Add a new auto-fix routine
- Contribute a PR to Craft
- Share your customizations with the community
