---
description: Read-only view of the multi-surface release registry — verify gate states and inspect the plugin × surface version matrix
category: dist
arguments:
  - name: json
    description: Emit the surface matrix as machine JSON instead of the formatted human report
    required: false
  - name: report-only
    description: Never block — print ALIGNED/DRIFTED/ABSENT/WARN per surface (including the 2 informational legs below) and always exit 0. Pass-through to `scripts/verify-surfaces.sh --report-only` via `scripts/surfaces.sh --verify`.
    required: false
  - name: version
    description: Check surfaces against this version instead of the current `plugin.json` version — diagnose a past release (e.g. `--version v2.58.0`). Pass-through to `scripts/verify-surfaces.sh --version`.
    required: false
---

# /craft:dist:surfaces — Surface Registry View

Read-only view of the craft surface registry. Runs `scripts/surfaces.sh --report` and presents
the full surface matrix: every registered surface × version × gate state. No `--propagate` — this
command never writes or pins; see the `dist-extras` skill for propagation workflows.

> **`--report-only` and `--version`** run the underlying `scripts/verify-surfaces.sh` directly
> (via `scripts/surfaces.sh --verify --report-only [--version X]`) rather than through
> `--report`'s registry-mapped 3-surface view — this is the only path that currently carries the
> 2 new legs below (GitHub release, docs site) and the never-block diagnostic mode. `--report`
> (no flags) is unaffected and keeps its existing registry-mapped output.

> **Note:** The user-facing "3-surface" model (Code / Cowork / Desktop) collapses the 8 entries
> in `registry.json` into three logical surfaces. Code aggregates git-tag, marketplace, tap, brew,
> code-registered, and aggregator; Cowork maps to the cowork surface; Desktop maps to desktop-ext.

## The 3-Surface Model

| Surface | Runtime | Gate | Distribution channel |
|---------|---------|------|----------------------|
| **Code** | Claude Code CLI | BLOCK | Homebrew tap + GitHub marketplace |
| **Cowork** | Cowork platform | WARN | Cowork plugin registry (manual update) |
| **Desktop** | Claude Desktop app | INFO | Desktop plugin store (report only) |

Each surface tracks an independent version pin. A release is "fully shipped" when all
BLOCK-gated surfaces report the expected version. Advisory surfaces (WARN, INFO) are surfaced
in the report but do not gate the release pipeline.

**Two additional legs** (M1/M10) are checked as part of the Code surface's aggregate: **GitHub
release** (is a release published for this version — `gh release list`) and **docs site** (does
the live deployed docs site show this version — reuses the same live-site poll `.github/workflows/docs.yml`
already runs post-deploy). Both follow the same BLOCK-on-mismatch / WARN-on-absent contract as
the other Code-surface legs.

## Quick Start

```bash
# Default — verify + full human matrix
/craft:dist:surfaces

# Machine-readable JSON matrix
/craft:dist:surfaces --json

# Diagnostic mode — never blocks, prints ALIGNED/DRIFTED per surface (all 7 legs)
/craft:dist:surfaces --report-only

# Diagnose a PAST release instead of the current plugin.json version
/craft:dist:surfaces --report-only --version v2.58.0
```

## Execution Steps

1. **Parse arguments** — detect `--json`, `--report-only`, and `--version <X>` flags.
2. **Run surfaces.sh** — call `scripts/surfaces.sh` with the appropriate flags:
   - Default: `scripts/surfaces.sh --report`
   - With `--json`: `scripts/surfaces.sh --report --json`
   - With `--report-only` and/or `--version`: `scripts/surfaces.sh --verify --report-only [--version X]`
     (pass-through to `scripts/verify-surfaces.sh`; bypasses the `--report` registry collapse so
     the GitHub-release and docs-site legs and the never-block diagnostic mode are visible)
3. **Present surface matrix** — display the table from `registry.py report-live`:

```
Surface Matrix (craft vX.Y.Z)
──────────────────────────────────────────────────────
Plugin          Surface     Version    Gate   Status
──────────────────────────────────────────────────────
craft           Code        2.52.0     BLOCK  ✓ aligned
craft           Cowork      2.52.0     WARN   ✓ aligned
craft           Desktop     2.52.0     INFO   ✓ aligned
──────────────────────────────────────────────────────
Gate result: ALL BLOCK surfaces aligned
```

4. **Report gate result** — summarise pass/fail. Exit 0 if all BLOCK surfaces aligned;
   exit 1 if any BLOCK surface mismatched (mirrors `verify-surfaces.sh` exit codes).

### With `--json`

Emits the real surface matrix as structured JSON — versions and states populated from
`verify-surfaces.sh`, gates from `registry.json`. Useful for piping into `jq` or other tooling.
This is distinct from the bare `--json` flag on `surfaces.sh` (which dumps the raw registry
schema); `--report --json` gives live data.

## Output Format

```
┌──────────────────────────────────────────────────────────────┐
│ /craft:dist:surfaces                                         │
├──────────────────────────────────────────────────────────────┤
│ Plugin: craft  Version: 2.52.0                               │
│ Surfaces checked: 3 (2 BLOCK, 1 WARN)                        │
├──────────────────────────────────────────────────────────────┤
│ Code    ............... 2.52.0  BLOCK  ✓ aligned             │
│ Cowork  ............... 2.52.0  WARN   ✓ aligned             │
├──────────────────────────────────────────────────────────────┤
│ Gate: PASSED — all BLOCK surfaces aligned                    │
└──────────────────────────────────────────────────────────────┘
```

On mismatch:

```
┌──────────────────────────────────────────────────────────────┐
│ /craft:dist:surfaces                                         │
├──────────────────────────────────────────────────────────────┤
│ Plugin: craft  Version: 2.52.0                               │
│ Surfaces checked: 3 (2 BLOCK, 1 WARN)                        │
├──────────────────────────────────────────────────────────────┤
│ Code    ............... 2.51.0  BLOCK  ✗ MISMATCH            │
│ Cowork  ............... 2.52.0  WARN   ✓ aligned             │
├──────────────────────────────────────────────────────────────┤
│ Gate: FAILED — at least one BLOCK surface misaligned         │
│ Run /craft:code:release to propagate the missing pin.        │
└──────────────────────────────────────────────────────────────┘
```

### With `--report-only` (raw legs, never blocks)

```
Surfaces for craft v2.60.0
  [OK] plugin.json      2.60.0  (source of truth)
  [OK] marketplace      2.60.0
  [OK] git tag          2.60.0
  [OK] tap formula      2.60.0
  [OK] brew-installed   2.60.0
  [OK] Code-registered  2.60.0
  [X ] github release   2.59.0  <- MISMATCH (blocks release)
  [!] docs site         N/A  (unreadable — not verified)
  [!] Desktop/Cowork    manual — add once: claude plugin marketplace add Data-Wise/craft

BLOCKED — a craft-controlled surface disagrees with plugin.json (v2.60.0).

--report-only (never blocks):
  marketplace      ALIGNED
  git tag          ALIGNED
  tap formula      ALIGNED
  brew-installed   ALIGNED
  Code-registered  ALIGNED
  github release   DRIFTED
  docs site        ABSENT
  cowork           ALIGNED
```

Exit code is always `0` in `--report-only` mode, even though the `github release` leg drifted —
this is the diagnostic surfaced by `/craft:dist:surfaces --report-only` for a release
post-mortem or a rollback check, without failing a calling pipeline.

## Integration

| Command / Skill | Relationship |
|-----------------|-------------|
| `/craft:code:release` | Release pipeline — runs surfaces verification as a gate step |
| `/craft:dist:marketplace` | Marketplace distribution (Code surface) |
| `/craft:dist:homebrew` | Homebrew formula (Code surface) |
| `skills/distribution/dist-extras/` | Propagation workflows for Cowork + Desktop surfaces |

## See Also

- `scripts/surfaces.sh` — underlying driver (`--verify`, `--report`, `--report --json`, `--json`, `--list`)
- `scripts/verify-surfaces.sh` — the 7-leg resolver (`--report-only`, `--version X`); see its
  header comment for the full `SURFACES_*` env-var override list
- `scripts/surfaces/registry.json` — surface registry (source of truth)
- `/craft:dist:marketplace` — marketplace distribution
- `/craft:dist:homebrew` — Homebrew formula automation
- `skills/distribution/dist-extras/` — dist-extras skill (propagation + advanced surface ops)
