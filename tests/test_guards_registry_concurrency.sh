#!/usr/bin/env bash
#
# Test Suite: guards.json write-race regression test
#
# Formalizes the ad hoc falsification test from the guard-hardening
# adversarial review session: 2 concurrent jq-mutate loops, 40 writes each,
# against a scratch copy, confirmed 40/80 writes lost pre-fix (unlocked
# read-modify-write). This suite proves lib/guards-lock.sh (Phase 1) closes
# that race for BOTH of guards.json's writers — skills/dev/git/SKILL.md
# Operation 12 (Phase 2) and scripts/install-guards.sh (Phase 3).
#
# SAFETY: every test operates on a scratch copy under a temp directory.
# This suite NEVER reads or writes the real ~/.claude/guards.json.
#
# Usage:
#   bash tests/test_guards_registry_concurrency.sh
#   MODE=unlocked bash tests/test_guards_registry_concurrency.sh   # red-first: prove the race exists

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOCK_HELPER="${REPO_ROOT}/lib/guards-lock.sh"

# MODE=locked (default, post-fix) uses lib/guards-lock.sh around every
# read-modify-write. MODE=unlocked skips the lock entirely, reproducing the
# pre-fix code path — used to prove this suite actually catches the bug.
MODE="${MODE:-locked}"

T_RED='\033[0;31m'
T_GREEN='\033[0;32m'
T_YELLOW='\033[1;33m'
T_BOLD='\033[1m'
T_NC='\033[0m'

TOTAL=0
PASS=0
FAIL=0
declare -a FAILED_NAMES=()

declare -a CLEANUP_DIRS=()
cleanup() {
  for d in "${CLEANUP_DIRS[@]:-}"; do
    [[ -n "$d" && -d "$d" ]] && rm -rf "$d"
  done
}
trap cleanup EXIT

make_scratch() {
  local d
  d="$(mktemp -d)"
  CLEANUP_DIRS+=("$d")
  echo "$d"
}

record() {
  local name="$1" ok="$2" detail="${3:-}"
  TOTAL=$((TOTAL + 1))
  if [[ "$ok" == "0" ]]; then
    PASS=$((PASS + 1))
    echo -e "  ${T_GREEN}✓${T_NC} $name"
  else
    FAIL=$((FAIL + 1))
    FAILED_NAMES+=("$name")
    echo -e "  ${T_RED}✗${T_NC} $name${detail:+ — $detail}"
  fi
}

# Guard the real registry can never be touched, even by accident.
REAL_GUARDS_JSON="${HOME}/.claude/guards.json"
assert_not_real() {
  local path="$1"
  if [[ "$path" == "$REAL_GUARDS_JSON" ]]; then
    echo -e "${T_RED}FATAL: test attempted to touch the real guards.json — aborting.${T_NC}" >&2
    exit 1
  fi
}

# ----------------------------------------------------------------------------
# increment_field <guards_json_path> <field> <iterations>
#   Simulates an Operation-12-style writer: read-jq-mutate-write loop that
#   increments a counter field N times. Honors $MODE (locked/unlocked).
# ----------------------------------------------------------------------------
increment_field() {
  local json="$1" field="$2" iterations="$3"
  local lockdir="${json}.lock"
  assert_not_real "$json"
  for ((i = 0; i < iterations; i++)); do
    if [[ "$MODE" == "locked" ]]; then
      bash "$LOCK_HELPER" acquire "$lockdir" 10
    fi
    # Per-write unique temp name (mktemp, not a shared $$/PID suffix — $$
    # resolves to the same value across bash background-job subshells, which
    # would otherwise make concurrent unlocked writers collide on the SAME
    # temp file — a confound distinct from the lost-update race under test).
    local tmp
    tmp="$(mktemp "${json}.tmp.XXXXXX")"
    jq --arg f "$field" '.guards[$f].mute_window_min += 1' "$json" > "$tmp" \
      && mv "$tmp" "$json"
    if [[ "$MODE" == "locked" ]]; then
      bash "$LOCK_HELPER" release "$lockdir"
    fi
  done
}

# ----------------------------------------------------------------------------
# install_style_merge <guards_json_path> <guard_name>
#   Simulates install-guards.sh's per-guard merge-loop iteration: existence
#   check + lock-guarded jq write of a fresh guard entry.
# ----------------------------------------------------------------------------
install_style_merge() {
  local json="$1" guard="$2"
  local lockdir="${json}.lock"
  assert_not_real "$json"
  if [[ "$MODE" == "locked" ]]; then
    bash "$LOCK_HELPER" acquire "$lockdir" 10
  fi
  if ! jq -e --arg g "$guard" '.guards[$g]' "$json" &>/dev/null; then
    local tmp
    tmp="$(mktemp "${json}.tmp.XXXXXX")"
    jq --arg g "$guard" '.guards[$g] = {"enabled":true,"muted_until":null,"mute_window_min":30}' \
      "$json" > "$tmp" && mv "$tmp" "$json"
  fi
  if [[ "$MODE" == "locked" ]]; then
    bash "$LOCK_HELPER" release "$lockdir"
  fi
}

seed_registry() {
  local json="$1"
  jq -n '{
    "guards": {
      "branch-guard":    { "enabled": true, "muted_until": null, "mute_window_min": 0 },
      "no-switch-guard": { "enabled": true, "muted_until": null, "mute_window_min": 0 }
    }
  }' > "$json"
}

echo -e "${T_BOLD}guards.json concurrency regression suite (MODE=$MODE)${T_NC}"
echo ""

# ==============================================================================
# Case 1: two concurrent writers hammering different fields (Operation-12-style)
# ==============================================================================
echo "Case 1: two concurrent writers, distinct fields, 40 increments each"

SCRATCH1="$(make_scratch)"
JSON1="${SCRATCH1}/guards.json"
assert_not_real "$JSON1"
seed_registry "$JSON1"

increment_field "$JSON1" "branch-guard" 40 &
PID_A=$!
increment_field "$JSON1" "no-switch-guard" 40 &
PID_B=$!
wait "$PID_A" "$PID_B"

COUNT_A="$(jq '.guards["branch-guard"].mute_window_min' "$JSON1")"
COUNT_B="$(jq '.guards["no-switch-guard"].mute_window_min' "$JSON1")"

if [[ "$MODE" == "locked" ]]; then
  [[ "$COUNT_A" == "40" ]]; record "case1_branch_guard_no_lost_updates (got $COUNT_A/40)" "$?"
  [[ "$COUNT_B" == "40" ]]; record "case1_no_switch_guard_no_lost_updates (got $COUNT_B/40)" "$?"
else
  # Red-first (MODE=unlocked): the race should be REPRODUCIBLE — at least one
  # counter should show lost updates. This is an expected-fail probe, not a
  # suite failure, so it reports informationally rather than via record().
  echo "  (unlocked) branch-guard=$COUNT_A/40, no-switch-guard=$COUNT_B/40"
  if [[ "$COUNT_A" != "40" || "$COUNT_B" != "40" ]]; then
    echo -e "  ${T_YELLOW}confirmed:${T_NC} lost updates reproduced without the lock (pre-fix behavior)"
  else
    echo -e "  ${T_YELLOW}note:${T_NC} no lost updates this run — race is timing-dependent, rerun to confirm"
  fi
fi

# ==============================================================================
# Case 2: Operation-12-style writer concurrent with install-guards.sh-style
# merge writer against the SAME scratch file — proves the SHARED lock, not
# just that each writer is internally self-consistent.
# ==============================================================================
echo ""
echo "Case 2: Operation-12-style writer + install-guards.sh-style writer, shared file"

SCRATCH2="$(make_scratch)"
JSON2="${SCRATCH2}/guards.json"
assert_not_real "$JSON2"
# Seed with only branch-guard present, so install-guards.sh's merge path has
# something to add (no-switch-guard) while Operation 12 hammers branch-guard.
jq -n '{ "guards": { "branch-guard": { "enabled": true, "muted_until": null, "mute_window_min": 0 } } }' > "$JSON2"

increment_field "$JSON2" "branch-guard" 40 &
PID_C=$!
( for ((j = 0; j < 40; j++)); do install_style_merge "$JSON2" "no-switch-guard"; done ) &
PID_D=$!
wait "$PID_C" "$PID_D"

COUNT_C="$(jq '.guards["branch-guard"].mute_window_min' "$JSON2")"
HAS_NSG="$(jq -e '.guards["no-switch-guard"]' "$JSON2" &>/dev/null && echo yes || echo no)"

if [[ "$MODE" == "locked" ]]; then
  [[ "$COUNT_C" == "40" ]]; record "case2_branch_guard_no_lost_updates (got $COUNT_C/40)" "$?"
  [[ "$HAS_NSG" == "yes" ]]; record "case2_no_switch_guard_entry_survives" "$?"
else
  echo "  (unlocked) branch-guard=$COUNT_C/40, no-switch-guard present=$HAS_NSG"
fi

# ==============================================================================
# Case 3: staleness-timeout — a pre-staged stale lock dir is force-broken
# rather than hanging forever.
# ==============================================================================
echo ""
echo "Case 3: stale lock is force-broken after the timeout"

SCRATCH3="$(make_scratch)"
STALE_LOCK="${SCRATCH3}/guards.json.lock"
mkdir "$STALE_LOCK"
# Backdate the lock dir's mtime well past any reasonable timeout.
touch -t 202001010000 "$STALE_LOCK" 2>/dev/null || touch -d "2020-01-01" "$STALE_LOCK"

START="$(date +%s)"
bash "$LOCK_HELPER" acquire "$STALE_LOCK" 1 >/tmp/guards-lock-stale.$$.log 2>&1
ACQUIRE_RC=$?
END="$(date +%s)"
ELAPSED=$((END - START))
bash "$LOCK_HELPER" release "$STALE_LOCK" 2>/dev/null || true

record "case3_stale_lock_force_acquired" "$ACQUIRE_RC" "rc=$ACQUIRE_RC"
[[ "$ELAPSED" -lt 5 ]]; record "case3_stale_lock_acquired_promptly (took ${ELAPSED}s)" "$?"
grep -q "breaking stale lock" "/tmp/guards-lock-stale.$$.log"; record "case3_stale_lock_warning_logged" "$?"
rm -f "/tmp/guards-lock-stale.$$.log"

echo ""

# ==============================================================================
# Summary
# ==============================================================================
echo -e "${T_BOLD}===============================${T_NC}"
echo -e "${T_BOLD}  guards.json Concurrency Summary (MODE=$MODE)${T_NC}"
echo -e "${T_BOLD}===============================${T_NC}"
echo ""
echo -e "  Total:  ${T_BOLD}$TOTAL${T_NC}"
echo -e "  Passed: ${T_GREEN}$PASS${T_NC}"
echo -e "  Failed: ${T_RED}$FAIL${T_NC}"
echo ""

if [[ "$MODE" != "locked" ]]; then
  echo -e "${T_YELLOW}MODE=unlocked is a red-first probe (see Case 1/2 notes above), not a pass/fail gate.${T_NC}"
  exit 0
fi

if [[ $FAIL -gt 0 ]]; then
  echo -e "${T_RED}Failed tests:${T_NC}"
  for name in "${FAILED_NAMES[@]}"; do
    echo -e "  ${T_RED}-${T_NC} $name"
  done
  echo ""
  echo -e "${T_RED}RESULT: FAIL${T_NC}"
  exit 1
else
  echo -e "${T_GREEN}RESULT: ALL TESTS PASSED${T_NC}"
  exit 0
fi
