---
description: Adversarially interrogate a plan, spec, or topic one question at a time — convergent counterpart to brainstorm
arguments:
  - name: target
    description: "Spec/plan path, a topic in quotes, or empty to detect from context"
    required: false
  - name: bound
    description: "Limit interrogation to N decision branches (used by orchestrate Step 0.5 for a quick gate)"
    required: false
    default: null
  - name: no-capture
    description: "Skip writing a GRILL spec file; return decisions inline (used by embedded callers like orchestrate Step 0.5)"
    required: false
    default: false
---

# /craft:grill — Interrogate Before Building

Convergent counterpart to `/craft:workflow:brainstorm`. brainstorm is **divergent** — it
GENERATES options and expands the space. grill is **convergent** — it INTERROGATES a position
to find gaps, contradictions, and unresolved dependencies before you implement.

Use grill to stress-test a spec/plan (or a bare topic) until every branch of the design tree is
resolved, then capture the locked decisions as a durable ledger that feeds `/craft:plan` → `/do`.

<!-- contract body (Steps 1–5) added in Wave 2 (Tasks 4–5) -->
