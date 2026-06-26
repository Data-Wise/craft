"""Integration tests for the full release-surface pipeline (Task 5, §5d).

Validates the green gate: propagate dry-run → verify → report over a fixture
set, touching NO real stores. All three phases must exit 0.

Marked integration (registered in pyproject.toml). Uses SURFACES_* overrides
so that brew, claude, git, and the aggregator are fully mocked/bypassed.
"""

import json
import os
import re
import subprocess
import tempfile

import pytest

# Absolute path to scripts under test — works from any CWD.
_WORKTREE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SURFACES_SCRIPT = os.path.join(_WORKTREE, "scripts", "surfaces.sh")
VERIFY_SCRIPT = os.path.join(_WORKTREE, "scripts", "verify-surfaces.sh")


# ---------------------------------------------------------------------------
# Fixture helpers
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


def _make_aggregator_file(tmp_dir: str, version: str) -> str:
    """Write a minimal aggregator marketplace.json; return its path."""
    path = os.path.join(tmp_dir, "aggregator.json")
    with open(path, "w") as f:
        json.dump({
            "name": "data-wise",
            "plugins": [{"name": "craft", "version": version}],
        }, f, indent=2)
    return path


def _run_script(args: list[str], env_overrides: dict) -> tuple[int, str]:
    """Run a shell script with env overrides; return (exit_code, combined_output)."""
    env = os.environ.copy()
    env.update(env_overrides)
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    output = re.sub(r'\033\[[0-9;]*m', '', result.stdout + result.stderr)
    return result.returncode, output


# ---------------------------------------------------------------------------
# §5d: full pipeline — propagate dry-run → verify → report
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_full_pipeline_propagate_check_verify_report_exits_0():
    """Full pipeline: propagate --check → verify → report all exit 0 without touching real stores.

    This is the §5d green gate. Three phases over a consistent fixture set:
    1. surfaces.sh --propagate <surface> --check for each actionable surface
    2. surfaces.sh --verify against aligned fixtures
    3. surfaces.sh --report (registry dump, always informational)

    None of these may touch real brew, real claude, or real aggregator stores.
    """
    version = "2.37.0"

    with tempfile.TemporaryDirectory() as tmp:
        _make_plugin_sandbox(tmp, version)
        installed = _make_installed_plugins(tmp, version)
        cowork_store = _make_cowork_store(tmp, version)
        agg_file = _make_aggregator_file(tmp, version)

        # Sentinel binaries: exit 1 if ever called (proves --check is dry-run)
        brew_sentinel = os.path.join(tmp, "fake-brew")
        with open(brew_sentinel, "w") as f:
            f.write("#!/bin/sh\necho 'BREW_SENTINEL_CALLED' >&2; exit 1\n")
        os.chmod(brew_sentinel, 0o755)

        claude_sentinel = os.path.join(tmp, "fake-claude")
        with open(claude_sentinel, "w") as f:
            f.write("#!/bin/sh\necho 'CLAUDE_SENTINEL_CALLED' >&2; exit 1\n")
        os.chmod(claude_sentinel, 0o755)

        # Base env that prevents any real store access
        base_env = {
            "SURFACES_REPO_DIR": tmp,
            "SURFACES_GIT_TAG": f"v{version}",
            "SURFACES_TAP_FORMULA": "/nonexistent/craft.rb",
            "SURFACES_BREW_VERSION": version,
            "SURFACES_INSTALLED_PLUGINS": installed,
            "SURFACES_COWORK_STORE": cowork_store,
            "SURFACES_AGGREGATOR_FILE": agg_file,
            "SURFACES_BREW_CMD": brew_sentinel,
            "SURFACES_CLAUDE_CMD": claude_sentinel,
        }

        # Phase 1a: brew propagate --check
        exit_code, output = _run_script(
            ["bash", SURFACES_SCRIPT, "--propagate", "brew", "--check"],
            base_env,
        )
        assert exit_code == 0, f"brew propagate --check must exit 0, got {exit_code}:\n{output}"
        assert "BREW_SENTINEL_CALLED" not in output, (
            "brew propagate --check must NOT invoke the brew binary"
        )

        # Phase 1b: code-registered propagate --check
        exit_code, output = _run_script(
            ["bash", SURFACES_SCRIPT, "--propagate", "code-registered", "--check"],
            base_env,
        )
        assert exit_code == 0, (
            f"code-registered propagate --check must exit 0, got {exit_code}:\n{output}"
        )
        assert "CLAUDE_SENTINEL_CALLED" not in output, (
            "code-registered propagate --check must NOT invoke the claude binary"
        )

        # Phase 1c: aggregator propagate --check (already tested in Task 4; regression guard)
        exit_code, output = _run_script(
            ["bash", SURFACES_SCRIPT, "--propagate", "aggregator", "--check",
             "--file", agg_file],
            base_env,
        )
        assert exit_code == 0, (
            f"aggregator propagate --check must exit 0, got {exit_code}:\n{output}"
        )

        # Phase 2: verify (all BLOCK surfaces aligned)
        exit_code, output = _run_script(
            ["bash", SURFACES_SCRIPT, "--verify"],
            base_env,
        )
        assert exit_code == 0, (
            f"verify must exit 0 when all BLOCK surfaces are aligned, got {exit_code}:\n{output}"
        )

        # Phase 3: report (always informational, never blocks)
        exit_code, output = _run_script(
            ["bash", SURFACES_SCRIPT, "--report"],
            base_env,
        )
        assert exit_code == 0, (
            f"report must exit 0, got {exit_code}:\n{output}"
        )


@pytest.mark.integration
def test_advisory_propagate_never_blocks_on_absent_binaries():
    """Advisory surfaces never flip exit 1 even when both brew and claude are absent.

    Validates the core WARN-only contract independently of the full pipeline:
    each advisory propagate surface exits 0 when the external binary is absent
    or non-executable.
    """
    version = "2.52.0"

    with tempfile.TemporaryDirectory() as tmp:
        _make_plugin_sandbox(tmp, version)

        base_env = {
            "SURFACES_REPO_DIR": tmp,
            "SURFACES_BREW_CMD": "/nonexistent-brew",
            "SURFACES_CLAUDE_CMD": "/nonexistent-claude",
        }

        for surface in ("brew", "code-registered"):
            exit_code, output = _run_script(
                ["bash", SURFACES_SCRIPT, "--propagate", surface],
                base_env,
            )
            assert exit_code == 0, (
                f"Advisory surface '{surface}' must exit 0 when binary absent, "
                f"got {exit_code}:\n{output}"
            )
