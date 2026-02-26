#!/usr/bin/env python3
"""Tests for scripts/release-watch.py"""

import importlib.util
import json
import os
import subprocess
import time

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


def _load_module():
    """Import release-watch.py as a module for unit testing."""
    spec = importlib.util.spec_from_file_location("release_watch", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Load module once for unit tests
rw = _load_module()


# ---------------------------------------------------------------------------
# E2E tests (existing, preserved)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Unit tests: Cache
# ---------------------------------------------------------------------------


class TestCache:
    """Unit tests for cache layer functions."""

    def test_cache_freshness_within_ttl(self):
        """Entry within TTL should be fresh."""
        entry = {"timestamp": time.time() - 100, "data": []}
        assert rw.is_fresh(entry, "test") is True

    def test_cache_freshness_expired(self):
        """Entry past TTL should be stale."""
        entry = {"timestamp": time.time() - 90000, "data": []}
        assert rw.is_fresh(entry, "test") is False

    def test_cache_freshness_missing_timestamp(self):
        """Entry without timestamp should be stale."""
        assert rw.is_fresh({}, "test") is False
        assert rw.is_fresh(None, "test") is False

    def test_cache_creation(self, tmp_path):
        """save_cache creates file with correct permissions."""
        # Temporarily override cache path
        original_dir = rw.CACHE_DIR
        original_file = rw.CACHE_FILE
        rw.CACHE_DIR = tmp_path / "test-cache"
        rw.CACHE_FILE = rw.CACHE_DIR / "cache.json"
        try:
            rw.save_cache({"test": {"timestamp": time.time(), "data": "hello"}})
            assert rw.CACHE_FILE.exists()
            # Check permissions (owner read/write only)
            mode = oct(rw.CACHE_FILE.stat().st_mode & 0o777)
            assert mode == "0o600", f"Expected 0o600, got {mode}"
            # Verify content
            data = json.loads(rw.CACHE_FILE.read_text())
            assert data["test"]["data"] == "hello"
        finally:
            rw.CACHE_DIR = original_dir
            rw.CACHE_FILE = original_file

    def test_get_cached_returns_data_when_fresh(self):
        """get_cached returns data for fresh entries."""
        cache = {"src": {"timestamp": time.time(), "data": [1, 2, 3]}}
        result = rw.get_cached("src", cache)
        assert result == [1, 2, 3]

    def test_get_cached_returns_none_when_stale(self):
        """get_cached returns None for expired entries."""
        cache = {"src": {"timestamp": time.time() - 90000, "data": [1, 2, 3]}}
        result = rw.get_cached("src", cache)
        assert result is None

    def test_get_cached_respects_refresh(self):
        """get_cached returns None when refresh=True."""
        cache = {"src": {"timestamp": time.time(), "data": [1, 2, 3]}}
        result = rw.get_cached("src", cache, refresh=True)
        assert result is None

    def test_get_cached_respects_no_cache(self):
        """get_cached returns None when no_cache=True."""
        cache = {"src": {"timestamp": time.time(), "data": [1, 2, 3]}}
        result = rw.get_cached("src", cache, no_cache=True)
        assert result is None


# ---------------------------------------------------------------------------
# Unit tests: CHANGELOG parser
# ---------------------------------------------------------------------------


class TestChangelogParser:
    """Unit tests for CHANGELOG.md parsing."""

    def test_parse_changelog_added(self):
        """Items starting with 'Added' map to NEW category."""
        content = "# Changelog\n\n## 2.1.59\n\n- Added new `/copy` command\n"
        versions = rw.parse_changelog(content)
        assert "2.1.59" in versions
        items = versions["2.1.59"]
        assert len(items) == 1
        assert items[0]["category"] == "NEW"
        assert "Added" in items[0]["text"]

    def test_parse_changelog_fixed(self):
        """Items starting with 'Fixed' map to FIXED category."""
        content = "## 2.1.58\n\n- Fixed a crash on startup\n- Fixed memory leak\n"
        versions = rw.parse_changelog(content)
        assert "2.1.58" in versions
        assert all(item["category"] == "FIXED" for item in versions["2.1.58"])
        assert len(versions["2.1.58"]) == 2

    def test_parse_changelog_breaking(self):
        """Items starting with 'Removed' map to BREAKING category."""
        content = "## 3.0.0\n\n- Removed legacy API support\n"
        versions = rw.parse_changelog(content)
        assert versions["3.0.0"][0]["category"] == "BREAKING"

    def test_parse_changelog_deprecated(self):
        """Items starting with 'Deprecated' map to DEPRECATED category."""
        content = "## 2.2.0\n\n- Deprecated old config format\n"
        versions = rw.parse_changelog(content)
        assert versions["2.2.0"][0]["category"] == "DEPRECATED"

    def test_parse_changelog_multiple_versions(self):
        """Parser handles multiple version sections."""
        content = (
            "## 2.1.59\n\n- Added feature A\n\n"
            "## 2.1.58\n\n- Fixed bug B\n\n"
            "## 2.1.57\n\n- Improved performance\n"
        )
        versions = rw.parse_changelog(content)
        assert len(versions) == 3
        assert "2.1.59" in versions
        assert "2.1.58" in versions
        assert "2.1.57" in versions

    def test_parse_changelog_empty_content(self):
        """Empty or None content returns empty dict."""
        assert rw.parse_changelog("") == {}
        assert rw.parse_changelog(None) == {}

    def test_parse_changelog_no_versions(self):
        """Content without version headers returns empty dict."""
        assert rw.parse_changelog("Just some text\nNo headers here") == {}

    def test_parse_changelog_v_prefix(self):
        """Handles v-prefixed version headers (## v2.1.59)."""
        content = "## v2.1.59\n\n- Added feature\n"
        versions = rw.parse_changelog(content)
        assert "2.1.59" in versions


# ---------------------------------------------------------------------------
# Unit tests: Word-boundary matching
# ---------------------------------------------------------------------------


class TestWordBoundary:
    """Unit tests for word-boundary keyword matching."""

    def test_word_boundary_no_false_positive(self):
        """'new' should NOT match 'renewable' or 'news'."""
        import re
        line = "renewable energy news coverage"
        # These are the keywords from new_features category
        for kw in ["new"]:
            assert not re.search(rf'\b{re.escape(kw)}\b', line), (
                f"'{kw}' should not match in '{line}'"
            )

    def test_word_boundary_matches_standalone(self):
        """'new' should match 'new feature' and 'brand new API'."""
        import re
        for line in ["new feature added", "brand new API", "this is new"]:
            assert re.search(r'\bnew\b', line), (
                f"'new' should match in '{line}'"
            )

    def test_word_boundary_fixed_no_false_positive(self):
        """'fix' should NOT match 'prefix' or 'fixture'."""
        import re
        for line in ["prefix notation", "test fixture setup"]:
            assert not re.search(r'\bfix\b', line), (
                f"'fix' should not match in '{line}'"
            )

    def test_word_boundary_fixed_matches(self):
        """'fixed' should match 'Fixed a bug' and 'bug fixed'."""
        import re
        for line in ["Fixed a bug in login", "the bug was fixed"]:
            assert re.search(r'\bfixed\b', line.lower()), (
                f"'fixed' should match in '{line}'"
            )

    def test_scan_releases_uses_word_boundary(self):
        """scan_releases should NOT produce findings for substring matches."""
        # Text contains "renewable" (has "new") and "prefix" (has "fix")
        # but NO standalone keywords — word-boundary should prevent matching.
        releases = [{
            "tag_name": "v1.0.0",
            "body": "- Improved renewable energy efficiency\n- Updated prefix notation\n",
        }]
        findings = rw.scan_releases(releases)
        all_summaries = []
        for cat in findings.values():
            all_summaries.extend(item["summary"] for item in cat)
        assert len(all_summaries) == 0, (
            f"Word-boundary should prevent substring matches, got: {all_summaries}"
        )


# ---------------------------------------------------------------------------
# Unit tests: Desktop source
# ---------------------------------------------------------------------------


class TestDesktopSource:
    """Unit tests for Desktop release parsing and security."""

    def test_desktop_source_tag(self):
        """All Desktop entries must be source-tagged as 'anthropic-docs'."""
        entries = [
            {"date": "Feb 25, 2026", "title": "New plugin support", "body": "Plugin marketplace", "source": "anthropic-docs"},
        ]
        findings = rw.scan_desktop_releases(entries)
        for cat, items in findings.items():
            for item in items:
                assert item["source"] == "anthropic-docs", (
                    f"Desktop finding should have source='anthropic-docs', got '{item['source']}'"
                )

    def test_desktop_excluded_from_autofix(self):
        """Desktop findings must NEVER be classified as safe for auto-fix."""
        # Create findings with Desktop source
        findings = {
            "NEW": [
                {"version": "Feb 25", "category": "NEW", "summary": "model update",
                 "keywords": ["model", "sonnet"], "source": "anthropic-docs",
                 "raw_line": "claude-sonnet-5-0 support added"},
            ],
            "DEPRECATED": [], "BREAKING": [], "FIXED": [],
        }
        safe, review = rw.classify_action_items(findings)
        assert len(safe) == 0, "Desktop findings should never be in safe list"
        assert len(review) == 1, "Desktop findings should be in review list"

    def test_parse_desktop_html_basic(self):
        """HTML parser extracts date-based entries."""
        html = """
        <h3>February 25, 2026</h3>
        <p><strong>New plugin feature</strong></p>
        <p>Details about the plugin feature.</p>
        <h3>February 24, 2026</h3>
        <p><strong>Another update</strong></p>
        <p>More details here.</p>
        """
        entries = rw._parse_desktop_html(html)
        assert len(entries) == 2
        assert entries[0]["date"] == "February 25, 2026"
        assert entries[0]["source"] == "anthropic-docs"
        assert entries[1]["date"] == "February 24, 2026"

    def test_parse_desktop_html_empty(self):
        """Empty HTML returns empty list."""
        assert rw._parse_desktop_html("") == []

    def test_parse_desktop_html_no_dates(self):
        """HTML without date headers returns empty list."""
        html = "<h3>Some Other Header</h3><p>Content</p>"
        assert rw._parse_desktop_html(html) == []


# ---------------------------------------------------------------------------
# Unit tests: Auto-fix classifier
# ---------------------------------------------------------------------------


class TestAutoFix:
    """Unit tests for auto-fix classification and patch generation."""

    def test_classify_breaking_as_review(self):
        """Breaking changes should always be in review, never safe."""
        findings = {
            "NEW": [], "DEPRECATED": [],
            "BREAKING": [{"version": "v3.0", "category": "BREAKING",
                          "summary": "removed API", "keywords": ["removed"],
                          "source": "github", "raw_line": "removed old API"}],
            "FIXED": [],
        }
        safe, review = rw.classify_action_items(findings)
        assert len(safe) == 0
        assert len(review) == 1
        assert review[0]["category"] == "BREAKING"

    def test_classify_deprecated_as_review(self):
        """Deprecated items should always be in review."""
        findings = {
            "NEW": [],
            "DEPRECATED": [{"version": "v2.5", "category": "DEPRECATED",
                            "summary": "old format", "keywords": ["deprecated"],
                            "source": "github", "raw_line": "deprecated old format"}],
            "BREAKING": [], "FIXED": [],
        }
        safe, review = rw.classify_action_items(findings)
        assert len(safe) == 0
        assert len(review) == 1

    def test_classify_model_update_as_safe(self):
        """Model-related NEW items from GitHub are safe for auto-fix."""
        findings = {
            "NEW": [{"version": "v2.2", "category": "NEW",
                      "summary": "new model claude-sonnet-5",
                      "keywords": ["model", "sonnet"],
                      "source": "github",
                      "raw_line": "Added claude-sonnet-5-0 model support"}],
            "DEPRECATED": [], "BREAKING": [], "FIXED": [],
        }
        safe, review = rw.classify_action_items(findings)
        assert len(safe) == 1
        assert safe[0]["keywords"] == ["model", "sonnet"]


# ---------------------------------------------------------------------------
# Unit tests: Backward compatibility
# ---------------------------------------------------------------------------


class TestBackwardCompat:
    """Tests ensuring --product code maintains v1 compatibility."""

    @requires_gh
    def test_v1_json_compat(self):
        """--product code --format json output is parseable by v1 consumers."""
        result = _run_watch("--product", "code", "--format", "json", "--count", "1")
        assert result.returncode == 0
        data = json.loads(result.stdout)

        # v1 required keys must still be present
        assert "releases_checked" in data
        assert "latest_version" in data
        assert "findings" in data
        assert "craft_state" in data

        # findings structure unchanged
        for key in ("new", "deprecated", "breaking", "fixed"):
            assert key in data["findings"]
            assert isinstance(data["findings"][key], list)

        # No desktop section when product=code
        assert "desktop" not in data

    @requires_gh
    def test_json_v2_has_version_field(self):
        """JSON v2 output includes version: 2 field."""
        result = _run_watch("--format", "json", "--count", "1")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data.get("version") == 2

    @requires_gh
    def test_product_code_no_desktop(self):
        """--product code should not include desktop data."""
        result = _run_watch("--product", "code", "--format", "json", "--count", "1")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["product"] == "code"
        assert "desktop" not in data
