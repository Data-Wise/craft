# /craft:docs:prompt

> **Generate reusable prompts for common documentation tasks**

---

## Synopsis

```bash
/craft:docs:prompt [type]
```

**Quick examples:**

```bash
# Show interactive prompt type menu
/craft:docs:prompt

# Generate a full maintenance prompt
/craft:docs:prompt full

# Generate a content audit prompt
/craft:docs:prompt audit
```

---

## Description

Generates ready-to-use prompts for documentation maintenance workflows. Each prompt is pre-filled with project context (name, version, doc count, site URL) and saved to a markdown file in the project root.

Designed for use with Claude Code or any AI assistant. The generated prompts follow ADHD-friendly design principles: progressive disclosure, visual hierarchy, clear action codes, and phased implementation plans.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `full` | Complete maintenance prompt covering all doc tasks | -- |
| `reorganize` | Navigation restructuring prompt | -- |
| `audit` | Content quality and inventory prompt | -- |
| `edit FILE` | Editing prompt for a specific file | -- |
| `cancel` | Exit without action | -- |
| *(none)* | Show interactive prompt type menu | -- |

---

## What It Generates

Each prompt type produces a different focus:

- **Full Maintenance** -- Covers navigation, content audit, editing, consolidation, gap analysis, and style consistency. Includes content health criteria and action codes.
- **Reorganize** -- Focused on navigation restructuring with ADHD-friendly design constraints (max 7 top-level sections, progressive disclosure).
- **Audit** -- Content inventory with status tracking: checks for outdated versions, duplicates, missing docs, broken links, and formatting issues.
- **Edit** -- File-specific editing prompt with clarity standards (tables over paragraphs, copy-paste examples, bullet points over prose).

Generated prompts are saved as `PROMPT-DOCS-<TYPE>.md` in the project root.

---

## See Also

- [/craft:docs:check](check.md) -- Full documentation health check
- [/craft:docs:update](update.md) -- Update documentation
- [/craft:docs:sync](sync.md) -- Smart documentation detection
