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
