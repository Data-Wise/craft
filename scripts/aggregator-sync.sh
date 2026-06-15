#!/usr/bin/env bash
# scripts/aggregator-sync.sh — update one plugin's version in the Data-Wise
# aggregator marketplace.json (the single cross-plugin source of truth).
#
# The aggregator lists every Data-Wise plugin so Code/Desktop add it ONCE and
# receive all current + future plugins. Each plugin's release must update its
# own entry here, or the aggregator drifts from the per-repo marketplace.json
# (verify-surfaces guards this as the "aggregator" leg via --aggregator-file).
#
# Updates an EXISTING entry only — an unknown plugin is an error, never a
# silent add (adding a brand-new plugin to the aggregator is a deliberate,
# reviewed change, not a release side effect).
#
# Usage:
#   ./scripts/aggregator-sync.sh --file PATH --plugin NAME --version X.Y.Z
#   ./scripts/aggregator-sync.sh --file PATH --plugin NAME --version X.Y.Z --check
#
#   --check   Report whether the entry would change; write nothing.
#
# Exit codes: 0 = synced / already current, 1 = plugin not found in aggregator,
#             2 = usage error.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/formatting.sh" ]]; then
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/formatting.sh"
    RED="$FMT_RED"; GREEN="$FMT_GREEN"; YELLOW="$FMT_YELLOW"; NC="$FMT_NC"
else
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
fi

FILE=""; PLUGIN=""; VERSION=""; CHECK=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --file)    FILE="${2:-}"; shift ;;
        --plugin)  PLUGIN="${2:-}"; shift ;;
        --version) VERSION="${2:-}"; shift ;;
        --check)   CHECK=true ;;
        --help|-h)
            echo "Usage: $0 --file PATH --plugin NAME --version X.Y.Z [--check]"
            exit 0 ;;
        *) echo -e "${RED}Error: Unknown argument '$1'${NC}"; exit 2 ;;
    esac
    shift
done

[[ -z "$FILE" || -z "$PLUGIN" || -z "$VERSION" ]] && {
    echo -e "${RED}Error: --file, --plugin and --version are all required${NC}"; exit 2; }
[[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] && {
    echo -e "${RED}Error: --version must be X.Y.Z${NC}"; exit 2; }
[[ ! -f "$FILE" ]] && { echo -e "${RED}Error: aggregator file not found: $FILE${NC}"; exit 2; }

# All entry logic in Python (JSON-safe). Exit codes: 0 changed/current, 1 not found.
python3 - "$FILE" "$PLUGIN" "$VERSION" "$CHECK" <<'PY'
import json, sys

path, plugin, version, check = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] == "true"
data = json.load(open(path))
entry = next((p for p in data.get("plugins", []) if p.get("name") == plugin), None)

if entry is None:
    sys.stderr.write(f"plugin '{plugin}' not found in aggregator — refusing to silently add\n")
    sys.exit(1)

old = entry.get("version")
if old == version:
    print(f"[current] {plugin} already at {version}")
    sys.exit(0)

if check:
    print(f"[would-change] {plugin}: {old} -> {version}")
    sys.exit(0)

entry["version"] = version
with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
print(f"[synced] {plugin}: {old} -> {version}")
sys.exit(0)
PY
rc=$?

if [[ $rc -eq 0 ]]; then
    [[ "$CHECK" == true ]] && echo -e "${YELLOW}(check only — no file written)${NC}" || true
elif [[ $rc -eq 1 ]]; then
    echo -e "${RED}Aggregator does not list '${PLUGIN}'.${NC} Add it deliberately (reviewed change), not via release."
fi
exit $rc
