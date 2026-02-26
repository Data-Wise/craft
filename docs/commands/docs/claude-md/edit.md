# /craft:docs:claude-md:edit

> **Interactive section-by-section CLAUDE.md editing with preview.**

---

## Synopsis

```bash
/craft:docs:claude-md:edit [options]
```

**Quick examples:**

```bash
# Open CLAUDE.md for interactive section editing
/craft:docs:claude-md:edit

# Edit a specific section directly
/craft:docs:claude-md:edit --section "testing"

# Edit with optimization suggestions after saving
/craft:docs:claude-md:edit --optimize
```

---

## Description

Opens CLAUDE.md in an external editor with section-by-section navigation, TODO optimization hints, and post-edit validation. The command parses the document structure, lets you choose which section to edit, and previews changes before applying them.

Before opening the file, the command inserts HTML comment hints showing optimization guidance (e.g., which sections are over budget). After you finish editing, it strips those comments, runs a validation audit, and reports the results including line budget status.

This command follows the "Show Steps First" pattern — it always shows available sections and lets you choose what to edit before opening the editor.

---

## Options

| Option | Alias | Default | Description |
|--------|-------|---------|-------------|
| `--section` | | auto-detect | Specific section to edit (skips selection menu) |
| `--editor` | `-e` | `ia` | Editor to use: `ia`, `code`, `sublime`, `cursor` |
| `--optimize` | `-o` | `false` | Have Claude suggest optimizations after editing |
| `--hints` | | `true` | Add TODO optimization comments before opening |
| `--no-hints` | | `false` | Open without annotations |
| `--global` | `-g` | `false` | Target `~/.claude/CLAUDE.md` instead of project |
| `--validate` | | `true` | Run audit after edit completes |
| `--no-validate` | | `false` | Skip post-edit validation |

---

## How It Works

1. **Parse** — Reads CLAUDE.md and detects sections by top-level headers and horizontal rules
2. **Show sections** — Displays numbered list of detected sections with line counts
3. **Select** — You choose a section number, `all` for sequential editing, or `cancel`
4. **Annotate** — Inserts TODO hint comments unless `--no-hints` is set
5. **Open** — Launches the file in your editor via AppleScript
6. **Wait** — Prompts "Type 'done' when finished editing"
7. **Clean up** — Strips all TODO comments from the file
8. **Validate** — Runs 5-check audit with budget status (unless `--no-validate`)
9. **Preview** — Shows before/after diff with line count changes
10. **Apply** — Writes changes after your confirmation

The original file is backed up to `.CLAUDE.md.bak` before any changes are applied.

---

## See Also

- [claude-md command suite](../claude-md.md) — Hub page for all claude-md commands
- [/craft:docs:claude-md:init](init.md) — Create new CLAUDE.md from template
- [/craft:docs:claude-md:sync](sync.md) — Update, audit, fix, and optimize CLAUDE.md
