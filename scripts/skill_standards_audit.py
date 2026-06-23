"""Audit skills/**/SKILL.md against Anthropic authoring standards.
Mirrors scripts/command-audit.sh: scan -> checks -> score -> exit 0/1/2.
Reuses commands/_discovery.py:parse_yaml_frontmatter.
"""
import os, sys, re, json, argparse, datetime
from pathlib import Path
from collections import namedtuple

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "commands"))
from _discovery import parse_yaml_frontmatter  # noqa: E402

SKILLS_DIR = REPO / "skills"
STANDARDS_DOC = REPO / "docs" / "reference" / "SKILL-STANDARDS.md"
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

TOC_STUB = "\n## Table of Contents\n\n<!-- Sections in this reference; keep in sync. -->\n"
TOC_RE = re.compile(r"(?im)^#{1,3}\s+table of contents")
_SIMPLE_KV = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):\s")
_BLOCK_SCALAR = re.compile(r":\s*[|>]\s*$")
_CONTINUATION = re.compile(r"^(\s+\S|-\s)")


def _normalize_frontmatter(text: str) -> str:
    """Lowercase and reorder frontmatter keys in SKILL.md; skip complex blocks."""
    lines = text.splitlines(keepends=True)
    # find first and second '---' delimiters
    delim_idx = [i for i, l in enumerate(lines) if l.strip() == "---"]
    if len(delim_idx) < 2:
        return text
    start, end = delim_idx[0], delim_idx[1]
    fm_lines = lines[start + 1: end]
    # Safety: skip if any block scalar or continuation line present
    for line in fm_lines:
        stripped = line.rstrip("\n")
        if _BLOCK_SCALAR.search(stripped):
            return text
        if _CONTINUATION.match(stripped):
            return text
    # Build normalized key -> raw_line mapping (preserve value byte-for-byte)
    kv_pairs = []  # list of (lowered_key, normalized_line)
    for line in fm_lines:
        stripped = line.rstrip("\n")
        m = _SIMPLE_KV.match(stripped)
        if m:
            raw_key = m.group(1)
            lower_key = raw_key.lower()
            if lower_key in VALID_SKILL_KEYS:
                # lowercase key, preserve everything after (including ": value")
                normalized_line = lower_key + stripped[len(raw_key):] + "\n"
            else:
                normalized_line = line
            kv_pairs.append((lower_key, normalized_line))
        else:
            # non-kv line (blank, comment): attach to previous or keep in place
            kv_pairs.append(("", line))
    # Reorder: name, description, when_to_use, then rest in original relative order
    CANONICAL_ORDER = ["name", "description", "when_to_use"]
    ordered = []
    seen = set()
    for key in CANONICAL_ORDER:
        for k, l in kv_pairs:
            if k == key and k not in seen:
                ordered.append(l)
                seen.add(k)
    for k, l in kv_pairs:
        if k not in seen:
            ordered.append(l)
            seen.add(k) if k else None
    new_fm = "".join(ordered)
    old_fm = "".join(fm_lines)
    if new_fm == old_fm:
        return text
    return "".join(lines[:start + 1]) + new_fm + "".join(lines[end:])


def apply_safe_fixes(root: Path, findings) -> list:
    # Fix #1: strip version tags from reference headers (hygiene findings)
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

    # Fix #3: insert TOC stub in oversized reference files lacking a TOC
    for f in findings:
        if f.category != "size":
            continue
        ref = Path(f.path)
        if ref.name == "SKILL.md" or "table of contents" not in f.message.lower():
            continue
        if not ref.suffix == ".md" or "references" not in ref.parts:
            continue
        text = ref.read_text(encoding="utf-8")
        if TOC_RE.search(text):
            continue  # already has TOC (e.g., fix #1 above added it on a prior run)
        # Insert after first H1 if present, else at top
        h1_match = re.search(r"(?m)^# .+", text)
        if h1_match:
            insert_at = h1_match.end()
            new_text = text[:insert_at] + TOC_STUB + text[insert_at:]
        else:
            new_text = TOC_STUB.lstrip("\n") + text
        ref.write_text(new_text, encoding="utf-8")

    # Fix #2: normalize frontmatter keys in SKILL.md files (blanket pass)
    for skill_md in root.rglob("SKILL.md"):
        text = skill_md.read_text(encoding="utf-8")
        fixed = _normalize_frontmatter(text)
        if fixed != text:
            skill_md.write_text(fixed, encoding="utf-8")

    return audit_all(root)  # residual findings after fixes

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
