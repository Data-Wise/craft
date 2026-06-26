---
description: Read-only view of the multi-surface release registry — verify gate states and inspect the plugin × surface version matrix
category: dist
arguments:
  - name: json
    description: Dump the raw registry.json instead of the formatted report
    required: false
  - name: owner
    description: "Filter by plugin owner (e.g. Data-Wise) — only rows matching this owner are shown"
    required: false
---

# /craft:dist:surfaces — Surface Registry View

Read-only view of the craft surface registry. Runs `scripts/surfaces.sh --verify --report`
and presents the full surface matrix: every registered plugin × surface × version, with gate
states. No `--propagate` — this command never writes or pins; see `/craft:dist:pypi` and the
`dist-extras` skill for propagation workflows.

## The 3-Surface Model

| Surface | Runtime | Distribution channel |
|---------|---------|----------------------|
| **Code** | Claude Code CLI | Homebrew tap + GitHub marketplace |
| **Cowork** | Cowork platform | Cowork plugin registry |
| **Desktop** | Claude Desktop app | Desktop plugin store |

Each surface tracks an independent version pin. A release is "fully shipped" when all
BLOCK-gated surfaces report the expected version. Advisory surfaces (WARN) are surfaced
in the report but do not gate the release pipeline.

## Quick Start

```bash
# Default — verify + full matrix
/craft:dist:surfaces

# Raw JSON (pipe-friendly)
/craft:dist:surfaces --json

# Filter to one owner
/craft:dist:surfaces --owner Data-Wise
```

## Execution Steps

1. **Parse arguments** — detect `--json` and `--owner` flags.
2. **Run surfaces.sh** — call `scripts/surfaces.sh` with the appropriate flags:
   - Default: `scripts/surfaces.sh --verify --report`
   - With `--json`: `scripts/surfaces.sh --json`
   - With `--owner OWNER`: pipe report output through an owner filter
3. **Present surface matrix** — display the table returned by `registry.py report`:

```
Surface Matrix (craft vX.Y.Z)
──────────────────────────────────────────────────────
Plugin          Surface     Version    Gate   Status
──────────────────────────────────────────────────────
craft           Code        2.52.0     BLOCK  ✓ aligned
craft           Cowork      2.52.0     BLOCK  ✓ aligned
craft           Desktop     2.52.0     WARN   ✓ aligned
──────────────────────────────────────────────────────
Gate result: ALL BLOCK surfaces aligned
```

4. **Report gate result** — summarise pass/fail. Exit 0 if all BLOCK surfaces aligned;
   exit 1 if any BLOCK surface mismatched (mirrors `verify-surfaces.sh` exit codes).

### With `--json`

Dumps the raw `scripts/surfaces/registry.json` content directly to stdout.
Useful for piping into `jq` or other tooling.

### With `--owner OWNER`

Filters the matrix to rows whose `owner` field matches OWNER (case-insensitive substring).
Useful in multi-plugin registries to inspect a single vendor's surfaces.

## Output Format

```
┌──────────────────────────────────────────────────────────────┐
│ /craft:dist:surfaces                                         │
├──────────────────────────────────────────────────────────────┤
│ Plugin: craft  Version: 2.52.0                               │
│ Surfaces checked: 3 (2 BLOCK, 1 WARN)                        │
├──────────────────────────────────────────────────────────────┤
│ Code    ............... 2.52.0  BLOCK  ✓ aligned             │
│ Cowork  ............... 2.52.0  BLOCK  ✓ aligned             │
│ Desktop ............... 2.52.0  WARN   ✓ aligned             │
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
│ Code    ............... 2.52.0  BLOCK  ✓ aligned             │
│ Cowork  ............... 2.51.0  BLOCK  ✗ MISMATCH            │
│ Desktop ............... 2.52.0  WARN   ✓ aligned             │
├──────────────────────────────────────────────────────────────┤
│ Gate: FAILED — 1 BLOCK surface misaligned                    │
│ Run /craft:code:release to propagate the missing pin.        │
└──────────────────────────────────────────────────────────────┘
```

## Integration

| Command / Skill | Relationship |
|-----------------|-------------|
| `/craft:code:release` | Release pipeline — runs surfaces verification as a gate step |
| `/craft:dist:marketplace` | Marketplace distribution (Code surface) |
| `/craft:dist:homebrew` | Homebrew formula (Code surface) |
| `skills/distribution/dist-extras/` | Propagation workflows for Cowork + Desktop surfaces |

## See Also

- `scripts/surfaces.sh` — underlying driver (`--verify`, `--report`, `--json`, `--list`)
- `scripts/surfaces/registry.json` — surface registry (source of truth)
- `/craft:dist:marketplace` — marketplace distribution
- `/craft:dist:homebrew` — Homebrew formula automation
- `skills/distribution/dist-extras/` — dist-extras skill (propagation + advanced surface ops)
