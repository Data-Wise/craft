"""Read-only orchestrate token report. Reads session JSONL; never writes ~/.claude."""
WEIGHTS = {"input_tokens": 1.0, "output_tokens": 5.0,
           "cache_creation_input_tokens": 1.25, "cache_read_input_tokens": 0.1}

def cost_weighted(usage, weights=WEIGHTS):
    return float(sum(weights.get(k, 0.0) * usage.get(k, 0) for k in weights))

import json

def iter_usages(jsonl_path, start_ts, end_ts):
    out = []
    with open(jsonl_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("type") != "assistant":
                continue
            ts = rec.get("timestamp")
            if start_ts and ts and ts < start_ts:
                continue
            if end_ts and ts and ts > end_ts:
                continue
            usage = rec.get("message", {}).get("usage")
            if usage:
                out.append(usage)
    return out

import re

def transcript_dir(cwd, home):
    slug = re.sub(r"[/.]", "-", cwd)
    return f"{home}/.claude/projects/{slug}"

def load_marker(path):
    with open(path) as f:
        return json.load(f)

import glob, os

def per_agent(transcript_dir, start_ts, end_ts):
    result = {}
    for path in glob.glob(os.path.join(transcript_dir, "agent-*.jsonl")):
        agent_id = os.path.basename(path)[len("agent-"):-len(".jsonl")]
        result[agent_id] = aggregate(iter_usages(path, start_ts, end_ts))
    return result

def aggregate(usages):
    keys = ["input_tokens", "output_tokens",
            "cache_creation_input_tokens", "cache_read_input_tokens"]
    raw = {k: sum(u.get(k, 0) for u in usages) for k in keys}
    denom = raw["input_tokens"] + raw["cache_read_input_tokens"]
    ratio = raw["cache_read_input_tokens"] / denom if denom else 0.0
    return {"raw": raw,
            "cost_weighted": sum(cost_weighted(u) for u in usages),
            "cache_hit_ratio": ratio}

import argparse, math, sys

def build_report(marker_path, home):
    m = load_marker(marker_path)
    tdir = transcript_dir(m["cwd"], home)
    session = sorted(glob.glob(os.path.join(tdir, "*.jsonl")))
    session = [p for p in session if not os.path.basename(p).startswith("agent-")]
    run_usages = []
    for p in session:
        run_usages += iter_usages(p, m.get("start_ts"), m.get("end_ts"))
    return {"marker": m,
            "run": aggregate(run_usages),
            "agents": per_agent(tdir, m.get("start_ts"), m.get("end_ts"))}

def diff_reports(a, b):
    aw, bw = a["run"]["cost_weighted"], b["run"]["cost_weighted"]
    return {"pct_reduction": (aw - bw) / aw * 100.0 if aw else 0.0}

# ---------------------------------------------------------------------------
# Parity-gate analysis (N=5 paired runs, df=4)
# ---------------------------------------------------------------------------

_T_TABLE_DF4 = [  # (t_abs, two_tailed_p) — linear interpolation
    (0.0, 1.0), (0.5, 0.64), (1.0, 0.37), (1.5, 0.21), (2.0, 0.116),
    (2.132, 0.10), (2.5, 0.067), (2.776, 0.05), (3.0, 0.040),
    (3.5, 0.025), (4.0, 0.016), (4.604, 0.010), (5.0, 0.007),
    (7.0, 0.002), (10.0, 0.0005),
]

def _t_pvalue_df4(t_abs):
    """Two-tailed p-value for df=4 via linear interpolation."""
    for i in range(len(_T_TABLE_DF4) - 1):
        t0, p0 = _T_TABLE_DF4[i]
        t1, p1 = _T_TABLE_DF4[i + 1]
        if t0 <= t_abs <= t1:
            frac = (t_abs - t0) / (t1 - t0)
            return max(1e-9, p0 + frac * (p1 - p0))
    return 1e-9

def parity_gate_analysis(reports, floor_pct):
    """Compute paired statistics from a list of (fanout_report, workflow_report) tuples."""
    fanout_cws = [r["run"]["cost_weighted"] for r, _ in reports]
    workflow_cws = [r["run"]["cost_weighted"] for _, r in reports]
    n = len(reports)
    ds = [(f - w) / f * 100.0 if f else 0.0
          for f, w in zip(fanout_cws, workflow_cws)]
    mean_d = sum(ds) / n
    s = (sum((d - mean_d) ** 2 for d in ds) / (n - 1)) ** 0.5 if n > 1 else 0.0
    se = s / n ** 0.5
    t_crit = 2.776  # df=4, 95% two-tailed (exact)
    ci_lb = mean_d - t_crit * se
    ci_ub = mean_d + t_crit * se
    cohens_d = mean_d / s if s else float("inf")
    t_stat = mean_d / se if se else float("inf")
    p = _t_pvalue_df4(abs(t_stat))
    surprisal = -math.log2(p) if p > 0 else float("inf")
    pairs = [{"pair": i + 1, "fanout_cw": f, "workflow_cw": w, "d_pct": d}
             for i, (f, w, d) in enumerate(zip(fanout_cws, workflow_cws, ds))]
    return {
        "n": n,
        "pairs": pairs,
        "mean_reduction_pct": round(mean_d, 2),
        "std_d": round(s, 2),
        "ci_95": [round(ci_lb, 2), round(ci_ub, 2)],
        "cohens_d_n": round(cohens_d, 3),
        "t_stat": round(t_stat, 3),
        "p_two_tailed": round(p, 5),
        "surprisal_bits": round(surprisal, 2),
        "floor_pct": floor_pct,
        "ci_lower_clears_floor": ci_lb > floor_pct,
        "decision": "FLIP" if ci_lb > floor_pct else "NO-FLIP",
    }

def run_parity_gate(files, floor_pct, out_path, home):
    """Load per-pair JSON files, separate by engine, pair by start_ts order, analyse."""
    loaded = []
    for f in files:
        try:
            with open(f) as fh:
                loaded.append((f, json.load(fh)))
        except Exception as e:
            print(f"WARNING: could not read {f}: {e}", file=sys.stderr)

    fanout = sorted(
        [(p, r) for p, r in loaded if r.get("marker", {}).get("engine") == "fanout"],
        key=lambda x: x[1].get("marker", {}).get("start_ts", ""),
    )
    workflow = sorted(
        [(p, r) for p, r in loaded if r.get("marker", {}).get("engine") == "workflow"],
        key=lambda x: x[1].get("marker", {}).get("start_ts", ""),
    )

    if len(fanout) != len(workflow):
        print(f"ERROR: {len(fanout)} fanout reports vs {len(workflow)} workflow reports — must match.",
              file=sys.stderr)
        return 1
    if not fanout:
        print("ERROR: no reports found (check that each JSON has marker.engine set).",
              file=sys.stderr)
        return 1

    pairs = list(zip([r for _, r in fanout], [r for _, r in workflow]))
    result = parity_gate_analysis(pairs, floor_pct)

    print(f"\nParity Gate — N={result['n']} paired runs")
    print(f"  mean reduction:  {result['mean_reduction_pct']:.1f}%")
    print(f"  95% CI:          [{result['ci_95'][0]:.1f}%, {result['ci_95'][1]:.1f}%]")
    print(f"  Cohen's d_n:     {result['cohens_d_n']:.2f}")
    print(f"  Surprisal S:     {result['surprisal_bits']:.1f} bits")
    print(f"  floor:           {floor_pct}%  |  CI lower clears: {result['ci_lower_clears_floor']}")
    print(f"\n  DECISION: {result['decision']}\n")

    for p in result["pairs"]:
        print(f"  pair {p['pair']}: fanout={p['fanout_cw']:.0f}  workflow={p['workflow_cw']:.0f}"
              f"  d={p['d_pct']:.1f}%")

    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as fh:
            json.dump(result, fh, indent=2)
        print(f"\nSummary written to {out_path}")
    return 0

def main(argv=None):
    ap = argparse.ArgumentParser(description="Read-only orchestrate token report.")
    ap.add_argument("marker", nargs="?", help="marker JSON path (or list of pair JSONs with --parity-gate)")
    ap.add_argument("files", nargs="*", help="additional pair JSON files (--parity-gate mode)")
    ap.add_argument("--against", help="second marker for A/B diff")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--home", default=os.path.expanduser("~"))
    ap.add_argument("--parity-gate", action="store_true",
                    help="analyse N paired runs; positional args are per-pair JSON files")
    ap.add_argument("--floor", type=float, default=15.0,
                    help="materiality floor %% for CI lower bound (default 15)")
    ap.add_argument("--out", help="write summary JSON to this path")
    args = ap.parse_args(argv)

    if args.parity_gate:
        all_files = ([args.marker] if args.marker else []) + list(args.files)
        return run_parity_gate(all_files, args.floor, args.out, args.home)

    if not args.marker:
        ap.error("marker is required unless --parity-gate is set")
    rep = build_report(args.marker, args.home)
    if args.against:
        rep["diff"] = diff_reports(rep, build_report(args.against, args.home))
    if args.json:
        print(json.dumps(rep, indent=2))
    else:
        r = rep["run"]
        print(f"run {rep['marker'].get('run_id')} [{rep['marker'].get('engine')}]")
        print(f"  cost-weighted: {r['cost_weighted']:.1f}  cache-hit: {r['cache_hit_ratio']:.2%}")
        print(f"  raw: {r['raw']}")
        for aid, a in rep["agents"].items():
            print(f"  agent {aid}: cw={a['cost_weighted']:.1f}")
        if "diff" in rep:
            print(f"  pct_reduction (vs --against): {rep['diff']['pct_reduction']:.1f}%")
    return 0

if __name__ == "__main__":
    sys.exit(main())
