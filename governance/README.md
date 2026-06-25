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
| `render_rules.py` | **Phase 3 safeguard** — generates the human-readable rule block from `RULES.yaml` and injects it between markers in any `CLAUDE.md`; `--check` is the `rules-drift` gate (wired at pre-commit + CI). |
| `CLAUDE-rules.md` | In-repo generated target, so the CI/pre-commit drift check runs self-contained. |

## Use

```bash
# Audit the live machine (exit 1 on any unwaived error-severity failure)
python3 governance/run_rules.py --target ~/.claude/skills --index ~/.claude/skills/SKILLS-INDEX.md

# Meta-validation: prove every checker flags its bad fixture and passes its good one
python3 governance/run_rules.py --selftest

# Scan a specific marketplace manifest for R03 (default: in-repo .claude-plugin/marketplace.json)
python3 governance/run_rules.py --marketplace path/to/marketplace.json

# Machine-readable
python3 governance/run_rules.py --json
```

**Enforcement (Phase 2):** `--selftest` + the `render --check` drift gate run at **pre-commit** (the
`governance-gate` hook, scoped to `governance/`) and in **CI** (`ci.yml`). CI deliberately does NOT run
the live-env audit — R01/R07 need the canon repos / cross-surface feed that exist only locally, so a
green CI run validates checker behaviour + doc currency, not those live-env rules.

**SessionStart hook (visibility):** `session_hook.py` runs the live-env audit against `~/.claude/skills`
at session open and injects a compact **RED-only** summary into context (silent when clean; mtime-cached;
a no-op where `~/.claude/skills` is absent). SessionStart hooks inject context, they cannot block — this
is the surface where local-only drift (a dead skill symlink) gets seen. Install it **globally** by adding
a `SessionStart` entry to `~/.claude/settings.json`:

```json
{ "hooks": { "SessionStart": [ { "hooks": [
  { "type": "command", "command": "python3 /ABS/PATH/TO/craft/governance/session_hook.py" }
] } ] } }
```

**SessionStart coordination (#205 item 4).** `session_hook.py` and the index writer
`~/.claude/scripts/skills-audit.py --write-index` do **not** conflict — they have distinct jobs:

| Component | Writes `SKILLS-INDEX.md`? | Role |
|-----------|--------------------------|------|
| `skills-audit.py --write-index` (in `settings.json`) | **yes** — sole writer | regenerates the index each session |
| `governance/session_hook.py` | no — **reads** it | runs the audit + feeds the soak ledger |

So **keep the `skills-audit.py --write-index` line** — removing it would leave nothing writing the
index. Wiring `session_hook.py` globally remains **deferred** (a deliberate, separate step; until then
it is not installed and there is no double-write to reconcile). The earlier worry that the hook would
*supersede* the index writer was based on a misread of what `session_hook.py` writes — it writes
nothing but the soak ledger.

**Fail-closed:** an `error` rule whose checker is missing or unresolvable (state `ERROR`) gates the
build too — a broken checker never passes silently. Only `error`-severity rules block; `warn` rules
in `ERROR`/`FAIL` are surfaced but never gate.

`R07-version-is-truth` is `kind: external` — it consumes drift findings from the cross-surface
auditor `~/.claude/scripts/skills-audit.py` (the per-machine tool); the engine here stays portable.
`--selftest` names external rules explicitly (they get no fixture meta-validation here) rather than
skipping them silently.

## Adding a rule (solo-light process)

1. Append one entry to `RULES.yaml` (id, statement, rationale, severity, gates, check).
2. If `severity: error`, add a `checks/<name>.py` + a `fixtures/<name>/{good,bad}/` pair.
3. If it has current violations, land it green with a time-boxed `waivers:` entry (owner + future `expires`).
4. Commit with a message explaining *why* (the commit is the rationale record).

## Severity & posture

- `error` blocks at its gates · `warn` is surfaced · `advisory` is documented only.
- Posture is **gentle-ramp**: new rules start `warn` (or `error` + waivers) and tighten once clean.

**Soak-then-flip promotion.** The SessionStart hook feeds a local, gitignored `STATE.json` ledger
(`first_seen`/`last_seen`/`last_red` per rule). `run_rules.py --promote-check` lists `warn` rules soaked
clean ≥ `--window` days (default 14) — eligible for a human `warn → error` flip in `RULES.yaml`. The
machinery recommends; the human promotes. Per-machine soak evidence is never committed.

```bash
python3 governance/run_rules.py --promote-check [--window N] [--state PATH]
```

**Cross-repo.** Consumers invoke the one installed craft engine via `governance/run.sh` (resolves its own
dir, `__file__`-relative engine → cwd-portable) — one pinned copy, no drift (`R07-version-is-truth`).

## Gates (advisory metadata — where a rule is *meant* to run)

`author` (pre-commit) · `ci` (PR) · `release` (dist) · `install` · `session` (SessionStart hook) · `runtime`.
Phase 0 ships the rule set + engine + selftest. See `skill-governance-proposal-2026-06`.

**`gates` is documentation, not runtime routing.** `render_rules.py` renders each rule's `gates` into
the human-readable rule block in `CLAUDE.md` to record where the check is intended to run. The audit
engine (`run_rules.py`) does **not** read `gates` — it runs every active rule regardless, and only
severity decides blocking. The intent records a future home for each check: `R01-single-source` is
meant for `session` (not `ci`) because the duplicate-canon check needs the savant + scholar repos
checked out, which only holds locally. When R01 runs in craft CI it announces a vacuous skip — that
skip comes from the checker's own "fewer than 2 canon dirs present" guard in
`checks/no_duplicate_canon.py`, not from gate routing. A checker that can't see its inputs must say so
out loud, never pass silently.

## Keeping CLAUDE.md in sync (Phase 3)

The rule block in any `CLAUDE.md` is **generated**, never hand-written:

```bash
python3 governance/render_rules.py                       # print the block
python3 governance/render_rules.py --init  ~/.claude/CLAUDE.md   # append a marked block (first time)
python3 governance/render_rules.py --apply ~/.claude/CLAUDE.md   # regenerate after editing RULES.yaml
python3 governance/render_rules.py --check ~/.claude/CLAUDE.md governance/CLAUDE-rules.md  # rules-drift gate (CI/hook)
```

Edit `RULES.yaml`, run `--apply`, commit. A `--check` in CI fails if anyone hand-edits between the
`RULES:BEGIN`/`RULES:END` markers — so the copies can never silently diverge from the source of truth.
