#!/usr/bin/env python3
"""
Tests for scripts/docs-staleness-check.sh
==========================================
Validates the docs staleness detection script's CLI interface, JSON output
structure, exclusion config, and exit code contracts.

Run with: python3 -m pytest tests/test_docs_staleness.py -v
"""

import json
import os
import subprocess
from pathlib import Path

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.docs]

PLUGIN_DIR = Path(__file__).parent.parent
SCRIPT_PATH = PLUGIN_DIR / "scripts" / "docs-staleness-check.sh"
EXCLUSIONS_FILE = PLUGIN_DIR / "scripts" / "config" / "exclusions.txt"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REQUIRED_TOP_LEVEL_KEYS = {
    "version",
    "status",
    "phases",
    "total_issues",
    "total_warnings",
    "total_errors",
    "total_fixed",
}

REQUIRED_PHASE_KEYS = {"nav_completeness", "count_consistency", "skill_agent_coverage", "cross_doc_freshness"}

REQUIRED_PHASE_FIELD_KEYS = {"status", "issues", "findings"}

VALID_STATUS_VALUES = {"GREEN", "YELLOW", "RED"}


def _run_script(*args, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run the staleness check script from the plugin root directory."""
    return subprocess.run(
        ["bash", str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(PLUGIN_DIR),
    )


# ============================================================================
# 1. Executability
# ============================================================================

class TestScriptExecutable:
    """The script must be directly executable."""

    def test_script_file_exists(self):
        """docs-staleness-check.sh exists at expected path."""
        assert SCRIPT_PATH.exists(), f"Script not found: {SCRIPT_PATH}"

    def test_script_is_executable(self):
        """Script file has executable permission bits set."""
        assert os.access(str(SCRIPT_PATH), os.X_OK), (
            f"Script is not executable: {SCRIPT_PATH}\n"
            "Fix with: chmod +x scripts/docs-staleness-check.sh"
        )


# ============================================================================
# 2. Help / Usage
# ============================================================================

class TestHelpFlag:
    """--help must exit 0 and print usage."""

    def test_help_exits_zero(self):
        """--help returns exit code 0."""
        result = _run_script("--help")
        assert result.returncode == 0, (
            f"--help exited with {result.returncode}, expected 0\n"
            f"stderr: {result.stderr}"
        )

    def test_help_prints_usage_line(self):
        """--help output contains 'Usage:' with the script name."""
        result = _run_script("--help")
        assert "Usage:" in result.stdout, (
            "--help output should contain 'Usage:'"
        )

    def test_help_documents_all_flags(self):
        """--help output mentions all four supported flags."""
        result = _run_script("--help")
        for flag in ("--fix", "--non-interactive", "--json", "--audit-exclusions"):
            assert flag in result.stdout, (
                f"--help output missing documentation for {flag}"
            )

    def test_short_help_flag_exits_zero(self):
        """-h (short form) also returns exit code 0."""
        result = _run_script("-h")
        assert result.returncode == 0, (
            f"-h exited with {result.returncode}, expected 0"
        )


# ============================================================================
# 3. Unknown Arguments -> Exit Code 2
# ============================================================================

class TestUnknownArguments:
    """Unknown or invalid arguments must return exit code 2 (usage error)."""

    def test_unknown_flag_exits_two(self):
        """Unrecognised flag returns exit code 2."""
        result = _run_script("--unknown-arg")
        assert result.returncode == 2, (
            f"Unknown flag exited with {result.returncode}, expected 2\n"
            f"stderr: {result.stderr}"
        )

    def test_unknown_flag_prints_error_message(self):
        """Unrecognised flag prints an 'Error:' message."""
        result = _run_script("--unknown-arg")
        combined = result.stdout + result.stderr
        assert "Error" in combined or "error" in combined, (
            "Expected an error message for unknown flag, got:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_unknown_flag_suggests_help(self):
        """Unrecognised flag output references --help."""
        result = _run_script("--unknown-arg")
        combined = result.stdout + result.stderr
        assert "--help" in combined, (
            "Expected '--help' hint in error output for unknown flag"
        )

    def test_bare_positional_arg_exits_two(self):
        """A bare positional argument is treated as unknown and exits 2."""
        result = _run_script("unexpected-positional")
        assert result.returncode == 2, (
            f"Positional arg exited with {result.returncode}, expected 2"
        )


# ============================================================================
# 4. Dry-Run (Default Mode)
# ============================================================================

class TestDryRunMode:
    """Default invocation (no --fix) must not modify files and must exit 0 or 1."""

    def test_dry_run_exits_with_valid_code(self):
        """Dry-run exits with 0 (GREEN) or 1 (YELLOW/RED) — never 2."""
        result = _run_script()
        assert result.returncode in (0, 1), (
            f"Dry-run exited with {result.returncode} — expected 0 or 1\n"
            f"stderr: {result.stderr}"
        )

    def test_dry_run_prints_phase_headers(self):
        """Dry-run output mentions all four phase names."""
        result = _run_script()
        output = result.stdout + result.stderr
        for phase_label in ("Phase 6", "Phase 7", "Phase 8", "Phase 9"):
            assert phase_label in output, (
                f"Expected '{phase_label}' header in dry-run output"
            )

    def test_dry_run_prints_status_line(self):
        """Dry-run output contains a 'Status:' summary line."""
        result = _run_script()
        assert "Status:" in result.stdout, (
            "Dry-run output should contain a 'Status:' summary line"
        )

    def test_dry_run_prints_version_header(self):
        """Dry-run output contains the plugin version in the header."""
        result = _run_script()
        assert "Version:" in result.stdout, (
            "Dry-run output should contain a 'Version:' header line"
        )


# ============================================================================
# 5. JSON Output
# ============================================================================

class TestJsonOutput:
    """--json flag must emit valid, well-structured JSON."""

    @pytest.fixture(scope="class")
    def json_result(self):
        """Run with --json once and cache the parsed output."""
        result = _run_script("--json")
        assert result.returncode in (0, 1), (
            f"--json exited with unexpected code {result.returncode}\n"
            f"stderr: {result.stderr}"
        )
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            pytest.fail(
                f"--json did not produce valid JSON: {exc}\n"
                f"stdout was:\n{result.stdout[:500]}"
            )

    def test_json_exits_zero_or_one(self):
        """--json exits with 0 or 1 (never 2)."""
        result = _run_script("--json")
        assert result.returncode in (0, 1), (
            f"--json exited with {result.returncode}, expected 0 or 1"
        )

    def test_json_is_valid(self, json_result):
        """--json stdout is parseable JSON (fixture verifies parse)."""
        assert isinstance(json_result, dict), "Top-level JSON should be an object"

    def test_json_has_required_top_level_keys(self, json_result):
        """JSON output contains all required top-level keys."""
        missing = REQUIRED_TOP_LEVEL_KEYS - set(json_result.keys())
        assert not missing, (
            f"JSON output missing top-level keys: {sorted(missing)}"
        )

    def test_json_status_is_valid_value(self, json_result):
        """JSON 'status' field is one of GREEN, YELLOW, or RED."""
        status = json_result.get("status", "")
        assert status in VALID_STATUS_VALUES, (
            f"JSON 'status' is '{status}', expected one of {VALID_STATUS_VALUES}"
        )

    def test_json_version_is_string(self, json_result):
        """JSON 'version' field is a non-empty string."""
        version = json_result.get("version", "")
        assert isinstance(version, str) and version, (
            "JSON 'version' should be a non-empty string"
        )

    def test_json_numeric_fields_are_non_negative_integers(self, json_result):
        """JSON total_issues, total_warnings, total_errors, total_fixed are >= 0."""
        for field in ("total_issues", "total_warnings", "total_errors", "total_fixed"):
            value = json_result.get(field)
            assert isinstance(value, int) and value >= 0, (
                f"JSON '{field}' should be a non-negative integer, got {value!r}"
            )

    def test_json_phases_key_present(self, json_result):
        """JSON output has a 'phases' object."""
        assert "phases" in json_result, "JSON output missing 'phases' key"
        assert isinstance(json_result["phases"], dict), "'phases' should be an object"

    def test_json_contains_all_four_phase_keys(self, json_result):
        """JSON 'phases' object contains all four detection phase keys."""
        phases = json_result.get("phases", {})
        missing = REQUIRED_PHASE_KEYS - set(phases.keys())
        assert not missing, (
            f"JSON 'phases' missing keys: {sorted(missing)}\n"
            f"Present keys: {sorted(phases.keys())}"
        )

    def test_json_each_phase_has_required_fields(self, json_result):
        """Each phase object has 'status', 'issues', and 'findings' fields."""
        phases = json_result.get("phases", {})
        failures = []
        for phase_name, phase_data in phases.items():
            if not isinstance(phase_data, dict):
                failures.append(f"{phase_name}: not an object")
                continue
            missing = REQUIRED_PHASE_FIELD_KEYS - set(phase_data.keys())
            if missing:
                failures.append(f"{phase_name}: missing {sorted(missing)}")
        assert not failures, (
            "Phase field validation failures:\n" + "\n".join(failures)
        )

    def test_json_each_phase_status_is_valid(self, json_result):
        """Each phase's 'status' is one of GREEN, YELLOW, or RED."""
        phases = json_result.get("phases", {})
        invalid = []
        for phase_name, phase_data in phases.items():
            status = phase_data.get("status", "") if isinstance(phase_data, dict) else ""
            if status not in VALID_STATUS_VALUES:
                invalid.append(f"{phase_name}: '{status}'")
        assert not invalid, (
            f"Phases with invalid 'status' values: {invalid}"
        )

    def test_json_each_phase_issues_is_non_negative_int(self, json_result):
        """Each phase's 'issues' count is a non-negative integer."""
        phases = json_result.get("phases", {})
        invalid = []
        for phase_name, phase_data in phases.items():
            if not isinstance(phase_data, dict):
                continue
            issues = phase_data.get("issues")
            if not isinstance(issues, int) or issues < 0:
                invalid.append(f"{phase_name}: {issues!r}")
        assert not invalid, (
            f"Phases with invalid 'issues' values: {invalid}"
        )

    def test_json_each_phase_findings_is_list(self, json_result):
        """Each phase's 'findings' is a JSON array."""
        phases = json_result.get("phases", {})
        invalid = []
        for phase_name, phase_data in phases.items():
            if not isinstance(phase_data, dict):
                continue
            findings = phase_data.get("findings")
            if not isinstance(findings, list):
                invalid.append(f"{phase_name}: {type(findings).__name__}")
        assert not invalid, (
            f"Phases with non-list 'findings': {invalid}"
        )

    def test_json_findings_have_severity_and_file_and_message(self, json_result):
        """Every finding object in any phase contains 'severity', 'file', 'message'."""
        phases = json_result.get("phases", {})
        failures = []
        for phase_name, phase_data in phases.items():
            if not isinstance(phase_data, dict):
                continue
            for i, finding in enumerate(phase_data.get("findings", [])):
                if not isinstance(finding, dict):
                    failures.append(f"{phase_name}[{i}]: not an object")
                    continue
                for field in ("severity", "file", "message"):
                    if field not in finding:
                        failures.append(f"{phase_name}[{i}]: missing '{field}'")
        assert not failures, (
            "Finding field validation failures:\n" + "\n".join(failures)
        )

    def test_json_total_issues_equals_sum_of_phase_issues(self, json_result):
        """JSON 'total_issues' equals the sum of all phase 'issues' counts."""
        phases = json_result.get("phases", {})
        phase_sum = sum(
            p.get("issues", 0)
            for p in phases.values()
            if isinstance(p, dict)
        )
        total = json_result.get("total_issues", -1)
        assert total == phase_sum, (
            f"total_issues ({total}) != sum of phase issues ({phase_sum})"
        )

    def test_json_no_human_text_mixed_in(self):
        """--json output is pure JSON with no ANSI escape codes or prose mixed in."""
        result = _run_script("--json")
        # Check for ANSI escape code prefix
        assert "\x1b[" not in result.stdout, (
            "--json stdout contains ANSI escape codes; output must be pure JSON"
        )
        # Must start with '{' (allowing leading whitespace)
        stripped = result.stdout.strip()
        assert stripped.startswith("{"), (
            f"--json stdout must start with '{{', got: {stripped[:40]!r}"
        )


# ============================================================================
# 6. Audit Exclusions
# ============================================================================

class TestAuditExclusions:
    """--audit-exclusions must report on exclusions and exit 0."""

    def test_audit_exclusions_exits_zero(self):
        """--audit-exclusions exits with code 0."""
        result = _run_script("--audit-exclusions")
        assert result.returncode == 0, (
            f"--audit-exclusions exited with {result.returncode}, expected 0\n"
            f"stderr: {result.stderr}"
        )

    def test_audit_exclusions_prints_audit_header(self):
        """--audit-exclusions output contains 'Exclusion audit:' header."""
        result = _run_script("--audit-exclusions")
        assert "Exclusion audit" in result.stdout, (
            "--audit-exclusions output should contain 'Exclusion audit:' header"
        )

    def test_audit_exclusions_reports_each_entry(self):
        """--audit-exclusions output mentions at least one exclusion entry."""
        result = _run_script("--audit-exclusions")
        # Each entry shows either "OK" or "!!" prefix
        has_ok = "OK" in result.stdout
        has_bad = "!!" in result.stdout
        assert has_ok or has_bad, (
            "--audit-exclusions should report each entry with 'OK' or '!!'"
        )

    def test_audit_exclusions_does_not_exit_with_two(self):
        """--audit-exclusions is not treated as an unknown argument."""
        result = _run_script("--audit-exclusions")
        assert result.returncode != 2, (
            "--audit-exclusions should not exit 2 (usage error)"
        )


# ============================================================================
# 7. Exclusion Config File
# ============================================================================

class TestExclusionConfig:
    """The exclusions.txt config file must exist and be well-formed."""

    def test_exclusions_file_exists(self):
        """scripts/config/exclusions.txt exists."""
        assert EXCLUSIONS_FILE.exists(), (
            f"Exclusions file not found: {EXCLUSIONS_FILE}"
        )

    def test_exclusions_file_is_non_empty(self):
        """exclusions.txt contains at least one non-comment, non-blank line."""
        content = EXCLUSIONS_FILE.read_text()
        active_lines = [
            line for line in content.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        assert len(active_lines) > 0, (
            "exclusions.txt has no active entries (only comments or blank lines)"
        )

    def test_exclusions_file_has_no_binary_content(self):
        """exclusions.txt is valid UTF-8 text with no null bytes."""
        raw = EXCLUSIONS_FILE.read_bytes()
        assert b"\x00" not in raw, "exclusions.txt contains null bytes"
        raw.decode("utf-8")  # raises if not valid UTF-8

    def test_exclusions_file_entries_are_parseable(self):
        """Every active line is a valid exclusion format (file, dir/, or file:pattern).

        Valid formats:
          docs/some/file.md              -- whole-file exclusion (no spaces allowed)
          docs/some/dir/                 -- directory exclusion (trailing slash, no spaces)
          docs/some/file.md:some pattern -- pattern exclusion (space OK in pattern part after ':')
        """
        content = EXCLUSIONS_FILE.read_text()
        malformed = []
        for lineno, line in enumerate(content.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            # Strip inline comments
            entry = stripped.split("#")[0].strip()
            if not entry:
                continue
            # For file:pattern entries, spaces are valid in the pattern portion
            if ":" in entry:
                file_part = entry.split(":")[0]
                # The file portion (before ':') must not contain spaces
                if " " in file_part:
                    malformed.append(
                        f"line {lineno}: space in file portion of pattern entry: {entry!r}"
                    )
            else:
                # Bare file or dir/ entries must not contain spaces at all
                if " " in entry:
                    malformed.append(
                        f"line {lineno}: unexpected whitespace in entry: {entry!r}"
                    )
        assert not malformed, (
            "Malformed exclusion entries:\n" + "\n".join(malformed)
        )

    def test_exclusions_file_whole_file_entries_reference_real_files_or_dirs(self):
        """Whole-file exclusion entries (no colon, no trailing slash) point to existing files."""
        content = EXCLUSIONS_FILE.read_text()
        missing = []
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            entry = stripped.split("#")[0].strip()
            if not entry:
                continue
            # Only check whole-file entries (no ':' and no trailing '/')
            if ":" not in entry and not entry.endswith("/"):
                target = PLUGIN_DIR / entry
                if not target.exists():
                    missing.append(entry)
        assert not missing, (
            "Whole-file exclusion entries pointing to non-existent files:\n"
            + "\n".join(missing)
        )

    def test_exclusions_file_directory_entries_reference_real_dirs(self):
        """Directory exclusion entries (trailing slash) point to existing directories."""
        content = EXCLUSIONS_FILE.read_text()
        missing = []
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            entry = stripped.split("#")[0].strip()
            if not entry:
                continue
            if entry.endswith("/"):
                target = PLUGIN_DIR / entry
                if not target.is_dir():
                    missing.append(entry)
        assert not missing, (
            "Directory exclusion entries pointing to non-existent directories:\n"
            + "\n".join(missing)
        )


# ============================================================================
# 8. Fix + Non-Interactive Mode (CI Mode)
# ============================================================================

class TestFixNonInteractiveMode:
    """--fix --non-interactive must run without hanging or error, exit 0 or 1."""

    def test_fix_non_interactive_does_not_hang(self):
        """--fix --non-interactive completes within 60 seconds."""
        result = _run_script("--fix", "--non-interactive", timeout=60)
        # If it timed out, subprocess.TimeoutExpired would be raised.
        # Reaching here means it completed.
        assert result.returncode in (0, 1), (
            f"--fix --non-interactive exited with {result.returncode}, expected 0 or 1\n"
            f"stderr: {result.stderr}"
        )

    def test_fix_non_interactive_exits_valid_code(self):
        """--fix --non-interactive exits 0 (GREEN) or 1 (YELLOW/RED)."""
        result = _run_script("--fix", "--non-interactive")
        assert result.returncode in (0, 1), (
            f"Expected exit 0 or 1, got {result.returncode}"
        )

    def test_fix_non_interactive_does_not_prompt(self):
        """--fix --non-interactive skips interactive review (no [f]ix [s]kip prompt)."""
        result = _run_script("--fix", "--non-interactive")
        # The interactive prompt contains "[f]ix  [s]kip"
        assert "[f]ix" not in result.stdout, (
            "--non-interactive mode should not display interactive fix prompts"
        )

    def test_fix_non_interactive_reports_skipped_review(self):
        """--fix --non-interactive reports that interactive review was skipped."""
        result = _run_script("--fix", "--non-interactive")
        # Should mention skipped or non-interactive
        mentions_skip = (
            "non-interactive" in result.stdout.lower()
            or "skipped" in result.stdout.lower()
            or "skip" in result.stdout.lower()
        )
        assert mentions_skip, (
            "--fix --non-interactive output should indicate interactive review was skipped"
        )

    def test_fix_non_interactive_shows_pass1_header(self):
        """--fix --non-interactive runs Pass 1 auto-fix and says so in output."""
        result = _run_script("--fix", "--non-interactive")
        assert "Pass 1" in result.stdout or "Auto-fix" in result.stdout, (
            "--fix --non-interactive output should mention Pass 1 or Auto-fix"
        )


# ============================================================================
# 9. Script Syntax
# ============================================================================

class TestScriptSyntax:
    """The script must pass bash syntax validation."""

    def test_script_passes_bash_syntax_check(self):
        """bash -n reports no syntax errors in docs-staleness-check.sh."""
        result = subprocess.run(
            ["bash", "-n", str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, (
            f"Syntax error in {SCRIPT_PATH.name}:\n{result.stderr}"
        )

    def test_script_has_shebang(self):
        """Script starts with a bash shebang line."""
        first_line = SCRIPT_PATH.read_text().split("\n", 1)[0]
        assert first_line.startswith("#!"), (
            f"Script missing shebang, first line is: {first_line!r}"
        )
        assert "bash" in first_line or "env" in first_line, (
            f"Shebang does not reference bash: {first_line!r}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
