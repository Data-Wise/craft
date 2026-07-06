---
title: "Tutorial: Generate Docs with /craft:docs:generate"
description: "Use the unified router to reach any of the 9 documentation generators by name"
category: "tutorial"
level: "beginner"
time_estimate: "5 minutes"
version: "2.59.0"
related:
  - ../commands/docs/generate.md
---

# Tutorial: Generate Docs with `/craft:docs:generate`

**Level:** Beginner
**Time:** 5 minutes
**Prerequisites:** None
**Version:** 2.59.0+

## What You'll Learn

1. How `/craft:docs:generate <type>` reaches any of the 9 doc generators
2. When to use the router vs. the direct command

## Overview

Craft ships 9 separate documentation generators (`api`, `guide`, `help`,
`prompt`, `quickstart`, `site`, `tutorial`, `website`, `workflow`) — each with
genuinely distinct logic, so none of them were merged. `/craft:docs:generate`
exists purely for discoverability: one name to remember, dispatching to the
canonical command underneath.

## Step 1: Pick a generator by name

```text
/craft:docs:generate quickstart
```

This validates `type` against the 9 known generators and then runs
`/craft:docs:quickstart` exactly as if you'd typed it directly — no behavior
difference, no reimplementation.

## Step 2: Or just call the direct command

```text
/craft:docs:quickstart
```

Both forms are equivalent and permanently supported side by side. Use the
router when you don't remember the exact generator name; use the direct form
when you already know it.

## Step 3: Handle an invalid type

```text
/craft:docs:generate nonsense
```

Shows the list of 9 valid types and stops — no partial execution.

## Common Issues

| Symptom | Cause | Fix |
|---|---|---|
| "Which generator to run" list printed | `type` missing or unrecognized | Pass one of the 9 valid names |

## See Also

- [`/craft:docs:generate`](../commands/docs/generate.md) — command reference
- Direct generators: `/craft:docs:api`, `/craft:docs:guide`, `/craft:docs:help`, `/craft:docs:prompt`, `/craft:docs:quickstart`, `/craft:docs:site`, `/craft:docs:tutorial`, `/craft:docs:website`, `/craft:docs:workflow`
