---
title: "Tutorial: CRAFT-001 Emoji-Attribute Spacing"
description: "Fix emoji-attribute spacing issues that break MkDocs rendering"
difficulty: beginner
time_estimate: "10 min"
prerequisites: ["bash", "markdown familiarity"]
version: "v2.11.0"
---

# CRAFT-001: Fixing Emoji-Attribute Spacing

## What You'll Learn

- Why spacing between emoji shortcodes and `{` breaks MkDocs rendering
- How to detect violations in your docs
- How to auto-fix them
- How to prevent them with pre-commit hooks

## The Problem

MkDocs uses the `attr_list` extension to attach CSS classes to elements.
Emojis use shortcode syntax like `:rocket:`. When you combine them, spacing
matters:

```markdown
<!-- BROKEN - space between :emoji: and { -->
:rocket: { .card-icon }

<!-- CORRECT - no space -->
:rocket:{ .card-icon }
```

With the space, MkDocs treats `{ .card-icon }` as plain text instead of an
attribute block. The emoji renders but the CSS class never attaches, so
styling silently breaks.

**Why this happens:** Prettier and other formatters automatically insert a
space before `{`, following standard formatting rules. This is correct for
most languages but breaks MkDocs attribute lists.

## Step 1: Check Your Project

Run the CRAFT-001 checker from your project root:

```bash
bash scripts/docs-lint-emoji.sh
```

**Clean output (exit 0):**

```
(no output - all clear)
```

**Violation found (exit 1):**

```
  docs/index.md:42 CRAFT-001 Emoji-attribute spacing: remove space before {
    :rocket: { .card-icon }

CRAFT-001: Found 1 emoji-attribute spacing issue(s)
  Fix: remove space between :emoji: and { so attr_list attaches correctly
  Run with --fix to auto-fix
```

The output shows the file, line number, and the offending content.

## Step 2: Auto-Fix Violations

Add `--fix` to automatically repair all violations:

```bash
bash scripts/docs-lint-emoji.sh --fix
```

Output:

```
  docs/index.md:42 CRAFT-001 Emoji-attribute spacing: remove space before {
    :rocket: { .card-icon }

CRAFT-001: Fixed 1 emoji-attribute spacing issue(s) in 1 file(s)
```

The script uses `sed` to remove the space between `:emoji:` and `{`. It
handles both macOS and Linux `sed` variants automatically.

**Verify the fix:**

```bash
bash scripts/docs-lint-emoji.sh
# (no output = clean)
echo $?
# 0
```

## Step 3: Understand What's Excluded

The checker skips certain directories to avoid false positives:

| Directory | Why Excluded |
|-----------|-------------|
| `node_modules/` | Third-party code |
| `.pytest_cache/` | Test artifacts |
| `brainstorm/` | Working drafts (gitignored) |
| `fixtures/` | Test fixture data |

It also skips violations inside fenced code blocks (`` ``` ``), so examples
in documentation won't trigger false positives.

## Step 4: Set Up Pre-Commit Hook

The hook is already configured in `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: emoji-attr-spacing
      name: Check emoji-attribute spacing (CRAFT-001)
      entry: bash -c 'scripts/docs-lint-emoji.sh'
      language: system
      files: '\.md$'
      pass_filenames: false
```

Install pre-commit if you haven't:

```bash
pip install pre-commit
pre-commit install
```

Now every commit touching `.md` files will check for emoji-attribute spacing
automatically. If a violation is found, the commit is blocked with a clear
error message.

## Step 5: CI Integration

CRAFT-001 runs in the `docs-quality.yml` GitHub Actions workflow:

```yaml
- name: Check emoji-attribute spacing (CRAFT-001)
  run: bash scripts/docs-lint-emoji.sh
```

This catches any violations that slip past the pre-commit hook (e.g., commits
made with `--no-verify`).

## Quick Reference

| Command | Purpose |
|---------|---------|
| `bash scripts/docs-lint-emoji.sh` | Check for violations |
| `bash scripts/docs-lint-emoji.sh --fix` | Auto-fix violations |
| `pre-commit run emoji-attr-spacing` | Run hook manually |
| `pre-commit run emoji-attr-spacing --all-files` | Check all files |

| Exit Code | Meaning |
|-----------|---------|
| `0` | No violations (or fixed with `--fix`) |
| `1` | Violations found (check mode only) |

## Common Patterns

**Grid cards with emoji icons (docs/index.md):**

```markdown
<!-- Before (broken) -->
:rocket: { .card-icon }

<!-- After (correct) -->
:rocket:{ .card-icon }
```

**Admonition-style emoji markers:**

```markdown
<!-- Before (broken) -->
:warning: { .admonition-icon }

<!-- After (correct) -->
:warning:{ .admonition-icon }
```

## Troubleshooting

**"Permission denied" running the script:**

```bash
chmod +x scripts/docs-lint-emoji.sh
```

**Pre-commit hook not running:**

```bash
pre-commit install  # Reinstall hooks
```

**Prettier keeps adding the space back:**

Add a `.prettierignore` file:

```
# Prevent prettier from breaking emoji-attribute spacing
docs/**/*.md
```

## Next Steps

- Run `/craft:docs:lint` for comprehensive markdown linting
- See the [Documentation Quality Guide](../guide/documentation-quality.md) for all lint rules
- Check the 50 CRAFT-001 tests in `tests/test_craft_001_emoji_spacing.py` for edge case examples
