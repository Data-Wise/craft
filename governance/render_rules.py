#!/usr/bin/env python3
"""
render_rules.py — Phase 3 safeguard: generate the human-readable rule block from
RULES.yaml and keep every CLAUDE.md copy in sync so they can never silently drift.

  --apply FILE...   replace the content between the RULES markers in each FILE
  --init  FILE...   like --apply, but append a fresh marked block if none exists
  --check FILE...   exit 1 if any FILE's block differs from a fresh render (the
                    'rules-drift' gate for CI / a hook)
  (no file)         print the rendered block to stdout

The block is delimited by:
  <!-- RULES:BEGIN (generated from governance/RULES.yaml — do not edit by hand) -->
  ...
  <!-- RULES:END -->
Edit RULES.yaml, re-run --apply; never hand-edit between the markers.

Stdlib + PyYAML.
"""
import os, sys, argparse
try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML required: pip install pyyaml\n"); sys.exit(2)

GOV = os.path.dirname(os.path.abspath(__file__))
BEGIN = "<!-- RULES:BEGIN (generated from governance/RULES.yaml — do not edit by hand) -->"
END = "<!-- RULES:END -->"


def render_block():
    doc = yaml.safe_load(open(os.path.join(GOV, "RULES.yaml"), encoding="utf-8"))
    sev_order = {"error": 0, "warn": 1, "advisory": 2}
    rules = [r for r in doc["rules"] if r.get("status") == "active"]
    rules.sort(key=lambda r: (sev_order.get(r.get("severity"), 9), r["id"]))
    lines = [BEGIN,
             "<!-- scope=%s · posture=%s · %d active rules -->" % (doc.get("scope"), doc.get("posture"), len(rules)),
             "",
             "## Skill-organization rules (generated)",
             "",
             "_Source of truth: `governance/RULES.yaml` (craft). Regenerate with `render_rules.py --apply`; do not edit between the markers._",
             ""]
    for r in rules:
        sev = r.get("severity", "warn").upper()
        gates = ", ".join(r.get("gates") or []) or "—"
        lines.append("- **%s** · `%s` · gates: %s — %s" % (r["id"], sev, gates, r["statement"]))
    lines += ["", END]
    return "\n".join(lines)


def splice(text, block):
    if BEGIN in text and END in text:
        pre = text[:text.index(BEGIN)]
        post = text[text.index(END) + len(END):]
        return pre + block + post
    return None


def apply_to(path, block, init):
    path = os.path.expanduser(path)
    text = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    spliced = splice(text, block)
    if spliced is None:
        if not init:
            print("  no markers in %s (use --init to append a fresh block)" % path); return False
        sep = "" if text.endswith("\n\n") or text == "" else ("\n" if text.endswith("\n") else "\n\n")
        spliced = text + sep + block + "\n"
    open(path, "w", encoding="utf-8").write(spliced)
    print("  wrote rule block -> %s" % path)
    return True


def check(path, block):
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        print("  MISSING %s" % path); return False
    text = open(path, encoding="utf-8").read()
    if BEGIN not in text or END not in text:
        print("  NO-MARKERS %s" % path); return False
    cur = text[text.index(BEGIN):text.index(END) + len(END)]
    ok = cur.strip() == block.strip()
    print("  %s %s" % ("OK     " if ok else "DRIFT  ", path))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", nargs="*", default=None)
    ap.add_argument("--init", nargs="*", default=None)
    ap.add_argument("--check", nargs="*", default=None)
    a = ap.parse_args()
    block = render_block()
    if a.check is not None:
        if not a.check:
            sys.stderr.write("--check needs at least one FILE to compare against\n"); return 2
        ok = all(check(p, block) for p in a.check)
        return 0 if ok else 1
    if a.init is not None:
        all(apply_to(p, block, init=True) for p in a.init)
        return 0
    if a.apply is not None:
        ok = all(apply_to(p, block, init=False) for p in a.apply)
        return 0 if ok else 1
    print(block)
    return 0


if __name__ == "__main__":
    sys.exit(main())
