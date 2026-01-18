#!/usr/bin/env python3
"""
Test YAML Parser Edge Cases
============================
Validates custom YAML parser handles edge cases correctly.

Run with: python tests/test_hub_yaml_edge_cases.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from commands._discovery import parse_yaml_frontmatter


class TestYAMLParserEdgeCases:
    """Test edge cases in YAML frontmatter parsing."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def run_test(self, test_name, test_func):
        """Run a single test and track results."""
        try:
            start = datetime.now()
            test_func()
            duration = (datetime.now() - start).total_seconds() * 1000
            self.passed += 1
            self.tests.append((test_name, True, duration, ""))
            print(f"  ✅ PASS ({duration:.1f}ms) - {test_name}")
        except AssertionError as e:
            self.failed += 1
            self.tests.append((test_name, False, 0, str(e)))
            print(f"  ❌ FAIL - {test_name}: {e}")
        except Exception as e:
            self.failed += 1
            self.tests.append((test_name, False, 0, f"Exception: {e}"))
            print(f"  ❌ ERROR - {test_name}: {e}")

    def test_empty_frontmatter(self):
        """Test file with empty frontmatter section."""
        content = """---
---
# Command without metadata
"""
        result = parse_yaml_frontmatter(content)
        assert result == {}, f"Expected empty dict, got {result}"

    def test_no_frontmatter(self):
        """Test file without frontmatter."""
        content = """# Command without frontmatter
Just markdown content.
"""
        result = parse_yaml_frontmatter(content)
        assert result == {}, f"Expected empty dict, got {result}"

    def test_simple_key_value_pairs(self):
        """Test parsing simple key-value pairs."""
        content = """---
name: test-command
description: Test description
category: test
---
# Test
"""
        result = parse_yaml_frontmatter(content)
        assert 'name' in result
        assert result['name'] == 'test-command'
        assert result['description'] == 'Test description'
        assert result['category'] == 'test'

    def test_boolean_values(self):
        """Test parsing boolean values."""
        content = """---
tutorial: true
dry_run: false
---
"""
        result = parse_yaml_frontmatter(content)
        assert 'tutorial' in result
        assert 'dry_run' in result
        # Parser treats as strings
        assert result['tutorial'] in ['true', True]
        assert result['dry_run'] in ['false', False]

    def test_numeric_values(self):
        """Test parsing numeric values."""
        content = """---
priority: 1
timeout: 300
version: 2.0
---
"""
        result = parse_yaml_frontmatter(content)
        assert 'priority' in result
        assert 'timeout' in result
        assert 'version' in result
        # Parser treats as strings
        assert result['priority'] in ['1', 1]

    def test_indented_arrays(self):
        """Test arrays with indentation."""
        content = """---
tags:
  - code-quality
  - testing
  - ci-cd
---
"""
        result = parse_yaml_frontmatter(content)
        assert 'tags' in result
        assert isinstance(result['tags'], list)
        assert len(result['tags']) == 3
        assert 'code-quality' in result['tags']

    def test_nested_objects_in_arrays(self):
        """Test complex nested structure (command arguments)."""
        content = """---
arguments:
  - name: mode
    description: Execution mode
  - name: path
    description: File path
---
"""
        result = parse_yaml_frontmatter(content)
        assert 'arguments' in result
        assert isinstance(result['arguments'], list)
        assert len(result['arguments']) == 2
        # Verify first argument
        assert isinstance(result['arguments'][0], dict)
        assert result['arguments'][0]['name'] == 'mode'
        assert 'description' in result['arguments'][0]

    def test_unicode_characters(self):
        """Test frontmatter with unicode."""
        content = """---
name: test-command
description: Command with emoji 🚀 and unicode ñ
---
"""
        result = parse_yaml_frontmatter(content)
        assert 'description' in result
        assert '🚀' in result['description']
        assert 'ñ' in result['description']

    def test_very_long_values(self):
        """Test handling of very long string values."""
        long_desc = "A" * 500
        content = f"""---
name: test-command
description: {long_desc}
---
"""
        result = parse_yaml_frontmatter(content)
        assert len(result['description']) == 500

    def test_trailing_whitespace(self):
        """Test frontmatter with trailing whitespace."""
        content = """---
name: test-command
description: Test
---
"""
        result = parse_yaml_frontmatter(content)
        # Parser should strip trailing whitespace
        assert result['name'] == 'test-command'
        assert result['description'] == 'Test'

    def test_colons_in_unquoted_strings(self):
        """Test handling colons in command names."""
        content = """---
name: test:command
category: code
---
"""
        result = parse_yaml_frontmatter(content)
        assert result['name'] == 'test:command'
        assert result['category'] == 'code'

    def test_multiple_arrays(self):
        """Test multiple arrays in frontmatter."""
        content = """---
tags:
  - tag1
  - tag2
modes:
  - default
  - debug
related_commands:
  - command1
  - command2
---
"""
        result = parse_yaml_frontmatter(content)
        assert 'tags' in result
        assert 'modes' in result
        assert 'related_commands' in result
        assert len(result['tags']) == 2
        assert len(result['modes']) == 2
        assert len(result['related_commands']) == 2


def main():
    """Run all YAML parser edge case tests."""
    print("=" * 70)
    print("🧪 Hub v2.0 YAML Parser Edge Case Tests")
    print("=" * 70)
    print()

    tester = TestYAMLParserEdgeCases()

    # Run all tests
    tests = [
        ("Empty frontmatter", tester.test_empty_frontmatter),
        ("No frontmatter", tester.test_no_frontmatter),
        ("Simple key-value pairs", tester.test_simple_key_value_pairs),
        ("Boolean values", tester.test_boolean_values),
        ("Numeric values", tester.test_numeric_values),
        ("Indented arrays", tester.test_indented_arrays),
        ("Nested objects in arrays", tester.test_nested_objects_in_arrays),
        ("Unicode characters", tester.test_unicode_characters),
        ("Very long values", tester.test_very_long_values),
        ("Trailing whitespace", tester.test_trailing_whitespace),
        ("Colons in unquoted strings", tester.test_colons_in_unquoted_strings),
        ("Multiple arrays", tester.test_multiple_arrays),
    ]

    for test_name, test_func in tests:
        tester.run_test(test_name, test_func)

    print()
    print("=" * 70)
    print(f"📊 Results: {tester.passed}/{len(tests)} tests passed")
    print("=" * 70)

    if tester.failed > 0:
        print(f"\n❌ {tester.failed} test(s) failed")
        return 1
    else:
        print("\n✅ All YAML parser edge case tests passed!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
