# Tutorial: docs:lint — Markdown Quality Checks

By the end of this tutorial you will have:

- Linted your Markdown documentation for formatting errors
- Used `--fix` to auto-correct violations
- Scoped the check to a specific file or directory

**Prerequisites:** craft installed, `markdownlint` available (or auto-installed via pre-commit).

---

## Step 1: Lint All Documentation

```
/craft:docs:lint
```

Scans all Markdown files and reports violations:

```
Docs Lint — docs/
───────────────────
Linting 47 files...

Issues found:
  docs/guide/installation.md:15  MD031  Fenced code blocks should be surrounded by blank lines
  docs/guide/installation.md:23  MD032  Lists should be surrounded by blank lines
  docs/reference/commands.md:8   MD013  Line length (147 chars, max: 120)
  docs/tutorials/index.md:1      MD041  First line should be a top-level heading

4 issues (0 errors, 4 warnings)
```

---

## Step 2: Auto-Fix Violations

```
/craft:docs:lint --fix
```

Applies markdownlint's auto-fixable rules in place:

- MD031/MD032: adds blank lines around fenced blocks and lists
- MD009: trims trailing whitespace

Non-auto-fixable rules (MD013 line length, MD041 heading) are reported but not changed.

---

## Step 3: Lint a Specific Path

```
/craft:docs:lint --path docs/tutorials
/craft:docs:lint --path docs/guide/installation.md
```

---

## Step 4: Common Violations

| Rule | Description | Auto-fixable |
|------|-------------|:---:|
| MD031 | Blank lines around fenced code blocks | ✅ |
| MD032 | Blank lines around lists | ✅ |
| MD009 | Trailing whitespace | ✅ |
| MD013 | Line length > 120 chars | ❌ |
| MD041 | First line not a heading | ❌ |
| MD051 | Link reference definitions | ❌ |

---

## Step 5: Pre-Commit Hook

The craft pre-commit hook runs `docs:lint --fix` automatically on staged `.md` files. If the hook auto-fixes a file, re-stage it and create a new commit (the original commit gets rolled back by the hook).

---

## What's Next

- Run before every PR that adds or modifies documentation
- Use `/craft:docs:check` for the broader health check that includes link validation
- See the [pre-commit auto-fix pattern](../guide/branch-guard-smart-mode.md) for hook behavior details
