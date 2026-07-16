---
description: Audit skills/**/SKILL.md against Anthropic authoring standards; report gaps, apply safe fixes, refresh vendored checklist
category: code
arguments:
  - name: format
    description: "Output format: terminal, json, markdown"
    required: false
    default: terminal
  - name: fix
    description: "Auto-fix safe mechanical issues: strip rot-prone version tags from reference headers, normalize frontmatter key casing and order in SKILL.md files, insert TOC stubs in oversized reference files. Never rewrites descriptions or prose."
    required: false
    default: false
    alias: --fix
  - name: refresh-standards
    description: "Refresh the provenance block in docs/reference/SKILL-STANDARDS.md (date + sources); prose synthesis is a manual step"
    required: false
    default: false
    alias: --refresh-standards
---

# /craft:code:skill-standards - Skill Standards Audit

> **This command is a thin shim.** Shared vocabulary (`--format`/`--fix` semantics, health-score
> formula, exit codes) and the full body live in the
> [`audit-router` skill](../../skills/code/audit-router/SKILL.md) — see
> [`references/skill-standards.md`](../../skills/code/audit-router/references/skill-standards.md)
> for the complete reference (what-it-checks table, 5-step remediation flow, auto-fix detail).

Scans every `skills/**/SKILL.md` against the vendored Anthropic authoring standards. Run:

```bash
/craft:code:skill-standards                    # Terminal output (default)
/craft:code:skill-standards --format json       # JSON output
/craft:code:skill-standards --fix               # Auto-fix safe mechanical issues
/craft:code:skill-standards --refresh-standards # Bump provenance date
```

## When Invoked

1. **Load the canonical procedure:** read
   [`skills/code/audit-router/references/skill-standards.md`](../../skills/code/audit-router/references/skill-standards.md)
   and follow it exactly — checks table, the 5-step remediation flow (scan → fix → description
   handoff to `skill-creator` → qualitative handoff to `plugin-dev:skill-reviewer` → refresh
   standards), auto-fix detail, exit codes.
2. **Do not reimplement here.** Any change to this command's checks or remediation flow must be
   made in the reference doc or `scripts/skill_standards_audit.py`, never duplicated into this
   shim.

## See Also

- `/craft:code:command-audit` — sibling schema-audit command (shares `--format`/`--fix`)
- `docs/reference/SKILL-STANDARDS.md` — vendored human-facing checklist
- `/craft:code:lint` — code quality checks
