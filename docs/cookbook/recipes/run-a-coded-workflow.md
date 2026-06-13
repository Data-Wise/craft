# Recipe: Run a coded workflow

1. Write a `WORKFLOW-*.yaml` (or copy `examples/workflow-code-review/WORKFLOW-code-review-sweep.yaml`).
2. `/craft:orchestrate:workflow --dry-run`   # preview the wave plan, no agents spawned
3. Check the stages, fan-out (`xN` = runtime width), and run-wide ceiling.
4. `/craft:orchestrate:workflow`              # execute wave by wave, schema-gated
5. To re-run after editing one stage: `/craft:orchestrate:workflow --resume <run-id>` — only changed stages (and their downstream) re-run.

> **workflow vs drive vs orchestrate:** use `workflow` for a fixed coded shape
> (decompose → cover → verify → synthesize); use `/craft:orchestrate:drive` for a
> spec-anchored `/goal` loop; use `/craft:orchestrate` for free-form exploration.
