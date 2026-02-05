---
description: "DEPRECATED: Use /craft:docs:claude-md:sync --fix instead"
arguments: []
---

# DEPRECATED: /craft:docs:claude-md:fix

> **This command has been replaced by `/craft:docs:claude-md:sync --fix`** in v2.12.0.
> It will be removed in v2.13.0.

## What Changed

| Old Command | New Command | Notes |
|-------------|-------------|-------|
| `/craft:docs:claude-md:fix` | `/craft:docs:claude-md:sync --fix` | Use `sync --fix` for same behavior, `sync --optimize` for budget enforcement |

## Automatic Forwarding

This command now forwards to `/craft:docs:claude-md:sync --fix`.

**Action:** Execute `/craft:docs:claude-md:sync` with `--fix` flag automatically added, plus all other arguments passed through.
