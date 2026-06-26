#!/usr/bin/env python3
"""
E2E tests for /craft:dist:surfaces command (Task 3 — release-multisurface).

Checks:
- commands/dist/surfaces.md exists
- Frontmatter is valid YAML with category: dist
- Arguments block declares --json and --owner flags
"""

import pytest
import yaml
from pathlib import Path

# Re-use the canonical PLUGIN_DIR from the main e2e module
from test_plugin_e2e import PLUGIN_DIR

pytestmark = [pytest.mark.e2e]

SURFACES_CMD = PLUGIN_DIR / "commands" / "dist" / "surfaces.md"


def _parse_frontmatter(path: Path) -> dict:
    """Extract and parse YAML frontmatter from a command .md file."""
    text = path.read_text()
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    return yaml.safe_load(parts[1]) or {}


class TestSurfacesCommandExists:
    """commands/dist/surfaces.md must exist and be non-empty."""

    def test_file_exists(self):
        assert SURFACES_CMD.exists(), (
            f"commands/dist/surfaces.md not found at {SURFACES_CMD}"
        )

    def test_file_not_empty(self):
        assert SURFACES_CMD.stat().st_size > 0, "surfaces.md is empty"


class TestSurfacesFrontmatter:
    """Frontmatter must be valid and carry category: dist."""

    def test_has_frontmatter(self):
        fm = _parse_frontmatter(SURFACES_CMD)
        assert fm, "surfaces.md has no parseable YAML frontmatter"

    def test_category_is_dist(self):
        fm = _parse_frontmatter(SURFACES_CMD)
        assert fm.get("category") == "dist", (
            f"Expected category: dist, got: {fm.get('category')!r}"
        )

    def test_has_description(self):
        fm = _parse_frontmatter(SURFACES_CMD)
        assert fm.get("description"), "surfaces.md frontmatter missing description"


class TestSurfacesArguments:
    """Arguments block must declare --json and --owner."""

    def _arg_names(self) -> list[str]:
        fm = _parse_frontmatter(SURFACES_CMD)
        args = fm.get("arguments", [])
        return [a.get("name", "") for a in args if isinstance(a, dict)]

    def test_declares_json_argument(self):
        names = self._arg_names()
        assert "json" in names, (
            f"surfaces.md arguments block missing 'json'; found: {names}"
        )

    def test_declares_owner_argument(self):
        names = self._arg_names()
        assert "owner" in names, (
            f"surfaces.md arguments block missing 'owner'; found: {names}"
        )


# ---------------------------------------------------------------------------
# Task 4: aggregator-sync.yml workflow assertions
# ---------------------------------------------------------------------------

AGGREGATOR_WORKFLOW = PLUGIN_DIR / ".github" / "workflows" / "aggregator-sync.yml"


def _workflow_text() -> str:
    return AGGREGATOR_WORKFLOW.read_text()


def _workflow_yaml() -> dict:
    return yaml.safe_load(_workflow_text())


class TestAggregatorSyncWorkflowExists:
    """The aggregator-sync.yml workflow file must exist and be valid YAML."""

    def test_file_exists(self):
        assert AGGREGATOR_WORKFLOW.exists(), (
            f"aggregator-sync.yml not found at {AGGREGATOR_WORKFLOW}"
        )

    def test_valid_yaml(self):
        assert AGGREGATOR_WORKFLOW.exists(), "workflow file missing (see test_file_exists)"
        data = _workflow_yaml()
        assert isinstance(data, dict), "aggregator-sync.yml is not a valid YAML mapping"


class TestAggregatorSyncWorkflowTrigger:
    """Workflow must trigger on release: published (not push, not dispatch)."""

    def test_triggers_on_release_published(self):
        assert AGGREGATOR_WORKFLOW.exists(), "workflow file missing"
        data = _workflow_yaml()
        on = data.get("on") or data.get(True)  # 'on' parsed as True in PyYAML
        assert on is not None, "workflow missing 'on:' trigger block"
        release = on.get("release") if isinstance(on, dict) else None
        assert release is not None, (
            f"workflow 'on:' block must contain 'release:' trigger; found: {list(on.keys()) if isinstance(on, dict) else on}"
        )
        types = release.get("types", []) if isinstance(release, dict) else []
        assert "published" in types, (
            f"workflow release trigger must include 'published'; found types: {types}"
        )


class TestAggregatorSyncWorkflowSecrets:
    """Workflow must reference APP_ID and APP_PRIVATE_KEY secrets for GitHub App auth."""

    def test_references_app_id_secret(self):
        assert AGGREGATOR_WORKFLOW.exists(), "workflow file missing"
        text = _workflow_text()
        assert "APP_ID" in text, (
            "aggregator-sync.yml must reference secrets.APP_ID for GitHub App auth"
        )

    def test_references_app_private_key_secret(self):
        assert AGGREGATOR_WORKFLOW.exists(), "workflow file missing"
        text = _workflow_text()
        assert "APP_PRIVATE_KEY" in text, (
            "aggregator-sync.yml must reference secrets.APP_PRIVATE_KEY for GitHub App auth"
        )


class TestAggregatorSyncWorkflowFailLoud:
    """Workflow must fail loud: non-zero exit if PR opens but does not merge."""

    def test_contains_admin_merge(self):
        assert AGGREGATOR_WORKFLOW.exists(), "workflow file missing"
        text = _workflow_text()
        assert "--admin" in text, (
            "aggregator-sync.yml must use 'gh pr merge --admin' to bypass branch protection"
        )

    def test_verifies_merged_state(self):
        """Must verify the PR actually merged — not just that the merge command ran."""
        assert AGGREGATOR_WORKFLOW.exists(), "workflow file missing"
        text = _workflow_text()
        # Workflow must contain BOTH: the merged-state comparison AND the fail-loud exit 1.
        # The vacuous "or 'state' in text" was removed — "state" appears everywhere.
        # These two substrings together gate the exact fail-loud block that craft#218 introduced.
        assert '"MERGED"' in text and "exit 1" in text, (
            "aggregator-sync.yml must contain the fail-loud block: "
            "'MERGED' state comparison AND 'exit 1' (craft#218 regression guard)"
        )
