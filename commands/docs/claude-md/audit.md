---
description: "DEPRECATED: Use /craft:docs:claude-md:sync instead"
arguments: []
---

# DEPRECATED: /craft:docs:claude-md:audit

> **This command has been replaced by `/craft:docs:claude-md:sync`** in v2.12.0.
> It will be removed in v2.13.0.

## What Changed

| Old Command | New Command | Notes |
|-------------|-------------|-------|
| `/craft:docs:claude-md:audit` | `/craft:docs:claude-md:sync` | Now part of 4-phase sync pipeline (detect, update, audit, fix) |

## Automatic Forwarding

This command now forwards to `/craft:docs:claude-md:sync`.

**Action:** Execute `/craft:docs:claude-md:sync` with all arguments passed through.
