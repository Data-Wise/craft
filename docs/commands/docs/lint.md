# /craft:docs:lint

> **Markdown quality and error detection with auto-fix**

---

## Synopsis

```bash
/craft:docs:lint [path] [--fix]
```

**Quick examples:**

```bash
# Check all markdown files for issues
/craft:docs:lint

# Auto-fix safe issues with confirmation
/craft:docs:lint --fix

# Check a specific directory
/craft:docs:lint docs/guide/
```

---

## Description

Detects and fixes markdown formatting errors using `markdownlint-cli2` with 30 embedded rules. Focuses on errors that break rendering (list formatting, code fences, trailing spaces) rather than style enforcement.

Philosophy: "Auto-fix what's safe, prompt for what matters." Safe issues like trailing spaces and missing blank lines before lists are fixed automatically. Complex issues like heading hierarchy skips or ambiguous code fence languages prompt for a decision.

The command detects whether `markdownlint-cli2` is installed globally (faster) or falls back to `npx` (auto-downloads). Install globally with `npm install -g markdownlint-cli2` for best performance.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `path` | Specific file or directory to lint | `.` (all docs) |
| `--fix` | Auto-fix safe issues (previews changes before applying) | `false` |

---

## What It Checks

**Critical rules (always enabled):**

- **List formatting** — Blank lines around lists (MD032), consistent markers (MD004), spacing after markers (MD030)
- **Code fences** — Language tag required (MD040), fenced style (MD046), backtick style (MD048)
- **Whitespace** — Trailing spaces (MD009), hard tabs (MD010), multiple blank lines (MD012)
- **Links** — Reversed syntax (MD011), empty links (MD042), image alt text (MD045)
- **Headings** — ATX style (MD003), blank lines around headings (MD022)

**Relaxed rules (Craft-specific):**

- Line length (MD013) disabled — long command examples are common
- Inline HTML (MD033) allowed — skill/agent tags need HTML elements
- First-line heading (MD041) disabled — files use frontmatter
- Duplicate headings (MD024) allowed for siblings — multiple "Examples" sections are valid

---

## Auto-Fix Behavior

**Automatically fixed (no confirmation):** trailing spaces, hard tabs, multiple blank lines, list spacing, inconsistent markers, bare URLs, emoji-attribute spacing (CRAFT-001).

**Prompts for decision:** heading hierarchy skips, unknown code fence languages, inconsistent fence styles.

When `--fix` is used, a preview of all changes is shown before applying. Fixes are re-verified by running lint again after application.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No issues or all issues auto-fixable |
| 1 | Manual fixes needed |
| 2 | Linting error (check command syntax) |

---

## See Also

- [/craft:docs:check](check.md) — Full documentation health check
- [/craft:docs:mermaid](mermaid.md) — Mermaid diagram generation and validation
