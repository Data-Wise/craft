# Contributing to Hub v2.0

**Version:** 2.0
**Date:** 2026-01-17
**Status:** Production Ready

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Architecture Overview](#architecture-overview)
4. [Adding New Commands](#adding-new-commands)
5. [Modifying the Discovery Engine](#modifying-the-discovery-engine)
6. [Testing Your Changes](#testing-your-changes)
7. [Code Style & Best Practices](#code-style--best-practices)
8. [Submitting Changes](#submitting-changes)
9. [Troubleshooting](#troubleshooting)

---

## Getting Started

Hub v2.0 is a zero-maintenance command discovery system for the Craft plugin. The system automatically detects commands from the file system and provides a 3-layer progressive disclosure interface.

### Key Principles

1. **Zero Maintenance**: No hardcoded command lists - everything is auto-detected
2. **Performance First**: Sub-10ms cached performance is critical
3. **ADHD-Friendly**: Progressive disclosure, clear hierarchy, visual organization
4. **Simplicity**: Pure Python, no external dependencies
5. **Testability**: 100% test coverage required

### Before You Start

- Read the [Architecture Documentation](../architecture/HUB-V2-ARCHITECTURE.md)
- Review the [API Reference](../api/DISCOVERY-API.md)
- Run the test suite to ensure everything works
- Familiarize yourself with the [User Guide](../help/hub.md)

---

## Development Setup

### 1. Clone and Branch

```bash
# Clone repository
cd ~/projects/dev-tools/craft

# Ensure you're on dev branch
git checkout dev

# Create feature branch
git checkout -b feature/hub-enhancement

# Or use Craft's worktree command
/craft:git:worktree feature/hub-enhancement
```

### 2. Install Dependencies

Hub v2.0 has no external dependencies! Only Python 3.8+ is required.

```bash
# Verify Python version
python3 --version  # Should be 3.8+

# No pip install needed
```

### 3. Verify Setup

```bash
# Run discovery engine
python3 commands/_discovery.py

# Run test suites
python3 tests/test_hub_discovery.py
python3 tests/test_hub_integration.py
python3 tests/test_hub_layer2.py
python3 tests/test_hub_layer3.py

# All tests should pass
```

---

## Architecture Overview

### Component Structure

```
commands/
├── _discovery.py          # Discovery engine (680 lines)
├── _cache.json           # Auto-generated cache (gitignored)
├── _schema.json          # Frontmatter schema
├── hub.md                # Hub command implementation
├── code/
│   ├── lint.md           # Example: code command
│   └── ...
├── test/
│   └── ...
└── ...                   # Other categories

tests/
├── test_hub_discovery.py # Discovery tests (12 tests)
├── test_hub_integration.py # Integration tests (7 tests)
├── test_hub_layer2.py    # Layer 2 tests (7 tests)
├── test_hub_layer3.py    # Layer 3 tests (8 tests)
├── demo_layer2.py        # Layer 2 demo
└── demo_layer3.py        # Layer 3 demo

docs/
├── help/
│   └── hub.md            # User-facing documentation
├── architecture/
│   └── HUB-V2-ARCHITECTURE.md # Architecture docs
├── api/
│   └── DISCOVERY-API.md  # API reference
└── dev/
    └── CONTRIBUTING-HUB-V2.md # This file
```

### Data Flow

```
User invokes /craft:hub
        ↓
Hub command loads (commands/hub.md)
        ↓
Call load_cached_commands()
        ↓
Check cache validity
        ↓
├─ Cache valid? → Load from cache (< 2ms)
└─ Cache stale? → discover_commands() (~ 12ms)
        ↓
Return commands array
        ↓
Layer-specific processing
├─ Layer 1: get_command_stats()
├─ Layer 2: get_commands_by_category()
└─ Layer 3: get_command_detail() + generate_command_tutorial()
        ↓
Format and display to user
```

---

## Adding New Commands

### 1. Create Command File

```bash
# Create new command file
touch commands/<category>/<command>.md
```

### 2. Add YAML Frontmatter

```yaml
---
name: category:command          # Required: Full command name
category: category              # Required: Primary category
description: One-line description  # Required: Short description
subcategory: optional           # Optional: For grouping in Layer 2
modes:                          # Optional: Execution modes
  - default
  - debug
related_commands:               # Optional: Cross-references
  - other:command
tags:                           # Optional: Search tags
  - tag1
  - tag2
---

# Command content here
```

### 3. Test Auto-Detection

```bash
# Regenerate cache
rm commands/_cache.json
python3 commands/_discovery.py

# Verify command appears
python3 -c "
from commands._discovery import get_command_detail
cmd = get_command_detail('category:command')
print(cmd)
"
```

### 4. Test in Hub

```bash
# Test Layer 2 (category view)
# Say to Claude: /craft:hub <category>

# Test Layer 3 (command detail)
# Say to Claude: /craft:hub <category>:<command>
```

### 5. Write Tests

Add tests to verify your command is discovered correctly:

```python
# In tests/test_hub_discovery.py or tests/test_hub_integration.py

def test_new_command_discovered():
    """Test that new command is discovered."""
    from commands._discovery import get_command_detail

    cmd = get_command_detail('category:command')
    assert cmd is not None
    assert cmd['name'] == 'category:command'
    assert cmd['category'] == 'category'
    assert 'description' in cmd
```

---

## Modifying the Discovery Engine

### Key Files to Modify

| File | Purpose | Lines |
|------|---------|-------|
| `commands/_discovery.py` | Core discovery engine | 830 |
| `commands/hub.md` | Hub command implementation | varies |
| `tests/test_hub_discovery.py` | Discovery tests | 570 |

### Common Modifications

#### 1. Adding New Metadata Fields

**Step 1:** Define field in frontmatter schema

```yaml
# commands/_schema.json
{
  "properties": {
    "new_field": {
      "type": "string",
      "description": "Description of new field"
    }
  }
}
```

**Step 2:** Parse field in `discover_commands()`

```python
# In commands/_discovery.py, discover_commands() function

if 'new_field' in metadata:
    command['new_field'] = metadata['new_field']
```

**Step 3:** Update tests

```python
# In tests/test_hub_discovery.py

def test_new_field_parsing():
    """Test that new_field is parsed correctly."""
    from commands._discovery import parse_yaml_frontmatter

    content = """---
name: test
new_field: value
---"""

    metadata = parse_yaml_frontmatter(content)
    assert metadata['new_field'] == 'value'
```

**Step 4:** Update documentation

- Add field to `commands/_discovery_usage.md`
- Update `docs/api/DISCOVERY-API.md`
- Add example to `docs/help/hub.md`

#### 2. Adding New Layer Functions

**Example: Layer 4 - Command Search**

```python
# In commands/_discovery.py

def search_commands(query: str) -> list[dict]:
    """
    Search commands by name or description.

    Args:
        query: Search query string

    Returns:
        List of matching command dictionaries
    """
    commands = load_cached_commands()
    query_lower = query.lower()

    return [
        cmd for cmd in commands
        if query_lower in cmd['name'].lower() or
           query_lower in cmd['description'].lower()
    ]
```

**Add tests:**

```python
# In tests/test_hub_layer4.py (new file)

import unittest
from commands._discovery import search_commands

class TestHubLayer4(unittest.TestCase):
    def test_search_by_name(self):
        """Test searching by command name."""
        results = search_commands('lint')
        self.assertGreater(len(results), 0)
        self.assertTrue(any('lint' in cmd['name'] for cmd in results))

    def test_search_by_description(self):
        """Test searching by description."""
        results = search_commands('quality')
        self.assertGreater(len(results), 0)

if __name__ == '__main__':
    unittest.main()
```

#### 3. Performance Optimizations

**Before optimizing:**

```python
# Benchmark current performance
import time

start = time.time()
commands = load_cached_commands()
elapsed = (time.time() - start) * 1000
print(f"Cached load: {elapsed:.2f}ms")

# Target: < 10ms
```

**Common optimizations:**

1. **Reduce file I/O**:
   ```python
   # Bad: Multiple file reads
   for filepath in files:
       with open(filepath) as f:
           content = f.read()

   # Good: Single pass
   contents = {}
   for filepath in files:
       with open(filepath) as f:
           contents[filepath] = f.read()
   ```

2. **Optimize JSON serialization**:
   ```python
   # Use compact JSON format
   json.dump(cache, f, separators=(',', ':'))
   ```

3. **Early termination**:
   ```python
   # Stop scanning if cache is valid
   if cache_is_valid():
       return load_cache()
   ```

---

## Testing Your Changes

### Test Hierarchy

1. **Unit Tests** (test_hub_discovery.py)
   - Test individual functions
   - Fast (< 100ms total)
   - No file I/O mocking

2. **Integration Tests** (test_hub_integration.py)
   - Test component interactions
   - Medium (< 200ms total)
   - Real file system access

3. **Layer Tests** (test_hub_layer2.py, test_hub_layer3.py)
   - Test layer-specific functionality
   - Fast (< 100ms each)
   - Real command data

4. **Manual Tests** (HUB-V2-TESTING-GUIDE.md)
   - User experience testing
   - 30-45 minutes
   - Real Claude interaction

### Running Tests

```bash
# Run all automated tests
python3 tests/test_hub_discovery.py && \
python3 tests/test_hub_integration.py && \
python3 tests/test_hub_layer2.py && \
python3 tests/test_hub_layer3.py

# Run single test file
python3 tests/test_hub_discovery.py

# Run specific test
python3 tests/test_hub_discovery.py -k "test_parse_frontmatter"

# Verbose output
python3 tests/test_hub_discovery.py -v
```

### Writing New Tests

**Test Structure:**

```python
import unittest
from commands._discovery import your_function

class TestYourFeature(unittest.TestCase):
    def test_basic_functionality(self):
        """Test basic usage."""
        result = your_function(input)
        self.assertEqual(result, expected)

    def test_edge_case(self):
        """Test edge case handling."""
        result = your_function(edge_input)
        self.assertIsNotNone(result)

    def test_error_handling(self):
        """Test error handling."""
        with self.assertRaises(ValueError):
            your_function(invalid_input)

if __name__ == '__main__':
    unittest.main()
```

### Test Best Practices

1. **One assertion per test**: Focus on a single behavior
2. **Clear test names**: Describe what is being tested
3. **Helpful failure messages**: Use custom assertion messages
4. **Fast execution**: < 100ms per test file
5. **No external dependencies**: Use built-in unittest
6. **Deterministic**: Same input → same output
7. **Independent**: Tests don't depend on each other

---

## Code Style & Best Practices

### Python Style

- **PEP 8 compliant**: Follow Python style guide
- **Type hints**: Use type annotations for function signatures
- **Docstrings**: Required for all public functions
- **Comments**: Explain "why", not "what"

**Example:**

```python
def parse_yaml_frontmatter(content: str) -> dict:
    """
    Extract YAML frontmatter from markdown file.

    Frontmatter is delimited by --- at start and end.
    Supports simple key-value pairs, arrays, and nested objects.

    Args:
        content: Full markdown file content

    Returns:
        Dictionary of frontmatter fields (empty dict if no frontmatter)
    """
    # Implementation...
```

### Documentation Standards

1. **Module docstring**: Describe module purpose and usage
2. **Function docstring**: Args, returns, raises, examples
3. **Complex logic**: Inline comments explaining algorithm
4. **Public API**: Detailed examples in docstring

### Performance Guidelines

1. **Cache everything**: Expensive operations should be cached
2. **Fail fast**: Validate inputs early
3. **Lazy evaluation**: Don't compute unless needed
4. **Profile first**: Measure before optimizing

### Error Handling

```python
# Good: Specific exception, helpful message
if not os.path.exists(filepath):
    raise FileNotFoundError(f"Command file not found: {filepath}")

# Bad: Generic exception, no context
if not os.path.exists(filepath):
    raise Exception("File not found")
```

### Git Commit Messages

**Format:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Adding tests
- `refactor`: Code restructuring
- `perf`: Performance improvement
- `chore`: Maintenance tasks

**Example:**

```
feat(hub): add search functionality to Layer 4

Implement full-text search across command names and descriptions.
Includes fuzzy matching and highlighting of search terms.

Performance: < 5ms for 97 commands
Tests: 8 new tests added (100% coverage)

Closes #42
```

---

## Submitting Changes

### Pre-Submit Checklist

- [ ] All tests pass (34 tests minimum)
- [ ] New tests added for new functionality
- [ ] Documentation updated (API docs, user guide, architecture)
- [ ] Code follows style guidelines
- [ ] Performance targets met (< 10ms cached, < 200ms uncached)
- [ ] Cache invalidation works correctly
- [ ] No breaking changes (or documented if necessary)

### Pull Request Process

1. **Create PR from feature branch to `dev`**

   ```bash
   # Push your feature branch
   git push origin feature/hub-enhancement

   # Create PR
   gh pr create --base dev --title "feat(hub): add new feature" --body "..."
   ```

2. **PR Description Template**

   ```markdown
   ## Summary
   Brief description of changes

   ## Motivation
   Why is this change needed?

   ## Changes
   - Added X
   - Modified Y
   - Fixed Z

   ## Testing
   - [ ] All existing tests pass
   - [ ] Added 5 new tests
   - [ ] Manual testing completed

   ## Performance Impact
   - Cached: <2ms (no change)
   - Uncached: 12ms → 11ms (8% improvement)

   ## Documentation
   - [ ] API docs updated
   - [ ] User guide updated
   - [ ] Architecture docs updated

   ## Breaking Changes
   None / [Describe breaking changes]

   ## Screenshots/Examples
   [If applicable]
   ```

3. **Review Process**

   - Code review by maintainer
   - Address feedback
   - Ensure CI passes
   - Merge to `dev`

4. **After Merge**

   - Delete feature branch
   - Update changelog
   - Monitor for issues

---

## Troubleshooting

### Common Issues

#### Tests Failing

**Problem:** Tests fail after changes

**Solution:**

```bash
# 1. Verify Python version
python3 --version  # Should be 3.8+

# 2. Delete cache
rm commands/_cache.json

# 3. Run discovery
python3 commands/_discovery.py

# 4. Run failing test with verbose output
python3 tests/test_hub_discovery.py -v -k "failing_test"

# 5. Check for file system changes
git status
git diff commands/
```

#### Cache Not Invalidating

**Problem:** Changes to commands not appearing

**Solution:**

```bash
# Delete cache manually
rm commands/_cache.json

# Verify cache regenerates
python3 commands/_discovery.py
ls -lh commands/_cache.json

# Check file mtimes
stat commands/code/lint.md
stat commands/_cache.json
```

#### Performance Regression

**Problem:** Discovery slower than 200ms uncached

**Solution:**

```python
# Profile discovery
import cProfile
import commands._discovery as discovery

cProfile.run('discovery.discover_commands()', sort='cumtime')

# Check for:
# - Excessive file I/O
# - Repeated parsing
# - Inefficient loops
```

#### Import Errors

**Problem:** `ModuleNotFoundError` when running tests

**Solution:**

```bash
# Ensure you're in plugin root
cd /path/to/craft

# Check Python path
python3 -c "import sys; print(sys.path)"

# Run tests from plugin root
python3 tests/test_hub_discovery.py
```

### Getting Help

1. **Check existing documentation**:
   - [Architecture docs](../architecture/HUB-V2-ARCHITECTURE.md)
   - [API reference](../api/DISCOVERY-API.md)
   - [Testing guide](../../tests/HUB-V2-TESTING-GUIDE.md)

2. **Review test suite**:
   - Tests show expected behavior
   - Look for similar functionality

3. **Ask for help**:
   - Open GitHub issue
   - Describe problem with code examples
   - Include test output

---

## Developer Resources

### Documentation

- [Architecture Documentation](../architecture/HUB-V2-ARCHITECTURE.md)
- [API Reference](../api/DISCOVERY-API.md)
- [User Guide](../help/hub.md)
- [Testing Guide](../../tests/HUB-V2-TESTING-GUIDE.md)
- [Testing Summary](../../tests/TESTING-SUMMARY.md)

### Source Code

- `commands/_discovery.py` (680 lines) - Discovery engine
- `commands/hub.md` - Hub command implementation
- `tests/test_hub_*.py` - Test suites (34 tests)
- `tests/demo_layer*.py` - Demonstration scripts

### Tools

- `python3 commands/_discovery.py` - Regenerate cache, print stats
- `python3 tests/test_hub_discovery.py` - Run discovery tests
- `bash tests/cli/automated-tests.sh` - CLI test suite
- `bash tests/cli/interactive-tests.sh` - Interactive testing

---

## License

Craft plugin is open source. See LICENSE file for details.

---

**Questions?** Open an issue on GitHub or check existing documentation.

**Last Updated:** 2026-01-17
**Version:** 2.0
**Status:** Production Ready
