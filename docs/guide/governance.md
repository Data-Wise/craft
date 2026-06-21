# Skill-Ecosystem Governance

Policy-as-code for keeping skills organized across **canon** repos (where skills are authored) and
**consumer** surfaces (Claude Code, Cowork, Claude.ai). The rules are stored as **data**, not prose,
so they can be audited, validated, and enforced automatically instead of rotting in scattered
`CLAUDE.md` files.

Lives in [`governance/`](https://github.com/Data-Wise/craft/tree/main/governance).

## Why

Rules written as prose drift and get silently bypassed: archived source paths leave dead symlinks,
and consumer installs lag the canon version for releases at a time. Governance makes organization a
property of the system — a single source of truth, machine-checkable rules, and a fail-loud audit
engine. The `--selftest` + rules-drift gates are wired at **pre-commit + CI** (prevention); the live-env
audit is surfaced at session open via a **SessionStart hook** (visibility).

## Components

| File | Role |
|---|---|
| `governance/RULES.yaml` | **Single source of truth** — every rule: `id`, `statement`, `severity`, `gates`, `check`, `waivers`. |
| `governance/run_rules.py` | Engine. Audits the live environment (exit 1 on any unwaived **error**-severity failure — **fail-closed**: a missing/broken checker on an error rule gates too); `--selftest` meta-validates the checkers. |
| `governance/render_rules.py` | Generates the human-readable rule block and injects it into any `CLAUDE.md` between markers; `--check` is the **rules-drift** gate (wired at pre-commit + CI). |
| `governance/checks/` | One small, portable checker per automatable rule. |
| `governance/fixtures/` | Good + bad layouts so the checkers are themselves tested. |

## Usage

```bash
# Audit the live environment against the rules
# (the live-env audit runs at session open via governance/session_hook.py; CI/pre-commit run --selftest + drift instead)
python3 governance/run_rules.py

# Meta-validation: every checker must flag its bad fixture and pass its good one
python3 governance/run_rules.py --selftest

# Keep CLAUDE.md in sync with RULES.yaml (single-source; never hand-edit between markers)
python3 governance/render_rules.py --apply ~/.claude/CLAUDE.md
python3 governance/render_rules.py --check  ~/.claude/CLAUDE.md   # rules-drift gate
```

## Severity, posture, gates

- **Severity** — `error` blocks · `warn` is surfaced · `advisory` is documented only. Severity is the
  only thing that decides blocking: `run_rules.py` runs **every** active rule and counts unwaived
  `error`-severity failures, regardless of `gates`.
- **Posture** — *gentle-ramp*: a new rule starts as `warn` (or `error` + time-boxed waivers) and
  tightens once the environment is clean.
- **Gates** — `author` (pre-commit) · `ci` (PR) · `release` (dist) · `install` · `session`
  (SessionStart hook) · `runtime`. **Gates are advisory metadata**: `render_rules.py` renders them
  into the human-readable rule block in `CLAUDE.md` to document *where a rule is meant to run*, but
  the audit engine does **not** read `gates` at runtime — it does not route execution. The intent
  records a future home for each check (e.g. `R01-single-source` is meant for `session`, not `ci`,
  since its canon repos only exist locally). When R01 runs in craft CI it announces a vacuous skip —
  but that skip comes from the checker's own "fewer than 2 canon dirs present" guard in
  `checks/no_duplicate_canon.py`, not from gate routing.

## Gates & enforcement (Phase 2)

The engine is wired into three surfaces — two that **prevent** (block bad changes) and one that
**surfaces** (shows drift without blocking):

- **pre-commit** (`author`, prevention) — the `governance-gate` hook (`files: ^governance/`) runs
  `run_rules.py --selftest` + `render_rules.py --check` on any `governance/` change. It blocks a commit
  that breaks a checker or hand-edits the generated rule block. It does **not** run the live-env audit
  (that needs the canon repos / `~/.claude/skills`, which a clean commit lacks).
- **CI** (`ci`, prevention) — `ci.yml` runs the same selftest + drift-check after the test suite. It
  prints an explicit note that CI does **not** evaluate R01/R07 live-env state (canon repos and the
  cross-surface feed exist only locally) — so a green run is never misread as live-env enforcement.
- **SessionStart hook** (`session`, **visibility**) — `governance/session_hook.py` audits the live
  `~/.claude/skills` tree at session open and injects a compact **RED-only** summary into context (e.g.
  `GOVERNANCE: 1 red — R08-no-dead-links`). SessionStart hooks **inject context, they cannot block** —
  this is the *visibility* surface where local-only rules (a dead skill symlink) actually get seen.
  Quiet by design: silent when clean, mtime-cached (unchanged tree → skip re-audit), and a no-op where
  `~/.claude/skills` is absent. Install it **globally** by wiring `session_hook.py` into a `SessionStart`
  entry in `~/.claude/settings.json` (see `governance/README.md`).
- **Release pre-flight** (`release`, **advisory**) — `scripts/pre-release-check.sh` runs
  `run_rules.py --json` and prints any RED finding count, but **never blocks the release** (it doesn't
  touch the script's error counter). Gentle-ramp: a release surfaces governance drift without being
  halted by it.

`R03-private-marketplace` is now automated (`checks/no_private_in_public_marketplace.py {marketplace}`):
it fails if a public marketplace manifest lists a plugin sourced from a private/PII repo (denylist,
no network). Pass `--marketplace FILE` to point the audit at a specific manifest; the default is the
in-repo `.claude-plugin/marketplace.json`.

`R04-consume-not-copy` is automated as **content drift** (`checks/no_drifted_copy.py {target}`): a skill
present on both a consumer surface and a canon repo must have a byte-identical `SKILL.md` — a divergence
means the copy was hand-edited rather than consumed via `plugin update`. This is **distinct from R07**
(version-pin equality): R04 catches a drifted *body* even when the version still matches. It gates
`session` (the canon repos are local-only; vacuous-skip elsewhere).

## Promotion: soak-then-flip (the gentle-ramp)

A rule starts at `severity: warn` and tightens to `error` only once its surface has been clean for a
while — the machinery **recommends**, a human **promotes** (an irreversible tightening stays a
deliberate edit).

- The SessionStart hook feeds a **local, gitignored `governance/STATE.json`** ledger: each audit stamps
  `first_seen` / `last_seen` and a `last_red` per rule. Soak evidence is **per-machine** (the live skills
  tree only exists locally), so the ledger is never committed.
- `run_rules.py --promote-check` lists `warn` rules that have soaked clean for ≥ the window
  (`--window`, default 14 days) — eligible for a human `warn → error` flip in `RULES.yaml`. A rule
  qualifies only with **both** enough observation history (`first_seen` ≥ window old) **and** no RED
  inside the window. Advisory: always exits 0.

```bash
python3 governance/run_rules.py --promote-check            # what's ripe to tighten?
python3 governance/run_rules.py --promote-check --window 7 # shorter soak
```

The flip itself is a one-line `RULES.yaml` edit (`severity: warn → error`), optionally with a time-boxed
`waivers:` entry for any residual violations — the waiver primitives already gate on owner + future expiry.

## Cross-repo consumption (one pinned copy, no drift)

`governance/` ships inside the craft plugin. Consumer canons (savant, scholar) do **not** vendor a copy —
they invoke the **installed** craft engine through a thin wrapper, so there is exactly one copy and no
drift (matches `R07-version-is-truth`):

```bash
<craft-plugin-root>/governance/run.sh --selftest
<craft-plugin-root>/governance/run.sh --target ~/.claude/skills --json
```

`run.sh` resolves its own directory and runs `run_rules.py` from there; the engine is `__file__`-relative,
so it works from any caller's cwd.

## Adding a rule

1. Append one entry to `RULES.yaml` (`id`, `statement`, `rationale`, `severity`, `gates`, `check`).
2. If `severity: error`, add a `checks/<name>.py` plus a `fixtures/<name>/{good,bad}/` pair.
3. If it has current violations, land it green with a time-boxed `waivers:` entry (owner + future
   `expires`).
4. Commit with a message explaining *why* — the commit is the rationale record.

See `governance/README.md` for the full reference and the proposal it implements.
