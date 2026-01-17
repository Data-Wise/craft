---
title: "Troubleshooting: Command Not Found"
description: "Fix 'command not found' errors when running Craft commands"
category: "cookbook"
level: "beginner"
time_estimate: "2 minutes"
related:
  - ../../guide/getting-started.md
  - ../../ADHD-QUICK-START.md
---

# Troubleshooting: Command Not Found

**Level:** Beginner

## Problem

You're trying to run a Craft command but getting an error:

```
/craft:do check
-bash: /craft:do: No such file or directory
```

or

```
craft:check: command not found
```

## Common Causes & Solutions

### 1. Wrong Command Format

**Issue:** Using shell syntax instead of Claude Code slash command syntax

**Wrong:**
```bash
craft:check          # Shell format (won't work)
/craft:check         # Missing colon separator
craft check          # Missing prefix
```

**Correct:**
```bash
/craft:check         # Claude Code slash command format
/craft:do check      # Smart routing alternative
```

**Why:** Craft commands are Claude Code slash commands, not shell commands. They must start with `/craft:` when invoked in Claude Code.

### 2. Running in Wrong Environment

**Issue:** Trying to run Craft commands in a terminal instead of Claude Code

**Solution:** Craft commands only work inside Claude Code conversations:
1. Open Claude Code application
2. Navigate to your project directory
3. Start a conversation
4. Run `/craft:check` or other commands

**Why:** Craft is a Claude Code plugin that extends Claude's capabilities. It doesn't install shell commands.

### 3. Plugin Not Loaded

**Issue:** Craft plugin hasn't been loaded in the current session

**Solution:**
1. Check if plugin is installed: Look for `.claude-plugin/` directory in your Craft repository
2. Restart Claude Code application
3. Verify plugin location: `~/.claude/` or project-specific location
4. Check plugin settings in `~/.claude/settings.json`

**Why:** Claude Code loads plugins at startup from configured locations.

### 4. Typo in Command Name

**Issue:** Misspelling the command name

**Common typos:**
- `/craft:checks` → `/craft:check` (extra 's')
- `/craft:do-check` → `/craft:do check` (hyphen vs space)
- `/craft:git-init` → `/craft:git:init` (hyphen vs colon)

**Solution:** Use tab completion or check [Commands Reference](../../commands/index.md) for exact command names

### 5. Command Doesn't Exist

**Issue:** Trying to use a command that hasn't been created yet

**Solution:**
1. Check the [Commands Index](../../commands/index.md) for available commands
2. Use `/craft:do <task>` for smart routing (it will suggest correct commands)
3. Check if you need to update to a newer version of Craft

**Example:**
```bash
# Instead of guessing command names
/craft:validate-links  # Might not exist

# Use smart routing
/craft:do validate links  # Routes to correct command
```

## Verification Steps

### Check Plugin Installation
```bash
# In Claude Code conversation
/craft:help
```

If this works, the plugin is installed correctly.

### Check Available Commands
```bash
# In Claude Code conversation
/hub
```

This shows all available commands across all plugins.

### Test Basic Command
```bash
# In Claude Code conversation
/craft:check
```

If this works, Craft is fully functional.

## Still Having Issues?

### Reset Plugin Cache

Sometimes Claude Code's plugin cache gets stale:

1. Exit Claude Code application
2. Clear plugin cache (if you know where it's stored)
3. Restart Claude Code
4. Try command again

### Check Version Compatibility

Ensure you're using a compatible version:

- Claude Code version: Check in Help → About
- Craft version: Check in `CHANGELOG.md` or git tags
- Required features: Some commands require specific Claude Code versions

### Ask for Help

If the issue persists:

1. Check [GitHub Issues](https://github.com/Data-Wise/craft/issues)
2. Search for similar problems
3. Create a new issue with:
   - Exact command you tried
   - Full error message
   - Claude Code version
   - Operating system

## Quick Reference

| Environment | How to Run Craft |
|-------------|-----------------|
| Claude Code | `/craft:check` (slash command) |
| Terminal | Not available (plugin only) |
| Claude Desktop | `/craft:check` (if plugin installed) |
| claude.ai web | Not available (requires Claude Code) |

## Related

- [Getting Started Guide](../../guide/getting-started.md) — Complete setup instructions
- [ADHD Quick Start](../../ADHD-QUICK-START.md) — 30-second quick start
- [Commands Index](../../commands/index.md) — Full command reference
- [Do Command](../../commands/do.md) — Smart routing for finding commands
