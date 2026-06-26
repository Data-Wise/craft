"""Dogfood / E2E tests for verify-surfaces.sh (Task 2) and aggregator-sync.sh --check (Task 4).

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

# Absolute path to the scripts under test — works from any CWD.
_WORKTREE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFY_SCRIPT = os.path.join(_WORKTREE, "scripts", "verify-surfaces.sh")
AGGREGATOR_SYNC = os.path.join(_WORKTREE, "scripts", "aggregator-sync.sh")
SURFACES_SCRIPT = os.path.join(_WORKTREE, "scripts", "surfaces.sh")


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
    # Prevent live cowork-store glob from touching the real machine state.
    env.setdefault("SURFACES_COWORK_STORE", "/nonexistent/cowork_store")
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


# ---------------------------------------------------------------------------
# FIX 4: surfaces.sh --report execute tests (real matrix, not null skeleton)
# ---------------------------------------------------------------------------

def _run_report(sandbox_dir: str, env_overrides: dict, extra_args: list | None = None) -> tuple[int, str]:
    """Run surfaces.sh --report in sandbox_dir; return (exit_code, combined_output)."""
    env = os.environ.copy()
    env["SURFACES_REPO_DIR"] = sandbox_dir
    env.setdefault("SURFACES_COWORK_STORE", "/nonexistent/cowork_store")
    env.update(env_overrides)
    cmd = ["bash", SURFACES_SCRIPT, "--report"] + (extra_args or [])
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)
    output = re.sub(r'\033\[[0-9;]*m', '', result.stdout + result.stderr)
    return result.returncode, output


@pytest.mark.e2e
@pytest.mark.dogfood
def test_report_produces_real_matrix_not_null():
    """surfaces.sh --report must emit a real surface matrix with version + state rows.

    This is the primary regression guard for FIX 1: the matrix must NOT be a null
    skeleton. At least one surface row must appear with a real version string or a
    known state label (✓/✗/—/!). The word 'null' must not appear in the output.
    """
    with tempfile.TemporaryDirectory() as tmp:
        _make_plugin_sandbox(tmp, "2.37.0")
        installed = _make_installed_plugins(tmp, "2.37.0")
        cowork_store = _make_cowork_store(tmp, "2.37.0")
        agg_file = os.path.join(tmp, "aggregator.json")
        with open(agg_file, "w") as f:
            json.dump({
                "name": "data-wise",
                "plugins": [{"name": "craft", "version": "2.37.0"}],
            }, f)

        exit_code, output = _run_report(tmp, {
            "SURFACES_GIT_TAG": "v2.37.0",
            "SURFACES_TAP_FORMULA": "/nonexistent/craft.rb",
            "SURFACES_BREW_VERSION": "2.37.0",
            "SURFACES_INSTALLED_PLUGINS": installed,
            "SURFACES_COWORK_STORE": cowork_store,
            "SURFACES_AGGREGATOR_FILE": agg_file,
        })

        # Matrix should render (exit 0 when all BLOCK legs aligned).
        assert exit_code == 0, (
            f"--report with aligned surfaces must exit 0, got {exit_code}:\n{output}"
        )
        # Real version must appear in the output.
        assert "2.37.0" in output, (
            f"--report must include the actual version '2.37.0'; got:\n{output}"
        )
        # The null-skeleton sentinel must NOT appear.
        assert "null" not in output.lower(), (
            f"--report must not emit null skeleton; got:\n{output}"
        )
        # At least one state label must appear.
        has_state = any(lbl in output for lbl in ("✓", "✗", "aligned", "MISMATCH", "absent"))
        assert has_state, (
            f"--report must include at least one state label (✓/✗/aligned/MISMATCH); got:\n{output}"
        )


@pytest.mark.e2e
@pytest.mark.dogfood
def test_report_json_flag_produces_valid_json():
    """surfaces.sh --report --json must produce valid JSON with surface rows.

    Machine-readable output must parse cleanly and include at least one surface
    entry with a 'name' and 'version' field.
    """
    with tempfile.TemporaryDirectory() as tmp:
        _make_plugin_sandbox(tmp, "2.37.0")
        installed = _make_installed_plugins(tmp, "2.37.0")
        cowork_store = _make_cowork_store(tmp, "2.37.0")

        exit_code, output = _run_report(tmp, {
            "SURFACES_GIT_TAG": "v2.37.0",
            "SURFACES_TAP_FORMULA": "/nonexistent/craft.rb",
            "SURFACES_BREW_VERSION": "2.37.0",
            "SURFACES_INSTALLED_PLUGINS": installed,
            "SURFACES_COWORK_STORE": cowork_store,
        }, extra_args=["--json"])

        # Must exit 0 (all BLOCK legs aligned).
        assert exit_code == 0, (
            f"--report --json with aligned surfaces must exit 0, got {exit_code}:\n{output}"
        )
        # Must be valid JSON.
        try:
            data = json.loads(output)
        except json.JSONDecodeError as e:
            pytest.fail(f"--report --json output is not valid JSON: {e}\nOutput:\n{output}")

        # Must include surface rows with real data.
        surfaces = data.get("surfaces", [])
        assert len(surfaces) > 0, (
            f"--report --json must include at least one surface row; got: {data}"
        )
        for row in surfaces:
            assert "name" in row, f"Each surface row must have 'name'; got: {row}"
            assert "version" in row, f"Each surface row must have 'version'; got: {row}"
        # Version must appear in at least one row.
        versions = [r.get("version", "") for r in surfaces]
        assert "2.37.0" in versions or any(v for v in versions if v and v != "—"), (
            f"At least one surface must have a real version; got versions: {versions}"
        )


# ---------------------------------------------------------------------------
# Task 4: aggregator-sync.sh --check mode dogfood tests
# ---------------------------------------------------------------------------

def _make_aggregator_fixture(tmp_dir: str, plugin: str, version: str) -> str:
    """Write a minimal aggregator marketplace.json; return its path."""
    path = os.path.join(tmp_dir, "aggregator.json")
    with open(path, "w") as f:
        json.dump({
            "name": "data-wise",
            "plugins": [{"name": plugin, "version": version}],
        }, f, indent=2)
    return path


def _run_aggregator_sync(file: str, plugin: str, version: str, extra_args: list | None = None) -> tuple[int, str]:
    """Run aggregator-sync.sh --check; return (exit_code, combined_output)."""
    cmd = ["bash", AGGREGATOR_SYNC, "--file", file, "--plugin", plugin, "--version", version] + (extra_args or [])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    output = re.sub(r'\033\[[0-9;]*m', '', result.stdout + result.stderr)
    return result.returncode, output


@pytest.mark.e2e
@pytest.mark.dogfood
def test_aggregator_sync_check_stale_reports_would_change():
    """--check on a STALE aggregator entry reports [would-change] and exits 0.

    The propagate --check leg in surfaces.sh delegates to aggregator-sync.sh --check.
    A stale entry (old != new version) must report [would-change], never write the file.
    """
    with tempfile.TemporaryDirectory() as tmp:
        agg_file = _make_aggregator_fixture(tmp, "craft", "2.36.0")
        mtime_before = os.path.getmtime(agg_file)

        exit_code, output = _run_aggregator_sync(agg_file, "craft", "2.37.0", ["--check"])

        assert exit_code == 0, (
            f"--check on stale entry must exit 0 (not write), got {exit_code}:\n{output}"
        )
        assert "[would-change]" in output, (
            f"--check on stale entry must report [would-change]; got:\n{output}"
        )
        assert "2.36.0" in output and "2.37.0" in output, (
            f"--check report must show old -> new versions; got:\n{output}"
        )
        # File must NOT be modified — --check is dry-run
        mtime_after = os.path.getmtime(agg_file)
        assert mtime_before == mtime_after, (
            "--check must not modify the aggregator file (dry-run violation)"
        )


@pytest.mark.e2e
@pytest.mark.dogfood
def test_aggregator_sync_check_current_reports_no_op():
    """--check on a CURRENT aggregator entry reports [current] and exits 0.

    When the aggregator already has the target version, --check must confirm
    no-op without writing. This is the short-circuit path the CI workflow uses.
    """
    with tempfile.TemporaryDirectory() as tmp:
        agg_file = _make_aggregator_fixture(tmp, "craft", "2.37.0")
        mtime_before = os.path.getmtime(agg_file)

        exit_code, output = _run_aggregator_sync(agg_file, "craft", "2.37.0", ["--check"])

        assert exit_code == 0, (
            f"--check on current entry must exit 0, got {exit_code}:\n{output}"
        )
        assert "[current]" in output, (
            f"--check on current entry must report [current]; got:\n{output}"
        )
        # File must NOT be modified
        mtime_after = os.path.getmtime(agg_file)
        assert mtime_before == mtime_after, (
            "--check on current entry must not touch the file"
        )


# ---------------------------------------------------------------------------
# Task 5: advisory propagate for brew + code-registered surfaces
# ---------------------------------------------------------------------------

def _run_propagate(
    surface: str,
    sandbox_dir: str,
    env_overrides: dict,
    extra_args: list | None = None,
) -> tuple[int, str]:
    """Run surfaces.sh --propagate <surface>; return (exit_code, combined_output)."""
    env = os.environ.copy()
    env["SURFACES_REPO_DIR"] = sandbox_dir
    env.update(env_overrides)
    cmd = ["bash", SURFACES_SCRIPT, "--propagate", surface] + (extra_args or [])
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    output = re.sub(r'\033\[[0-9;]*m', '', result.stdout + result.stderr)
    return result.returncode, output


@pytest.mark.e2e
@pytest.mark.dogfood
def test_brew_propagate_exits_0_when_brew_missing():
    """Advisory brew propagate exits 0 even when the brew binary is absent.

    The brew surface is WARN-gated. A missing brew binary must NEVER flip the
    exit code to 1. This is the primary advisory contract.
    """
    with tempfile.TemporaryDirectory() as tmp:
        _make_plugin_sandbox(tmp, "2.37.0")

        exit_code, output = _run_propagate(
            "brew",
            tmp,
            {"SURFACES_BREW_CMD": "/nonexistent-brew"},
        )

        assert exit_code == 0, (
            f"Advisory brew propagate must exit 0 when brew is absent, got {exit_code}:\n{output}"
        )


@pytest.mark.e2e
@pytest.mark.dogfood
def test_brew_propagate_prints_recovery_command_when_missing():
    """Advisory brew propagate prints the canonical brew recovery command when absent.

    The printed command must use 'brew' (canonical name), not the injected mock
    path — the user needs a command they can actually run.
    """
    with tempfile.TemporaryDirectory() as tmp:
        _make_plugin_sandbox(tmp, "2.37.0")

        exit_code, output = _run_propagate(
            "brew",
            tmp,
            {"SURFACES_BREW_CMD": "/nonexistent-brew"},
        )

        assert exit_code == 0, f"Must still exit 0:\n{output}"
        assert "brew upgrade" in output, (
            f"Recovery output must contain 'brew upgrade'; got:\n{output}"
        )
        assert "data-wise/tap/craft" in output, (
            f"Recovery output must reference the tap formula; got:\n{output}"
        )


@pytest.mark.e2e
@pytest.mark.dogfood
def test_brew_propagate_check_flag_prints_without_executing():
    """--check on brew propagate prints the would-run command and exits 0, no brew called."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_plugin_sandbox(tmp, "2.37.0")

        # Even with a real brew (if present), --check must not call it.
        # Use a sentinel that exits non-zero if called, to prove it wasn't invoked.
        sentinel = os.path.join(tmp, "fake-brew")
        with open(sentinel, "w") as f:
            f.write("#!/bin/sh\necho 'SENTINEL_CALLED' >&2; exit 1\n")
        os.chmod(sentinel, 0o755)

        exit_code, output = _run_propagate(
            "brew",
            tmp,
            {"SURFACES_BREW_CMD": sentinel},
            extra_args=["--check"],
        )

        assert exit_code == 0, f"--check must exit 0, got {exit_code}:\n{output}"
        assert "SENTINEL_CALLED" not in output, (
            "--check must not actually invoke the brew binary"
        )
        assert "brew upgrade" in output or "would" in output.lower() or "[check]" in output, (
            f"--check must describe what would run; got:\n{output}"
        )


@pytest.mark.e2e
@pytest.mark.dogfood
def test_code_registered_propagate_exits_0_when_claude_missing():
    """Advisory code-registered propagate exits 0 even when the claude binary is absent.

    The code-registered surface is WARN-gated. A missing claude binary must
    NEVER flip the exit code to 1.
    """
    with tempfile.TemporaryDirectory() as tmp:
        _make_plugin_sandbox(tmp, "2.37.0")

        exit_code, output = _run_propagate(
            "code-registered",
            tmp,
            {"SURFACES_CLAUDE_CMD": "/nonexistent-claude"},
        )

        assert exit_code == 0, (
            f"Advisory code-registered propagate must exit 0 when claude is absent, got {exit_code}:\n{output}"
        )


@pytest.mark.e2e
@pytest.mark.dogfood
def test_code_registered_propagate_prints_both_recovery_commands():
    """Advisory code-registered propagate prints BOTH recovery commands when claude is absent.

    marketplace update must appear BEFORE plugin update in the output,
    matching the critical ordering constraint from the post-install memory.
    """
    with tempfile.TemporaryDirectory() as tmp:
        _make_plugin_sandbox(tmp, "2.37.0")

        exit_code, output = _run_propagate(
            "code-registered",
            tmp,
            {"SURFACES_CLAUDE_CMD": "/nonexistent-claude"},
        )

        assert exit_code == 0, f"Must still exit 0:\n{output}"
        assert "marketplace update" in output or "plugin marketplace update" in output, (
            f"Recovery output must contain marketplace update command; got:\n{output}"
        )
        assert "plugin update" in output, (
            f"Recovery output must contain plugin update command; got:\n{output}"
        )
        # Order check: marketplace update must appear before plugin update
        mkt_pos = output.find("marketplace update")
        if mkt_pos == -1:
            mkt_pos = output.find("plugin marketplace update")
        plugin_pos = output.find("plugin update")
        assert mkt_pos < plugin_pos, (
            f"marketplace update must appear before plugin update in recovery output:\n{output}"
        )


@pytest.mark.e2e
@pytest.mark.dogfood
def test_code_registered_propagate_check_flag_prints_without_executing():
    """--check on code-registered propagate prints the would-run commands and exits 0."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_plugin_sandbox(tmp, "2.37.0")

        sentinel = os.path.join(tmp, "fake-claude")
        with open(sentinel, "w") as f:
            f.write("#!/bin/sh\necho 'SENTINEL_CALLED' >&2; exit 1\n")
        os.chmod(sentinel, 0o755)

        exit_code, output = _run_propagate(
            "code-registered",
            tmp,
            {"SURFACES_CLAUDE_CMD": sentinel},
            extra_args=["--check"],
        )

        assert exit_code == 0, f"--check must exit 0, got {exit_code}:\n{output}"
        assert "SENTINEL_CALLED" not in output, (
            "--check must not actually invoke the claude binary"
        )
        assert "marketplace" in output.lower() or "plugin update" in output or "[check]" in output, (
            f"--check must describe what would run; got:\n{output}"
        )
