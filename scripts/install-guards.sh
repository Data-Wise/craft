#!/usr/bin/env bash
#
# install-guards.sh — Install both branch-guard and no-switch-guard hooks for Claude Code
#
# Copies scripts/branch-guard.sh and scripts/no-switch-guard.sh to ~/.claude/hooks/
# and registers them in ~/.claude/settings.json as PreToolUse hooks.
#
# Usage:
#   ./scripts/install-guards.sh          # from repo root
#   bash scripts/install-guards.sh       # explicit
#
# Idempotent: safe to run multiple times.
# Requires: jq (for settings.json registration; warns if missing)

set -euo pipefail

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

HOOK_DIR="${HOME}/.claude/hooks"
SETTINGS="${HOME}/.claude/settings.json"

# ---------------------------------------------------------------------------
# Colors (minimal — no dependency on formatting.sh)
# ---------------------------------------------------------------------------
G='\033[0;32m' Y='\033[1;33m' R='\033[1;31m' B='\033[1m' N='\033[0m'

ok()   { printf "${G}✓${N} %s\n" "$1"; }
warn() { printf "${Y}!${N} %s\n" "$1"; }
err()  { printf "${R}✗${N} %s\n" "$1" >&2; }

# ---------------------------------------------------------------------------
# install_hook <src_basename>
#   Copies REPO_ROOT/scripts/<src_basename> to HOOK_DIR/<src_basename>.
#   Handles symlinks, up-to-date, and fresh installs idempotently.
# ---------------------------------------------------------------------------
install_hook() {
  local basename="$1"
  local src="${REPO_ROOT}/scripts/${basename}"
  local dest="${HOOK_DIR}/${basename}"

  if [[ ! -f "$src" ]]; then
    err "Source not found: $src"
    err "Run this script from the craft repo root."
    exit 1
  fi

  mkdir -p "$HOOK_DIR"

  if [[ -L "$dest" ]]; then
    ok "${basename} already symlinked: $(readlink "$dest")"
  elif [[ -f "$dest" ]]; then
    if diff -q "$src" "$dest" &>/dev/null; then
      ok "${basename} already up to date"
    else
      cp "$src" "$dest"
      chmod +x "$dest"
      ok "${basename} updated"
    fi
  else
    cp "$src" "$dest"
    chmod +x "$dest"
    ok "${basename} installed to ${HOOK_DIR}/"
  fi
}

# ---------------------------------------------------------------------------
# 1. Copy hooks to ~/.claude/hooks/
# ---------------------------------------------------------------------------
install_hook "branch-guard.sh"
install_hook "no-switch-guard.sh"

# ---------------------------------------------------------------------------
# 1b. Copy lib/git-utils.sh to ~/.claude/lib/ (needed by branch-guard squash-merge detection)
# ---------------------------------------------------------------------------
LIB_SRC="${REPO_ROOT}/lib/git-utils.sh"
LIB_DIR="${HOME}/.claude/lib"
LIB_DEST="${LIB_DIR}/git-utils.sh"

if [[ ! -f "$LIB_SRC" ]]; then
  warn "lib/git-utils.sh not found — squash-merge detection unavailable"
else
  mkdir -p "$LIB_DIR"
  if [[ -L "$LIB_DEST" ]]; then
    ok "git-utils.sh already symlinked"
  elif [[ -f "$LIB_DEST" ]] && diff -q "$LIB_SRC" "$LIB_DEST" &>/dev/null; then
    ok "git-utils.sh already up to date"
  else
    cp "$LIB_SRC" "$LIB_DEST"
    ok "git-utils.sh installed to ${LIB_DIR}/"
  fi
fi

# ---------------------------------------------------------------------------
# 2. Register in settings.json (requires jq)
# ---------------------------------------------------------------------------
if ! command -v jq &>/dev/null; then
  warn "jq not found — skipping settings.json registration"
  echo "  Install jq (brew install jq) and re-run, or add manually:"
  echo ""
  echo "  In ~/.claude/settings.json, add to \"hooks.PreToolUse\":"
  echo '    { "matcher": "Edit|Write", "hooks": [{ "type": "command", "command": "/bin/bash ~/.claude/hooks/branch-guard.sh", "timeout": 5000 }] }'
  echo '    { "matcher": "Bash",       "hooks": [{ "type": "command", "command": "/bin/bash ~/.claude/hooks/branch-guard.sh", "timeout": 5000 }] }'
  echo '    { "matcher": "Bash",       "hooks": [{ "type": "command", "command": "/bin/bash ~/.claude/hooks/no-switch-guard.sh", "timeout": 5000 }] }'
  exit 0
fi

if [[ ! -f "$SETTINGS" ]]; then
  echo '{}' > "$SETTINGS"
fi

BRANCH_GUARD_CMD="/bin/bash ${HOME}/.claude/hooks/branch-guard.sh"
NO_SWITCH_GUARD_CMD="/bin/bash ${HOME}/.claude/hooks/no-switch-guard.sh"

# ---------------------------------------------------------------------------
# 2a. Register branch-guard (Edit|Write + Bash entries)
# ---------------------------------------------------------------------------
if jq -e '.hooks.PreToolUse // [] | map(.hooks[]?.command) | any(test("branch-guard"))' "$SETTINGS" &>/dev/null; then
  ok "settings.json already has branch-guard entries"
else
  EDIT_ENTRY="$(jq -n --arg cmd "$BRANCH_GUARD_CMD" '{
    "matcher": "Edit|Write",
    "hooks": [{ "type": "command", "command": $cmd, "timeout": 5000 }]
  }')"

  BASH_ENTRY="$(jq -n --arg cmd "$BRANCH_GUARD_CMD" '{
    "matcher": "Bash",
    "hooks": [{ "type": "command", "command": $cmd, "timeout": 5000 }]
  }')"

  jq --argjson edit "$EDIT_ENTRY" --argjson bash "$BASH_ENTRY" '
    .hooks.PreToolUse = (.hooks.PreToolUse // []) + [$edit, $bash]
  ' "$SETTINGS" > "${SETTINGS}.tmp" && mv "${SETTINGS}.tmp" "$SETTINGS"

  ok "Registered branch-guard in ${SETTINGS}"
fi

# ---------------------------------------------------------------------------
# 2b. Register no-switch-guard (Bash only — does not gate Edit/Write)
# ---------------------------------------------------------------------------
if jq -e '.hooks.PreToolUse // [] | map(.hooks[]?.command) | any(test("no-switch-guard"))' "$SETTINGS" &>/dev/null; then
  ok "settings.json already has no-switch-guard entry"
else
  NSG_ENTRY="$(jq -n --arg cmd "$NO_SWITCH_GUARD_CMD" '{
    "matcher": "Bash",
    "hooks": [{ "type": "command", "command": $cmd, "timeout": 5000 }]
  }')"

  jq --argjson nsg "$NSG_ENTRY" '
    .hooks.PreToolUse = (.hooks.PreToolUse // []) + [$nsg]
  ' "$SETTINGS" > "${SETTINGS}.tmp" && mv "${SETTINGS}.tmp" "$SETTINGS"

  ok "Registered no-switch-guard in ${SETTINGS}"
fi

# ---------------------------------------------------------------------------
# 4. Seed guards.json registry (if not present)
# ---------------------------------------------------------------------------
GUARDS_JSON="${HOME}/.claude/guards.json"

if [[ ! -f "$GUARDS_JSON" ]]; then
  jq -n '{
    "guards": {
      "branch-guard":   { "enabled": true, "muted_until": null, "mute_window_min": 30 },
      "no-switch-guard":{ "enabled": true, "muted_until": null, "mute_window_min": 30 }
    }
  }' > "$GUARDS_JSON"
  ok "Created guards.json registry at ${GUARDS_JSON}"
else
  # Add any missing guard entries (idempotent merge)
  for guard in branch-guard no-switch-guard; do
    if ! jq -e --arg g "$guard" '.guards[$g]' "$GUARDS_JSON" &>/dev/null; then
      jq --arg g "$guard" '.guards[$g] = {"enabled":true,"muted_until":null,"mute_window_min":30}' \
        "$GUARDS_JSON" > "${GUARDS_JSON}.tmp" && mv "${GUARDS_JSON}.tmp" "$GUARDS_JSON"
      ok "Added ${guard} to guards.json"
    fi
  done
  ok "guards.json already exists (entries verified)"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo -e "${B}Guards installed.${N}"
echo ""
echo "  branch-guard.sh — branch protection:"
echo "    • main/master — all edits and commits blocked"
echo "    • dev/develop  — new code files blocked (edits allowed)"
echo "    • feature/*    — unrestricted"
echo ""
echo "  no-switch-guard.sh — switch/worktree gating:"
echo "    • GREEN  — read-only ops allowed silently"
echo "    • YELLOW — clean-tree switch / worktree add announced"
echo "    • RED    — dirty-tree switch, new-branch, main switch, destructive restore/worktree: ask"
echo ""
echo "Commands:"
echo "  /craft:git:unprotect  — session-scoped bypass"
echo "  /craft:git:protect    — re-enable protection"
