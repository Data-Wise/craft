#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TMPDIR_TEST="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_TEST"' EXIT

pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; exit 1; }

setup_fixture() {
    local tmp="$1"
    mkdir -p "$tmp/commands/ci"
    cat > "$tmp/commands/ci/triage.md" <<'EOF'
---
name: triage
description: Classify a failing CI check
category: ci
---
EOF
    cat > "$tmp/commands/ci/watch.md" <<'EOF'
---
name: watch
description: Poll a run, route next action
category: ci
---
EOF
    cat > "$tmp/commands/ci/deprecated-old.md" <<'EOF'
---
name: deprecated-old
description: Old command
deprecated: true
category: ci
---
EOF
}

test_generates_rows() {
    local tmp="$TMPDIR_TEST/gen_test"
    setup_fixture "$tmp"
    output=$(bash "$ROOT/scripts/refcard-gen.sh" --root "$tmp" --category ci)
    if ! echo "$output" | grep -q "craft:ci:triage"; then
        fail "missing triage row"
    fi
    if ! echo "$output" | grep -q "craft:ci:watch"; then
        fail "missing watch row"
    fi
    if echo "$output" | grep -q "deprecated-old"; then
        fail "deprecated command should not appear in output"
    fi
    pass "generates correct rows, skips deprecated"
}

test_check_mode_unsupported() {
    # --check always exits 1 with a clear message: docs/REFCARD.md uses heading-based
    # sections, not generated sentinels. doc-coverage-check.sh handles parity checks.
    local tmp="$TMPDIR_TEST/check_unsupported_test"
    setup_fixture "$tmp"
    mkdir -p "$tmp/docs"
    cat > "$tmp/docs/REFCARD.md" <<'EOF'
# REFCARD
EOF
    exit_code=0
    output=$(bash "$ROOT/scripts/refcard-gen.sh" --root "$tmp" --check 2>&1) || exit_code=$?
    if [[ "$exit_code" -eq 0 ]]; then
        fail "--check should always exit 1 (sentinels not supported)"
    fi
    if ! echo "$output" | grep -q "not supported"; then
        fail "--check should print 'not supported' message, got: $output"
    fi
    pass "--check mode exits 1 with not-supported message"
}

test_skips_internal_commands() {
    local tmp="$TMPDIR_TEST/internal_test"
    mkdir -p "$tmp/commands/ci"
    cat > "$tmp/commands/ci/pub.md" <<'EOF'
---
name: pub
description: Public command
category: ci
---
EOF
    cat > "$tmp/commands/ci/internal-cmd.md" <<'EOF'
---
name: internal-cmd
description: Internal only
internal: true
category: ci
---
EOF
    output=$(bash "$ROOT/scripts/refcard-gen.sh" --root "$tmp" --category ci)
    if echo "$output" | grep -q "internal-cmd"; then
        fail "internal command should not appear in output"
    fi
    if ! echo "$output" | grep -q "craft:ci:pub"; then
        fail "public command should appear in output"
    fi
    pass "skips internal commands"
}

test_generates_rows
test_check_mode_unsupported
test_skips_internal_commands
echo "All refcard-gen tests passed."
