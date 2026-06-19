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

def aggregate(usages):
    keys = ["input_tokens", "output_tokens",
            "cache_creation_input_tokens", "cache_read_input_tokens"]
    raw = {k: sum(u.get(k, 0) for u in usages) for k in keys}
    denom = raw["input_tokens"] + raw["cache_read_input_tokens"]
    ratio = raw["cache_read_input_tokens"] / denom if denom else 0.0
    return {"raw": raw,
            "cost_weighted": sum(cost_weighted(u) for u in usages),
            "cache_hit_ratio": ratio}
