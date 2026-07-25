#!/bin/bash
set -euo pipefail

# reference-scope-guard.sh — Claude Code PreToolUse hook (issue #286)
# Advisory-only: warns (never blocks) when a Write/Edit targets
# ~/.claude/reference/ with a filename that doesn't match this repo's naming
# convention for that directory — lowercase, topic-named, no SPEC-*/GRILL-*/
# BRAINSTORM-* prefix (those belong in docs/specs/, not a reference dir),
# no .html (reference/ is markdown-only).
#
# Reads JSON from stdin: { tool_name, tool_input: { file_path, ... }, cwd }
# Always exits 0 — this hook never blocks, per its own design (scope drift
# is cheap to flag at write time, but false positives on legitimate new
# naming shapes should never stop work; same posture as no-switch-guard.sh's
# YELLOW/advisory tier).
#
# Testability: `reference-scope-guard.sh --check <filename>` runs just the
# allow-pattern matcher against a bare filename and prints VIOLATIONS or OK,
# without needing to construct a full PreToolUse JSON payload — this is what
# the unit tests use; the e2e tests pipe real JSON through stdin like any
# other hook invocation.

REFERENCE_DIR="${HOME}/.claude/reference"

# ---------------------------------------------------------------------------
# check_filename <basename> — the allow-pattern matcher
# Prints one violation reason per line to stdout; prints nothing if clean.
# Pure function of the filename — no I/O, no stdin, testable standalone.
# ---------------------------------------------------------------------------
check_filename() {
  local basename="$1"
  local violations=0

  if [[ "$basename" == *.html ]]; then
    echo "no .html files — reference/ is markdown-only"
    violations=1
  fi

  case "$basename" in
    SPEC-*|spec-*|Spec-*|GRILL-*|grill-*|Grill-*|BRAINSTORM-*|brainstorm-*|Brainstorm-*)
      echo "no SPEC-*/GRILL-*/BRAINSTORM-* prefix — those belong in docs/specs/, not reference/"
      violations=1
      ;;
  esac

  # Lowercase, topic-named check: strip the extension, require kebab-case
  # (letters/digits, hyphen-separated, starts with a letter). Anything else
  # — uppercase, underscores, spaces, leading digits/dashes — is flagged.
  local stem="${basename%.*}"
  if ! [[ "$stem" =~ ^[a-z][a-z0-9]*(-[a-z0-9]+)*$ ]]; then
    echo "not lowercase topic-named kebab-case (e.g. \"shell-workflow.md\") — got \"${basename}\""
    violations=1
  fi

  return 0
}

# ---------------------------------------------------------------------------
# --check mode: unit-test entry point, bypasses stdin/JSON entirely
# ---------------------------------------------------------------------------
if [[ "${1:-}" == "--check" ]]; then
  TARGET_BASENAME="$(basename -- "${2:-}")"
  RESULT="$(check_filename "$TARGET_BASENAME")"
  if [[ -n "$RESULT" ]]; then
    echo "VIOLATIONS:"
    echo "$RESULT"
    exit 0
  else
    echo "OK"
    exit 0
  fi
fi

# ---------------------------------------------------------------------------
# Hook mode: read stdin JSON
# ---------------------------------------------------------------------------
INPUT="$(cat)"

_json_get() {
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
    local key="${query##*.}"
    printf '%s' "$json" | grep -o "\"${key}\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" 2>/dev/null | head -1 | sed "s/\"${key}\"[[:space:]]*:[[:space:]]*\"//;s/\"$//" || true
  fi
}

TOOL_NAME="$(_json_get '.tool_name' "$INPUT")"
FILE_PATH="$(_json_get '.tool_input.file_path' "$INPUT")"
if [[ -z "$FILE_PATH" ]]; then
  FILE_PATH="$(_json_get '.tool_input.filePath' "$INPUT")"
fi

# Only Write/Edit carry a file_path; nothing to check otherwise.
if [[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "write" && "$TOOL_NAME" != "Edit" && "$TOOL_NAME" != "edit" ]]; then
  exit 0
fi
[[ -z "$FILE_PATH" ]] && exit 0

# Resolve ~ so a literal "~/.claude/reference/..." path (some tools pass the
# tilde unexpanded) still matches, same as the real $HOME-rooted path.
_RESOLVED_PATH="${FILE_PATH/#\~/$HOME}"

# Out of scope entirely unless the target is under ~/.claude/reference/.
case "$_RESOLVED_PATH" in
  "${REFERENCE_DIR}"/*) ;;
  *) exit 0 ;;
esac

BASENAME="$(basename -- "$_RESOLVED_PATH")"
VIOLATIONS="$(check_filename "$BASENAME")"

if [[ -n "$VIOLATIONS" ]]; then
  {
    printf '\n\033[1;33m[reference-scope-guard]\033[0m %s doesn'"'"'t match ~/.claude/reference/'"'"'s naming convention:\n' "$BASENAME"
    while IFS= read -r line; do
      printf '  \033[1;33m→\033[0m %s\n' "$line"
    done <<< "$VIOLATIONS"
    printf '  (advisory only — not blocked; rename now or leave as-is)\n'
  } >&2
fi

exit 0
