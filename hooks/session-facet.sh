#!/bin/bash
# session-facet.sh — SessionEnd hook. Writes a low-fidelity skeleton facet once
# per session so insights have a baseline even without /done. Per-session-id
# dedup (D5): skip if this session already has a facet/marker. Silent, exit 0.

INPUT=$(cat 2>/dev/null)
sid() { printf '%s' "$INPUT" | jq -r '.session_id // empty' 2>/dev/null \
        || printf '%s' "$INPUT" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("session_id",""))' 2>/dev/null; }
cwdv() { printf '%s' "$INPUT" | jq -r '.cwd // empty' 2>/dev/null \
        || printf '%s' "$INPUT" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("cwd",""))' 2>/dev/null; }

SESSION_ID="$(sid)"; CWD="$(cwdv)"
[ -z "$SESSION_ID" ] && SESSION_ID="$(date +%Y%m%d-%H%M%S)-$$"
[ -z "$CWD" ] && CWD="$PWD"

FACETS="${SESSION_FACETS:-$HOME/.claude/usage-data/facets}"
MARKERS="$HOME/.claude/sessions/active"
mkdir -p "$FACETS" "$MARKERS"

# Dedup (D5 + grill open-question fallback): this session already captured?
[ -f "$MARKERS/$SESSION_ID.faceted" ] && exit 0
ls "$FACETS"/session-"$SESSION_ID".json >/dev/null 2>&1 && exit 0

PROJECT="$(basename "$CWD" 2>/dev/null || echo unknown)"
BRANCH="$(git -C "$CWD" branch --show-current 2>/dev/null || echo "")"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

cat > "$FACETS/session-$SESSION_ID.json" <<EOF
{
  "session_id": "$SESSION_ID",
  "timestamp": "$TS",
  "project": "$PROJECT",
  "branch": "$BRANCH",
  "goal_category": "unknown",
  "outcome": "session-end",
  "friction_events": [],
  "auto_collected": true
}
EOF
touch "$MARKERS/$SESSION_ID.faceted"
exit 0
