# Tutorial: Quota Gate — Pre-Flight Token Check

By the end of this tutorial you will have:

- Read your cached rate-limit state before a long orchestration run
- Understood the SAFE / TIGHT / DEFER advisory
- Used the `--run-type` flag to size the estimate correctly

**Prerequisites:** craft v2.41+, at least one prior orchestrate or long LLM run (populates the cache).

---

## Step 1: Run the Quota Gate

Before starting a heavy orchestration, check your token budget:

```
/craft:quota
```

Expected output (SAFE example):

```
Quota Gate — Pre-Flight Check
─────────────────────────────
  Cached limit:  400 000 tokens / 5 h window
  Estimated cost: ~28 000 tokens (default orchestrate run)
  Remaining:     312 000 tokens

  Advisory: ✅ SAFE — proceed with orchestration
```

Expected output (TIGHT example):

```
  Advisory: ⚠️ TIGHT — estimated run consumes 68 % of remaining budget
             Consider a lighter mode or wait ~47 min for window reset
```

---

## Step 2: Size the Estimate for Your Run Type

The default estimate targets a standard `orchestrate` call. For a large fanout pass, use `--run-type`:

```
/craft:quota --run-type fanout
/craft:quota --run-type release
/craft:quota --run-type quick
```

Each run-type adjusts the token multiplier so the advisory reflects the actual job.

---

## Step 3: Get JSON Output for Scripting

```
/craft:quota --json
```

Returns a machine-readable object:

```json
{
  "advisory": "SAFE",
  "remaining_tokens": 312000,
  "estimated_cost": 28000,
  "window_reset_minutes": 187
}
```

Use this in CI or shell scripts to gate expensive runs automatically.

---

## What's Next

- Run `/craft:orchestrate` with confidence after a SAFE advisory
- If TIGHT or DEFER, switch to `/craft:orchestrate <task> quick` or wait for the window to reset
- See [release pipeline](TUTORIAL-release-pipeline.md) for how quota fits into a full release
