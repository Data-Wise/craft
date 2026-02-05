---
title: "Troubleshooting: Wrong Command Output"
description: "Fix commands that produce unexpected, incomplete, or incorrect output"
category: "cookbook"
level: "beginner"
time_estimate: "3 minutes"
related:
  - ../../commands/do.md
  - ../../commands/overview.md
---

# Troubleshooting: Wrong Command Output

**Level:** Beginner

## Problem

A Craft command runs without errors but produces unexpected output:

```
/craft:code:lint debug
🔍 Debug mode: verbose trace enabled
[... 200 lines of trace output ...]
✅ Lint complete (0 issues)
```

You expected a simple summary but got a wall of debug information.

## Common Causes & Solutions

### 1. Mode Mismatch

**Issue:** `debug` mode produces verbose traces; `default` mode suppresses detail.

```bash
/craft:code:lint            # Concise: shows only issues found
/craft:code:lint debug      # Verbose: every file, every rule
/craft:code:lint release    # Thorough: full analysis with performance data
```

**Why:** Each mode adjusts both analysis depth and output verbosity.

### 2. Wrong Command for the Task

**Issue:** You used a specific command when a different one was appropriate.

**Solution:** Use `/craft:do` for smart routing:

```bash
/craft:do "check code quality"        # Routes to code:lint
/craft:do "analyze project structure"  # Routes to arch:analyze
/craft:do "validate before commit"     # Routes to check
```

### 3. Outdated Cached Data

**Issue:** Output references stale counts or old metrics.

**Solution:**

```bash
./scripts/validate-counts.sh       # Refresh cached metrics
/craft:docs:claude-md:sync         # Sync CLAUDE.md metrics
```

### 4. Wrong Flags or Arguments

**Issue:** Flags change behavior unexpectedly.

```bash
/craft:docs:claude-md:sync --fix    # Applies auto-fixes
/craft:docs:claude-md:sync          # Audit-only, shows what would change
```

**Solution:** Use the "Show Steps First" pattern -- commands preview their plan before executing.

### 5. Project Context Not Detected

**Issue:** Output seems generic because project type was not auto-detected.

**Solution:** Ensure your project has a recognized marker: `DESCRIPTION` (R), `pyproject.toml` (Python), `package.json` (Node), `_quarto.yml` (Quarto), or `.claude-plugin/` (Craft plugin).

## Verification Steps

```bash
/craft:do "lint my code"         # Verify smart routing
./scripts/validate-counts.sh     # Validate metrics
/craft:check                     # Quick sanity check
```

## Related

- [Do Command](../../commands/do.md) — Smart routing with complexity scoring
- [Commands Overview](../../commands/overview.md) — All execution modes and flags
