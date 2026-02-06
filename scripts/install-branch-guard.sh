#!/usr/bin/env bash
#
# install-branch-guard.sh — Install the branch-guard hook for Claude Code
#
# Copies scripts/branch-guard.sh to ~/.claude/hooks/ and registers it
# in ~/.claude/settings.json as a PreToolUse hook.
#
# Usage:
#   ./scripts/install-branch-guard.sh          # from repo root
#   bash scripts/install-branch-guard.sh       # explicit
#
# Idempotent: safe to run multiple times.
# Requires: jq (for settings.json registration; warns if missing)

set -euo pipefail

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

HOOK_SRC="${REPO_ROOT}/scripts/branch-guard.sh"
HOOK_DIR="${HOME}/.claude/hooks"
HOOK_DEST="${HOOK_DIR}/branch-guard.sh"
SETTINGS="${HOME}/.claude/settings.json"

# ---------------------------------------------------------------------------
# Colors (minimal — no dependency on formatting.sh)
# ---------------------------------------------------------------------------
G='\033[0;32m' Y='\033[1;33m' R='\033[1;31m' B='\033[1m' N='\033[0m'

ok()   { printf "${G}✓${N} %s\n" "$1"; }
warn() { printf "${Y}!${N} %s\n" "$1"; }
err()  { printf "${R}✗${N} %s\n" "$1" >&2; }

# ---------------------------------------------------------------------------
# 1. Verify source exists
# ---------------------------------------------------------------------------
if [[ ! -f "$HOOK_SRC" ]]; then
  err "Source not found: $HOOK_SRC"
  err "Run this script from the craft repo root."
  exit 1
fi

# ---------------------------------------------------------------------------
# 2. Copy hook to ~/.claude/hooks/
# ---------------------------------------------------------------------------
mkdir -p "$HOOK_DIR"

if [[ -L "$HOOK_DEST" ]]; then
  # Already a symlink (e.g. dev setup) — leave it
  ok "branch-guard.sh already symlinked: $(readlink "$HOOK_DEST")"
elif [[ -f "$HOOK_DEST" ]]; then
  # Compare contents — skip if identical
  if diff -q "$HOOK_SRC" "$HOOK_DEST" &>/dev/null; then
    ok "branch-guard.sh already up to date"
  else
    cp "$HOOK_SRC" "$HOOK_DEST"
    chmod +x "$HOOK_DEST"
    ok "branch-guard.sh updated"
  fi
else
  cp "$HOOK_SRC" "$HOOK_DEST"
  chmod +x "$HOOK_DEST"
  ok "branch-guard.sh installed to ${HOOK_DIR}/"
fi

# ---------------------------------------------------------------------------
# 3. Register in settings.json (requires jq)
# ---------------------------------------------------------------------------
if ! command -v jq &>/dev/null; then
  warn "jq not found — skipping settings.json registration"
  echo "  Install jq (brew install jq) and re-run, or add manually:"
  echo ""
  echo "  In ~/.claude/settings.json, add to \"hooks.PreToolUse\":"
  echo '    { "matcher": "Edit|Write", "hooks": [{ "type": "command", "command": "/bin/bash ~/.claude/hooks/branch-guard.sh", "timeout": 5000 }] }'
  echo '    { "matcher": "Bash",       "hooks": [{ "type": "command", "command": "/bin/bash ~/.claude/hooks/branch-guard.sh", "timeout": 5000 }] }'
  exit 0
fi

# Ensure settings.json exists with minimal structure
if [[ ! -f "$SETTINGS" ]]; then
  echo '{}' > "$SETTINGS"
fi

HOOK_CMD="/bin/bash ${HOME}/.claude/hooks/branch-guard.sh"

# Check if branch-guard is already registered (look for the hook command)
if jq -e '.hooks.PreToolUse // [] | map(.hooks[]?.command) | any(test("branch-guard"))' "$SETTINGS" &>/dev/null; then
  ok "settings.json already has branch-guard entries"
  exit 0
fi

# Build the two PreToolUse entries
EDIT_ENTRY="$(jq -n --arg cmd "$HOOK_CMD" '{
  "matcher": "Edit|Write",
  "hooks": [{ "type": "command", "command": $cmd, "timeout": 5000 }]
}')"

BASH_ENTRY="$(jq -n --arg cmd "$HOOK_CMD" '{
  "matcher": "Bash",
  "hooks": [{ "type": "command", "command": $cmd, "timeout": 5000 }]
}')"

# Append to PreToolUse array (create if missing)
jq --argjson edit "$EDIT_ENTRY" --argjson bash "$BASH_ENTRY" '
  .hooks.PreToolUse = (.hooks.PreToolUse // []) + [$edit, $bash]
' "$SETTINGS" > "${SETTINGS}.tmp" && mv "${SETTINGS}.tmp" "$SETTINGS"

ok "Registered branch-guard in ${SETTINGS}"

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo -e "${B}Branch guard installed.${N} Protection is active for:"
echo "  • main/master — all edits and commits blocked"
echo "  • dev/develop — new code files blocked (edits allowed)"
echo "  • feature/*   — unrestricted"
echo ""
echo "Commands:"
echo "  /craft:git:unprotect  — session-scoped bypass"
echo "  /craft:git:protect    — re-enable protection"
