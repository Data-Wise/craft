---
name: hooks
description: Common PostToolUse/PreToolUse hook templates for quality gates. Provides ready-to-install JSON blocks for MkDocs strict mode, linting, and other automated checks, with setup instructions for each.
---

# Hook Templates

Copy any block below into `.claude/settings.json` under the `hooks` key (merge, don't replace).

## MkDocs --strict hook

Catches broken internal links and Jinja template errors on every Edit/Write to a docs file.
Surfaces CI failures locally before `gh-deploy`.

**Install:** merge into `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "[ -f mkdocs.yml ] && mkdocs build --strict 2>&1 | tail -8 || true"
          }
        ]
      }
    ]
  }
}
```

**Guard:** `[ -f mkdocs.yml ]` makes this a no-op in non-MkDocs repos — safe to install globally.

**What it catches:**

- Broken `[text][ref]` links and undefined `[ref]:` entries
- Jinja2 template errors in `mkdocs.yml` or `overrides/`
- Missing nav pages (paths in `mkdocs.yml` that don't exist on disk)

**Cost:** `mkdocs build --strict` takes ~2–5s for a medium site. Fires only on file writes, not reads.

## How to add custom hooks

1. Choose trigger: `PreToolUse` (before) or `PostToolUse` (after)
2. Set `matcher` to the tool names that should trigger (pipe-separated regex: `"Edit|Write"`)
3. Write a shell `command` that exits 0 to allow, non-zero to block (PreToolUse) or flag (PostToolUse)
4. Merge the JSON block into `.claude/settings.json` — don't replace existing hooks

**Reference:** [Claude Code hooks documentation](https://docs.anthropic.com/en/docs/claude-code/hooks)
