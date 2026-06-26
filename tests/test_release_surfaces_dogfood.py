"""Dogfood / E2E tests for verify-surfaces.sh — Task 2 additions.

These tests use injected fixture stores (SURFACES_* env vars) so no live
machine state is required. They validate the exit-code contract:

  - A mismatched BLOCK surface → exit 1
  - A Cowork-only mismatch → WARN-only, exit 0
  - A name-mismatch in the aggregator → exit 1 (mutate-and-revert proves the gate)

Markers: e2e + dogfood (registered in pyproject.toml).
"""

import json
import os
import re
import subprocess
import tempfile

import pytest

# Absolute path to the script under test — works from any CWD.
_WORKTREE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFY_SCRIPT = os.path.join(_WORKTREE, "scripts", "verify-surfaces.sh")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def _make_installed_plugins(tmp_dir: str, version: str) -> str:
    """Write an installed_plugins.json fixture; return its path."""
    path = os.path.join(tmp_dir, "installed_plugins.json")
    with open(path, "w") as f:
        json.dump(
            {"version": 2, "plugins": {"craft@local-plugins": [{"version": version}]}},
            f,
        )
    return path


def _make_cowork_store(tmp_dir: str, version: str) -> str:
    """Create a cowork_plugins/ fixture directory; return its path."""
    store_dir = os.path.join(tmp_dir, "cowork_plugins")
    os.makedirs(store_dir, exist_ok=True)
    with open(os.path.join(store_dir, "known_marketplaces.json"), "w") as f:
        json.dump(
            {"my-mkt": {"source": {"source": "github", "repo": "Data-Wise/craft"}}},
            f,
        )
    with open(os.path.join(store_dir, "installed_plugins.json"), "w") as f:
        json.dump(
            {"plugins": {"craft@my-mkt": [{"version": version}]}},
            f,
        )
    return store_dir


def _run_verify(sandbox_dir: str, env_overrides: dict, extra_args: list | None = None) -> tuple[int, str]:
    """Run verify-surfaces.sh in sandbox_dir; return (exit_code, cleaned_output)."""
    env = os.environ.copy()
    env["SURFACES_REPO_DIR"] = sandbox_dir
    env.update(env_overrides)
    result = subprocess.run(
        ["bash", VERIFY_SCRIPT] + (extra_args or []),
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    output = re.sub(r'\033\[[0-9;]*m', '', result.stdout + result.stderr)
    return result.returncode, output


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.e2e
@pytest.mark.dogfood
def test_block_surface_mismatch_exits_1():
    """A mismatched BLOCK surface (brew leg here) → exit 1.

    This validates the baseline BLOCK contract that must remain unaffected
    by the Task 2 additions.
    """
    with tempfile.TemporaryDirectory() as tmp:
        _make_plugin_sandbox(tmp, "2.37.0")
        installed = _make_installed_plugins(tmp, "2.37.0")
        cowork_store = _make_cowork_store(tmp, "2.37.0")  # cowork aligned

        exit_code, output = _run_verify(tmp, {
            "SURFACES_GIT_TAG": "v2.37.0",
            "SURFACES_TAP_FORMULA": "/nonexistent/craft.rb",
            "SURFACES_BREW_VERSION": "2.36.0",  # WRONG — triggers BLOCK
            "SURFACES_INSTALLED_PLUGINS": installed,
            "SURFACES_COWORK_STORE": cowork_store,
        })

        assert exit_code == 1, (
            f"A BLOCK surface mismatch must exit 1, got {exit_code}:\n{output}"
        )
        assert "BLOCKED" in output or "MISMATCH" in output, (
            f"Output must flag the mismatch:\n{output}"
        )


@pytest.mark.e2e
@pytest.mark.dogfood
def test_cowork_only_mismatch_is_warn_exits_0():
    """Cowork mismatch with all other legs aligned → WARN only, exit 0.

    This is the critical safety check: a Cowork drift must NEVER change the
    exit code. If this test fails, the cowork leg incorrectly sets BLOCK=1.
    """
    with tempfile.TemporaryDirectory() as tmp:
        _make_plugin_sandbox(tmp, "2.37.0")
        installed = _make_installed_plugins(tmp, "2.37.0")
        # Cowork has WRONG version — all other legs are aligned
        cowork_store = _make_cowork_store(tmp, "2.36.0")

        exit_code, output = _run_verify(tmp, {
            "SURFACES_GIT_TAG": "v2.37.0",
            "SURFACES_TAP_FORMULA": "/nonexistent/craft.rb",
            "SURFACES_BREW_VERSION": "2.37.0",
            "SURFACES_INSTALLED_PLUGINS": installed,
            "SURFACES_COWORK_STORE": cowork_store,
        })

        assert exit_code == 0, (
            f"Cowork mismatch must NEVER block (exit 0), got {exit_code}:\n{output}"
        )
        assert "cowork" in output.lower(), (
            f"Cowork leg must appear in output:\n{output}"
        )
        # Confirm the summary says ALIGNED (all BLOCK legs are fine)
        assert "ALIGNED" in output, (
            f"Summary must be ALIGNED when only Cowork leg drifts:\n{output}"
        )


@pytest.mark.e2e
@pytest.mark.dogfood
def test_aggregator_name_mismatch_blocks_mutate_and_revert():
    """Aggregator name-mismatch gate fires on mutation, is silent on revert.

    Mutate: entry name → WRONG-NAME → exit 1 (gate fires).
    Revert: entry name → craft (correct) → exit 0 (gate silent).

    This proves the name-match guard is a real gate, not a phantom assertion.
    """
    with tempfile.TemporaryDirectory() as tmp:
        _make_plugin_sandbox(tmp, "2.37.0")
        installed = _make_installed_plugins(tmp, "2.37.0")
        cowork_store = _make_cowork_store(tmp, "2.37.0")
        agg_file = os.path.join(tmp, "aggregator.json")

        base_env = {
            "SURFACES_GIT_TAG": "v2.37.0",
            "SURFACES_TAP_FORMULA": "/nonexistent/craft.rb",
            "SURFACES_BREW_VERSION": "2.37.0",
            "SURFACES_INSTALLED_PLUGINS": installed,
            "SURFACES_COWORK_STORE": cowork_store,
            "SURFACES_AGGREGATOR_FILE": agg_file,
        }

        # --- MUTATE: wrong name in aggregator ---
        with open(agg_file, "w") as f:
            json.dump({
                "name": "data-wise",
                "plugins": [{"name": "WRONG-NAME", "version": "2.37.0"}],
            }, f)

        exit_code_mutated, output_mutated = _run_verify(tmp, base_env)
        assert exit_code_mutated == 1, (
            f"Name mismatch in aggregator must block (exit 1), got {exit_code_mutated}:\n{output_mutated}"
        )

        # --- REVERT: correct name ---
        with open(agg_file, "w") as f:
            json.dump({
                "name": "data-wise",
                "plugins": [{"name": "craft", "version": "2.37.0"}],
            }, f)

        exit_code_reverted, output_reverted = _run_verify(tmp, base_env)
        assert exit_code_reverted == 0, (
            f"Correct name in aggregator must exit 0, got {exit_code_reverted}:\n{output_reverted}"
        )
