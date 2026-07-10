#!/usr/bin/env bash
# scripts/cowork-recover.sh — one-shot diagnosis + recovery guidance for a
# drifted Cowork/Claude Desktop plugin install.
#
# There is no scriptable update path for Cowork/Desktop's plugin installer
# (craft#199) — its in-app "Update" reliably no-ops when the marketplace
# clone has gone stale, and no CLI/API surface has ever been found to drive
# it from outside the app. This script does the one thing that IS scriptable
# — diagnose exactly how far behind the install is — then hands off the
# unavoidable manual steps instead of leaving you to re-derive them each time.
#
# Usage:
#   ./scripts/cowork-recover.sh              # diagnose the plugin repo at $PWD
#   ./scripts/cowork-recover.sh <repo-dir>   # diagnose the plugin repo at <repo-dir>
#
# Exit codes: 0 = aligned or no Cowork store found (nothing to do),
#             1 = drift found (recovery steps printed), 2 = usage/lookup error.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERIFY_SCRIPT="$SCRIPT_DIR/verify-surfaces.sh"
export SURFACES_REPO_DIR="${1:-$PWD}"

if [[ -f "$SCRIPT_DIR/formatting.sh" ]]; then
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/formatting.sh"
    RED="$FMT_RED"; GREEN="$FMT_GREEN"; YELLOW="$FMT_YELLOW"; CYAN="$FMT_CYAN"; NC="$FMT_NC"
else
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
fi

if [[ ! -x "$VERIFY_SCRIPT" && ! -f "$VERIFY_SCRIPT" ]]; then
    echo -e "${RED}Error:${NC} verify-surfaces.sh not found beside this script at $VERIFY_SCRIPT"
    exit 2
fi

REPORT="$(bash "$VERIFY_SCRIPT" --json --report-only 2>&1)"
if ! printf '%s' "$REPORT" | python3 -c "import sys,json; json.load(sys.stdin)" >/dev/null 2>&1; then
    echo -e "${RED}Error:${NC} verify-surfaces.sh did not return valid JSON:"
    echo "$REPORT"
    exit 2
fi

# Parse via stdin (not string-interpolated into a python literal) so the JSON
# payload can never break out of a quoted string.
PARSED="$(printf '%s' "$REPORT" | python3 -c '
import json, sys
d = json.load(sys.stdin)
if not d.get("applicable", True):
    print("__NOT_APPLICABLE__ - - - -")
    sys.exit(0)
name = d.get("plugin", "-")
sot = d.get("version", "-")
leg = next((l for l in d.get("legs", []) if l.get("surface") == "cowork"), None)
if leg is None:
    print(f"{name} __NO_LEG__ - - {sot}")
else:
    state = leg.get("state", "-")
    ver = leg.get("version") or "-"
    behind = leg.get("releasesBehind")
    behind_out = str(behind) if behind is not None else "-"
    print(f"{name} {state} {ver} {behind_out} {sot}")
')"
read -r PLUGIN_NAME COWORK_STATE COWORK_VERSION COWORK_BEHIND SOT_VERSION <<<"$PARSED"

if [[ "$PLUGIN_NAME" == "__NOT_APPLICABLE__" ]]; then
    echo -e "${YELLOW}cowork-recover:${NC} no .claude-plugin/plugin.json here — nothing to diagnose."
    exit 0
fi

echo -e "${CYAN}Cowork/Desktop install check for ${PLUGIN_NAME}${NC} (canon: v${SOT_VERSION})"

case "$COWORK_STATE" in
    ok)
        echo -e "${GREEN}Aligned${NC} — Cowork's installed version (v${COWORK_VERSION}) matches canon. Nothing to do."
        exit 0
        ;;
    absent|"__NO_LEG__")
        echo -e "${YELLOW}No Cowork store found on this machine${NC} — nothing to recover."
        exit 0
        ;;
    warn)
        behind_note=""
        [[ "$COWORK_BEHIND" != "-" ]] && behind_note=" (${COWORK_BEHIND} release(s) behind)"
        echo -e "${RED}Drifted${NC} — Cowork has v${COWORK_VERSION}, canon is v${SOT_VERSION}${behind_note}."
        echo ""
        echo "There is no scriptable fix for this (craft#199) — the in-app 'Update' reliably"
        echo "no-ops once the marketplace clone has gone stale. Recovery is manual, in the app:"
        echo ""
        echo "  1. Open Claude Desktop → Plugins → find ${PLUGIN_NAME}."
        echo "  2. Uninstall it (NOT 'Update' — that's the path that no-ops)."
        echo "  3. Reinstall it from its marketplace."
        echo "  4. Fully quit the app: Cmd-Q (an in-app restart is not enough)."
        echo "  5. Relaunch, then re-run this script to confirm the drift cleared."
        exit 1
        ;;
    *)
        echo -e "${YELLOW}Unrecognized state '${COWORK_STATE}'${NC} — run 'verify-surfaces.sh --json --report-only' directly to inspect."
        exit 2
        ;;
esac
