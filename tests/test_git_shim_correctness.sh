#!/usr/bin/env bash
#
# git-migration-completeness test
# (SPEC-branch-protection-consolidation-2026-07-07 §4.7 / §6 -> T3.5.2 -> v4 folio-split)
#
# HISTORY — why this file inverted its assertions (2026-07-16):
#   Originally this suite asserted each commands/git/*.md was a genuine THIN SHIM
#   (deprecated: true + replaced-by: "skills/dev/git/" + under a line ceiling). Its
#   purpose was to catch "frontmatter claiming a migration that never happened."
#
#   T3.5.2 then COMPLETED that migration: all 11 git command shims were deleted and
#   their content now lives in skills/dev/git/SKILL.md as numbered Operations. The
#   original assertions became unsatisfiable — they required files the migration was
#   designed to remove — and the suite failed 7/21 on the v4 branch while passing on
#   dev, where the files still existed. (It is a CI-required check, ci.yml; pytest
#   does not run it, which is why the breakage went unnoticed: T3.5.2's verification
#   cited a green pytest run as its evidence.)
#
#   The shim-drift risk this file guarded is now structurally impossible — there are
#   no shims left to carry false frontmatter. So the assertions are INVERTED to guard
#   the migration's END STATE instead, which is a live invariant:
#     1. the 11 former shims stay deleted (nobody silently re-adds one)
#     2. skills/dev/git/SKILL.md still carries the Operations that replaced them
#     3. the one sanctioned live command (issue-check) stays live and non-deprecated
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

# The 11 former commands/git/*.md shims, deleted in T3.5.2. None may come back:
# their content lives in skills/dev/git/SKILL.md as Operations (see the mapping
# table in that file's "Integration" section).
DELETED_SHIMS=(
  guard.md
  protect.md
  protect-baseline.md
  status.md
  clean.md
  branch.md
  worktree.md
  unprotect.md
  init.md
  sync.md
  git-recap.md
)

# Operations that must survive in SKILL.md as "### N." headings. These are the
# replacement surface — if one disappears, the migration has silently regressed
# and the deleted commands have no home.
REQUIRED_OPS=(1 2 3 4 5 6 7 8 9 10 11 12)

# The ONLY sanctioned live command under commands/git/. Deliberately not folded
# into the skill: tests/test_issue_check_unit.py extracts its classify_issue()
# block from this exact path and exec()s it, so the command file is the single
# source of truth for the classifier (same constraint as commands/ci/triage.md,
# recorded as D13 in GRILL-phase-3-6-router-consolidation-2026-07-15.md).
LIVE_COMMANDS=(issue-check.md)

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

# 1. The former shims stay deleted.
for shim in "${DELETED_SHIMS[@]}"; do
  if [[ -f "$ROOT/commands/git/$shim" ]]; then
    check "deleted:$shim" false "resurrected — content belongs in skills/dev/git/SKILL.md"
  else
    check "deleted:$shim" true "still absent (migrated to skills/dev/git/)"
  fi
done

# 2. SKILL.md exists and still carries the replacement Operations.
if [[ ! -f "$SKILL_FILE" ]]; then
  check "skill:exists" false "skills/dev/git/SKILL.md not found — migration target is gone"
else
  check "skill:exists" true "skills/dev/git/SKILL.md present"
  for op in "${REQUIRED_OPS[@]}"; do
    if grep -qE "^### ${op}\." "$SKILL_FILE"; then
      check "op:$op" true "Operation $op present"
    else
      check "op:$op" false "Operation $op missing from SKILL.md"
    fi
  done
fi

# 3. The sanctioned live command stays live and non-deprecated.
for cmd in "${LIVE_COMMANDS[@]}"; do
  file="$ROOT/commands/git/$cmd"
  if [[ ! -f "$file" ]]; then
    check "live:$cmd" false "missing — expected a live command at commands/git/$cmd"
  elif grep -q 'deprecated: true' "$file"; then
    check "live:$cmd" false "marked deprecated — it is a live command, not a shim"
  else
    check "live:$cmd" true "live and non-deprecated"
  fi
done

# 4. No UNSANCTIONED command files under commands/git/ — anything new here is
#    either a resurrected shim or an undocumented addition that skipped the
#    skill-first convention. Fail loudly rather than let the surface drift back.
if [[ -d "$ROOT/commands/git" ]]; then
  while IFS= read -r found; do
    base="$(basename "$found")"
    sanctioned=false
    for cmd in "${LIVE_COMMANDS[@]}"; do
      [[ "$base" == "$cmd" ]] && sanctioned=true && break
    done
    if [[ "$sanctioned" == false ]]; then
      check "unsanctioned:$base" false "unexpected command under commands/git/ — add to LIVE_COMMANDS with a reason, or move it into skills/dev/git/"
    fi
  done < <(find "$ROOT/commands/git" -maxdepth 1 -name '*.md' -type f 2>/dev/null)
fi

echo ""
echo -e "${T_BOLD}git-migration-completeness summary: ${PASS}/${TOTAL} passed${T_NC}"

if [[ $FAIL -gt 0 ]]; then
  echo -e "${T_RED}Failed:${T_NC}"
  for n in "${FAILED_NAMES[@]}"; do
    echo -e "  ${T_RED}-${T_NC} $n"
  done
  exit 1
fi
exit 0
