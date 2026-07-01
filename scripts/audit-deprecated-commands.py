#!/usr/bin/env python3
"""Audit command/skill body-size ratios -- repo-wide sweep, or one pair at a time.

Generalizes the one-off scan from SPEC-craft-audit-and-next-steps-2026-06-30.md
section 5.1. Flags commands whose body is disproportionately larger than the
skill that's supposed to be canonical going into v3.0.0 -- the ADR-002
("deprecated-command rich-body trap") failure mode.

Two modes:
    Repo-wide sweep (original mode) -- scans every `deprecated: true` command:
        python3 scripts/audit-deprecated-commands.py [--threshold 2.0] [--json]

    Single-pair check (authoring-time mode, used by the
    command-skill-token-efficiency skill) -- check one file you just wrote or
    edited against its companion, without needing deprecated:true/replaced-by:
    frontmatter to already exist:
        python3 scripts/audit-deprecated-commands.py --pair <file_a> <file_b> [--threshold 2.0] [--json]

Exit codes:
    0 - no command/pair exceeds the threshold
    1 - at least one command/pair exceeds the threshold (WARN signal, not a
        hard gate -- see ADR-003, advisory-not-hard-gate precedent)
"""
import argparse
import glob
import json
import os
import re
import sys


def scan(plugin_dir="."):
    cmds = glob.glob(os.path.join(plugin_dir, "commands/**/*.md"), recursive=True)
    rows = []
    seen = set()
    for c in cmds:
        if c in seen:
            continue
        seen.add(c)
        try:
            text = open(c, encoding="utf-8").read()
        except OSError:
            continue
        if "deprecated: true" not in text:
            continue
        m = re.search(r'replaced-by:\s*"([^"]+)"', text)
        cmd_lines = len(text.splitlines())
        rel_cmd = os.path.relpath(c, plugin_dir)
        if not m:
            rows.append({
                "command": rel_cmd, "command_lines": cmd_lines,
                "target": None, "skill_lines": None, "ratio": None,
                "issue": "no replaced-by: frontmatter",
            })
            continue
        target_dir = m.group(1)
        skill_path = os.path.join(plugin_dir, target_dir, "SKILL.md")
        if not os.path.exists(skill_path):
            rows.append({
                "command": rel_cmd, "command_lines": cmd_lines,
                "target": target_dir, "skill_lines": None, "ratio": None,
                "issue": f"replaced-by target has no SKILL.md: {target_dir}",
            })
            continue
        skill_lines = len(open(skill_path, encoding="utf-8").read().splitlines())
        ratio = cmd_lines / skill_lines if skill_lines else None
        rows.append({
            "command": rel_cmd, "command_lines": cmd_lines,
            "target": target_dir, "skill_lines": skill_lines, "ratio": ratio,
            "issue": None,
        })
    rows.sort(key=lambda r: -(r["ratio"] or 0))
    return rows


def check_pair(file_a, file_b):
    """Authoring-time check: ratio between two arbitrary files (not just
    deprecated-command/skill pairs). No deprecated:true or replaced-by:
    frontmatter required -- this is for a file you just wrote or resized,
    checked against whatever it's meant to defer to (a skill, a references/
    doc, a sibling command). Larger-file-first is reported regardless of
    which argument order was given, so the ratio is always >= 1.
    """
    for f in (file_a, file_b):
        if not os.path.exists(f):
            return {"file_a": file_a, "file_b": file_b, "ratio": None,
                     "issue": f"file not found: {f}"}
    lines_a = len(open(file_a, encoding="utf-8").read().splitlines())
    lines_b = len(open(file_b, encoding="utf-8").read().splitlines())
    if lines_a >= lines_b:
        bigger, smaller, bigger_n, smaller_n = file_a, file_b, lines_a, lines_b
    else:
        bigger, smaller, bigger_n, smaller_n = file_b, file_a, lines_b, lines_a
    ratio = bigger_n / smaller_n if smaller_n else None
    return {"bigger": bigger, "bigger_lines": bigger_n,
            "smaller": smaller, "smaller_lines": smaller_n,
            "ratio": ratio, "issue": None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=2.0,
                     help="ratio above which to WARN (default 2.0)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--plugin-dir", default=".")
    ap.add_argument("--pair", nargs=2, metavar=("FILE_A", "FILE_B"),
                     help="check a single file pair instead of the repo-wide "
                          "deprecated-command sweep (authoring-time mode)")
    args = ap.parse_args()

    if args.pair:
        result = check_pair(*args.pair)
        flagged = bool(result["issue"]) or (
            result["ratio"] is not None and result["ratio"] >= args.threshold)
        if args.json:
            print(json.dumps({"threshold": args.threshold, **result}, indent=2))
        elif result["issue"]:
            print(f"! {result['issue']}")
        else:
            verdict = "FLAGGED" if flagged else "OK"
            print(f"{result['bigger']}: {result['bigger_lines']} lines")
            print(f"{result['smaller']}: {result['smaller_lines']} lines")
            print(f"ratio: {result['ratio']:.1f}  [{verdict}, threshold={args.threshold}]")
            if flagged:
                print("\nConsider: is the bigger file's extra content procedure "
                      "that belongs in the smaller file instead? See "
                      "skills/code/command-skill-token-efficiency/SKILL.md.")
        sys.exit(1 if flagged else 0)

    rows = scan(args.plugin_dir)
    flagged = [r for r in rows if r["issue"] or (r["ratio"] and r["ratio"] >= args.threshold)]

    if args.json:
        print(json.dumps({"threshold": args.threshold, "total_scanned": len(rows),
                           "flagged": flagged}, indent=2))
    else:
        print(f"Deprecated-command body-size audit (threshold={args.threshold})")
        print("=" * 70)
        print(f"Scanned: {len(rows)} deprecated commands\n")
        if not flagged:
            print("Clean -- no command exceeds the ratio threshold.")
        else:
            print(f"{'command':<45} {'lines':>6} {'skill_lines':>12} {'ratio':>7}")
            for r in flagged:
                if r["issue"]:
                    print(f"  ! {r['command']}: {r['issue']}")
                else:
                    print(f"{r['command']:<45} {r['command_lines']:>6} "
                          f"{r['skill_lines']:>12} {r['ratio']:>7.1f}")
            print(f"\n{len(flagged)} command(s) flagged. WARN-only signal --")
            print("see SPEC-craft-audit-and-next-steps-2026-06-30.md section 4.1.")

    sys.exit(1 if flagged else 0)


if __name__ == "__main__":
    main()
