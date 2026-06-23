<!-- PROVENANCE
synced: 2026-06-23
sources: https://code.claude.com/docs/en/skills.md ; installed skill-creator guide
-->

# Skill Standards Reference

Vendored checklist used by `scripts/skill_standards_audit.py`. Each rule is tagged
`[error]` (blocks the audit score hard) or `[warning]` (advisory; heuristics are
always `[warning]` to avoid false-positive CI breaks).

The script carries the machine constants (`VALID_SKILL_KEYS`, `DESC_MAX`, etc.);
this file is the human-facing companion. Run `--refresh-standards` to bump the
provenance date after pulling updated upstream docs, then re-synthesize prose as
needed.

---

## Frontmatter Rules

| Rule | Tag | Notes |
|------|-----|-------|
| `name` field is required | `[error]` | Absence blocks every NL-dispatch path |
| `name` must be kebab-case | `[error]` | `^[a-z0-9]+(-[a-z0-9]+)*$` |
| `description` field is required | `[error]` | Absent = skill is invisible to the model |
| `description` (+ `when_to_use`) must be ≤ 1536 chars combined | `[warning]` | Anthropic hard cap; excess is silently truncated |
| Unrecognized frontmatter keys | `[warning]` | Key set evolves; unknown keys are tolerated but flagged |

**Valid frontmatter keys** (current as of provenance date):

```
name, description, when_to_use, allowed-tools, disallowed-tools,
paths, disable-model-invocation, user-invocable, context, agent,
model, effort, argument-hint, arguments, shell, hooks, license,
category, deprecated, replaced-by
```

The last three (`category`, `deprecated`, `replaced-by`) are craft-local
extensions tolerated on skills.

---

## Size & Progressive Disclosure

| Rule | Tag | Notes |
|------|-----|-------|
| `SKILL.md` should be ≤ 500 lines | `[warning]` | Move long context to `references/*.md` |
| `references/*.md` > 300 lines requires a `## Table of Contents` heading | `[warning]` | Enables navigation in large reference files |

The 500-line and 300-line caps are soft ceilings; the scanner emits warnings so
authors can decide whether to split. Deep reference material belongs in
`references/` so the model can skip it when not relevant.

---

## Reference Hygiene

All checks in this section are `[warning]`-only (heuristic; false positives are
possible).

| Rule | Tag | Notes |
|------|-----|-------|
| Headers in `references/*.md` must not contain rot-prone version tags | `[warning]` | Pattern: `(NEW in v2.x)`, `(Phase N)` — these go stale |
| `references/*.md` must not open with second-person command framing | `[warning]` | `You are…` phrasing belongs in command `.md` files, not timeless reference prose |

**Safe fix:** `--fix` strips version tags from headers automatically.
Second-person framing is **never auto-fixed** — hand off to `skill-creator run_loop.py`.

---

## Advisory Keys

These keys are not errors or warnings; they are documentation for best practice.

- **`when_to_use`** — strongly recommended whenever `description` alone is
  ambiguous about trigger conditions. Counts toward the 1536-char cap.
- **`allowed-tools`** — restrict the tool surface available to the skill; reduces
  model confusion in multi-tool contexts.
- **`disable-model-invocation: true`** — for pure-reference skills that should
  never spin up a model context.
- **`user-invocable: false`** — hide utility sub-skills from the skill picker UI.

---

## Scoring

Mirrors `scripts/command-audit.sh`:

```
score = 100 − (errors × 5) − (warnings × 2)
score = max(0, score)
```

| Score | Rating |
|-------|--------|
| 90–100 | Excellent |
| 80–89 | Good |
| 60–79 | Needs attention |
| 0–59 | Critical |

Exit codes: `0` clean · `1` warnings only · `2` any error.

---

## See Also

- `scripts/skill_standards_audit.py` — machine implementation of these rules
- `/craft:code:skill-standards` — command surface (scan, fix, refresh, delegate)
- `plugin-dev:skill-reviewer` — qualitative gap analysis (voice, value, coverage)
- `skill-creator run_loop.py` — iterative description rewriting
