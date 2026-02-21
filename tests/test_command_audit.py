#!/usr/bin/env python3
"""Tests for scripts/command-audit.sh"""

import json
import os
import subprocess

import pytest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "command-audit.sh")
PLUGIN_DIR = os.path.join(os.path.dirname(__file__), "..")

pytestmark = [pytest.mark.e2e, pytest.mark.dogfood]


def _run_audit(*args, timeout=60):
    """Run command-audit.sh with given arguments."""
    return subprocess.run(
        ["bash", SCRIPT, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=PLUGIN_DIR,
    )


class TestCommandAudit:
    """Tests for the command-audit.sh script."""

    def test_audit_runs_without_error(self):
        """command-audit.sh runs without a bash error (exit 0, 1, or 2 are acceptable)."""
        result = _run_audit()
        assert result.returncode in (0, 1, 2), (
            f"Unexpected exit code {result.returncode}:\n"
            f"stdout: {result.stdout[:500]}\nstderr: {result.stderr[:500]}"
        )

    def test_audit_json_output_valid(self):
        """--format json produces valid JSON with expected keys."""
        result = _run_audit("--format", "json")
        assert result.returncode in (0, 1, 2), (
            f"Unexpected exit code {result.returncode}:\nstderr: {result.stderr[:500]}"
        )

        data = json.loads(result.stdout)
        required_keys = {"files_scanned", "errors", "warnings", "health_score"}
        missing = required_keys - set(data.keys())
        assert not missing, f"Missing keys in JSON output: {missing}"

    def test_audit_health_score_range(self):
        """Health score is between 0 and 100."""
        result = _run_audit("--format", "json")
        data = json.loads(result.stdout)
        score = data["health_score"]
        assert 0 <= score <= 100, f"Health score {score} is out of range [0, 100]"

    def test_audit_produces_consistent_counts(self):
        """Error and warning counts match the length of their arrays."""
        result = _run_audit("--format", "json")
        data = json.loads(result.stdout)
        assert data["error_count"] == len(data["errors"]), (
            f"error_count ({data['error_count']}) != len(errors) ({len(data['errors'])})"
        )
        assert data["warning_count"] == len(data["warnings"]), (
            f"warning_count ({data['warning_count']}) != len(warnings) ({len(data['warnings'])})"
        )

    def test_audit_strict_mode(self):
        """--strict treats warnings as errors, exit code 2 when issues exist."""
        result = _run_audit("--format", "json", "--strict")
        # In strict mode, any warnings or errors should yield exit code 2
        data = json.loads(result.stdout)
        total_issues = data["error_count"] + data["warning_count"]
        if total_issues > 0:
            assert result.returncode == 2, (
                f"Expected exit code 2 in strict mode with {total_issues} issues, "
                f"got {result.returncode}"
            )
        else:
            assert result.returncode == 0

    def test_audit_fix_mode_dry(self):
        """--fix flag is accepted and doesn't crash."""
        # Run with --format json so we can parse output; --fix may modify files
        # but we just verify it doesn't crash
        result = _run_audit("--format", "json", "--fix")
        assert result.returncode in (0, 1, 2), (
            f"--fix crashed with exit code {result.returncode}:\n"
            f"stderr: {result.stderr[:500]}"
        )
        # Verify output is still valid JSON
        data = json.loads(result.stdout)
        assert "files_scanned" in data

    def test_audit_scans_all_directories(self):
        """Audit scans a reasonable number of files (commands + skills + agents)."""
        result = _run_audit("--format", "json")
        data = json.loads(result.stdout)
        assert data["files_scanned"] > 50, (
            f"Expected > 50 files scanned, got {data['files_scanned']}. "
            "Are commands/, skills/, agents/ directories being scanned?"
        )
