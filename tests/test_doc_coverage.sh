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

# --- Task 2 Tests: doc-coverage-check.sh ---

# --- Test: detects missing REFCARD row ---
test_detects_missing_refcard() {
    local tmp="$TMPDIR_TEST/refcard_test"
    mkdir -p "$tmp/commands/ci"
    mkdir -p "$tmp/docs"

    # Command with no REFCARD entry
    cat > "$tmp/commands/ci/newcmd.md" <<'EOF'
---
name: newcmd
description: A new command
category: ci
---
# /craft:ci:newcmd
EOF
    # Empty REFCARD
    echo "# REFCARD" > "$tmp/docs/REFCARD.md"
    # Nav has the entry so only REFCARD fails
    cat > "$tmp/mkdocs.yml" <<'EOF'
nav:
  - /craft:ci:newcmd: commands/ci/newcmd.md
EOF

    output=$(bash "$ROOT/scripts/doc-coverage-check.sh" --root "$tmp" 2>&1 || true)

    if ! echo "$output" | grep -q "REFCARD"; then
        fail "did not detect missing REFCARD row"
    fi
    pass "detects missing REFCARD row"
}

# --- Test: detects missing nav entry ---
test_detects_missing_nav() {
    local tmp="$TMPDIR_TEST/nav_test"
    mkdir -p "$tmp/commands/ci"
    mkdir -p "$tmp/docs"

    cat > "$tmp/commands/ci/newcmd.md" <<'EOF'
---
name: newcmd
description: A new command
category: ci
---
EOF
    # REFCARD has entry, nav does not
    printf "| \`/craft:ci:newcmd\` | ci | A new command |\n" > "$tmp/docs/REFCARD.md"
    echo "nav:" > "$tmp/mkdocs.yml"

    output=$(bash "$ROOT/scripts/doc-coverage-check.sh" --root "$tmp" 2>&1 || true)
    if ! echo "$output" | grep -q "nav"; then
        fail "did not detect missing nav entry"
    fi
    pass "detects missing mkdocs nav entry"
}

# --- Test: skips deprecated commands ---
test_skips_deprecated() {
    local tmp="$TMPDIR_TEST/deprecated_test"
    mkdir -p "$tmp/commands/ci"
    mkdir -p "$tmp/docs"
    echo "nav:" > "$tmp/mkdocs.yml"
    echo "# REFCARD" > "$tmp/docs/REFCARD.md"

    cat > "$tmp/commands/ci/oldcmd.md" <<'EOF'
---
name: oldcmd
description: Old command
deprecated: true
replaced-by: newcmd
---
EOF
    exit_code=0
    bash "$ROOT/scripts/doc-coverage-check.sh" --root "$tmp" > /dev/null 2>&1 || exit_code=$?
    if [[ "$exit_code" -ne 0 ]]; then
        fail "deprecated command should not cause non-zero exit"
    fi
    pass "skips deprecated commands"
}

# --- Test: skips internal commands ---
test_skips_internal() {
    local tmp="$TMPDIR_TEST/internal_test"
    mkdir -p "$tmp/commands/ci"
    mkdir -p "$tmp/docs"
    echo "nav:" > "$tmp/mkdocs.yml"
    echo "# REFCARD" > "$tmp/docs/REFCARD.md"

    cat > "$tmp/commands/ci/internalcmd.md" <<'EOF'
---
name: internalcmd
description: Internal only
internal: true
---
EOF
    exit_code=0
    bash "$ROOT/scripts/doc-coverage-check.sh" --root "$tmp" > /dev/null 2>&1 || exit_code=$?
    if [[ "$exit_code" -ne 0 ]]; then
        fail "internal command should not cause non-zero exit"
    fi
    pass "skips internal commands"
}

test_detects_missing_refcard
test_detects_missing_nav
test_skips_deprecated
test_skips_internal

echo "All Task 1 and Task 2 tests passed."

# --- Task 3: refcard-gen.sh ---
bash "$SCRIPT_DIR/test_refcard_gen.sh"

# --- Task 4: Phase 8 integration ---
test_phase8_catches_refcard_gap() {
    # Use the real staleness check — it calls doc-coverage-check.sh internally
    # Create a minimal fixture via tmp command file that we can add temporarily
    local tmp_cmd="$ROOT/commands/ci/_test_coverage_gap_$$.md"
    cat > "$tmp_cmd" <<'EOF'
---
name: _test_coverage_gap
description: Temp test command
category: ci
---
EOF
    # Run staleness check JSON mode and check Phase 8 findings
    output=$(bash "$ROOT/scripts/docs-staleness-check.sh" --json 2>/dev/null || true)
    rm -f "$tmp_cmd"
    if ! echo "$output" | grep -q "refcard\|REFCARD\|nav"; then
        fail "Phase 8 did not report REFCARD/nav gap for new command"
    fi
    pass "Phase 8 detects REFCARD/nav gap for undocumented command"
}

test_phase8_catches_refcard_gap

# --- Task 5: pre-release-check.sh blocks on missing doc surfaces ---
test_prerelease_blocks_on_doc_gap() {
    # Temporarily add an undocumented command
    local tmp_cmd="$ROOT/commands/ci/_prerelease_gap_$$.md"
    cat > "$tmp_cmd" <<'EOF'
---
name: _prerelease_gap
description: Temp undocumented command
category: ci
---
EOF
    local version
    version=$(grep '"version"' "$ROOT/plugin.json" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    exit_code=0
    bash "$ROOT/scripts/pre-release-check.sh" "$version" > /dev/null 2>&1 || exit_code=$?
    rm -f "$tmp_cmd"
    if [[ "$exit_code" -eq 0 ]]; then
        fail "pre-release-check.sh should exit 1 when commands have missing doc surfaces"
    fi
    pass "pre-release-check.sh blocks on missing doc surfaces"
}

test_prerelease_blocks_on_doc_gap
