#!/usr/bin/env bash
#
# Regression test for scripts/version-sync.sh
#
# Guards the `set -euo pipefail` false-fail fix (PR #145). Under pipefail,
# a `grep | head` pipeline that finds NO match returns non-zero, and a
# trailing `[[ cond ]] && echo` short-circuits to 1 — either aborts the
# script mid-run under `set -e`.
#
# The discriminating scenario: a project with a version source of truth
# (pyproject.toml) PLUS a checked candidate file (CLAUDE.md) that has no
# version line. `check_file` then runs its `grep ... | head` and finds
# nothing. In `--quiet` mode the trailing `&& echo` also short-circuits.
# Pre-fix this aborts (exit 1); fixed it completes (exit 0).
#
# Verified to FAIL against the pre-fix script and PASS against the fix —
# i.e. it actually catches the regression, not a tautology.
#
# Usage: ./tests/test_version_sync.sh

# Note: not using `set -e` here — we want to observe the script's exit code.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VERSION_SYNC="$PROJECT_ROOT/scripts/version-sync.sh"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

PASS=0
FAIL=0

check() {
    local name="$1" expected="$2" actual="$3"
    if [[ "$expected" == "$actual" ]]; then
        echo -e "  ${GREEN}✓${NC} $name"
        PASS=$((PASS + 1))
    else
        echo -e "  ${RED}✗${NC} $name (expected exit $expected, got $actual)"
        FAIL=$((FAIL + 1))
    fi
}

# Build the discriminating project: a SoT (pyproject.toml) + a checked
# candidate (CLAUDE.md) with NO version line, so check_file's grep|head
# finds nothing — the exact pre-fix abort trigger.
make_trigger_project() {
    local dir="$1"
    printf '[project]\nname = "demo"\nversion = "1.2.3"\n' > "$dir/pyproject.toml"
    printf '# Demo project\n\nNo version line in this file.\n' > "$dir/CLAUDE.md"
}

echo "Testing version-sync.sh set -e robustness..."

WORKDIR="$(mktemp -d)"
EMPTYDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR" "$EMPTYDIR"' EXIT

make_trigger_project "$WORKDIR"

# 1. --quiet on the trigger project: the regression scenario. Must complete.
( cd "$WORKDIR" && bash "$VERSION_SYNC" --quiet >/dev/null 2>&1 )
check "--quiet completes on no-match candidate (the regression)" 0 $?

# 2. Verbose mode on the same project must also complete.
( cd "$WORKDIR" && bash "$VERSION_SYNC" >/dev/null 2>&1 )
check "verbose mode completes on no-match candidate" 0 $?

# 3. No source-of-truth path (empty dir) must not abort either.
( cd "$EMPTYDIR" && bash "$VERSION_SYNC" --quiet >/dev/null 2>&1 )
check "no-source-of-truth path completes" 0 $?

echo ""
echo "Results: $PASS passed, $FAIL failed"
[[ "$FAIL" -eq 0 ]]
