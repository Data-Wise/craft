#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Create temp directory for test files
TMPDIR_TEST="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_TEST" "$ROOT/commands/test"' EXIT

pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; exit 1; }

# --- Test: command-audit.sh accepts internal: true ---
test_audit_accepts_internal_field() {
    # Create test command file in a temporary directory first
    local cmd_dir="$TMPDIR_TEST/commands/test"
    mkdir -p "$cmd_dir"
    local cmd_file="$cmd_dir/internal-cmd.md"

    cat > "$cmd_file" <<'EOF'
---
name: test-internal
description: An internal command
category: test
internal: true
---
# /craft:test:internal-cmd
EOF

    # Copy to real commands tree so audit can scan it
    mkdir -p "$ROOT/commands/test"
    cp "$cmd_file" "$ROOT/commands/test/internal-cmd.md"

    # Run audit and capture output
    output=$(cd "$ROOT" && bash scripts/command-audit.sh 2>&1 || true)

    # Check if the audit flagged 'internal' as an invalid field
    if echo "$output" | grep -q "commands/test/internal-cmd.md: invalid field 'internal'"; then
        fail "command-audit.sh flagged 'internal' as invalid field"
    fi
    pass "command-audit.sh accepts internal: true"
}

test_audit_accepts_internal_field
echo "All Task 1 tests passed."
