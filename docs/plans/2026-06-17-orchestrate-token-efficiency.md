# Orchestrate Token-Efficiency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce orchestrate token usage by instrumenting it, trimming the inherited context floor, and making craft's deterministic `:workflow` mode the default (where derivable) behind a measured, estimation-based parity gate.

**Architecture:** A read-only Python parser reads ground-truth token `usage` from Claude Code's session JSONL transcripts, attributing it per orchestrate run via markers in `.craft/`. Token levers (floor trim, engine prompt-trim, cache/model routing) are each validated against a baseline. The default engine flips to `:workflow` only if a paired, cost-weighted comparison shows the 95% CI for the reduction clears a 15% floor.

**Tech Stack:** Python 3 (stdlib only — `json`, `pathlib`, `argparse`, `statistics`); pytest; craft markdown commands + `skills/orchestration/workflow-engine/`; bash for the measurement runbook.

**Source spec:** `docs/specs/SPEC-orchestrate-token-efficiency-2026-06-17.md` (approved).

## Global Constraints

- **Branch routing:** Phase 0 + Phases B/1/C/3 are feature code → implement in worktree `feature/orchestrate-workflow-default` (new files + feature behavior are blocked on `dev`). **Lever A is docs-only → `dev`-safe, ship separately.**
- **Parser is read-only:** must NEVER write to `~/.claude/`. Reads JSONL only.
- **Stdlib only** for the parser (no pip deps) — matches craft's `scripts/*.py` convention.
- **Fail soft:** parser tolerates missing/renamed JSONL fields (Claude-Code-internal schema) — never crash an analysis on a missing key.
- **Statistics framing:** report effect sizes + CIs + surprisal (`S = −log₂ p`); do NOT use "statistical significance" / bare p-thresholds. Decisions are interval-vs-floor.
- **Cost-weight defaults** (per-type, input = 1.0): `output = 5.0`, `cache_creation = 1.25`, `cache_read = 0.1`. Stored in a parser table, updatable.
- **Marker location:** `:workflow` runs extend `.craft/workflow-runs/<run>/manifest`; fan-out runs write `.craft/orchestrate-runs/<run-id>.json`. Never `.flow/`.
- **Tests** live in `tests/test_*.py`, run under pytest; wire new tests into the existing suite.

---

## File Structure

| File | Responsibility |
|---|---|
| `scripts/orchestrate-token-report.py` | Read-only CLI: parse session JSONL by run marker → per-run/per-agent cost-weighted token report + A/B diff |
| `scripts/lib/token_report/__init__.py` | (if needed) package marker; keep logic importable for tests |
| `tests/test_orchestrate_token_report.py` | Unit tests vs committed fixture JSONL |
| `tests/fixtures/token_report/session.jsonl` | Deterministic fixture transcript with known usage |
| `tests/fixtures/token_report/agent-AAA.jsonl` | Fixture per-agent transcript |
| `commands/orchestrate.md` | Add `--engine`, marker emission, derivation/confirm rule |
| `commands/orchestrate/workflow.md` | Marker fields in the workflow manifest |
| `skills/orchestration/workflow-engine/SKILL.md` | Prompt-trim (Lever B): spec slice + summaries + structured returns; Haiku routing (Lever C) |
| `MEMORY.md`, `craft/CLAUDE.md`, root `dev-tools/CLAUDE.md` | Lever A floor trim (dev-safe) |
| `docs/runbooks/parity-gate.md` | Phase 3 measurement runbook |
| `CHANGELOG.md` | One entry per shipped phase with measured deltas |

Decompose the parser into small pure functions (each independently testable): marker loading, transcript-dir resolution, JSONL slicing, cost weighting, aggregation, per-agent attribution, formatting. The CLI `main()` wires them together.

---

## Phase 0 — Instrumentation (worktree)

The parser is pure-stdlib and TDD'd function-by-function. Implement in `feature/orchestrate-workflow-default`.

### Task 1: Cost-weighting function

**Files:**

- Create: `scripts/orchestrate-token-report.py`
- Test: `tests/test_orchestrate_token_report.py`

**Interfaces:**

- Produces: `WEIGHTS: dict[str,float]`, `cost_weighted(usage: dict, weights: dict = WEIGHTS) -> float`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_orchestrate_token_report.py
import importlib.util, pathlib
spec = importlib.util.spec_from_file_location(
    "otr", pathlib.Path(__file__).parent.parent / "scripts" / "orchestrate-token-report.py")
otr = importlib.util.module_from_spec(spec); spec.loader.exec_module(otr)

def test_cost_weighted_applies_per_type_weights():
    usage = {"input_tokens": 100, "output_tokens": 10,
             "cache_creation_input_tokens": 40, "cache_read_input_tokens": 200}
    # 100*1 + 10*5 + 40*1.25 + 200*0.1 = 100 + 50 + 50 + 20 = 220
    assert otr.cost_weighted(usage) == 220.0

def test_cost_weighted_tolerates_missing_fields():
    assert otr.cost_weighted({"input_tokens": 10}) == 10.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_orchestrate_token_report.py -v`
Expected: FAIL (`AttributeError: module 'otr' has no attribute 'cost_weighted'`)

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/orchestrate-token-report.py
"""Read-only orchestrate token report. Reads session JSONL; never writes ~/.claude."""
WEIGHTS = {"input_tokens": 1.0, "output_tokens": 5.0,
           "cache_creation_input_tokens": 1.25, "cache_read_input_tokens": 0.1}

def cost_weighted(usage, weights=WEIGHTS):
    return float(sum(weights.get(k, 0.0) * usage.get(k, 0) for k in weights))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_orchestrate_token_report.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/orchestrate-token-report.py tests/test_orchestrate_token_report.py
git commit -m "feat(orchestrate): cost-weighted token metric (read-only report scaffold)"
```

### Task 2: JSONL usage extraction + timestamp slicing

**Files:**

- Modify: `scripts/orchestrate-token-report.py`
- Create: `tests/fixtures/token_report/session.jsonl`
- Modify: `tests/test_orchestrate_token_report.py`

**Interfaces:**

- Consumes: `cost_weighted`
- Produces: `iter_usages(jsonl_path: str, start_ts: str|None, end_ts: str|None) -> list[dict]` (each item the `usage` dict of one assistant message whose `timestamp` is within `[start_ts, end_ts]`)

- [ ] **Step 1: Write the fixture**

```jsonl
{"type":"assistant","timestamp":"2026-06-17T10:00:00Z","message":{"usage":{"input_tokens":100,"output_tokens":10,"cache_creation_input_tokens":0,"cache_read_input_tokens":0}}}
{"type":"assistant","timestamp":"2026-06-17T10:05:00Z","message":{"usage":{"input_tokens":50,"output_tokens":4,"cache_creation_input_tokens":0,"cache_read_input_tokens":200}}}
{"type":"assistant","timestamp":"2026-06-17T11:00:00Z","message":{"usage":{"input_tokens":999,"output_tokens":99,"cache_creation_input_tokens":0,"cache_read_input_tokens":0}}}
```

- [ ] **Step 2: Write the failing test**

```python
import pathlib
FX = pathlib.Path(__file__).parent / "fixtures" / "token_report" / "session.jsonl"

def test_iter_usages_slices_by_timestamp():
    usages = otr.iter_usages(str(FX), "2026-06-17T10:00:00Z", "2026-06-17T10:30:00Z")
    assert len(usages) == 2                       # excludes the 11:00 row
    assert sum(u["input_tokens"] for u in usages) == 150

def test_iter_usages_no_window_returns_all():
    assert len(otr.iter_usages(str(FX), None, None)) == 3
```

- [ ] **Step 3: Run test to verify it fails**

Run: `python3 -m pytest tests/test_orchestrate_token_report.py -k iter_usages -v`
Expected: FAIL (`AttributeError: ... 'iter_usages'`)

- [ ] **Step 4: Write minimal implementation**

```python
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
                continue                          # fail soft on malformed lines
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
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 -m pytest tests/test_orchestrate_token_report.py -k iter_usages -v`
Expected: PASS (2 passed)

- [ ] **Step 6: Commit**

```bash
git add scripts/orchestrate-token-report.py tests/test_orchestrate_token_report.py tests/fixtures/token_report/session.jsonl
git commit -m "feat(orchestrate): JSONL usage extraction with timestamp slicing"
```

### Task 3: Aggregation (totals, cache-hit ratio, cost-weighted)

**Files:**

- Modify: `scripts/orchestrate-token-report.py`
- Modify: `tests/test_orchestrate_token_report.py`

**Interfaces:**

- Consumes: `cost_weighted`, `iter_usages`
- Produces: `aggregate(usages: list[dict]) -> dict` with keys `raw` (per-type sums dict), `cost_weighted` (float), `cache_hit_ratio` (float = cache_read / (input + cache_read), 0.0 if denom 0)

- [ ] **Step 1: Write the failing test**

```python
def test_aggregate_totals_and_cache_ratio():
    usages = otr.iter_usages(str(FX), None, None)
    agg = otr.aggregate(usages)
    assert agg["raw"]["input_tokens"] == 1149      # 100+50+999
    assert agg["raw"]["cache_read_input_tokens"] == 200
    # cache_hit_ratio = 200 / (1149 + 200)
    assert round(agg["cache_hit_ratio"], 4) == round(200/1349, 4)
    assert agg["cost_weighted"] > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_orchestrate_token_report.py -k aggregate -v`
Expected: FAIL (`AttributeError: ... 'aggregate'`)

- [ ] **Step 3: Write minimal implementation**

```python
def aggregate(usages):
    keys = ["input_tokens", "output_tokens",
            "cache_creation_input_tokens", "cache_read_input_tokens"]
    raw = {k: sum(u.get(k, 0) for u in usages) for k in keys}
    denom = raw["input_tokens"] + raw["cache_read_input_tokens"]
    ratio = raw["cache_read_input_tokens"] / denom if denom else 0.0
    return {"raw": raw,
            "cost_weighted": sum(cost_weighted(u) for u in usages),
            "cache_hit_ratio": ratio}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_orchestrate_token_report.py -k aggregate -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/orchestrate-token-report.py tests/test_orchestrate_token_report.py
git commit -m "feat(orchestrate): aggregate totals, cost-weighted, cache-hit ratio"
```

### Task 4: Marker loading + transcript-dir resolution

**Files:**

- Modify: `scripts/orchestrate-token-report.py`
- Modify: `tests/test_orchestrate_token_report.py`

**Interfaces:**

- Produces:
  - `transcript_dir(cwd: str, home: str) -> str` → `<home>/.claude/projects/<slug>` where `slug` = `cwd` with `/` and `.` replaced by `-`
  - `load_marker(path: str) -> dict` (reads a fan-out marker JSON or a `:workflow` manifest; returns `{run_id, cwd, start_ts, end_ts, engine, ...}`)

- [ ] **Step 1: Write the failing test**

```python
def test_transcript_dir_slug():
    assert otr.transcript_dir("/Users/dt/projects/dev-tools/craft", "/Users/dt") == \
        "/Users/dt/.claude/projects/-Users-dt-projects-dev-tools-craft"

def test_load_marker(tmp_path):
    m = tmp_path / "run.json"
    m.write_text('{"run_id":"x","cwd":"/c","start_ts":"a","end_ts":"b","engine":"fanout"}')
    assert otr.load_marker(str(m))["engine"] == "fanout"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_orchestrate_token_report.py -k "transcript_dir or load_marker" -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
import re

def transcript_dir(cwd, home):
    slug = re.sub(r"[/.]", "-", cwd)
    return f"{home}/.claude/projects/{slug}"

def load_marker(path):
    with open(path) as f:
        return json.load(f)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_orchestrate_token_report.py -k "transcript_dir or load_marker" -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/orchestrate-token-report.py tests/test_orchestrate_token_report.py
git commit -m "feat(orchestrate): marker loading + transcript-dir slug resolution"
```

### Task 5: Per-agent attribution from `agent-*.jsonl`

**Files:**

- Modify: `scripts/orchestrate-token-report.py`
- Create: `tests/fixtures/token_report/agent-AAA.jsonl`
- Modify: `tests/test_orchestrate_token_report.py`

**Interfaces:**

- Consumes: `iter_usages`, `aggregate`
- Produces: `per_agent(transcript_dir: str, start_ts, end_ts) -> dict[str, dict]` keyed by agent id (from filename `agent-<id>.jsonl`), value = `aggregate(...)` for that agent within the window

- [ ] **Step 1: Write the fixture**

```jsonl
{"type":"assistant","timestamp":"2026-06-17T10:10:00Z","message":{"usage":{"input_tokens":80,"output_tokens":8,"cache_creation_input_tokens":0,"cache_read_input_tokens":0}}}
```

- [ ] **Step 2: Write the failing test**

```python
def test_per_agent_attribution():
    d = str(FX.parent)
    agents = otr.per_agent(d, "2026-06-17T10:00:00Z", "2026-06-17T10:30:00Z")
    assert "AAA" in agents
    assert agents["AAA"]["raw"]["input_tokens"] == 80
```

- [ ] **Step 3: Run test to verify it fails**

Run: `python3 -m pytest tests/test_orchestrate_token_report.py -k per_agent -v`
Expected: FAIL

- [ ] **Step 4: Write minimal implementation**

```python
import glob, os

def per_agent(transcript_dir, start_ts, end_ts):
    result = {}
    for path in glob.glob(os.path.join(transcript_dir, "agent-*.jsonl")):
        agent_id = os.path.basename(path)[len("agent-"):-len(".jsonl")]
        result[agent_id] = aggregate(iter_usages(path, start_ts, end_ts))
    return result
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 -m pytest tests/test_orchestrate_token_report.py -k per_agent -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add scripts/orchestrate-token-report.py tests/test_orchestrate_token_report.py tests/fixtures/token_report/agent-AAA.jsonl
git commit -m "feat(orchestrate): per-agent token attribution from agent-*.jsonl"
```

### Task 6: CLI (`main`), `--json`, A/B diff, read-only guarantee

**Files:**

- Modify: `scripts/orchestrate-token-report.py`
- Modify: `tests/test_orchestrate_token_report.py`

**Interfaces:**

- Consumes: all of the above
- Produces: `build_report(marker_path, home) -> dict`; `diff_reports(a, b) -> dict` (with `pct_reduction` on `cost_weighted`); `main(argv) -> int`

- [ ] **Step 1: Write the failing test**

```python
def test_diff_reports_pct_reduction():
    a = {"run": {"cost_weighted": 100.0}}
    b = {"run": {"cost_weighted": 80.0}}
    d = otr.diff_reports(a, b)
    assert d["pct_reduction"] == 20.0            # (100-80)/100*100

def test_report_is_read_only(tmp_path, monkeypatch):
    # building a report must not create/modify anything under a fake HOME/.claude
    fake_home = tmp_path / "home"; (fake_home / ".claude").mkdir(parents=True)
    before = set((fake_home / ".claude").rglob("*"))
    m = tmp_path / "run.json"
    m.write_text('{"run_id":"x","cwd":"/c","start_ts":null,"end_ts":null,"engine":"fanout"}')
    try:
        otr.build_report(str(m), str(fake_home))
    except FileNotFoundError:
        pass                                      # transcript dir absent is fine
    assert set((fake_home / ".claude").rglob("*")) == before
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_orchestrate_token_report.py -k "diff_reports or read_only" -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_orchestrate_token_report.py -v`
Expected: PASS (all tasks 1–6 green)

- [ ] **Step 5: Add `--help` smoke + commit**

Run: `python3 scripts/orchestrate-token-report.py --help`
Expected: usage text prints, exit 0.

```bash
git add scripts/orchestrate-token-report.py tests/test_orchestrate_token_report.py
git commit -m "feat(orchestrate): token-report CLI with --json + A/B diff (read-only)"
```

### Task 7: Emit run markers from orchestrate

**Files:**

- Modify: `commands/orchestrate.md` (fan-out path: write `.craft/orchestrate-runs/<run-id>.json` at start; update `end_ts` at finish)
- Modify: `commands/orchestrate/workflow.md` (add the marker fields to the existing `.craft/workflow-runs/<run>/manifest`)

**Interfaces:**

- Produces: marker files matching `load_marker`'s expected keys: `{run_id, command, mode, engine, agents, max_turns, cwd, start_ts, end_ts}`.

- [ ] **Step 1: Add marker-emission instructions to `commands/orchestrate.md`**

Insert a "Token instrumentation" subsection instructing: at run start, compute `run_id = <ISO8601-start>-<mode>` and write `.craft/orchestrate-runs/<run-id>.json` with `engine: "fanout"` and `start_ts`; at run end, set `end_ts`. (`.craft/orchestrate-runs/` must be gitignored — see Step 3.)

- [ ] **Step 2: Add marker fields to `commands/orchestrate/workflow.md` manifest**

Instruct the workflow engine to include `{run_id, command, mode, engine:"workflow", agents, max_turns, cwd, start_ts, end_ts}` in `.craft/workflow-runs/<run>/manifest`.

- [ ] **Step 3: Gitignore the fan-out marker dir**

Add `.craft/orchestrate-runs/` to `.gitignore` (sibling to the existing `.craft/workflow-runs/`).

- [ ] **Step 4: Verify (manual)**

Run a tiny orchestrate task; confirm a marker file appears with all keys and that `scripts/orchestrate-token-report.py <marker>` produces a report.

- [ ] **Step 5: Commit**

```bash
git add commands/orchestrate.md commands/orchestrate/workflow.md .gitignore
git commit -m "feat(orchestrate): emit token run-markers (.craft/ infra)"
```

---

## Lever A — Context-Floor Trim (DEV-SAFE — separate, ship first)

> Do this on `dev` (or no-commit for out-of-repo files). It is independent of the worktree.

### Task 8: Baseline, trim, re-measure the floor

**Files:**

- Modify: `MEMORY.md` (curate 105 entries → leaner index; merge/drop duplicates)
- Modify: root `dev-tools/CLAUDE.md` (de-duplicate; outside git — edit in place)
- Modify: `craft/CLAUDE.md` (tighten; existing file → `dev`-safe)

- [ ] **Step 1: Measure the floor BEFORE**

Run: `wc -c MEMORY.md ../CLAUDE.md craft/CLAUDE.md` (record bytes; approximate tokens = bytes/4).

- [ ] **Step 2: Trim** — curate `MEMORY.md` to a tighter index (one-line pointers only; no duplicated bodies), de-duplicate the root CLAUDE.md, tighten craft/CLAUDE.md. Preserve all `[[links]]` validity.

- [ ] **Step 3: Measure AFTER + verify links**

Run: `wc -c MEMORY.md ../CLAUDE.md craft/CLAUDE.md` and confirm reduction. Grep for now-dangling `[[...]]` links.

- [ ] **Step 4: Commit (dev)**

```bash
git add craft/CLAUDE.md   # MEMORY.md and root CLAUDE.md are out-of-repo
git commit -m "docs: trim craft CLAUDE.md context floor (Lever A)"
```

Record the before/after delta in the CHANGELOG and the spec's validation section.

---

## Phase B — Engine Prompt-Trim (worktree)

### Task 9: Spec-slice + summarized prior outputs in the workflow engine

**Files:**

- Modify: `skills/orchestration/workflow-engine/SKILL.md`

**Interfaces:**

- Produces: each Task subagent prompt = `{spec slice for this agent's files/phase} + {summaries of prior-stage outputs} + {instruction to return a concise structured summary}`. NOT the whole spec / full transcripts.

- [ ] **Step 1: Edit SKILL.md prompt-composition section** — specify that the engine passes only the agent's file-scoped spec slice, summarized prior outputs, and requires a short structured return.

- [ ] **Step 2: Behavior-parity check** — run the reference task via `:workflow`; confirm same files acted on, tests green.

- [ ] **Step 3: Measure** — `scripts/orchestrate-token-report.py <run>`; record per-agent input tokens **minus the inherited floor** (Lever A's domain) so Lever B's win is isolated.

- [ ] **Step 4: Commit**

```bash
git add skills/orchestration/workflow-engine/SKILL.md
git commit -m "feat(orchestrate): engine prompt-trim — spec slice + summaries (Lever B)"
```

---

## Phase 1 — `:workflow` Default Flip (worktree, flag-gated)

### Task 10: `--engine` flag + derivation/confirm routing

**Files:**

- Modify: `commands/orchestrate.md`

**Interfaces:**

- Produces: `--engine=workflow|fanout` (default `fanout` until Phase 3 passes). Routing: default to `:workflow` when a SPEC/ORCHESTRATE plan exists (reuse drive's derivation); free-form → fan-out. Auto-derived workflow → show + confirm; explicit plan file → auto-run; auto-mode flag skips confirm.

- [ ] **Step 1: Add the `--engine` flag + routing rule to `commands/orchestrate.md`** (derivable→`:workflow`, else fan-out; confirm gate as above). Keep the documented default `fanout`.

- [ ] **Step 2: Verify** — `/craft:orchestrate` with a spec present routes to `:workflow` and shows the confirm; a free-form prompt falls back to fan-out.

- [ ] **Step 3: Commit**

```bash
git add commands/orchestrate.md
git commit -m "feat(orchestrate): --engine flag + derivable-vs-fanout routing (default fanout)"
```

---

## Phase C — Cache + Model Routing (worktree)

### Task 11: Byte-stable tools, batching, Haiku for cheap stages

**Files:**

- Modify: `skills/orchestration/workflow-engine/SKILL.md`

- [ ] **Step 1: Edit SKILL.md** — instruct: keep the tool set/system prompt byte-stable across a run; batch turns (5-min cache TTL); dispatch cheap file-scoped subagents with the Haiku model.

- [ ] **Step 2: Measure** — re-run reference task; confirm cache-hit ratio up and cheap stages on Haiku via the report.

- [ ] **Step 3: Commit**

```bash
git add skills/orchestration/workflow-engine/SKILL.md
git commit -m "feat(orchestrate): cache-stable tools + Haiku routing for cheap stages (Lever C)"
```

---

## Phase 3 — Parity Gate (worktree; runbook, not code)

### Task 12: Run the paired, estimation-based parity gate

**Files:**

- Create: `docs/runbooks/parity-gate.md`

- [ ] **Step 1: Write the runbook** documenting the protocol:
  - Pick one reference task (a representative spec).
  - **N = 5 paired runs**, each pair = same task on `--engine=fanout` then `--engine=workflow`, both **cold-cache** (fresh session).
  - For each run, capture the cost-weighted metric via `scripts/orchestrate-token-report.py`.
  - Compute per-pair % reduction; report **mean % reduction + 95% CI**, **Cohen's *dₙ***, and **surprisal** (`S = −log₂ p`) as graded evidence (no "significance" verdict).

- [ ] **Step 2: Execute the runbook**, collecting the 5 pairs.

- [ ] **Step 3: Decide the flip** — if the **95% CI for the % reduction lies entirely above 15%** AND behavior parity holds AND no new failure modes → set `commands/orchestrate.md` default to `--engine=workflow` (where derivable), keeping `--engine=fanout`. Otherwise leave default `fanout`, keep `:workflow` opt-in, and record the measured effect + interval.

- [ ] **Step 4: Commit the outcome**

```bash
git add docs/runbooks/parity-gate.md commands/orchestrate.md CHANGELOG.md
git commit -m "feat(orchestrate): parity-gate runbook + flip decision (estimation-based)"
```

---

## Phase Q — Pre-Flight Quota Gate (worktree)

Builds on Phase 0's parser. New live-quota source: a statusline persister writes the native
`rate_limits` to a cache the command can read.

### Task 13: rate_limits persister

**Files:**

- Create: `scripts/quota-persist.sh`
- Test: `tests/test_quota_persist.sh`

**Interfaces:**

- Produces: reads a statusline stdin JSON on stdin; writes `~/.claude/quota-cache.json` =
  `{ five_hour_pct, seven_day_pct, five_hour_resets_at, seven_day_resets_at, captured_at }`.
  On absent `rate_limits`, keeps the existing file (last-good) and exits 0 without fabricating.

- [ ] **Step 1: Write the failing test**

```bash
# tests/test_quota_persist.sh
set -e
TMP=$(mktemp -d); export HOME="$TMP"; mkdir -p "$HOME/.claude"
echo '{"rate_limits":{"five_hour":{"used_percentage":31,"resets_at":1781000000},"seven_day":{"used_percentage":9,"resets_at":1781500000}}}' \
  | bash scripts/quota-persist.sh
test -f "$HOME/.claude/quota-cache.json" || { echo FAIL no cache; exit 1; }
grep -q '"five_hour_pct": *31' "$HOME/.claude/quota-cache.json" || { echo FAIL pct; exit 1; }
# absent rate_limits keeps last-good (does not overwrite to empty)
echo '{"model":{"display_name":"Opus"}}' | bash scripts/quota-persist.sh
grep -q '"five_hour_pct": *31' "$HOME/.claude/quota-cache.json" || { echo FAIL last-good; exit 1; }
echo PASS
```

- [ ] **Step 2: Run it, verify FAIL** — `bash tests/test_quota_persist.sh` → FAIL (script missing).

- [ ] **Step 3: Implement**

```bash
# scripts/quota-persist.sh — persist native rate_limits for non-statusline consumers.
in=$(cat); cache="$HOME/.claude/quota-cache.json"
has=$(printf '%s' "$in" | jq -r 'has("rate_limits") and (.rate_limits|has("five_hour"))' 2>/dev/null)
[ "$has" = "true" ] || exit 0           # absent → keep last-good, do not fabricate
printf '%s' "$in" | jq '{
  five_hour_pct: .rate_limits.five_hour.used_percentage,
  seven_day_pct: .rate_limits.seven_day.used_percentage,
  five_hour_resets_at: .rate_limits.five_hour.resets_at,
  seven_day_resets_at: .rate_limits.seven_day.resets_at,
  captured_at: now
}' > "$cache"
```

- [ ] **Step 4: Run it, verify PASS** — `bash tests/test_quota_persist.sh` → PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/quota-persist.sh tests/test_quota_persist.sh
git commit -m "feat(quota): statusline rate_limits persister (timestamped, keep-last-good)"
```

### Task 14: Cost estimator (historical distribution + cold-start)

**Files:**

- Create: `scripts/quota_estimate.py`
- Test: `tests/test_quota_estimate.py`

**Interfaces:**

- Consumes: Phase-0 markers + `orchestrate-token-report.py` history.
- Produces: `estimate(run_type: str, markers: list[dict]) -> dict` = `{ n, median, p05, p95, cold_start: bool }` (cost-weighted). `cold_start=True` and wide/None interval when `n < K` (K=3).

- [ ] **Step 1: Write the failing test**

```python
import importlib.util, pathlib
spec = importlib.util.spec_from_file_location("qe", pathlib.Path(__file__).parent.parent/"scripts"/"quota_estimate.py")
qe = importlib.util.module_from_spec(spec); spec.loader.exec_module(qe)

def test_estimate_distribution():
    markers = [{"engine":"workflow","cost_weighted":c} for c in [100,120,110,130,90]]
    e = qe.estimate("workflow", markers)
    assert e["n"] == 5 and e["cold_start"] is False
    assert e["p05"] <= e["median"] <= e["p95"]

def test_estimate_cold_start():
    e = qe.estimate("workflow", [{"engine":"workflow","cost_weighted":100}])
    assert e["cold_start"] is True        # n < 3
```

- [ ] **Step 2: Run it, verify FAIL** — `python3 -m pytest tests/test_quota_estimate.py -v` → FAIL.

- [ ] **Step 3: Implement**

```python
# scripts/quota_estimate.py
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
```

- [ ] **Step 4: Run it, verify PASS** — `python3 -m pytest tests/test_quota_estimate.py -v` → PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/quota_estimate.py tests/test_quota_estimate.py
git commit -m "feat(quota): historical cost estimator (median+interval, cold-start honest)"
```

### Task 15: `/craft:quota` command (join, advise, stale-refusal, --json)

**Files:**

- Create: `commands/quota.md`

**Interfaces:**

- Consumes: `~/.claude/quota-cache.json` (Task 13), `quota_estimate.py` (Task 14).
- Produces: prints estimate + % of each remaining window + reset times + `SAFE|TIGHT|DEFER`;
  writes `.craft/quota.json` (the contract flow consumes). **Refuses** (warns) if the cache
  `captured_at` is older than `STALE_SECS` (default 900) or absent.

- [ ] **Step 1: Author `commands/quota.md`** with steps: (1) read `quota-cache.json`; if absent
  or `now - captured_at > STALE_SECS` → print "quota stale (Nm old) — re-render statusline" and
  stop (no advice on stale data). (2) Run `quota_estimate.py <run-type>`; if `cold_start`, label
  the estimate "insufficient history (n=K)". (3) Compute `pct_of_5h = median/remaining_5h_budget`
  etc.; map to `SAFE` (<60% of the tighter window), `TIGHT` (60–100%), `DEFER` (>100%, show reset
  time). (4) Write `.craft/quota.json`. Add `--json`.

- [ ] **Step 2: Manual verify** — with a fresh `quota-cache.json`, `/craft:quota workflow`
  prints a recommendation; with a stale cache, it refuses.

- [ ] **Step 3: Gitignore** — add `.craft/quota.json` to `.gitignore` (runtime output).

- [ ] **Step 4: Commit**

```bash
git add commands/quota.md .gitignore
git commit -m "feat(quota): /craft:quota pre-flight gate (advisory, stale-refusing)"
```

### Task 16: `/craft:check` quota validator + docs

**Files:**

- Modify: `commands/check.md` (add an optional quota validator that calls `/craft:quota`)
- Modify: `commands/orchestrate.md` / docs (mention `/craft:quota` before heavy runs)

- [ ] **Step 1: Add an opt-in quota validator** to `/craft:check` that surfaces the current
  `SAFE/TIGHT/DEFER` for a `:workflow` run (skips silently if `quota-cache.json` absent).
- [ ] **Step 2: Doc cross-links** — reference `/craft:quota` from orchestrate docs + CHANGELOG.
- [ ] **Step 3: Commit**

```bash
git add commands/check.md commands/orchestrate.md CHANGELOG.md
git commit -m "feat(quota): /craft:check quota validator + docs cross-links"
```

---

## Self-Review

- **Spec coverage:** Phase 0 → Tasks 1–7; Lever A → Task 8; Lever B → Task 9; Phase 1 → Task 10; Lever C → Task 11; Phase 3 → Task 12; **Phase Q → Tasks 13–16** (persister, estimator, `/craft:quota`, `/craft:check` validator). ✅ All spec phases mapped (flow consumer is out-of-scope per spec).
- **Read-only guarantee:** Task 6 Step 1 includes an explicit no-write test against a fake HOME. ✅
- **Cost-weight + cache-controlled metric:** Tasks 1 & 3 implement the spec's cost-weighted metric verbatim (weights from Global Constraints). ✅
- **Marker location:** Task 7 uses `.craft/` (workflow manifest + fan-out dir), never `.flow/`. ✅
- **Estimation framing:** Task 12 reports CI + Cohen's *dₙ* + surprisal; flip is interval-vs-15%-floor, no p-threshold language. ✅
- **Type consistency:** `cost_weighted`, `iter_usages`, `aggregate`, `transcript_dir`, `load_marker`, `per_agent`, `build_report`, `diff_reports` referenced consistently across tasks. ✅
- **Branch routing:** Lever A flagged dev-safe; all else worktree (incl. Phase Q). ✅
- **Phase Q guardrails:** Task 13 has a keep-last-good test (no fabrication on absent `rate_limits`); Task 14 has a cold-start test (`n<K` → honest wide interval); Task 15 refuses on stale cache. Honest-uncertainty checks present. ✅
- **Phase Q type consistency:** `quota-cache.json` fields (`five_hour_pct`, `captured_at`, …) and `estimate()` keys (`n`, `median`, `p05`, `p95`, `cold_start`) referenced consistently across Tasks 13–15. ✅
