#!/usr/bin/env python3
"""Standalone surface registry helper for surfaces.sh.

Pattern: bump-version-helper.py — stdlib only, called by bash driver.

Usage:
  registry.py list                   Print all surface names, one per line
  registry.py show <name>            Print a single surface entry as JSON
  registry.py report                 Emit the full surface matrix as JSON (legacy skeleton)
  registry.py report-live [--json]   Emit real matrix from verify-surfaces.sh JSON on stdin
  registry.py gates                  Print name:gate pairs, one per line
  registry.py by-gate <BLOCK|WARN|INFO>  Print names for a given gate level
"""

import json
import sys
from pathlib import Path

REGISTRY_FILE = Path(__file__).parent / "registry.json"

# Reverse alias map: verify-surfaces.sh leg label → registry surface name.
# desktop-ext is INFO-only and has no verify leg — excluded by design.
_LEG_TO_SURFACE = {
    "git tag": "git-tag",
    "tap formula": "tap",
    "brew-installed": "brew",
    "Code-registered": "code-registered",
    "marketplace": "marketplace",
    "aggregator": "aggregator",
    "cowork": "cowork",
}

# Human-readable state labels for the rendered matrix.
_STATE_LABELS = {
    "ok": "✓ aligned",
    "mismatch": "✗ MISMATCH",
    "absent": "— absent",
    "warn": "! warn (manual)",
    "corrupt": "! CORRUPT",
    "name-mismatch": "✗ NAME MISMATCH",
}


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
    """Emit the surface matrix skeleton (legacy — propagated/verified fields null)."""
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


def cmd_report_live(surfaces: list[dict], as_json: bool = False) -> None:
    """Render a real surface matrix from verify-surfaces.sh --json output on stdin.

    The verify JSON shape (from verify-surfaces.sh):
      {
        "applicable": bool,
        "plugin": str,
        "version": str,
        "legs": [{"surface": str, "version": str, "state": str}, ...],
        "desktop": str,   # "info" / "warn" / absent
        "blocked": bool
      }

    Reads the registry to get gate values; cross-references via _LEG_TO_SURFACE alias map.
    """
    registry_by_name = {s["name"]: s for s in surfaces}

    # Read verify JSON from stdin.
    raw = sys.stdin.read().strip()
    try:
        verify = json.loads(raw) if raw else {}
    except json.JSONDecodeError as e:
        print(f"error: could not parse verify-surfaces.sh JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not verify.get("applicable", False):
        # Not applicable — no plugin found. Emit empty / inapplicable marker.
        if as_json:
            print(json.dumps({"applicable": False, "surfaces": []}, indent=2))
        else:
            print("surfaces: not applicable (no plugin.json found)")
        return

    plugin = verify.get("plugin", "?")
    version = verify.get("version", "?")
    legs = verify.get("legs", [])
    blocked = verify.get("blocked", False)

    # Build a lookup from leg label → {version, state}.
    leg_data: dict[str, dict] = {}
    for leg in legs:
        leg_data[leg["surface"]] = {"version": leg["version"], "state": leg["state"]}

    # Build the matrix by iterating surfaces in registry order.
    # Each surface gets its version + state from the verify output (via alias map),
    # and its gate from the registry.
    matrix_rows = []
    for s in surfaces:
        name = s["name"]
        gate = s["gate"]
        # Find the corresponding verify leg label.
        leg_label = None
        for label, reg_name in _LEG_TO_SURFACE.items():
            if reg_name == name:
                leg_label = label
                break
        if leg_label and leg_label in leg_data:
            ld = leg_data[leg_label]
            row_version = ld["version"]
            row_state = ld["state"]
        else:
            # desktop-ext is INFO only; no verify leg.
            row_version = "—"
            row_state = "info"
        matrix_rows.append({
            "name": name,
            "gate": gate,
            "version": row_version,
            "state": row_state,
            "state_label": _STATE_LABELS.get(row_state, row_state),
        })

    if as_json:
        # Machine-readable output: structured JSON including the full matrix.
        out = {
            "applicable": True,
            "plugin": plugin,
            "version": version,
            "blocked": blocked,
            "surfaces": [
                {
                    "name": r["name"],
                    "gate": r["gate"],
                    "version": r["version"],
                    "state": r["state"],
                }
                for r in matrix_rows
            ],
        }
        print(json.dumps(out, indent=2))
    else:
        # Human-readable box output.
        width = 64
        border = "─" * width
        print(f"┌{border}┐")
        print(f"│ /craft:dist:surfaces{' ' * (width - 20)}│")
        print(f"├{border}┤")
        plugin_line = f" Plugin: {plugin}  Version: {version}"
        print(f"│{plugin_line}{' ' * (width - len(plugin_line))}│")
        block_count = sum(1 for r in matrix_rows if r["gate"] == "BLOCK" and r["state"] not in ("info",))
        warn_count = sum(1 for r in matrix_rows if r["gate"] == "WARN" and r["state"] not in ("info",))
        checked_line = f" Surfaces checked: {block_count + warn_count} ({block_count} BLOCK, {warn_count} WARN)"
        print(f"│{checked_line}{' ' * (width - len(checked_line))}│")
        print(f"├{border}┤")
        visible_rows = [r for r in matrix_rows if r["gate"] != "INFO"]
        # Compute column widths dynamically.
        name_width = max((len(r["name"].capitalize()) for r in visible_rows), default=8)
        ver_width = max((len(r["version"]) for r in visible_rows), default=7)
        gate_width = max((len(r["gate"]) for r in visible_rows), default=5)
        for r in visible_rows:
            name_col = r["name"].capitalize().ljust(name_width)
            dots = "." * max(1, 15 - name_width)
            ver = r["version"].ljust(ver_width)
            gate = r["gate"].ljust(gate_width)
            label = r["state_label"]
            row = f" {name_col} {dots} {ver}  {gate}  {label}"
            print(f"│{row}{' ' * max(0, width - len(row))}│")
        print(f"├{border}┤")
        if blocked:
            gate_line = " Gate: FAILED — at least one BLOCK surface misaligned"
        else:
            gate_line = " Gate: PASSED — all BLOCK surfaces aligned"
        print(f"│{gate_line}{' ' * max(0, width - len(gate_line))}│")
        print(f"└{border}┘")


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
    elif cmd == "report-live":
        as_json = "--json" in sys.argv[2:]
        cmd_report_live(surfaces, as_json=as_json)
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
