# Skill-Ecosystem Governance

Policy-as-code for keeping skills organized across **canon** repos (where skills are authored) and
**consumer** surfaces (Claude Code, Cowork, Claude.ai). The rules are stored as **data**, not prose,
so they can be audited, validated, and enforced automatically instead of rotting in scattered
`CLAUDE.md` files.

Lives in [`governance/`](https://github.com/Data-Wise/craft/tree/main/governance).

## Why

Rules written as prose drift and get silently bypassed: archived source paths leave dead symlinks,
and consumer installs lag the canon version for releases at a time. Governance makes organization a
property of the system — a single source of truth, machine-checkable rules, and gates that fail
loudly.

## Components

| File | Role |
|---|---|
| `governance/RULES.yaml` | **Single source of truth** — every rule: `id`, `statement`, `severity`, `gates`, `check`, `waivers`. |
| `governance/run_rules.py` | Engine. Audits the live environment (exit 1 on any unwaived **error** failure); `--selftest` meta-validates the checkers. |
| `governance/render_rules.py` | Generates the human-readable rule block and injects it into any `CLAUDE.md` between markers; `--check` is the **rules-drift** gate. |
| `governance/checks/` | One small, portable checker per automatable rule. |
| `governance/fixtures/` | Good + bad layouts so the checkers are themselves tested. |

## Usage

```bash
# Audit the live environment against the rules (gate CI / a SessionStart hook)
python3 governance/run_rules.py

# Meta-validation: every checker must flag its bad fixture and pass its good one
python3 governance/run_rules.py --selftest

# Keep CLAUDE.md in sync with RULES.yaml (single-source; never hand-edit between markers)
python3 governance/render_rules.py --apply ~/.claude/CLAUDE.md
python3 governance/render_rules.py --check  ~/.claude/CLAUDE.md   # rules-drift gate
```

## Severity, posture, gates

- **Severity** — `error` blocks at its gates · `warn` is surfaced · `advisory` is documented only.
- **Posture** — *gentle-ramp*: a new rule starts as `warn` (or `error` + time-boxed waivers) and
  tightens once the environment is clean.
- **Gates** — each rule names where it fires: `author` (pre-commit) · `ci` (PR) · `release` (dist) ·
  `install` · `session` (SessionStart hook) · `runtime`.

## Adding a rule

1. Append one entry to `RULES.yaml` (`id`, `statement`, `rationale`, `severity`, `gates`, `check`).
2. If `severity: error`, add a `checks/<name>.py` plus a `fixtures/<name>/{good,bad}/` pair.
3. If it has current violations, land it green with a time-boxed `waivers:` entry (owner + future
   `expires`).
4. Commit with a message explaining *why* — the commit is the rationale record.

See `governance/README.md` for the full reference and the proposal it implements.
