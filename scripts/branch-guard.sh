#!/bin/bash
set -euo pipefail

# branch-guard.sh — Claude Code PreToolUse hook
# Enforces branch protection rules for main and dev branches.
# Reads JSON from stdin: { tool_name, tool_input: { file_path, command, ... }, cwd }
# Exits 0 = allow, 2 = block (message on stderr)
# Requires: jq (preferred), python3 (fallback), or grep/sed (last resort)
#
# Protection levels:
#   block-all       — Hard block everything (main)
#   smart           — 3-tier: LOW (note) + MEDIUM (confirm) + HIGH (block) (dev)
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

# ---------------------------------------------------------------------------
# 3. Determine git context
# ---------------------------------------------------------------------------
# If no cwd provided, fall back to PWD
CWD="${CWD:-$PWD}"

# Check if we're in a git repo
PROJECT_ROOT="$(cd "$CWD" 2>/dev/null && git rev-parse --show-toplevel 2>/dev/null)" || {
  # Not a git repo — allow everything
  exit 0
}

BRANCH="$(cd "$CWD" 2>/dev/null && git branch --show-current 2>/dev/null)" || {
  # Detached HEAD or other edge case — allow
  exit 0
}

# If branch is empty (detached HEAD), allow
[[ -z "$BRANCH" ]] && exit 0

# Project short name (basename of repo root)
PROJECT_NAME="$(basename "$PROJECT_ROOT")"

# ---------------------------------------------------------------------------
# 4. Check bypass marker
# ---------------------------------------------------------------------------
if [[ -f "${PROJECT_ROOT}/.claude/allow-dev-edit" ]]; then
  exit 0
fi

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
  # If current branch not found in config, no protection
  # (Custom config is explicit — only listed branches are protected)
fi

if [[ "$USE_CONFIG" == false ]]; then
  # Auto-detect: does 'dev' branch exist?
  MAIN_PROTECTION="block-all"
  DEV_PROTECTION=""
  if cd "$PROJECT_ROOT" && git rev-parse --verify dev &>/dev/null; then
    DEV_PROTECTION="smart"
  fi

  # Determine which protection level applies to current branch
  PROTECTION=""
  case "$BRANCH" in
    main|master)
      PROTECTION="$MAIN_PROTECTION"
      ;;
    dev|develop)
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
    rm -f "$ONCE_MARKER"
    exit 0
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
  local c=0
  c=$(grep -c "^${action_type}$" "$SESSION_FILE" 2>/dev/null) || true
  echo "$c"
}

_session_increment() {
  local action_type="$1"
  mkdir -p "$(dirname "$SESSION_FILE")"
  echo "$action_type" >> "$SESSION_FILE"
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
block() {
  local message="$1"
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

  block "$msg"
}

# _low_note: LOW risk — brief note on first encounter, then silent
# Usage: _low_note action_type note_message
_low_note() {
  local action_type="$1"
  local note="$2"
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
  block "$(_box "$@")"
}

# ---------------------------------------------------------------------------
# 8d. Universal catastrophic checks (ALL branches, before protection filter)
# ---------------------------------------------------------------------------
if [[ "$TOOL_NAME" == "Bash" || "$TOOL_NAME" == "bash" ]]; then
  # rm -rf .git — HIGH risk everywhere (destroys entire repository)
  if echo "$COMMAND" | grep -qE 'rm[[:space:]]+(-[rfRF]+[[:space:]]+)*\.git([[:space:]]|/|$)'; then
    _hard_block \
      "${_R}${_B}BRANCH GUARD — CATASTROPHIC RISK${_N}" \
      "---" \
      "Cannot run ${_B}rm -rf .git${_N} — destroys entire repository." \
      "" \
      "${_D}Command:${_N} ${_C}${COMMAND}${_N}" \
      "${_D}Branch:${_N}  ${BRANCH}" \
      "---" \
      "This action is ${_R}never${_N} allowed via the guard." \
      "If intentional, remove the hook temporarily."
  fi

  # git branch -D — MEDIUM risk everywhere (deletes unmerged branches)
  if echo "$COMMAND" | grep -qE 'git[[:space:]]+branch[[:space:]]+(-D|--delete[[:space:]]+--force|--force[[:space:]]+--delete)'; then
    _confirm "branch_delete" \
      "git branch -D (force delete)" \
      "Force-deletes branch even if not merged — commits may be lost" \
      "git branch -d (safe delete — only if merged)" \
      "git log <branch> to check for unmerged work"
  fi
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
        "${_Y}→ git checkout dev${_N}" \
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
        "${_Y}→ git checkout dev${_N}" \
      )"
      ;;

    Bash|bash)
      # Check for destructive git commands
      if echo "$COMMAND" | grep -qE 'git[[:space:]]+commit|git[[:space:]]+push'; then
        block "$(_box \
          "${_R}${_B}BRANCH PROTECTION${_N}" \
          "---" \
          "Cannot commit/push on ${_B}${BRANCH}${_N}." \
          "" \
          "Use the PR workflow:" \
          "  ${_Y}1.${_N} git checkout dev" \
          "  ${_Y}2.${_N} Create worktree for changes" \
          "  ${_Y}3.${_N} PR: feature → dev → main" \
        )"
      fi
      if echo "$COMMAND" | grep -qE 'git[[:space:]]+reset[[:space:]]+--hard'; then
        block "$(_box \
          "${_R}${_B}BRANCH PROTECTION${_N}" \
          "---" \
          "Cannot reset --hard on ${_B}${BRANCH}${_N}." \
          "${_D}Branch:${_N} ${BRANCH} (block-all)" \
        )"
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
            "/craft:git:protect --level <level> (safe config update)" \
            "/craft:git:unprotect (temporary bypass instead)"
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
            "/craft:git:protect --level <level> (safe config update)" \
            "/craft:git:unprotect (temporary bypass instead)"
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

      # New code file — determine extension
      EXT="${FILE_PATH##*.}"
      CODE_EXTENSIONS="py sh js ts jsx tsx json yml yaml toml cfg ini r R zsh"

      IS_CODE=false
      for ext in $CODE_EXTENSIONS; do
        if [[ "$EXT" == "$ext" ]]; then
          IS_CODE=true
          break
        fi
      done

      if [[ "$IS_CODE" == true ]]; then
        # MEDIUM risk — new code file on protected branch
        _confirm "write_new_code" \
          "Write new .${EXT} file: ${FILE_PATH}" \
          "New code files on ${BRANCH} should go in a feature branch" \
          "/craft:git:worktree feature/<name>" \
          "Edit an existing file instead (fixups allowed)" \
          "/craft:git:unprotect for bulk maintenance"
      fi

      # Non-code extension or unrecognized — allow
      exit 0
      ;;

    Bash|bash)
      # Force push — MEDIUM risk
      if echo "$COMMAND" | grep -qE 'git[[:space:]]+push[[:space:]].*(--force|--force-with-lease|-f)([[:space:]]|$)'; then
        _confirm "force_push" \
          "git push --force on ${BRANCH}" \
          "Force push overwrites remote history for all collaborators" \
          "git push origin ${BRANCH} (regular push)" \
          "git push --force-with-lease (safer — checks remote)" \
          "/craft:git:worktree feature/<name> (isolate changes)"
      fi

      # git reset --hard — MEDIUM risk (discards uncommitted changes)
      if echo "$COMMAND" | grep -qE 'git[[:space:]]+reset[[:space:]]+--hard'; then
        _confirm "reset_hard" \
          "git reset --hard on ${BRANCH}" \
          "Discards all uncommitted changes — cannot be undone" \
          "git stash (save changes for later)" \
          "git reset --soft (keep changes staged)" \
          "git diff to review what would be lost"
      fi

      # git checkout -- (discard working tree changes) — MEDIUM risk
      if echo "$COMMAND" | grep -qE 'git[[:space:]]+checkout[[:space:]]+--[[:space:]]'; then
        _confirm "checkout_discard" \
          "git checkout -- (discard changes) on ${BRANCH}" \
          "Discards working tree changes for specified files" \
          "git stash (save changes for later)" \
          "git diff <file> to review what would be lost"
      fi

      # git restore (discard working tree changes) — MEDIUM risk
      # Excludes --staged (which only unstages, doesn't discard)
      if echo "$COMMAND" | grep -qE 'git[[:space:]]+restore[[:space:]]' && \
         ! echo "$COMMAND" | grep -qE 'git[[:space:]]+restore[[:space:]]+--staged'; then
        _confirm "restore_discard" \
          "git restore (discard changes) on ${BRANCH}" \
          "Discards working tree changes for specified files" \
          "git stash (save changes for later)" \
          "git restore --staged <file> (unstage only, keeps changes)"
      fi

      # git clean -f (remove untracked files) — MEDIUM risk
      if echo "$COMMAND" | grep -qE 'git[[:space:]]+clean[[:space:]]+(-[fdxFDX]+|--force)'; then
        _confirm "clean_force" \
          "git clean -f (remove untracked files) on ${BRANCH}" \
          "Permanently removes untracked files — cannot be undone" \
          "git clean -n (dry run — see what would be removed)" \
          "git stash -u (stash including untracked files)"
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
