# /craft:code:demo

> **Create working code demonstrations and examples**

---

## Synopsis

```bash
/craft:code:demo
```

**Quick examples:**

```bash
# Beginner-friendly demo of a technique
/craft:code:demo "linear regression in R for beginners"

# Full workflow vignette
/craft:code:demo "mediation analysis workflow"

# Presentation-format live-coding examples
/craft:code:demo "live-coding examples for a dplyr workshop"
```

---

## Description

Generates working code demonstrations for package vignettes, tutorial
materials, conference presentations, documentation examples, and teaching
code. Builds from a simple working example toward full complexity, showing
intermediate outputs and common variations along the way.

---

## Required Input

| Input     | Description                                     |
|-----------|--------------------------------------------------|
| Topic     | What to demonstrate                              |
| Audience  | Beginners, intermediate, experts                 |
| Format    | Vignette, slides, standalone script              |
| Length    | Brief example or comprehensive tutorial          |

---

## Demo Types

| Type          | Shape                                              |
|---------------|-----------------------------------------------------|
| Quick Example | Single concept, ~10 lines, immediate output          |
| Tutorial      | Multiple concepts, step-by-step, full workflow       |
| Vignette      | Comprehensive, real-world use case, publication quality |
| Live Coding   | Presentation format, clear stopping points, audience interaction notes |

---

## Process

1. **Define scope** — concepts to cover, assumed prerequisites, learning objectives
2. **Design flow** — simple to complex, intermediate outputs, common variations
3. **Write code** — clear style, helpful comments, runnable examples
4. **Add context** — explain the "why", note pitfalls, suggest next steps

---

## MCP Integration

Uses these tools when available:

- `r_execute` — run and verify code
- `r_plot` — generate visualizations
- `r_preview` — preview output

---

## Best Practices

- Set seeds for random operations; include data-creation code; note package versions
- Explain before code blocks, interpret after outputs, connect to real-world use
- Start with the simplest working example, then build complexity gradually
- Show both success and error cases

---

## See Also

- [/folio:docs:tutorial](https://github.com/Data-Wise/folio) — long-form tutorial authoring (moved to `folio`)
