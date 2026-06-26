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
#   surfaces.sh --propagate [aggregator|brew|code-registered] [--check] [--file PATH]
#   surfaces.sh --list      List surface names from registry
#   surfaces.sh --help      Show this help
#
# SURFACES_* injectable overrides (passed through to verify-surfaces.sh):
#   SURFACES_GIT_TAG, SURFACES_TAP_FORMULA, SURFACES_BREW_VERSION,
#   SURFACES_INSTALLED_PLUGINS, SURFACES_REPO_DIR, SURFACES_AGGREGATOR_FILE,
#   SURFACES_BREW_CMD (default: brew), SURFACES_CLAUDE_CMD (default: claude)
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
  # Supports: aggregator, brew (advisory), code-registered (advisory).
  #
  # Usage:
  #   surfaces.sh --propagate [aggregator|brew|code-registered] [--check] [--file PATH]
  #
  #   aggregator        Sync version into the aggregator marketplace.json via aggregator-sync.sh.
  #   brew              Advisory: run brew upgrade data-wise/tap/<name> --formula post-release.
  #   code-registered   Advisory: run marketplace update then plugin update (in that order).
  #   --check           Dry-run: report what would change without writing or running.
  #   --file PATH       Path to the aggregator marketplace.json (overrides SURFACES_AGGREGATOR_FILE).
  #
  # Advisory surfaces (brew, code-registered) are WARN-gated: they NEVER exit 1.
  # If the required binary is absent or the command fails, the exact recovery commands
  # are printed to stderr and the script continues with exit 0.
  #
  # Env overrides:
  #   SURFACES_AGGREGATOR_FILE  Path to aggregator marketplace.json.
  #   SURFACES_BREW_CMD         Override the brew binary (default: brew). For testing.
  #   SURFACES_CLAUDE_CMD       Override the claude binary (default: claude). For testing.

  local surface="" check=false agg_file=""
  # Advisory binary overrides — tests inject /nonexistent to simulate absent binaries.
  local brew_cmd="${SURFACES_BREW_CMD:-brew}"
  local claude_cmd="${SURFACES_CLAUDE_CMD:-claude}"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      aggregator)       surface="aggregator" ;;
      brew)             surface="brew" ;;
      code-registered)  surface="code-registered" ;;
      --check)          check=true ;;
      --file)           [[ -z "${2:-}" || "$2" == --* ]] && { echo "surfaces.sh: --file requires a value" >&2; exit 2; }
                        agg_file="$2"; shift ;;
      *) echo "surfaces.sh --propagate: unknown argument '$1'" >&2; exit 2 ;;
    esac
    shift
  done

  # Default surface to aggregator if none specified (preserves backward compat).
  surface="${surface:-aggregator}"

  # Resolve plugin name from plugin.json (needed by all surfaces).
  local repo_dir="${SURFACES_REPO_DIR:-$(cd "${SCRIPT_DIR}/.." && pwd)}"
  local plugin_json="${repo_dir}/.claude-plugin/plugin.json"
  local plugin="craft"  # safe default; overridden below when plugin.json exists
  if [[ -f "$plugin_json" ]]; then
    plugin=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d['name'])" "$plugin_json") || plugin="craft"
  fi

  case "$surface" in
    aggregator)
      # Resolve aggregator file: --file flag > env var > error.
      local file="${agg_file:-${SURFACES_AGGREGATOR_FILE:-}}"
      if [[ -z "$file" ]]; then
        echo "surfaces.sh --propagate aggregator: --file PATH or SURFACES_AGGREGATOR_FILE required" >&2
        exit 2
      fi

      # Extract version from plugin.json (required for aggregator sync).
      if [[ ! -f "$plugin_json" ]]; then
        echo "surfaces.sh: plugin.json not found at $plugin_json" >&2
        exit 1
      fi
      local version
      version=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d['version'])" "$plugin_json")

      local sync_args=(--file "$file" --plugin "$plugin" --version "$version")
      [[ "$check" == "true" ]] && sync_args+=(--check)

      exec bash "${SCRIPT_DIR}/aggregator-sync.sh" "${sync_args[@]}"
      ;;

    brew)
      # Advisory: post-release brew upgrade. WARN only — NEVER exits 1.
      local brew_formula="data-wise/tap/${plugin}"
      local brew_upgrade_cmd="brew upgrade ${brew_formula} --formula"

      if [[ "$check" == "true" ]]; then
        echo "[check] would run: ${brew_upgrade_cmd}"
        exit 0
      fi

      if command -v "$brew_cmd" >/dev/null 2>&1 && "$brew_cmd" upgrade "${brew_formula}" --formula; then
        echo "brew surface refreshed: ${brew_formula}"
      else
        echo "[WARN] Could not refresh brew surface automatically." >&2
        echo "       Run manually: ${brew_upgrade_cmd}" >&2
      fi
      exit 0
      ;;

    code-registered)
      # Advisory: marketplace update THEN plugin update (order is critical).
      # WARN only — NEVER exits 1.
      local mkt="local-plugins"
      local mkt_update_cmd="claude plugin marketplace update ${mkt}"
      local plugin_update_cmd="claude plugin update ${plugin}@${mkt}"

      if [[ "$check" == "true" ]]; then
        echo "[check] would run: ${mkt_update_cmd}"
        echo "[check] would run: ${plugin_update_cmd}"
        exit 0
      fi

      if command -v "$claude_cmd" >/dev/null 2>&1; then
        # marketplace update FIRST (post-install-marketplace-refresh-before-update).
        if "$claude_cmd" plugin marketplace update "${mkt}" && \
           "$claude_cmd" plugin update "${plugin}@${mkt}"; then
          echo "code-registered surface refreshed: ${plugin}@${mkt}"
        else
          echo "[WARN] Could not refresh code-registered surface automatically." >&2
          echo "       Run manually:" >&2
          echo "         ${mkt_update_cmd}" >&2
          echo "         ${plugin_update_cmd}" >&2
        fi
      else
        echo "[WARN] claude binary not found. Run manually:" >&2
        echo "         ${mkt_update_cmd}" >&2
        echo "         ${plugin_update_cmd}" >&2
      fi
      exit 0
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
