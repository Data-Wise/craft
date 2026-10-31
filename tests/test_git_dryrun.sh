#!/usr/bin/env bash
# Test suite for lib/git-utils.sh — worktree_clean_dry_run() / branch_cleanup_dry_run()
# Phase 0 of docs/specs/ (see ORCHESTRATE-repo-triage.md) — `dev/git` Operation 5
# and Operation 4's dry-run / structured-output contract.
# Run from project root: bash tests/test_git_dryrun.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GIT_UTILS="${SCRIPT_DIR}/../lib/git-utils.sh"

T_RED='\033[0;31m'
T_GREEN='\033[0;32m'
T_BLUE='\033[0;34m'
T_BOLD='\033[1m'
T_NC='\033[0m'

TOTAL=0; PASS=0; FAIL=0
declare -a FAILED_NAMES=()
declare -a CLEANUP_DIRS=()

cleanup() {
    for dir in "${CLEANUP_DIRS[@]}"; do
        [[ -d "$dir" ]] && rm -rf "$dir"
    done
}
trap cleanup EXIT

make_tmpdir() {
    local dir
    dir=$(mktemp -d "${TMPDIR:-/tmp}/git-dryrun-test.XXXXXX")
    CLEANUP_DIRS+=("$dir")
    echo "$dir"
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

assert_true() {
    local name="$1" cond="$2"
    TOTAL=$((TOTAL + 1))
    if [[ "$cond" == "1" ]]; then
        PASS=$((PASS + 1))
        echo -e "  ${T_GREEN}PASS${T_NC}  $name"
    else
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$name")
        echo -e "  ${T_RED}FAIL${T_NC}  $name"
    fi
}

# ============================================================================
# Pre-flight
# ============================================================================

if [[ ! -f "$GIT_UTILS" ]]; then
    echo -e "${T_RED}ERROR${T_NC}: $GIT_UTILS not found"
    exit 1
fi

# shellcheck source=../lib/git-utils.sh
source "$GIT_UTILS"

if ! command -v jq >/dev/null 2>&1; then
    echo -e "${T_RED}ERROR${T_NC}: jq is required for this test suite"
    exit 1
fi

make_repo() {
    local repo
    repo=$(make_tmpdir)
    (
        cd "$repo"
        git init -b main --quiet
        git config user.email "test@test.com"
        git config user.name "Test User"
        echo "# README" > README.md
        git add README.md
        git commit -m "Initial commit" --quiet
        git branch dev
    )
    echo "$repo"
}

add_commit() {
    local repo="$1" msg="$2" file="${3:-file.txt}"
    echo "$msg" >> "${repo}/${file}"
    git -C "$repo" add "$file"
    git -C "$repo" commit -m "$msg" --quiet
}

# ============================================================================
# Group 1: branch_cleanup_dry_run — squash-merged branch, no mutation
# ============================================================================

echo -e "${T_BLUE}--- Group 1: branch_cleanup_dry_run (squash-merged) ---${T_NC}"

REPO1=$(make_repo)
git -C "$REPO1" checkout dev --quiet
git -C "$REPO1" checkout -b "feature/sq-test" --quiet
add_commit "$REPO1" "feat: feature work" "feature.txt"
git -C "$REPO1" checkout dev --quiet
git -C "$REPO1" merge --squash "feature/sq-test" --quiet
git -C "$REPO1" commit -m "squash: feature work" --quiet

BRANCHES_BEFORE=$(git -C "$REPO1" branch --format='%(refname:short)' | sort)
OUT1=$(cd "$REPO1" && branch_cleanup_dry_run dev)
BRANCHES_AFTER=$(git -C "$REPO1" branch --format='%(refname:short)' | sort)

run_test "branch_cleanup_zero_mutation" "$BRANCHES_BEFORE" "$BRANCHES_AFTER"

LINE1=$(echo "$OUT1" | grep '"feature/sq-test"')
run_test "branch_cleanup_emits_squash_candidate" "1" "$( [[ -n "$LINE1" ]] && echo 1 || echo 0)"

MERGE_EVIDENCE=$(echo "$LINE1" | jq -r '.merge_evidence')
run_test "branch_cleanup_merge_evidence_squash" "squash-merged" "$MERGE_EVIDENCE"

SCOPED_DIFF=$(echo "$LINE1" | jq -r '.scoped_diff_result')
run_test "branch_cleanup_scoped_diff_clean" "clean" "$SCOPED_DIFF"

KEYS=$(echo "$LINE1" | jq -S -c 'keys')
run_test "branch_cleanup_output_shape" '["ancestor_result","branch","merge_evidence","pr_head_match","pr_merge_in_base","pr_open","pr_state","scoped_diff_result"]' "$KEYS"

# ============================================================================
# Group 2: branch_cleanup_dry_run — active/unmerged branch NOT flagged
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 2: branch_cleanup_dry_run (active branch) ---${T_NC}"

REPO2=$(make_repo)
git -C "$REPO2" checkout dev --quiet
git -C "$REPO2" checkout -b "feature/active" --quiet
add_commit "$REPO2" "feat: still in progress" "wip.txt"
git -C "$REPO2" checkout dev --quiet

OUT2=$(cd "$REPO2" && branch_cleanup_dry_run dev)
LINE2=$(echo "$OUT2" | grep '"feature/active"')
MERGE_EVIDENCE2=$(echo "$LINE2" | jq -r '.merge_evidence')
run_test "branch_cleanup_active_branch_not_merged" "not-merged" "$MERGE_EVIDENCE2"

# ============================================================================
# Group 3: worktree_clean_dry_run — squash-merged worktree, no mutation
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 3: worktree_clean_dry_run (squash-merged worktree) ---${T_NC}"

REPO3=$(make_repo)
git -C "$REPO3" checkout dev --quiet
git -C "$REPO3" checkout -b "feature/wt-sq" --quiet
add_commit "$REPO3" "feat: worktree feature" "wtfeature.txt"
git -C "$REPO3" checkout dev --quiet

WT_DIR=$(make_tmpdir)
rmdir "$WT_DIR" 2>/dev/null || true
git -C "$REPO3" worktree add "$WT_DIR" "feature/wt-sq" --quiet
WT_DIR_RESOLVED=$(cd "$(dirname "$WT_DIR")" && pwd -P)/$(basename "$WT_DIR")

git -C "$REPO3" merge --squash "feature/wt-sq" --quiet
git -C "$REPO3" commit -m "squash: worktree feature" --quiet

WORKTREES_BEFORE=$(git -C "$REPO3" worktree list --porcelain)
OUT3=$(cd "$REPO3" && worktree_clean_dry_run dev)
WORKTREES_AFTER=$(git -C "$REPO3" worktree list --porcelain)

run_test "worktree_clean_zero_mutation" "$WORKTREES_BEFORE" "$WORKTREES_AFTER"

LINE3=$(echo "$OUT3" | grep '"feature/wt-sq"')
run_test "worktree_clean_emits_squash_candidate" "1" "$( [[ -n "$LINE3" ]] && echo 1 || echo 0)"

WT_EVIDENCE=$(echo "$LINE3" | jq -r '.is_merged_evidence')
run_test "worktree_clean_evidence_squash" "squash-merged" "$WT_EVIDENCE"

WT_PATH=$(echo "$LINE3" | jq -r '.path')
run_test "worktree_clean_path_matches" "$WT_DIR_RESOLVED" "$WT_PATH"

WT_KEYS=$(echo "$LINE3" | jq -S -c 'keys')
run_test "worktree_clean_output_shape" '["branch","is_merged_evidence","lock_status","path"]' "$WT_KEYS"

# Main worktree is never emitted as a candidate
MAIN_LINE=$(echo "$OUT3" | grep -c "\"$REPO3\"" || true)
run_test "worktree_clean_excludes_main_worktree" "0" "$MAIN_LINE"

# ============================================================================
# Group 4: Non-goal — neither function calls a mutating git subcommand
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 4: Non-goal (never mutates) ---${T_NC}"

MUTATING_CALLS=$(grep -nE 'git (branch -D|branch -d|worktree remove|worktree prune)' "$GIT_UTILS" | grep -vE '^[0-9]+:[[:space:]]*#' || true)
assert_true "git_utils_never_calls_mutating_commands" "$( [[ -z "$MUTATING_CALLS" ]] && echo 1 || echo 0)"

# ============================================================================
# Shims: fake `gh` (canned PR JSON / forced failure) and a `git` wrapper that
# can force `merge-base --is-ancestor` to a chosen exit code. Both sit first on
# PATH only inside the subshells below, so the groups above are untouched.
# (GRILL-branch-triage-verdicts decisions 9, 11, 13.)
# ============================================================================

REAL_GIT=$(command -v git)
SHIM_DIR=$(make_tmpdir)
cat > "${SHIM_DIR}/gh" <<'SHIM'
#!/usr/bin/env bash
if [[ -n "${GH_SHIM_FAIL:-}" ]]; then echo "gh: simulated failure" >&2; exit 1; fi
cat "${GH_SHIM_JSON:?GH_SHIM_JSON unset}"
SHIM
cat > "${SHIM_DIR}/git" <<SHIM
#!/usr/bin/env bash
if [[ -n "\${GIT_SHIM_ANCESTOR_RC:-}" && "\$1" == "merge-base" && "\$2" == "--is-ancestor" ]]; then
  exit "\$GIT_SHIM_ANCESTOR_RC"
fi
exec "${REAL_GIT}" "\$@"
SHIM
chmod +x "${SHIM_DIR}/gh" "${SHIM_DIR}/git"

# branch_json <repo> <branch> [ENV=VAL ...] -> the branch's JSONL line, shims on PATH.
branch_json() {
    local repo="$1" branch="$2"; shift 2
    (cd "$repo" && env PATH="${SHIM_DIR}:${PATH}" "$@" bash -c \
        'source "$0"; branch_cleanup_dry_run dev' "$GIT_UTILS") | grep "\"${branch}\""
}

# pr_entry <number> <state> <headRefOid> <mergeOid|null> <isCrossRepository>
pr_entry() {
    jq -cn --argjson n "$1" --arg s "$2" --arg h "$3" --arg m "$4" --argjson x "$5" \
        '{number:$n, state:$s, headRefOid:$h, isCrossRepository:$x,
          mergeCommit:(if $m == "null" then null else {oid:$m} end)}'
}

# pr_file: slurp PR entries from stdin into a JSON array file. Fails the whole run
# if the result is not a flat array of objects, so a malformed fixture cannot
# silently satisfy an assertion (GRILL decision 13).
pr_file() {
    local f; f=$(make_tmpdir)/prs.json
    jq -cs '.' > "$f"
    if ! jq -e 'type == "array" and all(.[]; type == "object")' "$f" >/dev/null 2>&1; then
        echo "FIXTURE ERROR: invalid PR JSON in $f" >&2
        # pr_file runs inside $(...); `exit` would only end that subshell, so
        # signal the main script ($$ is the parent shell's PID) to abort the run.
        kill -TERM $$
        exit 2
    fi
    echo "$f"
}

# Fixture: feature/p1 has tip T (not an ancestor of dev); dev holds squash commit S.
REPO5=$(make_repo)
git -C "$REPO5" checkout dev --quiet
git -C "$REPO5" checkout -b "feature/p1" --quiet
add_commit "$REPO5" "feat: p1 work" "p1.txt"
TIP5=$(git -C "$REPO5" rev-parse feature/p1)
git -C "$REPO5" checkout dev --quiet
git -C "$REPO5" merge --squash "feature/p1" --quiet
git -C "$REPO5" commit -m "squash: p1" --quiet
SQUASH5=$(git -C "$REPO5" rev-parse dev)
OTHER5=$(git -C "$REPO5" rev-parse main)

# ============================================================================
# Group 5: ancestor_result — exit 1 is "not-ancestor", other failures are "unknown"
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 5: ancestor_result exit-code mapping (decision 9) ---${T_NC}"

anc() { branch_json "$REPO5" "feature/p1" GH_SHIM_FAIL=1 "$@" | jq -r '.ancestor_result'; }
run_test "ancestry_rc0_is_ancestor"        "ancestor"     "$(anc GIT_SHIM_ANCESTOR_RC=0)"
run_test "ancestry_rc1_is_not_ancestor"    "not-ancestor" "$(anc GIT_SHIM_ANCESTOR_RC=1)"
run_test "ancestry_rc128_is_unknown"       "unknown"      "$(anc GIT_SHIM_ANCESTOR_RC=128)"
run_test "ancestry_rc129_is_unknown"       "unknown"      "$(anc GIT_SHIM_ANCESTOR_RC=129)"

# ============================================================================
# Group 6: PR evidence — pr_open / pr_head_match / pr_merge_in_base (decisions 8, 11)
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 6: PR evidence fields (decisions 8, 11) ---${T_NC}"

# pr_ev <json-file|FAIL> -> "open|head_match|merge_in_base"
pr_ev() {
    local src="$1" line
    if [[ "$src" == "FAIL" ]]; then
        line=$(branch_json "$REPO5" "feature/p1" GH_SHIM_FAIL=1)
    else
        line=$(branch_json "$REPO5" "feature/p1" GH_SHIM_JSON="$src")
    fi
    echo "$line" | jq -r '[.pr_open, .pr_head_match, .pr_merge_in_base] | join("|")'
}

F=$(pr_entry 1 MERGED "$TIP5" "$SQUASH5" false | pr_file)
run_test "pr_match_head_and_merge_in_base"   "no|match|yes"      "$(pr_ev "$F")"

F=$(pr_entry 1 MERGED "$OTHER5" "$SQUASH5" false | pr_file)
run_test "pr_head_mismatch"                  "no|mismatch|na"    "$(pr_ev "$F")"

# Planted control: an empty PR head must never match (empty-operand guard).
F=$(pr_entry 1 MERGED "" "$SQUASH5" false | pr_file)
run_test "pr_empty_head_never_matches"       "no|mismatch|na"    "$(pr_ev "$F")"

F=$(printf '' | pr_file)
run_test "pr_none_found"                     "no|none|na"        "$(pr_ev "$F")"

F=$( { pr_entry 1 MERGED "$TIP5" "$SQUASH5" false; pr_entry 2 OPEN "$TIP5" null false; } | pr_file)
run_test "pr_open_and_merged_collision"      "yes|match|yes"     "$(pr_ev "$F")"

# Fork PR with the same branch name and tip is ignored entirely.
F=$(pr_entry 1 MERGED "$TIP5" "$SQUASH5" true | pr_file)
run_test "pr_fork_head_ignored"              "no|none|na"        "$(pr_ev "$F")"

# PR merged into some other branch: head matches but the merge commit is not in base.
F=$(pr_entry 1 MERGED "$TIP5" "$TIP5" false | pr_file)
run_test "pr_merge_commit_not_in_base"       "no|match|no"       "$(pr_ev "$F")"

# Merge commit object absent locally (shallow/unfetched): unknown, never "no".
F=$(pr_entry 1 MERGED "$TIP5" "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" false | pr_file)
run_test "pr_missing_merge_object_unknown"   "no|match|unknown"  "$(pr_ev "$F")"

F=$(pr_entry 1 MERGED "$TIP5" null false | pr_file)
run_test "pr_null_merge_commit_unknown"      "no|match|unknown"  "$(pr_ev "$F")"

# Planted control: a failed lookup must read unknown, never "none".
run_test "pr_gh_failure_is_unknown"          "unknown|unknown|unknown" "$(pr_ev FAIL)"

# A result list as long as the request limit may be truncated: unknown.
F=$(for i in $(seq 1 100); do pr_entry "$i" CLOSED "$OTHER5" null false; done | pr_file)
run_test "pr_result_at_limit_is_unknown"     "unknown|unknown|unknown" "$(pr_ev "$F")"

# ============================================================================
# Group 7: Collector never mutates — git spy rejects mutating subcommands
# ============================================================================

echo ""
echo -e "${T_BLUE}--- Group 7: git spy (decision 13) ---${T_NC}"

SPY_DIR=$(make_tmpdir)
SPY_LOG="${SPY_DIR}/calls.log"
cat > "${SPY_DIR}/git" <<SHIM
#!/usr/bin/env bash
echo "\$*" >> "${SPY_LOG}"
case "\$1" in
  branch) for a in "\$@"; do [[ "\$a" == "-d" || "\$a" == "-D" || "\$a" == "--delete" || "\$a" == "-m" || "\$a" == "-M" ]] && { echo "SPY: mutating \$*" >&2; exit 99; }; done ;;
  worktree) [[ "\$2" == "remove" || "\$2" == "prune" || "\$2" == "add" || "\$2" == "move" ]] && { echo "SPY: mutating \$*" >&2; exit 99; } ;;
  update-ref|checkout|switch|reset|commit|push|merge|rebase|gc|prune) echo "SPY: mutating \$*" >&2; exit 99 ;;
esac
exec "${REAL_GIT}" "\$@"
SHIM
chmod +x "${SPY_DIR}/git"
F=$(pr_entry 1 MERGED "$TIP5" "$SQUASH5" false | pr_file)
(cd "$REPO5" && env PATH="${SPY_DIR}:${SHIM_DIR}:${PATH}" GH_SHIM_JSON="$F" bash -c \
    'source "$0"; branch_cleanup_dry_run dev; worktree_clean_dry_run dev' "$GIT_UTILS" >/dev/null 2>"${SPY_DIR}/stderr.log")
SPY_HITS=$(grep -c 'SPY: mutating' "${SPY_DIR}/stderr.log" || true)
SPY_CALLS=$(wc -l < "$SPY_LOG" | tr -d ' ')
run_test "spy_no_mutating_git_calls"         "0" "$SPY_HITS"
# Guard: the spy must actually have seen git run, or a silent pass proves nothing.
assert_true "spy_observed_git_calls"         "$( [[ "$SPY_CALLS" -gt 0 ]] && echo 1 || echo 0)"

# ============================================================================
# Summary
# ============================================================================

echo ""
echo -e "${T_BOLD}===============================${T_NC}"
echo -e "${T_BOLD}  git-dryrun Test Summary${T_NC}"
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
