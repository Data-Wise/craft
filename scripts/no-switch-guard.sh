#!/usr/bin/env bash
# PreToolUse(Bash) hook: enforce ~/.claude/rules/no-unrequested-branch-switch.md
#
# Gates branch/worktree operations BY HARM, not by verb (3-tier, mirrors
# craft's branch-guard LOW/MEDIUM/HIGH). See
# ~/.claude/PROPOSAL-switch-guard-harm-taxonomy.md for the rationale.
#
#   GREEN  allow silently  — read-only inspection (branch --show-current,
#                            worktree list, status, log, diff, pwd). `cd` is
#                            no longer gated (cwd resets every call).
#   YELLOW allow + announce — clean-tree switch to an EXISTING non-main branch;
#                            `git worktree add`. Emits a systemMessage notice
#                            (you SEE it, you don't click) so you're never
#                            context-desynced, but you're not nagged.
#   RED    ask (confirm)    — dirty-tree switch; new-branch creation
#                            (switch -c / checkout -b); switch ONTO main/master;
#                            worktree remove/move; destructive restore
#                            (git restore / git checkout -- <file>, data loss).
#
# Why this still "guards Claude's switches only": a Bash hook payload has no
# actor field, so it can't tell who asked. But user-typed `!git switch …` runs
# in the user's shell (no hook), and every command I run goes through the Bash
# tool (hook fires). Gating by harm means the only prompts you ever see are for
# genuinely dangerous switches — exactly the ones Claude must not do unprompted.
#
# Wired in ~/.claude/settings.json under PreToolUse > matcher "Bash".
# Contract: payload arrives as JSON on STDIN (NOT env vars). Never errors out
# (a crash would fail-open + show "Ran 1 hook" UI noise).

set -uo pipefail

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // ""' 2>/dev/null || true)
[ -z "$cmd" ] && exit 0

# --- Registry: check if this guard is enabled/muted -----------------------
_GUARD_REG="${HOME}/.claude/guards.json"
if command -v jq &>/dev/null && [[ -f "$_GUARD_REG" ]]; then
  _guard_enabled=$(jq -r '.guards["no-switch-guard"].enabled' "$_GUARD_REG" 2>/dev/null || true)
  _guard_muted=$(jq -r '.guards["no-switch-guard"].muted_until // "null"' "$_GUARD_REG" 2>/dev/null || echo "null")
  [[ "$_guard_enabled" == "false" ]] && exit 0
  if [[ "$_guard_muted" != "null" && "$_guard_muted" != "" ]]; then
    _now=$(date -u +%s)
    _until=$(date -u -j -f "%Y-%m-%dT%H:%M:%SZ" "$_guard_muted" +%s 2>/dev/null || echo 0)
    [[ "$_now" -lt "$_until" ]] && exit 0
  fi
fi
# --------------------------------------------------------------------------

# --- output helpers -------------------------------------------------------
# Statusline: /craft:git:guard list shows guard state; claude-hud renders guards.json if available
ask() {       # $1 = reason → confirmation prompt
  jq -nc --arg r "$1" \
    '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"ask",permissionDecisionReason:($r + "\n\nTo mute this guard: /craft:git:guard disable no-switch-guard")}}'
  exit 0
}
announce() {  # $1 = notice → allowed, but shown to the user
  jq -nc --arg m "$1" '{systemMessage:$m}'
  exit 0
}

# --- helpers --------------------------------------------------------------
# Resolve the repo dir the command targets (honor `git -C <dir>`), else cwd.
git_dir=$(printf '%s' "$cmd" | grep -oE 'git[[:space:]]+-C[[:space:]]+[^[:space:]]+' | head -1 | awk '{print $3}')
is_dirty() {
  local out
  out=$(git ${git_dir:+-C "$git_dir"} status --porcelain 2>/dev/null) || return 1
  [ -n "$out" ]
}
# First non-flag token after switch/checkout = the target ref.
switch_target() {
  printf '%s' "$cmd" \
    | sed -E 's/.*(switch|checkout)[[:space:]]+//' \
    | tr ' \t' '\n\n' | grep -vE '^-' | head -1
}

GITPFX='(^|[^[:alnum:]_])git([[:space:]]+-[^[:space:]]+|[[:space:]]+-C[[:space:]]+[^[:space:]]+)*[[:space:]]+'

# === 1. Destructive restore (data loss) — RED ============================
# Excludes --staged (only unstages, doesn't discard working-tree changes)
if printf '%s' "$cmd" | grep -Eq "${GITPFX}restore([[:space:]]|$)" \
   && ! printf '%s' "$cmd" | grep -Eq "${GITPFX}restore[[:space:]]+--staged"; then
  ask "Destructive restore detected (git restore / git checkout -- <file>) — this DISCARDS uncommitted changes. Approve only if you mean to throw that work away."
fi
if printf '%s' "$cmd" | grep -Eq 'checkout[[:space:]]+--([[:space:]]|$)'; then
  ask "Destructive restore detected (git checkout -- <file>) — this DISCARDS uncommitted changes. Approve only if you mean to throw that work away."
fi

# === 2. Worktree ops =====================================================
if printf '%s' "$cmd" | grep -Eq 'worktree[[:space:]]+add([[:space:]]|$)'; then
  announce "🌿 no-switch-guard: allowed a 'git worktree add' (creates isolation, destroys nothing)."
fi
if printf '%s' "$cmd" | grep -Eq 'worktree[[:space:]]+(remove|move)([[:space:]]|$)'; then
  ask "Destructive worktree op detected (git worktree remove/move). Approve only if you intend to delete/relocate that worktree (uncommitted work there may be lost)."
fi

# === 3. Branch switch (git switch / git checkout <branch>) ===============
is_switch=""
if printf '%s' "$cmd" | grep -Eq "${GITPFX}switch([[:space:]]|$)"; then
  is_switch=1
elif printf '%s' "$cmd" | grep -Eq "${GITPFX}checkout([[:space:]]|$)" \
   && ! printf '%s' "$cmd" | grep -Eq 'checkout[[:space:]]+--([[:space:]]|$)'; then
  is_switch=1
fi

if [ -n "$is_switch" ]; then
  # 3a. new-branch creation — RED
  if printf '%s' "$cmd" | grep -Eq '(switch[[:space:]].*(-c|-C|--create)|checkout[[:space:]].*(-b|-B))([[:space:]]|=|$)'; then
    ask "New-branch creation detected (git switch -c / git checkout -b). Approve only if you meant to create a branch (mind the 'no new code on dev' rule)."
  fi
  target=$(switch_target)
  # 3b. switch ONTO main/master — RED
  if printf '%s' "$target" | grep -Eq '^(origin/|upstream/)?(main|master)$'; then
    ask "Switch ONTO '${target}' detected. main/master is protected — approve only if you intend to be on it (no edits/commits there)."
  fi
  # 3c. dirty working tree — RED
  if is_dirty; then
    ask "Branch switch with a DIRTY working tree (uncommitted changes present). Approve only if you intend to carry/strand those changes."
  fi
  # 3d. clean switch to existing non-main branch — YELLOW announce
  announce "🔀 no-switch-guard: switching to '${target:-?}' (clean tree, existing branch) — allowed. Heads-up so your next command isn't on the wrong branch."
fi

# === GREEN: everything else (read-only, cd, etc.) — allow silently ======
exit 0
