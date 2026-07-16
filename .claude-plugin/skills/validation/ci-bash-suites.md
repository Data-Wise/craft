---
name: check:ci-bash-suites
description: Run the bash test suites CI runs but the language test runner does not collect
category: validation
context: fork
hot_reload: true
version: 1.0.0
---

# CI Bash-Suite Parity Validation

Runs the shell test suites that this repo's CI workflows invoke directly — the ones a language
test runner (`pytest`, `jest`, `go test`) never collects, and therefore never reports on.

## Why This Exists

A green test run only covers what the runner collects. When CI invokes suites *outside* that
runner, the local gate and CI measure different things — and the local one reports a comfortable
green for a surface it never touched.

This is not hypothetical. In craft's v4 folio-split (2026-07-16), task T3.5.2 deleted
`commands/git/` and cited **"full pytest 2575 passed"** as its verification evidence. That was
true and irrelevant: `tests/test_git_shim_correctness.sh` — a **CI-required** check — asserted
those exact files still existed. It had been red for days. pytest does not run it, so nothing
local ever said so. The regression surfaced only when CI rejected the PR.

The general failure is **gate divergence**: *CI runs checks the local gate doesn't.* This
validator closes it by deriving what to run from the workflows themselves, so it cannot drift
out of sync the way a hardcoded list would.

## What It Runs

Parses `.github/workflows/*.yml` for direct shell-suite invocations (`bash <path>` /
`sh <path>`) whose path lives under a test directory, then runs exactly those — no more, no
less. Deriving the list from CI is the whole point:

- **Not every `*.sh` in `tests/`.** craft has 22; CI runs 6. Running all 22 would invent a gate
  CI never asked for and fail on suites that are deliberately manual.
- **Not a hardcoded list.** That is the drift this validator exists to prevent. Add a suite to
  a workflow and it is picked up on the next run, with no edit here.
- **Only test-directory paths.** Workflows also invoke non-test scripts
  (`scripts/docs-staleness-check.sh`, `scripts/aggregator-sync.sh`); those are build/deploy
  steps or have their own validators, not test suites.

## Modes

Follows the release-gated validator contract (same as `version-check`, `skill-standards`):
validators receive their tier **only** via `CRAFT_MODE`.

| `CRAFT_MODE` | Behavior on a failing suite |
|---|---|
| `default` (also `--for commit` / `--for pr`) | **Advisory** — reports the failure loudly, exits 0 |
| `release` (also `--for deploy`) | **Blocking** — exits 1 |

Advisory-in-default is deliberate, and it is enough to have caught the T3.5.2 case: the failure
becomes *visible* at check time instead of surfacing when CI rejects the PR. `CRAFT_MODE` cannot
distinguish `--for pr` from `--for commit` (both resolve to `default`), so blocking at that tier
would block every commit on a multi-minute run.

**Runtime:** these suites are slow by nature (craft's take ~3–5 min combined). That is inherent
to what they test — self-contained temp repos and real git operations.

## Environment

`SKIP_PERF` defaults to `1`, matching what CI exports for perf-sensitive suites (wall-clock
timing budgets are runner-sensitive and are not behavioral guards). Override with `SKIP_PERF=0`
to include them.

## Implementation

```bash
#!/bin/bash
set -uo pipefail

MODE="${CRAFT_MODE:-default}"
# Match CI: perf/timing tests are runner-sensitive, not behavioral guards.
export SKIP_PERF="${SKIP_PERF:-1}"

WORKFLOW_DIR=".github/workflows"

if [ ! -d "$WORKFLOW_DIR" ]; then
    echo "⚠️  SKIP: no $WORKFLOW_DIR — nothing to derive a suite list from"
    exit 0
fi

# Derive the suite list FROM the workflows: direct `bash <path>` / `sh <path>`
# invocations whose path sits under a test directory. Deliberately excludes
# non-test scripts (docs-staleness-check.sh, aggregator-sync.sh) — those are
# build steps or have their own validators.
SUITES=$(grep -rhoE '(bash|sh)[[:space:]]+[^[:space:]]*tests?/[^[:space:]]+\.sh' \
             "$WORKFLOW_DIR"/*.yml 2>/dev/null \
         | awk '{print $2}' \
         | sort -u)

if [ -z "$SUITES" ]; then
    echo "✅ PASS: no CI-invoked bash test suites found (nothing to check)"
    exit 0
fi

TOTAL=0
PASSED=0
FAILED=0
MISSING=0
declare -a FAILED_NAMES=()

for suite in $SUITES; do
    TOTAL=$((TOTAL + 1))

    if [ ! -f "$suite" ]; then
        # A workflow references a suite that does not exist. CI would hard-fail
        # here, so surface it rather than silently skipping.
        echo "  ❌ $suite — referenced by a workflow but not found on disk"
        MISSING=$((MISSING + 1))
        FAILED=$((FAILED + 1))
        FAILED_NAMES+=("$suite (missing)")
        continue
    fi

    if bash "$suite" >/dev/null 2>&1; then
        echo "  ✅ $suite"
        PASSED=$((PASSED + 1))
    else
        echo "  ❌ $suite (exit $?)"
        FAILED=$((FAILED + 1))
        FAILED_NAMES+=("$suite")
    fi
done

echo ""

if [ "$FAILED" -eq 0 ]; then
    echo "✅ PASS: $PASSED/$TOTAL CI bash suites green (${MODE} mode)"
    exit 0
fi

echo "Failed:"
for n in "${FAILED_NAMES[@]}"; do
    echo "  - $n"
done
echo ""
echo "These suites run in CI but are NOT collected by the language test runner —"
echo "a green pytest/jest run says nothing about them. Re-run one directly to see"
echo "its output, e.g.:  bash ${FAILED_NAMES[0]%% *}"

if [ "$MISSING" -gt 0 ]; then
    echo ""
    echo "Note: $MISSING suite(s) are referenced by a workflow but absent from disk."
    echo "Either restore them or drop the invocation from the workflow — CI will"
    echo "hard-fail on this."
fi

if [ "$MODE" = "release" ]; then
    echo ""
    echo "❌ FAIL: $FAILED/$TOTAL CI bash suites failing (release mode — blocking)"
    exit 1
else
    echo ""
    echo "⚠️  WARN: $FAILED/$TOTAL CI bash suites failing (${MODE} mode — advisory)"
    echo "    CI will reject this. Fix before opening a PR."
    exit 0
fi
```

## Output Format

```
  ✅ tests/test_branch_guard.sh
  ✅ tests/test_bump_version.sh
  ❌ tests/test_git_shim_correctness.sh (exit 1)

Failed:
  - tests/test_git_shim_correctness.sh

These suites run in CI but are NOT collected by the language test runner —
a green pytest/jest run says nothing about them.

⚠️  WARN: 1/6 CI bash suites failing (default mode — advisory)
    CI will reject this. Fix before opening a PR.
```

## Hot-Reload Behavior

Detected and loaded automatically when `/craft:check` runs:

1. No restart required when this file is added/modified
2. Changes take effect on the next `/craft:check` execution
3. The suite list needs no maintenance — it is re-derived from the workflows each run

## See Also

- `/craft:test` — run the language test suite
- `/craft:check --for release` — blocking tier for this validator
- `.claude-plugin/skills/validation/test-coverage.md` — the language-runner counterpart
