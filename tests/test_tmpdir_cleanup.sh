#!/usr/bin/env bash
# Guards against temp-dir leaks in the bash test suites.
#
# Each suite's make_tmpdir is called as dir=$(make_tmpdir), which runs in a
# subshell, so its CLEANUP_DIRS+= never reaches the parent and the EXIT trap
# removes nothing. Each suite runs here with its own empty TMPDIR; after it
# exits the TMPDIR must be empty again. (The suites' pass/fail results are not
# judged here, only what they leave behind.)
#
# Usage: ./tests/test_tmpdir_cleanup.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SUITES=(
    test_branch_guard
    test_branch_guard_e2e
    test_git_dryrun
    test_git_utils
    test_insights_improvements_e2e
    test_marketplace_e2e
    test_no_switch_guard
    test_release_skill_e2e
)

PASS=0
FAIL=0
BASE="$(mktemp -d)"
trap 'rm -rf "$BASE"' EXIT

for suite in "${SUITES[@]}"; do
    iso="$BASE/$suite"
    mkdir -p "$iso"
    TMPDIR="$iso" bash "$SCRIPT_DIR/$suite.sh" >/dev/null 2>&1
    left=$(find "$iso" -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ')
    if [[ "$left" -eq 0 ]]; then
        echo "  ✓ $suite leaves no temp dirs"
        PASS=$((PASS + 1))
    else
        echo "  ✗ $suite leaked $left temp dir(s)"
        FAIL=$((FAIL + 1))
    fi
done

echo ""
echo "Results: $PASS passed, $FAIL failed"
[[ "$FAIL" -eq 0 ]]
