---
title: "Help: The --refine Flag"
description: "Sharpen a vague prompt before a command runs, with a before/after confirm step"
category: "help"
level: "beginner"
version: "2.34.0"
related:
  - ../tutorials/TUTORIAL-refine-flag.md
  - ../cookbook/recipes/refine-before-running.md
---

# Help: The `--refine` Flag

Turn a vague one-liner into a sharp, context-aware prompt before the command acts.

```text
/craft:do --refine "make the CLI faster"

  ┌─ Original ──────────────────────────────────────────┐
  │ make the CLI faster                                  │
  ├─ Refined ───────────────────────────────────────────┤
  │ Profile the craft CLI startup path and reduce        │
  │ cold-start latency; target the discovery cache and   │
  │ command load. Report before/after timings.           │
  └─────────────────────────────────────────────────────┘

  Accept (Recommended) / Edit / Use original?
```

## What `--refine` does

`--refine` is a thin pre-processor. Before the command runs, it hands your
argument to the **`prompt-refiner` skill**, which reads project context
(project type, current branch, `.STATUS`) and returns a tighter, more
actionable version of your prompt plus a short summary of what changed. You
then confirm, and the command proceeds on the prompt you chose.

## When to use it

Reach for `--refine` whenever your prompt is vague, terse, or missing the
context a command needs to do good work — e.g. `"add auth"`,
`"make it faster"`, `"clean up the docs"`. If your prompt is already specific,
skip the flag and run the command directly.

## The Accept / Edit / Use-original flow

After the before/after box appears you choose one of:

- **Accept** *(Recommended)* — run on the refined prompt.
- **Edit** — tweak the refined text inline, then run on your edited version.
- **Use original** — discard the refinement and run on your original argument.

## `--yes` / auto auto-accepts

There is exactly one no-confirm path: passing **`--yes`** (or running in an
**auto / unattended** context) **auto-accepts the refined prompt** and skips
the prompt entirely. Use it for scripted or hands-off runs where you trust the
refinement.

## Which commands support it

`--refine` is available on these five commands:

| Command | Purpose |
|---|---|
| `/craft:workflow:brainstorm` | Brainstorm on a refined topic |
| `/craft:do` | Route a refined task |
| `/craft:orchestrate` | Orchestrate a refined goal |
| `/craft:plan:feature` | Plan a refined feature |
| `/craft:arch:plan` | Architecture plan from a refined prompt |

## See also

- [Tutorial: The --refine Flag](../tutorials/TUTORIAL-refine-flag.md)
- [Recipe: Refine a prompt before running](../cookbook/recipes/refine-before-running.md)
