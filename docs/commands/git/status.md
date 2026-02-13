# /craft:git:status

> **Enhanced git status with teaching mode awareness**

---

## Synopsis

```bash
/craft:git:status [options]
```

**Quick examples:**

```bash
# Show enhanced status
/craft:git:status

# Verbose output with additional details
/craft:git:status --verbose

# Compact output for quick checks
/craft:git:status --compact
```

---

## Description

Provides an enhanced view of your repository's status with intelligent highlighting of critical files. In teaching mode, automatically highlights course-critical files like syllabi, schedules, and assignments.

This command wraps `git status` with additional context, making it easier to understand the state of your repository at a glance and avoid accidentally committing sensitive or auto-generated files.

---

## Options

| Option        | Description                              | Default |
|---------------|------------------------------------------|---------|
| `--verbose`   | Show additional details and file diffs   | `false` |
| `-v`          | Alias for `--verbose`                    | `false` |
| `--compact`   | Minimal output for quick checks          | `false` |
| `-c`          | Alias for `--compact`                    | `false` |

---

## Teaching Mode Features

When in a teaching repository (detected via `.flow/teach-config.yml`):

- Highlights critical files (syllabus, schedule, assignments)
- Warns about uncommitted changes to published content
- Shows semester progress context
- Flags draft vs. published content states

---

## Output Sections

1. **Branch Information** — Current branch and tracking status
2. **Branch Guard Status** — Protection level, session confirms, one-shot marker
3. **Staged Changes** — Files ready to commit
4. **Unstaged Changes** — Modified but not staged
5. **Untracked Files** — New files not in git
6. **Critical File Alerts** — Teaching-specific warnings (if applicable)

---

## Branch Guard Indicator

When the branch guard hook is installed, status shows protection information:

```text
│ Guard: smart (3 confirms) · one-shot: inactive  │
```

| Field | Meaning |
|-------|---------|
| `smart` | Current protection level (or `block-all`, `bypassed`, `none`) |
| `3 confirms` | Number of MEDIUM-risk confirmations this session |
| `one-shot: active` | A one-shot approval marker exists (next action will be allowed) |
| `one-shot: inactive` | No pending one-shot marker |

**On feature branches:**

```text
│ Guard: none (feature branch — unrestricted)      │
```

**When bypassed:**

```text
│ Guard: BYPASSED (reason: maintenance)             │
```

---

## Critical File Detection

Automatically highlights:

- `.env`, `.env.*` — Environment variables (never commit)
- `**/secrets/*` — Sensitive data directories
- Teaching files (teaching mode only):
  - `syllabus.md` or `syllabus.qmd`
  - `schedule.md` or `schedule.qmd`
  - `assignments/*.md`

---

## Exit Codes

| Code | Meaning                              |
|------|--------------------------------------|
| 0    | Status displayed successfully        |
| 1    | Not a git repository                 |
| 2    | Repository in invalid state          |

---

## See Also

- [/craft:git:sync](sync.md) — Smart git synchronization
- [/craft:git:branch](branch.md) — Branch management
- [/craft:git:protect](protect.md) — Branch protection management
- [/craft:git:unprotect](unprotect.md) — Temporary bypass
- [/craft:git:clean](clean.md) — Remove merged branches
- [Smart Mode Guide](../../guide/branch-guard-smart-mode.md) — Full guard documentation
- [Teaching Workflow Guide](../../guide/teaching-workflow.md) — Teaching mode details
