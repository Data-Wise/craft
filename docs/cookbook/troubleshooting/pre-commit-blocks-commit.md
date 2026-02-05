---
title: "Troubleshooting: Pre-Commit Blocks Commit"
description: "Fix pre-commit hook failures that prevent git commits"
category: "cookbook"
level: "beginner"
time_estimate: "4 minutes"
related:
  - ../../guide/documentation-quality.md
  - ../../commands/code.md
---

# Troubleshooting: Pre-Commit Blocks Commit

**Level:** Beginner

## Problem

Running `git commit` triggers pre-commit hooks and the commit is rejected:

```
$ git commit -m "feat: add new command"
markdownlint-cli2..................................................Failed
- hook id: markdownlint-cli2
docs/guide/new-feature.md:15 MD032/blanks-around-lists
docs/guide/new-feature.md:28 MD040/fenced-code-language

emoji-attr-spacing.................................................Failed
- hook id: emoji-attr-spacing
docs/index.md:42 CRAFT-001: space between emoji and attr_list
```

## Common Causes & Solutions

### 1. Markdownlint Failures (24 Rules)

**Issue:** Markdown files violate enforced rules. Common violations:

- `MD032` — Missing blank line before/after list
- `MD040` — Fenced code block without language tag
- `MD009` — Trailing whitespace

**Solution:**

```bash
npx markdownlint-cli2 "**/*.md"          # See all issues
npx markdownlint-cli2 --fix "**/*.md"    # Auto-fix
```

### 2. Emoji-Attribute Spacing (CRAFT-001)

**Issue:** Space between emoji shortcode and `attr_list` breaks MkDocs rendering.

```markdown
:material-code-tags: { .lg .middle }   <!-- Wrong: space before { -->
:material-code-tags:{ .lg .middle }    <!-- Correct: no space -->
```

**Solution:**

```bash
bash scripts/docs-lint-emoji.sh          # Check violations
bash scripts/docs-lint-emoji.sh --fix    # Auto-fix
```

### 3. CLAUDE.md Budget Check Failure

**Issue:** CLAUDE.md exceeds the line budget (150-line target for new projects).

**Solution:**

1. Run the optimizer: `/craft:docs:claude-md:sync`
2. Move detail to `docs/VERSION-HISTORY.md` or `docs/ARCHITECTURE.md`

### 4. Bypassing Hooks (Emergency Only)

```bash
git commit --no-verify -m "wip: urgent fix, lint cleanup follows"
```

Use sparingly. CI will still catch issues on push.

## Verification Steps

```bash
npx markdownlint-cli2 "**/*.md"           # Check markdown
bash scripts/docs-lint-emoji.sh            # Check CRAFT-001
bash scripts/claude-md-budget-check.sh     # Check budget
git add -A && git commit -m "feat: add new command"  # Retry
```

## Related

- [Documentation Quality Guide](../../guide/documentation-quality.md) — Full lint rule reference
- [Code Commands](../../commands/code.md) — Lint and quality commands
