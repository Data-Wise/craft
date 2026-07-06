---
title: "Tutorial: Plan a Feature with /craft:plan:feature"
description: "Turn a one-line feature idea into a structured task breakdown with estimates, dependencies, and acceptance criteria"
category: "tutorial"
level: "beginner"
time_estimate: "10 minutes"
version: "2.59.0"
related:
  - ../commands/plan/feature.md
---

# Tutorial: Plan a Feature with `/craft:plan:feature`

**Level:** Beginner
**Time:** 10 minutes
**Prerequisites:** None
**Version:** 2.59.0+

## What You'll Learn

1. How to turn a short feature description into a full plan
2. How to scope the output (MVP vs. full vs. enterprise)
3. How to export the plan as markdown, Jira, or a GitHub issue

## Step 1: Describe the feature

```bash
/craft:plan:feature "user profile page with avatar upload"
```

By default this runs the `prompt-refiner` skill first to sharpen a vague
description — accept, edit, or use the original before planning proceeds.
Pass `--no-refine` to skip that step.

## Step 2: Read the plan

The output breaks the feature into:

- **User Stories** — who/what/why
- **Tasks** — grouped by layer (backend/frontend/infra), each with a time estimate
- **Dependencies** — what has to exist first
- **Risks** — things likely to bite you
- **Acceptance Criteria** — how you'll know it's done

## Step 3: Narrow the scope

```bash
/craft:plan:feature "search functionality" --scope mvp
```

`--scope` accepts `mvp`, `full`, or `enterprise` — controls how much detail
and how many edge cases the breakdown covers.

## Step 4: Export it

```bash
/craft:plan:feature "notifications" --format github
```

`--format` accepts `markdown` (default), `jira`, or `github` — the last one
produces text ready to paste into a new GitHub issue.

## Common Issues

| Symptom | Cause | Fix |
|---|---|---|
| Plan feels generic | Description too vague | Let the default `--refine` step sharpen it, or add more context up front |
| Missing a section you expected | `--include-tests` not passed | Add `--include-tests` for explicit test planning |

## See Also

- [`/craft:plan:feature`](../commands/plan/feature.md) — command reference
- `/craft:plan:sprint` — sprint planning
- `/craft:arch:plan` — architecture planning
