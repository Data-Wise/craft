# Tutorial: code:desktop-watch — Track Claude Desktop Releases

By the end of this tutorial you will have:

- Checked for new Claude Desktop releases
- Reviewed plugin integration opportunities surfaced from the release notes
- Formatted the output for different consumption needs

**Prerequisites:** craft installed, internet access.

---

## Step 1: Check for New Releases

```
/craft:code:desktop-watch
```

Fetches the latest Claude Desktop release information and analyzes it for plugin-relevant changes:

```
Claude Desktop Release Watch
─────────────────────────────
Latest:   Claude Desktop 0.7.3 (released 2026-06-15)
Previous: Claude Desktop 0.7.2

New in 0.7.3:
  🔌 Plugin API changes:
    • New hook: PostToolUse — fired after every tool completion
    • Expanded settings.json schema: 'autoMode.hard_deny' now accepts wildcards
    • Deprecated: 'hooks.PreToolUse[].timeout' — use 'timeoutMs' instead

  🎯 Plugin integration opportunities:
    • PostToolUse hook enables response-time measurement per tool
    • Wildcard deny patterns simplify security policy configuration

No breaking changes detected for craft plugin.
```

---

## Step 2: Choose Output Format

```
/craft:code:desktop-watch --format brief    # One-line summary
/craft:code:desktop-watch --format full     # All release notes
/craft:code:desktop-watch --format json     # Machine-readable
```

---

## Step 3: Use in a Release Workflow

Run before releasing a new craft version to ensure compatibility:

```
/craft:code:desktop-watch --format brief
```

If breaking changes are detected, address them before cutting the release.

---

## What's Next

- Pair with `/craft:code:release-watch` to monitor both Claude Code and Desktop
- If new hooks are available, use `/craft:orchestrate` to prototype integration
- Track changes in `CHANGELOG.md` for your plugin's compatibility notes
