#!/usr/bin/env bash
# scripts/run-evals.sh - Safe wrapper around `claude plugin eval` for craft
#
# Owns the safety flags so humans and docs never call the raw command:
#   --no-publish (the eval publishes its report to claude.ai by default),
#   --max-cost-usd (every run bills your credential), --output-dir outside the tree.
#
# Usage:
#   ./scripts/run-evals.sh                       # smoke: 1 run per case
#   ./scripts/run-evals.sh --tier full           # 3 runs per case
#   ./scripts/run-evals.sh --case 'modes-*'      # filter cases by name glob
#   ./scripts/run-evals.sh --record              # also update evals/_coverage.json
#   ./scripts/run-evals.sh --dry-run             # print the command, run nothing
#
# Options: --tier smoke|full  --runs N  --case GLOB  --max-cost USD (default 5)
#          --output-dir DIR   --record  --trust  --dry-run
#   --trust passes --trust-plugin (skips the eval's first-run trust prompt; your call).
#
# Exit codes: 0 = ok, 1 = eval reported a failure, 2 = usage error / claude missing

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

TIER="smoke"
RUNS=""
CASE_GLOB=""
MAX_COST="5"
OUTPUT_DIR=""
RECORD=0
TRUST=0
DRY_RUN=0

usage() { sed -n '2,19p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }
die() { echo "run-evals: $*" >&2; exit 2; }

while [ $# -gt 0 ]; do
  case "$1" in
    --tier) TIER="${2:-}"; shift 2 ;;
    --runs) RUNS="${2:-}"; shift 2 ;;
    --case) CASE_GLOB="${2:-}"; shift 2 ;;
    --max-cost) MAX_COST="${2:-}"; shift 2 ;;
    --output-dir) OUTPUT_DIR="${2:-}"; shift 2 ;;
    --record) RECORD=1; shift ;;
    --trust) TRUST=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown option: $1 (see --help)" ;;
  esac
done

case "$TIER" in
  smoke) [ -n "$RUNS" ] || RUNS=1 ;;
  full)  [ -n "$RUNS" ] || RUNS=3 ;;
  *) die "--tier must be smoke or full" ;;
esac
case "$RUNS" in ''|*[!0-9]*|0) die "--runs must be a positive integer" ;; esac
case "$MAX_COST" in ''|*[!0-9.]*|.|*.*.*) die "--max-cost must be a number" ;; esac

[ -n "$OUTPUT_DIR" ] || OUTPUT_DIR="${TMPDIR:-/tmp}/craft-evals-$(date +%Y%m%d-%H%M%S)"
case "$OUTPUT_DIR" in
  "$PROJECT_ROOT"|"$PROJECT_ROOT"/*) die "--output-dir must be outside the repo (results are never committed)" ;;
esac

CMD=(claude plugin eval "$PROJECT_ROOT" --no-publish
     --runs "$RUNS" --max-cost-usd "$MAX_COST"
     --output-dir "$OUTPUT_DIR"
     --json "$OUTPUT_DIR/result.json" --report "$OUTPUT_DIR/report.html")
[ -z "$CASE_GLOB" ] || CMD+=(--case "$CASE_GLOB")
[ "$TRUST" -eq 0 ] || CMD+=(--trust-plugin)

if [ "$DRY_RUN" -eq 1 ]; then
  printf '%q ' "${CMD[@]}"; echo
  exit 0
fi

command -v claude >/dev/null 2>&1 || die "claude CLI not found on PATH"
mkdir -p "$OUTPUT_DIR"
"${CMD[@]}"
EVAL_RC=$?

# Record deltas only from a complete result; the eval exits 1 on a below-threshold
# score, which is still a valid result worth recording.
if [ "$RECORD" -eq 1 ]; then
  RESULT="$OUTPUT_DIR/result.json"
  COVERAGE="${CRAFT_EVALS_COVERAGE_FILE:-$PROJECT_ROOT/evals/_coverage.json}"
  if [ ! -f "$RESULT" ]; then
    echo "run-evals: no result.json, nothing recorded" >&2
  else
    python3 - "$RESULT" "$COVERAGE" <<'PY' || { echo "run-evals: record failed" >&2; exit 2; }
import json, os, sys, datetime
result, coverage = sys.argv[1], sys.argv[2]
d = json.load(open(result))
if d.get("partial"):
    print("run-evals: result is partial, nothing recorded", file=sys.stderr)
    sys.exit(0)
old = {}
if os.path.exists(coverage):
    old = {e["case"]: e for e in json.load(open(coverage)).get("cases", [])}
today = datetime.date.today().isoformat()
for c in d.get("cases", []):
    a = c.get("aggregates", {})
    entry = old.get(c["name"], {})
    entry.update({
        "case": c["name"],
        "skill": entry.get("skill"),
        "delta": a.get("delta"),
        "runs": len(c.get("arms", {}).get("with", [])),
        "claudeVersion": d.get("claudeVersion"),
        "date": today,
    })
    old[c["name"]] = entry
os.makedirs(os.path.dirname(coverage), exist_ok=True)
json.dump({"schemaVersion": 1, "cases": sorted(old.values(), key=lambda e: e["case"])},
          open(coverage, "w"), indent=2)
open(coverage, "a").write("\n")
print(f"run-evals: recorded {len(d.get('cases', []))} case(s) -> {coverage}")
PY
  fi
fi
exit "$EVAL_RC"
