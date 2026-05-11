---
name: check:version
description: Validate version string consistency across all Tier 1 files (13 files, plugin.json is source of truth)
category: validation
context: fork
hot_reload: true
version: 1.0.0
dependencies:
  - python3
  - scripts/bump-version.sh
---

# Version Sync Validator

Verify that the project's version string is consistent across the 13 Tier 1 files that `scripts/bump-version.sh` knows how to update. Catches drift introduced by manual edits, missed `--dry-run` previews, or merge conflicts that touch version strings outside the normal release pipeline.

## What This Checks

- **Source of truth**: `.claude-plugin/plugin.json` `version` field
- **Tier 1 files** (mechanically synced by `bump-version.sh`):
  - `plugin.json`, `marketplace.json`, `package.json`
  - `CLAUDE.md`, `README.md`, `docs/index.md`, `docs/REFCARD.md`
  - `mkdocs.yml`, `.STATUS`
  - `docs/DEPENDENCY-ARCHITECTURE.md`, `docs/reference/configuration.md`
  - `commands/hub.md`, `docs/commands/hub.md`

Tier 2 long-tail drift (example commands, REFCARD headers, brainstorm files) is **not** in scope — that's `scripts/post-release-sweep.sh`'s job. This validator catches the high-leverage drift before release.

## Mode Behavior

| Mode | What runs | Exit on drift |
|------|-----------|---------------|
| **default** | `bump-version.sh --verify` (13 Tier 1 files) | Warning only |
| **debug** | Same + per-file table | Warning only |
| **thorough** | Tier 1 + Tier 2 grep sweep | Warning only |
| **release** | Tier 1 + Tier 2 + count sweep | Exit 1 on drift |

## Implementation

```bash
#!/bin/bash
set -eo pipefail

# Find craft root robustly:
#   - if BASH_SOURCE is set (normal sourced/invoked case), walk up from the
#     skill file's directory
#   - if BASH_SOURCE is unset (script piped in via stdin, e.g. during testing),
#     walk up from $PWD until we find .claude-plugin/plugin.json
if [[ -n "${BASH_SOURCE[0]:-}" ]]; then
    CRAFT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
else
    CRAFT_ROOT="$PWD"
    while [[ "$CRAFT_ROOT" != "/" && ! -f "$CRAFT_ROOT/.claude-plugin/plugin.json" ]]; do
        CRAFT_ROOT="$(dirname "$CRAFT_ROOT")"
    done
fi

MODE="${CRAFT_MODE:-default}"

# Run the canonical verifier
output="$(bash "${CRAFT_ROOT}/scripts/bump-version.sh" --verify 2>&1 || true)"
exit_code=0
if echo "$output" | grep -q "INCONSISTENT\|drift\|FAILED"; then
    exit_code=1
fi

# Extract version + counts (best-effort)
current_version="$(python3 -c "import json; print(json.load(open('${CRAFT_ROOT}/.claude-plugin/plugin.json'))['version'])" 2>/dev/null || echo "?")"

# Format output per SPEC v2.33.0
if [[ "$exit_code" -eq 0 ]]; then
    cat <<EOF
╭─ /craft:check --version ────────────────────────╮
│ Project: craft (Claude Code Plugin)             │
│ Mode: ${MODE}                                    │
├─────────────────────────────────────────────────┤
│ Source of Truth:                                │
│   .claude-plugin/plugin.json → v${current_version}      │
│                                                 │
│ Tier 1 Files (13): ALL CONSISTENT ✓             │
│                                                 │
│ STATUS: PASS                                    │
├─────────────────────────────────────────────────┤
│ Tip: Use --thorough to also sweep Tier 2 refs   │
╰─────────────────────────────────────────────────╯
EOF
    exit 0
fi

# Drift detected — show the bump-version verbose output
echo "╭─ /craft:check --version ────────────────────────╮"
echo "│ Project: craft (Claude Code Plugin)             │"
echo "│ Mode: ${MODE}                                    │"
echo "├─────────────────────────────────────────────────┤"
echo "│ STATUS: DRIFT DETECTED                          │"
echo "├─────────────────────────────────────────────────┤"
echo "$output" | sed 's/^/│ /'
echo "├─────────────────────────────────────────────────┤"
echo "│ Fix: ./scripts/bump-version.sh v${current_version}     │"
echo "╰─────────────────────────────────────────────────╯"

# In release mode, drift is fatal
if [[ "$MODE" == "release" ]]; then
    exit 1
fi
exit 0  # warn only in other modes
```

## Example Output

### Pass

```
╭─ /craft:check --version ────────────────────────╮
│ Project: craft (Claude Code Plugin)             │
│ Mode: default                                   │
├─────────────────────────────────────────────────┤
│ Source of Truth:                                │
│   .claude-plugin/plugin.json → v2.33.0          │
│                                                 │
│ Tier 1 Files (13): ALL CONSISTENT ✓             │
│                                                 │
│ STATUS: PASS                                    │
├─────────────────────────────────────────────────┤
│ Tip: Use --thorough to also sweep Tier 2 refs   │
╰─────────────────────────────────────────────────╯
```

### Drift Detected

```
╭─ /craft:check --version ────────────────────────╮
│ Project: craft (Claude Code Plugin)             │
│ Mode: default                                   │
├─────────────────────────────────────────────────┤
│ STATUS: DRIFT DETECTED                          │
├─────────────────────────────────────────────────┤
│ Inconsistent version strings:
│   plugin.json:        v2.33.0
│   CLAUDE.md:          v2.32.1   ← stale
│   docs/REFCARD.md:    v2.32.1   ← stale
├─────────────────────────────────────────────────┤
│ Fix: ./scripts/bump-version.sh v2.33.0          │
╰─────────────────────────────────────────────────╯
```

## Integration with /craft:check

Auto-included when:

- `/craft:check --version` (explicit invocation)
- `/craft:check --for pr` (version drift would break the release PR)
- `/craft:check --for release` (drift is fatal in this context)

Manually invokable in any context:

```bash
/craft:check --version              # Tier 1 only, warn on drift
/craft:check --version thorough     # Tier 1 + Tier 2 sweep
/craft:check --version release      # Exit 1 on any drift (CI gating)
```

## Hot-Reload Behavior

- Auto-discovered by `/craft:check` (no command file edit needed)
- Picks up new Tier 1 files automatically — `bump-version.sh` is the source of truth for the file list
- Mode-aware: default warns, release exits 1

## See Also

- `scripts/bump-version.sh --verify` — the underlying mechanical check
- `scripts/post-release-sweep.sh` — Tier 2/3 drift after release
- `docs/reference/REFCARD-BUMP-VERSION.md` — bump-version.sh quick reference
- `/craft:check --for release` — full pre-release validation including this
