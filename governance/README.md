# Skill-Ecosystem Governance (Phase 0)

Policy-as-code for keeping skills organized across canons (savant=research, scholar=teaching)
and consumer surfaces (Claude Code, Cowork, Claude.ai). The rules are **data**, not prose.

## Files

| File | Role |
|---|---|
| `RULES.yaml` | **Single source of truth** — every rule (id, severity, gates, check, waivers). |
| `run_rules.py` | The engine: audits the live environment; `--selftest` meta-validates the checkers. |
| `checks/` | One small, portable checker per automatable rule. |
| `fixtures/` | A known-bad + known-good layout per checker (so we can *test the tester*). |

## Use

```bash
# Audit the live machine (exit 1 on any unwaived ERROR failure -> gate CI / session hook)
python3 governance/run_rules.py --target ~/.claude/skills --index ~/.claude/skills/SKILLS-INDEX.md

# Meta-validation: prove every checker flags its bad fixture and passes its good one
python3 governance/run_rules.py --selftest

# Machine-readable
python3 governance/run_rules.py --json
```

`R07-version-is-truth` is `kind: external` — it consumes drift findings from the cross-surface
auditor `~/.claude/scripts/skills-audit.py` (the per-machine tool); the engine here stays portable.

## Adding a rule (solo-light process)

1. Append one entry to `RULES.yaml` (id, statement, rationale, severity, gates, check).
2. If `severity: error`, add a `checks/<name>.py` + a `fixtures/<name>/{good,bad}/` pair.
3. If it has current violations, land it green with a time-boxed `waivers:` entry (owner + future `expires`).
4. Commit with a message explaining *why* (the commit is the rationale record).

## Severity & posture

- `error` blocks at its gates · `warn` is surfaced · `advisory` is documented only.
- Posture is **gentle-ramp**: new rules start `warn` (or `error` + waivers) and tighten once clean.

## Gates (where a rule fires)

`author` (pre-commit) · `ci` (PR) · `release` (dist) · `install` · `session` (SessionStart hook) · `runtime`.
Phase 0 ships the rule set + engine + selftest. Wiring to gates is Phase 2; `RULES.yaml -> CLAUDE.md`
generation + a `rules-drift` check is Phase 3. See `skill-governance-proposal-2026-06`.
