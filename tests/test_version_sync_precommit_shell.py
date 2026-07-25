"""Pytest wrapper for the version-sync-precommit shell suite.

The behavioral tests for ``scripts/version-sync-precommit.sh`` live in
``tests/test_version_sync_precommit.sh`` (sandbox git repo + staged fixtures).
CI runs ``pytest tests/`` but does not collect ``*.sh`` files, so this wrapper
shells out to the suite and surfaces its pass/fail to CI. Same pattern as
tests/test_verify_surfaces.py.
"""

import subprocess
from pathlib import Path

TESTS_DIR = Path(__file__).parent
SHELL_SUITE = TESTS_DIR / "test_version_sync_precommit.sh"


def test_version_sync_precommit_shell_suite_passes():
    """The full version-sync-precommit shell suite exits 0 (all assertions pass)."""
    result = subprocess.run(
        ["bash", str(SHELL_SUITE)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"version-sync-precommit shell suite failed:\n{result.stdout}\n{result.stderr}"
    )
    # Sanity: the suite actually ran its cases (not a silent no-op).
    assert "0 failed" in result.stdout, result.stdout
