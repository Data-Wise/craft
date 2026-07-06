# Orchestration & the Skill-Evaluation Loop — external-perspective review

> **Status:** internal working doc (not published to the docs site).
> **Origin:** a Cowork / Claude Desktop session (2026-07-02) that built two skills
> (`prompt-engineer` / `prompt-refiner`) end-to-end, then reverse-engineered
> craft's orchestration surface from the outside.
> **Why it's in `docs/internal/`:** §10–§11 compare `/craft:orch`
> (fanout · `--swarm` · `--engine=workflow`) and the new `--dispatch`
> (`orchestrate-dispatch`, v2.57.0 #240) against a hand-rolled subagent loop,
> with a token-cost model and an honest (inconclusive) empirical-measurement
> attempt against `.craft/orchestrate-runs/`.
> **Action for maintainers:** read §9–§11 and mine them for improvements to the
> `orchestrate` command family — see the matching `.STATUS` backlog item.

---

## The tutorial

How the `prompt-engineer` / `prompt-refiner` skills were built, benchmarked, and
iterated — and exactly how to open the **review page that submits reviews**.

**TL;DR** — Write evals → run each eval as a subagent *with* the skill → grade
against assertions → run the same evals *without* the skill (baseline) →
subtract for a delta → **serve** the review page with `generate_review.py`,
leave feedback (auto-saves to `feedback.json`) → tell Claude "done" → Claude reads
the feedback and iterates → repackage the `.skill`. Two ways to run it: **manual**
(what worked in Cowork) and **scripted** (`claude -p`, needs Claude Code).

---

## 0. The mental model

An eval loop answers one question: *does the skill actually make the output
better than plain Claude?* You need three things:

1. **Evals** — a frozen set of prompts + machine-checkable **assertions**.
2. **Two runs of each** — `with_skill` and `without_skill` (baseline).
3. **A grader + a human review pass** — assertions give the number; the review
   page gives the qualitative feedback that drives the next iteration.

---

## 1. Workspace layout

```text
outputs/
  prompt-engineer/                 # skill source (SKILL.md, references/, evals/evals.json)
  prompt-refiner/
  prompt-audit-rubric.md           # the shared rubric that SOURCES the assertions
  prompt-skills-workspace/
    iteration-1/
      <skill>/<eval-name>/
        with_skill/outputs/output.md    + grading.json
        without_skill/outputs/output.md + grading.json   # baseline
    BENCHMARK-DELTA.md
  prompt-skills-eval-review.html   # static snapshot (read-only; NOT the submit server)
```

The **run directory** is any folder containing an `outputs/` subfolder — that's
what the viewer discovers.

---

## 2. Write the evals (the contract)

`evals/evals.json` per skill. Each eval = a realistic `prompt` + 3–5
**assertions** phrased as pass/fail checks. Source the assertions from
`prompt-audit-rubric.md` so "good" is defined the same way every time.

Design rule: at least one eval should be a **negative / restraint** case — e.g.
`thin-intent-clarify` (skill must *ask*, not dump) and `trivial-no-overengineering`
(skill must *not* add chain-of-thought). Those are where a skill earns its delta.

---

## 3. Run the evals — WITH the skill

**Manual (Cowork):** spawn one subagent per eval, in parallel, each told to invoke
the skill and write its verbatim answer to `.../with_skill/outputs/output.md`.
Eight evals → eight subagents in one batch.

**Scripted (Claude Code only):**

```bash
python skill-creator/scripts/run_eval.py \
  --eval-set outputs/prompt-refiner/evals/evals.json \
  --skill-path outputs/prompt-refiner \
  --runs-per-query 3 --num-workers 10 --model <model>
```

`run_eval.py` shells out to `claude -p`, so it needs the Claude Code CLI. In
Cowork there's no `claude -p`, which is why the manual subagent path is the one
that worked.

---

## 4. Grade

Judge each `output.md` against its eval's assertions and write a `grading.json`
next to it: `{eval, config, assertions:[{text,verdict,note}], passed, total}`.
Verdicts: `pass` / `partial` / `n/a`. Be adversarial — a skill that scores 30/30
either is excellent or has weak assertions.

---

## 5. Run the BASELINE — WITHOUT the skill

Same prompts, a plain agent, **no skill**, writing to
`.../without_skill/outputs/output.md`. Grade identically. The delta is the whole
point: skill − baseline.

Result from the origin session: **baseline 19/30 (63%) → with-skill 30/30 (100%),
+11 assertions**, concentrated in *clarify-when-thin*, *move-instruction-to-end*,
and *format discipline*.

Scripted aggregation, if you have both result JSONs:

```bash
python skill-creator/scripts/aggregate_benchmark.py <with.json> <without.json>
```

---

## 6. THE REVIEW PAGE — how to open it and submit reviews

The static `.html` you can double-click is **read-only** — its textareas can't
persist. To actually **submit** reviews you must run the generator, which serves
the page over a tiny HTTP server and writes `feedback.json`:

```bash
python /path/to/skill-creator/eval-viewer/generate_review.py \
  outputs/prompt-skills-workspace/iteration-1 \
  --skill-name prompt-refiner --port 8123
```

Then:

1. **Open** the URL it prints (e.g. `http://localhost:8123`).
2. **Review each run** — arrow keys / buttons to navigate; type notes in **Your
   Feedback**. It **auto-saves** (~0.8s after you stop typing) to `feedback.json`
   in the workspace via `/api/feedback`.
3. Click **Submit All Reviews** → confirm. Feedback is now on disk.
4. Tell Claude **"done reviewing."** Claude reads `feedback.json`, maps each note
   to its `run_id`, and drives iteration 2.

**Fresh iteration with side-by-side history** — regenerate pointing at the prior
round's feedback so the page shows *previous feedback + previous output*:

```bash
python .../generate_review.py outputs/prompt-skills-workspace/iteration-2 \
  --skill-name prompt-refiner \
  --previous-feedback outputs/prompt-skills-workspace/iteration-1/feedback.json
```

> The served viewer needs a local Python + an open port. In a sandbox that can't
> serve a page to the browser, the fallback is: read the **static** viewer and give
> feedback in chat; Claude folds it into iteration 2 the same way.

---

## 7. Iterate

With `feedback.json` (or chat notes) + the baseline delta, edit `SKILL.md` and its
`references/`, bump to `iteration-2/`, and re-run steps 3–6. Stop when assertions
plateau at 100% **and** the review pass surfaces no substantive complaint.

Optional — **description tuning** (improves *triggering*, not output quality):

```bash
python skill-creator/scripts/improve_description.py \
  --eval-results <results.json> --skill-path outputs/prompt-refiner --model <model>
```

---

## 8. Repackage

```bash
cd outputs/prompt-engineer && zip -qr /tmp/prompt-engineer.skill . -x '*.DS_Store'
```

Installed skills keep running the **old** bundle until the new `.skill` is
re-saved/reinstalled. Verify the new content is inside:
`unzip -p x.skill references/prompt-audit-rubric.md | grep GATE`.

---

## 9. Subagent economics — what's actually being saved

**The capability.** Spawning is the **Agent / Task tool** from the Claude Agent
SDK (the same subagent mechanism Claude Code / craft orchestration use). Each call
starts a *fresh agent* with its **own context window**, system prompt, and tool
set. The parent thread gets back only that agent's **final message** — not its
transcript. Subagent *types*: `general-purpose`, `Explore` (read-only search),
`Plan`. You can set `model` per agent (`haiku`/`sonnet`/`opus`) and `SendMessage`
to resume one with its context intact.

**Token-efficient? Yes for context, no for raw spend — know the difference.**

| Dimension | Effect of subagents |
|---|---|
| **Orchestrator context** | **Big win.** 8 baseline runs burned ~300k tokens *inside the subagents*, but the parent ingested only `"done."` + a usage line per run. The main thread never bloats toward compaction. |
| **Wall-clock** | **Win.** 8 ran concurrently instead of serially. |
| **Isolation** | **Win.** Baseline runs can't "see" the skill; no cross-run contamination. |
| **Total tokens billed** | **No saving.** You still pay every subagent's full context. 8 subagents ≈ 8× one run — cheaper *for the parent*, not *in aggregate*. |

**The lever** was *"write your full answer to `output.md`, then reply with just
`done`."* That keeps 1,000-word outputs **out of the parent context** — read back
later only when grading, via capped `sed`/`grep`.

**When to spawn vs. inline** — spawn when the work dumps tokens you don't need in
the main thread, parallelizes cleanly, or needs a clean room; inline when it's
short or you need the content in-context immediately. Batch independent spawns in
one message. Right-size the model. A subagent can't ask a mid-run question (make
the prompt self-contained), returns only its last message (tell it what to
return), and writes to the real filesystem (give absolute paths).

## 10. Doing this with craft (it already has orchestration)

Craft ships a **more mature version of the manual fan-out** (`commands/orch.md`,
`agents/orchestrator-v2.md`, `skills/orchestration/`, `scripts/orchestrate-token-report.py`):

```bash
/craft:orch "<task>"              # fan-out subagents, monitor, synthesize
/craft:orch "<task>" --dry-run    # preview the plan; spawn nothing
/craft:orch "<task>" --swarm      # each agent in its OWN worktree, then converge
/craft:orch "<task>" --refine     # pre-run the task through prompt-refiner first
/craft:orch "<task>" --engine=workflow   # YAML DAG instead of parallel fan-out
/craft:orch status | timeline | compress | continue | abort
```

Over the hand-rolled loop in §3, craft adds: **dry-run planning**; **`--swarm`
worktree isolation**; **token accounting** (`orchestrate-token-report.py` +
`.craft/orchestrate-runs/`); **session persistence**; and it is **already wired to
`prompt-refiner`** via `--refine`. Orchestration is the *spawning + synthesis*
layer; skill-creator is the *eval + review* layer — they compose.

## 11. Execution-mode comparison — including `--dispatch`

`orchestrate-dispatch` (v2.57.0, #240) is a third `--output` value of the
`plan-orchestrator` *Spec → ORCHESTRATE* flow. The other two
(`orchestrate-worktree` default, `orchestrate-only`) write an `ORCHESTRATE-*.md`
and tell **you to open a fresh session** to run it (STOP-new-session).
`--dispatch` instead **fires a background `Agent` from the live planning session**
— the agent's whole prompt is *"Read `ORCHESTRATE-<topic>.md` in full, then
execute it,"* so self-containment is inherited from the durable file.

| Mode | Executor | Same session? | Worktree isolation | Human gate | Resume / failure |
|---|---|---|---|---|---|
| **Manual fan-out** | you spawn `Agent`s | yes | no (shared FS) | none | none |
| **`/craft:orch`** (fanout) | orchestrator spawns agents | yes | no | plan confirm | monitor + synthesize |
| **`--swarm`** | agents in own worktrees | yes | **yes, per-agent** | plan confirm | branch convergence |
| **`--engine=workflow`** | YAML DAG waves | yes | optional | plan confirm | **cache-replay `--resume`** |
| **`plan` STOP-new-session** | a **fresh human session** | **no** | yes (one worktree) | plan confirm | manual resume |
| **`plan --dispatch`** | **background `Agent` from live session** | yes (launches) | yes (one worktree) | **unconditional confirm gate** (`--yes` can't suppress) | idempotent re-dispatch; hang = 2× phase-effort; HELD `.STATUS`, worktree kept |

### Token usage — prediction & actual

| Mode | Orchestrator/parent load | Predictability | Where cost hides |
|---|---|---|---|
| Manual fan-out | **Low** *if* write-to-file + return `done` | Low | grading re-reads |
| orchestrate fanout | Medium (monitor + synthesize N) | Medium | synthesis grows with N |
| `--swarm` | Medium + worktree merge | Medium | branch convergence |
| `--engine=workflow` | **Lowest/agent** (prompt-trim + cache) | **Highest** (static waves) | one-time DAG parse |
| STOP-new-session | planner freed; each exec **cold-starts** | Medium | per-session `C_session` |
| **`--dispatch`** | planner **stays resident** + bg agent reads ORCHESTRATE | Medium | **saves `C_session`** |

**Rule of thumb:** `--dispatch` wins when a fresh session's cold-start
(`C_session` = re-priming CLAUDE.md + context + a new human turn) exceeds the cost
of keeping the planner resident plus the safety machinery. All modes pay the same
`N·T` execution floor; only overhead differs:

```
manual/fanout(in-session):  N·T  +  N·r        (r = small return msg if write-to-file)
STOP-new-session:           N·T  +  Σ C_session (one cold-start per exec session)
--dispatch:                 N·T  +  S_plan_resident + A_orch   (no C_session)
--engine=workflow:          Σ (T − trim) + cache_hits·0        (trim shrinks input; replay is free)
```

**Measurable, not hand-wavy.** Craft emits run markers to `.craft/` and ships
`scripts/orchestrate-token-report.py`, `scripts/quota_estimate.py`,
`scripts/token-probe.py`; `docs/runbooks/parity-gate.md` (N=5 paired) validates
token-efficiency gains without prompt-drift confounds.

**Safety unique to `--dispatch`:** the confirm-before-dispatch gate fires **every
time** (dispatch-now / review-first / cancel) and `--yes` does **not** suppress it.
Soft cap 2 dispatches/session; a hang (no checkbox movement within 2× the phase's
stated effort) leaves the worktree intact with a HELD `.STATUS` note.

### Empirical note (2026-07-02) — why the token numbers stay parametric

An attempt to replace the model with real figures from the nine on-disk
parity-gate markers (`.craft/orchestrate-runs/`, 2026-06-19) was **inconclusive by
data availability**: markers store no token counts (only `engine`/timestamps/
`agents`/`status`); there are **zero `agent-*.jsonl`** transcripts (the input
`orchestrate-token-report.py`'s `per_agent()` needs — the gate almost certainly ran
headless `claude -p`); and summing `usage` over each run's `[start_ts,end_ts]`
window caught 0 records for every fanout run and only 2 near-zero-output turns for
two workflow windows (contamination, not the orchestration). **To get real
numbers:** run a fresh `/craft:orch` once `--engine=fanout` and once
`--engine=workflow`, then **immediately** run `orchestrate-token-report.py` before
`agent-*.jsonl` rotate; `quota_estimate.py` needs K≥3 same-engine runs for
p05/p95, so plan ~3–5 paired runs (exactly `parity-gate.md`).

> **Recommendation hook for maintainers:** this outside view suggests three
> concrete `orchestrate` improvements worth grilling — (1) have every engine write
> a **token-usage field into the run marker itself** (self-contained; no reliance
> on transcript retention / `agent-*.jsonl`), (2) a `--report` convenience flag on
> `/craft:orch` that runs `orchestrate-token-report.py` for the just-finished
> run, and (3) surface the fanout-vs-workflow `cost_weighted` delta in
> `orchestrate status`. Grounded against **v2.57.0** (`CHANGELOG.md` #240;
> `skills/orchestration/plan-orchestrator/SKILL.md`).

## Quick reference

| Step | Manual | Scripted (Claude Code) |
|---|---|---|
| Run evals | spawn subagents → `output.md` | `run_eval.py` |
| Grade | write `grading.json` | grader agent |
| Baseline | subagents, no skill | `run_eval.py` (no `--skill-path`) |
| Delta | `BENCHMARK-DELTA.md` | `aggregate_benchmark.py` |
| **Review+submit** | **`generate_review.py` (served) → feedback.json** | same |
| Iterate | edit SKILL.md, bump iteration | `run_loop.py` |
| Repackage | `zip … .skill` | `package_skill.py` |
| Orchestrate (real) | — | `/craft:orch [--swarm\|--engine=workflow\|--dispatch]` |
