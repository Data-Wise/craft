---
name: audit-router
description: This skill should be used when the user asks to "audit commands", "check command frontmatter", "audit skills", "check skill standards", "validate command/skill health", or invokes `/craft:code:command-audit` or `/craft:code:skill-standards`. Shared vocabulary + reference bodies for craft's two schema-audit commands — both validate craft's own frontmatter (commands/skills/agents vs `_schema.json`, or `skills/**/SKILL.md` vs Anthropic's authoring standards) and share the same `--format`/`--fix` semantics. Not for dependency or docs-site checks — see `/craft:code:deps-audit`, `/craft:code:deps-check`, `/craft:code:docs-check` instead, which are unrelated generic cross-project tools despite living in the same `commands/code/` directory.
---

# Audit Router — Shared Vocabulary for craft's Schema-Audit Commands

Two commands audit craft's own frontmatter against a schema and share one vocabulary:

| Command | Validates | Against |
|---|---|---|
| `/craft:code:command-audit` | `commands/`, `skills/`, `agents/` frontmatter | `_schema.json` |
| `/craft:code:skill-standards` | `skills/**/SKILL.md` | vendored Anthropic authoring standards (`docs/reference/SKILL-STANDARDS.md`) |

Both commands stay independently slash-invocable — this skill holds the shared vocabulary and
each command's full reference body, not a replacement entry point.

## Shared Flag Vocabulary

Both commands accept the same two flags with the same meaning:

- **`--format terminal|json|markdown`** — output rendering only, default `terminal`. Never
  changes what is checked.
- **`--fix`** — auto-fixes *safe mechanical issues only*, never prose or descriptions:
  - `command-audit --fix`: removes invalid frontmatter fields, renames `args` → `arguments`.
  - `skill-standards --fix`: strips rot-prone version tags from reference headers, normalizes
    frontmatter key casing/order, inserts TOC stubs in oversized reference files.

Both share the same health-score formula (`100 − errors×5 − warnings×2`, floored at 0) and the
same exit-code convention (0 clean, 1 warnings-only, 2 errors — `command-audit --strict` also
treats warnings as errors, matching skill-standards' own error-severity checks).

`skill-standards` carries one extra flag (`--refresh-standards`) with no `command-audit`
equivalent — documented in its own reference only, not promoted to the shared set.

## Full Reference Bodies

- [`references/command-audit.md`](references/command-audit.md) — full command-audit body
  (what-it-checks table, CI integration, output example, exit codes)
- [`references/skill-standards.md`](references/skill-standards.md) — full skill-standards body
  (what-it-checks table, 5-step remediation flow, auto-fix mode detail, exit codes)

## Not This Skill

`deps-audit`, `deps-check`, `docs-check` are **not** schema-audit-shaped — they're generic
cross-project tools (dependency security/freshness for any project, or a full docs/site
preflight+deploy pipeline) with incompatible flag surfaces. They stay independent commands
with their own bodies, not references under this skill.
