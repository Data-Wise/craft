# /craft:docs:check

> **Full documentation health check with auto-fix capabilities**

---

## Synopsis

```bash
/craft:docs:check [options]
```

**Quick examples:**

```bash
# Check docs health and report issues
/craft:docs:check

# Auto-fix safe issues (broken links, stale refs)
/craft:docs:check --fix

# Preview changes without modifying files
/craft:docs:check --dry-run
```

---

## Description

Performs comprehensive documentation health checks including broken links, stale documentation references, navigation consistency, and MkDocs configuration validation. Automatically fixes safe issues when `--fix` is enabled.

Philosophy: "Just run it. It fixes what it can and tells you what needs attention."

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--fix` | Auto-fix safe issues (broken links, stale refs) | `false` |
| `--dry-run`, `-n` | Preview changes without modifying files | `false` |

---

## What It Checks

- **Broken Links**: Internal and external link validity
- **Stale Docs**: References to removed/renamed files
- **Navigation**: mkdocs.yml navigation consistency
- **Formatting**: Markdownlint compliance
- **Structure**: Missing required sections

---

## Auto-Fix Capabilities

When `--fix` is enabled, automatically repairs:

- Broken internal links (updates paths)
- Stale file references (removes or updates)
- Navigation inconsistencies (syncs with actual files)
- Safe formatting issues (spacing, list markers)

Manual attention required for:

- External broken links (may be temporary)
- Major structural issues
- Content accuracy problems

---

## See Also

- [/craft:docs:sync](sync.md) — Smart documentation detection
- [/craft:docs:update](update.md) — Update documentation
- [/craft:check](../check.md) — Pre-flight validation
