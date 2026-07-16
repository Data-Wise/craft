#!/bin/bash
set -euo pipefail

# branch-guard.sh — Claude Code PreToolUse hook
# Enforces branch protection rules for main and dev branches.
# Reads JSON from stdin: { tool_name, tool_input: { file_path, command, ... }, cwd }
# Exits 0 = allow, 2 = block (message on stderr)
# Requires: jq (preferred), python3 (fallback), or grep/sed (last resort)

# ---------------------------------------------------------------------------
# 0. Load shared git utilities (resolve symlink to find real script location)
# ---------------------------------------------------------------------------
_SCRIPT_REAL="$(realpath "${BASH_SOURCE[0]}" 2>/dev/null || readlink -f "${BASH_SOURCE[0]}" 2>/dev/null || echo "${BASH_SOURCE[0]}")"
_CRAFT_LIB="$(dirname "$_SCRIPT_REAL")/../lib"
[[ -f "${_CRAFT_LIB}/git-utils.sh" ]] && source "${_CRAFT_LIB}/git-utils.sh"

# Protection levels:
#   block-all       — Hard block everything (main)
#   smart           — 3-tier: LOW (note) + MEDIUM (confirm) + HIGH (block) (dev / research draft)
#   block-new-code  — DEPRECATED alias for smart (backward compat)
#   confirm         — Alias for smart
#   (empty)         — No protection (feature/*)

# ---------------------------------------------------------------------------
# 1. Read stdin (JSON blob)
# ---------------------------------------------------------------------------
INPUT="$(cat)"

# ---------------------------------------------------------------------------
# 2. Extract fields from JSON using jq (Python fallback)
# ---------------------------------------------------------------------------
_json_get() {
  # Extract a string value from JSON. Uses jq, falls back to Python.
  # Usage: _json_get '.tool_name' "$json"
  local query="$1" json="$2"
  if command -v jq &>/dev/null; then
    printf '%s' "$json" | jq -r "$query // empty" 2>/dev/null || true
  elif command -v python3 &>/dev/null; then
    printf '%s' "$json" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    keys = '${query}'.lstrip('.').split('.')
    v = d
    for k in keys:
        v = v.get(k) if isinstance(v, dict) else None
        if v is None: break
    if v is not None: print(v, end='')
except: pass
" 2>/dev/null || true
  else
    # Last resort: grep/sed (extracts by the final key name in the path)
    local key="${query##*.}"
    printf '%s' "$json" | grep -o "\"${key}\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" 2>/dev/null | head -1 | sed "s/\"${key}\"[[:space:]]*:[[:space:]]*\"//;s/\"$//" || true
  fi
}

TOOL_NAME="$(_json_get '.tool_name' "$INPUT")"
CWD="$(_json_get '.cwd' "$INPUT")"

# Extract file_path from tool_input (for Edit / Write tools)
FILE_PATH="$(_json_get '.tool_input.file_path' "$INPUT")"
# Also try filePath variant
if [[ -z "$FILE_PATH" ]]; then
  FILE_PATH="$(_json_get '.tool_input.filePath' "$INPUT")"
fi

# Extract command from tool_input (for Bash tool)
COMMAND="$(_json_get '.tool_input.command' "$INPUT")"

# --- Registry: check if this guard is enabled/muted -----------------------
# SAFETY: catastrophic ops (rm -rf .git, git branch -D) are NEVER muteable —
# the registry gate must not bypass the universal catastrophic checks (8d).
_GUARD_REG="${HOME}/.claude/guards.json"
if command -v jq &>/dev/null && [[ -f "$_GUARD_REG" ]]; then
  _bg_catastrophic=0
  if echo "$COMMAND" | grep -qE 'rm[[:space:]]+-[rfRF]*[[:space:]]*((-[rfRF]+[[:space:]]+)*)\.git([[:space:]]|/|$)' \
     || echo "$COMMAND" | grep -qE '(^|;|&&|\|\|)[[:space:]]*git[[:space:]]+branch[[:space:]]+(-D|--delete[[:space:]]+--force|--force[[:space:]]+--delete)'; then
    _bg_catastrophic=1
  fi
  if [[ "$_bg_catastrophic" -eq 0 ]]; then
    _guard_enabled=$(jq -r '.guards["branch-guard"].enabled' "$_GUARD_REG" 2>/dev/null || true)
    _guard_muted=$(jq -r '.guards["branch-guard"].muted_until // "null"' "$_GUARD_REG" 2>/dev/null || echo "null")
    [[ "$_guard_enabled" == "false" ]] && exit 0
    if [[ "$_guard_muted" != "null" && "$_guard_muted" != "" ]]; then
      _now=$(date -u +%s)
      # BSD date first, GNU `date -d` fallback (Linux/CI)
      _until=$(date -u -j -f "%Y-%m-%dT%H:%M:%SZ" "$_guard_muted" +%s 2>/dev/null || date -u -d "$_guard_muted" +%s 2>/dev/null || echo 0)
      [[ "$_now" -lt "$_until" ]] && exit 0
    fi
  fi
fi
# --------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 3. Determine git context
# ---------------------------------------------------------------------------
# If no cwd provided, fall back to PWD
CWD="${CWD:-$PWD}"

# Prefer the target file's own directory over the session cwd when resolving
# git context (Edit/Write only). A session whose cwd isn't itself a git repo
# (e.g. a non-repo dotfiles dir) would otherwise exit 0 below before ever
# looking at FILE_PATH — silently bypassing protection for edits to files
# that ARE inside a protected repo elsewhere on disk. Bash commands (no
# FILE_PATH) are unaffected — they still resolve from CWD as before.
GIT_CTX_DIR="$CWD"
if [[ -n "$FILE_PATH" ]]; then
  _fp_dir="$FILE_PATH"
  if [[ "$FILE_PATH" != /* ]]; then
    _fp_dir="${CWD}/${FILE_PATH}"
  fi
  _fp_dir="$(dirname "$_fp_dir")"
  if [[ -d "$_fp_dir" ]] && (cd "$_fp_dir" 2>/dev/null && git rev-parse --show-toplevel &>/dev/null); then
    GIT_CTX_DIR="$_fp_dir"
  fi
fi

# Check if we're in a git repo
PROJECT_ROOT="$(cd "$GIT_CTX_DIR" 2>/dev/null && git rev-parse --show-toplevel 2>/dev/null)" || {
  # Not a git repo — allow everything
  exit 0
}

BRANCH="$(cd "$GIT_CTX_DIR" 2>/dev/null && git branch --show-current 2>/dev/null)" || {
  # Detached HEAD or other edge case — allow
  exit 0
}

# If branch is empty (detached HEAD), allow
[[ -z "$BRANCH" ]] && exit 0

# ---------------------------------------------------------------------------
# 3b. Allow writes to paths outside the repository
# ---------------------------------------------------------------------------
# If the tool provides a file_path, resolve it and check if it is outside
# the project root. Non-repo paths (memory files, /tmp, etc.) are always
# allowed regardless of branch protection level.
if [[ -n "$FILE_PATH" ]]; then
  # CWD-from-payload may differ in symlink-resolution from PROJECT_ROOT
  # (e.g. macOS: CWD=/tmp/x, git rev-parse=/private/tmp/x). Resolve CWD once
  # via cd/pwd -P — CWD always exists by definition, so this can't fail like
  # the per-call canonicalization in earlier versions of this hook did.
  CWD_RESOLVED="$(cd "$CWD" 2>/dev/null && pwd -P)" || CWD_RESOLVED="$CWD"

  FILE_PATH_ABS="$FILE_PATH"
  if [[ "$FILE_PATH" != /* ]]; then
    FILE_PATH_ABS="${CWD_RESOLVED}/${FILE_PATH}"
  elif [[ "$CWD" != "$CWD_RESOLVED" && "$FILE_PATH" == "$CWD"/* ]]; then
    # Absolute path supplied via the un-resolved CWD form (e.g. /tmp/x/foo
    # while CWD_RESOLVED is /private/tmp/x). Rewrite the prefix so the
    # membership check below matches PROJECT_ROOT without a python3 spawn.
    FILE_PATH_ABS="${CWD_RESOLVED}${FILE_PATH#$CWD}"
  fi

  # Canonicalize further only if the path contains `..` segments OR the
  # absolute form doesn't yet share the PROJECT_ROOT prefix (which means
  # either a different symlink path that needs resolving, or a real outside-
  # repo write that should fall through to the exit-0 below).
  #
  # The Write tool creates new files in possibly-new subdirs — using `cd`
  # to canonicalize would fail (silently) and leak unprotected writes
  # through. os.path.realpath walks the path and resolves what exists,
  # leaving any missing tail un-resolved — exactly the contract we need.
  # Python3 costs ~30ms per spawn; the fast path here skips it for the
  # common case where the user's tool already produced a clean absolute path
  # under PROJECT_ROOT.
  if { [[ "$FILE_PATH_ABS" == *"/../"* ]] || [[ "$FILE_PATH_ABS" == */.. ]] \
       || [[ "$FILE_PATH_ABS" != "$PROJECT_ROOT"/* && "$FILE_PATH_ABS" != "$PROJECT_ROOT" ]]; } \
     && command -v python3 &>/dev/null; then
    FILE_PATH_ABS="$(python3 -c "import os, sys; print(os.path.realpath(sys.argv[1]))" "$FILE_PATH_ABS" 2>/dev/null || printf '%s' "$FILE_PATH_ABS")"
  fi

  if [[ "$FILE_PATH_ABS" != "$PROJECT_ROOT"/* && "$FILE_PATH_ABS" != "$PROJECT_ROOT" ]]; then
    exit 0
  fi
fi

# Project short name (basename of repo root)
PROJECT_NAME="$(basename "$PROJECT_ROOT")"

# ---------------------------------------------------------------------------
# 4. (Bypass-marker check moved to step 8e, after the universal catastrophic
#    checks in 8d — allow-dev-edit must never be able to skip those.)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 5. Check dry-run marker
# ---------------------------------------------------------------------------
DRY_RUN=false
if [[ -f "${PROJECT_ROOT}/.claude/branch-guard-dryrun" ]]; then
  DRY_RUN=true
fi

# ---------------------------------------------------------------------------
# 6. Load config or auto-detect protection rules
# ---------------------------------------------------------------------------
# Protection levels: "block-all", "smart", "block-new-code" (alias), "confirm" (alias), "" (none)
PROTECTION=""
MAIN_PROTECTION=""
DEV_PROTECTION=""

# Detect integration-branch presence once, here, so both the protection
# auto-detect (below) and the user-facing remediation hints reuse the result
# instead of re-cd-ing and re-probing. Restrict to refs/heads/* so a same-named
# tag can't be mistaken for the branch. Each probe runs in a SUBSHELL so the
# script's own CWD is never changed (the rest of the hook resolves paths
# absolutely; a stray cd here would be a latent footgun).
DEV_EXISTS=false
DRAFT_EXISTS=false
( cd "$PROJECT_ROOT" 2>/dev/null && git rev-parse --verify refs/heads/dev   &>/dev/null ) && DEV_EXISTS=true
( cd "$PROJECT_ROOT" 2>/dev/null && git rev-parse --verify refs/heads/draft &>/dev/null ) && DRAFT_EXISTS=true

# Integration branch name: 'dev' for most repos, 'draft' for research repos
# (~/projects/research/*). Used in user-facing remediation hints below (which
# only render on main/master). Defaults to 'dev'; switched to 'draft' only when
# 'dev' is absent but 'draft' exists.
INTEGRATION_BRANCH="dev"
if [[ "$DEV_EXISTS" == false && "$DRAFT_EXISTS" == true ]]; then
  INTEGRATION_BRANCH="draft"
fi

CONFIG_FILE="${PROJECT_ROOT}/.claude/branch-guard.json"

USE_CONFIG=false
if [[ -f "$CONFIG_FILE" ]]; then
  # Validate and parse config file
  CONFIG_CONTENT="$(cat "$CONFIG_FILE")"
  if command -v jq &>/dev/null && ! printf '%s' "$CONFIG_CONTENT" | jq -e . &>/dev/null; then
    echo "[branch-guard] WARNING: Invalid JSON in $CONFIG_FILE — using auto-detect" >&2
  else
    USE_CONFIG=true
    # Look up current branch directly in the config (supports any branch name)
    PROTECTION="$(_json_get ".\"${BRANCH}\"" "$CONFIG_CONTENT")"
  fi
  # If current branch not found in config, no protection.
  # Custom config is EXPLICIT and authoritative — only branches it lists are
  # protected. This intentionally overrides auto-detection: a research repo that
  # adds a `.claude/branch-guard.json` must list "draft" (and/or "dev") itself to
  # keep integration-branch protection. We do NOT silently merge auto-detected
  # smart protection on top, because that could override a deliberate opt-out
  # (e.g. an explicit `"dev": ""`). Auto-detect (no config) still covers draft.
fi

if [[ "$USE_CONFIG" == false ]]; then
  # Auto-detect: does an integration branch ('dev' or research 'draft') exist?
  # Reuses the presence probe done once above.
  MAIN_PROTECTION="block-all"
  DEV_PROTECTION=""
  if [[ "$DEV_EXISTS" == true || "$DRAFT_EXISTS" == true ]]; then
    DEV_PROTECTION="smart"
  fi

  # Determine which protection level applies to current branch.
  # 'draft' is the research-repo integration branch — treated exactly like 'dev'.
  PROTECTION=""
  case "$BRANCH" in
    main|master)
      PROTECTION="$MAIN_PROTECTION"
      ;;
    dev|develop|draft)
      PROTECTION="$DEV_PROTECTION"
      ;;
    feature/*|feat/*|fix/*|hotfix/*|bugfix/*|refactor/*|chore/*|docs/*|test/*)
      # Feature branches and common prefixes — no protection
      PROTECTION=""
      ;;
    *)
      # Any other branch — no protection
      PROTECTION=""
      ;;
  esac
fi

# ---------------------------------------------------------------------------
# 6b. Normalize protection level aliases
# ---------------------------------------------------------------------------
case "$PROTECTION" in
  block-new-code|confirm) PROTECTION="smart" ;;
esac

# ---------------------------------------------------------------------------
# 7. One-shot marker check (smart mode only)
# ---------------------------------------------------------------------------
if [[ "$PROTECTION" == "smart" ]]; then
  ONCE_MARKER="${PROJECT_ROOT}/.claude/allow-once"
  if [[ -f "$ONCE_MARKER" ]]; then
    # TTL: expire one-shot markers older than 5 minutes (300 seconds)
    MARKER_NOW=$(date +%s)
    MARKER_MTIME=0
    if MARKER_MTIME=$(stat -f %m "$ONCE_MARKER" 2>/dev/null); then
      : # macOS
    elif MARKER_MTIME=$(stat -c %Y "$ONCE_MARKER" 2>/dev/null); then
      : # Linux
    else
      MARKER_MTIME=$MARKER_NOW  # Can't stat — treat as fresh
    fi
    MARKER_AGE=$(( MARKER_NOW - MARKER_MTIME ))
    if (( MARKER_AGE > 300 )); then
      # Expired — delete without allowing
      rm -f "$ONCE_MARKER"
      # Fall through to normal risk classification
    else
      rm -f "$ONCE_MARKER"
      exit 0
    fi
  fi
fi

# ---------------------------------------------------------------------------
# 7b. Session counter functions (smart mode)
# ---------------------------------------------------------------------------
SESSION_FILE="${PROJECT_ROOT}/.claude/guard-session-counts"

_session_count() {
  local action_type="$1"
  [[ -f "$SESSION_FILE" ]] || { echo 0; return; }
  # Age out: reset if older than 8 hours (28800 seconds)
  local now mtime age
  now=$(date +%s)
  if mtime=$(stat -f %m "$SESSION_FILE" 2>/dev/null); then
    : # macOS stat worked
  elif mtime=$(stat -c %Y "$SESSION_FILE" 2>/dev/null); then
    : # Linux stat worked
  else
    mtime=0
  fi
  age=$(( now - mtime ))
  if (( age > 28800 )); then
    rm -f "$SESSION_FILE"
    echo 0; return
  fi
  # Re-check existence (another hook may have deleted during age-out window)
  [[ -f "$SESSION_FILE" ]] || { echo 0; return; }
  local c=0
  c=$(grep -c "^${action_type}$" "$SESSION_FILE" 2>/dev/null) || true
  echo "$c"
}

_session_increment() {
  local action_type="$1"
  mkdir -p "$(dirname "$SESSION_FILE")"
  # Use flock for atomic append (prevents corruption from concurrent hooks)
  if command -v flock &>/dev/null; then
    (
      flock -x 200
      echo "$action_type" >> "$SESSION_FILE"
    ) 200>"${SESSION_FILE}.lock"
  else
    # macOS: flock not available by default, use simple append
    # (append to a file is atomic on most filesystems for small writes)
    echo "$action_type" >> "$SESSION_FILE"
  fi
}

_verbosity() {
  local count="$1"
  if (( count == 0 )); then echo "full"
  elif (( count <= 2 )); then echo "brief"
  else echo "minimal"
  fi
}

# ---------------------------------------------------------------------------
# 8. Helper: block or dry-run
# ---------------------------------------------------------------------------
# --classify / GUARD_DRY_RUN=1: a SEPARATE, additive ground-truth mode (not to
# be confused with the existing .claude/branch-guard-dryrun marker file above).
# When active, block()/_confirm()/_low_note() print the tier that WOULD have
# fired (BLOCK/ASK/ALLOW) to stdout and return/exit 0 without ever emitting the
# real stderr+exit-2 blocking contract. This reuses the existing call sites —
# it does not duplicate the classification logic — so skills/dev/git/ Op 12's
# `explain` subcommand and the dogfood test tier get ground truth instead of
# LLM narration (SPEC-branch-protection-consolidation-2026-07-07 §4.6 #3).
CLASSIFY_MODE=false
if [[ "${GUARD_DRY_RUN:-0}" == "1" ]] || [[ "${1:-}" == "--classify" ]]; then
  CLASSIFY_MODE=true
fi
CLASSIFY_EMITTED=false
if [[ "$CLASSIFY_MODE" == true ]]; then
  # Safety net: every path in the script eventually does a bare `exit 0`
  # ("allow"). Rather than instrument each call site, print a fallback ALLOW
  # line on exit if block()/_low_note() haven't already emitted a classify line.
  trap '[[ "$CLASSIFY_EMITTED" == true ]] || echo "ALLOW: no rule matched (fell through to default allow)"' EXIT
fi

block() {
  local message="$1"
  local tier="${2:-BLOCK}"
  if [[ "$CLASSIFY_MODE" == true ]]; then
    # Print only the tier + first non-empty text line — keeps classify output terse.
    local summary
    summary="$(printf '%b' "$message" | sed -E 's/\x1b\[[0-9;]*m//g' | grep -m1 '[A-Za-z0-9]')"
    CLASSIFY_EMITTED=true
    echo "${tier}: ${summary}"
    exit 0
  fi
  if [[ "$DRY_RUN" == true ]]; then
    echo "[DRY-RUN] branch-guard would block: $message" >&2
    exit 0
  else
    printf '%b\n' "$message" >&2
    exit 2
  fi
}

# ---------------------------------------------------------------------------
# 8b. Inline box-drawing helpers (standalone — no external dependency)
# ---------------------------------------------------------------------------
_W=63  # visible width (matches formatting.sh convention)
_TL='╔' _TR='╗' _BL='╚' _BR='╝'
_H='═' _V='║' _ML='╠' _MR='╣'
_R='\033[1;31m' _G='\033[0;32m' _Y='\033[1;33m'
_C='\033[1;36m' _B='\033[1m' _D='\033[2m' _N='\033[0m'

_hr() {
  local l="$1" r="$2" pad=""
  pad="$(printf '%0.s═' $(seq 1 $((_W - 2))))"
  printf '%s%s%s\n' "$l" "$pad" "$r"
}
_row() {
  local txt="$1"
  # Strip ANSI for width measurement
  local plain
  plain="$(printf '%b' "$txt" | sed $'s/\033\[[0-9;]*m//g')"
  local len=${#plain}
  local gap=$((_W - 3 - len))
  if (( gap < 0 )); then gap=0; fi
  printf '%s %b%*s%s\n' "$_V" "$txt" "$gap" "" "$_V"
}
_empty() { printf '%s%*s%s\n' "$_V" "$((_W - 2))" "" "$_V"; }

# Build a formatted block message
# Usage: _box "line1" "line2" ...
# Special lines: "---" inserts a mid-rule (╠═══╣)
_box() {
  local msg=""
  msg+="$(_hr "$_TL" "$_TR")"$'\n'
  for line in "$@"; do
    if [[ "$line" == "---" ]]; then
      msg+="$(_hr "$_ML" "$_MR")"$'\n'
    elif [[ "$line" == "" ]]; then
      msg+="$(_empty)"$'\n'
    else
      msg+="$(_row "$line")"$'\n'
    fi
  done
  msg+="$(_hr "$_BL" "$_BR")"
  printf '%s' "$msg"
}

# ---------------------------------------------------------------------------
# 8c. Smart mode helpers: confirm (MEDIUM) and low_note (LOW)
# ---------------------------------------------------------------------------

# _confirm: MEDIUM risk — teaching box + [CONFIRM] protocol, then exit 2
# Usage: _confirm action_type action_desc risk_reason suggestion1 [suggestion2 ...]
_confirm() {
  local action_type="$1"
  local action_desc="$2"
  local risk_reason="$3"
  shift 3
  local suggestions=("$@")

  local count verbosity msg
  count=$(_session_count "$action_type") || true
  verbosity=$(_verbosity "$count")
  _session_increment "$action_type"

  msg=""
  case "$verbosity" in
    full)
      # Full teaching box
      local box_lines=()
      box_lines+=("${_C}${_B}BRANCH GUARD — Medium Risk${_N}")
      box_lines+=("---")
      box_lines+=("")
      box_lines+=("${_D}Action:${_N}  ${action_desc}")
      box_lines+=("")
      box_lines+=("${_D}Why risky:${_N}")
      box_lines+=("  ${risk_reason}")
      box_lines+=("")
      box_lines+=("${_D}Safe alternatives:${_N}")
      for s in "${suggestions[@]}"; do
        box_lines+=("  ${_Y}→${_N} ${s}")
      done
      box_lines+=("")
      msg="$(_box "${box_lines[@]}")"
      # Structured [CONFIRM] message
      msg+=$'\n'
      msg+="[CONFIRM] ${risk_reason}"$'\n'
      msg+="Action:    ${action_desc}"$'\n'
      msg+="Risk:      ${risk_reason}"$'\n'
      for s in "${suggestions[@]}"; do
        msg+="Suggest:   ${s}"$'\n'
      done
      msg+="Branch:    ${BRANCH} (smart mode)"$'\n'
      msg+="Verbosity: full (1st encounter)"
      ;;
    brief)
      # Brief box
      msg="$(_box \
        "${_C}${_B}BRANCH GUARD${_N}" \
        "---" \
        "${_D}Action:${_N}  ${action_desc}" \
        "${_D}Risk:${_N}    ${risk_reason}" \
        "${_D}Branch:${_N}  ${BRANCH} (smart mode)" \
      )"
      msg+=$'\n'
      msg+="[CONFIRM] ${action_desc} on ${BRANCH}."$'\n'
      msg+="Action:  ${action_desc}"$'\n'
      msg+="Risk:    ${risk_reason}"$'\n'
      msg+="Branch:  ${BRANCH} (smart mode)"
      ;;
    minimal)
      # One-liner
      msg="[CONFIRM] ${action_desc} on ${BRANCH}. Allow?"
      ;;
  esac

  msg+=$'\n'"To mute: ask \"disable branch-guard\" (dev/git skill)"

  block "$msg" "ASK"
}

# _low_note: LOW risk — brief note on first encounter, then silent
# Usage: _low_note action_type note_message
_low_note() {
  local action_type="$1"
  local note="$2"
  if [[ "$CLASSIFY_MODE" == true ]]; then
    CLASSIFY_EMITTED=true
    echo "ALLOW: ${note}"
    exit 0
  fi
  local count
  count=$(_session_count "$action_type") || true
  if (( count == 0 )); then
    printf '%b\n' "${_D}[guard]${_N} ${note}" >&2
  fi
  _session_increment "$action_type"
  exit 0
}

# _hard_block: HIGH risk — hard block, no [CONFIRM] (not confirmable)
# Usage: _hard_block box_lines...
_hard_block() {
  block "$(_box "$@")" "BLOCK"
}

# ---------------------------------------------------------------------------
# 8d0. Bash cross-context target resolution (leading cd / -C) — 2026-07-14
# ---------------------------------------------------------------------------
# Everything below classifies $COMMAND against the SESSION's own
# BRANCH/PROTECTION/PROJECT_ROOT. That's wrong when the command itself
# retargets a different directory via a leading `cd <path> &&`/`cd <path>;`
# or a `git -C <path>` flag — a worktree push, or a genuinely different
# repository. The session's own branch is not the right gate for someone
# else's checkout. This block detects that shape, resolves the ACTUAL
# target, and rebinds classification context to it.
#
# Scope (v2, documented — see GRILL-branch-guard-target-resolution-
# 2026-07-14.md open questions): CUMULATIVE cd/-C tracking across a compound
# command's clauses — each bare `cd <path>` retargets every subsequent clause
# (so `cd a && cd b && git push` resolves to b), and a `git -C <path>` sets that
# invocation's target; the LAST retarget wins. Still NOT full quote-aware shell
# parsing: a `;`/`&&`/`|` separator INSIDE a quoted arg (e.g. a commit message
# `-m "wip; cd /x"`) can be mis-split — mitigated by skipping quote-bearing
# paths and by the -d/git-repo/branch re-derivation guards below (a spurious
# target that isn't a real git repo on a different branch is simply ignored).
# Custom per-repo `.claude/branch-guard.json` in the OTHER repo is not consulted
# here (auto-detect protection only) — a documented limitation, not a silent gap.
IS_CROSS_REPO_TARGET=false
if [[ ( "$TOOL_NAME" == "Bash" || "$TOOL_NAME" == "bash" ) && -n "$COMMAND" ]]; then
  _BG_TARGET_DIR=""

  # Walk clauses left-to-right, tracking the effective cwd cumulatively.
  # awk gsub emits a REAL newline on BSD & GNU (BSD sed's `\n` does not).
  # Single `|` also splits so a piped `grep -C N` can't be misread as `git -C`.
  _bg_eff="$CWD"
  _bg_norm="$(printf '%s' "$COMMAND" | awk '{gsub(/&&|[;|]/,"\n"); print}')"
  while IFS= read -r _bg_clause; do
    _bg_clause="${_bg_clause#"${_bg_clause%%[![:space:]]*}"}"  # trim leading ws
    if printf '%s' "$_bg_clause" | grep -qE '^cd[[:space:]]+[^[:space:]]+'; then
      _bg_p="$(printf '%s' "$_bg_clause" | sed -E 's/^cd[[:space:]]+//' | awk '{print $1}')"
      case "$_bg_p" in ''|*'$'*|*'`'*|*'"'*|*"'"*) _bg_p="" ;; esac
      if [[ -n "$_bg_p" ]]; then
        [[ "$_bg_p" != /* ]] && _bg_p="${_bg_eff%/}/$_bg_p"
        _bg_eff="$_bg_p"; _BG_TARGET_DIR="$_bg_p"
      fi
    elif printf '%s' "$_bg_clause" | grep -qE '(^|[[:space:]])git([[:space:]]|$)' \
      && printf '%s' "$_bg_clause" | grep -qE '(^|[[:space:]])-C[[:space:]]+[^[:space:]]+'; then
      _bg_p="$(printf '%s' "$_bg_clause" | grep -oE '(^|[[:space:]])-C[[:space:]]+[^[:space:]]+' | head -1 | sed -E 's/^[[:space:]]*-C[[:space:]]+//')"
      case "$_bg_p" in ''|*'$'*|*'`'*|*'"'*|*"'"*) _bg_p="" ;; esac
      if [[ -n "$_bg_p" ]]; then
        [[ "$_bg_p" != /* ]] && _bg_p="${_bg_eff%/}/$_bg_p"
        _BG_TARGET_DIR="$_bg_p"
      fi
    fi
  done <<EOF
$_bg_norm
EOF

  if [[ -n "$_BG_TARGET_DIR" && -d "$_BG_TARGET_DIR" ]]; then
    _BG_TARGET_ROOT="$(cd "$_BG_TARGET_DIR" 2>/dev/null && git rev-parse --show-toplevel 2>/dev/null || true)"
    if [[ -n "$_BG_TARGET_ROOT" ]]; then
      _BG_TARGET_BRANCH="$(cd "$_BG_TARGET_DIR" 2>/dev/null && git branch --show-current 2>/dev/null || true)"
      if [[ -n "$_BG_TARGET_BRANCH" && ( "$_BG_TARGET_ROOT" != "$PROJECT_ROOT" || "$_BG_TARGET_BRANCH" != "$BRANCH" ) ]]; then
        [[ "$_BG_TARGET_ROOT" != "$PROJECT_ROOT" ]] && IS_CROSS_REPO_TARGET=true

        BRANCH="$_BG_TARGET_BRANCH"
        PROJECT_ROOT="$_BG_TARGET_ROOT"
        PROJECT_NAME="$(basename "$PROJECT_ROOT")"

        _bg_dev=false _bg_draft=false
        ( cd "$PROJECT_ROOT" 2>/dev/null && git rev-parse --verify refs/heads/dev   &>/dev/null ) && _bg_dev=true
        ( cd "$PROJECT_ROOT" 2>/dev/null && git rev-parse --verify refs/heads/draft &>/dev/null ) && _bg_draft=true
        INTEGRATION_BRANCH="dev"
        [[ "$_bg_dev" == false && "$_bg_draft" == true ]] && INTEGRATION_BRANCH="draft"

        _bg_main_p="block-all" _bg_dev_p=""
        [[ "$_bg_dev" == true || "$_bg_draft" == true ]] && _bg_dev_p="smart"
        case "$BRANCH" in
          main|master) PROTECTION="$_bg_main_p" ;;
          dev|develop|draft) PROTECTION="$_bg_dev_p" ;;
          *) PROTECTION="" ;;
        esac
      fi
    fi
  fi
fi

# ---------------------------------------------------------------------------
# 8d. Universal catastrophic checks (ALL branches, before protection filter)
# ---------------------------------------------------------------------------
if [[ "$TOOL_NAME" == "Bash" || "$TOOL_NAME" == "bash" ]]; then
  # rm -rf .git — HIGH risk everywhere (destroys entire repository)
  # Catches: rm -rf .git, rm -fr .git, rm -Rf .git, rm -r -f .git, etc.
  if echo "$COMMAND" | grep -qE 'rm[[:space:]]+-[rfRF]*[[:space:]]*((-[rfRF]+[[:space:]]+)*)\.git([[:space:]]|/|$)'; then
    _confirm "git_destroy" \
      "rm -rf .git (destroy entire git repository)" \
      "Permanently destroys the entire .git directory and all git history" \
      "git stash, git bundle, or backup first" \
      "This action cannot be undone — all commits/branches lost"
  fi

  # git branch -D — MEDIUM risk everywhere (deletes unmerged branches)
  if echo "$COMMAND" | grep -qE '(^|;|&&|\|\|)[[:space:]]*git[[:space:]]+branch[[:space:]]+(-D|--delete[[:space:]]+--force|--force[[:space:]]+--delete)'; then
    # Squash-merge check: if all commits are already in the integration branch,
    # the branch is safe to force-delete without confirmation.
    _DEL_BRANCH="$(echo "$COMMAND" | sed -n 's/.*git branch -D \([^[:space:];|&]*\).*/\1/p' 2>/dev/null || true)"
    if [[ -n "$_DEL_BRANCH" ]] && command -v is_squash_merged &>/dev/null; then
      _SQUASH_STATUS="$(cd "$CWD" 2>/dev/null && is_squash_merged "${INTEGRATION_BRANCH:-dev}" "$_DEL_BRANCH" 2>/dev/null || echo "UNKNOWN")"
      if [[ "$_SQUASH_STATUS" == "SAFE" ]]; then
        # All commits already in base — squash-merge confirmed, allow force-delete
        printf '\n\033[33m[branch-guard]\033[0m Squash-merge confirmed for \033[1m%s\033[0m — allowing force-delete\n' "$_DEL_BRANCH" >&2
        exit 0
      fi
    fi
    _confirm "branch_delete" \
      "git branch -D (force delete)" \
      "Force-deletes branch even if not merged — commits may be lost" \
      "git branch -d (safe delete — only if merged)" \
      "git log <branch> to check for unmerged work"
  fi
fi

# ---------------------------------------------------------------------------
# 8e. Check bypass marker (after 8d — allow-dev-edit can skip smart-mode
#     risk classification below, but never the catastrophic checks above)
# ---------------------------------------------------------------------------
if [[ -f "${PROJECT_ROOT}/.claude/allow-dev-edit" ]]; then
  exit 0
fi

# No protection for this branch — allow everything
[[ -z "$PROTECTION" ]] && exit 0

# ---------------------------------------------------------------------------
# 9. Apply protection: block-all (main branch)
# ---------------------------------------------------------------------------
if [[ "$PROTECTION" == "block-all" ]]; then
  case "$TOOL_NAME" in
    Edit|edit)
      block "$(_box \
        "${_R}${_B}BRANCH PROTECTION${_N}" \
        "---" \
        "Cannot edit files on ${_B}${BRANCH}${_N}." \
        "" \
        "${_D}File:${_N}   ${_C}${FILE_PATH}${_N}" \
        "${_D}Branch:${_N} ${BRANCH} (block-all)" \
        "---" \
        "${_Y}→ git checkout ${INTEGRATION_BRANCH}${_N}" \
      )"
      ;;

    Write|write)
      block "$(_box \
        "${_R}${_B}BRANCH PROTECTION${_N}" \
        "---" \
        "Cannot write files on ${_B}${BRANCH}${_N}." \
        "" \
        "${_D}File:${_N}   ${_C}${FILE_PATH}${_N}" \
        "${_D}Branch:${_N} ${BRANCH} (block-all)" \
        "---" \
        "${_Y}→ git checkout ${INTEGRATION_BRANCH}${_N}" \
      )"
      ;;

    Bash|bash)
      # Check for destructive git commands
      if echo "$COMMAND" | grep -qE '(^|;|&&|\|\|)[[:space:]]*git[[:space:]]+(-C[[:space:]]+[^[:space:]]+[[:space:]]+)?(commit|push)'; then
        if [[ "$IS_CROSS_REPO_TARGET" == true ]]; then
          # Cross-repo target resolved to a protected branch (e.g. another
          # repo's main) — confirm, never hard-block. The originating
          # session's own branch never authorized this, but a hard block
          # would also disrupt legitimate cross-repo work (explicit
          # decision: BRAINSTORM-branch-guard-target-resolution-2026-07-14,
          # "I do not want hard gate to disrupt").
          _confirm "cross_repo_protected_push" \
            "git commit/push on ${BRANCH} in a different repository (${PROJECT_NAME})" \
            "This command targets another repository's protected ${BRANCH} branch — the session's own branch is not a valid gate for that repo's state" \
            "Run this from a session/worktree already cd'd into ${PROJECT_ROOT}" \
            "Split into a separate Bash call scoped to that repo"
        else
          block "$(_box \
            "${_R}${_B}BRANCH PROTECTION${_N}" \
            "---" \
            "Cannot commit/push on ${_B}${BRANCH}${_N}." \
            "" \
            "Use the PR workflow:" \
            "  ${_Y}1.${_N} git checkout ${INTEGRATION_BRANCH}" \
            "  ${_Y}2.${_N} Create worktree for changes" \
            "  ${_Y}3.${_N} PR: feature → ${INTEGRATION_BRANCH} → main" \
          )"
        fi
      fi
      if echo "$COMMAND" | grep -qE '(^|;|&&|\|\|)[[:space:]]*git[[:space:]]+(-C[[:space:]]+[^[:space:]]+[[:space:]]+)?reset[[:space:]]+--hard'; then
        _confirm "reset_hard_main" \
          "git reset --hard on ${BRANCH} (protected branch)" \
          "Resets working tree and index to specified commit — discards all uncommitted changes" \
          "git stash (save changes) then reset" \
          "git reset --soft HEAD~1 (keep changes staged)"
      fi
      # All other bash commands are allowed
      exit 0
      ;;

    *)
      # Any other tool — allow
      exit 0
      ;;
  esac
fi

# ---------------------------------------------------------------------------
# 10. Apply protection: smart (dev branch — 3-tier risk classification)
#     Replaces the old block-new-code handler with teaching-first protection.
#     LOW = allow + optional note, MEDIUM = confirm + teaching, HIGH = hard block
# ---------------------------------------------------------------------------
if [[ "$PROTECTION" == "smart" ]]; then
  # Non-code / safe-to-create extensions (shared by Write handler and Bash
  # write-through detection). Denylist-of-safe, not allowlist-of-code: an
  # unrecognized extension (e.g. .swift, .rb, .go) now defaults to a MEDIUM
  # confirm rather than silently allowed — a fixed allowlist misses every
  # language it doesn't enumerate.
  NONCODE_EXTENSIONS="txt csv tsv log lock example sample css html htm png jpg jpeg gif svg webp ico bmp pdf woff woff2 ttf eot otf mp3 mp4 mov wav zip gz tar tgz"

  case "$TOOL_NAME" in
    Edit|edit)
      # Critical file check — MEDIUM risk (sensitive config/secrets)
      EDIT_BASENAME="$(basename "$FILE_PATH")"
      case "$EDIT_BASENAME" in
        .env|.env.*)
          _confirm "edit_env" \
            "Edit ${EDIT_BASENAME} on ${BRANCH}" \
            "Environment files may contain secrets — edits should be intentional" \
            "Copy .env to .env.local for local changes" \
            "Use a secrets manager for production values"
          ;;
      esac
      case "$FILE_PATH" in
        *.pem|*.key|*.secret)
          _confirm "edit_secret" \
            "Edit secret/key file: ${FILE_PATH}" \
            "Key/secret files should rarely be edited directly" \
            "Regenerate keys rather than editing" \
            "Check if file is in .gitignore"
          ;;
        */.claude/branch-guard.json|.claude/branch-guard.json)
          _confirm "edit_guard_config" \
            "Edit branch-guard.json on ${BRANCH}" \
            "Modifying guard config changes protection rules" \
            "ask \"set branch protection level <level>\" — safe config update (dev/git skill)" \
            "ask \"unprotect for a temporary bypass\" (dev/git skill)"
          ;;
        */.claude/allow-once|.claude/allow-once|*/.claude/allow-dev-edit|.claude/allow-dev-edit)
          _confirm "edit_guard_bypass" \
            "Edit guard-bypass marker on ${BRANCH}: $(basename "$FILE_PATH")" \
            "This file self-approves a bypass of branch-guard's own protection — never editable silently" \
            "ask \"unprotect\" — the sanctioned way to request this bypass (dev/git skill)"
          ;;
      esac
      # Editing existing files is always allowed on dev (LOW)
      _low_note "edit_existing" "Editing existing file on ${BRANCH} (allowed)"
      ;;

    Write|write)
      # Critical file check — MEDIUM risk (sensitive config/secrets)
      WRITE_BASENAME="$(basename "$FILE_PATH")"
      case "$WRITE_BASENAME" in
        .env|.env.*)
          _confirm "write_env" \
            "Write ${WRITE_BASENAME} on ${BRANCH}" \
            "Environment files may contain secrets — writes should be intentional" \
            "Copy .env to .env.local for local changes" \
            "Use a secrets manager for production values"
          ;;
      esac
      case "$FILE_PATH" in
        *.pem|*.key|*.secret)
          _confirm "write_secret" \
            "Write secret/key file: ${FILE_PATH}" \
            "Key/secret files should rarely be written directly" \
            "Use a key generation tool instead" \
            "Check if file is in .gitignore"
          ;;
        */.claude/branch-guard.json|.claude/branch-guard.json)
          _confirm "write_guard_config" \
            "Write branch-guard.json on ${BRANCH}" \
            "Modifying guard config changes protection rules" \
            "ask \"set branch protection level <level>\" — safe config update (dev/git skill)" \
            "ask \"unprotect for a temporary bypass\" (dev/git skill)"
          ;;
        */.claude/allow-once|.claude/allow-once|*/.claude/allow-dev-edit|.claude/allow-dev-edit)
          _confirm "write_guard_bypass" \
            "Write guard-bypass marker on ${BRANCH}: $(basename "$FILE_PATH")" \
            "Creating this file self-approves a bypass of branch-guard's own protection — must be a deliberate, confirmed action, never a silent allow" \
            "ask \"unprotect\" — the sanctioned way to request this bypass (dev/git skill)"
          ;;
      esac

      # Markdown files — always allowed (LOW)
      if [[ "$FILE_PATH" == *.md ]]; then
        _low_note "write_md" "New markdown on ${BRANCH} (always allowed)"
      fi

      # Extension-less files (no dot in basename) — allowed (LOW)
      # Examples: .STATUS, Makefile, Dockerfile, LICENSE
      BASENAME="$(basename "$FILE_PATH")"
      if [[ "$BASENAME" != *.* ]] || [[ "$BASENAME" == .* && "${BASENAME#.}" != *.* ]]; then
        _low_note "write_extensionless" "Extension-less file (allowed): ${BASENAME}"
      fi

      # Files in tests/ directory — allowed (LOW)
      if echo "$FILE_PATH" | grep -qE '(^|/)tests/'; then
        _low_note "write_test" "Test files on ${BRANCH} (always allowed)"
      fi

      # Determine the actual file path (could be relative or absolute)
      ACTUAL_PATH="$FILE_PATH"
      if [[ "$FILE_PATH" != /* ]]; then
        ACTUAL_PATH="${CWD}/${FILE_PATH}"
      fi

      # Existing file (overwrite/fixup) — allowed (LOW)
      if [[ -f "$ACTUAL_PATH" ]]; then
        _low_note "write_existing" "Overwriting existing file on ${BRANCH} (allowed)"
      fi

      # Also check relative to project root
      if [[ -f "${PROJECT_ROOT}/${FILE_PATH}" ]]; then
        _low_note "write_existing" "Overwriting existing file on ${BRANCH} (allowed)"
      fi

      # New code file — determine extension. Default-suspect: everything
      # not in NONCODE_EXTENSIONS is treated as code (see definition above).
      EXT="${FILE_PATH##*.}"

      IS_CODE=true
      for ext in $NONCODE_EXTENSIONS; do
        if [[ "$EXT" == "$ext" ]]; then
          IS_CODE=false
          break
        fi
      done

      if [[ "$IS_CODE" == true ]]; then
        # MEDIUM risk — new code file on protected branch
        _confirm "write_new_code" \
          "Write new .${EXT} file: ${FILE_PATH}" \
          "New code files on ${BRANCH} should go in a feature branch" \
          "Ask Claude to create a worktree (dev/git skill): feature/<name>" \
          "Edit an existing file instead (fixups allowed)" \
          "ask \"unprotect for bulk maintenance\" (dev/git skill)"
      fi

      # Known-safe non-code extension (NONCODE_EXTENSIONS) — allow
      exit 0
      ;;

    Bash|bash)
      # Force push — MEDIUM risk
      if echo "$COMMAND" | grep -qE '(^|;|&&|\|\|)[[:space:]]*git[[:space:]]+(-C[[:space:]]+[^[:space:]]+[[:space:]]+)?push[[:space:]].*(--force|--force-with-lease|-f)([[:space:]]|$)'; then
        _confirm "force_push" \
          "git push --force on ${BRANCH}" \
          "Force push overwrites remote history for all collaborators" \
          "git push origin ${BRANCH} (regular push)" \
          "git push --force-with-lease (safer — checks remote)" \
          "Ask Claude to create a worktree (dev/git skill) to isolate changes"
      fi

      # git reset --hard — MEDIUM risk (discards uncommitted changes)
      if echo "$COMMAND" | grep -qE '(^|;|&&|\|\|)[[:space:]]*git[[:space:]]+(-C[[:space:]]+[^[:space:]]+[[:space:]]+)?reset[[:space:]]+--hard'; then
        _confirm "reset_hard" \
          "git reset --hard on ${BRANCH}" \
          "Discards all uncommitted changes — cannot be undone" \
          "git stash (save changes for later)" \
          "git reset --soft (keep changes staged)" \
          "git diff to review what would be lost"
      fi

      # git clean -f (remove untracked files) — MEDIUM risk
      if echo "$COMMAND" | grep -qE '(^|;|&&|\|\|)[[:space:]]*git[[:space:]]+(-C[[:space:]]+[^[:space:]]+[[:space:]]+)?clean[[:space:]]+(-[fdxFDX]+|--force)'; then
        _confirm "clean_force" \
          "git clean -f (remove untracked files) on ${BRANCH}" \
          "Permanently removes untracked files — cannot be undone" \
          "git clean -n (dry run — see what would be removed)" \
          "git stash -u (stash including untracked files)"
      fi

      # ---------------------------------------------------------------
      # Bash write-through detection (file creation via redirection)
      # Catches: echo/cat/printf > file, tee file, cp src dst
      # Skips: markdown files, variables in paths, existing files
      # ---------------------------------------------------------------
      BASH_TARGET=""

      # Heredoc bodies (e.g. `git commit -m "$(cat <<'EOF' ... EOF)"`) are
      # free-form text that can contain a literal '>' with no relation to a
      # real redirect (e.g. "orchestrate->orch" in a commit message) — skip
      # Pattern 1 when a heredoc marker is present to avoid false-positiving
      # on prose text scanned as if it were shell syntax.
      HAS_HEREDOC=false
      if echo "$COMMAND" | grep -qE '<<-?["'"'"']?[A-Za-z_][A-Za-z0-9_]*["'"'"']?'; then
        HAS_HEREDOC=true
      fi

      # Pattern 1: redirect to file (>, >>)  e.g. "echo x > file.py", "cat > file.py"
      # The `|| true` on each extraction below is load-bearing under this
      # script's `set -euo pipefail`: the coarse guard (grep -q, above) and
      # the fine extraction pattern (grep -o, below) aren't always in sync —
      # e.g. "cat file 2>&1" passes the coarse '>' check but the fine
      # pattern excludes '&', so grep -o matches nothing and exits 1. In a
      # bare `VAR=$(pipeline)` assignment, pipefail propagates that 1 and
      # set -e kills the whole hook silently (no stderr) — exactly the
      # "no match" case the `[[ -z "$BASH_TARGET" ]]` checks below already
      # handle correctly. `|| true` makes a real no-match behave like the
      # empty-string fallback it was always meant to be, instead of a crash.
      if [[ "$HAS_HEREDOC" == false ]] && echo "$COMMAND" | grep -qE '>[[:space:]]*[^>]'; then
        # Extract the target after the last >
        BASH_TARGET="$(echo "$COMMAND" | grep -oE '>[[:space:]]*[^>|&;[:space:]]+' | tail -1 | sed 's/^>[[:space:]]*//' || true)"
      fi

      # Pattern 2: tee <file>  e.g. "echo x | tee file.py"
      # HAS_HEREDOC gate (see Pattern 1 comment above) applies here too —
      # grep is line-oriented, so a heredoc body line that happens to start
      # with "tee "/"touch "/contain "cp <word> <word>" as prose is
      # indistinguishable from real shell syntax without it.
      if [[ "$HAS_HEREDOC" == false ]] && [[ -z "$BASH_TARGET" ]] && echo "$COMMAND" | grep -qE 'tee[[:space:]]+[^-]'; then
        BASH_TARGET="$(echo "$COMMAND" | grep -oE 'tee[[:space:]]+(-a[[:space:]]+)?[^|;&[:space:]]+' | head -1 | sed 's/^tee[[:space:]]*\(-a[[:space:]]*\)\{0,1\}//' || true)"
      fi

      # Pattern 3: cp <src> <dst>  e.g. "cp template.py new.py"
      if [[ "$HAS_HEREDOC" == false ]] && [[ -z "$BASH_TARGET" ]] && echo "$COMMAND" | grep -qE 'cp[[:space:]]'; then
        BASH_TARGET="$(echo "$COMMAND" | grep -oE 'cp[[:space:]]+[^[:space:]]+[[:space:]]+([^|;&[:space:]]+)' | head -1 | awk '{print $NF}' || true)"
      fi

      # Pattern 4: touch <file>  e.g. "touch .claude/allow-once"
      # (extensionless targets like guard-bypass markers use touch, not
      # redirection — patterns 1-3 alone never see them)
      if [[ "$HAS_HEREDOC" == false ]] && [[ -z "$BASH_TARGET" ]] && echo "$COMMAND" | grep -qE '(^|;|&&|\|\|)[[:space:]]*touch[[:space:]]'; then
        BASH_TARGET="$(echo "$COMMAND" | grep -oE 'touch[[:space:]]+[^|;&[:space:]]+' | tail -1 | sed 's/^touch[[:space:]]*//' || true)"
      fi

      # Device/pseudo-file targets (2>/dev/null, >/dev/tty, etc.) are stream
      # redirects, not file creation — never classify these as new code.
      if [[ "$BASH_TARGET" == /dev/* ]]; then
        BASH_TARGET=""
      fi

      # If we found a target, check if it's a new code file
      if [[ -n "$BASH_TARGET" ]]; then
        # Skip if target contains variables ($, backticks) — can't resolve
        if echo "$BASH_TARGET" | grep -qE '[$`]'; then
          : # gracefully skip — can't determine actual path
        else
          BASH_BASENAME="$(basename "$BASH_TARGET")"
          BASH_EXT="${BASH_BASENAME##*.}"

          # Guard-bypass marker — never a silent shell-created allow (H1 fix)
          case "$BASH_BASENAME" in
            allow-once|allow-dev-edit)
              _confirm "bash_guard_bypass" \
                "Bash creates guard-bypass marker on ${BRANCH}: ${BASH_BASENAME}" \
                "Creating this file via shell self-approves a bypass of branch-guard's own protection" \
                "ask \"unprotect\" — the sanctioned way to request this bypass (dev/git skill)"
              ;;
          esac

          # Skip markdown — always allowed
          if [[ "$BASH_EXT" != "md" ]]; then
            # Default-suspect: code unless in NONCODE_EXTENSIONS (see above)
            BASH_IS_CODE=true
            for ext in $NONCODE_EXTENSIONS; do
              if [[ "$BASH_EXT" == "$ext" ]]; then
                BASH_IS_CODE=false
                break
              fi
            done

            if [[ "$BASH_IS_CODE" == true ]]; then
              # Check if file already exists (overwrite is OK)
              BASH_ACTUAL="$BASH_TARGET"
              [[ "$BASH_TARGET" != /* ]] && BASH_ACTUAL="${CWD}/${BASH_TARGET}"

              if [[ ! -f "$BASH_ACTUAL" ]] && [[ ! -f "${PROJECT_ROOT}/${BASH_TARGET}" ]]; then
                _confirm "bash_write_through" \
                  "Bash creates new .${BASH_EXT} file: ${BASH_TARGET}" \
                  "Shell redirection creates a new code file on ${BRANCH}" \
                  "Use the Write tool instead (tracked by guard)" \
                  "Ask Claude to create a worktree (dev/git skill) to isolate changes"
              fi
            fi
          fi
        fi
      fi

      # All other bash commands — allow
      exit 0
      ;;

    *)
      # Any other tool — allow
      exit 0
      ;;
  esac
fi

# If we get here, no rule matched — allow
exit 0
