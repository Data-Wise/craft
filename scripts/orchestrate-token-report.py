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

import argparse, sys

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

def main(argv=None):
    ap = argparse.ArgumentParser(description="Read-only orchestrate token report.")
    ap.add_argument("marker")
    ap.add_argument("--against", help="second marker for A/B diff")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--home", default=os.path.expanduser("~"))
    args = ap.parse_args(argv)
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
