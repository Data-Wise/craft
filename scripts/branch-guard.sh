#!/bin/bash
set -euo pipefail

# branch-guard.sh — Claude Code PreToolUse hook
# Enforces branch protection rules for main and dev branches.
# Reads JSON from stdin: { tool_name, tool_input: { file_path, command, ... }, cwd }
# Exits 0 = allow, 2 = block (message on stderr)
# Requires: jq (preferred), python3 (fallback), or grep/sed (last resort)

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
# Protection levels: "block-all", "block-new-code", "" (none)
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
    DEV_PROTECTION="block-new-code"
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

# No protection for this branch — allow everything
[[ -z "$PROTECTION" ]] && exit 0

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
# 10. Apply protection: block-new-code (dev branch)
# ---------------------------------------------------------------------------
if [[ "$PROTECTION" == "block-new-code" ]]; then
  case "$TOOL_NAME" in
    Edit|edit)
      # Editing existing files is always allowed on dev
      exit 0
      ;;

    Write|write)
      # Markdown files — always allowed
      if [[ "$FILE_PATH" == *.md ]]; then
        exit 0
      fi

      # Extension-less files (no dot in basename) — allowed
      # Examples: .STATUS, Makefile, Dockerfile, LICENSE
      BASENAME="$(basename "$FILE_PATH")"
      if [[ "$BASENAME" != *.* ]] || [[ "$BASENAME" == .* && "${BASENAME#.}" != *.* ]]; then
        exit 0
      fi

      # Files in tests/ directory — allowed
      if echo "$FILE_PATH" | grep -qE '(^|/)tests/'; then
        exit 0
      fi

      # Determine the actual file path (could be relative or absolute)
      ACTUAL_PATH="$FILE_PATH"
      if [[ "$FILE_PATH" != /* ]]; then
        ACTUAL_PATH="${CWD}/${FILE_PATH}"
      fi

      # Existing file (overwrite/fixup) — allowed
      if [[ -f "$ACTUAL_PATH" ]]; then
        exit 0
      fi

      # Also check relative to project root
      if [[ -f "${PROJECT_ROOT}/${FILE_PATH}" ]]; then
        exit 0
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
        block "$(_box \
          "${_R}${_B}BRANCH PROTECTION${_N}" \
          "---" \
          "Cannot create new ${_B}.${EXT}${_N} file on ${_B}${BRANCH}${_N}." \
          "" \
          "${_D}File:${_N}   ${_C}${FILE_PATH}${_N}" \
          "${_D}Branch:${_N} ${BRANCH} (block-new-code)" \
          "---" \
          "Options:" \
          "  ${_Y}1.${_N} Create worktree for feature work" \
          "  ${_Y}2.${_N} Edit an EXISTING file (fixups allowed)" \
          "  ${_Y}3.${_N} Bypass: ${_G}/craft:git:unprotect${_N}" \
        )"
      fi

      # Non-code extension or unrecognized — allow
      exit 0
      ;;

    Bash|bash)
      # Block force push (--force, -f, --force-with-lease)
      if echo "$COMMAND" | grep -qE 'git[[:space:]]+push[[:space:]].*(--force|--force-with-lease|-f)([[:space:]]|$)'; then
        block "$(_box \
          "${_R}${_B}BRANCH PROTECTION${_N}" \
          "---" \
          "Cannot force push on ${_B}${BRANCH}${_N}." \
          "" \
          "${_D}Command:${_N} ${_C}${COMMAND}${_N}" \
          "${_D}Branch:${_N}  ${BRANCH} (block-new-code)" \
        )"
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
