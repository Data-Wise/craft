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

def apply_safe_fixes(root, findings):  # filled in Task 6
    return findings

def refresh_standards():               # filled in Task 7
    return 0

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
        return refresh_standards()
    findings = audit_all(root)
    if args.fix:
        findings = apply_safe_fixes(root, findings)
    _emit(findings, args.mode or "terminal", root)
    if any(f.severity == "error" for f in findings):
        return 2
    return 1 if findings else 0

if __name__ == "__main__":
    raise SystemExit(main())
