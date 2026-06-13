# Recipe: Fan a workflow across changed files

A common fixed shape: **list the changed files → run one agent per file → gate
each result → summarize**. Code it once, replay it on every branch.

```yaml
# WORKFLOW-audit-changed.yaml
stages:
  - id: list
    type: agent
    role: code-explorer
    output_schema: { files: "string[]" }       # the changed files to audit
  - id: audit
    type: parallel
    over: ${list.files}                         # one agent per file
    agent: { role: code-reviewer, output_schema: { findings: "object[]" } }
  - id: summarize
    type: agent
    role: docs-architect
    input: ${audit[].findings}                  # flatten every file's findings
    output_schema: { report: "string" }
```

1. `/craft:orchestrate:workflow WORKFLOW-audit-changed.yaml --dry-run` — preview the per-file fan-out width (`xN` = one `audit` agent per file, known at runtime).
2. `/craft:orchestrate:workflow WORKFLOW-audit-changed.yaml` — audit every file in parallel under the run-wide ceiling; each result is schema-gated, and an empty `list.files` is a hard error (never a silent no-op).
3. Re-run after a fix with `--resume <run-id>` — only the stage you changed (and its downstream) re-runs.

> **vs. the [code-review sweep](run-a-coded-workflow.md) recipe:** same engine,
> different shape — here the fan-out is *one agent per file* instead of *per
> review dimension*. The shape lives in the `over:` binding; swap it to
> re-target the fan-out without touching the rest of the program.
