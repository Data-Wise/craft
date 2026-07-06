# /craft:dist:surfaces

Read-only view of the multi-surface release registry — verify gate states and inspect the plugin × surface version matrix.

## Usage

```bash
/craft:dist:surfaces                              # verify + full human matrix (default)
/craft:dist:surfaces --json                       # machine JSON matrix (live versions + states)
/craft:dist:surfaces --report-only                # diagnostic mode, never blocks (all 7 legs)
/craft:dist:surfaces --report-only --version v2.58.0   # diagnose a PAST release
```

## Arguments

| Argument | Description |
|----------|-------------|
| `--json` | Emit the surface matrix as machine JSON (live data, not raw registry schema) |
| `--report-only` | Never block — print ALIGNED/DRIFTED/ABSENT/WARN per surface (including the GitHub-release and docs-site legs below) and always exit 0. Runs `scripts/verify-surfaces.sh --report-only` directly, bypassing the registry-mapped 3-surface view. |
| `--version <X>` | Check surfaces against `<X>` instead of the current `plugin.json` version — diagnose a past release. Only meaningful alongside `--report-only`. |

## The 3-Surface Model

| Surface | Runtime | Gate | Propagation |
|---------|---------|------|-------------|
| **Code** | Claude Code CLI | BLOCK | Homebrew tap + GitHub marketplace |
| **Cowork** | Cowork platform | WARN | Manual (Cowork store update) |
| **Desktop** | Claude Desktop | INFO | Manual (DXT store; report only) |

A release is "fully shipped" when all BLOCK surfaces report the expected version.

`--report-only` additionally checks two informational legs as part of Code's aggregate:
**GitHub release** (is a release published for this version) and **docs site** (does the live
deployed site show this version) — both diagnostic-only, never block outside `--report-only`.

> The user-facing "3-surface" model collapses the 8 entries in `registry.json`:
> Code = {git-tag, marketplace, tap, brew, code-registered, aggregator}; Cowork = cowork; Desktop = desktop-ext.

## Output

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

Exit code 0 if all BLOCK surfaces aligned; exit 1 if any BLOCK surface mismatched.

## Related

- `/craft:code:release` — release pipeline (runs surfaces verification as a gate step)
- `scripts/surfaces/registry.json` — surface registry (source of truth)
- `skills/distribution/dist-extras/` — 3-surface model + propagation reference
- `docs/adr/ADR-004-release-surface-registry.md` — architecture decision
- [Release rollback runbook](../../runbooks/release-rollback.md) — manual per-surface undo steps for a bad release; `--report-only` is the diagnostic to run first
- [Tutorial: Multi-Surface Release Propagation](../../tutorials/TUTORIAL-dist-surfaces.md)
