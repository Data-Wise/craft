#!/usr/bin/env python3
"""Soak-then-flip state tracking — the gentle-ramp promotion ledger.

A governance rule starts at `severity: warn`. Once its surface has been observed
clean for a soak window (default 14 days), `run_rules.py --promote-check` lists it
as *promotion-eligible* — a human then flips it to `error` in RULES.yaml. The
machinery **recommends**; the human **promotes** (an irreversible tightening stays
a deliberate edit).

State lives in a LOCAL, gitignored `governance/STATE.json` — soak evidence is
per-machine (the live `~/.claude/skills` tree only exists locally), so it is never
committed. The session audit (`session_hook.py`) feeds it; `--promote-check` reads
it. All date math accepts an injected `today` so tests stay deterministic (no
wall-clock flake).
"""
import json
import os
from datetime import datetime, date

SCHEMA = 1


def _today(today=None):
    return today or date.today().isoformat()


def _days_between(a_iso, b_iso):
    a = datetime.strptime(a_iso, "%Y-%m-%d").date()
    b = datetime.strptime(b_iso, "%Y-%m-%d").date()
    return (b - a).days


def load_state(path):
    """Return the state dict, or a fresh empty one on missing/corrupt/old-schema."""
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        if d.get("schema") == SCHEMA and isinstance(d.get("rules"), dict):
            return d
    except Exception:
        pass
    return {"schema": SCHEMA, "updated": None, "rules": {}}


def record_audit(path, results, today=None):
    """Fold one audit's results into STATE.json. Stamps `last_red` per RED rule,
    sets `first_seen` once, refreshes `last_seen` + recorded `severity` each run.
    Best-effort — a hook must never break a session, so this never raises."""
    today = _today(today)
    try:
        state = load_state(path)
        rules = state["rules"]
        for r in results:
            rid = r.get("id")
            if not rid:
                continue
            entry = rules.setdefault(rid, {"first_seen": today, "last_red": None})
            entry.setdefault("first_seen", today)
            entry["last_seen"] = today
            entry["severity"] = r.get("severity")
            if r.get("state") in ("FAIL", "ERROR"):
                entry["last_red"] = today
        state["updated"] = today
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return state
    except Exception:
        return None


def promotion_eligible(path, warn_rule_ids, today=None, window_days=14):
    """List rules that have soaked clean long enough to recommend `warn → error`.

    `warn_rule_ids` is the authoritative set of currently-`warn` active rule ids
    (from RULES.yaml) — the caller passes it so eligibility never trusts a stale
    severity snapshot in STATE.json. A rule qualifies only if BOTH hold:
      - enough observation history: `first_seen` is >= window_days old, AND
      - no RED within the window: `last_red` is null or >= window_days old.
    Returns a sorted list of dicts: {id, clean_since, clean_days}.
    """
    today = _today(today)
    state = load_state(path)
    eligible = []
    for rid in sorted(warn_rule_ids):
        e = state["rules"].get(rid)
        if not e:
            continue  # never observed on this machine — no soak evidence
        first_seen = e.get("first_seen")
        if not first_seen or _days_between(first_seen, today) < window_days:
            continue  # not enough soak history yet
        last_red = e.get("last_red")
        if last_red and _days_between(last_red, today) < window_days:
            continue  # went RED too recently
        clean_since = last_red or first_seen
        eligible.append({
            "id": rid,
            "clean_since": clean_since,
            "clean_days": _days_between(clean_since, today),
        })
    return eligible
