"""Pytest wrapper for the aggregator-sync shell suite.

Behavioral tests live in ``tests/test_aggregator_sync.sh`` (temp-file
fixtures). CI runs ``pytest tests/`` but does not collect ``*.sh``, so this
wrapper shells out and surfaces pass/fail.
"""

import subprocess
from pathlib import Path

TESTS_DIR = Path(__file__).parent
SHELL_SUITE = TESTS_DIR / "test_aggregator_sync.sh"


def test_aggregator_sync_shell_suite_passes():
    result = subprocess.run(
        ["bash", str(SHELL_SUITE)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"aggregator-sync shell suite failed:\n{result.stdout}\n{result.stderr}"
    )
    assert "Failed: 0" in result.stdout, result.stdout
