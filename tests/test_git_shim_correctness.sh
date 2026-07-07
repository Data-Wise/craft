#!/usr/bin/env bash
#
# Shim-correctness test (SPEC-branch-protection-consolidation-2026-07-07 §4.7 / §6)
#
# For each thinned commands/git/*.md shim, assert:
#   1. frontmatter declares deprecated: true + replaced-by: "skills/dev/git/"
#   2. the shim references at least one real "Operation N" that exists as a
#      "### N." heading in skills/dev/git/SKILL.md
#   3. the file is actually thin (line count under a generous ceiling) —
#      prevents the exact drift this SPEC found: frontmatter claiming a
#      migration that never happened.
#
# Usage: bash tests/test_git_shim_correctness.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILL_FILE="$ROOT/skills/dev/git/SKILL.md"

T_RED='\033[0;31m'
T_GREEN='\033[0;32m'
T_BOLD='\033[1m'
T_NC='\033[0m'

TOTAL=0
PASS=0
FAIL=0
declare -a FAILED_NAMES=()

# name -> max line count considered "thin"
declare -A SHIMS=(
  [guard.md]=90
  [protect.md]=70
  [status.md]=70
  [clean.md]=70
  [git-recap.md]=70
  [branch.md]=80
  [sync.md]=60
  [worktree.md]=260
  [unprotect.md]=160
)

# Files unchanged by this SPEC (already thin shims per prior migrations) that
# don't necessarily cite "Operation N" by that literal string — skip the
# op-ref check for these, still enforce frontmatter + thinness.
SKIP_OPREF="unprotect.md"

check() {
  local name="$1"
  local ok="$2"
  local detail="$3"
  TOTAL=$((TOTAL + 1))
  if [[ "$ok" == "true" ]]; then
    PASS=$((PASS + 1))
    echo -e "  ${T_GREEN}PASS${T_NC}  $name  ${T_BOLD}($detail)${T_NC}"
  else
    FAIL=$((FAIL + 1))
    FAILED_NAMES+=("$name")
    echo -e "  ${T_RED}FAIL${T_NC}  $name  ${T_BOLD}($detail)${T_NC}"
  fi
}

for shim in "${!SHIMS[@]}"; do
  file="$ROOT/commands/git/$shim"
  max_lines="${SHIMS[$shim]}"

  if [[ ! -f "$file" ]]; then
    check "exists:$shim" false "file not found"
    continue
  fi

  # 1. frontmatter
  if grep -q 'deprecated: true' "$file" && grep -q 'replaced-by: "skills/dev/git/"' "$file"; then
    check "frontmatter:$shim" true "deprecated + replaced-by present"
  else
    check "frontmatter:$shim" false "missing deprecated/replaced-by frontmatter"
  fi

  # 2. references a real Operation N that exists in SKILL.md
  if [[ " $SKIP_OPREF " == *" $shim "* ]]; then
    check "op-ref:$shim" true "skipped (pre-existing shim, unchanged by this SPEC)"
    lines=$(wc -l < "$file" | tr -d ' ')
    if (( lines <= max_lines )); then
      check "thin:$shim" true "$lines lines (<= $max_lines)"
    else
      check "thin:$shim" false "$lines lines (> $max_lines ceiling)"
    fi
    continue
  fi
  ops="$(grep -oE 'Operation [0-9]+' "$file" | grep -oE '[0-9]+' | sort -u)"
  if [[ -z "$ops" ]]; then
    check "op-ref:$shim" false "no 'Operation N' reference found in shim"
  else
    all_found=true
    missing=""
    for op in $ops; do
      if ! grep -qE "^### ${op}\." "$SKILL_FILE"; then
        all_found=false
        missing="$missing $op"
      fi
    done
    if [[ "$all_found" == true ]]; then
      check "op-ref:$shim" true "references Operation(s):$ops, all present in SKILL.md"
    else
      check "op-ref:$shim" false "references Operation(s) not found in SKILL.md:$missing"
    fi
  fi

  # 3. thin (line count under ceiling)
  lines=$(wc -l < "$file" | tr -d ' ')
  if (( lines <= max_lines )); then
    check "thin:$shim" true "$lines lines (<= $max_lines)"
  else
    check "thin:$shim" false "$lines lines (> $max_lines ceiling — no longer a thin shim)"
  fi
done

echo ""
echo -e "${T_BOLD}Shim-correctness summary: ${PASS}/${TOTAL} passed${T_NC}"

if [[ $FAIL -gt 0 ]]; then
  echo -e "${T_RED}Failed:${T_NC}"
  for n in "${FAILED_NAMES[@]}"; do
    echo -e "  ${T_RED}-${T_NC} $n"
  done
  exit 1
fi
exit 0
