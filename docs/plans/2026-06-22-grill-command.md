# `/craft:grill` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `/craft:grill` — a standalone one-question-at-a-time interrogation command that stress-tests a spec/plan or bare topic, walking the design tree with a recommended answer per question, codebase-first, capturing a durable decision-ledger spec that feeds the `/plan → /do` pipeline.

**Architecture:** A markdown command (`commands/grill.md`) carrying the interrogation contract, backed by one Python util (`commands/utils/grill_ledger.py`) for collision-safe output-filename resolution + decision-ledger append. The interactive loop itself is model-executed (not Python); its *structure* and the *util* are the testable surfaces. Orchestrate's Step 0.5 reuses grill via a bounded pass.

**Tech Stack:** craft plugin conventions (markdown commands + `commands/utils/*.py`), Python 3 stdlib only, pytest harness (`tests/`), bump-version + validate-counts for the count cascade.

## Global Constraints

- Branch model: code on `feature/*` worktree only; never new code files on `dev`/`main`. (verbatim: `~/.claude/CLAUDE.md`)
- Strict plugin.json schema — no unrecognized frontmatter keys. (memory: claude-code-plugin-json-strict-schema)
- No `execSync`; use `execFileSync`. Python utils: stdlib only, POSIX-portable (BSD/GNU sed parity not relevant here; no shelling out needed).
- Adding ONE command triggers the ~30-file count cascade: ~14 bump-version files + `plugin.json (N craft)` subtotal (manual) + ~29 doc refs + Phase 8 doc entry. (memory: adding-a-command-cascades-30-file-count-bump)
- Frontmatter list-value descriptions containing a colon must be quoted (command-audit uses real YAML).
- Current version baseline: v2.47.0; counts 113 / 39 / 8 → grill makes it 114 commands.
- TDD: failing test → run-fail → minimal impl → run-pass → commit. DRY, YAGNI, frequent commits.

---

## Wave structure (gates)

| Wave | Deliverable | Gate |
|---|---|---|
| **W1** | Collision-safe ledger util + command scaffold (frontmatter, args incl. `--bound`/`--stop`, discovery) | none — start here |
| **W2** | Interrogation contract body (directives, codebase-first read-then-confirm, decision-ledger capture, `/plan` handoff) | W1 |
| **W3** | Orchestrate optimize/refactor (lean contract + reference-doc split) + Step 0.5 → bounded grill | W1+W2 (grill `--bound` exists) |
| **W4** | grill-with-docs (G7): ADR + `CONTEXT.md` glossary on-the-spot | W2 — DEFERRABLE (heavy) |
| **W5** | Docs + count cascade + release prep | W1–W3 green |

Each wave produces working, testable software on its own. W4 is optional and must not block W1–W3.

---

## Wave 1 — Ledger util + command scaffold

### Task 1: Collision-safe output-filename resolver

**Files:**

- Create: `commands/utils/grill_ledger.py`
- Test: `tests/test_grill_ledger.py`

**Interfaces:**

- Produces: `resolve_ledger_path(topic: str, date: str, specs_dir: str) -> tuple[str, str]` returning `(path, mode)` where `mode ∈ {"create", "append"}`. If a brainstorm `SPEC-<topic>-<date>.md` already exists, grill APPENDS to it (mode="append"); otherwise it creates `GRILL-<topic>-<date>.md` (mode="create"). Fixes the confirmed brainstorm/grill collision.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_grill_ledger.py
import os, tempfile
from commands.utils.grill_ledger import resolve_ledger_path

def test_creates_grill_prefixed_file_when_no_spec_exists():
    with tempfile.TemporaryDirectory() as d:
        path, mode = resolve_ledger_path("auth", "2026-06-22", d)
        assert path == os.path.join(d, "GRILL-auth-2026-06-22.md")
        assert mode == "create"

def test_appends_to_existing_brainstorm_spec():
    with tempfile.TemporaryDirectory() as d:
        spec = os.path.join(d, "SPEC-auth-2026-06-22.md")
        open(spec, "w").write("# spec\n")
        path, mode = resolve_ledger_path("auth", "2026-06-22", d)
        assert path == spec
        assert mode == "append"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_grill_ledger.py -v`
Expected: FAIL — `ModuleNotFoundError: commands.utils.grill_ledger`

- [ ] **Step 3: Write minimal implementation**

```python
# commands/utils/grill_ledger.py
"""Collision-safe ledger path resolution for /craft:grill.

brainstorm writes docs/specs/SPEC-<topic>-<date>.md; grill must not clobber it.
"""
import os


def resolve_ledger_path(topic, date, specs_dir):
    """Return (path, mode). Append to a brainstorm SPEC if present, else create a GRILL file."""
    slug = topic.strip().lower().replace(" ", "-")
    spec = os.path.join(specs_dir, f"SPEC-{slug}-{date}.md")
    if os.path.exists(spec):
        return spec, "append"
    return os.path.join(specs_dir, f"GRILL-{slug}-{date}.md"), "create"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_grill_ledger.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add commands/utils/grill_ledger.py tests/test_grill_ledger.py
git commit -m "feat(grill): collision-safe ledger path resolver"
```

### Task 2: Decision-ledger append helper

**Files:**

- Modify: `commands/utils/grill_ledger.py`
- Test: `tests/test_grill_ledger.py`

**Interfaces:**

- Produces: `append_decision(path: str, branch_id: str, branch: str, decision: str) -> None` — appends a markdown table row to a `## Decision Ledger` section, creating the section + header if absent. Idempotent header (never double-writes the header row).

- [ ] **Step 1: Write the failing test**

```python
from commands.utils.grill_ledger import append_decision

def test_append_decision_creates_section_then_rows():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "GRILL-x-2026-06-22.md")
        open(p, "w").write("# Grill: x\n")
        append_decision(p, "G1", "Form factor", "Standalone command")
        append_decision(p, "G2", "Interaction", "One-at-a-time")
        body = open(p).read()
        assert body.count("## Decision Ledger") == 1
        assert body.count("| # | Branch | Decision |") == 1
        assert "| G1 | Form factor | Standalone command |" in body
        assert "| G2 | Interaction | One-at-a-time |" in body
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_grill_ledger.py::test_append_decision_creates_section_then_rows -v`
Expected: FAIL — `ImportError: cannot import name 'append_decision'`

- [ ] **Step 3: Write minimal implementation**

```python
LEDGER_HEADER = "## Decision Ledger\n\n| # | Branch | Decision |\n|---|---|---|\n"


def append_decision(path, branch_id, branch, decision):
    body = open(path).read() if os.path.exists(path) else ""
    if "## Decision Ledger" not in body:
        if body and not body.endswith("\n"):
            body += "\n"
        body += "\n" + LEDGER_HEADER
    body += f"| {branch_id} | {branch} | {decision} |\n"
    open(path, "w").write(body)
```

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m pytest tests/test_grill_ledger.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add commands/utils/grill_ledger.py tests/test_grill_ledger.py
git commit -m "feat(grill): live decision-ledger append helper"
```

### Task 3: Command scaffold + frontmatter (discovery + audit pass)

**Files:**

- Create: `commands/grill.md`
- Test: `tests/test_grill_command.py`

**Interfaces:**

- Produces: the `grill` command discoverable by `_discovery.py` and valid per `command-audit`. Arguments: `target` (optional), `--bound N` (limit branches — used by orchestrate Step 0.5), `--stop` token doc, `--yes` (re-run auto-accept).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_grill_command.py
import subprocess, sys, os
CRAFT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_grill_command_exists_and_has_frontmatter():
    p = os.path.join(CRAFT, "commands", "grill.md")
    assert os.path.exists(p), "commands/grill.md missing"
    head = open(p).read()
    assert head.startswith("---"), "missing frontmatter"
    assert "description:" in head
    assert "name: bound" in head, "missing --bound arg (orchestrate Step 0.5 needs it)"

def test_grill_passes_command_audit():
    r = subprocess.run([sys.executable, "scripts/command-audit.sh".replace("scripts/","scripts/")],
                       cwd=CRAFT, capture_output=True, text=True)
    # audit is a bash script; invoke via bash
    r = subprocess.run(["bash", os.path.join(CRAFT, "scripts", "command-audit.sh")],
                       cwd=CRAFT, capture_output=True, text=True)
    assert "grill" not in r.stdout or "ERROR" not in r.stdout.upper()
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_grill_command.py -v`
Expected: FAIL — `commands/grill.md missing`

- [ ] **Step 3: Write minimal implementation (frontmatter + stub body)**

```markdown
---
description: Adversarially interrogate a plan, spec, or topic one question at a time — convergent counterpart to brainstorm
arguments:
  - name: target
    description: "Spec/plan path, a topic in quotes, or empty to detect from context"
    required: false
  - name: bound
    description: "Limit interrogation to N decision branches (used by orchestrate Step 0.5 for a quick gate)"
    required: false
    default: null
  - name: yes
    description: "Auto-accept recommended answers — only for re-running a settled artifact"
    required: false
    default: false
    alias: -y
---

# /craft:grill — Interrogate Before Building

Convergent counterpart to `/craft:workflow:brainstorm` (which is divergent — it
GENERATES options; grill INTERROGATES a position to find gaps). Use grill to
stress-test a spec/plan before implementation.

<!-- contract body added in Wave 2 -->
```

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m pytest tests/test_grill_command.py -v && bash scripts/command-audit.sh`
Expected: PASS; audit reports no errors for `grill`.

- [ ] **Step 5: Commit**

```bash
git add commands/grill.md tests/test_grill_command.py
git commit -m "feat(grill): command scaffold + frontmatter (bound/yes args)"
```

---

## Wave 2 — Interrogation contract body

### Task 4: Port the three directives + one-at-a-time loop + stop signal

**Files:**

- Modify: `commands/grill.md` (replace `<!-- contract body -->`)
- Test: `tests/test_grill_command.py`

**Interfaces:**

- Consumes: frontmatter args from Task 3.
- Produces: a body containing the verbatim grill-me directives, the codebase-first rule, the explicit `--stop` / "say stop" halt, and the `--bound` honoring. (Structure-testable; the live loop is model-executed.)

- [ ] **Step 1: Write the failing test**

```python
def test_grill_body_carries_contract():
    body = open(os.path.join(CRAFT, "commands", "grill.md")).read()
    assert "one question at a time" in body.lower()
    assert "recommended" in body.lower()                      # recommended-answer rule
    assert "explore the codebase" in body.lower()             # codebase-first
    assert "stop" in body.lower()                             # halt signal defined
    assert "bound" in body.lower()                            # bounded pass honored
    # justify the deliberate AskUserQuestion exception so a future audit won't "fix" it:
    assert "one at a time" in body.lower() and "askuserquestion" in body.lower()
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_grill_command.py::test_grill_body_carries_contract -v`
Expected: FAIL — directives not present.

- [ ] **Step 3: Write minimal implementation (the contract body)**

````markdown
## When Invoked

### Step 1: Resolve the target

- Path argument → load that artifact.
- Quoted topic → sketch a 3–5 bullet skeleton, show it, then interrogate the skeleton.
- Empty → detect from `.STATUS`, branch name, recent commits; confirm the target before grilling.

### Step 2: Codebase-first sweep (read-then-confirm)

Before asking anything, read repo evidence (`.STATUS`, git log, `docs/specs/*`,
`commands/`, `~/.claude/settings.json` when relevant) and PRE-ANSWER every branch you can.
Each pre-answer becomes the **Recommended:** line on its question — shown, never silently
skipped, so the user can override.

### Step 3: The grill loop (deliberate one-at-a-time)

Follow the grill-me directives:

> Interview the user relentlessly about every aspect until shared understanding. Walk each
> branch of the design tree, resolving dependencies one-by-one. For EACH question provide a
> **Recommended:** answer. Ask **one question at a time**. If a question can be answered by
> exploring the codebase, explore the codebase instead.

**Why one-at-a-time free-text and NOT AskUserQuestion batches:** decision-tree fidelity is the
point — each answer reshapes the next question. This is a deliberate exception to craft's
AskUserQuestion-batch convention; do not "fix" it to batches.

**Halt:** the user types `stop` (or `--stop` was passed) → go to Step 4. If `--bound N` was
given, stop after N resolved branches. Otherwise continue until every branch resolves.

**After each resolved branch:** append it to the ledger immediately (Step 4 helper) so a
crash/compaction never loses decisions.
````

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m pytest tests/test_grill_command.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add commands/grill.md tests/test_grill_command.py
git commit -m "feat(grill): interrogation contract — directives, codebase-first, stop/bound"
```

### Task 5: Capture + `/plan` handoff wiring

**Files:**

- Modify: `commands/grill.md`
- Test: `tests/test_grill_command.py`

**Interfaces:**

- Consumes: `grill_ledger.resolve_ledger_path`, `append_decision` (Tasks 1–2).
- Produces: a Step 4 (Capture) + Step 5 (Handoff) in the body that call the util and offer `/plan` tier 4 → ORCHESTRATE → `/do`.

- [ ] **Step 1: Write the failing test**

```python
def test_grill_body_captures_and_hands_off():
    body = open(os.path.join(CRAFT, "commands", "grill.md")).read()
    assert "grill_ledger" in body                       # uses the util, not ad-hoc writes
    assert "resolve_ledger_path" in body
    assert "/craft:plan" in body or "plan-orchestrator" in body   # handoff to the spine
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_grill_command.py::test_grill_body_captures_and_hands_off -v`
Expected: FAIL.

- [ ] **Step 3: Write minimal implementation**

````markdown
### Step 4: Capture (durable, collision-safe)

Resolve the output path with `commands/utils/grill_ledger.py`:

```python
from commands.utils.grill_ledger import resolve_ledger_path, append_decision
path, mode = resolve_ledger_path(topic, date, "docs/specs")
# mode "append" → add to an existing brainstorm SPEC; "create" → new GRILL-<topic>-<date>.md
```

Write the locked-decision ledger + an `## Open Questions` section. Never clobber a brainstorm
SPEC — append to it.

### Step 5: Handoff

Offer (one-directional into the planning spine, SPEC-B §4):
`/craft:plan` tier 4 (plan-orchestrator) → `ORCHESTRATE-*.md` → `/craft:do` / `/craft:orchestrate`.
````

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m pytest tests/test_grill_command.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add commands/grill.md tests/test_grill_command.py
git commit -m "feat(grill): durable capture via ledger util + /plan handoff"
```

---

## Wave 3 — Orchestrate optimize/refactor + Step 0.5 reuse

### Task 6: Split orchestrate into lean contract + reference doc

**Files:**

- Modify: `commands/orchestrate.md` (remove reference sections)
- Create: `commands/orchestrate/docs/orchestrate-reference.md`
- Test: `tests/test_orchestrate_refactor.py`

**Interfaces:**

- Produces: `orchestrate.md` retaining the full Step 0→3-N contract; reference (mockups, session mgmt, worktree types, swarm deep-config, perf tips, token instrumentation) moved out; a "See reference" pointer added.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_orchestrate_refactor.py
import os
CRAFT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_contract_preserved_and_reference_extracted():
    cmd = open(os.path.join(CRAFT, "commands", "orchestrate.md")).read()
    # contract steps must remain
    for marker in ["Step 0:", "Step 0.5", "Step 1:", "Step 2:", "Steps 3-N"]:
        assert marker in cmd, f"contract step missing: {marker}"
    ref = os.path.join(CRAFT, "commands", "orchestrate", "docs", "orchestrate-reference.md")
    assert os.path.exists(ref), "reference doc not created"
    # bulky reference moved OUT of the command
    assert "Token Instrumentation" not in cmd
    assert "Token Instrumentation" in open(ref).read()
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_orchestrate_refactor.py -v`
Expected: FAIL — reference doc missing / Step 0.5 absent.

- [ ] **Step 3: Implement the split**

Move these sections from `orchestrate.md` into `commands/orchestrate/docs/orchestrate-reference.md`:
status/timeline/budget/compression mockups · Session Management + history · Worktree Types + decision tree · Swarm deep config + swarm dry-run mockup · Performance Tips · Token Instrumentation · Control Commands catalog. Leave a one-line pointer in `orchestrate.md`:

```markdown
## Reference

Mockups, session management, worktree types, swarm deep config, performance tips, and token
instrumentation live in [orchestrate-reference.md](orchestrate/docs/orchestrate-reference.md).
```

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m pytest tests/test_orchestrate_refactor.py -v && bash scripts/command-audit.sh`
Expected: PASS; audit clean; verify `_discovery.py` does NOT count the reference doc as a command.

- [ ] **Step 5: Commit**

```bash
git add commands/orchestrate.md commands/orchestrate/docs/orchestrate-reference.md tests/test_orchestrate_refactor.py
git commit -m "refactor(orchestrate): split lean contract from reference doc"
```

### Task 7: Add Step 0.5 Clarify invoking bounded grill

**Files:**

- Modify: `commands/orchestrate.md`
- Test: `tests/test_orchestrate_refactor.py`

**Interfaces:**

- Consumes: grill `--bound` arg (Task 3).
- Produces: a Step 0.5 between mode-select and task-analysis that invokes `/craft:grill --bound 2` on ambiguous tasks; skips under `--yes`/`--no-clarify`/spec-derived.

- [ ] **Step 1: Write the failing test**

```python
def test_step_0_5_invokes_bounded_grill():
    cmd = open(os.path.join(CRAFT, "commands", "orchestrate.md")).read()
    assert "Step 0.5" in cmd
    assert "/craft:grill" in cmd and "bound" in cmd
    assert "--no-clarify" in cmd        # suppress path documented
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_orchestrate_refactor.py::test_step_0_5_invokes_bounded_grill -v`
Expected: FAIL.

- [ ] **Step 3: Implement Step 0.5**

```markdown
### Step 0.5: Clarify (default ON)

If the task is underspecified or admits multiple valid interpretations, invoke
`/craft:grill --bound 2` for a quick bounded interrogation that LOCKS the decisions
which change the plan — one question at a time, recommended answer per question,
codebase-first. Then build Step 1 on the locked answers.

SKIP when: `--yes` / `--no-clarify` passed, OR a matching SPEC/ORCHESTRATE/WORKFLOW
file pins the decisions, OR the task is unambiguous. Fallback if grill unavailable:
1–2 AskUserQuestion rounds, recommended-option-first.
```

Add `--no-clarify` to frontmatter args.

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m pytest tests/test_orchestrate_refactor.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add commands/orchestrate.md tests/test_orchestrate_refactor.py
git commit -m "feat(orchestrate): Step 0.5 Clarify via bounded /craft:grill"
```

---

## Wave 4 — grill-with-docs (G7) — DEFERRABLE

> Heavy: ADR + `CONTEXT.md` glossary maintained on the spot. Implement only after W1–W3 are green and merged. Single task; expand if adopted.

### Task 8: ADR + glossary on-the-spot capture (optional)

**Files:**

- Modify: `commands/grill.md`, `commands/utils/grill_ledger.py`
- Test: `tests/test_grill_ledger.py`

**Interfaces:**

- Produces: `append_adr(path, title, context, decision, consequences)` + `upsert_glossary(context_md_path, term, definition)`; grill body gains a Step 4b that calls them when an ADR dir / `CONTEXT.md` exists.

- [ ] **Step 1:** Write failing tests for `append_adr` (writes a numbered ADR block) and `upsert_glossary` (inserts or updates a term row, no duplicates).
- [ ] **Step 2:** Run — FAIL (functions absent).
- [ ] **Step 3:** Implement both in `grill_ledger.py` (stdlib only; glossary upsert = read, replace-or-append term line, write).
- [ ] **Step 4:** Run — PASS.
- [ ] **Step 5:** Commit `feat(grill): grill-with-docs ADR + glossary on-the-spot`.

---

## Wave 5 — Docs + count cascade + release prep

### Task 9: Documentation surface

**Files:**

- Create: `docs/tutorials/TUTORIAL-grill.md`, `docs/help/grill.md`, `docs/commands/grill.md`
- Modify: `docs/REFCARD.md`, `commands/smart-help.md`, `mkdocs.yml`, `docs/skills-agents.md`

- [ ] **Step 1:** Write the tutorial (grill vs brainstorm; worked example: grill a spec → ledger → handoff).
- [ ] **Step 2:** Add help + command-reference pages; REFCARD row; smart-help entry; mkdocs nav; skills-agents catalog row.
- [ ] **Step 3:** Run `python3 -m pytest tests/ -k "broken_links or hub_discovery" -v` → PASS.
- [ ] **Step 4:** Commit `docs(grill): tutorial, help, reference, nav`.

### Task 10: Count cascade + CHANGELOG

**Files:**

- Modify: `plugin.json` (`(N craft)` subtotal — manual), CHANGELOG.md + docs/CHANGELOG.md (`[Unreleased]`), the ~14 bump-version count files, ~29 doc refs.

- [ ] **Step 1:** Run `./scripts/validate-counts.sh` → note 113→114 drift.
- [ ] **Step 2:** Run bump-version count sweep; manually bump `plugin.json (N craft)` subtotal; `--fix` doc staleness for the ~29 refs.
- [ ] **Step 3:** Add CHANGELOG `[Unreleased]` entry (grill command + orchestrate refactor).
- [ ] **Step 4:** Run full suite: `python3 -m pytest tests/ -q` → all pass; `./scripts/validate-counts.sh` clean; `./scripts/docs-staleness-check.sh` clean.
- [ ] **Step 5:** Commit `chore(grill): count cascade + CHANGELOG`.

---

## Self-Review

**Spec coverage (SPEC-grill-command):**

- G1 standalone command → Task 3 ✓
- G2 one-at-a-time + AskUserQuestion-exception justified → Task 4 (test asserts both) ✓
- G3 codebase-first read-then-confirm → Task 4 ✓
- G4 artifact-or-topic input → Task 4 Step 1 ✓
- G5 grill-vs-brainstorm header distinction → Task 3 body + Task 4 ✓
- G6 decision-ledger spec → `/plan` handoff → Tasks 1–2, 5 ✓
- G7 grill-with-docs → Task 8 (deferrable W4) ✓
- G8 orchestrate Step 0.5 invokes grill → Task 7 ✓
- Review bug #1 (filename collision) → Task 1 ✓
- Review bug #2 (stop signal) → Task 4 (`--stop`/`stop`) ✓
- Review bug #3 (`--bound`) → Task 3 frontmatter + Task 7 ✓
- Review bug #4 (loop untestable) → handled honestly: structure + util tested, live loop model-executed (documented in Architecture) ✓
- Orchestrate optimize/refactor → Task 6 ✓
- Count cascade → Task 10 ✓

**Placeholder scan:** none — every code/test step carries real content; Task 8 (deferrable) uses summarized steps by design and is gated out of the critical path.

**Type consistency:** `resolve_ledger_path` / `append_decision` signatures match between Tasks 1–2 (definition) and Task 5 (use). `--bound` named consistently in Tasks 3 and 7.

## Execution Handoff

Implementation is code → requires a `feature/*` worktree (never on `dev`). Per workflow rules I will not create one unprompted.

Two execution options once a worktree exists:

1. **Subagent-Driven (recommended)** — fresh subagent per task, two-stage review between tasks.
2. **Inline Execution** — batch tasks in one session with checkpoints (`superpowers:executing-plans`).
