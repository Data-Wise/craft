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
