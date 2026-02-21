#!/usr/bin/env python3
"""Tests for scripts/release-watch.py"""

import json
import os
import subprocess

import pytest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "release-watch.py")
PLUGIN_DIR = os.path.join(os.path.dirname(__file__), "..")

pytestmark = [pytest.mark.e2e, pytest.mark.dogfood]

# Skip tests that require authenticated gh CLI
requires_gh = pytest.mark.skipif(
    subprocess.run(
        ["gh", "auth", "status"], capture_output=True
    ).returncode != 0,
    reason="gh CLI not authenticated",
)


def _run_watch(*args, timeout=60):
    """Run release-watch.py with given arguments."""
    return subprocess.run(
        ["python3", SCRIPT, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=PLUGIN_DIR,
    )


class TestReleaseWatch:
    """Tests for the release-watch.py script."""

    def test_release_watch_help(self):
        """--help exits cleanly and shows usage information."""
        result = _run_watch("--help")
        assert result.returncode == 0, (
            f"--help failed with exit code {result.returncode}:\n{result.stderr[:500]}"
        )
        assert "usage" in result.stdout.lower(), (
            "Expected 'usage' in --help output"
        )

    @requires_gh
    def test_release_watch_json_valid(self):
        """--format json produces valid JSON with expected top-level keys."""
        result = _run_watch("--format", "json", "--count", "1")
        assert result.returncode == 0, (
            f"Exit code {result.returncode}:\nstderr: {result.stderr[:500]}"
        )

        data = json.loads(result.stdout)
        required_keys = {"releases_checked", "latest_version", "findings", "craft_state"}
        missing = required_keys - set(data.keys())
        assert not missing, f"Missing keys in JSON output: {missing}"

    @requires_gh
    def test_release_watch_count_flag(self):
        """--count 1 checks exactly 1 release."""
        result = _run_watch("--format", "json", "--count", "1")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["releases_checked"] == 1, (
            f"Expected 1 release checked, got {data['releases_checked']}"
        )

    @requires_gh
    def test_release_watch_findings_structure(self):
        """findings dict has expected category keys."""
        result = _run_watch("--format", "json", "--count", "1")
        assert result.returncode == 0
        data = json.loads(result.stdout)

        findings = data["findings"]
        expected_keys = {"new", "deprecated", "breaking", "fixed"}
        missing = expected_keys - set(findings.keys())
        assert not missing, f"Missing findings keys: {missing}"

        # Each category should be a list
        for key in expected_keys:
            assert isinstance(findings[key], list), (
                f"findings['{key}'] should be a list, got {type(findings[key])}"
            )

    @requires_gh
    def test_release_watch_craft_state_structure(self):
        """craft_state dict has expected keys."""
        result = _run_watch("--format", "json", "--count", "1")
        assert result.returncode == 0
        data = json.loads(result.stdout)

        craft_state = data["craft_state"]
        expected_keys = {"hardcoded_models", "agent_features"}
        missing = expected_keys - set(craft_state.keys())
        assert not missing, f"Missing craft_state keys: {missing}"
