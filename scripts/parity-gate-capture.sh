#!/usr/bin/env bash
# Capture one leg of a parity gate pair after an orchestrate run completes.
#
# Usage:
#   ./scripts/parity-gate-capture.sh <pair_number> <engine> <marker_file>
#
#   pair_number   1-5
#   engine        fanout | workflow
#   marker_file   path to .craft/orchestrate-runs/<run-id>.json

set -euo pipefail

PAIR="${1:-}"
ENGINE="${2:-}"
MARKER="${3:-}"

if [[ -z "$PAIR" || -z "$ENGINE" || -z "$MARKER" ]]; then
    echo "Usage: $0 <pair_number> <engine> <marker_file>" >&2
    exit 1
fi

if [[ ! "$ENGINE" =~ ^(fanout|workflow)$ ]]; then
    echo "engine must be 'fanout' or 'workflow'" >&2
    exit 1
fi

if [[ ! -f "$MARKER" ]]; then
    echo "marker file not found: $MARKER" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

OUT="$REPO_ROOT/.craft/parity-gate-results/pair_${PAIR}/${ENGINE}.json"
mkdir -p "$(dirname "$OUT")"

python3 "$SCRIPT_DIR/orchestrate-token-report.py" "$MARKER" --json > "$OUT"
echo "Captured pair $PAIR / $ENGINE → $OUT"
python3 "$SCRIPT_DIR/orchestrate-token-report.py" "$MARKER"
