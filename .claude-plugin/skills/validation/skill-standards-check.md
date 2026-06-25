---
name: check:skill-standards
description: Audit skills/**/SKILL.md against Anthropic's skill standards (advisory — reports score, never fails the check)
category: validation
context: fork
hot_reload: true
version: 1.0.0
dependencies:
  - python3
  - scripts/skill_standards_audit.py
---

# Skill Standards Validator (Advisory)

Audit every `skills/**/SKILL.md` against the vendored Anthropic skill standards
(`docs/reference/SKILL-STANDARDS.md`) via `scripts/skill_standards_audit.py`.
**Advisory only**: it surfaces sub-100 skills as warnings but never fails
`/craft:check`. Graduation to a blocking gate follows the governance warn→error
soak path once the ecosystem stays clean.

## What This Checks

Per-skill frontmatter completeness, size limits, naming hygiene, and version-tag
cleanliness — the same rules `/craft:code:skill-standards` enforces. Reports an
aggregate score and lists any skill below 100.

## Mode Behavior

| Mode | What runs | Exit on findings |
|------|-----------|------------------|
| default | audit all SKILL.md, print summary | **0 (advisory)** |
| debug | same + per-skill score table | **0 (advisory)** |
| release | same | **0 (advisory)** — never blocks |

## Implementation

```bash
#!/bin/bash
set -uo pipefail

# Resolve craft root (BASH_SOURCE when sourced, else walk up from PWD).
ROOT="${CRAFT_ROOT:-}"
if [ -z "$ROOT" ]; then
  d="$PWD"
  while [ "$d" != "/" ] && [ ! -f "$d/.claude-plugin/plugin.json" ]; do d="$(dirname "$d")"; done
  ROOT="$d"
fi
AUDIT="$ROOT/scripts/skill_standards_audit.py"
SKILLS_ROOT="${SKILL_STANDARDS_ROOT:-$ROOT/skills}"

if [ ! -f "$AUDIT" ]; then
  echo "⚠️  skill-standards: audit script not found ($AUDIT) — skipping (advisory)"
  exit 0
fi

OUT="$(python3 "$AUDIT" --root "$SKILLS_ROOT" 2>&1)"; CODE=$?
echo "╭─ skill-standards (advisory) ────────────────────────╮"
printf '%s\n' "$OUT" | sed 's/^/│ /'
case "$CODE" in
  0) echo "│ ✅ all skills compliant"                        ;;
  1) echo "│ ⚠️  findings above — advisory, not blocking"     ;;
  2) echo "│ ⚠️  audit engine error — advisory, not blocking" ;;
esac
echo "╰─────────────────────────────────────────────────────╯"
exit 0   # advisory: never propagate the audit's exit code
```
