---
description: Read-only view of the multi-surface release registry — verify gate states and inspect the plugin × surface version matrix
category: dist
arguments:
  - name: json
    description: Emit the surface matrix as machine JSON instead of the formatted human report
    required: false
---

# /craft:dist:surfaces — Surface Registry View

Read-only view of the craft surface registry. Runs `scripts/surfaces.sh --report` and presents
the full surface matrix: every registered surface × version × gate state. No `--propagate` — this
command never writes or pins; see the `dist-extras` skill for propagation workflows.

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

## Quick Start

```bash
# Default — verify + full human matrix
/craft:dist:surfaces

# Machine-readable JSON matrix
/craft:dist:surfaces --json
```

## Execution Steps

1. **Parse arguments** — detect `--json` flag.
2. **Run surfaces.sh** — call `scripts/surfaces.sh` with the appropriate flags:
   - Default: `scripts/surfaces.sh --report`
   - With `--json`: `scripts/surfaces.sh --report --json`
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

## Integration

| Command / Skill | Relationship |
|-----------------|-------------|
| `/craft:code:release` | Release pipeline — runs surfaces verification as a gate step |
| `/craft:dist:marketplace` | Marketplace distribution (Code surface) |
| `/craft:dist:homebrew` | Homebrew formula (Code surface) |
| `skills/distribution/dist-extras/` | Propagation workflows for Cowork + Desktop surfaces |

## See Also

- `scripts/surfaces.sh` — underlying driver (`--verify`, `--report`, `--report --json`, `--json`, `--list`)
- `scripts/surfaces/registry.json` — surface registry (source of truth)
- `/craft:dist:marketplace` — marketplace distribution
- `/craft:dist:homebrew` — Homebrew formula automation
- `skills/distribution/dist-extras/` — dist-extras skill (propagation + advanced surface ops)
