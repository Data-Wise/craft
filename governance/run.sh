#!/usr/bin/env bash
# Cross-repo entrypoint for the governance engine.
#
# Consumers (savant, scholar, …) do NOT vendor a copy of governance/ — they invoke
# the ONE installed craft plugin's engine through this wrapper, so there is exactly
# one copy and no drift (matches R07-version-is-truth). The engine itself is
# __file__-relative, so this resolves its own directory and runs run_rules.py from
# there regardless of the caller's cwd.
#
# Usage (from any repo): <craft-plugin-root>/governance/run.sh [run_rules.py args]
#   e.g.  /path/to/craft/governance/run.sh --selftest
#         /path/to/craft/governance/run.sh --target ~/.claude/skills --json
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$HERE/run_rules.py" "$@"
