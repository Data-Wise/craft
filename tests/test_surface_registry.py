"""Unit tests for the surface registry (Task 1 — TDD RED phase).

Tests:
  1. registry.json loads; every entry has the required fields; gate ∈ valid set.
  2. Parity: every BLOCK/WARN surface (minus cowork — Task 2 adds its verify leg)
     maps, via the explicit alias map, onto an add_leg call in verify-surfaces.sh.
"""

import json
import re
from pathlib import Path

WORKTREE = Path(__file__).parent.parent
REGISTRY_PATH = WORKTREE / "scripts" / "surfaces" / "registry.json"
VERIFY_SCRIPT = WORKTREE / "scripts" / "verify-surfaces.sh"

REQUIRED_FIELDS = {"name", "detect", "propagate", "verify", "gate"}
VALID_GATES = {"BLOCK", "WARN", "INFO"}

# Explicit alias map: registry surface name → verify-surfaces.sh leg label.
# Cowork is excluded — its verify leg is added in Task 2.
# desktop-ext is excluded — INFO, no verify leg by design.
PARITY_ALIAS_MAP = {
    "git-tag": "git tag",
    "tap": "tap formula",
    "brew": "brew-installed",
    "code-registered": "Code-registered",
    "marketplace": "marketplace",
    "aggregator": "aggregator",
    # cowork: excluded — verify leg added in Task 2
    # desktop-ext: excluded — INFO, no verify leg by design
}


def load_registry() -> list[dict]:
    """Load and return the registry entries."""
    with open(REGISTRY_PATH) as f:
        data = json.load(f)
    return data["surfaces"]


def test_registry_loads_and_has_required_fields():
    """Every registry entry has name, detect, propagate, verify, gate; gate is valid."""
    surfaces = load_registry()
    assert len(surfaces) == 8, f"Expected 8 surfaces, got {len(surfaces)}"

    for surface in surfaces:
        name = surface.get("name", "<missing>")
        missing = REQUIRED_FIELDS - surface.keys()
        assert not missing, f"Surface {name!r} missing fields: {missing}"
        assert surface["gate"] in VALID_GATES, (
            f"Surface {name!r} has invalid gate {surface['gate']!r}; "
            f"must be one of {VALID_GATES}"
        )


def test_registry_has_expected_surface_names():
    """Registry contains exactly the 8 expected surface names."""
    surfaces = load_registry()
    names = {s["name"] for s in surfaces}
    expected = {
        "git-tag", "marketplace", "tap", "brew",
        "code-registered", "aggregator", "cowork", "desktop-ext",
    }
    assert names == expected, f"Surface names mismatch: got {names}"


def test_registry_gate_values():
    """Each surface has the specified gate value from the spec."""
    surfaces = load_registry()
    gate_map = {s["name"]: s["gate"] for s in surfaces}
    expected_gates = {
        "git-tag": "BLOCK",
        "marketplace": "BLOCK",
        "tap": "BLOCK",
        "aggregator": "BLOCK",
        "brew": "WARN",
        "code-registered": "WARN",
        "cowork": "WARN",
        "desktop-ext": "INFO",
    }
    for name, expected_gate in expected_gates.items():
        assert name in gate_map, f"Surface {name!r} not found in registry"
        assert gate_map[name] == expected_gate, (
            f"Surface {name!r}: expected gate {expected_gate!r}, got {gate_map[name]!r}"
        )


def test_parity_block_warn_surfaces_map_to_verify_legs():
    """Every BLOCK/WARN surface in PARITY_ALIAS_MAP maps to an add_leg label in verify-surfaces.sh.

    Uses static parse (regex on source text) so the aggregator leg is found even
    though it is runtime-conditional ([[ -n "$AGG_FILE" ]] && add_leg "aggregator").

    Cowork is explicitly excluded from parity scope — its verify leg is added in Task 2.
    """
    verify_source = VERIFY_SCRIPT.read_text()

    # Extract all leg labels passed to add_leg.
    # Pattern matches: add_leg "label" (function def add_leg() won't match — no space+quote).
    leg_labels = set(re.findall(r'add_leg\s+"([^"]+)"', verify_source))

    for surface_name, leg_label in PARITY_ALIAS_MAP.items():
        assert leg_label in leg_labels, (
            f"Registry surface {surface_name!r} maps to leg {leg_label!r}, "
            f"but that label is not found in verify-surfaces.sh add_leg calls. "
            f"Found labels: {sorted(leg_labels)}"
        )
