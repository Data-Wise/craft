#!/bin/bash
# install-hard-deny.sh - Install craft's hard_deny rules into ~/.claude/settings.json
#
# Reads scripts/hard-deny-rules.json (the canonical rule catalog), filters to
# entries with category == "hard_deny", merges the prose rule strings into
# settings.autoMode.hard_deny, prepending "$defaults" if absent. Preserves any
# user-added entries already present. Idempotent.
#
# Usage:
#   ./install-hard-deny.sh                  # --check (default): show what would change
#   ./install-hard-deny.sh --check          # explicit check mode
#   ./install-hard-deny.sh --install        # apply the merge
#   ./install-hard-deny.sh --show           # print current ~/.claude/settings.json autoMode.hard_deny
#   ./install-hard-deny.sh --uninstall      # remove ONLY craft's rules (preserves user entries + $defaults)
#   ./install-hard-deny.sh --json           # emit structured JSON on stdout (combine with --check or --show)
#
# Exit codes:
#   0  success / no changes needed
#   1  generic error
#   2  invalid arguments
#   3  catalog file missing or malformed

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
CRAFT_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)
CATALOG="$CRAFT_ROOT/scripts/hard-deny-rules.json"
SETTINGS_PATH="${HARD_DENY_SETTINGS_PATH:-$HOME/.claude/settings.json}"

MODE="check"
JSON_OUT="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check)      MODE="check"; shift ;;
    --install)    MODE="install"; shift ;;
    --show)       MODE="show"; shift ;;
    --uninstall)  MODE="uninstall"; shift ;;
    --json)       JSON_OUT="true"; shift ;;
    -h|--help)
      awk 'NR==1{next} /^set -euo/{exit} {sub(/^# ?/,""); print}' "$0"
      exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ ! -f "$CATALOG" ]]; then
  echo "ERROR: catalog not found at $CATALOG" >&2
  exit 3
fi

# Human-readable preamble on stderr; structured payload on stdout (when --json).
{
  echo "Catalog:   $CATALOG"
  echo "Settings:  $SETTINGS_PATH"
  echo "Mode:      $MODE"
} >&2

python3 - "$CATALOG" "$SETTINGS_PATH" "$MODE" "$JSON_OUT" <<'PYEOF'
"""Merge / inspect / uninstall craft hard_deny rules in ~/.claude/settings.json."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

catalog_path = Path(sys.argv[1])
settings_path = Path(sys.argv[2])
mode = sys.argv[3]
json_out = sys.argv[4] == "true"

try:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
except (json.JSONDecodeError, OSError) as exc:
    print(f"ERROR: catalog unreadable: {exc}", file=sys.stderr)
    sys.exit(3)

craft_rules = [
    entry["rule"]
    for entry in catalog.get("rules", [])
    if entry.get("category") == "hard_deny"
]
defaults_marker = catalog.get("defaults_marker", "$defaults")

# Load existing settings (empty if absent).
if settings_path.exists():
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"ERROR: settings unreadable: {exc}", file=sys.stderr)
        sys.exit(1)
else:
    settings = {}

auto_mode = settings.get("autoMode", {})
current = list(auto_mode.get("hard_deny", []))

# Compute target list (idempotent merge).
target = list(current)

# Ensure $defaults is present and first.
if defaults_marker not in target:
    target.insert(0, defaults_marker)
elif target.index(defaults_marker) != 0:
    target.remove(defaults_marker)
    target.insert(0, defaults_marker)

# Append craft rules that aren't already present.
for rule in craft_rules:
    if rule not in target:
        target.append(rule)

added = [r for r in target if r not in current]
already_present = [r for r in craft_rules if r in current]

# --uninstall: remove craft rules (keep $defaults and user entries).
if mode == "uninstall":
    target = [r for r in current if r not in craft_rules]
    # Don't strip $defaults — that's not craft's call.

report = {
    "settings_path": str(settings_path),
    "current_count": len(current),
    "target_count": len(target),
    "craft_rules_total": len(craft_rules),
    "craft_rules_already_present": len(already_present),
    "would_add": added if mode != "uninstall" else [],
    "would_remove": (
        [r for r in craft_rules if r in current] if mode == "uninstall" else []
    ),
    "defaults_present": defaults_marker in target,
}


def emit_human():
    print("", file=sys.stderr)
    print(f"  current entries:     {report['current_count']}", file=sys.stderr)
    print(f"  craft rules total:   {report['craft_rules_total']}", file=sys.stderr)
    print(
        f"  craft rules already: {report['craft_rules_already_present']}",
        file=sys.stderr,
    )
    print(f"  defaults marker:     {report['defaults_present']}", file=sys.stderr)
    if mode == "uninstall":
        print(f"  would remove:        {len(report['would_remove'])}", file=sys.stderr)
        for r in report["would_remove"]:
            print(f"    - {r[:80]}{'…' if len(r) > 80 else ''}", file=sys.stderr)
    else:
        print(f"  would add:           {len(report['would_add'])}", file=sys.stderr)
        for r in report["would_add"]:
            print(f"    + {r[:80]}{'…' if len(r) > 80 else ''}", file=sys.stderr)


if mode == "show":
    emit_human()
    if json_out:
        print(json.dumps({"current": current, **report}, indent=2))
    else:
        print(json.dumps({"autoMode": {"hard_deny": current}}, indent=2))
    sys.exit(0)

if mode == "check":
    emit_human()
    if json_out:
        print(json.dumps(report, indent=2))
    else:
        if not report["would_add"]:
            print("No changes needed — craft rules already installed.", file=sys.stderr)
        else:
            print(
                f"Run with --install to apply {len(report['would_add'])} change(s).",
                file=sys.stderr,
            )
    sys.exit(0)

# install or uninstall: write back.
auto_mode["hard_deny"] = target
settings["autoMode"] = auto_mode

# Ensure parent dir exists.
settings_path.parent.mkdir(parents=True, exist_ok=True)

# Atomic write via temp file + rename.
tmp_path = settings_path.with_suffix(settings_path.suffix + ".craft-tmp")
tmp_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
os.replace(tmp_path, settings_path)

if mode == "uninstall":
    print(f"Uninstalled {len(report['would_remove'])} craft rule(s).", file=sys.stderr)
else:
    print(f"Installed {len(report['would_add'])} change(s).", file=sys.stderr)

emit_human()
if json_out:
    print(json.dumps(report, indent=2))
sys.exit(0)
PYEOF
