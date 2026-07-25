#!/usr/bin/env bash
#
# Regression test for scripts/version-sync-precommit.sh's .STATUS version
# extraction.
#
# .STATUS accumulates historical "vX.Y.Z SHIPPED" session-recap prose below
# its `version:` frontmatter field. The pre-fix `.STATUS)` case grepped the
# FIRST bare X.Y.Z number in the whole staged file — no `v` prefix required,
# no anchor — which risks matching a historical mention (or, in principle,
# any other X.Y.Z-shaped number in the recap prose) instead of the real
# `version:` field. This is the same bug class that false-positived
# scripts/pre-release-check.sh's docs/index.md check for both v4.2.0 and
# v4.3.0 (fixed in PR #308): grab the first bare version-shaped string
# instead of anchoring to the actual source-of-truth field.
#
# The fix anchors to `^version:` (the frontmatter field) before extracting
# the number.
#
# Usage: ./tests/test_version_sync_precommit.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOK_SCRIPT="$PROJECT_ROOT/scripts/version-sync-precommit.sh"

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

SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT

(
    cd "$SANDBOX"
    git init -q
    git config user.email "test@example.com"
    git config user.name "Test"

    mkdir -p .claude-plugin
    printf '{"name":"demo","version":"4.3.0"}\n' > .claude-plugin/plugin.json

    # .STATUS: `version:` frontmatter says 4.3.0 (matches SOT). This script
    # is a generic hook (also handles Cargo.toml/package.json/DESCRIPTION
    # projects), so it can't assume .STATUS's frontmatter is always the
    # first content in the file the way craft's own .STATUS convention
    # happens to keep it today. This fixture puts a decoy X.Y.Z-shaped
    # number (from unrelated historical prose) BEFORE the `version:` field
    # to force the discriminating case: an unanchored first-match grep picks
    # up the decoy; an anchored `^version:` grep does not.
    cat > .STATUS <<'STATUS'
milestone: **historical note, references the folio split since 3.9.1**
version: 4.3.0
progress: 100
STATUS

    git add .claude-plugin/plugin.json .STATUS
    bash "$HOOK_SCRIPT" >/tmp/version_sync_precommit_test_out.txt 2>&1
    echo $? > /tmp/version_sync_precommit_test_exit.txt
)

exit_code="$(cat /tmp/version_sync_precommit_test_exit.txt)"
output="$(cat /tmp/version_sync_precommit_test_out.txt)"
rm -f /tmp/version_sync_precommit_test_out.txt /tmp/version_sync_precommit_test_exit.txt

echo "Testing version-sync-precommit.sh .STATUS extraction..."
check ".STATUS with matching version: field, decoy number ahead of it in file order -> commit not blocked" 0 "$exit_code"
if [[ "$exit_code" -ne 0 ]]; then
    echo "  Output was:"
    echo "$output" | sed 's/^/    /'
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
[[ "$FAIL" -eq 0 ]]
