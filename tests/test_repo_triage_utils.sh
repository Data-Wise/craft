#!/usr/bin/env bash
# Test suite for lib/repo-triage-utils.sh — merge_candidates() / bucket_candidates()
# Phase 3.1 / 4.1 of ORCHESTRATE-repo-triage.md.
# Run from project root: bash tests/test_repo_triage_utils.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_FILE="${SCRIPT_DIR}/../lib/repo-triage-utils.sh"

T_RED='\033[0;31m'
T_GREEN='\033[0;32m'
T_BLUE='\033[0;34m'
T_BOLD='\033[1m'
T_NC='\033[0m'

TOTAL=0; PASS=0; FAIL=0
declare -a FAILED_NAMES=()
declare -a CLEANUP_FILES=()

cleanup() {
    for f in "${CLEANUP_FILES[@]}"; do
        [[ -f "$f" ]] && rm -f "$f"
    done
}
trap cleanup EXIT

make_tmpfile() {
    local f
    f=$(mktemp "${TMPDIR:-/tmp}/repo-triage-test.XXXXXX")
    CLEANUP_FILES+=("$f")
    echo "$f"
}

run_test() {
    local name="$1" expected="$2" actual="$3"
    TOTAL=$((TOTAL + 1))
    if [[ "$actual" == "$expected" ]]; then
        PASS=$((PASS + 1))
        echo -e "  ${T_GREEN}PASS${T_NC}  $name"
    else
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$name")
        echo -e "  ${T_RED}FAIL${T_NC}  $name  (expected='$expected', got='$actual')"
    fi
}

if [[ ! -f "$LIB_FILE" ]]; then
    echo -e "${T_RED}ERROR${T_NC}: $LIB_FILE not found"
    exit 1
fi

# shellcheck source=../lib/repo-triage-utils.sh
source "$LIB_FILE"

if ! command -v jq >/dev/null 2>&1; then
    echo -e "${T_RED}ERROR${T_NC}: jq is required for this test suite"
    exit 1
fi

# ============================================================================
# Group 1: merge_candidates — coupled branch+worktree pair
# ============================================================================

echo -e "${T_BLUE}--- Group 1: merge_candidates (coupled pair) ---${T_NC}"

BF=$(make_tmpfile)
WF=$(make_tmpfile)
cat > "$BF" <<'EOF'
{"branch":"feature/a","merge_evidence":"squash-merged","ancestor_result":"ancestor","pr_state":"merged","scoped_diff_result":"clean"}
EOF
cat > "$WF" <<'EOF'
{"path":"/wt/a","branch":"feature/a","is_merged_evidence":"squash-merged","lock_status":"unlocked"}
EOF

OUT=$(merge_candidates "$BF" "$WF")
LINE_COUNT=$(echo "$OUT" | wc -l | tr -d ' ')
run_test "coupled_pair_emits_one_item" "1" "$LINE_COUNT"

TYPE=$(echo "$OUT" | jq -r '.type')
run_test "coupled_pair_type" "branch+worktree" "$TYPE"

PATH_FIELD=$(echo "$OUT" | jq -r '.path')
run_test "coupled_pair_carries_worktree_path" "/wt/a" "$PATH_FIELD"

# ============================================================================
# Group 2: merge_candidates — no coupling (branch-only, worktree-only)
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 2: merge_candidates (no coupling) ---${T_NC}"

BF2=$(make_tmpfile)
WF2=$(make_tmpfile)
cat > "$BF2" <<'EOF'
{"branch":"feature/b","merge_evidence":"not-merged","ancestor_result":"not-ancestor","pr_state":"unknown","scoped_diff_result":"has-diff"}
EOF
cat > "$WF2" <<'EOF'
{"path":"/wt/c","branch":"feature/c","is_merged_evidence":"merged","lock_status":"unlocked"}
EOF

OUT2=$(merge_candidates "$BF2" "$WF2")
BRANCH_ONLY=$(echo "$OUT2" | jq -c 'select(.type == "branch")')
WT_ONLY=$(echo "$OUT2" | jq -c 'select(.type == "worktree")')

run_test "branch_only_present" "1" "$( [[ -n "$BRANCH_ONLY" ]] && echo 1 || echo 0)"
run_test "worktree_only_present" "1" "$( [[ -n "$WT_ONLY" ]] && echo 1 || echo 0)"

# ============================================================================
# Group 3: merge_candidates — dedup (no double-counting a coupled branch)
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 3: merge_candidates (dedup) ---${T_NC}"

BF3=$(make_tmpfile)
WF3=$(make_tmpfile)
cat > "$BF3" <<'EOF'
{"branch":"feature/dup","merge_evidence":"squash-merged","ancestor_result":"ancestor","pr_state":"merged","scoped_diff_result":"clean"}
EOF
cat > "$WF3" <<'EOF'
{"path":"/wt/dup","branch":"feature/dup","is_merged_evidence":"squash-merged","lock_status":"unlocked"}
EOF

OUT3=$(merge_candidates "$BF3" "$WF3")
DUP_COUNT=$(echo "$OUT3" | jq -r '.branch' | grep -c "feature/dup")
run_test "coupled_branch_appears_exactly_once" "1" "$DUP_COUNT"

# ============================================================================
# Group 4: merge_candidates — empty inputs (missing files) don't error
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 4: merge_candidates (empty inputs) ---${T_NC}"

OUT4=$(merge_candidates /nonexistent/branches.jsonl /nonexistent/worktrees.jsonl 2>&1)
run_test "missing_files_produce_no_output" "" "$OUT4"

# ============================================================================
# Group 5: bucket_candidates
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 5: bucket_candidates ---${T_NC}"

BUCKET_OUT=$(printf '%s\n' \
  '{"status":"unclear","evidence":[],"reasoning":"x"}' \
  '{"status":"valid","evidence":[],"reasoning":"y"}' \
  '{"status":"moot","evidence":[],"reasoning":"z"}' \
  | bucket_candidates)

UNCLEAR_BUCKET=$(echo "$BUCKET_OUT" | jq -c 'select(.status == "unclear") | .bucket' | tr -d '"')
run_test "unclear_is_grill_ready" "grill-ready" "$UNCLEAR_BUCKET"

# ============================================================================
# Group 6: merge_candidates preserves every collector field (GRILL decision 10)
# The join used to rebuild each object from four named fields, silently dropping
# anything the collector added later.
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 6: merge_candidates preserves new evidence fields ---${T_NC}"

NEW_FIELDS='"pr_open":"no","pr_head_match":"match","pr_merge_in_base":"yes","upstream_status":"ahead","worktree_status":"live","owner_hint":"tool"'
BF6=$(make_tmpfile)
WF6=$(make_tmpfile)
cat > "$BF6" <<EOF
{"branch":"feature/coupled","merge_evidence":"not-merged","ancestor_result":"not-ancestor","pr_state":"merged","scoped_diff_result":"has-diff",${NEW_FIELDS}}
{"branch":"feature/solo","merge_evidence":"not-merged","ancestor_result":"not-ancestor","pr_state":"merged","scoped_diff_result":"has-diff",${NEW_FIELDS}}
EOF
cat > "$WF6" <<'EOF'
{"path":"/wt/coupled","branch":"feature/coupled","is_merged_evidence":"not-merged","lock_status":"unlocked"}
EOF
OUT6=$(merge_candidates "$BF6" "$WF6")
for key in pr_open pr_head_match pr_merge_in_base upstream_status worktree_status owner_hint; do
    EXPECTED=$(echo "{${NEW_FIELDS}}" | jq -r --arg k "$key" '.[$k]')
    GOT_C=$(echo "$OUT6" | jq -r --arg k "$key" 'select(.branch == "feature/coupled") | .[$k]')
    GOT_S=$(echo "$OUT6" | jq -r --arg k "$key" 'select(.branch == "feature/solo") | .[$k]')
    run_test "join_keeps_${key}_coupled" "$EXPECTED" "$GOT_C"
    run_test "join_keeps_${key}_solo"    "$EXPECTED" "$GOT_S"
done
# The worktree fields must still be merged onto the coupled item, and the type kept.
run_test "join_coupled_type_and_path" "branch+worktree|/wt/coupled" \
    "$(echo "$OUT6" | jq -r 'select(.branch == "feature/coupled") | [.type, .path] | join("|")')"
run_test "join_solo_type" "branch" "$(echo "$OUT6" | jq -r 'select(.branch == "feature/solo") | .type')"

VALID_BUCKET=$(echo "$BUCKET_OUT" | jq -c 'select(.status == "valid") | .bucket' | tr -d '"')
run_test "valid_is_plan_ready" "plan-ready" "$VALID_BUCKET"

MOOT_BUCKET=$(echo "$BUCKET_OUT" | jq -c 'select(.status == "moot") | .bucket' | tr -d '"')
run_test "moot_falls_back_to_defer" "defer" "$MOOT_BUCKET"

# ============================================================================
# Group 7: verdict_candidates — GRILL decisions 1, 6, 7, 8, 13, 14, 15
# Pure jq over the evidence fields; no git, no network. Base fixture is an
# unmerged, pushed, non-tool branch (verdict KEEP); each case overrides fields.
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 7: verdict_candidates ---${T_NC}"

BASE_EV='{"type":"branch","branch":"feature/t","merge_evidence":"not-merged","ancestor_result":"not-ancestor","pr_state":"unknown","pr_open":"no","pr_head_match":"none","pr_merge_in_base":"na","upstream_status":"present","worktree_status":"none","owner_hint":"none","scoped_diff_result":"has-diff"}'

verdict_of() { # <jq filter producing the object under test> -> "VERDICT"
    echo "$BASE_EV" | jq -c "$1" | verdict_candidates | jq -r '.verdict'
}
v() { verdict_of ". + $1"; }   # v '{"k":"v"}' -> verdict with those overrides

# --- one happy path per verdict ---
run_test "base_unmerged_pushed_is_keep"        "KEEP"               "$(verdict_of '.')"
run_test "ancestor_is_delete_safe"             "DELETE-SAFE"        "$(v '{"ancestor_result":"ancestor","merge_evidence":"merged"}')"
run_test "no_upstream_unmerged_is_backup"      "BACKUP-THEN-DECIDE" "$(v '{"upstream_status":"none"}')"
run_test "live_worktree_is_keep"               "KEEP"               "$(v '{"worktree_status":"live"}')"

# Merged PR whose head equals the tip, merge commit in base, content proven.
PR_OK='{"pr_head_match":"match","pr_merge_in_base":"yes","merge_evidence":"squash-merged","upstream_status":"none"}'
run_test "merged_pr_with_content_proof_delete_safe" "DELETE-SAFE"   "$(v "$PR_OK")"

# --- decision 7: a reverted PR (PR evidence but content not in base) is never DELETE-SAFE ---
REVERTED='{"pr_head_match":"match","pr_merge_in_base":"yes","merge_evidence":"not-merged","upstream_status":"none"}'
run_test "reverted_pr_no_remote_is_backup"     "BACKUP-THEN-DECIDE" "$(v "$REVERTED")"
run_test "reverted_pr_ahead_is_backup"         "BACKUP-THEN-DECIDE" "$(v '{"pr_head_match":"match","pr_merge_in_base":"yes","merge_evidence":"not-merged","upstream_status":"ahead"}')"
# ... unless a durable remote ref holds the tip (decision 7's second proof).
run_test "reverted_pr_remote_holds_tip_delete_safe" "DELETE-SAFE"   "$(v '{"pr_head_match":"match","pr_merge_in_base":"yes","merge_evidence":"not-merged","upstream_status":"present"}')"
# PR merged into a non-base branch: the merge commit is not in base.
run_test "pr_merged_elsewhere_not_delete_safe" "BACKUP-THEN-DECIDE" "$(v '{"pr_head_match":"match","pr_merge_in_base":"no","merge_evidence":"squash-merged","upstream_status":"none"}')"
run_test "pr_head_mismatch_not_delete_safe"    "BACKUP-THEN-DECIDE" "$(v '{"pr_head_match":"mismatch","merge_evidence":"squash-merged","upstream_status":"none"}')"
# Planted control: a branch one commit off base has no PR and is not an ancestor.
run_test "one_commit_off_branch_not_delete_safe" "BACKUP-THEN-DECIDE" "$(v '{"upstream_status":"none","merge_evidence":"not-merged","pr_head_match":"none"}')"
# Squash evidence alone (no PR) is not enough under decision 2.
run_test "squash_evidence_without_pr_not_delete_safe" "BACKUP-THEN-DECIDE" "$(v '{"merge_evidence":"squash-merged","upstream_status":"none"}')"

# --- precedence pairs (decision 14: UNKNOWN > KEEP > DELETE-SAFE > BACKUP > KEEP) ---
ANC='"ancestor_result":"ancestor","merge_evidence":"merged"'
# Override objects are built in plain assignments: macOS bash 3.2 brace-expands
# "{${VAR},\"k\":\"v\"}" when it appears inside $(...), mangling the jq filter.
OV_LIVE="{${ANC},\"worktree_status\":\"live\"}"
OV_OPEN="{${ANC},\"pr_open\":\"yes\"}"
OV_NOUP="{${ANC},\"upstream_status\":\"none\"}"
OV_PRUNK="{${ANC},\"pr_head_match\":\"unknown\"}"
run_test "live_worktree_beats_delete_safe"     "KEEP"               "$(v "$OV_LIVE")"
run_test "open_pr_beats_delete_safe"           "KEEP"               "$(v "$OV_OPEN")"
run_test "delete_safe_beats_backup"            "DELETE-SAFE"        "$(v "$OV_NOUP")"
run_test "backup_beats_tool_keep"              "BACKUP-THEN-DECIDE" "$(v '{"upstream_status":"none","owner_hint":"tool"}')"
run_test "unknown_beats_keep_live"             "UNKNOWN"            "$(v '{"worktree_status":"live","pr_open":"unknown"}')"
run_test "unknown_beats_delete_safe"           "UNKNOWN"            "$(v "$OV_PRUNK")"
run_test "open_pr_beats_backup"                "KEEP"               "$(v '{"pr_open":"yes","upstream_status":"none"}')"

# --- the two KEEP flavors are told apart by evidence ---
run_test "tool_keep_evidence" "tool-owned" \
    "$(echo "$BASE_EV" | jq -c '. + {"owner_hint":"tool"}' | verdict_candidates | jq -r '.evidence | if test("tool-owned") then "tool-owned" else . end')"
run_test "pushed_keep_evidence" "unmerged, pushed" \
    "$(echo "$BASE_EV" | verdict_candidates | jq -r '.evidence')"

# --- decision 8: unknown, absent, empty and off-enum evidence => UNKNOWN, never a delete ---
for key in merge_evidence ancestor_result pr_open pr_head_match pr_merge_in_base upstream_status worktree_status owner_hint; do
    run_test "unknown_${key}_is_unknown"  "UNKNOWN" "$(verdict_of ". + {\"$key\":\"unknown\"}")"
    run_test "absent_${key}_is_unknown"   "UNKNOWN" "$(verdict_of "del(.$key)")"
    run_test "empty_${key}_is_unknown"    "UNKNOWN" "$(verdict_of ". + {\"$key\":\"\"}")"
    run_test "offenum_${key}_is_unknown"  "UNKNOWN" "$(verdict_of ". + {\"$key\":\"bogus\"}")"
done
# A DELETE-SAFE-looking branch with one field missing must not be DELETE-SAFE.
run_test "ancestor_with_absent_pr_open_is_unknown" "UNKNOWN" "$(verdict_of ". + {${ANC}} | del(.pr_open)")"
# Worktree-only items carry no branch evidence.
run_test "worktree_only_item_is_unknown" "UNKNOWN" \
    "$(echo '{"type":"worktree","branch":"feature/w","path":"/wt/w","is_merged_evidence":"merged","lock_status":"unlocked"}' | verdict_candidates | jq -r '.verdict')"

# --- passthrough and shape ---
SHAPE=$(echo "$BASE_EV" | verdict_candidates | jq -c '[.branch, .type, .pr_open, (.evidence | type), (.evidence | length > 0)]')
run_test "output_keeps_input_fields_and_adds_evidence" '["feature/t","branch","no","string",true]' "$SHAPE"

# --- exhaustive safety invariants over every valid evidence combination ---
INV=$(jq -cn '
    def vals: {merge_evidence:["merged","squash-merged","not-merged","unknown"],
               ancestor_result:["ancestor","not-ancestor","unknown"],
               pr_open:["yes","no","unknown"],
               pr_head_match:["match","mismatch","none","unknown"],
               pr_merge_in_base:["yes","no","na","unknown"],
               upstream_status:["none","ahead","present","unknown"],
               worktree_status:["live","none","unknown"],
               owner_hint:["tool","none","unknown"]};
    [vals | to_entries[] | .key as $k | .value | map({($k): .})]
    | reduce .[] as $set ([{}]; [ .[] as $acc | $set[] | $acc + . ])
    | .[] | . + {type:"branch", branch:"b"}' \
  | verdict_candidates \
  | jq -rs '
    def fields: ["merge_evidence","ancestor_result","pr_open","pr_head_match","pr_merge_in_base","upstream_status","worktree_status","owner_hint"];
    def any_unknown: . as $o | any(fields[]; $o[.] == "unknown");
    def landed: .ancestor_result == "ancestor"
        or (.pr_head_match == "match" and .pr_merge_in_base == "yes"
            and ((.merge_evidence | IN("squash-merged","merged")) or .upstream_status == "present"));
    { total: length,
      delete_safe_without_proof: [ .[] | select(.verdict == "DELETE-SAFE")
          | select((any_unknown) or (.worktree_status != "none") or (.pr_open != "no") or ((landed) | not)) ] | length,
      unknown_not_flagged:       [ .[] | select(any_unknown and .verdict != "UNKNOWN") ] | length,
      live_or_open_deleted:      [ .[] | select((.worktree_status == "live" or .pr_open == "yes") and .verdict == "DELETE-SAFE") ] | length,
      bad_verdict:               [ .[] | select(.verdict | IN("DELETE-SAFE","BACKUP-THEN-DECIDE","KEEP","UNKNOWN") | not) ] | length,
      empty_evidence:            [ .[] | select((.evidence | type) != "string" or (.evidence | length) == 0) ] | length
    } | [.total, .delete_safe_without_proof, .unknown_not_flagged, .live_or_open_deleted, .bad_verdict, .empty_evidence] | join("|")')
run_test "invariants_total_combos_and_zero_violations" "20736|0|0|0|0|0" "$INV"

# ============================================================================
# Summary
# ============================================================================

echo ""
echo -e "${T_BOLD}===============================${T_NC}"
echo -e "${T_BOLD}  repo-triage-utils Test Summary${T_NC}"
echo -e "${T_BOLD}===============================${T_NC}"
echo ""
echo -e "  Total:  ${T_BOLD}$TOTAL${T_NC}"
echo -e "  Passed: ${T_GREEN}$PASS${T_NC}"
echo -e "  Failed: ${T_RED}$FAIL${T_NC}"
echo ""

if [[ $FAIL -gt 0 ]]; then
    echo -e "${T_RED}Failed tests:${T_NC}"
    for name in "${FAILED_NAMES[@]}"; do
        echo -e "  ${T_RED}-${T_NC} $name"
    done
    echo -e "${T_RED}RESULT: FAIL${T_NC}"
    exit 1
else
    echo -e "${T_GREEN}RESULT: ALL TESTS PASSED${T_NC}"
    exit 0
fi
