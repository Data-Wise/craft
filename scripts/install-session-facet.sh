#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$HOME/.claude/hooks/session-facet.sh"
SETTINGS="$HOME/.claude/settings.json"
mkdir -p "$HOME/.claude/hooks"
cp "$ROOT/hooks/session-facet.sh" "$DEST"; chmod +x "$DEST"

# Register SessionEnd idempotently via python3 (stdlib JSON).
python3 - "$SETTINGS" "$DEST" <<'PY'
import json, sys, os
settings_path, hook_path = sys.argv[1], sys.argv[2]
s = json.load(open(settings_path)) if os.path.exists(settings_path) else {}
hooks = s.setdefault("hooks", {})
arr = hooks.setdefault("SessionEnd", [])
flat = json.dumps(arr)
if "session-facet.sh" not in flat:
    arr.append({"hooks": [{"type": "command", "command": hook_path}]})
json.dump(s, open(settings_path, "w"), indent=2)
PY
echo "session-facet SessionEnd hook installed + registered"
