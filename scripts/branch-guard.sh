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
# 0. Shared `git <global-flags>` prefix
# ---------------------------------------------------------------------------
# Matches `git ` plus any run of GLOBAL options that may legally precede the
# subcommand, so a gate keyed on the subcommand can't be walked past by
# inserting one. Two token shapes:
#   `-c k=v` / `-C <path>` — flag AND its value are separate tokens
#   `-P`, `--no-pager`, `--git-dir=x` — single self-contained token
# The two-token alternative is listed first and POSIX ERE leftmost-longest
# picks it over the one-token read of the same `-c` (same property #32/#36
# relied on for `&&` vs bare `&`) — verified against BSD/macOS `grep -E`.
#
# Before this existed each gate inlined `(-C <path>)?`, tolerating exactly one
# global flag. `git -c a=b commit` and `git --no-pager push` therefore failed
# the match and fell through to default allow on a protected branch — bypass
# #5 of the #32 review, fixed there only in the push-exemption path. Every
# gate below MUST use this variable; a new inline `git[[:space:]]+` prefix
# reintroduces the hole. See issue #41 and
# docs/specs/SPEC-guard-hardening-2026-08-08.md.
# A global option's VALUE may itself contain spaces when quoted
# (`-c user.name="Test User"`, `-c core.editor='vim -f'`) — this matches the
# raw command string, not shell-tokenized argv, so a value read as plain
# `[^[:space:]]+` stops at the first space, the run breaks, and the
# subcommand escapes the gate.
_BG_GIT_VAL='([^[:space:]]*("[^"]*"|'"'"'[^'"'"']*'"'"')[^[:space:]]*|[^[:space:]]+)'
# Global options whose value is a SEPARATE token. git accepts both
# `--git-dir=<path>` and `--git-dir <path>`; only the equals form is
# self-contained, so the space form needs listing here or it walks past.
#
# Found in cc-config#74 (ported from no-switch-guard.sh's GITPFX fix in #72,
# same construction, same gap): this list was still incomplete
# (--attr-source, --list-cmds missing — checked against `man git`'s GLOBAL
# OPTIONS) AND the generic single-token branch (`-[^[:space:]]+`) couldn't
# span a quoted `=`-joined value containing a space
# (`--git-dir="/path with space"`) — either gap fell through to default
# ALLOW on a protected branch, confirmed live against `git branch -D` and
# `git push --force` on `main` before this fix. Closing both: the flag list,
# and generalizing the single-token branch to `=`-joined quoted values so
# future undocumented-here two-token flags in `=`-form don't need listing.
_BG_GIT_TWO='(-[cC]|--git-dir|--work-tree|--namespace|--exec-path|--super-prefix|--config-env|--attr-source|--list-cmds)'
_BG_GIT="git[[:space:]]+((${_BG_GIT_TWO}[[:space:]]+${_BG_GIT_VAL}|-[^[:space:]=]+(=${_BG_GIT_VAL})?)[[:space:]]+)*"

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
# NotebookEdit uses a different schema (notebook_path, not file_path/filePath)
# — GRILL-pretooluse-cross-repo-write-path-2026-08-03.md finding 1: widening
# the settings.json matcher alone (without this) makes the hook silently
# allow every NotebookEdit write on a protected branch. Aliasing into
# FILE_PATH lets every existing FILE_PATH-keyed check (git-context
# resolution, outside-repo allow, per-tool dispatch below) cover it for
# free instead of duplicating that logic for a second variable.
if [[ -z "$FILE_PATH" && "$TOOL_NAME" == "NotebookEdit" ]]; then
  FILE_PATH="$(_json_get '.tool_input.notebook_path' "$INPUT")"
fi

# Extract command from tool_input (for Bash tool)
COMMAND="$(_json_get '.tool_input.command' "$INPUT")"

# _bg_blank_quoted: return $COMMAND with the CONTENTS of quoted segments
# replaced by spaces, so that clause separators (;, &&, |) appearing INSIDE a
# quoted argument are not mistaken for real shell separators.
#
# Why this exists (2026-09-04): the force-delete gate below anchors its match to
# `(^|;|&&|&|\|\|)`, but that anchor was tested against the raw command, so a
# separator sitting inside quoted DATA satisfied it. `jq --arg c "x && git
# branch -D y"` therefore confirmed as though a force-delete were being run,
# and so did a heredoc writing documentation that quoted the command. Both were
# observed blocking real work.
#
# Length and offsets are preserved (each blanked character becomes one space)
# so nothing is silently joined: `a"&&"b` stays three tokens wide, never `ab`.
#
# SAFETY: this is applied ONLY to the force-delete gate, never to the
# `rm -rf .git` gate. That check deliberately matches anywhere in the command
# with no separator anchor, so blanking quotes there would newly permit
# `bash -c "rm -rf .git"`, which is caught today. The force-delete gate has no
# such exposure: because it is separator-anchored, `bash -c "git branch -D x"`,
# `eval "..."` and `sh -c '...'` already fall through to allow (verified by
# probe, 2026-09-04). Blanking quotes therefore removes false positives without
# widening what escapes.
#
# FAIL-SAFE: on unbalanced quotes the awk program exits non-zero and the raw
# command is returned unchanged, so an unparseable command is still judged by
# the stricter original text.
_bg_blank_quoted() {
  local _bgq_out
  _bgq_out="$(printf '%s' "$1" | awk -v SQ="$(printf '\047')" '
    {
      n = length($0); out = ""; q = ""
      for (i = 1; i <= n; i++) {
        c = substr($0, i, 1)
        if (q == "") {
          if (c == "\"" || c == SQ) { q = c; out = out " " }
          else { out = out c }
        } else {
          # Backslash escape inside double quotes consumes the next character.
          if (c == "\\" && q == "\"" && i < n) { out = out "  "; i++ }
          else if (c == q) { q = ""; out = out " " }
          else { out = out " " }
        }
      }
      if (q != "") { exit 3 }
      print out
    }')" || { printf '%s' "$1"; return 0; }
  printf '%s' "$_bgq_out"
}

# Quote-blanked view of the command, used only by the force-delete gates.
COMMAND_UNQ="$(_bg_blank_quoted "$COMMAND")"

# --- Registry: check if this guard is enabled/muted -----------------------
# SAFETY: catastrophic ops (rm -rf .git, git branch -D) are NEVER muteable —
# the registry gate must not bypass the universal catastrophic checks (8d).
_GUARD_REG="${HOME}/.claude/guards.json"
if command -v jq &>/dev/null && [[ -f "$_GUARD_REG" ]]; then
  _bg_catastrophic=0
  if echo "$COMMAND" | grep -qE 'rm[[:space:]]+-[rfRF]*[[:space:]]*((-[rfRF]+[[:space:]]+)*)\.git([[:space:]]|/|$)' \
     || echo "$COMMAND_UNQ" | grep -qE '(^|;|&&|&|\|\|)[[:space:]]*'"${_BG_GIT}"'branch[[:space:]]+(-D|--delete[[:space:]]+--force|--force[[:space:]]+--delete)'; then
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

# Preserve the session's own resolved root before any later cross-repo
# retargeting (8d0 below) can overwrite $PROJECT_ROOT with the TARGET's
# root. Needed as the correct comparand for the git-common-dir worktree
# check in 8d0 — comparing against the by-then-clobbered $PROJECT_ROOT
# would self-compare the target to itself and always read "same repo"
# (GRILL-pretooluse-cross-repo-write-path-2026-08-03.md finding 2).
_BG_SESSION_ROOT="$PROJECT_ROOT"

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
  # Most call sites already name the branch in action_desc ("git clean -f ...
  # on ${BRANCH}"); only append it for the ones that don't, so the brief and
  # minimal lines never read "... on dev on dev." FILE_PATH is stripped before
  # matching: it is user-controlled, and a path like ".../notes on dev/x.pem"
  # must not suppress the branch on a prompt that doesn't otherwise name it.
  local on_branch=" on ${BRANCH}" fixed_desc="$action_desc"
  [[ -n "${FILE_PATH:-}" ]] && fixed_desc="${fixed_desc//"$FILE_PATH"/}"
  [[ "$fixed_desc" == *" on ${BRANCH}"* ]] && on_branch=""

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
      msg+="[CONFIRM] ${action_desc}${on_branch}."$'\n'
      msg+="Action:  ${action_desc}"$'\n'
      msg+="Risk:    ${risk_reason}"$'\n'
      msg+="Branch:  ${BRANCH} (smart mode)"
      ;;
    minimal)
      # One-liner
      msg="[CONFIRM] ${action_desc}${on_branch}. Allow?"
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

# _bg_push_refspec_safe: does this `git push` clause confidently avoid
# touching the protected branch? Only two forms are recognized as safe —
# `--delete <ref>` (one or more, git allows a list after one --delete) and
# an explicit `<src>:<dst>` refspec. Echoes SAFE only when every recognized
# destination ref is confirmed NOT the protected branch; a bare push, an
# unparseable clause, or ANY destination matching the protected branch
# (including deleting it outright) stays UNSAFE — callers must gate exactly
# as before in that case. Never widen this to bare-ref pushes (`git push
# origin <branch>`) without also resolving what a bare ref actually targets;
# that ambiguity is the reason bare pushes stay UNSAFE by design (issue #6).
_bg_push_refspec_safe() {
  local clause="$1" protected="$2"
  case "$clause" in *'$'*|*'`'*|*'"'*|*"'"*) echo "UNSAFE"; return ;; esac

  local -a _tokens
  read -ra _tokens <<< "$clause"
  local n=${#_tokens[@]} i=0

  # Skip everything through the literal `push` token — clause extraction can
  # prepend a compound-command separator (&&, ||, ;), `git`, and an optional
  # `-C <path>` pair, none of which are push arguments.
  while [[ $i -lt $n && "${_tokens[$i]}" != "push" ]]; do
    i=$((i+1))
  done
  i=$((i+1))

  # Per `git push [<repository> [<refspec>...]]`, the first non-flag token
  # after `push` is ALWAYS the repository (name or URL) — a refspec never
  # appears without it. It must never be read as a --delete target or a
  # <src>:<dst> refspec even though it can itself contain a colon (SCP-style
  # `user@host:path` remotes, `https://host:443/...` URLs) — excluding it
  # unconditionally is what makes those forms safe to parse, rather than
  # trying to pattern-match "looks like a URL" (which a hostile-shaped but
  # legitimate remote name could still evade).
  # Pre-scan (issue #44 finding 1): does --delete appear ANYWHERE in this
  # clause? Flags are not positional in git's argument parser — `git push
  # origin main --delete` deletes `main` exactly like `git push origin
  # --delete main` — so a bare ref token that appears BEFORE a trailing
  # --delete must still be treated as a delete target. Tracking this by
  # loop position (the previous approach) missed exactly that ordering.
  local global_delete=false
  local k=$i
  while [[ $k -lt $n ]]; do
    [[ "${_tokens[$k]}" == "--delete" ]] && { global_delete=true; break; }
    k=$((k+1))
  done

  local seen_remote=false saw_explicit_ref=false
  while [[ $i -lt $n ]]; do
    local tok="${_tokens[$i]}"
    if [[ "$seen_remote" == false && "$tok" != -* ]]; then
      seen_remote=true
      i=$((i+1))
      continue
    fi
    if [[ "$tok" == "--delete" ]]; then
      i=$((i+1))
      continue
    fi
    if [[ "$tok" == -* ]]; then
      # Any OTHER flag is never itself a refspec, even when its value
      # contains a colon — e.g. `--force-with-lease=main:0000...0`. Without
      # this, the colon check below would read the flag's value as a
      # <src>:<dst> refspec and only inspect the substring after ITS colon,
      # never the actual (implicit, bare) destination the push touches.
      i=$((i+1))
      continue
    fi
    # Every remaining token is classified explicitly below — an
    # unrecognized shape defaults to UNSAFE (issue #44 finding 2: a bare
    # ref used to fall through every case unclassified when it co-occurred
    # with an explicit `src:dst` refspec elsewhere in the same push,
    # silently skipping a real destination check).
    case "$tok" in
      *:*)
        saw_explicit_ref=true
        local dst="${tok#*:}"
        dst="${dst#refs/heads/}"
        dst="${dst#heads/}"
        [[ -z "$dst" || "$dst" == "$protected" ]] && { echo "UNSAFE"; return; }
        ;;
      *)
        if [[ "$global_delete" == true ]]; then
          saw_explicit_ref=true
          local ref="${tok#refs/heads/}"
          ref="${ref#heads/}"
          [[ "$ref" == "$protected" ]] && { echo "UNSAFE"; return; }
        else
          # Bare ref with no --delete in effect: its actual destination
          # depends on remote.*.push / push.default and is never provably
          # safe to infer here — stays UNSAFE by the same design as #6.
          echo "UNSAFE"; return
        fi
        ;;
    esac
    i=$((i+1))
  done

  [[ "$saw_explicit_ref" == true ]] && echo "SAFE" || echo "UNSAFE"
}

# _bg_command_push_only_safe: does $1 consist of NOTHING but an optional
# leading `cd <path>`/`git -C <path>` target-resolution prefix (already
# handled elsewhere for BRANCH/PROJECT_ROOT resolution) and EXACTLY ONE
# `git push` clause, with that one clause's refspec confirmed SAFE by
# _bg_push_refspec_safe? Any other clause — a second push, a `git commit`,
# an unrelated command riding along in the same compound string (`rm -rf
# x && git push ...`) — denies the exemption outright, falling back to the
# original gate exactly as if no refspec parsing existed. This is
# deliberately stricter than classifying each clause independently: doing
# that missed that (1) a co-riding `git commit` can itself be disguised
# (e.g. `git -c commit.gpgsign=false commit`) past a narrower "is there a
# commit clause" regex, and (2) the ORIGINAL coarse trigger's only real
# virtue was blocking the ENTIRE Bash invocation — including anything else
# riding in the same compound command — the instant it saw commit/push
# anywhere; per-clause safety analysis silently gave that up. Restricting
# the exemption to "provably nothing else is happening in this command"
# preserves that side-effect while still fixing issue #6's actual
# reproduction (a bare push, optionally cd/-C prefixed).
_bg_command_push_only_safe() {
  local cmd="$1" protected="$2"
  local push_count=0 push_clause="" other_seen=false

  # &&, ;, |, and a bare & (background operator) all separate independent
  # clauses. Listing &&/& as separate alternatives (rather than omitting
  # bare &) relies on POSIX ERE leftmost-longest matching to prefer && as a
  # whole over its own first character when both are present — verified
  # against this awk (macOS/BSD): a lone & without this was previously
  # unsplit, letting a co-riding command fused via `push ... & rm -rf x`
  # tokenize straight through as if it were part of the push clause.
  local _norm
  _norm="$(printf '%s' "$cmd" | awk '{gsub(/&&|&|[;|]/,"\n"); print}')"
  while IFS= read -r _clause; do
    _clause="${_clause#"${_clause%%[![:space:]]*}"}"
    [[ -z "$_clause" ]] && continue
    if printf '%s' "$_clause" | grep -qE '^cd[[:space:]]+[^[:space:]]+[[:space:]]*$'; then
      continue
    fi
    if printf '%s' "$_clause" | grep -qE "^${_BG_GIT}"'push([[:space:]]|$)'; then
      push_count=$((push_count + 1))
      push_clause="$_clause"
      continue
    fi
    other_seen=true
  done <<EOF
$_norm
EOF

  if [[ "$other_seen" == true || "$push_count" -ne 1 ]]; then
    echo "UNSAFE"
    return
  fi
  _bg_push_refspec_safe "$push_clause" "$protected"
}

# _dev_edit_preauthorized: env-var escape hatch for creating/editing the
# allow-once/allow-dev-edit guard-bypass marker itself (issue #281). Same
# shape as issue #168's CRAFT_GUARD_ALLOW_FORCE_DELETE: /craft:git:unprotect
# collects human consent via AskUserQuestion, then tries to write the marker
# _confirm() needs — but writing that marker is itself intercepted by this
# same _confirm() gate, and in a non-interactive/auto-mode session there is
# no way for the already-given consent to resolve the resulting exit-2 block
# (hooks are stateless per-invocation; AskUserQuestion's answer isn't visible
# here). This lets the user pre-authorize out-of-band (shell profile / Claude
# env) so the marker write exit 0s without any runtime confirm at all.
_dev_edit_preauthorized() {
  if [[ "${CRAFT_GUARD_ALLOW_DEV_EDIT:-}" == "1" ]]; then
    printf '\n\033[33m[branch-guard]\033[0m CRAFT_GUARD_ALLOW_DEV_EDIT=1 — allowing guard-bypass marker\n' >&2
    exit 0
  fi
}

# Resolve `git rev-parse --git-common-dir` from a given directory, normalized
# to an absolute path. Git sometimes prints a CWD-relative path (e.g. `.git`)
# rather than absolute — a documented quirk that would otherwise produce a
# spurious mismatch when comparing two `-C`/`cd` invocations run from
# different base directories (GRILL-pretooluse-cross-repo-write-path-
# 2026-08-03.md finding 3). Prints nothing on any failure — callers MUST
# guard on non-empty before treating two results as comparable (finding 4:
# two empty strings must never read as "same repo").
_bg_resolve_common_dir() {
  local _dir="$1" _out
  _out="$(cd "$_dir" 2>/dev/null && git rev-parse --git-common-dir 2>/dev/null)" || return
  [[ -z "$_out" ]] && return
  if [[ "$_out" != /* ]]; then
    _out="$(cd "$_dir" 2>/dev/null && cd "$_out" 2>/dev/null && pwd -P)" || return
  fi
  printf '%s' "$_out"
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
IS_SAME_LOGICAL_REPO=false
if [[ ( "$TOOL_NAME" == "Bash" || "$TOOL_NAME" == "bash" ) && -n "$COMMAND" ]]; then
  _BG_TARGET_DIR=""

  # Walk clauses left-to-right, tracking the effective cwd cumulatively.
  # awk gsub emits a REAL newline on BSD & GNU (BSD sed's `\n` does not).
  # Single `|` also splits so a piped `grep -C N` can't be misread as `git -C`.
  _bg_eff="$CWD"
  _bg_norm="$(printf '%s' "$COMMAND" | awk '{gsub(/&&|&|[;|]/,"\n"); print}')"
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

        # Distinguish "different worktree of the SAME logical repo" from "a
        # genuinely different repo" — used ONLY to reword the confirm
        # message below (Branch 5: confirm-vs-block severity is unchanged,
        # deliberately, per the 2026-07-14 "confirm, never hard-block"
        # decision). Compares against $_BG_SESSION_ROOT, never the
        # about-to-be-clobbered $PROJECT_ROOT (finding 2).
        if [[ "$_BG_TARGET_ROOT" != "$_BG_SESSION_ROOT" ]]; then
          _BG_TARGET_COMMONDIR="$(_bg_resolve_common_dir "$_BG_TARGET_DIR")" || true
          _BG_SESSION_COMMONDIR="$(_bg_resolve_common_dir "$_BG_SESSION_ROOT")" || true
          if [[ -n "$_BG_TARGET_COMMONDIR" && -n "$_BG_SESSION_COMMONDIR" \
                && "$_BG_TARGET_COMMONDIR" == "$_BG_SESSION_COMMONDIR" ]]; then
            IS_SAME_LOGICAL_REPO=true
          fi
        fi

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
  if echo "$COMMAND_UNQ" | grep -qE '(^|;|&&|&|\|\|)[[:space:]]*'"${_BG_GIT}"'branch[[:space:]]+(-D|--delete[[:space:]]+--force|--force[[:space:]]+--delete)'; then
    # User-preconfigured escape hatch (issue #168): auto-mode's hard_deny classifier
    # refuses to let the agent create the allow-once/allow-dev-edit marker _confirm()
    # needs, deadlocking even explicit user authorization. This env var lets the user
    # pre-authorize out-of-band (shell profile / Claude env) so branch-guard exit 0s
    # without any runtime marker fabrication.
    if [[ "${CRAFT_GUARD_ALLOW_FORCE_DELETE:-}" == "1" ]]; then
      printf '\n\033[33m[branch-guard]\033[0m CRAFT_GUARD_ALLOW_FORCE_DELETE=1 — allowing force-delete\n' >&2
      exit 0
    fi
    # -------------------------------------------------------------------
    # Verified-merge confirm gate (2026-07-29): a squash-merged branch used
    # to be force-delete-eligible via a SILENT exit 0 (no confirm at all)
    # once the local `is_squash_merged` check said SAFE. Two problems with
    # that: (a) too permissive — a stale/incorrect merge status would nuke
    # a branch with zero human check, and (b) the local check itself
    # (git cherry / tree-diff) misreports multi-commit squash merges as
    # NOT_MERGED (repo memory git-cherry-misreports-squash-merges), which
    # is too STRICT the other direction — hard-blocking genuinely-merged
    # branches with no escape except the CRAFT_GUARD_ALLOW_FORCE_DELETE
    # env var above.
    #
    # New contract: a branch verified merged (by either tier below) gets
    # an explicit [CONFIRM] naming the branch and the evidence — never a
    # silent allow, never an unconditional hard block. An unverified
    # branch keeps the original hard confirm unchanged.
    #
    # Verification tiers — either is sufficient for a given branch:
    #   1. Local (is_squash_merged, lib/git-utils.sh): offline, fast, exact
    #      for single-commit squashes; can false-negative on multi-commit.
    #   2. Strong (this function): `gh pr view` + the two-part gate from
    #      repo CLAUDE.md / memory git-cherry-misreports-squash-merges —
    #      local branch tip must equal the merged PR's headRefOid AND the
    #      PR's mergeCommit must be an ancestor of the integration branch.
    #      Fails CLOSED on any missing tool, timeout, or mismatch.
    #
    # Defined inline (not lib/git-utils.sh) so this works identically
    # whether sourced via the canonical craft copy or the live installed
    # hook — the live hook's `../lib` does not resolve to a real
    # lib/git-utils.sh, so anything only in that file would silently not
    # apply live (memory live-hook-fix-must-port-to-repo-source).
    _bg_strong_merge_check() {
      # Usage: _bg_strong_merge_check <branch> <integration_branch>
      # Echoes "SAFE <pr_number>" or "NOT_SAFE" (never anything else).
      local br="$1" integ="$2"
      command -v gh &>/dev/null || { echo "NOT_SAFE"; return; }
      command -v jq &>/dev/null || { echo "NOT_SAFE"; return; }
      local _bg_timeout_bin=""
      command -v timeout &>/dev/null && _bg_timeout_bin="timeout 5"
      local local_tip
      local_tip="$(git rev-parse "refs/heads/${br}" 2>/dev/null)" || { echo "NOT_SAFE"; return; }
      local pr_json
      pr_json="$(${_bg_timeout_bin} gh pr view "$br" --json number,headRefOid,mergeCommit,state 2>/dev/null)" || { echo "NOT_SAFE"; return; }
      [[ -n "$pr_json" ]] || { echo "NOT_SAFE"; return; }
      local pr_state pr_num pr_head pr_merge
      pr_state="$(printf '%s' "$pr_json" | jq -r '.state // empty' 2>/dev/null)" || true
      [[ "$pr_state" == "MERGED" ]] || { echo "NOT_SAFE"; return; }
      pr_num="$(printf '%s' "$pr_json" | jq -r '.number // empty' 2>/dev/null)" || true
      pr_head="$(printf '%s' "$pr_json" | jq -r '.headRefOid // empty' 2>/dev/null)" || true
      pr_merge="$(printf '%s' "$pr_json" | jq -r '.mergeCommit.oid // empty' 2>/dev/null)" || true
      [[ -n "$pr_num" && -n "$pr_head" && -n "$pr_merge" ]] || { echo "NOT_SAFE"; return; }
      [[ "$pr_head" == "$local_tip" ]] || { echo "NOT_SAFE"; return; }
      git merge-base --is-ancestor "$pr_merge" "$integ" 2>/dev/null || { echo "NOT_SAFE"; return; }
      echo "SAFE ${pr_num}"
    }

    # Extract ALL branch args in the -D clause (git allows deleting several
    # at once). Stop at the first clause terminator so a chained command
    # (&&, ||, ;, |) doesn't get swept in as a "branch name".
    _bg_del_clause="$(echo "$COMMAND" | sed -E 's/.*git branch (-D|--delete[[:space:]]+--force|--force[[:space:]]+--delete)[[:space:]]*//')"
    _bg_del_clause="${_bg_del_clause%%;*}"
    _bg_del_clause="${_bg_del_clause%%&&*}"
    _bg_del_clause="${_bg_del_clause%%||*}"
    _bg_del_clause="${_bg_del_clause%%|*}"
    read -ra _DEL_BRANCHES <<< "$_bg_del_clause"

    _BG_ALL_VERIFIED=true
    _BG_ANY_BRANCH=false
    _BG_EVIDENCE=""
    for _bg_b in "${_DEL_BRANCHES[@]:-}"; do
      case "$_bg_b" in ""|-*) continue ;; esac
      _BG_ANY_BRANCH=true
      _bg_verified=false

      if command -v is_squash_merged &>/dev/null; then
        _bg_local_status="$(cd "$CWD" 2>/dev/null && is_squash_merged "${INTEGRATION_BRANCH:-dev}" "$_bg_b" 2>/dev/null || echo "UNKNOWN")"
        if [[ "$_bg_local_status" == "SAFE" ]]; then
          _BG_EVIDENCE+="  ${_bg_b} — local commit-graph check: fully contained in ${INTEGRATION_BRANCH:-dev}"$'\n'
          _bg_verified=true
        fi
      fi

      if [[ "$_bg_verified" == false ]]; then
        _bg_strong_result="$(cd "$CWD" 2>/dev/null && _bg_strong_merge_check "$_bg_b" "${INTEGRATION_BRANCH:-dev}" 2>/dev/null || echo "NOT_SAFE")"
        if [[ "$_bg_strong_result" == "SAFE "* ]]; then
          _bg_pr="${_bg_strong_result#SAFE }"
          _BG_EVIDENCE+="  ${_bg_b} — merged via PR #${_bg_pr}, ancestor check passed against ${INTEGRATION_BRANCH:-dev}"$'\n'
          _bg_verified=true
        fi
      fi

      if [[ "$_bg_verified" == false ]]; then
        _BG_ALL_VERIFIED=false
        break
      fi
    done

    if [[ "$_BG_ANY_BRANCH" == true && "$_BG_ALL_VERIFIED" == true ]]; then
      _confirm "branch_delete_verified" \
        "git branch -D (force delete) — VERIFIED merged" \
        "Verified merged — evidence:"$'\n'"${_BG_EVIDENCE}" \
        "Confirm to force-delete — the evidence above already establishes these are safe" \
        "git branch -d instead for git's own belt-and-suspenders check"
    fi

    _confirm "branch_delete" \
      "git branch -D (force delete)" \
      "Force-deletes branch even if not merged — but see the squash-merge note below first" \
      "If squash-merged: \"git branch -d\" CANNOT succeed here even when safe (its ancestry check always fails for a squash merge) — verify with: gh pr view <N> --json headRefOid,mergeCommit + git merge-base --is-ancestor <mergeCommit> ${INTEGRATION_BRANCH:-dev} (docs/branch-guard.md)" \
      "If not merged: git log <branch> to check for unmerged work" \
      "Either way this is recoverable: a merged PR's commits stay reachable at refs/pull/<N>/head regardless of local/remote branch state"
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
    Edit|edit|NotebookEdit|notebookedit)
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
      if echo "$COMMAND" | grep -qE '(^|;|&&|&|\|\|)[[:space:]]*'"${_BG_GIT}"'(commit|push)'; then
        # A `git push` whose refspec provably doesn't touch $BRANCH (e.g.
        # `--delete feature/x`, `feature/x:feature/y`) isn't a protected-branch
        # write no matter which repo/branch it resolves against — skip the
        # gate entirely rather than confirm/block a command that cannot
        # modify the protected branch (issue #6). The exemption only fires
        # when the ENTIRE command is nothing but an optional leading `cd`/
        # `-C` target-resolution prefix and exactly one `git push` clause
        # with a confirmed-safe refspec (see _bg_command_push_only_safe) —
        # any co-riding clause (a second push, a `git commit`, an unrelated
        # command) denies the exemption and falls back to gating exactly as
        # before, on purpose: per-clause classification was tried first and
        # missed a disguised co-riding commit and an unrelated command
        # riding past on a safe push's coattails.
        _bg_push_gate_needed=true
        [[ "$(_bg_command_push_only_safe "$COMMAND" "$BRANCH")" == "SAFE" ]] && _bg_push_gate_needed=false
        if [[ "$_bg_push_gate_needed" == true && "$IS_CROSS_REPO_TARGET" == true ]]; then
          # Cross-repo target resolved to a protected branch (e.g. another
          # repo's main) — confirm, never hard-block. The originating
          # session's own branch never authorized this, but a hard block
          # would also disrupt legitimate cross-repo work (explicit
          # decision: BRAINSTORM-branch-guard-target-resolution-2026-07-14,
          # "I do not want hard gate to disrupt").
          _bg_target_desc="a different repository (${PROJECT_NAME})"
          _bg_target_reason="another repository's protected ${BRANCH} branch — the session's own branch is not a valid gate for that repo's state"
          if [[ "$IS_SAME_LOGICAL_REPO" == true ]]; then
            _bg_target_desc="a different worktree of this same repository (${PROJECT_NAME})"
            _bg_target_reason="this repo's protected ${BRANCH} branch from a different worktree — the originating session's own branch is not a valid gate for another worktree's state"
          fi
          _confirm "cross_repo_protected_push" \
            "git commit/push on ${BRANCH} in ${_bg_target_desc}" \
            "This command targets ${_bg_target_reason}" \
            "Run this from a session/worktree already cd'd into ${PROJECT_ROOT}" \
            "Split into a separate Bash call scoped to that repo"
        elif [[ "$_bg_push_gate_needed" == true ]]; then
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
      if echo "$COMMAND" | grep -qE '(^|;|&&|&|\|\|)[[:space:]]*'"${_BG_GIT}"'reset[[:space:]]+--hard'; then
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
    Edit|edit|NotebookEdit|notebookedit)
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
          _dev_edit_preauthorized
          _confirm "edit_guard_bypass" \
            "Edit guard-bypass marker on ${BRANCH}: $(basename "$FILE_PATH")" \
            "This file self-approves a bypass of branch-guard's own protection — never editable silently" \
            "ask \"unprotect\" — the sanctioned way to request this bypass (dev/git skill)" \
            "Non-interactive: CRAFT_GUARD_ALLOW_DEV_EDIT=1 must be in Claude Code's OWN process env (pre-launch, or settings.json's env block) -- a tool-shell 'export' cannot reach this hook (issue #56, #281)"
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
          _dev_edit_preauthorized
          _confirm "write_guard_bypass" \
            "Write guard-bypass marker on ${BRANCH}: $(basename "$FILE_PATH")" \
            "Creating this file self-approves a bypass of branch-guard's own protection — must be a deliberate, confirmed action, never a silent allow" \
            "ask \"unprotect\" — the sanctioned way to request this bypass (dev/git skill)" \
            "Non-interactive: CRAFT_GUARD_ALLOW_DEV_EDIT=1 must be in Claude Code's OWN process env (pre-launch, or settings.json's env block) -- a tool-shell 'export' cannot reach this hook (issue #56, #281)"
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
        # LOW risk (relaxed 2026-07-28 — was MEDIUM/_confirm, asked every
        # time with no way to quiet down): new code file on protected
        # branch is a style-convention nudge, not data-loss prevention.
        # Note once per session, then allow silently.
        _low_note "write_new_code" \
          "New .${EXT} file on ${BRANCH}: ${FILE_PATH} — style convention is feature branches for new code (allowed)"
      fi

      # Known-safe non-code extension (NONCODE_EXTENSIONS) — allow
      exit 0
      ;;

    Bash|bash)
      # Force push — MEDIUM risk. Matches both flag forms (--force,
      # --force-with-lease, -f) and the `+<refspec>` prefix form, which sets
      # the same force semantics with none of those tokens (issue #45
      # finding B — `git push origin +feature/x:${BRANCH}` was undetected).
      #
      # The middle `.*` is bounded to `[^;&|]*` — NOT left as a bare `.*` —
      # so it cannot span past this push clause into a later one. A bare
      # `.*` let a trailing token in an UNRELATED later clause (e.g. `git
      # push origin dev && grep -c --force file.txt`) satisfy the flag
      # alternative and false-positive this gate; this was a PRE-EXISTING
      # bug in the `--force`/`-f` flag form (confirmed live against dev
      # HEAD before this fix, not introduced by the `+refspec` addition
      # below) — fixed here rather than left as an unfixed sibling, per
      # `/code-review 46`'s finding on the `+refspec`/`--delete` additions.
      if echo "$COMMAND" | grep -qE '(^|;|&&|&|\|\|)[[:space:]]*'"${_BG_GIT}"'push[[:space:]][^;&|]*((--force|--force-with-lease|-f)([[:space:]]|$)|[[:space:]]\+[^[:space:]]+)'; then
        _confirm "force_push" \
          "git push --force on ${BRANCH}" \
          "Force push overwrites remote history for all collaborators" \
          "git push origin ${BRANCH} (regular push)" \
          "git push --force-with-lease (safer — checks remote)" \
          "Ask Claude to create a worktree (dev/git skill) to isolate changes"
      fi

      # git push --delete / bare `:<ref>` — MEDIUM risk (deletes a remote
      # branch directly; the catastrophic `git branch -D` check above only
      # sees LOCAL branch deletion, not this). Issue #45 finding A — smart
      # mode had no gate at all for `git push origin --delete ${BRANCH}`.
      # Bounded to `[^;&|]*` (see force_push comment above) so a trailing
      # `:token` in a later, unrelated clause can't false-positive this gate.
      if echo "$COMMAND" | grep -qE '(^|;|&&|&|\|\|)[[:space:]]*'"${_BG_GIT}"'push[[:space:]][^;&|]*(--delete([[:space:]]|$)|[[:space:]]:[^[:space:]]+([[:space:]]|$))'; then
        _confirm "push_delete" \
          "git push --delete on ${BRANCH}" \
          "Deletes a remote branch directly — cannot be undone from here" \
          "Confirm the target ref before deleting a remote branch" \
          "Delete via the GitHub UI/gh CLI instead, where it's reversible from reflog for longer"
      fi

      # git reset --hard — MEDIUM risk (discards uncommitted changes)
      if echo "$COMMAND" | grep -qE '(^|;|&&|&|\|\|)[[:space:]]*'"${_BG_GIT}"'reset[[:space:]]+--hard'; then
        _confirm "reset_hard" \
          "git reset --hard on ${BRANCH}" \
          "Discards all uncommitted changes — cannot be undone" \
          "git stash (save changes for later)" \
          "git reset --soft (keep changes staged)" \
          "git diff to review what would be lost"
      fi

      # git clean -f (remove untracked files) — MEDIUM risk
      if echo "$COMMAND" | grep -qE '(^|;|&&|&|\|\|)[[:space:]]*'"${_BG_GIT}"'clean[[:space:]]+(-[fdxFDX]+|--force)'; then
        _confirm "clean_force" \
          "git clean -f (remove untracked files) on ${BRANCH}" \
          "Permanently removes untracked files — cannot be undone" \
          "git clean -n (dry run — see what would be removed)" \
          "git stash -u (stash including untracked files)"
      fi

      # ---------------------------------------------------------------
      # Bash write-through detection (file creation via redirection)
      # Catches: echo/cat/printf > file, tee file, cp src dst
      # Skips: markdown files, variables in paths, existing files,
      #        out-of-repo targets, quoted program/pattern text
      # ---------------------------------------------------------------
      BASH_TARGET=""

      # Quoted-span stripping (2026-07-16 fix): Patterns 1-4 below coarse-scan
      # $COMMAND for shell metacharacters/keywords with plain grep, which has
      # no notion of quoting. A `>` or `cp `/`tee `/`touch ` substring INSIDE
      # a single- or double-quoted argument — e.g. `awk 'NR>=203'`,
      # `grep -E '>[^=]'`, `grep "cp \|redirect"` — is program/pattern TEXT,
      # not real shell syntax, but was scanned identically to an unquoted
      # redirect. This is the same failure class Group 14c (2026-07-10)
      # already fixed for heredoc bodies via HAS_HEREDOC; this generalizes it
      # to any quoted span, not just heredoc bodies.
      #
      # COMMAND_SCAN is used ONLY for the coarse `grep -q` presence checks
      # below, deciding whether a pattern applies at all. Extraction
      # (`grep -oE`) still runs against the ORIGINAL $COMMAND, so a real
      # target quoted for spaces (e.g. `cp a.py "new file.py"`) is unaffected
      # — only text that would otherwise cause a pattern to fire on content
      # that was never real shell syntax is suppressed.
      #
      # MUST be a single alternation pattern (`'...'|"..."`), not two
      # independent s/// passes for single- and double-quotes. Two independent
      # passes let a single-quote-pair span cross entirely unrelated
      # double-quoted strings — e.g. `echo "it's" > f.py && echo "don't"` has
      # two double-quoted words that each contain exactly one apostrophe; a
      # standalone `s/'[^']*'/Q/g` pairs those two apostrophes across the ` >
      # f.py && echo ` in between and erases the REAL redirect from
      # COMMAND_SCAN, causing a genuine write-through to go undetected (a
      # false NEGATIVE, not just a false positive — confirmed live against
      # this exact command on 2026-07-16). The combined alternation resolves
      # quote-type at the first quote character encountered, so it can never
      # pair across a boundary of the other quote type.
      #
      # Single-quoted spans are stripped exactly: bash disallows a literal '
      # inside '...' with no escape mechanism, so `'[^']*'` cannot mismatch a
      # real single-quoted span. Double-quoted spans are a best-effort
      # approximation (bash permits \" inside "..."); under-stripping here
      # only returns to the prior (already-shipped) behavior for that rare
      # case — it can never introduce a NEW false positive.
      # Single sed invocation — this runs on every Bash tool call, so
      # process-fork count matters for the dogfood perf budget
      # (test_branch_guard_under_200ms).
      COMMAND_SCAN="$(sed -E "s/'[^']*'|\"[^\"]*\"/Q/g" <<< "$COMMAND")"

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
      # Excludes '&' after '>' so fd-duplication redirects (2>&1, 1>&2 — near-
      # ubiquitous, always benign) never satisfy this gate. Without this, a
      # command like `git commit -m "...(7 -> 9)" 2>&1` gets misdetected: the
      # coarse gate fires on the harmless `2>&1`, then extraction re-scans the
      # WHOLE original command and can pick up the unrelated `->` arrow safely
      # inside the already-quoted commit message as a false file-creation
      # target (confirmed live 2026-07-26 — `git commit -m "...(7 -> 9)" 2>&1`
      # blocked citing target `9)"`, a fragment of the quoted prose).
      if [[ "$HAS_HEREDOC" == false ]] && echo "$COMMAND_SCAN" | grep -qE '>[[:space:]]*[^>&]'; then
        # Extract the target after the last > — against the ORIGINAL
        # command, so a real quoted target (spaces, etc.) is found intact.
        BASH_TARGET="$(echo "$COMMAND" | grep -oE '>[[:space:]]*[^>|&;[:space:]]+' | tail -1 | sed 's/^>[[:space:]]*//' || true)"
      fi

      # Pattern 2: tee <file>  e.g. "echo x | tee file.py"
      # HAS_HEREDOC gate (see Pattern 1 comment above) applies here too —
      # grep is line-oriented, so a heredoc body line that happens to start
      # with "tee "/"touch "/contain "cp <word> <word>" as prose is
      # indistinguishable from real shell syntax without it.
      if [[ "$HAS_HEREDOC" == false ]] && [[ -z "$BASH_TARGET" ]] && echo "$COMMAND_SCAN" | grep -qE 'tee[[:space:]]+[^-]'; then
        BASH_TARGET="$(echo "$COMMAND" | grep -oE 'tee[[:space:]]+(-a[[:space:]]+)?[^|;&[:space:]]+' | head -1 | sed 's/^tee[[:space:]]*\(-a[[:space:]]*\)\{0,1\}//' || true)"
      fi

      # Pattern 3: cp <src> <dst>  e.g. "cp template.py new.py"
      # Anchored to a standalone `cp` token (start-of-string or preceded by
      # whitespace) — the prior unanchored `cp[[:space:]]` matched the
      # substring inside any word ending in "cp" (mcp, scp, gcp, ...), so
      # `claude mcp list ... 2>&1 | grep ...` and `claude mcp remove archex`
      # both false-positived as file-creation targeting "2>"/"archex"
      # (confirmed live 2026-07-28).
      if [[ "$HAS_HEREDOC" == false ]] && [[ -z "$BASH_TARGET" ]] && echo "$COMMAND_SCAN" | grep -qE '(^|[[:space:]])cp[[:space:]]'; then
        BASH_TARGET="$(echo "$COMMAND" | grep -oE '(^|[[:space:]])cp[[:space:]]+[^[:space:]]+[[:space:]]+([^|;&[:space:]]+)' | head -1 | awk '{print $NF}' || true)"
      fi

      # Pattern 4: touch <file>  e.g. "touch .claude/allow-once"
      # (extensionless targets like guard-bypass markers use touch, not
      # redirection — patterns 1-3 alone never see them)
      if [[ "$HAS_HEREDOC" == false ]] && [[ -z "$BASH_TARGET" ]] && echo "$COMMAND_SCAN" | grep -qE '(^|;|&&|&|\|\|)[[:space:]]*touch[[:space:]]'; then
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
              _dev_edit_preauthorized
              _confirm "bash_guard_bypass" \
                "Bash creates guard-bypass marker on ${BRANCH}: ${BASH_BASENAME}" \
                "Creating this file via shell self-approves a bypass of branch-guard's own protection" \
                "ask \"unprotect\" — the sanctioned way to request this bypass (dev/git skill)" \
                "Non-interactive: CRAFT_GUARD_ALLOW_DEV_EDIT=1 must be in Claude Code's OWN process env (pre-launch, or settings.json's env block) -- a tool-shell 'export' cannot reach this hook (issue #56, #281)"
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

              # Path scoping (2026-07-16 fix): a write to /tmp, $HOME, or any
              # absolute path outside PROJECT_ROOT poses no risk to THIS
              # repo's ${BRANCH} — e.g. backing up an installed hook to the
              # scratchpad before re-installing it. Only /dev/* was excluded
              # before (line ~1013); an out-of-repo real path was still
              # flagged as "creates a new code file on ${BRANCH}", which is
              # false — the file isn't in the repo tree at all.
              #
              # PROJECT_ROOT is a REALPATH (from `git rev-parse
              # --show-toplevel`, which resolves symlinks). $CWD is whatever
              # the caller passed — often NOT canonicalized (e.g. macOS's
              # /tmp is a symlink to /private/tmp; `mktemp -d` returns the
              # /tmp form). A literal-prefix compare of the raw BASH_ACTUAL
              # against PROJECT_ROOT would then mismatch for every in-repo
              # write under a symlinked ancestor — a real regression, not a
              # fix. Canonicalize BASH_ACTUAL's directory the same way
              # PROJECT_ROOT was canonicalized before comparing. `pwd -P` is
              # POSIX and avoids `realpath`/`readlink -f`, which aren't
              # universally available (see memory:
              # macos-shell-portability-gotchas). If the directory doesn't
              # exist yet, fall back to the raw path — no worse than the
              # unscoped behavior this replaces.
              BASH_ACTUAL_DIR="$(dirname "$BASH_ACTUAL")"
              BASH_ACTUAL_DIR_REAL="$(cd "$BASH_ACTUAL_DIR" 2>/dev/null && pwd -P || printf '%s' "$BASH_ACTUAL_DIR")"
              BASH_ACTUAL_REAL="${BASH_ACTUAL_DIR_REAL}/$(basename "$BASH_ACTUAL")"

              if [[ "$BASH_ACTUAL_REAL" != "${PROJECT_ROOT}" && "$BASH_ACTUAL_REAL" != "${PROJECT_ROOT}/"* ]]; then
                BASH_TARGET=""
              fi
            fi

            if [[ -n "$BASH_TARGET" ]] && [[ "$BASH_IS_CODE" == true ]]; then
              if [[ ! -f "$BASH_ACTUAL" ]] && [[ ! -f "${PROJECT_ROOT}/${BASH_TARGET}" ]]; then
                # Relaxed 2026-07-28 (see write_new_code above) — same
                # style-convention tier, not data-loss prevention. Note
                # once per session, then allow silently.
                _low_note "bash_write_through" \
                  "Shell redirection creates new .${BASH_EXT} file on ${BRANCH}: ${BASH_TARGET} (allowed)"
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
