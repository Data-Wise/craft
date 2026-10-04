#!/usr/bin/env bash
#
# Tests for scripts/run-evals.sh (safety flags, validation, --record). Uses a stub
# `claude` on PATH, so no real eval runs and nothing is billed.
#
# Usage: ./tests/test_run_evals_wrapper.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WRAPPER="$PROJECT_ROOT/scripts/run-evals.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PASS=0
FAIL=0
ok()   { PASS=$((PASS + 1)); echo "  ok   $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  FAIL $1"; }
has()  { case "$2" in *"$1"*) return 0 ;; *) return 1 ;; esac; }

check_has()    { if has "$2" "$3"; then ok "$1"; else fail "$1 (missing: $2)"; fi; }
check_lacks()  { if has "$2" "$3"; then fail "$1 (unexpected: $2)"; else ok "$1"; fi; }
check_rc()     { if [ "$2" -eq "$3" ]; then ok "$1"; else fail "$1 (rc=$3, want $2)"; fi; }

echo "dry-run safety flags"
OUT=$("$WRAPPER" --dry-run); RC=$?
check_rc "dry-run exits 0" 0 "$RC"
check_has "always --no-publish" "--no-publish" "$OUT"
check_has "default cost cap 5" "--max-cost-usd 5" "$OUT"
check_has "smoke = 1 run" "--runs 1" "$OUT"
check_lacks "no --trust-plugin by default" "--trust-plugin" "$OUT"

OUT=$("$WRAPPER" --dry-run --tier full --case 'modes-*' --trust --max-cost 2.5)
check_has "full = 3 runs" "--runs 3" "$OUT"
check_has "case filter passed" "--case modes-" "$OUT"
check_has "--trust adds --trust-plugin" "--trust-plugin" "$OUT"
check_has "custom cost cap" "--max-cost-usd 2.5" "$OUT"
check_has "--no-publish still present with every flag" "--no-publish" "$OUT"

echo "validation"
"$WRAPPER" --dry-run --runs 0 >/dev/null 2>&1; check_rc "runs=0 rejected" 2 $?
"$WRAPPER" --dry-run --runs x >/dev/null 2>&1; check_rc "runs=x rejected" 2 $?
"$WRAPPER" --dry-run --tier bogus >/dev/null 2>&1; check_rc "bad tier rejected" 2 $?
"$WRAPPER" --dry-run --max-cost 1.2.3 >/dev/null 2>&1; check_rc "bad cost rejected" 2 $?
"$WRAPPER" --bogus >/dev/null 2>&1; check_rc "unknown flag rejected" 2 $?
"$WRAPPER" --dry-run --output-dir "$PROJECT_ROOT/evals/results" >/dev/null 2>&1
check_rc "in-repo output dir rejected" 2 $?

echo "claude missing"
(PATH="/usr/bin:/bin"; command -v claude >/dev/null 2>&1 && exit 99; "$WRAPPER" --output-dir "$TMP/none" >/dev/null 2>&1)
RC=$?; if [ "$RC" -eq 99 ]; then ok "skipped (claude on minimal PATH)"; else check_rc "missing claude exits 2" 2 "$RC"; fi

echo "record (stub claude)"
mkdir -p "$TMP/bin"
cat > "$TMP/bin/claude" <<'STUB'
#!/usr/bin/env bash
# Stub: find --json <path> and write a fixed result; exit 1 like a below-threshold run.
while [ $# -gt 0 ]; do [ "$1" = "--json" ] && J="$2"; shift; done
cat > "$J" <<JSON
{"schemaVersion":1,"claudeVersion":"stub-1","partial":${STUB_PARTIAL:-false},
 "cases":[{"name":"demo-case","arms":{"with":[{"score":1}]},"aggregates":{"delta":1}}]}
JSON
exit 1
STUB
chmod +x "$TMP/bin/claude"
COV="$TMP/cov/_coverage.json"
printf '{"schemaVersion":1,"cases":[{"case":"demo-case","skill":"demo-skill","delta":0}]}\n' > /dev/null
mkdir -p "$TMP/cov"; printf '{"schemaVersion":1,"cases":[{"case":"demo-case","skill":"demo-skill","delta":0}]}\n' > "$COV"

PATH="$TMP/bin:$PATH" CRAFT_EVALS_COVERAGE_FILE="$COV" "$WRAPPER" --record --output-dir "$TMP/out1" >/dev/null 2>&1
check_rc "eval failure rc passed through" 1 $?
J=$(cat "$COV")
check_has "delta recorded" '"delta": 1' "$J"
check_has "existing skill mapping preserved" '"skill": "demo-skill"' "$J"
check_has "claude version recorded" '"claudeVersion": "stub-1"' "$J"

printf '{"schemaVersion":1,"cases":[{"case":"demo-case","skill":"demo-skill","delta":0}]}\n' > "$COV"
PATH="$TMP/bin:$PATH" STUB_PARTIAL=true CRAFT_EVALS_COVERAGE_FILE="$COV" "$WRAPPER" --record --output-dir "$TMP/out2" >/dev/null 2>&1
J=$(cat "$COV")
check_has "partial result not recorded (delta unchanged)" '"delta":0' "$J"

echo
echo "passed=$PASS failed=$FAIL"
[ "$FAIL" -eq 0 ]
