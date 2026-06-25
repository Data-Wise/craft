#!/usr/bin/env python3
"""Caveats-staleness gate for Homebrew formulae (Checks 1-3; Check 4 brew audit
lives in the shell wrapper). D8: single entry point, no Check 5."""
import re, sys, argparse
from dataclasses import dataclass, field

@dataclass
class GateReport:
    ok: bool
    findings: list = field(default_factory=list)

def _extract_def_body(text, def_name):
    """Extract the body of a Ruby def block, handling nested end keywords."""
    m = re.search(rf"def {re.escape(def_name)}\b", text)
    if not m:
        return None
    start = m.end()
    depth = 1
    pos = start
    lines = text[start:].split("\n")
    collected = []
    for line in lines:
        stripped = line.strip()
        # keywords that increase depth
        if re.match(r"\b(def|do|begin|if|unless|while|until|case|class|module)\b", stripped):
            depth += 1
        # 'end' decreases depth
        if re.match(r"end\b", stripped):
            depth -= 1
            if depth == 0:
                break
        collected.append(line)
    return "\n".join(collected)

def _caveats_block(text):
    body = _extract_def_body(text, "caveats")
    return body if body is not None else ""

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
    pi_body = _extract_def_body(text, "post_install")
    if pi_body is not None and not (
        re.search(r"\bbegin\b", pi_body) and
        re.search(r"\brescue\b", pi_body)
    ):
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
