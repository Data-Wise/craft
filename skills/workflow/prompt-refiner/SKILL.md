---
name: prompt-refiner
description: This skill should be used when a command's --refine flag is set, or the user asks to "refine my prompt", "optimize this prompt", "make this request sharper" — rewrites a vague natural-language request into a specific, well-structured prompt using project context, shows before/after, and confirms before the caller proceeds. Replaces the deprecated /craft:workflow:refine command.
---

# Prompt Refiner

Rewrites a raw user request into a sharper prompt, then confirms. Called
by the `--refine` flag on brainstorm / do / orchestrate / plan:feature /
arch:plan, or standalone ("refine and print").

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
   `refined (auto-accepted)`.
5. **Return** the chosen prompt string to the caller.

## Constraints

- NEVER execute the prompt or call tools — rewrite text only.
- NEVER write files — context reads are read-only.
- NEVER touch secrets/tokens.

## Standalone use

Invoked with no downstream command, stop after step 3–4 and print the
refined prompt — this preserves the deprecated `/refine` behavior.
