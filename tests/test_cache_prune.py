"""Pytest wrapper for the cache-prune shell suite.

Behavioral tests for ``scripts/cache-prune.sh`` live in
``tests/test_cache_prune.sh`` (fixture CACHE_DIR, never the real ~/.claude
cache). CI runs ``pytest tests/`` but does not collect ``*.sh``, so this
wrapper shells out and surfaces pass/fail.
"""

import subprocess
from pathlib import Path

TESTS_DIR = Path(__file__).parent
SHELL_SUITE = TESTS_DIR / "test_cache_prune.sh"


def test_cache_prune_shell_suite_passes():
    """The full cache-prune shell suite exits 0 (all assertions pass)."""
    result = subprocess.run(
        ["bash", str(SHELL_SUITE)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"cache-prune shell suite failed:\n{result.stdout}\n{result.stderr}"
    )
    assert "Failed: 0" in result.stdout, result.stdout
