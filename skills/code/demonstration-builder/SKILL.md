---
name: demonstration-builder
description: This skill should be used when the user asks to "create a demo", "build a code demonstration", "write a vignette", "generate tutorial code", "make live-coding examples", "demo this package", or wants runnable instructional code for teaching, presentations, vignettes, or documentation. Designs progressive code examples that build from simple to complex with explanations, expected outputs, and common variations.
---

# Demonstration Builder

Design runnable, instructional code demonstrations: vignettes, tutorials, conference live-coding, package examples, and teaching materials. Focused on pedagogy — what to show, in what order, with what scaffolding — not on test coverage or correctness validation (use `test-strategist` for that).

## When to Use

- "Create a demo of [topic] for [audience]"
- "Build a vignette showing [workflow]"
- "Generate tutorial code for a workshop"
- "Make a live-coding example with stopping points"
- Writing a package vignette, README example, or conference demo
- Producing runnable teaching material from a concept

## When NOT to Use

- **Test coverage / coverage analysis** → use `test-strategist` skill (covers "Coverage Analysis", coverage metric interpretation, untested code paths)
- **Test generation (dogfooding, CLI tests)** → use `test-generator` skill
- **API/library docs reference** → use the `docs/` skills
- **Slides for a lecture** → use `scholar:teaching:slides`

## Required Input

Before drafting, confirm or infer:

| Field | Examples |
|---|---|
| **Topic** | "Linear regression", "mediation analysis", "ggplot2 themes" |
| **Audience** | Beginner / intermediate / expert |
| **Format** | Vignette · standalone script · live-coding · README example |
| **Length** | Quick (~10 lines) · tutorial (multi-section) · vignette (publication) |
| **Runtime** | What language/env (R, Python, shell)? Any MCP tools available? |

If any are missing and the answer affects scope, ask once and proceed.

## Design Process

1. **Scope** — list 2-5 concepts in dependency order. Cut anything not load-bearing for the audience's level.
2. **Flow** — simple → complex. Each step produces a visible intermediate output the reader can compare against their own run.
3. **Code** — readable over clever. All `library()` / `import` calls explicit. Set seeds for any randomness.
4. **Narration** — explain *before* each code block (what + why), interpret *after* the output (so what).
5. **Variations** — show 1-2 "what if" branches at the end of major sections; flag common pitfalls.
6. **Next steps** — link to deeper docs, related functions, or follow-on demos.

## Output Template

```markdown
# Demo: <Topic>

## Overview
<What this demo covers and why it matters>

## Prerequisites
- <Packages / tools>
- <Assumed background>

## Setup
<library calls + sample data>

## Part 1: <First concept>
<explanation>
<code>
<expected output as comment>
<interpretation>

## Part 2: <Next concept>
...

## Common Variations
### Variation A
### Variation B

## Troubleshooting
**Issue:** ...  **Fix:** ...

## Next Steps
- <Links / related demos>
```

## Demo Types

| Type | Length | Use for |
|---|---|---|
| **Quick example** | ~10 lines, one concept | README, doc page snippet |
| **Tutorial** | Multi-section, full workflow | Blog post, workshop handout |
| **Vignette** | Publication quality, real use case | Package vignette, paper supplement |
| **Live-coding** | Clear stopping points, audience-interaction notes | Talks, classroom |

## Pedagogy Checklist

- [ ] Starts with simplest working example
- [ ] Each code block ≤ ~15 lines (chunkable on a slide / in a head)
- [ ] Expected output shown inline (as comment or printed)
- [ ] Seeds set; reproducible
- [ ] Includes at least one "what if" variation
- [ ] Notes one common pitfall
- [ ] Ends with concrete next step

## MCP Integration (when present)

For R demos, prefer running snippets through `r_execute` / `r_plot` to verify they work and capture real output before pasting expected results. Don't fabricate output — run it.

## Integration

- `test-strategist` — for coverage analysis (NOT this skill's concern)
- `scholar:teaching:slides` — for slide decks (this skill produces the code, not the slides)
- `/craft:docs:demo` — terminal recording / GIF generation for finished demos
