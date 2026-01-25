# AGENTS.md - Development Guidelines for Craft Plugin

This document provides development guidelines for agentic coding assistants working on the Craft plugin repository. It covers build/lint/test commands, code style conventions, and project-specific practices.

## Build/Lint/Test Commands

### Primary Test Commands

```bash
# Run all unit tests (581+ tests, ~90% coverage)
python3 tests/test_craft_plugin.py

# Run all tests with pytest (includes integration tests)
python3 -m pytest tests/ -v

# Run specific test file
python3 tests/test_craft_plugin.py::TestClass::test_method

# Run integration tests only
python3 tests/test_integration_*.py

# Run dependency system tests
bash tests/test_dependency_management.sh

# Run specific integration test
python3 tests/test_integration_dependency_system.py
```

### Linting and Validation

```bash
# Validate command/skill/agent counts match documentation
./scripts/validate-counts.sh

# Markdown linting (24 rules enforced)
npx markdownlint-cli2 "**/*.md" --config .markdownlint.json

# Build documentation site
mkdocs build

# Check broken links (with ignore rules)
python3 tests/test_craft_plugin.py -k "broken_links"
```

### Development Workflow

```bash
# Quick validation (lint + test counts)
./scripts/validate-counts.sh && python3 tests/test_craft_plugin.py

# Full CI validation
python3 -m pytest tests/ -v && npx markdownlint-cli2 "**/*.md"

# Documentation validation
mkdocs build && python3 tests/test_craft_plugin.py -k "broken_links"
```

## Code Style Guidelines

### Python Conventions

#### Imports

```python
# Standard library imports first
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Third-party imports (none in this project)

# Local imports (alphabetized)
from .complexity_scorer import calculate_complexity_score
from .validators import validate_command_structure
```

#### Type Hints

- **Always use type hints** for function parameters and return values
- Use `Optional[T]` for nullable types, not `Union[T, None]`
- Use `List[T]`, `Dict[K, V]` instead of bare `list`, `dict`
- Use dataclasses with `field()` for complex defaults

```python
def calculate_complexity_score(task: str) -> int:
    """Calculate complexity score for a task."""

@dataclass
class TestResult:
    name: str
    passed: bool
    duration_ms: float
    details: str
    category: str = "general"
```

#### Error Handling

- Use specific exception types, not bare `Exception`
- Provide descriptive error messages
- Log errors appropriately with context

```python
try:
    result = risky_operation()
except FileNotFoundError as e:
    log(f"Configuration file not found: {config_path}")
    return TestResult(name, False, 0, f"Missing config: {e}", "structure")
except json.JSONDecodeError as e:
    log(f"Invalid JSON in plugin.json: {e}")
    return TestResult(name, False, 0, f"JSON parse error: {e}", "structure")
```

#### Naming Conventions

- **Functions**: `snake_case` (e.g., `calculate_complexity_score`)
- **Classes**: `PascalCase` (e.g., `IgnorePattern`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MULTI_STEP_INDICATORS`)
- **Variables**: `snake_case` (e.g., `task_lower`)
- **Methods**: `snake_case`, descriptive names

#### Documentation

- **Always include docstrings** for public functions and classes
- Use triple quotes with proper formatting
- Include Args and Returns sections for complex functions

```python
def should_ignore(self, source_file: str, target_link: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a broken link should be ignored.

    Args:
        source_file: Path to the file containing the link
        target_link: The broken link target

    Returns:
        (should_ignore, category) tuple
    """
```

### Markdown Conventions

#### Frontmatter (for Commands/Skills/Agents)

```yaml
---
description: Brief description of the command
arguments:
  - name: mode
    description: Execution mode
    required: false
    default: default
  - name: path
    description: Target path
    required: true
---
```

#### Formatting Rules (from .markdownlint.json)

- **Lists**: Use dashes (`-`) not asterisks (`*`)
- **Line length**: No hard limit (MD013 disabled)
- **Headers**: No duplicate headers in same section (MD024 with siblings_only)
- **Inline HTML**: Limited allowed elements (MD033)
- **List spacing**: Consistent single-line spacing (MD030)
- **Code blocks**: Use fenced code blocks with language specification

#### Table Formatting

```markdown
| Mode | Time | Focus |
|------|------|-------|
| default | < 30s | Quick smoke tests |
| debug | < 120s | Verbose with traces |
```

### Git Workflow

#### Commit Messages

- Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
- Keep first line under 50 characters
- Use imperative mood ("Add feature" not "Added feature")
- Reference issues when applicable

```bash
git commit -m "feat: add complexity scoring for task routing"
git commit -m "fix: resolve broken link validation in docs"
git commit -m "test: add integration tests for dependency system"
```

#### Branching

- **Never commit directly to main** - always use feature branches
- Use worktrees for isolation: `git worktree add ../feature-name -b feature/name`
- Branch naming: `feature/description`, `fix/issue-number`

### Project Structure

#### Command Organization

- Commands in `commands/` directory with category subdirs
- Each command is a `.md` file with frontmatter
- Frontmatter defines arguments, descriptions, defaults

#### Test Organization

- Unit tests in `tests/test_*.py`
- Integration tests in `tests/test_integration_*.py`
- Test shell scripts in `tests/*.sh`
- Use descriptive test method names: `test_should_ignore_broken_links`

#### File Structure Expectations

```bash
commands/
├── arch/          # Architecture analysis commands
├── ci/           # CI/CD commands
├── code/         # Code quality commands
├── docs/         # Documentation commands
└── git/          # Git workflow commands

skills/           # Specialized capabilities
agents/           # Multi-step task handlers
utils/            # Shared Python utilities
scripts/          # Shell scripts and tools
```

### Testing Practices

#### Unit Tests

- Test individual functions/classes in isolation
- Use descriptive test names that explain the scenario
- Mock external dependencies
- Assert both positive and negative cases

```python
def test_calculate_complexity_score():
    # Test multi-step task detection
    score = calculate_complexity_score("lint and test the code")
    assert score >= 2, "Multi-step tasks should score at least 2"

    # Test simple task
    score = calculate_complexity_score("run tests")
    assert score < 2, "Simple tasks should score less than 2"
```

#### Integration Tests

- Test component interactions
- Use realistic test data
- Validate end-to-end workflows
- Clean up test artifacts

#### Test Coverage

- Target 90%+ coverage
- Focus on critical paths
- Include edge cases and error conditions

### Security Considerations

#### File Operations

- **Never** commit secrets or credentials
- Use absolute paths for file operations
- Validate file paths before operations
- Handle file permissions appropriately

#### Input Validation

- Sanitize user inputs
- Validate file paths exist before operations
- Use type hints to catch type-related issues early

### Performance Guidelines

#### Code Efficiency

- Prefer list comprehensions over explicit loops when appropriate
- Use `pathlib.Path` for path operations
- Cache expensive operations when possible
- Profile performance-critical code

#### Test Performance

- Keep unit tests under 100ms each
- Use appropriate fixtures for test data
- Parallelize independent tests when possible
- Mock slow external dependencies

### Documentation Standards

#### README Updates

- Update README.md when adding new features
- Include usage examples and screenshots
- Document breaking changes clearly
- Keep installation instructions current

#### Inline Documentation

- Comment complex algorithms
- Explain non-obvious business logic
- Document API contracts and expectations

### CI/CD Integration

#### Pre-commit Hooks

- Markdown linting enforced (24 rules)
- Count validation for commands/skills/agents
- Test execution required
- Link validation with ignore patterns

#### Release Process

- Update version in package.json
- Run full test suite
- Validate documentation builds
- Create GitHub release with changelog

### Troubleshooting

#### Common Issues

- **Count mismatches**: Run `./scripts/validate-counts.sh` to identify discrepancies
- **Test failures**: Check for missing dependencies or environment issues
- **Link validation errors**: Update `.linkcheck-ignore` for known broken links
- **Markdown linting**: Run `npx markdownlint-cli2 "**/*.md"` to identify issues

#### Debug Commands

```bash
# Verbose test output
python3 -m pytest tests/ -v -s

# Debug specific test
python3 -m pytest tests/test_craft_plugin.py::test_plugin_json_exists -v -s

# Profile test performance
python3 -m pytest tests/ --durations=10
```

This guide ensures consistent development practices across all contributors to the Craft plugin project.
