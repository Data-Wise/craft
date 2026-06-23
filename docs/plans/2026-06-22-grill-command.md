# `/craft:grill` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Status:** ✅ SHIPPED — v2.48.0 (PR #201 → dev 2727c576, PR #202 → main 4dea8ac8, 2026-06-23). W1–W3 + W5 complete. W4 (ADR + CONTEXT.md glossary) deferred as fast-follow.

**Goal:** Add `/craft:grill` — a standalone one-question-at-a-time interrogation command that stress-tests a spec/plan or bare topic, walking the design tree with a recommended answer per question, codebase-first, capturing a durable decision-ledger spec that feeds the `/plan → /do` pipeline.

**Architecture:** A markdown command (`commands/grill.md`) carrying the interrogation contract, backed by one Python util (`commands/utils/grill_ledger.py`) for collision-safe output-filename resolution + decision-ledger append. The interactive loop itself is model-executed (not Python); its *structure* and the *util* are the testable surfaces. Orchestrate's Step 0.5 reuses grill via a bounded pass.

**Tech Stack:** craft plugin conventions (markdown commands + `commands/utils/*.py`), Python 3 stdlib only, pytest harness (`tests/`), bump-version + validate-counts for the count cascade.

## Global Constraints

- Branch model: code on `feature/*` worktree only; never new code files on `dev`/`main`. (verbatim: `~/.claude/CLAUDE.md`)
- Strict plugin.json schema — no unrecognized frontmatter keys. (memory: claude-code-plugin-json-strict-schema)
- No `execSync`; use `execFileSync`. Python utils: stdlib only, POSIX-portable (BSD/GNU sed parity not relevant here; no shelling out needed).
- Adding ONE command triggers the ~30-file count cascade: ~14 bump-version files + `plugin.json (N craft)` subtotal (manual) + ~29 doc refs + Phase 8 doc entry. (memory: adding-a-command-cascades-30-file-count-bump)
- Frontmatter list-value descriptions containing a colon must be quoted (command-audit uses real YAML).
- Current version baseline: v2.47.0; counts 113 / 39 / 8 → grill makes it 115 commands.
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

- Produces (decision: grill ALWAYS owns its file; never mutates a brainstorm `SPEC-*`):
  - `resolve_ledger_path(topic, date, specs_dir) -> str` — always `GRILL-<slug>-<date>.md`, with `<slug>` filesystem-sanitized (no path traversal).
  - `spec_crosslink(topic, specs_dir) -> str | None` — filename of the **latest** brainstorm `SPEC-<slug>-*.md` (glob by slug, newest mtime — not date-coupled) for grill's header forward-link, else None.
  - `add_backlink(spec_path, grill_filename) -> None` — idempotent, **atomic** one-line back-link into the SPEC (the only touch grill makes to a brainstorm artifact; never rewrites its body).
  - All file I/O uses `with` + `encoding="utf-8"` and atomic `os.replace` writes (em-dash/arrow glyphs + crash-safety).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_grill_ledger.py
import os, tempfile, time
from commands.utils.grill_ledger import (
    resolve_ledger_path, spec_crosslink, add_backlink, _slug)

def test_always_owns_a_grill_file():
    with tempfile.TemporaryDirectory() as d:
        # even when a brainstorm SPEC exists, grill writes its OWN file
        open(os.path.join(d, "SPEC-auth-2026-06-22.md"), "w", encoding="utf-8").write("# spec\n")
        assert resolve_ledger_path("auth", "2026-06-22", d) == \
            os.path.join(d, "GRILL-auth-2026-06-22.md")

def test_slug_sanitizes_path_and_special_chars():
    assert _slug("Auth / OAuth!!") == "auth-oauth"
    assert _slug("../../etc/passwd") == "etc-passwd"      # no traversal
    assert "/" not in os.path.basename(resolve_ledger_path("a/b", "2026-06-22", "/tmp"))
    assert _slug("") == "untitled"                        # never empty

def test_crosslink_finds_latest_across_dates():
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "SPEC-auth-2026-06-20.md"), "w", encoding="utf-8").write("x")
        time.sleep(0.01)
        open(os.path.join(d, "SPEC-auth-2026-06-22.md"), "w", encoding="utf-8").write("x")
        assert spec_crosslink("auth", d) == "SPEC-auth-2026-06-22.md"   # latest, not same-date
        assert spec_crosslink("missing", d) is None

def test_backlink_is_idempotent_and_atomic():
    with tempfile.TemporaryDirectory() as d:
        spec = os.path.join(d, "SPEC-auth-2026-06-22.md")
        open(spec, "w", encoding="utf-8").write("# spec\n")
        add_backlink(spec, "GRILL-auth-2026-06-22.md")
        add_backlink(spec, "GRILL-auth-2026-06-22.md")
        # the filename appears twice per backlink line ([text](url)); assert ONE backlink line
        assert open(spec, encoding="utf-8").read().count("> Interrogated by grill") == 1
        assert not os.path.exists(spec + ".tmp")          # atomic write cleaned up
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_grill_ledger.py -v`
Expected: FAIL — `ModuleNotFoundError: commands.utils.grill_ledger`

- [ ] **Step 3: Write minimal implementation**

```python
# commands/utils/grill_ledger.py
"""Ledger path + cross-link helpers for /craft:grill.

grill ALWAYS owns GRILL-<slug>-<date>.md and never rewrites a brainstorm SPEC body.
The only touch to a SPEC is an idempotent, atomic one-line back-link.
"""
import glob
import os
import re

_BACKLINK = "> Interrogated by grill — see [{name}]({name})\n"


def _slug(topic):
    """Filesystem-safe slug: lowercase, [a-z0-9] runs → '-', no traversal, capped."""
    s = re.sub(r"[^a-z0-9]+", "-", str(topic).strip().lower()).strip("-")
    return (s or "untitled")[:60]


def _atomic_write(path, text):
    """Write via temp + os.replace so a crash never leaves a truncated file."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def resolve_ledger_path(topic, date, specs_dir):
    """Always return grill's own file path; never the brainstorm SPEC."""
    return os.path.join(specs_dir, f"GRILL-{_slug(topic)}-{date}.md")


def spec_crosslink(topic, specs_dir):
    """Return the latest brainstorm SPEC filename for this slug (any date), or None."""
    matches = glob.glob(os.path.join(specs_dir, f"SPEC-{_slug(topic)}-*.md"))
    if not matches:
        return None
    return os.path.basename(max(matches, key=os.path.getmtime))


def add_backlink(spec_path, grill_filename):
    """Insert an idempotent, atomic one-line back-link into the SPEC (no body rewrite)."""
    with open(spec_path, encoding="utf-8") as f:
        body = f.read()
    if grill_filename in body:
        return
    _atomic_write(spec_path, body.rstrip("\n") + "\n\n" + _BACKLINK.format(name=grill_filename))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_grill_ledger.py -v`
Expected: PASS (3 passed)

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
        open(p, "w", encoding="utf-8").write("# Grill: x\n")
        append_decision(p, "G1", "Form factor", "Standalone command")
        append_decision(p, "G2", "Interaction", "One-at-a-time")
        body = open(p, encoding="utf-8").read()
        assert body.count("## Decision Ledger") == 1
        assert body.count("| # | Branch | Decision |") == 1
        assert "| G1 | Form factor | Standalone command |" in body
        assert "| G2 | Interaction | One-at-a-time |" in body

def test_append_decision_escapes_pipes_and_newlines():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "GRILL-x-2026-06-22.md")
        open(p, "w", encoding="utf-8").write("# x\n")
        append_decision(p, "G1", "Syntax", "use a | b\nform")
        row = [l for l in open(p, encoding="utf-8").read().splitlines() if l.startswith("| G1")][0]
        assert r"use a \| b form" in row            # pipe escaped, newline flattened
        assert row.count("|") - row.count(r"\|") == 4   # 4 UNescaped delimiters → table intact
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_grill_ledger.py::test_append_decision_creates_section_then_rows -v`
Expected: FAIL — `ImportError: cannot import name 'append_decision'`

- [ ] **Step 3: Write minimal implementation**

```python
LEDGER_HEADER = "## Decision Ledger\n\n| # | Branch | Decision |\n|---|---|---|\n"


def _cell(text):
    """Escape a value for a markdown table cell (pipe + newline safe)."""
    return str(text).replace("\\", "\\\\").replace("|", r"\|").replace("\n", " ").strip()


def append_decision(path, branch_id, branch, decision):
    body = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            body = f.read()
    if "## Decision Ledger" not in body:
        if body and not body.endswith("\n"):
            body += "\n"
        body += "\n" + LEDGER_HEADER
    body += f"| {_cell(branch_id)} | {_cell(branch)} | {_cell(decision)} |\n"
    _atomic_write(path, body)        # reuse the atomic writer from Task 1
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
    # command-audit.sh is a bash script; invoke via bash from the repo root
    r = subprocess.run(["bash", os.path.join(CRAFT, "scripts", "command-audit.sh")],
                       cwd=CRAFT, capture_output=True, text=True)
    combined = (r.stdout + r.stderr).lower()
    # no audit ERROR line should mention grill
    assert not any("error" in line and "grill" in line
                   for line in combined.splitlines()), combined
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
  - name: no-capture
    description: "Skip writing a GRILL spec file; return decisions inline (used by embedded callers like orchestrate Step 0.5)"
    required: false
    default: false
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
    assert "/done" in body                                    # distinct halt sentinel (not "stop")
    assert "milestone" in body.lower()                        # ADHD-friendly progress checkpoints
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

**Halt:** the user enters the sentinel `/done` (or empty-enter) at any question → go to Step 4.
Do NOT use the bare word "stop" — it can be a legitimate answer. If `--bound N` was given, stop
after N resolved branches. Otherwise continue until every branch resolves.

**Milestone checkpoints (ADHD-friendly):** every 5 resolved branches, pause with an
AskUserQuestion: "keep going / wrap up now / show ledger so far" (reuses brainstorm's milestone
pattern). This is the ONE place embedded AskUserQuestion is allowed inside the otherwise
free-text loop — for progress, not for the questions themselves.

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
### Step 4: Capture (durable, own file, cross-linked)

**If `--no-capture` (embedded callers like orchestrate Step 0.5):** skip all file writes; return the
locked decisions inline to the caller. No `GRILL-*` file is created.

Otherwise grill writes its own file and never rewrites a brainstorm SPEC body:

```python
from commands.utils.grill_ledger import (
    resolve_ledger_path, spec_crosslink, add_backlink, append_decision)
path = resolve_ledger_path(topic, date, "docs/specs")        # GRILL-<topic>-<date>.md
link = spec_crosslink(topic, "docs/specs")                   # latest brainstorm SPEC for this slug, or None
# write GRILL header (include `link` if present), the decision ledger, and an ## Open Questions section
if link:
    add_backlink(os.path.join("docs/specs", link), os.path.basename(path))  # idempotent, atomic
```

Each resolved branch is appended live via `append_decision` (Task 2). The brainstorm SPEC, if any,
is only ever touched by the single idempotent back-link.

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
    assert "--no-capture" in cmd        # embedded grill must not write a spec file
    assert "--no-clarify" in cmd        # suppress path documented
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_orchestrate_refactor.py::test_step_0_5_invokes_bounded_grill -v`
Expected: FAIL.

- [ ] **Step 3: Implement Step 0.5**

```markdown
### Step 0.5: Clarify (default ON)

If the task is underspecified or admits multiple valid interpretations, invoke
`/craft:grill --bound 2 --no-capture` for a quick bounded interrogation that LOCKS the
decisions which change the plan — one question at a time, recommended answer per
question, codebase-first. `--no-capture` keeps it from writing a GRILL spec file mid-
orchestration; decisions return inline. Then build Step 1 on the locked answers.

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
- Review bug #1 (filename collision) → Task 1: grill owns `GRILL-*`, never mutates the brainstorm SPEC; idempotent back-link only ✓
- Review bug #2 (stop signal) → Task 4 (`stop` token + `--bound`) ✓
- Review bug #3 (`--bound`) → Task 3 frontmatter + Task 7 ✓
- Review bug #4 (loop untestable) → handled honestly: structure + util tested, live loop model-executed (documented in Architecture) ✓
- Review bug #5 (`--yes` defeats interrogation) → **dropped** — grill is always interactive; the bounded orchestrate pass uses `--bound`, not auto-accept ✓

**Full-stack hardening pass (round 2):**

- #1 UTF-8 + `with` on all I/O → Task 1/2 ✓
- #2 filename sanitization (no path traversal) → `_slug`, Task 1 + test ✓
- #3 markdown-table pipe/newline escaping → `_cell`, Task 2 + test ✓
- #4 atomic writes (`_atomic_write` + `os.replace`) → Task 1/2, crash-safety claim now real ✓
- #5 cross-link decoupled from date (glob latest) → `spec_crosslink(topic, specs_dir)`, Task 1 + test ✓
- #6 embedded grill side-effect → `--no-capture` arg, Tasks 3/4/7 ✓
- #7 embedded interaction mode documented → spec G9 ✓
- #8 milestone UX + `/done` sentinel → spec G10, Task 4 + test ✓

- Orchestrate optimize/refactor → Task 6 ✓
- Count cascade → Task 10 ✓

**Placeholder scan:** none — every code/test step carries real content; Task 8 (deferrable) uses summarized steps by design and is gated out of the critical path.

**Type consistency:** `resolve_ledger_path(topic, date, specs_dir) -> str`, `spec_crosslink(topic, specs_dir) -> str|None`, `add_backlink(spec_path, grill_filename)`, `append_decision(path, branch_id, branch, decision)` — signatures match between Tasks 1–2 (definition) and Task 5 (use); Task 5 calls `spec_crosslink(topic, "docs/specs")` (2-arg). Shared helpers `_atomic_write`/`_cell`/`_slug` live in `grill_ledger.py`. `--bound`/`--no-capture` named consistently across Tasks 3/4/7. No `--yes` references remain.

## Execution Handoff

Implementation is code → requires a `feature/*` worktree (never on `dev`). Per workflow rules I will not create one unprompted.

**Chosen execution model: subagent-driven, sequential** (`superpowers:subagent-driven-development`) — fresh subagent per task, two-stage review between tasks, in task order. Rationale: `grill.md` is a shared file across Tasks 3–5 and the count cascade (Task 10) must run last, so swarm parallelism's convergence overhead isn't worth it at ~10 small tasks. Run waves in order; W4 (grill-with-docs) is optional and gated out of the critical path.
