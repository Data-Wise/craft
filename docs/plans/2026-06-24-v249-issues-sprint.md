# v2.49.x Issues Sprint Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close GitHub issues #200, #199, #183, #171 and wire the skill-standards auditor into `/craft:check`, shipped as one coordinated `v2.49.1` release.

**Architecture:** Four independent units land on `dev`, then a single release cut. Tracks 0 (quick-wins) and 1 (skill-standards validator) commit directly to `dev` (`.md` + validator skill only — branch-guard permits). Tracks A (homebrew gates) and B (insights hook) are feature code → each needs its own `feature/*` worktree and its own Claude session (built in parallel per D10). No track depends on another's code.

**Tech Stack:** Python 3 (stdlib only — no new deps), Bash hooks, Ruby Homebrew formulae (parsed, never executed destructively), craft's hot-reload validator framework, pytest.

**Source artifacts:** [SPEC-v249-issues-sprint-2026-06-23.md](../specs/SPEC-v249-issues-sprint-2026-06-23.md) · [GRILL-v249-issues-sprint-2026-06-23.md](../specs/GRILL-v249-issues-sprint-2026-06-23.md) (10 locked decisions D1–D10).

## Global Constraints

- **No new runtime dependencies** — Python stdlib only; Bash hooks fall back to Python3 when `jq` is absent.
- **Branch model:** Tracks 0 & 1 → direct to `dev`. Tracks A & B → `feature/*` worktree, separate session each. `main` is PR-only.
- **Gate severity (D3/D4):** skill-standards validator = advisory (never exit 1). aggregator-sync gate = blocking (exit 1). caveats/post_install gates = advisory by default, strict under `HOMEBREW_GATE_STRICT=1`.
- **Hook event (D5):** the insights hook registers on `SessionEnd` (NOT the non-existent "SessionStop", NOT `Stop`). Dedup keys on session id, not date.
- **No count cascade:** `scripts/` and `~/.claude/hooks/` are excluded from hub auto-discovery; new validator skill under `.claude-plugin/skills/validation/` is a validator, not a command — confirm `validate-counts.sh` stays green, no `(N commands)` bump.
- **Audit exit codes:** `scripts/skill_standards_audit.py` returns 0=clean, 1=findings, 2=error. The advisory validator converts 1→warning and returns 0; a 2 (engine error) surfaces but still must not fail the check run.
- **Issue close (D7):** quick-win commit carries `Closes #171`; the `dev→main` `v2.49.1` release PR body MUST also carry `Closes #171` (squash can drop per-commit trailers; auto-close fires only on merge to `main`).
- **Every commit message** ends with the `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` trailer.

---

## TRACK 0 — Quick Wins (direct to `dev`, no worktree)

### Task 0.1: Fix the false "automatic" insights claim

**Files:**

- Modify: `commands/workflow/insights.md` (the line claiming collection is automatic)
- Modify: `docs/commands/workflow/insights.md` (mirror)

**Interfaces:**

- Consumes: nothing.
- Produces: nothing (doc-only).

- [ ] **Step 1: Locate the exact false claim**

Run: `grep -n "automatic" commands/workflow/insights.md`
Expected: a line asserting facets are collected automatically (spec cites line ~62).

- [ ] **Step 2: Rewrite the claim to be accurate**

Replace the sentence asserting automatic collection with the true state until PR B ships:

```markdown
Facets are written when you run `/craft:workflow:done`. Once the SessionEnd
facet hook (issue #183) is installed, a lower-fidelity skeleton facet is also
written automatically at the end of every session — see the insights setup tutorial.
```

- [ ] **Step 3: Mirror the change in the docs copy**

Apply the identical edit to `docs/commands/workflow/insights.md`.

- [ ] **Step 4: Verify docs staleness check still passes**

Run: `./scripts/docs-staleness-check.sh`
Expected: exit 0, no new findings.

- [ ] **Step 5: Commit (folded into the Track-0 commit at Task 0.3)**

Do not commit yet — Track 0's three tasks share one commit (Step at Task 0.3 Step 4).

---

### Task 0.2: Write ADR-001 (decision-only) and close #171

**Files:**

- Create: `docs/adr/ADR-001-workflow-branch-guard.md`

**Interfaces:**

- Consumes: nothing.
- Produces: a permanent decision record referenced by TUTORIAL/ORCHESTRATE docs.

- [ ] **Step 1: Create the `docs/adr/` directory and ADR file**

Create `docs/adr/ADR-001-workflow-branch-guard.md` with exactly this content (decision-only per spec line 253 — no Task-vs-Workflow table, no migration guide):

```markdown
# ADR-001: Workflow() Tool vs Worktree Branch Model

**Status:** Accepted
**Date:** 2026-06-24
**Issue:** #171

## Context

Claude Code's `Workflow()` tool spawns in-session agents that inherit the parent
session's CWD. When the parent session is on `dev`, branch-guard blocks new code
files in all spawned agents. `isolation: 'worktree'` creates ephemeral worktrees
(no persistent branch), incompatible with the craft `feature/*` branch model.

## Decision

`Workflow()` is safe for READ operations from `dev` sessions (research, audit,
analysis). Feature code writes use the ORCHESTRATE protocol: plan on `dev` →
create a `feature/*` worktree → commit the ORCHESTRATE file → start a new session
in the worktree. No change to branch-guard or Workflow semantics.

## Alternatives Considered

1. `isolation: 'worktree'` per `agent()` call — rejected: ephemeral, no branch name, state discarded at session end.
2. Workflow-aware branch-guard bypass — rejected: the safety invariant exists for correctness, not policy.
3. Pre-create a worktree then call Workflow from `dev` — rejected: agents inherit the calling session's CWD, not the worktree path.
4. Disable Workflow on `dev` entirely — rejected: too restrictive for read-only use.

## Consequences

Constraint formally documented. No code added. Usage guidance stays in TUTORIAL
and ORCHESTRATE docs. Issue #171 closed by this record.
```

- [ ] **Step 2: Add the ADR to mkdocs nav (if an ADR section is absent, create one)**

Run: `grep -n "adr\|ADR" mkdocs.yml`
If no ADR nav entry exists, add under the existing reference/docs nav section:

```yaml
  - Architecture Decisions:
    - ADR-001 Workflow vs Worktree: adr/ADR-001-workflow-branch-guard.md
```

- [ ] **Step 3: Verify the doc builds and link-checks**

Run: `mkdocs build 2>&1 | grep -iE "warn|error" || echo "clean"`
Expected: `clean` (no broken-link or nav warnings for the new file).

- [ ] **Step 4: Commit — deferred to Task 0.3** (shared Track-0 commit).

---

### Task 0.3: Document the `@local-plugins` qualifier as the only form + commit Track 0

**Files:**

- Modify: `skills/release/references/release-checklist.md` (or the release runbook doc that documents `claude plugin update`)

**Interfaces:**

- Consumes: nothing.
- Produces: the canonical Cowork/Desktop update instruction reused by PR A Step 10d.

- [ ] **Step 1: Find every documented `claude plugin update` invocation**

Run: `grep -rn "claude plugin update" skills/ docs/ commands/ | grep -v "@local-plugins"`
Expected: any bare-name occurrences are the drift to fix.

- [ ] **Step 2: Rewrite each bare invocation to the qualified form**

Replace `claude plugin update <name>` with:

```bash
# Cowork/Desktop and local Code both require the marketplace-qualified name:
claude plugin marketplace update local-plugins   # refresh cache FIRST (else update no-ops)
claude plugin update <name>@local-plugins
```

- [ ] **Step 3: Verify markdown lints clean**

Run: `python3 -m pytest tests/test_craft_plugin.py -k "broken_links" -q`
Expected: PASS.

- [ ] **Step 4: Commit all of Track 0**

```bash
git add commands/workflow/insights.md docs/commands/workflow/insights.md \
        docs/adr/ADR-001-workflow-branch-guard.md mkdocs.yml \
        skills/release/references/release-checklist.md
git commit -m "$(cat <<'EOF'
chore(docs): fix insights false-auto claim + ADR-001 + release runbook @local-plugins

Closes #171

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

Note: `Closes #171` fires only when this reaches `main`; ensure the `v2.49.1` release PR body repeats it.

---

## TRACK 1 — skill-standards Validator (direct to `dev`, advisory)

### Task 1.1: Create the advisory skill-standards validation skill

**Files:**

- Create: `.claude-plugin/skills/validation/skill-standards-check.md`
- Test: `tests/test_skill_standards_validator.py`

**Interfaces:**

- Consumes: `scripts/skill_standards_audit.py` (CLI: `--root`, `--json`; exit 0=clean,1=findings,2=error).
- Produces: a hot-reload validator discovered by `/craft:check`; emits a box-drawing report; **always exits 0** (advisory).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_skill_standards_validator.py
import subprocess, sys, os, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / ".claude-plugin/skills/validation/skill-standards-check.md"

def _impl_block(md_text):
    # extract the first ```bash fenced block under "## Implementation"
    import re
    m = re.search(r"## Implementation\s+```bash\n(.*?)```", md_text, re.S)
    assert m, "no bash Implementation block found"
    return m.group(1)

def test_validator_skill_exists_with_hotreload_frontmatter():
    text = VALIDATOR.read_text()
    assert "hot_reload: true" in text
    assert "category: validation" in text
    assert "context: fork" in text

def test_validator_is_advisory_never_exits_one(tmp_path):
    # Run the implementation against a skills root that has a deliberately
    # non-compliant SKILL.md; the validator must report but exit 0.
    bad = tmp_path / "skills" / "bad"
    bad.mkdir(parents=True)
    (bad / "SKILL.md").write_text("# no frontmatter at all\n")
    script = tmp_path / "run.sh"
    script.write_text(_impl_block(VALIDATOR.read_text()))
    env = {**os.environ, "SKILL_STANDARDS_ROOT": str(tmp_path / "skills")}
    r = subprocess.run(["bash", str(script)], capture_output=True, text=True, env=env)
    assert r.returncode == 0, f"advisory validator must exit 0, got {r.returncode}: {r.stderr}"
    assert "skill" in (r.stdout + r.stderr).lower()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python3 -m pytest tests/test_skill_standards_validator.py -v`
Expected: FAIL — validator file does not exist yet.

- [ ] **Step 3: Create the validator skill with grounded frontmatter + implementation**

Create `.claude-plugin/skills/validation/skill-standards-check.md`:

````markdown
---
name: check:skill-standards
description: Audit skills/**/SKILL.md against Anthropic's skill standards (advisory — reports score, never fails the check)
category: validation
context: fork
hot_reload: true
version: 1.0.0
dependencies:
  - python3
  - scripts/skill_standards_audit.py
---

# Skill Standards Validator (Advisory)

Audit every `skills/**/SKILL.md` against the vendored Anthropic skill standards
(`docs/reference/SKILL-STANDARDS.md`) via `scripts/skill_standards_audit.py`.
**Advisory only**: it surfaces sub-39 skills as warnings but never fails
`/craft:check`. Graduation to a blocking gate follows the governance warn→error
soak path once the ecosystem stays clean.

## What This Checks

Per-skill frontmatter completeness, size limits, naming hygiene, and version-tag
cleanliness — the same rules `/craft:code:skill-standards` enforces. Reports an
aggregate score and lists any skill below 100.

## Mode Behavior

| Mode | What runs | Exit on findings |
|------|-----------|------------------|
| default | audit all SKILL.md, print summary | **0 (advisory)** |
| debug | same + per-skill score table | **0 (advisory)** |
| release | same | **0 (advisory)** — never blocks |

## Implementation

```bash
#!/bin/bash
set -uo pipefail

# Resolve craft root (BASH_SOURCE when sourced, else walk up from PWD).
ROOT="${CRAFT_ROOT:-}"
if [ -z "$ROOT" ]; then
  d="$PWD"
  while [ "$d" != "/" ] && [ ! -f "$d/.claude-plugin/plugin.json" ]; do d="$(dirname "$d")"; done
  ROOT="$d"
fi
AUDIT="$ROOT/scripts/skill_standards_audit.py"
SKILLS_ROOT="${SKILL_STANDARDS_ROOT:-$ROOT/skills}"

if [ ! -f "$AUDIT" ]; then
  echo "⚠️  skill-standards: audit script not found ($AUDIT) — skipping (advisory)"
  exit 0
fi

OUT="$(python3 "$AUDIT" --root "$SKILLS_ROOT" 2>&1)"; CODE=$?
echo "╭─ skill-standards (advisory) ────────────────────────╮"
printf '%s\n' "$OUT" | sed 's/^/│ /'
case "$CODE" in
  0) echo "│ ✅ all skills compliant"                        ;;
  1) echo "│ ⚠️  findings above — advisory, not blocking"     ;;
  2) echo "│ ⚠️  audit engine error — advisory, not blocking" ;;
esac
echo "╰─────────────────────────────────────────────────────╯"
exit 0   # advisory: never propagate the audit's exit code
```
````

- [ ] **Step 4: Run the test to verify it passes**

Run: `python3 -m pytest tests/test_skill_standards_validator.py -v`
Expected: PASS (both tests).

- [ ] **Step 5: Confirm `/craft:check` discovers it and counts stay green**

Run: `./scripts/validate-counts.sh && grep -rl "hot_reload: true" .claude-plugin/skills/validation/ | grep skill-standards`
Expected: counts clean; the new validator file is listed.

- [ ] **Step 6: Commit**

```bash
git add .claude-plugin/skills/validation/skill-standards-check.md tests/test_skill_standards_validator.py
git commit -m "$(cat <<'EOF'
feat(check): advisory skill-standards validator (hot-reload, never blocks)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

## TRACK A — PR A `feature/homebrew-dist-gates` (worktree, own session)

> Build in a `feature/homebrew-dist-gates` worktree, started by the user when ready. Closes #200, #199.

### Task A.1: `verify_caveats.py` — Checks 1–4 (D8 signature)

**Files:**

- Create: `scripts/verify_caveats.py`
- Test: `tests/test_homebrew_gates.py`

**Interfaces:**

- Consumes: a formula path, a CHANGELOG path, a version string.
- Produces: `verify_caveats(formula_path, changelog_path, version, strict=False, formula_name=None) -> GateReport` where `GateReport` is a `dataclass(ok: bool, findings: list[str])`. (D8: single entry, no `run_all_gates`, no Check 5.)

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_homebrew_gates.py
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
from verify_caveats import verify_caveats

FORMULA_STALE = '''class Foo < Formula
  def caveats
    <<~EOS
      New in v2.48.0:
      # --- dynamic bullets ---
      - old feature
      # --- end dynamic bullets ---
    EOS
  end
  def post_install
    begin
      system "x"
    rescue => e
      opoo e.message
    end
  end
end
'''
CHANGELOG = "## [2.49.0]\n- new shiny feature\n- second feature\n"

def test_version_string_mismatch_is_a_finding(tmp_path):
    f = tmp_path / "foo.rb"; f.write_text(FORMULA_STALE)
    c = tmp_path / "CHANGELOG.md"; c.write_text(CHANGELOG)
    rep = verify_caveats(str(f), str(c), "2.49.0")
    assert not rep.ok
    assert any("v2.49.0" in x for x in rep.findings)

def test_advisory_default_returns_findings_not_exception(tmp_path):
    f = tmp_path / "foo.rb"; f.write_text(FORMULA_STALE)
    c = tmp_path / "CHANGELOG.md"; c.write_text(CHANGELOG)
    rep = verify_caveats(str(f), str(c), "2.49.0", strict=False)
    assert isinstance(rep.findings, list)

def test_missing_changelog_section_fails_loudly(tmp_path):
    f = tmp_path / "foo.rb"; f.write_text(FORMULA_STALE.replace("2.48.0", "2.49.0"))
    c = tmp_path / "CHANGELOG.md"; c.write_text("## [9.9.9]\n- unrelated\n")
    rep = verify_caveats(str(f), str(c), "2.49.0")
    assert not rep.ok
    assert any("no CHANGELOG entry" in x.lower() for x in rep.findings)

def test_no_dynamic_markers_falls_back_to_version_check_only(tmp_path):
    no_markers = FORMULA_STALE.replace("# --- dynamic bullets ---", "").replace("# --- end dynamic bullets ---", "").replace("2.48.0", "2.49.0")
    f = tmp_path / "foo.rb"; f.write_text(no_markers)
    c = tmp_path / "CHANGELOG.md"; c.write_text(CHANGELOG)
    rep = verify_caveats(str(f), str(c), "2.49.0")
    assert rep.ok  # version string present, no marker zone to diff
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m pytest tests/test_homebrew_gates.py -v`
Expected: FAIL — `verify_caveats` module missing.

- [ ] **Step 3: Implement `scripts/verify_caveats.py`**

```python
#!/usr/bin/env python3
"""Caveats-staleness gate for Homebrew formulae (Checks 1-3; Check 4 brew audit
lives in the shell wrapper). D8: single entry point, no Check 5."""
import re, sys, argparse
from dataclasses import dataclass, field

@dataclass
class GateReport:
    ok: bool
    findings: list = field(default_factory=list)

def _caveats_block(text):
    m = re.search(r"def caveats\b(.*?)\n\s*end\b", text, re.S)
    return m.group(1) if m else ""

def _managed_bullets(block):
    m = re.search(r"# --- dynamic bullets ---(.*?)# --- end dynamic bullets ---", block, re.S)
    if not m:
        return None  # signal: no marker zone
    return [ln.strip("- ").strip() for ln in m.group(1).splitlines() if ln.strip().startswith("-")]

def _changelog_items(changelog_text, version):
    m = re.search(rf"##\s*\[?{re.escape(version)}\]?.*?\n(.*?)(?:\n##\s|\Z)", changelog_text, re.S)
    if not m:
        return None  # signal: no section
    return [ln.strip("- ").strip() for ln in m.group(1).splitlines() if ln.strip().startswith("-")]

def verify_caveats(formula_path, changelog_path, version, strict=False, formula_name=None):
    findings = []
    text = open(formula_path, encoding="utf-8").read()
    block = _caveats_block(text)

    # Check 1: version string present
    if f"New in v{version}" not in block:
        findings.append(f"caveats missing 'New in v{version}:' header")

    # Check 3 prerequisite: structural post_install (begin/rescue/end)
    pi = re.search(r"def post_install\b(.*?)\n\s*end\b", text, re.S)
    if pi and not re.search(r"\bbegin\b.*?\brescue\b.*?\bend\b", pi.group(1), re.S):
        findings.append("post_install lacks begin/rescue/end guard")

    # Check 2: managed bullets vs CHANGELOG
    bullets = _managed_bullets(block)
    items = _changelog_items(open(changelog_path, encoding="utf-8").read(), version)
    if items is None:
        findings.append(f"no CHANGELOG entry for v{version}")
    elif bullets is not None and set(bullets) != set(items):
        findings.append(f"caveats bullets differ from CHANGELOG v{version}: {set(items) ^ set(bullets)}")
    # bullets is None => no marker zone => version-check only (no false positive)

    return GateReport(ok=not findings, findings=findings)

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("formula"); p.add_argument("changelog"); p.add_argument("version")
    p.add_argument("--strict", action="store_true"); p.add_argument("--name")
    a = p.parse_args(argv)
    rep = verify_caveats(a.formula, a.changelog, a.version, a.strict, a.name)
    for f in rep.findings:
        print(f"⚠️  {f}")
    if rep.ok:
        print("✅ caveats current"); return 0
    return 1 if a.strict else 0   # advisory unless --strict

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run to verify pass**

Run: `python3 -m pytest tests/test_homebrew_gates.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/verify_caveats.py tests/test_homebrew_gates.py
git commit -m "feat(dist): verify_caveats gate (checks 1-3, advisory/strict)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task A.2: `post_install_check.py` — structural always + sandbox opt-in (D6)

**Files:**

- Create: `scripts/post_install_check.py`
- Test: `tests/test_homebrew_gates.py` (append)

**Interfaces:**

- Consumes: a formula path; optional `--sandbox` flag.
- Produces: `check_post_install(formula_path, sandbox=False) -> GateReport` (reuses `GateReport` imported from `verify_caveats`). Structural check asserts `begin/rescue/end`, that `marketplace update` textually precedes `plugin update`, and that `libexec` paths appear. Sandbox mode (opt-in, macOS-local) runs the block under a `HOME`-redirected temp dir.

- [ ] **Step 1: Write the failing tests**

```python
# append to tests/test_homebrew_gates.py
from post_install_check import check_post_install

GOOD_PI = '''class Foo < Formula
  def post_install
    begin
      system "claude", "plugin", "marketplace", "update", "local-plugins"
      system "claude", "plugin", "update", "foo@local-plugins"
      (libexec/"x").install "y"
    rescue => e
      opoo e.message
    end
  end
end
'''
BAD_ORDER_PI = GOOD_PI.replace(
  'system "claude", "plugin", "marketplace", "update", "local-plugins"\n      system "claude", "plugin", "update", "foo@local-plugins"',
  'system "claude", "plugin", "update", "foo@local-plugins"\n      system "claude", "plugin", "marketplace", "update", "local-plugins"')

def test_structural_pass_on_correct_ordering(tmp_path):
    f = tmp_path / "g.rb"; f.write_text(GOOD_PI)
    assert check_post_install(str(f)).ok

def test_structural_flags_update_before_marketplace_refresh(tmp_path):
    f = tmp_path / "b.rb"; f.write_text(BAD_ORDER_PI)
    rep = check_post_install(str(f))
    assert not rep.ok
    assert any("marketplace update" in x for x in rep.findings)
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m pytest tests/test_homebrew_gates.py -k post_install -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Implement `scripts/post_install_check.py`**

```python
#!/usr/bin/env python3
"""post_install gate: structural always; sandbox execution opt-in (macOS-local)."""
import re, sys, argparse, os, tempfile, subprocess
from verify_caveats import GateReport

def check_post_install(formula_path, sandbox=False):
    findings = []
    text = open(formula_path, encoding="utf-8").read()
    m = re.search(r"def post_install\b(.*?)\n\s*end\b", text, re.S)
    if not m:
        return GateReport(False, ["no post_install block found"])
    body = m.group(1)
    if not re.search(r"\bbegin\b.*?\brescue\b.*?\bend\b", body, re.S):
        findings.append("post_install lacks begin/rescue/end guard")
    mk = body.find("marketplace")
    up = re.search(r'plugin",?\s*"?update|plugin update', body)
    up_idx = up.start() if up else -1
    if mk == -1:
        findings.append("post_install missing 'marketplace update' refresh (stale-cache bug class)")
    elif up_idx != -1 and mk > up_idx:
        findings.append("'marketplace update' must precede 'plugin update' (ordering bug)")
    if "libexec" not in body:
        findings.append("post_install references no libexec path")
    if sandbox and findings == []:
        if sys.platform != "darwin":
            findings.append("(sandbox skipped: not macOS)")
        else:
            with tempfile.TemporaryDirectory() as home:
                env = {**os.environ, "HOME": home}
                # Dry structural-only invocation; do NOT call brew install for real.
                # Sandbox proves the block parses + runs without touching real ~/.claude.
                r = subprocess.run(["ruby", "-c", formula_path], capture_output=True, text=True, env=env)
                if r.returncode != 0:
                    findings.append(f"ruby syntax check failed in sandbox: {r.stderr.strip()}")
    return GateReport(not findings, findings)

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("formula"); p.add_argument("--sandbox", action="store_true")
    p.add_argument("--strict", action="store_true")
    a = p.parse_args(argv)
    rep = check_post_install(a.formula, a.sandbox)
    for f in rep.findings: print(f"⚠️  {f}")
    if rep.ok: print("✅ post_install structurally sound"); return 0
    return 1 if a.strict else 0

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run to verify pass**

Run: `python3 -m pytest tests/test_homebrew_gates.py -k post_install -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/post_install_check.py tests/test_homebrew_gates.py
git commit -m "feat(dist): post_install structural gate + sandbox opt-in

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task A.3: Wire gates + aggregator-sync (blocking) + Steps 10b/c/d into the release path

**Files:**

- Modify: `commands/dist/homebrew.md` (add Step 10b verify-caveats, 10c post_install, 10d Cowork verify)
- Modify: `skills/release/SKILL.md` (Step 10a sub-gate, post-url/sha256, pre-tap-push)
- Modify: `scripts/post-release-sweep.sh` (add a caveats-staleness phase, advisory)
- Test: `tests/test_homebrew_gates.py` (append a wiring smoke test)

**Interfaces:**

- Consumes: `verify_caveats.py`, `post_install_check.py`, `scripts/aggregator-sync.sh`.
- Produces: release-pipeline steps. **aggregator-sync is BLOCKING (exit 1)** per D4; caveats/post_install are advisory unless `HOMEBREW_GATE_STRICT=1`. Tap-absent leg warns only (spec risk #1).

- [ ] **Step 1: Write the failing wiring test**

```python
# append to tests/test_homebrew_gates.py
import pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent

def test_release_path_documents_blocking_aggregator_and_advisory_gates():
    hb = (ROOT / "commands/dist/homebrew.md").read_text()
    assert "verify_caveats.py" in hb and "Step 10b" in hb
    assert "post_install_check.py" in hb and "Step 10c" in hb
    assert "aggregator-sync" in hb and ("exit 1" in hb or "BLOCKING" in hb)
    assert "@local-plugins" in hb and "Step 10d" in hb

def test_caveats_gate_is_advisory_by_default_strict_via_env():
    hb = (ROOT / "commands/dist/homebrew.md").read_text()
    assert "HOMEBREW_GATE_STRICT" in hb
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m pytest tests/test_homebrew_gates.py -k "release_path or advisory_by_default" -v`
Expected: FAIL — steps not yet documented.

- [ ] **Step 3: Add Steps 10b–10d to `commands/dist/homebrew.md`** (insert after the existing Step 10a)

````markdown
### Step 10b: Verify caveats freshness (advisory; strict via env)

```bash
python3 scripts/verify_caveats.py "$FORMULA" CHANGELOG.md "$VERSION" \
  ${HOMEBREW_GATE_STRICT:+--strict} --name "$PLUGIN_NAME"
# Tap-absent leg: if "$FORMULA" is not locally checked out, warn and continue
# (ubuntu CI has no local tap) — never block on absence.
```

### Step 10c: Verify post_install structure (advisory; strict via env)

```bash
python3 scripts/post_install_check.py "$FORMULA" \
  ${HOMEBREW_GATE_STRICT:+--strict}
# Add --sandbox only on a macOS-local release host for higher fidelity.
```

### Step 10d: Cowork/Desktop verification (BLOCKING aggregator-sync)

```bash
# BLOCKING (D4): a stale aggregator ships silent wrong-version installs.
bash scripts/aggregator-sync.sh || { echo "❌ aggregator-sync failed — release blocked"; exit 1; }

echo "Verify on Cowork/Desktop after publish:"
echo "  claude plugin marketplace update local-plugins"
echo "  claude plugin update $(jq -r .name .claude-plugin/plugin.json)@local-plugins"
echo "  Expected version: $(jq -r .version .claude-plugin/plugin.json)"
```
````

- [ ] **Step 4: Add the advisory caveats phase to `scripts/post-release-sweep.sh`**

Append a phase that runs `verify_caveats.py` against the released tap formula and prints findings to the sweep report (advisory — sweep never blocks).

- [ ] **Step 5: Run to verify pass + full gate suite**

Run: `python3 -m pytest tests/test_homebrew_gates.py -v`
Expected: PASS (all gate + wiring tests, ≥6 total per acceptance criteria).

- [ ] **Step 6: Commit**

```bash
git add commands/dist/homebrew.md skills/release/SKILL.md scripts/post-release-sweep.sh tests/test_homebrew_gates.py
git commit -m "feat(dist): wire caveats+post_install advisory gates + blocking aggregator-sync (10b/c/d)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task A.4: Docs, tutorial, and PR

**Files:**

- Create: `docs/tutorials/TUTORIAL-homebrew-gates.md`
- Modify: `docs/commands/dist/homebrew.md` (mirror Steps 10b–10d)
- Modify: `docs/REFCARD.md` (gate flags section)

- [ ] **Step 1: Write the tutorial** covering the three gates, `HOMEBREW_GATE_STRICT`, the blocking aggregator-sync, and the tap-absent warn-only rule. No placeholders — show each command and its expected advisory vs strict output.

- [ ] **Step 2: Mirror Steps 10b–10d** into `docs/commands/dist/homebrew.md`.

- [ ] **Step 3: Verify docs + counts**

Run: `./scripts/docs-staleness-check.sh && ./scripts/validate-counts.sh`
Expected: both exit 0.

- [ ] **Step 4: Commit and open PR A**

```bash
git add docs/tutorials/TUTORIAL-homebrew-gates.md docs/commands/dist/homebrew.md docs/REFCARD.md
git commit -m "docs(dist): homebrew gates tutorial + command-ref + refcard

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
gh pr create --base dev --title "feat(dist): homebrew dist-gates (#200, #199)" --body "$(cat <<'EOF'
Caveats + post_install advisory gates, blocking aggregator-sync, Cowork verify (Steps 10b/c/d).

Closes #200, #199

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## TRACK B — PR B `feature/insights-session-hook` (worktree, own session, parallel to A)

> Build in a `feature/insights-session-hook` worktree. Closes #183.

### Task B.1: `session-facet.sh` — SessionEnd hook with per-session-id dedup (D5/D9)

**Files:**

- Create: `hooks/session-facet.sh` (in-repo source of truth per D9)
- Test: `tests/test_session_stop_hook.py`

**Interfaces:**

- Consumes: SessionEnd stdin JSON (`.cwd`, `.session_id`).
- Produces: a skeleton facet `session-<session_id-or-timestamp>.json` in `~/.claude/usage-data/facets/`, written once per session. Dedup: skip if a facet whose name encodes THIS session id already exists (handles the `/done`-already-ran case). **Open question carried from grill:** `/done` currently writes timestamp-named facets with no `session_id`; until that's reconciled, the guard also checks a per-session marker `~/.claude/sessions/active/<session_id>.faceted`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_session_stop_hook.py
import subprocess, json, os, pathlib, tempfile

HOOK = pathlib.Path(__file__).resolve().parent.parent / "hooks/session-facet.sh"

def _run(stdin_obj, home):
    env = {**os.environ, "HOME": str(home)}
    return subprocess.run(["bash", str(HOOK)], input=json.dumps(stdin_obj),
                          capture_output=True, text=True, env=env)

def test_writes_facet_on_session_end(tmp_path):
    r = _run({"cwd": str(tmp_path), "session_id": "abc123"}, tmp_path)
    assert r.returncode == 0
    facets = list((tmp_path / ".claude/usage-data/facets").glob("session-*.json"))
    assert len(facets) == 1
    data = json.loads(facets[0].read_text())
    assert data["session_id"] == "abc123"
    assert data["auto_collected"] is True

def test_no_double_write_for_same_session(tmp_path):
    _run({"cwd": str(tmp_path), "session_id": "abc123"}, tmp_path)
    _run({"cwd": str(tmp_path), "session_id": "abc123"}, tmp_path)
    facets = list((tmp_path / ".claude/usage-data/facets").glob("session-*.json"))
    assert len(facets) == 1  # second SessionEnd for same session is a no-op

def test_distinct_sessions_each_get_a_facet_same_day(tmp_path):
    _run({"cwd": str(tmp_path), "session_id": "s1"}, tmp_path)
    _run({"cwd": str(tmp_path), "session_id": "s2"}, tmp_path)
    facets = list((tmp_path / ".claude/usage-data/facets").glob("session-*.json"))
    assert len(facets) == 2  # per-session, NOT per-day

def test_exits_zero_without_jq_or_git(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", "/usr/bin:/bin")  # minimal; hook must self-fallback
    r = _run({"cwd": "/nonexistent", "session_id": "x"}, tmp_path)
    assert r.returncode == 0
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m pytest tests/test_session_stop_hook.py -v`
Expected: FAIL — hook missing.

- [ ] **Step 3: Implement `hooks/session-facet.sh`** (clones `done-reminder.sh` stdin pattern)

```bash
#!/bin/bash
# session-facet.sh — SessionEnd hook. Writes a low-fidelity skeleton facet once
# per session so insights have a baseline even without /done. Per-session-id
# dedup (D5): skip if this session already has a facet/marker. Silent, exit 0.

INPUT=$(cat 2>/dev/null)
sid() { printf '%s' "$INPUT" | jq -r '.session_id // empty' 2>/dev/null \
        || printf '%s' "$INPUT" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("session_id",""))' 2>/dev/null; }
cwdv() { printf '%s' "$INPUT" | jq -r '.cwd // empty' 2>/dev/null \
        || printf '%s' "$INPUT" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("cwd",""))' 2>/dev/null; }

SESSION_ID="$(sid)"; CWD="$(cwdv)"
[ -z "$SESSION_ID" ] && SESSION_ID="$(date +%Y%m%d-%H%M%S)-$$"
[ -z "$CWD" ] && CWD="$PWD"

FACETS="${SESSION_FACETS:-$HOME/.claude/usage-data/facets}"
MARKERS="$HOME/.claude/sessions/active"
mkdir -p "$FACETS" "$MARKERS"

# Dedup (D5 + grill open-question fallback): this session already captured?
[ -f "$MARKERS/$SESSION_ID.faceted" ] && exit 0
ls "$FACETS"/session-"$SESSION_ID".json >/dev/null 2>&1 && exit 0

PROJECT="$(basename "$CWD" 2>/dev/null || echo unknown)"
BRANCH="$(git -C "$CWD" branch --show-current 2>/dev/null || echo "")"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

cat > "$FACETS/session-$SESSION_ID.json" <<EOF
{
  "session_id": "$SESSION_ID",
  "timestamp": "$TS",
  "project": "$PROJECT",
  "branch": "$BRANCH",
  "goal_category": "unknown",
  "outcome": "session-end",
  "friction_events": [],
  "auto_collected": true
}
EOF
touch "$MARKERS/$SESSION_ID.faceted"
exit 0
```

- [ ] **Step 4: Run to verify pass**

Run: `python3 -m pytest tests/test_session_stop_hook.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add hooks/session-facet.sh tests/test_session_stop_hook.py
git commit -m "feat(workflow): SessionEnd facet hook (per-session dedup)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task B.2: Installer + settings registration (D9)

**Files:**

- Modify: `scripts/install-guards.sh` (or create `scripts/install-session-facet.sh` if guards installer is guard-specific)
- Test: `tests/test_session_stop_hook.py` (append an install smoke test)

**Interfaces:**

- Consumes: `hooks/session-facet.sh` (in-repo).
- Produces: copies the hook to `~/.claude/hooks/` and registers a `SessionEnd` entry in `~/.claude/settings.json` (idempotent — no duplicate entries on re-run).

- [ ] **Step 1: Write the failing install test**

```python
# append to tests/test_session_stop_hook.py
import shutil

INSTALLER = pathlib.Path(__file__).resolve().parent.parent / "scripts/install-session-facet.sh"

def test_installer_registers_sessionend_idempotently(tmp_path):
    home = tmp_path; (home / ".claude/hooks").mkdir(parents=True)
    (home / ".claude/settings.json").write_text('{"hooks":{}}')
    env = {**os.environ, "HOME": str(home)}
    for _ in range(2):  # run twice — must stay idempotent
        subprocess.run(["bash", str(INSTALLER)], capture_output=True, text=True, env=env, check=True)
    settings = json.loads((home / ".claude/settings.json").read_text())
    se = json.dumps(settings["hooks"].get("SessionEnd", []))
    assert "session-facet.sh" in se
    assert se.count("session-facet.sh") == 1  # idempotent
    assert (home / ".claude/hooks/session-facet.sh").exists()
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m pytest tests/test_session_stop_hook.py -k installer -v`
Expected: FAIL — installer missing.

- [ ] **Step 3: Implement `scripts/install-session-facet.sh`**

```bash
#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$HOME/.claude/hooks/session-facet.sh"
SETTINGS="$HOME/.claude/settings.json"
mkdir -p "$HOME/.claude/hooks"
cp "$ROOT/hooks/session-facet.sh" "$DEST"; chmod +x "$DEST"

# Register SessionEnd idempotently via python3 (stdlib JSON).
python3 - "$SETTINGS" "$DEST" <<'PY'
import json, sys, os
settings_path, hook_path = sys.argv[1], sys.argv[2]
s = json.load(open(settings_path)) if os.path.exists(settings_path) else {}
hooks = s.setdefault("hooks", {})
arr = hooks.setdefault("SessionEnd", [])
flat = json.dumps(arr)
if "session-facet.sh" not in flat:
    arr.append({"hooks": [{"type": "command", "command": hook_path}]})
json.dump(s, open(settings_path, "w"), indent=2)
PY
echo "✅ session-facet SessionEnd hook installed + registered"
```

- [ ] **Step 4: Run to verify pass**

Run: `python3 -m pytest tests/test_session_stop_hook.py -k installer -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/install-session-facet.sh tests/test_session_stop_hook.py
git commit -m "feat(workflow): idempotent installer for SessionEnd facet hook

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task B.3: Insights tutorial note + PR

**Files:**

- Modify: `docs/tutorials/TUTORIAL-insights-setup.md` (add the SessionEnd hook install + behavior note)

- [ ] **Step 1: Document the hook** — how to install (`bash scripts/install-session-facet.sh`), that it writes a shallow facet per session, and the hook-vs-`/done` fidelity table (shallow/no-AI vs rich/AI). The `insights.md:62` claim was already corrected in Track 0.

- [ ] **Step 2: Verify docs**

Run: `./scripts/docs-staleness-check.sh`
Expected: exit 0.

- [ ] **Step 3: Commit and open PR B**

```bash
git add docs/tutorials/TUTORIAL-insights-setup.md
git commit -m "docs(workflow): SessionEnd facet hook setup note

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
gh pr create --base dev --title "feat(workflow): SessionEnd facet hook (#183)" --body "$(cat <<'EOF'
Automatic shallow facet collection at session end; per-session dedup with /done.

Closes #183

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## RELEASE — single `v2.49.1` cut (after all four units merge to `dev`)

- [ ] Run the full suite: `python3 -m pytest tests/ -q` — confirm pass count, zero failures.
- [ ] `./scripts/pre-release-check.sh 2.49.1` (expects files already bumped — run `bump-version.sh` first).
- [ ] Dual-CHANGELOG `[Unreleased]` → `[2.49.1] — <date>`; mirror root + `docs/CHANGELOG.md`.
- [ ] `gh pr create --base main --head dev --title "Release: v2.49.1"` — **PR body includes `Closes #200 #199 #183 #171`** (so auto-close fires on merge to `main`).
- [ ] After merge: GitHub release tag, tap sync, post-release sweep (now includes the new advisory caveats phase), brew upgrade verify, Cowork `claude plugin update <name>@local-plugins` verify.

---

## Self-Review

**Spec coverage:** #200 → Task A.1/A.2/A.3. #199 → Task A.3 (aggregator-sync blocking + Step 10d). #183 → Track B. #171 → Task 0.2 + release PR body. skill-standards wiring → Track 1. Acceptance criteria "≥6 test cases in test_homebrew_gates.py" → A.1 (4) + A.2 (2) + A.3 (2) = 8. "≥4 in test_session_stop_hook.py" → B.1 (4) + B.2 (1) = 5. ✅

**Open dependencies (carried from grill, not gaps):** per-session `session_id` reconciliation between the hook and `/done` (Task B.1 interface note — resolved here via the `~/.claude/sessions/active/<sid>.faceted` marker fallback); `verify-caveats.sh` project-contract versioning (spec risk #2 — version the marker format if a project wrapper is later added); sandbox fidelity caveat (A.2 — proves "parses/runs," not "does the right thing").

**Type consistency:** `GateReport(ok, findings)` defined in `verify_caveats.py`, imported by `post_install_check.py` — single definition, no drift. `verify_caveats(formula_path, changelog_path, version, strict, formula_name)` signature matches D8 and is called identically in Step 10b. `check_post_install(formula_path, sandbox)` consistent across test and impl.

**Placeholder scan:** every code step carries real code; every command step carries the exact command + expected result. No TBD/TODO/"handle edge cases".
