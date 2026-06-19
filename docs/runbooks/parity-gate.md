# Parity Gate — Token-Efficiency Measurement Protocol

## Purpose

Before flipping `/craft:orchestrate` to default `--engine=workflow`, run a paired
measurement to confirm the cost-weighted token reduction is real and materially large
(>15% floor). Decision is interval-based, not significance-based.

---

## Prerequisites

- Tasks 7, 9, 10, 11 merged to `dev`
- `scripts/orchestrate-token-report.py` available on PATH
- A **reference task**: one representative SPEC/ORCHESTRATE file used for both engines
  in every pair (keeps the task constant across runs)

---

## Protocol: N=5 Paired Runs

Run each pair back-to-back on the same reference task. Cold-cache both engines.

For each pair `i` (i = 1 … 5):

1. **Fanout run** — fresh session (cold cache):

   ```bash
   /craft:orchestrate --engine=fanout   # or current default
   # capture the session marker printed at end of run
   MARKER_F=$(...)
   python3 scripts/orchestrate-token-report.py "$MARKER_F" --json > pair_${i}_fanout.json
   ```

2. **Workflow run** — fresh session (cold cache):

   ```bash
   /craft:orchestrate --engine=workflow
   MARKER_W=$(...)
   python3 scripts/orchestrate-token-report.py "$MARKER_W" --json > pair_${i}_workflow.json
   ```

3. Record both JSON outputs to `.craft/parity-gate-results/pair_${i}/`.

> **Cold-cache discipline**: close and reopen the Claude Code session between runs so
> prompt-cache hits from the previous run do not carry over. Verify `cache_read` tokens
> are near zero at the start of each fanout run.

---

## Metric: Cost-Weighted Tokens

```
cost_weighted = input_tokens * 1.0
              + output_tokens * 5.0
              + cache_creation_tokens * 1.25
              + cache_read_tokens * 0.1
```

Extract from each JSON:

```python
def cost_weighted(r):
    return (r["input_tokens"] * 1.0
          + r["output_tokens"] * 5.0
          + r["cache_creation_tokens"] * 1.25
          + r["cache_read_tokens"] * 0.1)
```

---

## Analysis

### Per-pair reduction

```
d_i = (fanout_i - workflow_i) / fanout_i * 100   [% reduction]
```

### Summary statistics (df = 4)

| Statistic | Formula |
|---|---|
| Mean reduction | `mean_d = sum(d_i) / 5` |
| Std deviation | `s = sqrt(sum((d_i - mean_d)^2) / 4)` |
| 95% CI | `mean_d ± 2.776 * s / sqrt(5)` |
| Cohen's d_n | `mean_d / s` (paired, normalized to within-pair SD) |
| Surprisal | `S = -log2(p)` where p is from t(df=4) — report as graded evidence, not a threshold |

**Surprisal interpretation guide** (do not apply a binary cutoff):

| S value | Rough interpretation |
|---|---|
| S < 2 | Weak evidence; consistent with noise |
| 2 ≤ S < 4 | Moderate evidence of a real effect |
| 4 ≤ S < 6 | Substantial evidence |
| S ≥ 6 | Strong evidence |

> Do **not** report "statistically significant." Report the measured effect size,
> CI bounds, and S-value together. A large S with a CI that barely clears 15%
> warrants a different read than a large S with a CI lower bound near 30%.

---

## Decision Rule

### FLIP (set `--engine=workflow` as default) if ALL three hold

1. **95% CI lower bound > 15%** — the minimum plausible reduction clears the materiality floor
2. **Behavior parity holds** — output quality spot-checked on ≥3 pairs (same task completion, no
   new failure modes observed)
3. **No new failure modes** — workflow engine does not error or degrade on edge tasks in
   the reference suite

### NO-FLIP (keep `--engine=workflow` as opt-in) if ANY of

- 95% CI lower bound ≤ 15%
- Parity failure on any pair
- New failure modes observed

**Record the measured effect regardless of the decision.** A NO-FLIP with a CI of
[12%, 22%] is informative and should be logged — it signals Lever C gains may push
the lower bound above 15% in a future gate.

---

## Post-Decision Actions

### If FLIP

- Update routing rule in `commands/orchestrate.md` (change `--engine=fanout` default
  to `--engine=workflow`)
- Update `CHANGELOG.md` with the measured effect:

  ```markdown
  ### Changed
  - `orchestrate`: default engine flipped to `workflow` after N=5 parity gate;
    measured cost-weighted token reduction: MEAN_D% (95% CI [LB%, UB%],
    Cohen's d_n=D, S=S_VALUE)
  ```

### If NO-FLIP

- Update `CHANGELOG.md` noting the gate result and why the flip was deferred:

  ```markdown
  ### Notes
  - `orchestrate`: parity gate ran N=5; 95% CI lower bound BELOW 15% floor
    (measured: MEAN_D%, CI [LB%, UB%]). Workflow remains opt-in.
    Revisit after Lever C gains measured.
  ```

- Keep `--engine=workflow` as opt-in; do not change routing defaults

---

## Records

Store per-pair JSON files and the analysis notebook/script in:

```
.craft/parity-gate-results/
  pair_1/
    fanout.json
    workflow.json
  pair_2/ ...
  ...
  pair_5/
  analysis.py        # or analysis.ipynb
  summary.json       # mean_d, CI, cohen_d, surprisal, decision
```

`.craft/parity-gate-results/` is gitignored (raw telemetry). The `summary.json`
**is** committed alongside the CHANGELOG entry when the decision is recorded.

---

## Quick Reference

```bash
# Run the full analysis after collecting 5 pairs
python3 scripts/orchestrate-token-report.py --parity-gate \
    .craft/parity-gate-results/pair_{1..5}/fanout.json \
    .craft/parity-gate-results/pair_{1..5}/workflow.json \
    --floor 15 --out .craft/parity-gate-results/summary.json
```

Decision output example:

```json
{
  "mean_reduction_pct": 23.4,
  "ci_95": [17.1, 29.7],
  "cohens_d_n": 2.1,
  "surprisal_bits": 5.8,
  "floor_pct": 15,
  "ci_lower_clears_floor": true,
  "parity_ok": true,
  "decision": "FLIP"
}
```
