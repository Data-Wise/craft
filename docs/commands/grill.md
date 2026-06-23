# /craft:grill

> **Adversarially interrogate a plan, spec, or topic one question at a time — the convergent counterpart to brainstorm.**

---

## Synopsis

```bash
/craft:grill [target] [--bound N] [--no-capture]
```

**Quick examples:**

```bash
# Stress-test an existing spec before building
/craft:grill docs/specs/SPEC-auth-2026-06-22.md

# Grill a bare topic (sketches a skeleton, then interrogates it)
/craft:grill "add OAuth login"

# Detect the target from context (.STATUS / branch / recent work)
/craft:grill
```

## What it does

`brainstorm` is **divergent** — it generates options and expands the space. `grill` is
**convergent** — it interrogates a position to surface gaps, contradictions, and unresolved
dependencies *before* you implement.

1. **Resolve the target** — a spec/plan path, a quoted topic (skeleton-then-grill), or empty (detect from context).
2. **Codebase-first sweep** — reads repo evidence (`.STATUS`, git, specs, command tree) and pre-answers every branch it can; each pre-answer becomes the **Recommended:** line you can override.
3. **Grill loop** — one question at a time, walking the design tree, dependencies first, a recommended answer on every question. Enter `/done` to halt; `--bound N` stops after N branches.
4. **Capture** — writes a durable decision-ledger `GRILL-<topic>-<date>.md` in `docs/specs/` (never overwrites a brainstorm `SPEC-*`; adds an idempotent cross-link). `--no-capture` returns decisions inline without a file (used by embedded callers).
5. **Handoff** — offers `/craft:plan` → `ORCHESTRATE` → `/craft:do`.

## Arguments

| Argument | Description |
|----------|-------------|
| `target` | Spec/plan path, a quoted topic, or empty to detect from context |
| `--bound N` | Limit interrogation to N decision branches (used by `/craft:orchestrate` Step 0.5) |
| `--no-capture` | Skip writing a `GRILL-*` file; return decisions inline (embedded callers) |

## When to use grill vs brainstorm

| You want to… | Use |
|--------------|-----|
| Generate ideas, options, MVP scope | `/craft:workflow:brainstorm` (divergent) |
| Stress-test a plan/spec for gaps before building | `/craft:grill` (convergent) |

## See also

- [`/craft:workflow:brainstorm`](../commands.md) — generate before you interrogate
- [`/craft:orchestrate`](orchestrate.md) — its Step 0.5 Clarify invokes a bounded grill
- [Grill Tutorial](../tutorials/TUTORIAL-grill.md)
