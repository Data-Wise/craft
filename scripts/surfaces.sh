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
#   surfaces.sh --propagate [aggregator] [--check] [--file PATH]
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
  # Propagate the current plugin version to each release surface.
  # Currently supports: aggregator (Data-Wise/claude-plugins marketplace.json).
  #
  # Usage:
  #   surfaces.sh --propagate [aggregator] [--check] [--file PATH]
  #
  #   aggregator   Sync version into the aggregator marketplace.json via aggregator-sync.sh.
  #   --check      Dry-run: report what would change without writing (delegates to --check).
  #   --file PATH  Path to the aggregator marketplace.json (overrides SURFACES_AGGREGATOR_FILE).
  #
  # Env overrides:
  #   SURFACES_AGGREGATOR_FILE  Path to aggregator marketplace.json (same var as verify-surfaces.sh).

  local surface="" check=false agg_file=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      aggregator) surface="aggregator" ;;
      --check)    check=true ;;
      --file)     [[ -z "${2:-}" || "$2" == --* ]] && { echo "surfaces.sh: --file requires a value" >&2; exit 2; }
                  agg_file="$2"; shift ;;
      *) echo "surfaces.sh --propagate: unknown argument '$1'" >&2; exit 2 ;;
    esac
    shift
  done

  # Default surface to aggregator if none specified (only surface supported so far).
  surface="${surface:-aggregator}"

  case "$surface" in
    aggregator)
      # Resolve aggregator file: --file flag > env var > error.
      local file="${agg_file:-${SURFACES_AGGREGATOR_FILE:-}}"
      if [[ -z "$file" ]]; then
        echo "surfaces.sh --propagate aggregator: --file PATH or SURFACES_AGGREGATOR_FILE required" >&2
        exit 2
      fi

      # Extract plugin name + version from plugin.json in SURFACES_REPO_DIR.
      local repo_dir="${SURFACES_REPO_DIR:-$(cd "${SCRIPT_DIR}/.." && pwd)}"
      local plugin_json="${repo_dir}/.claude-plugin/plugin.json"
      if [[ ! -f "$plugin_json" ]]; then
        echo "surfaces.sh: plugin.json not found at $plugin_json" >&2
        exit 1
      fi
      local plugin version
      plugin=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d['name'])" "$plugin_json")
      version=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d['version'])" "$plugin_json")

      local sync_args=(--file "$file" --plugin "$plugin" --version "$version")
      [[ "$check" == "true" ]] && sync_args+=(--check)

      exec bash "${SCRIPT_DIR}/aggregator-sync.sh" "${sync_args[@]}"
      ;;
    *)
      echo "surfaces.sh --propagate: unknown surface '$surface'" >&2
      exit 2
      ;;
  esac
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
