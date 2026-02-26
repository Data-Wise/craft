# /craft:docs:nav-update

> **Update mkdocs.yml navigation from directory structure**

---

## Synopsis

```bash
/craft:docs:nav-update [options]
```

**Quick examples:**

```bash
# Scan docs and update navigation
/craft:docs:nav-update

# Preview navigation changes without modifying mkdocs.yml
/craft:docs:nav-update --dry-run
```

---

## Description

Keeps the `mkdocs.yml` navigation section in sync with the actual files in `docs/`. Scans the documentation directory, compares it against the current nav entries, and produces an update plan showing additions, removals, and orphan files.

The command infers page titles from H1 headings, YAML frontmatter, or filename conversion (kebab-case to Title Case). It places new files into the appropriate nav section based on their directory location and alphabetical ordering.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--dry-run`, `-n` | Preview changes without executing | `false` |

---

## How It Works

1. **Scan** -- Finds all `.md` files under `docs/` and reads the current `nav:` from `mkdocs.yml`.
2. **Compare** -- Identifies new files not in nav, dead entries pointing to deleted files, and orphan files that exist but are excluded.
3. **Plan** -- Displays a structured update plan with proposed additions, removals, and the resulting nav structure. Prompts for confirmation before applying.
4. **Update** -- Writes the updated `nav:` section to `mkdocs.yml`.

### Smart Features

- **Title inference** from H1 headings, frontmatter, or filenames
- **Section detection** based on directory structure
- **Orphan handling** with options to add, move to `_drafts/`, delete, or ignore
- **Structure validation** with reorganization suggestions

---

## See Also

- [/craft:docs:check](check.md) -- Full documentation health check
- [/craft:docs:site](site.md) -- Website documentation focus
- [/craft:docs:sync](sync.md) -- Smart documentation detection
