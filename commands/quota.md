---
description: Pre-flight quota check — reads cached rate_limits, estimates cost-weighted tokens for the planned run, maps to SAFE/TIGHT/DEFER
category: orchestrate
arguments:
  - name: run-type
    description: "Engine type to estimate: workflow or fanout (default: workflow)"
    required: false
    default: workflow
  - name: json
    description: Output as JSON instead of human-readable
    required: false
    default: false
related_commands: orchestrate, check
tags: quota, tokens, pre-flight
---

# /craft:quota -- Pre-Flight Quota Check

Reads cached rate_limits, estimates cost-weighted tokens for the planned run, and maps to a SAFE / TIGHT / DEFER advisory before committing to an orchestrated run.

## Usage

```bash
/craft:quota                    # Check quota for workflow engine (default)
/craft:quota fanout             # Check quota for fanout engine
/craft:quota --json             # Machine-readable JSON output
/craft:quota fanout --json      # Fanout estimate as JSON
```

## Execution Behavior (MANDATORY)

When this command runs, Claude MUST follow these steps in order. Do NOT skip any step.

### Step 1: Load and Validate Quota Cache

Read `~/.claude/quota-cache.json`.

If the file is absent:

```
quota cache absent -- run scripts/quota-persist.sh first
```

STOP. Do not proceed.

If `captured_at` is more than `STALE_SECS=900` seconds ago, compute age in minutes and print:

```
quota cache stale (Nm old) -- run scripts/quota-persist.sh to refresh
```

STOP. Do not proceed.

Extract from cache:

- `five_hour_pct` — percentage of 5-hour rolling window consumed
- `reset_at` — ISO timestamp when the window resets (for DEFER output)
- `captured_at` — ISO timestamp of last cache write

### Step 2: Load Estimation History

Run `python3 scripts/quota_estimate.py` with marker files for the requested engine type:

- `workflow`: `.craft/workflow-runs/*/manifest.json`
- `fanout`: `.craft/orchestrate-runs/*.json`

The script returns:

```json
{ "n": 12, "median": 45200, "p05": 18000, "p95": 112000, "cold_start": false }
```

If `cold_start` is true (`n < 3`), label the estimate as **insufficient history** and note that the median/percentiles are unreliable. Proceed with the advisory using whatever data is available.

### Step 3: Map to Advisory

Using `five_hour_pct` from the cache:

| Range | Advisory | Action |
|-------|----------|--------|
| < 60 | **SAFE** | Proceed — ample quota headroom |
| 60–85 | **TIGHT** | Proceed with caution — monitor usage |
| > 85 | **DEFER** | Do not start — show reset time |

For DEFER, compute and display the reset time from `reset_at`.

### Step 4: Write Output and Display

Write `.craft/quota.json`:

```json
{
  "advisory": "SAFE",
  "five_hour_pct": 42.1,
  "estimate": {
    "n": 12,
    "median": 45200,
    "p05": 18000,
    "p95": 112000,
    "cold_start": false
  },
  "captured_at": "<from cache>",
  "generated_at": "<now ISO>"
}
```

**Human-readable output (default):**

```
Quota Pre-Flight Check
  Engine:        workflow
  Cache age:     4m (fresh)
  5-hour usage:  42.1%

  Advisory:      SAFE
  Estimate:      ~45,200 tokens (n=12 runs, p05=18k p95=112k)

  Proceed: quota headroom is sufficient.
```

For TIGHT:

```
  Advisory:      TIGHT
  Resets at:     14:32 UTC (23m)
  Consider deferring if the run is > 80k tokens.
```

For DEFER:

```
  Advisory:      DEFER
  5-hour usage:  88.3%
  Resets at:     14:32 UTC (23m)
  Wait for reset or reduce run scope before proceeding.
```

For cold-start (insufficient history):

```
  Advisory:      SAFE  (cold start -- n=1, estimate unreliable)
  Estimate:      ~45,200 tokens (UNRELIABLE: need n>=3 runs)
```

**JSON output (`--json`):**

Print the `.craft/quota.json` content to stdout and nothing else.

## See Also

- `scripts/quota-persist.sh` — refresh the quota cache from the Claude API statusline
- `scripts/quota_estimate.py` — token estimation from run history marker files
- `/craft:check` — general pre-flight validation
- `/craft:orchestrate` — workflow engine that consumes quota
