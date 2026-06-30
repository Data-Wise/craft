#!/usr/bin/env python3
"""Audit deprecated commands' body size against their replaced-by skill.

Generalizes the one-off scan from SPEC-craft-audit-and-next-steps-2026-06-30.md
section 5.1. Flags commands whose body is disproportionately larger than the
skill that's supposed to be canonical going into v3.0.0 -- the ADR-002
("deprecated-command rich-body trap") failure mode.

Usage:
    python3 scripts/audit-deprecated-commands.py [--threshold 2.0] [--json]

Exit codes:
    0 - no command exceeds the threshold
    1 - at least one command exceeds the threshold (WARN signal, not a hard gate
        -- see ADR-003, advisory-not-hard-gate precedent)
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=2.0,
                     help="ratio above which to WARN (default 2.0)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--plugin-dir", default=".")
    args = ap.parse_args()

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
