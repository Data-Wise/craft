---
name: prompt-refiner
description: This skill should be used when a command's --refine flag is set, or the user asks to "refine my prompt", "optimize this prompt", "make this request sharper" — rewrites a vague natural-language request into a specific, well-structured prompt using project context, shows before/after, and confirms before the caller proceeds. Replaces the deprecated /craft:refine command.
---

# Prompt Refiner

> **Note:** Chat (claude.ai) may have a differently-scoped skill also named
> `prompt-refiner` — general-purpose prompt improvement, not craft's `--refine`
> flag plumbing. Unconfirmed from this repo; if cross-referencing
> "prompt-refiner" in docs or conversation, specify which one is meant.

Rewrites a raw user request into a sharper prompt, then confirms. Called
by the `--refine` flag on brainstorm / do / orchestrate / plan:feature /
arch:plan, or standalone ("refine and print").

## Default Policy (D6, 2026-07-04)

`--refine`'s default is **ON for deliberation-entry commands, OFF for execution
engines** — stated once here; callers reference this section instead of each
re-explaining the same on/off choice independently.

| Command | Default | Category |
|---|---|---|
| `do` | **ON** | Deliberation-entry (routes a task; refining sharpens what gets routed) |
| `workflow:brainstorm` | **ON** | Deliberation-entry |
| `plan:feature` | **ON** | Deliberation-entry |
| `grill` | **ON** (topic-scoped — skipped when the argument is a path, nothing to refine) | Deliberation-entry |
| `orchestrate` | **OFF** | Execution engine (task is already decided by the time it reaches here; refining would re-litigate a settled scope) |
| `orchestrate:workflow` | **OFF** | Execution engine |

**Rule of thumb for any future command:** if the command's job is *deciding what to
do*, default ON. If its job is *doing the already-decided thing*, default OFF.
`arch:plan` currently defaults OFF and predates this policy — it wasn't part of the
D6 conflict finding (Conflict 1.1.1) and isn't renamed here; revisit separately if it
turns out to need one.

## Inputs

- `prompt` — the raw argument the user typed.
- `context` — project type (DESCRIPTION / package.json / pyproject.toml),
  current git branch, and `.STATUS` current-task if present.

## Procedure (the canonical --refine flow — callers MUST delegate here)

1. **Read context** (read-only): detect project type, branch, `.STATUS`.
2. **Rewrite** the prompt to add scope, specifics, and intent — without
   inventing requirements the user didn't imply.
3. **Show before/after** in a boxed display:

   ```

   ╭─ --refine ─────────────────────────────────────╮
   │ Original:  RAW                                  │
   │ Refined:   REWRITTEN                            │
   │ Changed:   ONE-LINE WHAT CHANGED               │
   ╰─────────────────────────────────────────────────╯

   ```

4. **Confirm** via AskUserQuestion — Accept (Recommended) / Edit /
   Use original. On **Edit**, present the refined text and take the
   user's edited version **inline** (no $EDITOR). With `--yes` or auto
   mode, skip the picker and auto-accept, printing
   `refined (auto-accepted)`. This is the `--yes` cascade: one flag
   both auto-accepts the prompt-refiner AND suppresses the caller's
   interactive loop — fully headless.
5. **Return** the chosen prompt string to the caller.

## Constraints

- NEVER execute the prompt or call tools — rewrite text only.
- NEVER write files — context reads are read-only.
- NEVER touch secrets/tokens.

## Standalone use

Invoked with no downstream command, stop after step 3–4 and print the
refined prompt — this preserves the deprecated `/refine` behavior.

## Optional: explain mode

If the user passes `--explain` or asks "why" after seeing the refined
prompt, add a one-line rationale per change under "Changed:" (e.g.
"directive > question — clearer instructions get better results").
Skip by default; only triggered on request to keep the standard flow lean.
