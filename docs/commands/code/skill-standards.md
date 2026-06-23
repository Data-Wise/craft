# /craft:code:skill-standards

> **Audit skill quality against Anthropic authoring standards**

---

## Synopsis

```bash
/craft:code:skill-standards [--fix] [--json] [--refresh-standards]
```

**Quick examples:**

```bash
# Terminal output (default)
/craft:code:skill-standards

# JSON output for CI pipelines
/craft:code:skill-standards --json

# Auto-fix safe issues (strips rot-prone version tags)
/craft:code:skill-standards --fix

# Refresh provenance block in docs/reference/SKILL-STANDARDS.md
/craft:code:skill-standards --refresh-standards
```

---

## Description

Scans every `skills/**/SKILL.md` against the vendored Anthropic authoring standards in `docs/reference/SKILL-STANDARDS.md`. Reports errors (missing required fields, kebab violations) and warnings (size, hygiene, overlong descriptions). Delegates description rewrites and qualitative gaps to `skill-creator` and `plugin-dev:skill-reviewer`.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--fix` | Auto-fix safe issues (strips rot-prone version tags from reference headers) | false |
| `--json` | Machine-readable JSON output (one object per finding) | false |
| `--refresh-standards` | Update provenance block in `docs/reference/SKILL-STANDARDS.md` | false |

---

## Checks

| # | Check | Severity |
|---|-------|----------|
| 1 | Missing `name` field | ERROR |
| 2 | Non-kebab-case `name` | ERROR |
| 3 | Missing `description` field | ERROR |
| 4 | `description` + `when_to_use` > 1536 chars | WARNING |
| 5 | Unrecognized frontmatter key | WARNING |
| 6 | `SKILL.md` > 500 lines | WARNING |
| 7 | `references/*.md` > 300 lines, no TOC | WARNING |
| 8 | Rot-prone version tag in reference header | WARNING |
| 9 | Second-person framing in reference body | WARNING |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No findings |
| 1 | Warnings only |
| 2 | At least one error |

---

## Score

`Score = 100 − (10 × errors) − (2 × warnings)`, floored at 0.

---

## CI Integration

```bash
# Fail on any errors
python3 scripts/skill_standards_audit.py --json | jq 'any(.[]; .severity == "error")' | grep -q false

# Get errors only
python3 scripts/skill_standards_audit.py --json | jq '[.[] | select(.severity=="error")]'
```

---

## See Also

- [/craft:code:command-audit](command-audit.md) — Command frontmatter validation
- [Tutorial: code:skill-standards](../../tutorials/TUTORIAL-code-skill-standards.md) — Step-by-step usage guide
- [Skill Standards Reference](../../reference/SKILL-STANDARDS.md) — Vendored Anthropic authoring standards
