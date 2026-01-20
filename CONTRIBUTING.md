# Contributing to Craft

Thank you for your interest in contributing to Craft! This document provides guidelines for contributing effectively.

## Quick Start

1. Fork the repository
2. Create a feature branch from `dev`
3. Install development hooks: `./scripts/install-hooks.sh`
4. Make your changes
5. Ensure tests pass
6. Submit a pull request to `dev`

## Development Workflow

### Branch Structure

```text
main (production, protected)
  ↑ PR only
dev (integration hub)
  ↑ branch from here
feature/* (implementation work)
```

**Important Rules:**

- Never commit directly to `main`
- Always start feature branches from `dev`
- Use worktrees for isolated development
- Create PRs to `dev`, not `main`

### Setting Up a Worktree

```bash
# From main repo (stays on main)
cd ~/projects/dev-tools/craft

# Create worktree for your feature
git worktree add ~/.git-worktrees/craft/feature-<name> -b feature/<name> dev

# Work in worktree
cd ~/.git-worktrees/craft/feature-<name>
```

### Development Setup

After creating your worktree, install Git hooks to ensure code quality:

```bash
# One-time setup in your worktree
./scripts/install-hooks.sh
```

This installs:

- **Pre-commit hook**: Automatically checks markdown list spacing (MD030, MD004, MD032)
- Offers interactive auto-fix when violations are found
- Prevents commits with formatting issues

**Bypass hook (not recommended):**

```bash
git commit --no-verify
```

## Code Standards

### Conventional Commits

Use conventional commit format:

```text
<type>: <description>

<optional detailed description>

<optional footer>
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring
- `docs`: Documentation changes
- `test`: Test additions/changes
- `chore`: Maintenance tasks
- `style`: Code style changes (no logic changes)

**Examples:**

```text
feat: add markdownlint list spacing enforcement
fix: resolve pre-commit hook race condition
docs: update API reference for v2.0
test: add integration tests for hub discovery
refactor: simplify command parsing logic
```

### Documentation Standards

#### Markdown Quality

All markdown documentation must pass `/craft:docs:lint` checks:

**Required Rules (auto-fixable):**

- **MD030**: List spacing - exactly 1 space after markers

  ```markdown
  ✅ Correct: - Item with 1 space
  ❌ Wrong:  - Item with 2 spaces
  ```

- **MD004**: List marker style - use `-` (dash) consistently

  ```markdown
  ✅ Correct: - Dash marker
  ❌ Wrong: * Asterisk marker
  ❌ Wrong: + Plus marker
  ```

- **MD032**: Blank lines around lists

  ```markdown
  ✅ Correct: Text before list

  - List item
  ```

  ```markdown
  ❌ Wrong: Text before list
  - List item
  ```

**Auto-fixing issues:**

```bash
# Fix all auto-fixable issues
/craft:docs:lint --fix

# Preview changes without modifying
/craft:docs:lint --fix --dry-run
```

**Checking your documentation:**

```bash
# Check for markdown quality issues
/craft:docs:lint

# Check for broken links
/craft:docs:check-links
```

**Pre-commit validation:**

- Pre-commit hooks automatically check staged `.md` files
- Hooks offer interactive auto-fix prompt
- Block commits with MD030/MD004/MD032 violations

#### Command Documentation

All commands must have proper frontmatter:

```yaml
---
description: Clear one-line description
category: <category>
arguments:
  - name: <arg-name>
    description: Argument description
    required: true|false
    default: <default-value>
---
```

**Required sections:**

- Description (one-line in frontmatter)
- Purpose (what the command does)
- Usage examples
- Options/arguments
- Related commands

## Testing

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/

# Run specific test suite
python3 -m pytest tests/test_craft_plugin.py

# Run with verbose output
python3 -m pytest tests/ -v

# Run specific test
python3 -m pytest tests/test_craft_plugin.py::test_command_exists
```

### Test Coverage

- Aim for >80% test coverage
- Test happy paths and error cases
- Test edge cases and boundaries
- Mock external dependencies (npx, gh, etc.)

### Adding Tests

Test file naming convention:

- `test_<feature>.py` for unit tests
- `test_integration_<feature>.py` for integration tests
- `test_e2e_<feature>.py` for end-to-end tests

## Pull Request Process

### Before Submitting

1. **Update documentation**: Add/update docs for new features
2. **Run tests**: Ensure all tests pass
3. **Lint code**: Check for style issues
4. **Check links**: Validate all markdown links work
5. **Write description**: Clear PR description with:
   - Summary of changes
   - Testing performed
   - Breaking changes (if any)

### PR Template

```markdown
## Summary
Brief description of what this PR does and why.

## Changes
- Bulleted list of key changes
- Include file paths if relevant

## Testing
- ✅ Unit tests pass
- ✅ Integration tests pass
- ✅ Manual testing performed
- ✅ Documentation updated

## Checklist
- [ ] Code follows project style
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] All tests passing
- [ ] No breaking changes (or documented)
```

## Documentation Structure

```text
craft/
├── commands/          # Command documentation (Markdown)
│   └── docs/
│       └── lint.md   # Example: /craft:docs:lint command
├── docs/
│   ├── guide/        # User guides
│   ├── specs/        # Implementation specs
│   └── help/        # Command reference docs
└── skills/           # Skill definitions
    └── validation/    # Hot-reload validators
```

### Writing Guides

Guides in `docs/guide/` should:

- Start with TL;DR summary
- Include time estimate
- Have clear step-by-step instructions
- Provide before/after examples
- Include troubleshooting section

**Example guide structure:**

```markdown
# Feature Name Guide

> **TL;DR** (2 minutes)
> - Step 1: Quick action
> - Step 2: Quick action
> - Goal: Outcome

## What You'll Learn

1. ✅ First learning outcome
2. ✅ Second learning outcome

## Prerequisites

- Requirement 1
- Requirement 2

## Getting Started

### Step 1: First Step

Description...

**Example:**

```bash
# Command or code
```

## Troubleshooting

### Common Issue

**Symptom:** What happens
**Solution:** How to fix it

```text
(placeholder for troubleshooting examples)
```

## Development Tools

### Python

- Python 3.14+
- `pytest` for testing
- `black` for formatting (optional)

### Node.js

- Used for markdownlint and link-checking
- Auto-installed via npx when needed

### Git Hooks

Pre-commit hooks are stored in `.git/hooks/`:

- Pre-commit hook validates markdown quality
- Hooks are not tracked in git (they're local)
- Use `.gitignore` for hook-related files

## Getting Help

### Documentation

- [Commands Reference](https://data-wise.github.io/craft/commands/)
- [User Guides](https://data-wise.github.io/craft/guide/)
- [API Reference](https://data-wise.github.io/craft/reference/)

### Issues

- [GitHub Issues](https://github.com/Data-Wise/craft/issues)
- Check existing issues before creating new ones
- Use issue templates when available

### Discussions

- [GitHub Discussions](https://github.com/Data-Wise/craft/discussions)
- For questions and general discussion

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
