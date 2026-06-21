#!/usr/bin/env python3
"""
run_rules.py — the governance engine. Loads RULES.yaml, runs each rule's check,
applies severity + waivers, and reports. Two modes:

  (default)    audit the live environment against the rules; exit 1 on any
               unwaived ERROR failure (so CI / a SessionStart hook can gate on it).
  --selftest   META-VALIDATION (P5): prove each checker works on its own fixtures
               (bad must fail, good must pass), flag error-rules with no automated
               check, and verify every waiver has an owner + a future expiry.
               Exit 1 if any checker misbehaves.

Stdlib + PyYAML. Paths in RULES.yaml are relative to this file's directory.
  python3 run_rules.py [--target DIR] [--index FILE] [--json] [--selftest]
"""
import os, sys, json, subprocess, datetime, argparse
try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML required: pip install pyyaml\n"); sys.exit(2)

GOV = os.path.dirname(os.path.abspath(__file__))
DEF_TARGET = os.path.expanduser("~/.claude/skills")
DEF_INDEX = os.path.expanduser("~/.claude/skills/SKILLS-INDEX.md")


def load_rules():
    with open(os.path.join(GOV, "RULES.yaml")) as f:
        return yaml.safe_load(f)


def run_script(cmd_str, subs):
    """cmd_str like 'checks/x.py {target}'. Returns (rc, output)."""
    parts = cmd_str.format(**subs).split()
    script = os.path.join(GOV, parts[0])
    if not os.path.exists(script):
        return None, "checker not found: %s" % parts[0]
    p = subprocess.run([sys.executable, script] + parts[1:], capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).rstrip()


def active_waiver(rule):
    today = datetime.date.today().isoformat()
    for w in rule.get("waivers") or []:
        exp = str(w.get("expires", ""))
        if exp and exp >= today:
            return w
    return None


def audit(rules_doc, target, index, as_json):
    subs = {"target": target, "index": index}
    results, red = [], 0
    for r in rules_doc["rules"]:
        if r.get("status") != "active":
            continue
        chk = r.get("check", {}) or {}
        kind = chk.get("kind", "manual")
        sev = r.get("severity", "warn")
        rc, out = None, ""
        if kind == "script":
            rc, out = run_script(chk["cmd"], subs)
            state = "PASS" if rc == 0 else ("FAIL" if rc else "ERROR")
        elif kind == "external":
            state = "EXTERNAL"  # supplied by skills-audit.py cross-surface auditor; not run here
        else:
            state = "MANUAL"    # advisory / not yet automated
        waiver = active_waiver(r)
        if state == "FAIL" and waiver:
            state = "WAIVED"
        if state == "FAIL" and sev == "error":
            red += 1
        results.append({"id": r["id"], "severity": sev, "state": state, "kind": kind, "output": out, "waiver": bool(waiver)})

    if as_json:
        print(json.dumps({"results": results, "red": red}, indent=2)); return 1 if red else 0
    print("GOVERNANCE AUDIT  scope=%s  posture=%s" % (rules_doc.get("scope"), rules_doc.get("posture")))
    for x in results:
        tag = {"PASS": "ok  ", "FAIL": "FAIL", "WAIVED": "waiv", "ERROR": "ERR ", "EXTERNAL": "ext ", "MANUAL": "man "}.get(x["state"], "?")
        print("  [%s] %-22s %-8s %s" % (tag, x["id"], x["severity"], x["state"]))
        if x["output"]:
            for line in x["output"].splitlines():
                print("        " + line)
    print("  ---> %d unwaived ERROR failure(s)" % red)
    return 1 if red else 0


def selftest(rules_doc):
    print("GOVERNANCE SELFTEST (meta-validation)")
    bad_meta = 0
    today = datetime.date.today().isoformat()
    for r in rules_doc["rules"]:
        rid, sev = r["id"], r.get("severity")
        chk = r.get("check", {}) or {}
        fx = chk.get("fixtures")
        # 1) checker must behave on its fixtures
        if fx:
            rc_bad, _ = run_script(chk["cmd"], {"target": os.path.join(GOV, fx["bad"]), "index": os.path.join(GOV, fx["bad"])})
            rc_good, _ = run_script(chk["cmd"], {"target": os.path.join(GOV, fx["good"]), "index": os.path.join(GOV, fx["good"])})
            ok = (rc_bad not in (0, None)) and (rc_good == 0)
            print("  [%s] %-22s fixtures: bad->%s good->%s  %s" % ("ok  " if ok else "FAIL", rid, rc_bad, rc_good, "" if ok else "<-- checker misbehaves"))
            if not ok:
                bad_meta += 1
        # 2) an ERROR rule with no automated check is an enforcement gap
        elif sev == "error" and chk.get("kind") in (None, "manual"):
            print("  [warn] %-22s ERROR severity but no automated check (enforcement gap)" % rid)
        # 3) waiver hygiene
        for w in r.get("waivers") or []:
            if not w.get("owner") or not w.get("expires"):
                print("  [FAIL] %-22s waiver missing owner/expires" % rid); bad_meta += 1
            elif str(w["expires"]) < today:
                print("  [FAIL] %-22s waiver EXPIRED (%s)" % (rid, w["expires"])); bad_meta += 1
    print("  ---> %d meta-failure(s)" % bad_meta)
    return 1 if bad_meta else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default=DEF_TARGET)
    ap.add_argument("--index", default=DEF_INDEX)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    doc = load_rules()
    if a.selftest:
        return selftest(doc)
    return audit(doc, a.target, a.index, a.json)


if __name__ == "__main__":
    sys.exit(main())
