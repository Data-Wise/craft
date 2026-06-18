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

test_check_mode_fails_on_drift() {
    local tmp="$TMPDIR_TEST/check_test"
    setup_fixture "$tmp"
    mkdir -p "$tmp/docs"
    # REFCARD missing triage row
    cat > "$tmp/docs/REFCARD.md" <<'EOF'
<!-- REFCARD:GENERATED:START:ci -->
| `/craft:ci:watch` | ci | Poll a run, route next action |
<!-- REFCARD:GENERATED:END:ci -->
EOF
    exit_code=0
    bash "$ROOT/scripts/refcard-gen.sh" --root "$tmp" --check > /dev/null 2>&1 || exit_code=$?
    if [[ "$exit_code" -eq 0 ]]; then
        fail "--check should exit 1 when REFCARD is stale"
    fi
    pass "--check mode exits 1 on drift"
}

test_check_mode_passes_when_current() {
    local tmp="$TMPDIR_TEST/check_pass_test"
    setup_fixture "$tmp"
    mkdir -p "$tmp/docs"
    # Generate the expected output first, then put it in REFCARD
    generated=$(bash "$ROOT/scripts/refcard-gen.sh" --root "$tmp" --category ci)
    cat > "$tmp/docs/REFCARD.md" <<EOF
# REFCARD
$generated
EOF
    exit_code=0
    bash "$ROOT/scripts/refcard-gen.sh" --root "$tmp" --check > /dev/null 2>&1 || exit_code=$?
    if [[ "$exit_code" -ne 0 ]]; then
        fail "--check should exit 0 when REFCARD is current"
    fi
    pass "--check mode exits 0 when REFCARD is current"
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
test_check_mode_fails_on_drift
test_check_mode_passes_when_current
test_skips_internal_commands
echo "All refcard-gen tests passed."
