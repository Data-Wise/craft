"""Unit tests for the surface registry (Task 1 — TDD RED phase; Task 2 additions).

Tests:
  1. registry.json loads; every entry has the required fields; gate ∈ valid set.
  2. Parity: every BLOCK/WARN surface (minus desktop-ext which is INFO) maps,
     via the explicit alias map, onto an add_leg call in verify-surfaces.sh.
  3. Cowork-store parser reads fixture known_marketplaces.json +
     installed_plugins.json → marketplaces + pins (injectable, no live store).
  4. Name-match validator flags an entry whose name ≠ source-declared name.
"""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

WORKTREE = Path(__file__).parent.parent
REGISTRY_PATH = WORKTREE / "scripts" / "surfaces" / "registry.json"
VERIFY_SCRIPT = WORKTREE / "scripts" / "verify-surfaces.sh"

REQUIRED_FIELDS = {"name", "detect", "propagate", "verify", "gate"}
VALID_GATES = {"BLOCK", "WARN", "INFO"}

# Explicit alias map: registry surface name → verify-surfaces.sh leg label.
# desktop-ext is excluded — INFO, no verify leg by design.
PARITY_ALIAS_MAP = {
    "git-tag": "git tag",
    "tap": "tap formula",
    "brew": "brew-installed",
    "code-registered": "Code-registered",
    "marketplace": "marketplace",
    "aggregator": "aggregator",
    "cowork": "cowork",  # Task 2: cowork leg added to verify-surfaces.sh
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
    """Every BLOCK/WARN surface in PARITY_ALIAS_MAP maps to an add_leg call in verify-surfaces.sh.

    Uses static parse (regex on source text) so the aggregator leg is found even
    though it is runtime-conditional ([[ -n "$AGG_FILE" ]] && add_leg "aggregator").

    desktop-ext is excluded — INFO surface, no verify leg by design.
    """
    verify_source = VERIFY_SCRIPT.read_text()

    # Extract all leg labels passed to add_leg or add_warn_leg.
    # Pattern matches: add_leg "label" or add_warn_leg "label"
    # (function def won't match — it has () not space+quote).
    leg_labels = set(re.findall(r'add(?:_warn)?_leg\s+"([^"]+)"', verify_source))

    for surface_name, leg_label in PARITY_ALIAS_MAP.items():
        assert leg_label in leg_labels, (
            f"Registry surface {surface_name!r} maps to leg {leg_label!r}, "
            f"but that label is not found in verify-surfaces.sh add_leg/add_warn_leg calls. "
            f"Found labels: {sorted(leg_labels)}"
        )


# ---------------------------------------------------------------------------
# Task 2: Cowork-store parser tests (fixture-based, no live store)
# ---------------------------------------------------------------------------

def _make_cowork_store(tmp_dir: str, marketplaces: dict, plugins: dict) -> str:
    """Create a cowork store fixture directory with the expected JSON shape."""
    store_dir = os.path.join(tmp_dir, "cowork_plugins")
    os.makedirs(store_dir, exist_ok=True)
    with open(os.path.join(store_dir, "known_marketplaces.json"), "w") as f:
        json.dump(marketplaces, f)
    with open(os.path.join(store_dir, "installed_plugins.json"), "w") as f:
        json.dump(plugins, f)
    return store_dir


def _run_verify(sandbox_dir: str, env_overrides: dict, extra_args: list[str] | None = None) -> tuple[int, str]:
    """Run verify-surfaces.sh in sandbox_dir with env_overrides; return (exit_code, stripped_output)."""
    env = os.environ.copy()
    env["SURFACES_REPO_DIR"] = sandbox_dir
    # Prevent live cowork-store glob from touching the real machine state.
    env.setdefault("SURFACES_COWORK_STORE", "/nonexistent/cowork_store")
    env.update(env_overrides)
    result = subprocess.run(
        ["bash", str(VERIFY_SCRIPT)] + (extra_args or []),
        capture_output=True,
        text=True,
        env=env,
    )
    # Strip ANSI codes
    output = re.sub(r'\033\[[0-9;]*m', '', result.stdout + result.stderr)
    return result.returncode, output


def _make_plugin_sandbox(tmp_dir: str, version: str) -> None:
    """Populate tmp_dir with minimal plugin.json + marketplace.json."""
    plugin_dir = os.path.join(tmp_dir, ".claude-plugin")
    os.makedirs(plugin_dir, exist_ok=True)
    with open(os.path.join(plugin_dir, "plugin.json"), "w") as f:
        json.dump({"name": "craft", "version": version, "description": "test"}, f)
    with open(os.path.join(plugin_dir, "marketplace.json"), "w") as f:
        json.dump({
            "metadata": {"version": version},
            "plugins": [{"name": "craft", "version": version}],
        }, f)


def test_cowork_store_present_and_matching_is_warn_not_block():
    """Cowork leg: present with matching version → warn (exit 0, not exit 1)."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_plugin_sandbox(tmp, "2.37.0")
        store = _make_cowork_store(
            tmp,
            marketplaces={"my-mkt": {"source": {"source": "github", "repo": "Data-Wise/craft"}}},
            plugins={"plugins": {"craft@my-mkt": [{"version": "2.37.0"}]}},
        )
        exit_code, output = _run_verify(tmp, {
            "SURFACES_GIT_TAG": "v2.37.0",
            "SURFACES_TAP_FORMULA": "/nonexistent/craft.rb",
            "SURFACES_BREW_VERSION": "2.37.0",
            "SURFACES_INSTALLED_PLUGINS": "/nonexistent/installed_plugins.json",
            "SURFACES_COWORK_STORE": store,
        })
        assert exit_code == 0, f"Cowork match must not block (exit 0), got {exit_code}:\n{output}"
        assert "cowork" in output.lower(), f"Output must show cowork leg:\n{output}"


def test_cowork_store_mismatch_is_warn_only_not_block():
    """Cowork leg: present with WRONG version → WARN, exit 0 (never blocks)."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_plugin_sandbox(tmp, "2.37.0")
        store = _make_cowork_store(
            tmp,
            marketplaces={"my-mkt": {"source": {"source": "github", "repo": "Data-Wise/craft"}}},
            plugins={"plugins": {"craft@my-mkt": [{"version": "2.36.0"}]}},  # WRONG version
        )
        exit_code, output = _run_verify(tmp, {
            "SURFACES_GIT_TAG": "v2.37.0",
            "SURFACES_TAP_FORMULA": "/nonexistent/craft.rb",
            "SURFACES_BREW_VERSION": "2.37.0",
            "SURFACES_INSTALLED_PLUGINS": "/nonexistent/installed_plugins.json",
            "SURFACES_COWORK_STORE": store,
        })
        assert exit_code == 0, (
            f"Cowork mismatch must NOT block (WARN only, exit 0), got {exit_code}:\n{output}"
        )
        assert "cowork" in output.lower(), f"Output must show cowork leg:\n{output}"


def test_cowork_store_absent_is_warn_not_block():
    """Cowork leg: SURFACES_COWORK_STORE points at non-existent path → absent/warn, exit 0."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_plugin_sandbox(tmp, "2.37.0")
        exit_code, output = _run_verify(tmp, {
            "SURFACES_GIT_TAG": "v2.37.0",
            "SURFACES_TAP_FORMULA": "/nonexistent/craft.rb",
            "SURFACES_BREW_VERSION": "2.37.0",
            "SURFACES_INSTALLED_PLUGINS": "/nonexistent/installed_plugins.json",
            "SURFACES_COWORK_STORE": "/nonexistent/cowork_store_path",
        })
        assert exit_code == 0, f"Absent cowork store must not block (exit 0), got {exit_code}:\n{output}"


def test_aggregator_name_mismatch_blocks():
    """Name-match assertion: aggregator entry with wrong name → BLOCK (exit 1).

    The entry is found by source-repo (independent key), then its declared 'name'
    is compared against PLUGIN_NAME. A name mismatch is as bad as a version mismatch.
    """
    with tempfile.TemporaryDirectory() as tmp:
        _make_plugin_sandbox(tmp, "2.37.0")
        # Aggregator has correct version but WRONG name for the craft entry
        agg_file = os.path.join(tmp, "aggregator.json")
        with open(agg_file, "w") as f:
            json.dump({
                "name": "data-wise",
                "plugins": [{"name": "WRONG-NAME", "version": "2.37.0"}],
            }, f)
        exit_code, output = _run_verify(tmp, {
            "SURFACES_GIT_TAG": "v2.37.0",
            "SURFACES_TAP_FORMULA": "/nonexistent/craft.rb",
            "SURFACES_BREW_VERSION": "2.37.0",
            "SURFACES_INSTALLED_PLUGINS": "/nonexistent/installed_plugins.json",
            "SURFACES_AGGREGATOR_FILE": agg_file,
        })
        assert exit_code == 1, (
            f"Aggregator name mismatch must block (exit 1), got {exit_code}:\n{output}"
        )


def test_aggregator_name_match_does_not_block():
    """Name-match assertion: aggregator entry with correct name + version → ALIGNED, exit 0."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_plugin_sandbox(tmp, "2.37.0")
        agg_file = os.path.join(tmp, "aggregator.json")
        with open(agg_file, "w") as f:
            json.dump({
                "name": "data-wise",
                "plugins": [{"name": "craft", "version": "2.37.0"}],
            }, f)
        exit_code, output = _run_verify(tmp, {
            "SURFACES_GIT_TAG": "v2.37.0",
            "SURFACES_TAP_FORMULA": "/nonexistent/craft.rb",
            "SURFACES_BREW_VERSION": "2.37.0",
            "SURFACES_INSTALLED_PLUGINS": "/nonexistent/installed_plugins.json",
            "SURFACES_AGGREGATOR_FILE": agg_file,
        })
        assert exit_code == 0, (
            f"Correct name + version in aggregator must exit 0, got {exit_code}:\n{output}"
        )
