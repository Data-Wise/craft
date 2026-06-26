#!/usr/bin/env python3
"""Standalone surface registry helper for surfaces.sh.

Pattern: bump-version-helper.py — stdlib only, called by bash driver.

Usage:
  registry.py list                   Print all surface names, one per line
  registry.py show <name>            Print a single surface entry as JSON
  registry.py report                 Emit the full surface matrix as JSON
  registry.py gates                  Print name:gate pairs, one per line
  registry.py by-gate <BLOCK|WARN|INFO>  Print names for a given gate level
"""

import json
import sys
from pathlib import Path

REGISTRY_FILE = Path(__file__).parent / "registry.json"


def load() -> list[dict]:
    with open(REGISTRY_FILE) as f:
        data = json.load(f)
    return data["surfaces"]


def cmd_list(surfaces: list[dict]) -> None:
    for s in surfaces:
        print(s["name"])


def cmd_show(surfaces: list[dict], name: str) -> None:
    for s in surfaces:
        if s["name"] == name:
            print(json.dumps(s, indent=2))
            return
    print(f"error: surface {name!r} not found", file=sys.stderr)
    sys.exit(1)


def cmd_report(surfaces: list[dict]) -> None:
    """Emit the surface matrix skeleton (propagated/verified fields filled in at runtime)."""
    matrix = [
        {
            "name": s["name"],
            "gate": s["gate"],
            "propagated": None,
            "verified": None,
        }
        for s in surfaces
    ]
    print(json.dumps({"surfaces": matrix}, indent=2))


def cmd_gates(surfaces: list[dict]) -> None:
    for s in surfaces:
        print(f"{s['name']}:{s['gate']}")


def cmd_by_gate(surfaces: list[dict], gate: str) -> None:
    gate = gate.upper()
    for s in surfaces:
        if s["gate"] == gate:
            print(s["name"])


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)

    surfaces = load()
    cmd = sys.argv[1]

    if cmd == "list":
        cmd_list(surfaces)
    elif cmd == "show":
        if len(sys.argv) < 3:
            print("error: show requires a surface name", file=sys.stderr)
            sys.exit(2)
        cmd_show(surfaces, sys.argv[2])
    elif cmd == "report":
        cmd_report(surfaces)
    elif cmd == "gates":
        cmd_gates(surfaces)
    elif cmd == "by-gate":
        if len(sys.argv) < 3:
            print("error: by-gate requires a gate level (BLOCK|WARN|INFO)", file=sys.stderr)
            sys.exit(2)
        cmd_by_gate(surfaces, sys.argv[2])
    else:
        print(f"error: unknown command {cmd!r}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
