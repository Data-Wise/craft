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

# --classify / GUARD_DRY_RUN=1: additive ground-truth mode, mirrors
# branch-guard.sh's identically-named mode (SPEC-branch-protection-consolidation
# -2026-07-07 §4.6 #3). Prints the tier (ALLOW/YELLOW/ASK) that would fire
# instead of emitting the real permissionDecision JSON / systemMessage. Reuses
# ask()/announce()'s existing call sites — no separate classification logic.
CLASSIFY_MODE=false
if [ "${GUARD_DRY_RUN:-0}" = "1" ] || [ "${1:-}" = "--classify" ]; then
  CLASSIFY_MODE=true
fi

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // ""' 2>/dev/null || true)
if [ -z "$cmd" ]; then
  [ "$CLASSIFY_MODE" = true ] && echo "ALLOW: no command in payload"
  exit 0
fi

# --- Registry: check if this guard is enabled/muted -----------------------
_GUARD_REG="${HOME}/.claude/guards.json"
if command -v jq &>/dev/null && [[ -f "$_GUARD_REG" ]]; then
  _guard_enabled=$(jq -r '.guards["no-switch-guard"].enabled' "$_GUARD_REG" 2>/dev/null || true)
  _guard_muted=$(jq -r '.guards["no-switch-guard"].muted_until // "null"' "$_GUARD_REG" 2>/dev/null || echo "null")
  if [[ "$_guard_enabled" == "false" ]]; then
    [ "$CLASSIFY_MODE" = true ] && echo "SKIP: guard disabled"
    exit 0
  fi
  if [[ "$_guard_muted" != "null" && "$_guard_muted" != "" ]]; then
    _now=$(date -u +%s)
    # BSD date first, GNU `date -d` fallback (Linux/CI)
    _until=$(date -u -j -f "%Y-%m-%dT%H:%M:%SZ" "$_guard_muted" +%s 2>/dev/null || date -u -d "$_guard_muted" +%s 2>/dev/null || echo 0)
    if [[ "$_now" -lt "$_until" ]]; then
      [ "$CLASSIFY_MODE" = true ] && echo "SKIP: guard muted"
      exit 0
    fi
  fi
fi
# --------------------------------------------------------------------------

# --- output helpers -------------------------------------------------------
# Statusline: /craft:git:guard list shows guard state; claude-hud renders guards.json if available
ask() {       # $1 = reason → confirmation prompt
  if [ "$CLASSIFY_MODE" = true ]; then
    echo "ASK: $1"
    exit 0
  fi
  jq -nc --arg r "$1" \
    '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"ask",permissionDecisionReason:($r + "\n\nTo mute this guard: /craft:git:guard disable no-switch-guard")}}'
  exit 0
}
announce() {  # $1 = notice → allowed, but shown to the user
  if [ "$CLASSIFY_MODE" = true ]; then
    echo "YELLOW: $1"
    exit 0
  fi
  jq -nc --arg m "$1" '{systemMessage:$m}'
  exit 0
}

# --- helpers --------------------------------------------------------------
# Resolve the repo dir the command targets, with CUMULATIVE cwd tracking.
# A compound command may retarget a different directory than the hook's own
# invocation cwd via `cd <path> &&`/`;` clauses or a `git -C <path>` flag.
# Walk the clauses left-to-right: each bare `cd <path>` updates the effective
# working directory for every SUBSEQUENT clause (not just the next one — a
# `cd a && cd b && git switch x` resolves to b, not a); a `git ... -C <path>`
# sets the target for that git invocation, resolved against the effective cwd
# in force at that point. The LAST such retarget wins (last-wins, matching the
# cumulative-cd model). Paths containing `$`/backtick are skipped (a shell
# expansion we can't statically resolve). Without this, is_dirty() below would
# check the wrong repo.
#
# Parallel-inline with branch-guard.sh §8d0 rather than a shared sourced file:
# the two hooks derive their base cwd differently (no-switch from process $PWD,
# branch-guard from the JSON `.cwd`), and a shared file would force both install
# scripts to deploy + source it. See the Phase 1 commit message.
resolve_target_dir() {  # $1 = command, $2 = base cwd → echoes resolved dir ("" if no retarget)
  local _cmd="$1" _eff="$2" _rt="" _clause _p _norm
  # Split compound-command separators (&& ; | and ||) to one clause per line.
  # awk gsub emits a REAL newline on BSD & GNU (BSD sed's `\n` does not — see
  # macos-shell-portability-gotchas). Single `|` also splits so a piped
  # `grep -C N` can't be misread as a git `-C` target.
  _norm=$(printf '%s' "$_cmd" | awk '{gsub(/&&|[;|]/,"\n"); print}')
  while IFS= read -r _clause; do
    _clause="${_clause#"${_clause%%[![:space:]]*}"}"  # trim leading whitespace
    if printf '%s' "$_clause" | grep -qE '^cd[[:space:]]+[^[:space:]]+'; then
      _p=$(printf '%s' "$_clause" | sed -E 's/^cd[[:space:]]+//' | awk '{print $1}')
      case "$_p" in ''|*'$'*|*'`'*|*'"'*|*"'"*) _p="" ;; esac
      if [ -n "$_p" ]; then
        [ "${_p#/}" = "$_p" ] && _p="${_eff%/}/$_p"  # relative → resolve vs effective cwd
        _eff="$_p"; _rt="$_p"
      fi
    elif printf '%s' "$_clause" | grep -qE '(^|[[:space:]])git([[:space:]]|$)' \
      && printf '%s' "$_clause" | grep -qE '(^|[[:space:]])-C[[:space:]]+[^[:space:]]+'; then
      _p=$(printf '%s' "$_clause" | grep -oE '(^|[[:space:]])-C[[:space:]]+[^[:space:]]+' | head -1 | sed -E 's/^[[:space:]]*-C[[:space:]]+//')
      case "$_p" in ''|*'$'*|*'`'*|*'"'*|*"'"*) _p="" ;; esac
      if [ -n "$_p" ]; then
        [ "${_p#/}" = "$_p" ] && _p="${_eff%/}/$_p"
        _rt="$_p"
      fi
    fi
  done <<EOF
$_norm
EOF
  printf '%s' "$_rt"
}
git_dir=$(resolve_target_dir "$cmd" "$PWD")
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
# When the command retargets a different repo (a cd/-C the resolver picked up),
# name it in user-facing prompts so a cross-context switch isn't ambiguous
# about WHICH repo it acts on (mirrors branch-guard.sh's "name the resolved
# repo/branch explicitly" review-checklist item from #284).
target_repo_note=""
[ -n "$git_dir" ] && target_repo_note=" [target repo: $(basename "$git_dir")]"

GITPFX='(^|[^[:alnum:]_])git([[:space:]]+-[^[:space:]]+|[[:space:]]+-C[[:space:]]+[^[:space:]]+)*[[:space:]]+'

# === 1. Destructive restore (data loss) — RED ============================
# `git restore` discards working-tree changes UNLESS it's staged-only
# (--staged/-S WITHOUT --worktree/-W). `git restore --staged --worktree` (or -SW, -W)
# IS destructive and must still be gated.
if printf '%s' "$cmd" | grep -Eq "${GITPFX}restore([[:space:]]|$)"; then
  if printf '%s' "$cmd" | grep -Eq 'restore[[:space:]].*(--staged|[[:space:]]-S)' \
     && ! printf '%s' "$cmd" | grep -Eq 'restore[[:space:]].*(--worktree|[[:space:]]-[A-Za-z]*W)'; then
    : # staged-only restore — not destructive, allow
  else
    ask "Destructive restore detected (git restore discards working-tree changes). Approve only if you mean to throw that work away."
  fi
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
    ask "Branch switch with a DIRTY working tree${target_repo_note} (uncommitted changes present). Approve only if you intend to carry/strand those changes."
  fi
  # 3d. clean switch to existing non-main branch — YELLOW announce
  announce "🔀 no-switch-guard: switching to '${target:-?}'${target_repo_note} (clean tree, existing branch) — allowed. Heads-up so your next command isn't on the wrong branch."
fi

# === GREEN: everything else (read-only, cd, etc.) — allow silently ======
[ "$CLASSIFY_MODE" = true ] && echo "ALLOW: no rule matched (GREEN — read-only or unclassified)"
exit 0
