"""Pytest wrapper for the verify-surfaces shell suite.

The behavioral tests for ``scripts/verify-surfaces.sh`` live in
``tests/test_verify_surfaces.sh`` (sandbox fixtures + injected SURFACES_* env).
CI runs ``pytest tests/`` but does not collect ``*.sh`` files, so this wrapper
shells out to the suite and surfaces its pass/fail to CI.
"""

import subprocess
from pathlib import Path

TESTS_DIR = Path(__file__).parent
SHELL_SUITE = TESTS_DIR / "test_verify_surfaces.sh"


def test_verify_surfaces_shell_suite_passes():
    """The full verify-surfaces shell suite exits 0 (all assertions pass)."""
    result = subprocess.run(
        ["bash", str(SHELL_SUITE)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"verify-surfaces shell suite failed:\n{result.stdout}\n{result.stderr}"
    )
    # Sanity: the suite actually ran its cases (not a silent no-op).
    assert "Failed: 0" in result.stdout, result.stdout
