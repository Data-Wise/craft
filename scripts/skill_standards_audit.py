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
