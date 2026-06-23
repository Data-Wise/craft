# Tutorial: code:skill-standards — Audit Skill Quality

By the end of this tutorial you will have:

- Audited all `skills/**/SKILL.md` files against the Anthropic Skill Standards
- Understood each finding type and its severity
- Applied safe auto-fixes with `--fix`
- Delegated qualitative gaps to `skill-creator` / `plugin-dev:skill-reviewer`

**Prerequisites:** craft installed, working in a Claude Code plugin repo that has a `skills/` directory.

---

## Step 1: Run the Audit

```
/craft:code:skill-standards
```

Scans every `skills/**/SKILL.md` against the vendored standards in
`docs/reference/SKILL-STANDARDS.md`:

```
Skill Standards Audit
──────────────────────────────
Scanning 39 skills...

  🔴 [missing-field] workflow/brainstorm/SKILL.md: missing required field 'description'
  🟡 [overlong-desc] code/lint/SKILL.md: description is 247 chars (limit 200)
  🟡 [size] release/SKILL.md: SKILL.md is 1308 lines, exceeds 500 — move detail to references/
  🟡 [no-toc] docs/changelog-automation/SKILL.md: file > 300 lines and has no table of contents

Score: 90/100  (1 error, 3 warnings)
```

### Reading the Report

| Symbol | Severity | Meaning |
| ------ | -------- | ------- |
| 🔴     | Error    | Required field missing or kebab-case name violation — must fix before releasing |
| 🟡     | Warning  | Size, hygiene, or length guidance — fix when practical |

**Score** = 100 − (10 × errors) − (2 × warnings), floored at 0.

---

## Step 2: Apply Safe Auto-Fixes

```
/craft:code:skill-standards --fix
```

Strips rot-prone version tags from description fields (e.g., `"(v2.3.0) "` prefixes).
Does not rewrite content — only removes patterns that become stale as versions change.

After `--fix` runs, verify the changes with `git diff`, then re-run without `--fix` to
confirm the score improved.

---

## Step 3: Machine-Readable Output

```
/craft:code:skill-standards --json
```

Emits a JSON array — one object per finding:

```json
[
  {
    "skill": "release/SKILL.md",
    "check": "size",
    "severity": "warning",
    "message": "SKILL.md is 1308 lines, exceeds 500 — move detail to references/"
  }
]
```

Pipe to `jq` for filtering:

```bash
python3 scripts/skill_standards_audit.py --json | jq '[.[] | select(.severity=="error")]'
```

---

## Step 4: Refresh the Standards Reference

```
/craft:code:skill-standards --refresh-standards
```

Updates the provenance block (date and source URLs) in `docs/reference/SKILL-STANDARDS.md`.
The prose content itself is not overwritten — prose synthesis is a manual step when
Anthropic publishes a substantive update to the authoring guidelines.

Run this once per quarter or whenever Anthropic announces skill-authoring changes.

---

## Step 5: Fix Qualitative Gaps

Auto-fix handles structural issues. For content quality — rewriting a weak description,
adding missing `trigger` examples, improving `when_to_use` specificity — delegate to the
skill-authoring tools:

**Rewrite a single skill:**

```
Use skill-creator to improve the description and trigger in skills/workflow/brainstorm/SKILL.md.
Current description: "Brainstorming support" (too vague).
Target: specific, action-oriented, ≤200 chars.
```

**Review a skill for overall quality:**

```
/plugin-dev:skill-reviewer skills/release/SKILL.md
```

The `plugin-dev:skill-reviewer` agent checks trigger effectiveness, example coverage,
and whether the `when_to_use` clause would fire correctly in the Claude Code NL routing path.

---

## Step 6: Pre-Release Gate

Add to your pre-release checklist:

```
/craft:code:skill-standards
```

The command exits non-zero when errors remain. CI can gate on this:

```bash
python3 scripts/skill_standards_audit.py --json | jq 'any(.[]; .severity == "error")' | grep -q false
```

A clean run (0 errors) gives a score ≥ 90/100 with only warnings remaining.

---

## Summary

| Flag                    | Effect                                                          |
| ----------------------- | --------------------------------------------------------------- |
| *(none)*                | Terminal report — errors + warnings, score, exit 1 if errors   |
| `--fix`                 | Strip version tags from descriptions; exit 0 if no errors left |
| `--json`                | Machine-readable array (pipe to `jq`)                          |
| `--refresh-standards`   | Update provenance block in `docs/reference/SKILL-STANDARDS.md` |

**Reference:** `docs/reference/SKILL-STANDARDS.md` — canonical Anthropic Skill Standards, vendored offline.
