# /craft:docs:claude-md:init

> **Create CLAUDE.md from lean project-type template with auto-population.**

---

## Synopsis

```bash
/craft:docs:claude-md:init [options]
```

**Quick examples:**

```bash
# Auto-detect project type and generate CLAUDE.md
/craft:docs:claude-md:init

# Preview the generated template without creating the file
/craft:docs:claude-md:init --dry-run

# Overwrite an existing CLAUDE.md
/craft:docs:claude-md:init --force
```

---

## Description

Generates a new CLAUDE.md file tailored to your project type. The command detects whether your project is a craft plugin, teaching site, or R package, then populates a lean template with auto-discovered metadata such as version, command counts, and repository URL.

All generated files enforce a less-than-150-line budget using pointer architecture. Instead of embedding full details (release history, architecture docs), the template ends with a References section containing links to detail files that Claude can follow on demand.

This command follows the "Show Steps First" pattern — it always previews the generated content and asks for confirmation before creating the file. If a CLAUDE.md already exists, the command refuses unless `--force` is set.

---

## Options

| Option | Alias | Default | Description |
|--------|-------|---------|-------------|
| `--type` | | auto-detect | Template type: `plugin`, `teaching`, `r-package` |
| `--force` | `-f` | `false` | Overwrite existing CLAUDE.md (creates `.CLAUDE.md.backup` first) |
| `--dry-run` | `-n` | `false` | Preview template without creating file |
| `--global` | `-g` | `false` | Target `~/.claude/CLAUDE.md` instead of project |

---

## What It Does

1. **Detect** — Identifies project type from filesystem indicators (e.g., `.claude-plugin/plugin.json`, `_quarto.yml`, `DESCRIPTION`)
2. **Scan** — Gathers metadata from project files and git (version, counts, repo URL)
3. **Populate** — Fills lean template with discovered values, targeting less than 150 lines
4. **Preview** — Shows generated CLAUDE.md with line count and population percentage
5. **Confirm** — Waits for approval (`y`, `n`, `edit`, or `preview-full`)
6. **Create** — Writes the file and runs post-creation audit to validate

### Available Templates

| Type | Detection | Auto-populated Fields | Target Lines |
|------|-----------|----------------------|--------------|
| **plugin** | `.claude-plugin/plugin.json` | name, version, counts, repo_url | ~120 |
| **teaching** | `_quarto.yml` + `course.yml` | course info, weeks, assignments | ~100 |
| **r-package** | `DESCRIPTION` + `Package:` | package info, version, functions | ~110 |

If multiple project types are detected, the highest-confidence match is used. You can override with `--type`.

---

## See Also

- [claude-md command suite](../claude-md.md) — Hub page for all claude-md commands
- [/craft:docs:claude-md:edit](edit.md) — Interactive section editing
- [/craft:docs:claude-md:sync](sync.md) — Update, audit, fix, and optimize CLAUDE.md
