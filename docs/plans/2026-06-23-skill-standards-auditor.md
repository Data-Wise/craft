# Skill Standards Auditor Implementation Plan

**Status:** ✅ SHIPPED — `/craft:code:skill-standards` command landed v2.49.0 (PR #203); advisory validator in `/craft:check` v2.50.0; graduated to release-tier gate v2.51.0 (PR #212). Checkboxes below left un-ticked at ship time (tracked via .STATUS). NOTE: `SPEC-skill-standards-auditor-2026-06-23.md` still reads "not implemented" — that status line is stale; the command is live.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `/craft:code:skill-standards` — a batch scanner that audits every `skills/**/SKILL.md` against a vendored copy of Anthropic's authoring standards, reports gaps, and applies only safe mechanical fixes.

**Architecture:** A stdlib-only Python scanner (`scripts/skill_standards_audit.py`) mirrors `scripts/command-audit.sh` (scan → per-file checks → score → exit 0/1/2). It reuses `commands/_discovery.py:parse_yaml_frontmatter`. A vendored `docs/reference/SKILL-STANDARDS.md` is the human-facing checklist; the script carries the machine constants. A thin command surface (`commands/code/skill-standards.md`) wraps it. Deep work (description rewrites, evals) is delegated to the installed `skill-creator` and `plugin-dev:skill-reviewer` — never reimplemented.

**Tech Stack:** Python 3 stdlib (`re`, `argparse`, `json`, `pathlib`) — no new dependencies. pytest for tests. Bash pre-commit/markdownlint as elsewhere.

## Spec Audit (gaps found → resolved in this plan)

The source spec is `docs/specs/SPEC-skill-standards-auditor-2026-06-23.md`. Auditing it surfaced six gaps, each resolved below:

1. **Parser reuse confirmed** — `parse_yaml_frontmatter(content: str) -> dict` (`commands/_discovery.py:33`) is generic; works on SKILL.md. No adapter needed.
2. **Valid-keys allowlist was undefined** — spec said "no unrecognized keys" but Anthropic recently added many. Task 2 defines `VALID_SKILL_KEYS` (current full set); unknown keys are a **WARNING**, not an error (the set evolves).
3. **Fuzzy checks must be WARNING-only** — third-person/second-person detection is heuristic; emit as warnings, never errors, so CI/pre-commit never breaks on a false positive.
4. **`--refresh-standards` cannot auto-synthesize prose** in a deterministic script. Split: the *script* `--refresh-standards` only rewrites the provenance block (source URLs + today's date + installed skill-creator path). The *command* (`.md`, model-executed) performs the actual prose synthesis. (Task 7.)
5. **Count cascade** — adding one command cascades ~30 files. Task 8 handles bump-version, the `plugin.json` `(100 craft → 101 craft)` subtotal, doc refs, and the Phase 8 entry.
6. **Non-gating first cut** — the command is standalone; it is NOT wired into `ci.yml`/pre-commit initially (39 legacy skills will have real gaps; gating would break builds). Revisit after triage.

## Global Constraints

- Python 3 **stdlib only** — no new dependencies (matches craft scripts).
- Reuse `commands/_discovery.py:parse_yaml_frontmatter` and its `SKILLS_DIR` (`commands/_discovery.py:30`); do not write a second frontmatter parser.
- **Report-only by default**; mutations only under `--fix`, and only the safe mechanical set in Task 6.
- Heuristic checks (description voice, reference voice) are **WARNING** severity only.
- Scoring + exit codes match `command-audit.sh`: `score = 100 − errors*5 − warnings*2`; exit `0` clean, `1` warnings only, `2` any error.
- **Execution requires a `feature/skill-standards` worktree** (new `.py` files are blocked on `dev` by branch-guard). Create it with superpowers:using-git-worktrees at execution time — NOT during planning.
- Description voice/value checks **never auto-fix** — hand off to `skill-creator run_loop.py`.

## File Structure

- `scripts/skill_standards_audit.py` — scanner: constants, checks, scoring, output, argparse, `--fix`, `--refresh-standards`. One file (mirrors the single-file `command-audit.sh`).
- `docs/reference/SKILL-STANDARDS.md` — vendored human-facing checklist + provenance header. Data, not code.
- `commands/code/skill-standards.md` — command surface (frontmatter + steps), house style of `commands/code/command-audit.md`.
- `tests/test_skill_standards.py` — unit tests (tmp_path skill fixtures) + structural tests.
- Doc surfaces: `docs/tutorials/TUTORIAL-skill-standards.md`, `docs/REFCARD.md`, `CHANGELOG.md`, `mkdocs.yml`.

---

### Task 1: Scanner skeleton — constants + finding model + frontmatter load

**Files:**

- Create: `scripts/skill_standards_audit.py`
- Test: `tests/test_skill_standards.py`

**Interfaces:**

- Produces: `Finding` (namedtuple: `severity, category, path, message`); `load_frontmatter(skill_md: Path) -> dict`; `VALID_SKILL_KEYS: set[str]`; `DESC_MAX = 1536`, `SKILL_MAX_LINES = 500`, `REF_TOC_LINES = 300`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_skill_standards.py
import os, sys
from pathlib import Path
CRAFT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CRAFT / "scripts"))
import skill_standards_audit as ssa

def test_load_frontmatter_reads_name_and_description(tmp_path):
    sk = tmp_path / "SKILL.md"
    sk.write_text("---\nname: demo-skill\ndescription: Does a thing.\n---\n# Body\n")
    fm = ssa.load_frontmatter(sk)
    assert fm["name"] == "demo-skill"
    assert fm["description"] == "Does a thing."

def test_valid_keys_includes_recent_anthropic_additions():
    for k in ("when_to_use", "allowed-tools", "paths", "disable-model-invocation"):
        assert k in ssa.VALID_SKILL_KEYS
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_skill_standards.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'skill_standards_audit'`

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/skill_standards_audit.py
"""Audit skills/**/SKILL.md against Anthropic authoring standards.
Mirrors scripts/command-audit.sh: scan -> checks -> score -> exit 0/1/2.
Reuses commands/_discovery.py:parse_yaml_frontmatter.
"""
import os, sys, re, json, argparse
from pathlib import Path
from collections import namedtuple

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "commands"))
from _discovery import parse_yaml_frontmatter  # noqa: E402

SKILLS_DIR = REPO / "skills"
DESC_MAX = 1536          # description (+ when_to_use) combined char cap
SKILL_MAX_LINES = 500    # SKILL.md soft ceiling
REF_TOC_LINES = 300      # reference files larger than this need a TOC

VALID_SKILL_KEYS = {
    "name", "description", "when_to_use", "allowed-tools", "disallowed-tools",
    "paths", "disable-model-invocation", "user-invocable", "context", "agent",
    "model", "effort", "argument-hint", "arguments", "shell", "hooks", "license",
    # craft-local markers tolerated on skills:
    "category", "deprecated", "replaced-by",
}

Finding = namedtuple("Finding", "severity category path message")  # severity: "error"|"warning"

def load_frontmatter(skill_md: Path) -> dict:
    return parse_yaml_frontmatter(skill_md.read_text(encoding="utf-8"))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_skill_standards.py -q`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/skill_standards_audit.py tests/test_skill_standards.py
git commit -m "feat(skill-standards): scanner skeleton — constants + frontmatter load"
```

---

### Task 2: Frontmatter checks

**Files:**

- Modify: `scripts/skill_standards_audit.py`
- Test: `tests/test_skill_standards.py`

**Interfaces:**

- Produces: `check_frontmatter(fm: dict, path: Path) -> list[Finding]`.
- Consumes: `Finding`, `VALID_SKILL_KEYS`, `DESC_MAX` (Task 1).

- [ ] **Step 1: Write the failing test**

```python
def test_check_frontmatter_flags_missing_name_as_error(tmp_path):
    findings = ssa.check_frontmatter({"description": "x"}, tmp_path / "SKILL.md")
    assert any(f.severity == "error" and f.category == "frontmatter" and "name" in f.message for f in findings)

def test_check_frontmatter_flags_non_kebab_name(tmp_path):
    findings = ssa.check_frontmatter({"name": "Demo_Skill", "description": "x"}, tmp_path / "SKILL.md")
    assert any("kebab" in f.message for f in findings)

def test_check_frontmatter_unknown_key_is_warning(tmp_path):
    findings = ssa.check_frontmatter({"name": "demo", "description": "x", "bogus": "y"}, tmp_path / "SKILL.md")
    assert any(f.severity == "warning" and "bogus" in f.message for f in findings)

def test_check_frontmatter_overlong_description_is_warning(tmp_path):
    findings = ssa.check_frontmatter({"name": "demo", "description": "z" * 1600}, tmp_path / "SKILL.md")
    assert any("1536" in f.message for f in findings)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_skill_standards.py -k check_frontmatter -q`
Expected: FAIL — `AttributeError: module has no attribute 'check_frontmatter'`

- [ ] **Step 3: Write minimal implementation**

```python
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

def check_frontmatter(fm: dict, path: Path) -> list:
    out = []
    name = fm.get("name", "")
    if not name:
        out.append(Finding("error", "frontmatter", path, "missing required 'name'"))
    elif not KEBAB.match(name):
        out.append(Finding("error", "frontmatter", path, f"name '{name}' is not kebab-case"))
    desc = fm.get("description", "")
    if not desc:
        out.append(Finding("error", "frontmatter", path, "missing 'description'"))
    combined = len(desc) + len(fm.get("when_to_use", ""))
    if combined > DESC_MAX:
        out.append(Finding("warning", "frontmatter", path,
                           f"description(+when_to_use) is {combined} chars, exceeds {DESC_MAX}"))
    for key in fm:
        if key not in VALID_SKILL_KEYS:
            out.append(Finding("warning", "frontmatter", path, f"unrecognized frontmatter key '{key}'"))
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_skill_standards.py -k check_frontmatter -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/skill_standards_audit.py tests/test_skill_standards.py
git commit -m "feat(skill-standards): frontmatter checks (name/desc/keys)"
```

---

### Task 3: Size & progressive-disclosure checks

**Files:**

- Modify: `scripts/skill_standards_audit.py`
- Test: `tests/test_skill_standards.py`

**Interfaces:**

- Produces: `check_size(skill_md: Path) -> list[Finding]` (covers SKILL.md line cap + each `references/*.md` > `REF_TOC_LINES` needing a TOC).

- [ ] **Step 1: Write the failing test**

```python
def _mkskill(tmp_path, body_lines, refs=None):
    d = tmp_path / "skills" / "demo"
    (d / "references").mkdir(parents=True)
    (d / "SKILL.md").write_text("---\nname: demo\ndescription: x\n---\n" + "\n".join(["line"] * body_lines))
    for fname, lines, has_toc in (refs or []):
        toc = "## Table of Contents\n" if has_toc else ""
        (d / "references" / fname).write_text(toc + "\n".join(["x"] * lines))
    return d / "SKILL.md"

def test_check_size_flags_oversized_skill_md(tmp_path):
    sk = _mkskill(tmp_path, body_lines=600)
    assert any("500" in f.message for f in ssa.check_size(sk))

def test_check_size_flags_large_reference_without_toc(tmp_path):
    sk = _mkskill(tmp_path, body_lines=10, refs=[("big.md", 400, False)])
    assert any("big.md" in f.message and "table of contents" in f.message.lower() for f in ssa.check_size(sk))

def test_check_size_passes_large_reference_with_toc(tmp_path):
    sk = _mkskill(tmp_path, body_lines=10, refs=[("big.md", 400, True)])
    assert not any("big.md" in f.message for f in ssa.check_size(sk))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_skill_standards.py -k check_size -q`
Expected: FAIL — no attribute `check_size`

- [ ] **Step 3: Write minimal implementation**

```python
def check_size(skill_md: Path) -> list:
    out = []
    n = len(skill_md.read_text(encoding="utf-8").splitlines())
    if n > SKILL_MAX_LINES:
        out.append(Finding("warning", "size", skill_md,
                           f"SKILL.md is {n} lines, exceeds {SKILL_MAX_LINES} — move detail to references/"))
    refs = skill_md.parent / "references"
    if refs.is_dir():
        for ref in sorted(refs.glob("*.md")):
            text = ref.read_text(encoding="utf-8")
            if len(text.splitlines()) > REF_TOC_LINES and not re.search(r"(?im)^#{1,3}\s+table of contents", text):
                out.append(Finding("warning", "size", ref,
                                   f"{ref.name} > {REF_TOC_LINES} lines and has no table of contents"))
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_skill_standards.py -k check_size -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/skill_standards_audit.py tests/test_skill_standards.py
git commit -m "feat(skill-standards): size & progressive-disclosure checks"
```

---

### Task 4: Reference-hygiene checks (heuristic, warning-only)

**Files:**

- Modify: `scripts/skill_standards_audit.py`
- Test: `tests/test_skill_standards.py`

**Interfaces:**

- Produces: `check_reference_hygiene(skill_md: Path) -> list[Finding]` — rot-prone version tags in headers + second-person framing in reference bodies. All `warning`.

- [ ] **Step 1: Write the failing test**

```python
def test_hygiene_flags_version_tags(tmp_path):
    sk = _mkskill(tmp_path, 10, refs=[("r.md", 20, True)])
    (sk.parent / "references" / "r.md").write_text("## Step 1 (NEW in v2.49.0)\nbody\n")
    assert any("version tag" in f.message.lower() for f in ssa.check_reference_hygiene(sk))

def test_hygiene_flags_second_person_framing(tmp_path):
    sk = _mkskill(tmp_path, 10, refs=[("r.md", 20, True)])
    (sk.parent / "references" / "r.md").write_text("You are an assistant. Do the thing.\n")
    assert any(f.severity == "warning" and "second-person" in f.message.lower()
               for f in ssa.check_reference_hygiene(sk))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_skill_standards.py -k hygiene -q`
Expected: FAIL — no attribute `check_reference_hygiene`

- [ ] **Step 3: Write minimal implementation**

```python
VERSION_TAG = re.compile(r"\((?:NEW(?:!| in)? v\d|Phase \d)", re.I)
SECOND_PERSON = re.compile(r"(?im)^\s*you are\b")

def check_reference_hygiene(skill_md: Path) -> list:
    out = []
    refs = skill_md.parent / "references"
    if not refs.is_dir():
        return out
    for ref in sorted(refs.glob("*.md")):
        text = ref.read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.lstrip().startswith("#") and VERSION_TAG.search(line):
                out.append(Finding("warning", "hygiene", ref,
                                   f"rot-prone version tag in header: {line.strip()[:60]}"))
        if SECOND_PERSON.search(text):
            out.append(Finding("warning", "hygiene", ref,
                               "second-person command framing ('You are…') — prefer timeless reference prose"))
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_skill_standards.py -k hygiene -q`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/skill_standards_audit.py tests/test_skill_standards.py
git commit -m "feat(skill-standards): reference-hygiene heuristics (warning-only)"
```

---

### Task 5: Aggregation — audit_skill, score, output modes, argparse, exit codes

**Files:**

- Modify: `scripts/skill_standards_audit.py`
- Test: `tests/test_skill_standards.py`

**Interfaces:**

- Consumes: `check_frontmatter`, `check_size`, `check_reference_hygiene`, `load_frontmatter`, `SKILLS_DIR`.
- Produces: `audit_skill(skill_md: Path) -> list[Finding]`; `audit_all(root: Path) -> list[Finding]`; `score(findings) -> int`; `main(argv) -> int` (exit code).

- [ ] **Step 1: Write the failing test**

```python
def test_score_formula_matches_command_audit():
    f = [ssa.Finding("error","c",Path("a"),"m"), ssa.Finding("warning","c",Path("a"),"m")]
    assert ssa.score(f) == 100 - 5 - 2

def test_main_exit_2_on_error(tmp_path, capsys):
    # a skill missing name => error => exit 2
    d = tmp_path / "skills" / "bad"; d.mkdir(parents=True)
    (d / "SKILL.md").write_text("---\ndescription: x\n---\n# b\n")
    rc = ssa.main(["--root", str(tmp_path / "skills"), "--json"])
    assert rc == 2
    assert "frontmatter" in capsys.readouterr().out

def test_main_exit_0_when_clean(tmp_path):
    d = tmp_path / "skills" / "good"; d.mkdir(parents=True)
    (d / "SKILL.md").write_text("---\nname: good\ndescription: A clean skill.\n---\n# Good\n")
    assert ssa.main(["--root", str(tmp_path / "skills"), "--json"]) == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_skill_standards.py -k "score or main_exit" -q`
Expected: FAIL — no attribute `score` / `main`

- [ ] **Step 3: Write minimal implementation**

```python
def audit_skill(skill_md: Path) -> list:
    fm = load_frontmatter(skill_md)
    return (check_frontmatter(fm, skill_md)
            + check_size(skill_md)
            + check_reference_hygiene(skill_md))

def audit_all(root: Path) -> list:
    out = []
    for skill_md in sorted(root.rglob("SKILL.md")):
        out.extend(audit_skill(skill_md))
    return out

def score(findings) -> int:
    e = sum(1 for f in findings if f.severity == "error")
    w = sum(1 for f in findings if f.severity == "warning")
    return max(0, 100 - e * 5 - w * 2)

def _emit(findings, mode, root):
    if mode == "json":
        print(json.dumps([{"severity": f.severity, "category": f.category,
                            "path": str(f.path), "message": f.message} for f in findings], indent=2))
    elif mode == "markdown":
        for f in findings:
            print(f"- **{f.severity}** `{f.path}` [{f.category}] — {f.message}")
    else:  # terminal
        for f in findings:
            icon = "🔴" if f.severity == "error" else "🟡"
            print(f"  {icon} [{f.category}] {Path(f.path).relative_to(root) if root in Path(f.path).parents else f.path}: {f.message}")
        print(f"\nScore: {score(findings)}/100  ({sum(1 for x in findings if x.severity=='error')} errors, "
              f"{sum(1 for x in findings if x.severity=='warning')} warnings)")

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Audit SKILL.md files against Anthropic standards")
    p.add_argument("--root", default=str(SKILLS_DIR))
    p.add_argument("--json", action="store_const", const="json", dest="mode")
    p.add_argument("--markdown", action="store_const", const="markdown", dest="mode")
    p.add_argument("--fix", action="store_true")
    p.add_argument("--refresh-standards", action="store_true")
    args = p.parse_args(argv)
    root = Path(args.root)
    if args.refresh_standards:
        return refresh_standards()        # Task 7
    findings = audit_all(root)
    if args.fix:
        findings = apply_safe_fixes(root, findings)   # Task 6
    _emit(findings, args.mode or "terminal", root)
    if any(f.severity == "error" for f in findings):
        return 2
    return 1 if findings else 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_skill_standards.py -q`
Expected: PASS (all). NOTE: `apply_safe_fixes` and `refresh_standards` are referenced but only invoked under flags not yet tested — define no-op stubs now to keep import clean:

```python
def apply_safe_fixes(root, findings):  # filled in Task 6
    return findings
def refresh_standards():               # filled in Task 7
    return 0
```

- [ ] **Step 5: Commit**

```bash
git add scripts/skill_standards_audit.py tests/test_skill_standards.py
git commit -m "feat(skill-standards): aggregation, scoring, output modes, exit codes"
```

---

### Task 6: `--fix` safe mechanical fixes

**Files:**

- Modify: `scripts/skill_standards_audit.py` (replace the `apply_safe_fixes` stub)
- Test: `tests/test_skill_standards.py`

**Interfaces:**

- Consumes: findings from `audit_all`.
- Produces: `apply_safe_fixes(root, findings) -> list[Finding]` (re-audits and returns residual findings). Fixes ONLY: strip version tags from reference headers. Never touches descriptions.

- [ ] **Step 1: Write the failing test**

```python
def test_fix_strips_version_tags_only(tmp_path):
    d = tmp_path / "skills" / "demo" / "references"; d.mkdir(parents=True)
    (d.parent / "SKILL.md").write_text("---\nname: demo\ndescription: A skill.\n---\n# Demo\n")
    ref = d / "r.md"
    ref.write_text("## Step 1 (NEW in v2.49.0)\nYou are an assistant.\n")
    ssa.apply_safe_fixes(tmp_path / "skills", ssa.audit_all(tmp_path / "skills"))
    txt = ref.read_text()
    assert "(NEW in v2.49.0)" not in txt          # version tag stripped
    assert "You are an assistant." in txt          # prose NOT auto-rewritten
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_skill_standards.py -k fix_strips -q`
Expected: FAIL — version tag still present (stub is a no-op)

- [ ] **Step 3: Write minimal implementation**

```python
def apply_safe_fixes(root: Path, findings) -> list:
    for ref in {Path(f.path) for f in findings if f.category == "hygiene"}:
        if ref.name == "SKILL.md":
            continue
        text = ref.read_text(encoding="utf-8")
        fixed = "\n".join(
            re.sub(r"\s*\((?:NEW(?:!| in)? v[\d.]+|Phase \d+)\)", "", line) if line.lstrip().startswith("#") else line
            for line in text.splitlines()
        )
        if fixed != text:
            ref.write_text(fixed + ("\n" if text.endswith("\n") else ""), encoding="utf-8")
    return audit_all(root)  # residual findings after fixes
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_skill_standards.py -k fix_strips -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/skill_standards_audit.py tests/test_skill_standards.py
git commit -m "feat(skill-standards): --fix strips version tags (prose untouched)"
```

---

### Task 7: Vendored standards doc + `--refresh-standards` + command surface

**Files:**

- Create: `docs/reference/SKILL-STANDARDS.md`
- Create: `commands/code/skill-standards.md`
- Modify: `scripts/skill_standards_audit.py` (replace `refresh_standards` stub)
- Test: `tests/test_skill_standards.py`

**Interfaces:**

- Produces: `refresh_standards() -> int` — rewrites only the provenance block (today's date + installed skill-creator path) between HTML-comment markers in `docs/reference/SKILL-STANDARDS.md`; returns 0. Prose synthesis stays a model step in the command.

- [ ] **Step 1: Write the failing test**

```python
def test_refresh_standards_updates_provenance(tmp_path, monkeypatch):
    doc = tmp_path / "SKILL-STANDARDS.md"
    doc.write_text("<!-- PROVENANCE\nsynced: 1970-01-01\n-->\n# Standards\nrules…\n")
    monkeypatch.setattr(ssa, "STANDARDS_DOC", doc)
    assert ssa.refresh_standards() == 0
    body = doc.read_text()
    assert "synced: 1970-01-01" not in body      # date bumped
    assert "# Standards" in body                  # prose preserved
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_skill_standards.py -k refresh -q`
Expected: FAIL — stub returns 0 but does not rewrite provenance

- [ ] **Step 3: Write minimal implementation**

```python
import datetime
STANDARDS_DOC = REPO / "docs" / "reference" / "SKILL-STANDARDS.md"

def refresh_standards() -> int:
    if not STANDARDS_DOC.exists():
        print(f"missing {STANDARDS_DOC}"); return 2
    today = datetime.date.today().isoformat()
    text = STANDARDS_DOC.read_text(encoding="utf-8")
    new_block = (f"<!-- PROVENANCE\nsynced: {today}\n"
                 f"sources: https://code.claude.com/docs/en/skills.md ; installed skill-creator guide\n-->")
    text = re.sub(r"<!-- PROVENANCE.*?-->", new_block, text, count=1, flags=re.DOTALL)
    STANDARDS_DOC.write_text(text, encoding="utf-8")
    print(f"provenance refreshed: {today} (prose synthesis is a manual/model step)")
    return 0
```

- [ ] **Step 4: Write the vendored doc and command (no code execution — content steps)**

Create `docs/reference/SKILL-STANDARDS.md` with: a `<!-- PROVENANCE ... -->` block, then the checklist from the spec's "Standards checklist" section (frontmatter, size/progressive-disclosure, reference hygiene, advisory keys), each rule tagged `[error]`/`[warning]` to match the scanner.

Create `commands/code/skill-standards.md` mirroring `commands/code/command-audit.md` frontmatter (quote any colon-bearing arg descriptions — command-audit uses real YAML). Body steps: (1) run `python3 scripts/skill_standards_audit.py` (+ `--json`/`--markdown`/`--fix`/`--refresh-standards`); (2) on description findings, suggest `skill-creator run_loop.py`; (3) on qualitative gaps, dispatch `plugin-dev:skill-reviewer`; (4) `--refresh-standards` then re-synthesize the doc prose from the live standards.

- [ ] **Step 5: Run test + command-audit, then commit**

Run: `python3 -m pytest tests/test_skill_standards.py -k refresh -q` → PASS
Run: `bash scripts/command-audit.sh` → no errors mentioning `skill-standards`

```bash
git add scripts/skill_standards_audit.py docs/reference/SKILL-STANDARDS.md commands/code/skill-standards.md tests/test_skill_standards.py
git commit -m "feat(skill-standards): vendored standards doc, --refresh-standards, command surface"
```

---

### Task 8: Count cascade + doc surfaces + dogfood

**Files:**

- Modify: `.claude-plugin/plugin.json` (`100 craft` → `101 craft`, total `114` → `115`), `CHANGELOG.md`, `mkdocs.yml`, `docs/REFCARD.md`
- Create: `docs/tutorials/TUTORIAL-skill-standards.md`
- Run: `scripts/bump-version.sh` sweep equivalents + `validate-counts.sh`

- [ ] **Step 1: Run the count + staleness baseline**

Run: `./scripts/validate-counts.sh` — note the new command count (should report a mismatch until plugin.json is bumped).

- [ ] **Step 2: Apply the count cascade**

Edit `.claude-plugin/plugin.json` description subtotal `(100 craft + 14 workflow)` → `(101 craft + 14 workflow)` and total `114` → `115`. Add the `[Unreleased]` CHANGELOG entry. Add the tutorial + reference to `mkdocs.yml` nav (pattern: the Done-Optimization tutorial / Memory-Optimization reference pair already added under the tutorials group). Add a REFCARD row.

- [ ] **Step 3: Write the tutorial**

Create `docs/tutorials/TUTORIAL-skill-standards.md` — usage (`/craft:code:skill-standards`, `--fix`, `--json`, `--refresh-standards`), how to read the report, the delegate-to-skill-creator/skill-reviewer handoffs.

- [ ] **Step 4: Verify clean**

Run: `./scripts/validate-counts.sh` → all match (+1 command).
Run: `./scripts/docs-staleness-check.sh` → GREEN.
Run: `python3 -m pytest tests/test_skill_standards.py -q` → all PASS.

- [ ] **Step 5: Dogfood + commit**

Run: `python3 scripts/skill_standards_audit.py` against craft's real skills. Confirm `skills/workflow/adhd-workflow/SKILL.md` + `references/done.md` produce **zero findings** (fixed under ADR-002). Triage other skills' findings into a follow-up note. If `references/done.md` (~1190 lines, has a TOC?) trips the >300-line/no-TOC rule, that resolves the optional `/done` example-extraction question from the spec.

```bash
git add .claude-plugin/plugin.json CHANGELOG.md mkdocs.yml docs/REFCARD.md docs/tutorials/TUTORIAL-skill-standards.md
git commit -m "docs(skill-standards): count cascade + tutorial + REFCARD + nav"
```

---

## Self-Review

**Spec coverage:** scanner (T1–T5) ✓, `--fix` safe set (T6) ✓, vendored standards + `--refresh-standards` (T7) ✓, command surface (T7) ✓, tests (every task) ✓, docs + count cascade (T8) ✓, delegation to skill-creator/skill-reviewer (T7 command steps) ✓, dogfood/done-gating (T8 Step 5) ✓. The six audit gaps are each resolved (constraints + Tasks 2,4,7,8).

**Placeholder scan:** Task 7 Step 4 and Task 8 Steps 2–3 describe doc *content* rather than showing every line — acceptable because they are prose-doc authoring steps, not code; their structure and source sections are named exactly. All code steps carry complete code.

**Type consistency:** `Finding(severity, category, path, message)` used identically across Tasks 1–6. `audit_all`/`score`/`apply_safe_fixes`/`refresh_standards` signatures defined in Task 5 match their fills in Tasks 6–7. `STANDARDS_DOC` introduced in Task 7 and patched in its test.

## Execution Handoff

Plan complete and saved to `docs/plans/2026-06-23-skill-standards-auditor.md`. Execution requires a `feature/skill-standards` worktree (new `.py` files). Two options:

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks.
2. **Inline Execution** — execute in-session with checkpoints.

Worktree creation + execution is a separate, explicitly-authorized step — not started here.
