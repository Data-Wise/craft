---
description: Validate command frontmatter, find deprecated patterns, report health score
category: code
arguments:
  - name: format
    description: "Output format: terminal, json, markdown"
    required: false
    default: terminal
  - name: fix
    description: Auto-fix safe issues
    required: false
    default: false
    alias: --fix
  - name: strict
    description: Treat warnings as errors (for CI)
    required: false
    default: false
    alias: --strict
---

# /craft:code:command-audit - Command Audit

> **This command is a thin shim.** Shared vocabulary (`--format`/`--fix` semantics, health-score
> formula, exit codes) and the full body live in the
> [`audit-router` skill](../../skills/code/audit-router/SKILL.md) — see
> [`references/command-audit.md`](../../skills/code/audit-router/references/command-audit.md)
> for the complete reference (what-it-checks table, CI integration, output example).

Validate all command, skill, and agent frontmatter against the schema (`_schema.json`). Run:

```bash
/craft:code:command-audit                    # Terminal output (default)
/craft:code:command-audit --format json      # JSON output
/craft:code:command-audit --fix              # Auto-fix safe issues (invalid fields, args->arguments rename)
/craft:code:command-audit --strict           # Treat warnings as errors (CI)
```

## When Invoked

1. **Load the canonical procedure:** read
   `${CLAUDE_PLUGIN_ROOT:-.}/skills/code/audit-router/references/command-audit.md`
   and follow it exactly — checks table, CLI invocation (`bash scripts/command-audit.sh`),
   health-score formula, output format, exit codes.
2. **Do not reimplement here.** Any change to this command's checks or output must be made in
   the reference doc or `scripts/command-audit.sh`, never duplicated into this shim.

## See Also

- `/craft:code:skill-standards` — sibling schema-audit command (shares `--format`/`--fix`)
- `/craft:code:lint` — code quality checks
- `/craft:check` — pre-flight validation
