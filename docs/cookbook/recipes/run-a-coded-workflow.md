# Recipe: Run a coded workflow

1. Write a `WORKFLOW-*.yaml` (or copy `examples/workflow-code-review/WORKFLOW-code-review-sweep.yaml`).
2. `/craft:orch:workflow --dry-run`   # preview the wave plan, no agents spawned
3. Check the stages, fan-out (`xN` = runtime width), and run-wide ceiling.
4. `/craft:orch:workflow`              # execute wave by wave, schema-gated
5. To re-run after editing one stage: `/craft:orch:workflow --resume <run-id>` — only changed stages (and their downstream) re-run.

> **workflow vs drive vs orchestrate:** use `workflow` for a fixed coded shape
> (decompose → cover → verify → synthesize); use `/craft:orch:drive` for a
> spec-anchored `/goal` loop; use `/craft:orch` for free-form exploration.
