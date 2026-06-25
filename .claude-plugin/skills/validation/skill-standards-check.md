---
name: check:skill-standards
description: Audit skills/**/SKILL.md against Anthropic's skill standards (advisory below release, blocking at the release tier)
category: validation
context: fork
hot_reload: true
version: 2.0.0
dependencies:
  - python3
  - scripts/skill_standards_audit.py
---

# Skill Standards Validator (Graduated Gate)

Audit every `skills/**/SKILL.md` against the vendored Anthropic skill standards
(`docs/reference/SKILL-STANDARDS.md`) via `scripts/skill_standards_audit.py`.
**Graduated gate**: advisory (warn-only) in `commit`/`pr`/`default`/`debug`/`thorough`
contexts, **blocking at the release tier** (`CRAFT_MODE=release`, set by
`/craft:check --for release`). The ecosystem is at 39/39 skills @ 100/100, so the
governance warn→error soak completed — the release gate now keeps it that way.
A missing audit script or standards doc degrades to advisory (never red-lists a
release on a tooling fault).

## What This Checks

Per-skill frontmatter completeness, size limits, naming hygiene, and version-tag
cleanliness — the same rules `/craft:code:skill-standards` enforces. Reports an
aggregate score and lists any skill below 100.

## Mode Behavior

The audit (`scripts/skill_standards_audit.py`) exits `0` clean · `1` warnings-only ·
`2` error-severity findings. This validator propagates that exit code **only at the
release tier**; below it, findings are advisory.

| Mode | What runs | Exit on findings |
|------|-----------|------------------|
| default / debug / thorough | audit all SKILL.md, print summary | **0 (advisory)** |
| release | same (set by `--for release`) | **propagates audit code (1/2) — blocks** |

## Implementation

```bash
#!/bin/bash
set -uo pipefail

MODE="${CRAFT_MODE:-default}"

# Resolve craft root (BASH_SOURCE when sourced, else walk up from PWD).
ROOT="${CRAFT_ROOT:-}"
if [ -z "$ROOT" ]; then
  d="$PWD"
  while [ "$d" != "/" ] && [ ! -f "$d/.claude-plugin/plugin.json" ]; do d="$(dirname "$d")"; done
  ROOT="$d"
fi
AUDIT="$ROOT/scripts/skill_standards_audit.py"
SKILLS_ROOT="${SKILL_STANDARDS_ROOT:-$ROOT/skills}"

# Missing tooling is a fault, not a finding — degrade to advisory so a release
# is never red-listed because the audit script could not be located.
if [ ! -f "$AUDIT" ]; then
  echo "⚠️  skill-standards: audit script not found ($AUDIT) — skipping (advisory)"
  exit 0
fi

# Audit exit codes: 0 clean · 1 warnings-only · 2 error-severity findings.
OUT="$(python3 "$AUDIT" --root "$SKILLS_ROOT" 2>&1)"; CODE=$?

if [ "$MODE" = "release" ]; then LABEL="release gate"; else LABEL="advisory"; fi
echo "╭─ skill-standards ($LABEL) ──────────────────────────╮"
printf '%s\n' "$OUT" | sed 's/^/│ /'
case "$CODE" in
  0) echo "│ ✅ all skills compliant"                         ;;
  1) echo "│ ⚠️  warnings (sub-100) — see above"              ;;
  2) echo "│ 🔴 error-severity findings — see above"          ;;
esac

# Gate only at the release tier; warn-only everywhere else.
if [ "$MODE" = "release" ] && [ "$CODE" -ne 0 ]; then
  echo "│ ⛔ release tier: blocking on findings"
  echo "╰─────────────────────────────────────────────────────╯"
  exit "$CODE"
fi
[ "$CODE" -ne 0 ] && echo "│ (advisory below release — not blocking)"
echo "╰─────────────────────────────────────────────────────╯"
exit 0
```
