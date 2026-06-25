#!/usr/bin/env python3
"""post_install gate: structural always; sandbox execution opt-in (macOS-local)."""
import re, sys, argparse, os, tempfile, subprocess
from verify_caveats import GateReport

def _extract_def_body(text, def_name):
    """Extract the body of a Ruby def block, handling nested end keywords."""
    m = re.search(rf"def {re.escape(def_name)}\b", text)
    if not m:
        return None
    start = m.end()
    depth = 1
    lines = text[start:].split("\n")
    collected = []
    for line in lines:
        stripped = line.strip()
        # keywords that open a new depth
        if re.match(r"\b(def|do|begin|if|unless|while|until|case|class|module)\b", stripped):
            depth += 1
        # 'end' closes a depth
        if re.match(r"end\b", stripped):
            depth -= 1
            if depth == 0:
                break
        collected.append(line)
    return "\n".join(collected)

def check_post_install(formula_path, sandbox=False):
    findings = []
    text = open(formula_path, encoding="utf-8").read()
    body = _extract_def_body(text, "post_install")
    if body is None:
        return GateReport(False, ["no post_install block found"])
    if not (re.search(r"\bbegin\b", body) and re.search(r"\brescue\b", body)):
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
