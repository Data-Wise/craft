# Tutorial: code:release-watch — Track Claude Code Releases

By the end of this tutorial you will have:

- Fetched recent Claude Code releases and identified plugin-relevant changes
- Filtered by product and time range
- Used the output to plan your next plugin update

**Prerequisites:** craft installed, internet access.

---

## Step 1: Check Recent Releases

```
/craft:code:release-watch
```

Fetches recent releases from Claude Code and Claude Desktop and surfaces plugin-relevant changes:

```
Release Watch — Claude Code + Desktop
───────────────────────────────────────
Last 5 releases checked.

Claude Code 1.0.45 (2026-06-18):
  🔌 Plugin-relevant:
    • New tool: WebFetch — available to all plugins
    • AskUserQuestion now supports 'preview' field on options
    • settings.json 'autoMode' key expanded (4 new subkeys)

Claude Code 1.0.44 (2026-06-14):
  ℹ️  No plugin API changes detected

Claude Desktop 0.7.3 (2026-06-15):
  🔌 Plugin-relevant:
    • PostToolUse hook now available
    • Deprecated: hooks.PreToolUse[].timeout → use timeoutMs

Action items for craft:
  ⭐ Add AskUserQuestion preview support to interactive commands
  ⭐ Migrate timeout → timeoutMs in branch-guard hook registration
```

---

## Step 2: Limit to Recent Releases

```
/craft:code:release-watch --count 3
/craft:code:release-watch --since 2026-06-01
```

---

## Step 3: Filter by Product

```
/craft:code:release-watch --product claude-code
/craft:code:release-watch --product claude-desktop
```

---

## Step 4: Choose Output Format

```
/craft:code:release-watch --format brief   # One line per release
/craft:code:release-watch --format full    # Full release notes
/craft:code:release-watch --format json    # Machine-readable
```

---

## What's Next

- Pair with `/craft:code:desktop-watch` for Desktop-only monitoring
- Use action items to create issues or feature branches for plugin updates
- Run before every `/release` to check for compatibility changes since the last craft version
