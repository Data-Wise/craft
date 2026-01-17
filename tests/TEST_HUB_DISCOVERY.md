# Hub v2.0 Discovery Test Suite Documentation

## Overview

This test suite validates the command discovery engine that powers the `/craft:hub` command. It ensures reliable auto-detection of all 97 commands, accurate metadata parsing, efficient caching, and consistent performance.

## File Structure

```
tests/
├── test_hub_discovery.py         # Main test suite
├── hub_discovery_test_report.md  # Generated test report
└── TEST_HUB_DISCOVERY.md        # This documentation
```

## Running Tests

### Quick Run
```bash
python tests/test_hub_discovery.py
```

### With Verbose Output
```bash
python tests/test_hub_discovery.py | tee test_output.log
```

### Run Specific Test Category
```python
# Edit test_hub_discovery.py, comment out unwanted tests in run_all_tests()
python tests/test_hub_discovery.py
```

## Test Categories

### 1. Discovery Tests (2 tests)
Validates command file discovery and organization.

- **test_discovery_finds_all_commands**: Ensures all 97 command files are found
- **test_category_inference**: Verifies category extraction from directory paths

**Expected Results:**
- 97 total commands (71 main + 26 docs/utils)
- Categories inferred from directory structure

### 2. Parsing Tests (3 tests)
Validates YAML frontmatter extraction and mode detection.

- **test_frontmatter_parsing**: Tests YAML frontmatter extraction
- **test_mode_extraction**: Tests execution mode detection (default, debug, optimize, release)
- **test_missing_frontmatter_handling**: Tests graceful fallback for files without frontmatter

**Expected Results:**
- All frontmatter fields parsed correctly
- Modes extracted from markdown tables
- Empty dict returned for missing frontmatter (not None or error)

### 3. Cache Tests (3 tests)
Validates cache generation, loading, and invalidation.

- **test_cache_generation**: Tests creation of `_cache.json`
- **test_cache_loading**: Tests loading cached data
- **test_cache_invalidation**: Tests staleness detection when files change

**Expected Results:**
- Cache file created with correct JSON structure
- Cache loads successfully
- Cache invalidates when command files are modified

### 4. Performance Tests (2 tests)
Validates speed targets for discovery operations.

- **test_performance_first_run**: Tests fresh discovery < 200ms
- **test_performance_cached_run**: Tests cached load < 10ms

**Expected Results:**
- First run: ~50-150ms (well under 200ms target)
- Cached run: ~1-5ms (well under 10ms target)

### 5. Statistics Tests (2 tests)
Validates command counting and categorization.

- **test_command_stats**: Tests statistics generation
- **test_all_categories_present**: Tests all expected categories exist

**Expected Results:**
- Total: 97 commands
- Categories: arch, ci, code, dist, docs, git, hub, plan, site, test, utils, workflow
- Commands with modes: ~7 (as of initial implementation, may increase)

## Test Results (Current)

```
Total Tests: 12
Passed: 12/12 (100%)
Total Duration: ~558ms
```

| Category | Passed | Total | Avg Duration |
|----------|--------|-------|--------------|
| Discovery | 2/2 | 2 | ~56ms |
| Parsing | 3/3 | 3 | <1ms |
| Cache | 3/3 | 3 | ~93ms |
| Performance | 2/2 | 2 | ~29ms |
| Statistics | 2/2 | 2 | ~55ms |

## Implementation Status

### Current (Agent 2 - Test Suite)
- ✅ Test suite structure complete
- ✅ 12 comprehensive test cases
- ✅ Stubbed discovery functions for testing
- ✅ All tests passing with expected results
- ✅ Test report generation
- ✅ Documentation complete

### Next Steps (After Agent 1 - Discovery Engine)

Once `commands/_discovery.py` is implemented:

1. **Replace stub functions with actual imports:**
   ```python
   # Remove stub functions
   # Add at top of test_hub_discovery.py:
   from commands._discovery import (
       discover_commands,
       parse_frontmatter,
       generate_cache,
       load_cache,
       get_command_stats
   )
   ```

2. **Run integration tests:**
   ```bash
   python tests/test_hub_discovery.py
   ```

3. **Verify performance targets:**
   - First run < 200ms
   - Cached run < 10ms

4. **Update test expectations if needed:**
   - Adjust expected command counts if structure changes
   - Update category list if new categories added

## Cache File Structure

The discovery engine generates `commands/_cache.json`:

```json
{
  "version": "1.0.0",
  "generated_at": "2026-01-17T11:18:58.777226",
  "total_commands": 97,
  "commands": [
    {
      "path": "commands/do.md",
      "name": "do",
      "category": "hub",
      "description": "Universal command that intelligently routes...",
      "arguments": [
        {
          "name": "task",
          "description": "Natural language description...",
          "required": true
        }
      ],
      "modes": []
    }
  ]
}
```

### Cache Fields

- **version**: Schema version (currently 1.0.0)
- **generated_at**: ISO timestamp of cache generation
- **total_commands**: Total count for quick validation
- **commands**: Array of command objects

### Command Object Fields

- **path**: Relative path from plugin root
- **name**: Command name (filename without .md)
- **category**: Inferred from directory structure
- **description**: From YAML frontmatter
- **arguments**: Array of argument definitions from frontmatter
- **modes**: Execution modes extracted from content

## Stub Functions (Temporary)

Current implementation uses stub functions that simulate the discovery engine:

### stub_discover_commands()
- Walks `commands/` directory recursively
- Parses frontmatter from each .md file
- Extracts category from directory path
- Returns array of command objects

### stub_parse_frontmatter()
- Extracts YAML between `---` markers
- Returns dict of frontmatter fields
- Returns empty dict if no frontmatter (graceful handling)

### stub_generate_cache()
- Creates `commands/_cache.json`
- Writes cache data with version, timestamp, commands
- Returns path to cache file

### stub_load_cache()
- Reads `commands/_cache.json`
- Parses JSON and returns data
- Returns None if cache doesn't exist

### stub_get_command_stats()
- Calculates total command count
- Groups by category
- Counts commands with modes
- Returns statistics object

## Adding New Tests

To add a new test:

1. **Create test function:**
   ```python
   def test_new_feature() -> TestResult:
       """Test description."""
       start = time.time()

       # Test implementation
       result = some_function()

       duration = (time.time() - start) * 1000

       if not result:
           return TestResult(
               "Test Name",
               False,
               duration,
               "Error details",
               "category"
           )

       return TestResult(
           "Test Name",
           True,
           duration,
           "Success details",
           "category"
       )
   ```

2. **Add to test runner:**
   ```python
   def run_all_tests() -> list[TestResult]:
       tests = [
           # ... existing tests
           test_new_feature,  # Add here
       ]
       # ...
   ```

3. **Run and verify:**
   ```bash
   python tests/test_hub_discovery.py
   ```

## Troubleshooting

### Test Failures

**Discovery finds wrong number of commands**
- Check if new commands were added/removed
- Update expected count in test
- Verify `commands/` directory structure

**Frontmatter parsing fails**
- Check YAML syntax in command file
- Ensure `---` markers are on their own lines
- Verify required fields exist

**Cache tests fail**
- Check write permissions on `commands/` directory
- Ensure `_cache.json` can be created/deleted
- Verify JSON serialization works

**Performance tests fail**
- May be due to disk I/O on slow systems
- Acceptable if < 300ms first run, < 20ms cached
- Consider adjusting targets for CI environments

### Common Issues

**Import errors after integration**
- Ensure `commands/__init__.py` exists
- Check `_discovery.py` is in correct location
- Verify function signatures match stubs

**Stale cache**
- Delete `commands/_cache.json`
- Re-run tests to regenerate

**Test file conflicts**
- `_test_no_frontmatter.md` should auto-cleanup
- If left behind, manually delete

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Hub Discovery

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install pyyaml
      - name: Run discovery tests
        run: python tests/test_hub_discovery.py
      - name: Upload test report
        uses: actions/upload-artifact@v3
        with:
          name: test-report
          path: tests/hub_discovery_test_report.md
```

## Performance Benchmarks

### Expected Performance (Post-Integration)

| Operation | Target | Expected | Notes |
|-----------|--------|----------|-------|
| First discovery | < 200ms | 50-150ms | Parse all 97 commands |
| Cached load | < 10ms | 1-5ms | Read JSON file |
| Cache generation | - | 50-100ms | Write JSON file |
| Category inference | - | < 1ms | Per command |
| Frontmatter parse | - | < 1ms | Per command |

### Factors Affecting Performance

- **Disk I/O**: SSD vs HDD
- **File system**: APFS, ext4, NTFS
- **Python version**: 3.11+ faster than 3.9
- **System load**: CPU/memory usage

## Maintenance

### When to Update Tests

- **New commands added**: Update expected count (97 → N)
- **New categories added**: Update category list
- **Frontmatter schema changes**: Update parsing tests
- **Performance regressions**: Investigate and fix
- **Cache format changes**: Update cache tests

### Test Report

After each run, check `tests/hub_discovery_test_report.md`:
- Summary statistics
- Category-by-category results
- Detailed pass/fail information
- Implementation notes

## Related Files

- `commands/_discovery.py` - Discovery engine (Agent 1 implementation)
- `commands/_cache.json` - Generated cache file
- `commands/hub.md` - Hub command using discovery
- `tests/test_craft_plugin.py` - General plugin tests

## References

- [Hub v2.0 Specification](../docs/specs/SPEC-hub-v2-discovery-2026-01-16.md)
- [Craft Plugin Documentation](https://data-wise.github.io/craft/)
- [Python unittest documentation](https://docs.python.org/3/library/unittest.html)
