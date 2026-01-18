---
name: check:broken-links
description: Validate documentation has no broken internal links
category: validation
context: fork
hot_reload: true
version: 1.0.0
dependencies:
  - python3
  - tests/test_craft_plugin.py
---

# Broken Links Validation

Check all markdown files for broken internal links using existing test infrastructure.

## What This Checks

- **Internal links**: Links to files within the project (`[text](path/to/file.md)`)
- **Anchor links**: Links to headings (`[text](#heading)`)
- **Cross-references**: Links between documentation pages
- **Command references**: Links to command files (`commands/*.md`)

## Exclusions

Links in `.linkcheck-ignore` file are skipped (test files, brainstorm docs, etc.).

## Implementation

```bash
#!/bin/bash
set -euo pipefail

# Check if test file exists
if [ ! -f "tests/test_craft_plugin.py" ]; then
    echo "⚠️  SKIP: Test file not found"
    exit 0
fi

# Run broken links test
echo "🔗 Checking internal links..."
python3 tests/test_craft_plugin.py -k "test_no_broken_links_in_docs" -v

if [ $? -eq 0 ]; then
    # Count total links checked
    TOTAL_LINKS=$(grep -r '\[.*\](.*\.md\|#.*)' docs/ README.md CLAUDE.md 2>/dev/null | wc -l | tr -d ' ')

    echo "✅ PASS: No broken links found ($TOTAL_LINKS links checked)"
    exit 0
else
    # Extract error details from test output
    echo "❌ FAIL: Broken links detected"
    echo ""
    echo "💡 Tip: Check .linkcheck-ignore if these are expected (test files, brainstorm docs)"
    echo "💡 Run: python3 tests/test_craft_plugin.py -k 'test_no_broken_links_in_docs' -v"
    exit 1
fi
```

## Example Output

### Success
```
✅ PASS: No broken links found (342 links checked)
```

### Failure
```
❌ FAIL: Broken links detected

💡 Tip: Check .linkcheck-ignore if these are expected (test files, brainstorm docs)
💡 Run: python3 tests/test_craft_plugin.py -k 'test_no_broken_links_in_docs' -v
```

## .linkcheck-ignore Format

Document expected broken links (e.g., test files, brainstorm drafts):

```
# Test files (intentionally broken for testing)
docs/test-violations.md

# Brainstorm docs (gitignored, may reference non-existent files)
docs/brainstorm/*.md

# External tools (not part of core docs)
docs/workflows/external-*.md
```

## Integration

This validator runs automatically as part of `/craft:check`:

1. **Pre-commit**: Optional (can be slow for large doc sets)
2. **Pre-PR**: Always runs (prevent deploying broken docs)
3. **Pre-release**: Always runs (ensure documentation quality)

## Hot-Reload Behavior

- Automatically detected by `/craft:check` (no restart needed)
- Changes take effect immediately on next check
- Can be disabled with `.craft/validation-config.yml`:

```yaml
validators:
  broken-links:
    enabled: false
```

## See Also

- `/craft:docs:check-links` - Detailed link validation with modes
- `/craft:docs:lint` - Markdown quality checks
- `.linkcheck-ignore` - Document expected broken links
- `tests/test_craft_plugin.py` - Full test suite
