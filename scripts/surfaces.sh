#!/usr/bin/env bash
# surfaces.sh — surface registry driver for the craft release pipeline.
#
# Wraps verify-surfaces.sh for the --verify mode; delegates JSON-heavy logic
# to scripts/surfaces/registry.py. Does NOT re-implement resolver logic.
#
# Usage:
#   surfaces.sh --verify    Run verify-surfaces.sh (wrapped, exit code preserved)
#   surfaces.sh --report    Emit the full surface matrix via registry.py
#   surfaces.sh --json      Dump the raw registry.json
#   surfaces.sh --propagate [--dry-run]  (stub — implemented in Task 3)
#   surfaces.sh --list      List surface names from registry
#   surfaces.sh --help      Show this help
#
# SURFACES_* injectable overrides (passed through to verify-surfaces.sh):
#   SURFACES_GIT_TAG, SURFACES_TAP_FORMULA, SURFACES_BREW_VERSION,
#   SURFACES_INSTALLED_PLUGINS, SURFACES_REPO_DIR, SURFACES_AGGREGATOR_FILE
#
# Exit codes (inherited from verify-surfaces.sh for --verify):
#   0 — all BLOCK surfaces aligned (or absent)
#   1 — at least one BLOCK surface mismatched
#   2 — usage error

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY_JSON="${SCRIPT_DIR}/surfaces/registry.json"
REGISTRY_PY="${SCRIPT_DIR}/surfaces/registry.py"
VERIFY_SCRIPT="${SCRIPT_DIR}/verify-surfaces.sh"

usage() {
  grep '^#' "$0" | sed 's/^# \{0,1\}//' | grep -v '^!'
  exit "${1:-0}"
}

cmd_verify() {
  # Wrap verify-surfaces.sh — pass all SURFACES_* overrides via env inheritance.
  # Exit code is preserved (0, 1, or 2) so the release pipeline gates correctly.
  exec bash "${VERIFY_SCRIPT}" "$@"
}

cmd_report() {
  python3 "${REGISTRY_PY}" report
}

cmd_json() {
  cat "${REGISTRY_JSON}"
}

cmd_list() {
  python3 "${REGISTRY_PY}" list
}

cmd_propagate() {
  # Stub — full implementation in Task 3 (aggregator CI action + pin-refresh).
  local dry_run=false
  for arg in "$@"; do
    [[ "$arg" == "--dry-run" ]] && dry_run=true
  done

  if [[ "$dry_run" == "true" ]]; then
    echo "[surfaces.sh] --propagate --dry-run: no-op stub (Task 3)" >&2
  else
    echo "[surfaces.sh] --propagate: not yet implemented (Task 3)" >&2
    exit 1
  fi
}

# ── Argument dispatch ─────────────────────────────────────────────────────────
if [[ $# -eq 0 ]]; then
  usage 2
fi

case "$1" in
  --verify)    shift; cmd_verify "$@" ;;
  --report)    shift; cmd_report "$@" ;;
  --json)      shift; cmd_json "$@" ;;
  --list)      shift; cmd_list "$@" ;;
  --propagate) shift; cmd_propagate "$@" ;;
  --help|-h)   usage 0 ;;
  *)
    echo "surfaces.sh: unknown option $1" >&2
    usage 2
    ;;
esac
