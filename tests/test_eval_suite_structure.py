"""Structural checks for the plugin eval suite in evals/ (no claude calls, no cost).

Live scores come from scripts/run-evals.sh; this file only guards the shape of the
suite and of evals/_coverage.json (GRILL B2/B3 in docs/specs/GRILL-eval-harness-*.md).
"""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
EVALS = ROOT / "evals"
SKILLS = ROOT / "skills"

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
GRADER_TYPES = {"llm", "tool_used"}


def frontmatter(path):
    m = FRONTMATTER.match(path.read_text(encoding="utf-8"))
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def case_dirs(evals):
    if not evals.is_dir():
        return []
    return sorted(p for p in evals.iterdir()
                  if p.is_dir() and not p.name.startswith("_") and p.name != "results")


def skill_names(skills):
    names = set()
    for p in skills.rglob("SKILL.md"):
        fm = frontmatter(p)
        if fm and fm.get("name"):
            names.add(fm["name"])
    return names


def check_case(case):
    """Return a list of problems for one case dir."""
    problems = []
    prompt = case / "prompt.md"
    if not prompt.is_file():
        return [f"{case.name}: missing prompt.md"]
    fm = frontmatter(prompt)
    if fm is None:
        problems.append(f"{case.name}: prompt.md has no frontmatter")
    else:
        if fm.get("allowed_tools") != "[Skill]":
            problems.append(f"{case.name}: allowed_tools must be [Skill] (baseline must not read repo files)")
        mt = fm.get("max_turns", "")
        if not mt.isdigit() or not 1 <= int(mt) <= 10:
            problems.append(f"{case.name}: max_turns must be an integer 1-10")
    graders = sorted((case / "graders").glob("*.md")) if (case / "graders").is_dir() else []
    types = []
    for g in graders:
        gfm = frontmatter(g)
        if gfm is None or gfm.get("type") not in GRADER_TYPES:
            problems.append(f"{case.name}/{g.name}: type must be one of {sorted(GRADER_TYPES)}")
        else:
            types.append(gfm["type"])
    if "llm" not in types:
        problems.append(f"{case.name}: needs at least one scored type: llm grader")
    return problems


def check_coverage(coverage_file, evals, skills):
    problems = []
    if not coverage_file.is_file():
        return problems
    data = json.loads(coverage_file.read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 1:
        problems.append("_coverage.json: schemaVersion must be 1")
    known = skill_names(skills)
    for e in data.get("cases", []):
        if not (evals / e.get("case", "")).is_dir():
            problems.append(f"_coverage.json: case dir missing for {e.get('case')!r}")
        if e.get("skill") is not None and e["skill"] not in known:
            problems.append(f"_coverage.json: unknown skill {e['skill']!r}")
        if e.get("delta") is not None and not isinstance(e["delta"], (int, float)):
            problems.append(f"_coverage.json: delta must be a number for {e.get('case')!r}")
    return problems


def test_every_case_is_well_formed():
    problems = [p for c in case_dirs(EVALS) for p in check_case(c)]
    assert not problems, "\n".join(problems)


def test_coverage_file_is_consistent():
    problems = check_coverage(EVALS / "_coverage.json", EVALS, SKILLS)
    assert not problems, "\n".join(problems)


def test_there_are_cases():
    assert case_dirs(EVALS), "evals/ has no cases"


# --- positive controls: planted defects must be caught ----------------------

def _case(tmp, name, prompt, graders):
    d = tmp / name
    (d / "graders").mkdir(parents=True)
    (d / "prompt.md").write_text(prompt, encoding="utf-8")
    for fname, body in graders.items():
        (d / "graders" / fname).write_text(body, encoding="utf-8")
    return d


GOOD_PROMPT = "---\nmax_turns: 6\nallowed_tools: [Skill]\n---\n\nAsk something.\n"
GOOD_GRADER = "---\ntype: llm\nweight: 1\n---\n\nPass if correct.\n"


def test_good_case_has_no_problems(tmp_path):
    c = _case(tmp_path, "ok", GOOD_PROMPT, {"criteria.md": GOOD_GRADER})
    assert check_case(c) == []


def test_planted_read_tool_is_caught(tmp_path):
    c = _case(tmp_path, "bad", GOOD_PROMPT.replace("[Skill]", "[Read, Skill]"), {"criteria.md": GOOD_GRADER})
    assert any("allowed_tools" in p for p in check_case(c))


def test_planted_missing_llm_grader_is_caught(tmp_path):
    tool = "---\ntype: tool_used\nweight: 1\ntool: Skill\n---\n\nx\n"
    c = _case(tmp_path, "bad", GOOD_PROMPT, {"skill.md": tool})
    assert any("llm grader" in p for p in check_case(c))


def test_planted_bad_grader_type_is_caught(tmp_path):
    c = _case(tmp_path, "bad", GOOD_PROMPT, {"criteria.md": GOOD_GRADER.replace("llm", "magic")})
    assert any("type must be" in p for p in check_case(c))


def test_planted_coverage_defects_are_caught(tmp_path):
    ev = tmp_path / "evals"
    (ev / "real-case").mkdir(parents=True)
    sk = tmp_path / "skills" / "x"
    sk.mkdir(parents=True)
    (sk / "SKILL.md").write_text("---\nname: real-skill\n---\n", encoding="utf-8")
    cov = ev / "_coverage.json"
    cov.write_text(json.dumps({"schemaVersion": 1, "cases": [
        {"case": "ghost-case", "skill": "real-skill", "delta": 1},
        {"case": "real-case", "skill": "no-such-skill", "delta": 1},
    ]}), encoding="utf-8")
    problems = check_coverage(cov, ev, tmp_path / "skills")
    assert any("ghost-case" in p for p in problems)
    assert any("no-such-skill" in p for p in problems)
