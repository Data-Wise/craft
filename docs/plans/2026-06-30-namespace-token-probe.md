# Namespace Refactor Token-Cost Probe — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Answer, with real token counts (not estimates), whether consolidating craft's flat
commands into fewer top-level entries with sub-actions (per
`docs/specs/SPEC-refactor-namespace-2026-06-29.md`) would reduce session-start token cost — then
append a go/no-go recommendation to that spec. This plan does not implement the namespace refactor.

**Architecture:** A standalone, disposable Python script builds two synthetic frontmatter sets
(flat vs. consolidated) representative of craft's actual `docs/*.md` commands, counts tokens with
a real tokenizer, and prints a comparison. No changes to `commands/`, no `namespace.json`, no file
moves.

**Tech Stack:** Python 3, `tiktoken` (installed disposably, not added to `pyproject.toml`).

## Global Constraints

- **Working directory:** `/Users/dt/projects/dev-tools/craft` on `dev` (this is doc/research work,
  not a feature branch — no worktree needed; `.md`/`.py` scratch files under a `scratch/` dir are
  fine on `dev` per branch-guard rules for non-`commands/` paths, but verify with
  `git branch --show-current` first regardless).
- The probe script and its synthetic fixture files are **disposable** — delete them in the final
  task. Only the recommendation addendum to `SPEC-refactor-namespace-2026-06-29.md` is committed.
- `tiktoken`'s `cl100k_base` encoding is an approximation of Claude's actual tokenizer (Claude uses
  a different vocabulary), but it's a real, consistent tokenizer — good enough for a *relative*
  comparison between two layouts, which is what this probe needs. State this caveat in the
  recommendation addendum.

---

### Task 1: Build the synthetic frontmatter fixtures

**Files:**

- Create: `scratch/namespace-probe/flat_layout.py`
- Create: `scratch/namespace-probe/consolidated_layout.py`

**Interfaces:**

- Produces: `FLAT_FRONTMATTERS: list[str]` (one YAML frontmatter block per file, `flat_layout.py`)
- Produces: `CONSOLIDATED_FRONTMATTER: str` (one YAML frontmatter block with sub-action
  descriptions inlined, `consolidated_layout.py`)

- [ ] **Step 1: Pull the real frontmatter for the 10 `docs/*` commands the namespace spec proposes consolidating**

```bash
cd /Users/dt/projects/dev-tools/craft
for f in docs/guide docs/quickstart docs/website docs/update docs/sync docs/nav-update docs/changelog docs/check docs/check-links docs/lint; do
  echo "=== commands/$f.md ==="
  sed -n '/^---$/,/^---$/p' "commands/$f.md" 2>/dev/null | head -10
done
```

Use this output to populate `flat_layout.py`'s `FLAT_FRONTMATTERS` list — one real
`name`/`description`/`category` block per file (10 entries total), verbatim from what's actually
in the repo. Do not paraphrase the descriptions; copy them exactly, since description length is
what's being measured.

- [ ] **Step 2: Write `flat_layout.py`**

```python
# scratch/namespace-probe/flat_layout.py
"""Real frontmatter for the 10 docs/* commands SPEC-refactor-namespace-2026-06-29.md
proposes consolidating. Pulled verbatim from commands/docs/*.md on 2026-06-30."""

FLAT_FRONTMATTERS = [
    # Paste each of the 10 real frontmatter blocks here as triple-quoted strings,
    # exactly as found in Step 1's output. Example shape (replace with real content):
    """---
name: docs-guide
description: <exact description from commands/docs/guide.md>
category: docs
---""",
    # ... 9 more, one per file
]

assert len(FLAT_FRONTMATTERS) == 10, f"expected 10 fixtures, got {len(FLAT_FRONTMATTERS)}"
```

- [ ] **Step 3: Write `consolidated_layout.py`**

Build the equivalent consolidated frontmatter per the namespace spec's proposed `docs: init`
sub-action structure — one top-level `name`/`description` block whose description enumerates the
sub-actions, matching the spec's `### docs: 17 → 5 with sub-actions` table.

```python
# scratch/namespace-probe/consolidated_layout.py
"""Synthetic consolidated frontmatter per SPEC-refactor-namespace-2026-06-29.md's
proposed docs: 17->5 sub-action structure, scoped to the same 10 commands as
flat_layout.py for a fair comparison."""

CONSOLIDATED_FRONTMATTER = """---
name: docs
description: Documentation operations. Sub-actions — init: scaffold docs for a project type (replaces guide, quickstart, website); sync: pull latest, update nav and changelog (replaces update, sync, nav-update, changelog); check: validate links, lint, coverage (replaces check, check-links, lint).
category: docs
---"""
```

- [ ] **Step 4: Verify both fixture files import cleanly**

```bash
cd /Users/dt/projects/dev-tools/craft
python3 -c "from scratch.namespace_probe.flat_layout import FLAT_FRONTMATTERS; print(len(FLAT_FRONTMATTERS))"
# Expected: 10
python3 -c "from scratch.namespace_probe.consolidated_layout import CONSOLIDATED_FRONTMATTER; print(len(CONSOLIDATED_FRONTMATTER))"
# Expected: a positive integer (character count)
```

(Note: Python package imports need `__init__.py` or `-m` invocation with dots — if the bare
import fails, create an empty `scratch/namespace-probe/__init__.py` and `scratch/__init__.py`, or
just run the scripts directly with `python3 scratch/namespace-probe/flat_layout.py` plus a `print`
at the bottom instead of importing. Either works; pick whichever has fewer moving parts.)

- [ ] **Step 5: No commit yet** — this is scratch content, committed only if Task 4 decides to keep
the script (unlikely; default is delete per Task 5).

---

### Task 2: Count tokens for both layouts with a real tokenizer

**Files:**

- Create: `scratch/namespace-probe/count_tokens.py`

**Interfaces:**

- Consumes: `FLAT_FRONTMATTERS` from `flat_layout.py`, `CONSOLIDATED_FRONTMATTER` from
  `consolidated_layout.py`
- Produces: prints `flat_total`, `consolidated_total`, `delta`, `delta_pct` to stdout

- [ ] **Step 1: Install tiktoken disposably**

```bash
pip install --user tiktoken
python3 -c "import tiktoken; print('ok')"
```

Expected: `ok`. (If `pip install --user` fails due to an externally-managed environment, use
`pip install --user --break-system-packages tiktoken` or a throwaway venv — do not add tiktoken to
`pyproject.toml`, this is disposable tooling.)

- [ ] **Step 2: Write the counting script**

```python
# scratch/namespace-probe/count_tokens.py
import tiktoken
from flat_layout import FLAT_FRONTMATTERS
from consolidated_layout import CONSOLIDATED_FRONTMATTER

enc = tiktoken.get_encoding("cl100k_base")

def count(text: str) -> int:
    return len(enc.encode(text))

flat_total = sum(count(fm) for fm in FLAT_FRONTMATTERS)
consolidated_total = count(CONSOLIDATED_FRONTMATTER)

delta = flat_total - consolidated_total
delta_pct = (delta / flat_total) * 100 if flat_total else 0.0

print(f"Flat layout (10 separate frontmatter blocks): {flat_total} tokens")
print(f"Consolidated layout (1 block, sub-actions inlined): {consolidated_total} tokens")
print(f"Delta: {delta} tokens ({delta_pct:.1f}% {'reduction' if delta > 0 else 'increase'})")
```

- [ ] **Step 3: Run it and record the actual output**

```bash
cd /Users/dt/projects/dev-tools/craft/scratch/namespace-probe
python3 count_tokens.py
```

Record the exact printed numbers — these are the real measurement this whole track exists to
produce. Do not round or approximate when transcribing into Task 4's addendum.

- [ ] **Step 4: Sanity-check the direction**

If `delta` is negative (consolidated costs *more* tokens than flat), that's a real, valid, and
notable result — don't second-guess the tokenizer or rerun hoping for a different answer. A
negative delta would mean the consolidated description (which has to enumerate all sub-actions in
one string) costs more than N small separate descriptions, contradicting the namespace spec's
implicit assumption. Report whatever the number actually is.

---

### Task 3: Scale the result to the full proposed consolidation

**Files:**

- No new files — pure arithmetic on Task 2's output, documented inline in Task 4's addendum.

- [ ] **Step 1: Compute the per-command average delta**

```
per_command_delta = delta / 10  # from Task 2's 10-command sample
```

- [ ] **Step 2: Project to the full namespace spec's scope**

The namespace spec proposes consolidating `docs` (17→5) and `site` (15→4) — 32 commands total
collapsing into 9. Using the per-command average from Step 1:

```
projected_total_delta = per_command_delta * 32
```

State this projection explicitly as an extrapolation from a 10-command sample, not a second
measurement — flag the uncertainty (different commands have different description lengths; this
assumes the 10 sampled `docs/*` commands are representative of the other 22).

- [ ] **Step 3: No commit** — this is arithmetic feeding directly into Task 4.

---

### Task 4: Write the recommendation addendum to SPEC-refactor-namespace-2026-06-29.md

**Files:**

- Modify: `docs/specs/SPEC-refactor-namespace-2026-06-29.md` (append new section at end of file)

**Interfaces:** None.

- [ ] **Step 1: Append the addendum**

Append to the end of `docs/specs/SPEC-refactor-namespace-2026-06-29.md`, after the existing
"Implementation Notes" section:

```markdown

---

## Addendum (2026-06-30): Token-Cost Go/No-Go

**Source:** `docs/plans/2026-06-30-namespace-token-probe.md`, run against the 10 `docs/*` commands
this spec proposes consolidating.

**Method:** real frontmatter for 10 commands, tokenized with `tiktoken` (`cl100k_base` — an
approximation of Claude's actual tokenizer, used for a *relative* comparison between layouts, not
an absolute Claude token count) — flat (10 separate blocks) vs. consolidated (1 block, sub-actions
enumerated in the description).

**Result:** [FILL IN FROM TASK 2's ACTUAL OUTPUT — do not estimate]
- Flat layout: `<flat_total>` tokens
- Consolidated layout: `<consolidated_total>` tokens
- Delta: `<delta>` tokens (`<delta_pct>`% `<reduction|increase>`)
- Projected across the full `docs`+`site` consolidation (32→9 commands, extrapolated from this
  10-command sample): `<projected_total_delta>` tokens

**Recommendation:** [Choose one based on the actual measured result, not a default]
- If delta is meaningfully positive (>10% reduction) and the projection is non-trivial in
  absolute terms: **Proceed with Workstream B (docs/site consolidation) as a real priority**, not
  the "optional, can be a follow-up" status the spec currently assigns it.
- If delta is small (<10%) or negative: **Shelve Workstream B** (consolidation) — the always-loaded
  frontmatter cost isn't where the structural-bloat argument pays off in tokens; Workstream A
  (namespace.json index, replacing `_discovery.py`) and Workstream C (CI enforcement) can still
  proceed on their original structural-clarity/drift-prevention merits, independent of this token
  question.

**Caveat:** this measures only session-start frontmatter cost, not the structural-bloat,
routing-ambiguity, or cross-repo-dedup motivations the rest of this spec is built on — those may
independently justify consolidation regardless of this result.
```

- [ ] **Step 2: Fill in the bracketed placeholders with Task 2/3's real numbers**

This step has no example code because the values are data, not logic — copy them verbatim from
Task 2's stdout and Task 3's arithmetic. Do not leave any `<...>` placeholder unfilled.

- [ ] **Step 3: Verify no placeholders remain**

```bash
cd /Users/dt/projects/dev-tools/craft
grep -n "<.*>" docs/specs/SPEC-refactor-namespace-2026-06-29.md
```

Expected: no output (or only matches unrelated to this addendum, e.g. existing angle-bracket
syntax elsewhere in the file like `<command-name>`).

- [ ] **Step 4: Commit**

```bash
cd /Users/dt/projects/dev-tools/craft
git branch --show-current
# Must print: dev
git add docs/specs/SPEC-refactor-namespace-2026-06-29.md
git commit -m "docs(specs): add token-cost go/no-go addendum to namespace refactor spec

Measured (not estimated) frontmatter token cost for flat vs.
consolidated command layouts on a 10-command sample, per
docs/plans/2026-06-30-namespace-token-probe.md. Recommendation: see
the addendum's Recommendation section for the actual call, scaled to
this measurement's result."
```

---

### Task 5: Clean up the disposable probe

**Files:**

- Delete: `scratch/namespace-probe/` (entire directory)

- [ ] **Step 1: Confirm the addendum is committed before deleting anything**

```bash
cd /Users/dt/projects/dev-tools/craft
git log -1 --oneline -- docs/specs/SPEC-refactor-namespace-2026-06-29.md
```

Must show Task 4's commit. Do not proceed if it doesn't.

- [ ] **Step 2: Delete the scratch directory**

```bash
rm -rf /Users/dt/projects/dev-tools/craft/scratch/namespace-probe
git -C /Users/dt/projects/dev-tools/craft status -s
```

Expected: clean (the scratch dir was never committed, so nothing shows in git status after
deletion — if it does show as a deletion, that means it was accidentally committed in an earlier
task; remove it from git history with `git rm -r --cached` instead of leaving a tracked deletion).

- [ ] **Step 3: Uninstall the disposable tiktoken dependency (optional cleanup)**

```bash
pip uninstall -y tiktoken
```

Skip this step if other work on the machine depends on tiktoken already being installed — check
before uninstalling.

---

## Done Signal

- [ ] Real (not estimated) token counts recorded for both layouts
- [ ] Recommendation addendum committed to `SPEC-refactor-namespace-2026-06-29.md`
- [ ] No `namespace.json`, no file moves, no command consolidation implemented
- [ ] Scratch probe files deleted
