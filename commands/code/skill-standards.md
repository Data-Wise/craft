---
description: Audit skills/**/SKILL.md against Anthropic authoring standards; report gaps, apply safe fixes, refresh vendored checklist
category: code
arguments:
  - name: format
    description: "Output format: terminal, json, markdown"
    required: false
    default: terminal
  - name: fix
    description: Auto-fix safe issues (strips rot-prone version tags from reference headers)
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

Scans every `skills/**/SKILL.md` against the vendored Anthropic authoring
standards in `docs/reference/SKILL-STANDARDS.md`. Reports errors (missing
`name`/`description`, kebab violations) and warnings (size, hygiene,
overlong descriptions). Delegates description rewrites and qualitative gaps
to `skill-creator` and `plugin-dev:skill-reviewer`.

## What It Checks

| # | Check | Severity | Description |
|---|-------|----------|-------------|
| 1 | Missing `name` | ERROR | Required field; absence blocks NL dispatch |
| 2 | Non-kebab-case `name` | ERROR | Must match `^[a-z0-9]+(-[a-z0-9]+)*$` |
| 3 | Missing `description` | ERROR | Required; absent = skill invisible to model |
| 4 | `description`+`when_to_use` > 1536 chars | WARNING | Anthropic hard cap |
| 5 | Unrecognized frontmatter key | WARNING | Key set evolves; flagged for review |
| 6 | `SKILL.md` > 500 lines | WARNING | Move detail to `references/` |
| 7 | `references/*.md` > 300 lines, no TOC | WARNING | Add `## Table of Contents` |
| 8 | Rot-prone version tag in reference header | WARNING | e.g. `(NEW in v2.x)` — safe to `--fix` |
| 9 | Second-person framing in reference body | WARNING | `You are…` — hand off to skill-creator |

## Usage

```bash
python3 scripts/skill_standards_audit.py                    # Terminal output (default)
python3 scripts/skill_standards_audit.py --json             # JSON output
python3 scripts/skill_standards_audit.py --markdown         # Markdown report
python3 scripts/skill_standards_audit.py --fix              # Auto-fix safe issues
python3 scripts/skill_standards_audit.py --refresh-standards  # Bump provenance date
```

## Steps

**Step 1 — Run the scanner**

```bash
python3 scripts/skill_standards_audit.py
```

Review the terminal report. For machine-readable output pipe to a file:

```bash
python3 scripts/skill_standards_audit.py --json > /tmp/skill-audit.json
python3 scripts/skill_standards_audit.py --markdown > /tmp/skill-audit.md
```

**Step 2 — Apply safe mechanical fixes**

```bash
python3 scripts/skill_standards_audit.py --fix
```

`--fix` strips rot-prone version tags from `references/*.md` headers only.
It never rewrites `description` or other prose.

**Step 3 — Fix description findings**

For any `frontmatter` errors/warnings touching `description` quality or voice,
hand off to `skill-creator`:

```bash
skill-creator run_loop.py skills/<category>/<name>/SKILL.md
```

`skill-creator` iterates the description against Anthropic's trigger-effectiveness
rubric and proposes rewrites. Review and accept interactively.

**Step 4 — Fix qualitative gaps**

For structural gaps (missing `when_to_use`, thin body, weak examples), dispatch
`plugin-dev:skill-reviewer`:

> "Review `skills/<category>/<name>/SKILL.md` for quality gaps — missing
> trigger conditions, thin body, weak examples. Report findings only."

Apply the suggested improvements to the SKILL.md body.

**Step 5 — Refresh the vendored standards (after upstream changes)**

When Anthropic releases updates to the skills authoring guide:

```bash
python3 scripts/skill_standards_audit.py --refresh-standards
```

This rewrites only the `<!-- PROVENANCE ... -->` block in
`docs/reference/SKILL-STANDARDS.md` with today's date and source URLs.
After refreshing, re-read the upstream docs and update the prose checklist
in `docs/reference/SKILL-STANDARDS.md` manually (or ask the model to
synthesize the delta).

## Auto-Fix Mode

When `--fix` is passed, the script will:

- Strip version tags from `references/*.md` section headers (e.g. `(NEW in v2.49.0)`)

It will **not** auto-fix:

- Description voice or value issues → use `skill-creator run_loop.py`
- Second-person framing in references → edit manually or use `skill-creator`
- Size issues → manually split content into `references/`

## Health Score

```text
score = 100 − (errors × 5) − (warnings × 2)
score = max(0, score)
```

| Score | Rating |
|-------|--------|
| 90–100 | Excellent |
| 80–89 | Good |
| 60–79 | Needs attention |
| 0–59 | Critical |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | Warnings found (no errors) |
| 2 | Errors found |

## Integration

Works with:

- `plugin-dev:skill-reviewer` — qualitative gap analysis
- `skill-creator run_loop.py` — iterative description rewriting
- `/craft:code:command-audit` — command-level frontmatter audit
- `/craft:check` — pre-flight validation

## See Also

- `docs/reference/SKILL-STANDARDS.md` — vendored human-facing checklist
- `scripts/skill_standards_audit.py` — scanner implementation
- `/craft:code:lint` — code quality checks
