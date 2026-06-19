import statistics
K = 3

def estimate(run_type, markers):
    xs = sorted(m["cost_weighted"] for m in markers if m.get("engine") == run_type)
    n = len(xs)
    if n < K:
        return {"n": n, "median": (xs[len(xs)//2] if xs else None),
                "p05": None, "p95": None, "cold_start": True}
    def pct(p): return xs[min(n-1, int(p*(n-1)))]
    return {"n": n, "median": statistics.median(xs),
            "p05": pct(0.05), "p95": pct(0.95), "cold_start": False}
