# Test Violations File

This file contains known violations for testing documentation quality checks.

## Test Case 1: Broken Internal Links

### Relative Links (Broken)
Check the [missing file](nonexistent.md) for more information.

Also see [another broken link](../missing-directory/file.md).

### Absolute Repo Links (Broken)
Visit the [configuration guide](/docs/missing-config.md) for setup instructions.

Read the [API reference](/docs/reference/nonexistent-api.md) for details.

## Test Case 2: Valid Internal Links

### Relative Links (Valid)
See the [index page](index.md) for an overview.

Check the [commands reference](commands/index.md) for available commands.

### Absolute Repo Links (Valid)
Visit the [main documentation](/docs/index.md) for getting started.

## Test Case 3: Markdown Linting Issues

### Missing Blank Line Before List
Some text without blank line before list:
- Item 1
- Item 2
- Item 3

### Code Fence Without Language Tag

```
This code fence has no language tag
def example():
    pass
```

### Code Fence With Language Tag (Valid)

```python
def valid_example():
    """This code fence has a language tag."""
    pass
```

## Test Case 4: Mixed Link Styles

Some files use relative paths:
- [Guide](guide/quickstart.md)
- [Tutorial](../docs/tutorial.md)

Others use absolute paths:
- [Commands](/docs/commands/index.md)
- [Reference](/docs/reference/api.md)

## Test Case 5: External Links (Skipped in MVP)

These should be skipped in internal link checking:
- [GitHub](https://github.com/Data-Wise/craft)
- [Documentation Site](https://data-wise.github.io/craft/)
- [Contact](mailto:example@example.com)

## Test Case 6: Anchor Links (Release Mode Only)

Links with anchors should work in release mode:
- [Test Case 1](#test-case-1-broken-internal-links)
- [Test Case 2](#test-case-2-valid-internal-links)
- [Nonexistent Heading](#this-heading-does-not-exist)

Cross-file anchor links:
- [Index intro](index.md#overview)
- [Commands intro](commands/index.md#available-commands)

## Expected Results

When running `/craft:docs:check-links`:

**Default Mode:**
- Should find 4 broken internal links:
  1. nonexistent.md (relative)
  2. ../missing-directory/file.md (relative)
  3. /docs/missing-config.md (absolute)
  4. /docs/reference/nonexistent-api.md (absolute)
- Should validate 4 valid internal links
- Should skip external links (https://, mailto:)
- Should skip anchors (default mode doesn't check them)

**Release Mode:**
- Should find the same 4 broken internal links
- Should validate anchor links within same file
- Should check cross-file anchor links
- Should detect "this-heading-does-not-exist" as broken anchor

## Cleanup Instructions

After testing, remove this file:

```bash
git reset HEAD docs/test-violations.md
rm docs/test-violations.md
```

Or if committed:

```bash
git reset HEAD~1
rm docs/test-violations.md
```
