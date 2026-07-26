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

| Command file | Default | Category |
|---|---|---|
| `commands/do.md` | **ON** | Deliberation-entry (routes a task; refining sharpens what gets routed) |
| `commands/brainstorm.md` | **ON** | Deliberation-entry |
| `commands/plan.md` | **ON** | Deliberation-entry (universal planning router) |
| `commands/plan/feature.md` | **ON** | Deliberation-entry |
| `commands/grill.md` | **ON** (topic-scoped — skipped when the argument is a path, nothing to refine) | Deliberation-entry |
| `commands/orch.md` | **OFF** | Execution engine (task is already decided by the time it reaches here; refining would re-litigate a settled scope) |
| `commands/orch/workflow.md` | **OFF** | Execution engine |
| `commands/arch/plan.md` | **OFF** | Predates D6 (Conflict 1.1.1 didn't cover it) — kept OFF, not revisited here |
| `commands/smart-help.md` | **OFF** | Lookup/help, not deliberation — most `topic` args are a single keyword or short question |

**Rule of thumb for any future command:** if the command's job is *deciding what to
do*, default ON. If its job is *doing the already-decided thing*, default OFF. This
table is exhaustive over current `--refine` declarers — a dogfood test
(`tests/test_interactive_commands_dogfood.py`) asserts every command file that
declares the flag has a matching row here, so add a row in the same change that
adds a new caller.

## Inputs

- `prompt` — the raw argument the user typed.
- `context` — project type (DESCRIPTION / package.json / pyproject.toml),
  current git branch, and `.STATUS` current-task if present.

## Procedure (the canonical --refine flow — callers MUST delegate here)

1. **Read context** (read-only): detect project type, branch, `.STATUS`.
   - **Software project** (default): DESCRIPTION / package.json / pyproject.toml,
     current git branch, `.STATUS` current-task if present.
   - **Manuscript/research project** (parallel branch — detect by presence of
     `references.bib` alongside a `.qmd`/`.tex` main file, same pattern
     `/savant:restore` uses): additionally note whether the main file has a
     notation/symbol glossary table, whether `docs/reviews/` (or an equivalent
     existing-reports folder) has prior review docs on the same topic, and
     whether `.flow/research-config.yml` exists (journal/register context).
     Still read-only — a wider file set to check, not a different constraint.

2. **Skip-gate (terse action-verb prompts):** before rewriting, check the raw
   prompt against the `action-verb-execution` pattern — a single clear verb
   plus an already-scoped target, no compound clauses (e.g. "render the
   article", "commit and push"). If it matches, skip straight to step 5 and
   return the prompt unchanged — no rewrite, no before/after box, no confirm.
   This round-trip has zero information gain on prompts that are already
   unambiguous; it stays valuable (and still runs in full) for anything
   compound or ambiguous. When unsure whether a prompt qualifies, do NOT
   skip — fall through to the full procedure below.

3. **Rewrite** the prompt to add scope, specifics, and intent — without
   inventing requirements the user didn't imply.
4. **Show before/after** in a boxed display, THEN print the refined prompt
   in its own fenced, copy-paste-ready code block — two separate visible
   blocks, both emitted as response text:

   ```

   ╭─ --refine ─────────────────────────────────────╮
   │ Original:  RAW                                  │
   │ Refined:   REWRITTEN                            │
   │ Changed:   ONE-LINE WHAT CHANGED               │
   ╰─────────────────────────────────────────────────╯

   ```

   ```text
   REWRITTEN
   ```

   **Ordering constraint (fixes a confirmed bug — do not skip):** both blocks
   above MUST render as visible response text in this turn BEFORE the
   `AskUserQuestion` tool call in step 5 fires. Never collapse steps 4 and 5
   into a single tool-call-only turn with no interstitial text — that
   produces a confirm question with nothing shown first, which is exactly
   the failure this ordering constraint exists to prevent.

5. **Confirm** via AskUserQuestion, exactly these four options:

   | Option | Meaning |
   |---|---|
   | **Execute now** (Recommended when a clear action is implied) | Accept the rewrite AND act on it in this session (dispatch, run a command, apply as a rule). Falls back to just returning the text when no downstream action is implied — never force an artificial action. |
   | **Copy for elsewhere** | Accept the rewrite, take NO further action here — the refined prompt was for pasting into a different session/context. Short-circuits whatever called `--refine`: the caller's own downstream flow (e.g. brainstorm's depth/focus questions) must not start in this branch. |
   | **Edit first** | Present the refined text and take the user's edited version **inline** (no $EDITOR), then re-ask this same question with the edited version. |
   | **Skip** | Keep the original, unrefined text — proceed with it, not an abort. |

   With `--yes` or auto mode, skip the picker and auto-accept **Execute now**,
   printing `refined (auto-accepted)`. This is the `--yes` cascade: one flag
   both auto-accepts the prompt-refiner AND suppresses the caller's
   interactive loop — fully headless.
6. **Return** the chosen prompt string to the caller (empty/no-op return on
   **Copy for elsewhere**, since that branch takes no further action). The
   skip-gate in step 2 also returns here, with the original prompt unchanged.

## Constraints

- NEVER execute the prompt or call tools — rewrite text only.
- NEVER write files — context reads are read-only.
- NEVER touch secrets/tokens.

## Standalone use

Invoked with no downstream command, stop after step 4–5 (or after the step-2
skip-gate, if it fires) and print the
refined prompt — this preserves the deprecated `/refine` behavior.

## Optional: explain mode

If the user passes `--explain` or asks "why" after seeing the refined
prompt, add a one-line rationale per change under "Changed:" (e.g.
"directive > question — clearer instructions get better results").
Skip by default; only triggered on request to keep the standard flow lean.
