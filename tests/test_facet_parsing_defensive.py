#!/usr/bin/env python3
"""
Behavioral + structural regression tests for the facet-parsing defensive
contract documented in `commands/workflow/insights.md` (v2.33.0).

Two real facet-reader snippets exist in the repo:
  - `commands/hub.md`  Step 1.7  (Recently Used footer)
  - `commands/do.md`   Step 1.5  (Insights Check)

Both must tolerate malformed facet files: catch the documented exception set,
log a stderr warning, and continue. This test runs the hub.md snippet as a
subprocess against a corrupt fixtures directory and asserts both files
document the contract structurally.
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

import pytest

pytestmark = [pytest.mark.dogfood]

CRAFT_ROOT = pathlib.Path(__file__).resolve().parent.parent
HUB_MD = CRAFT_ROOT / "commands" / "hub.md"
DO_MD = CRAFT_ROOT / "commands" / "do.md"
INSIGHTS_MD = CRAFT_ROOT / "commands" / "workflow" / "insights.md"

REQUIRED_EXCEPTIONS = (
    "json.JSONDecodeError",
    "KeyError",
    "TypeError",
    "FileNotFoundError",
    "UnicodeDecodeError",
    "OSError",
)


def _extract_python_block(md_path: pathlib.Path, anchor: str) -> str:
    """Return the first ```python ... ``` fenced block after `anchor`."""
    text = md_path.read_text(encoding="utf-8")
    idx = text.find(anchor)
    if idx < 0:
        raise AssertionError(f"anchor {anchor!r} not found in {md_path}")
    match = re.search(r"```python\n(.*?)\n```", text[idx:], flags=re.DOTALL)
    if not match:
        raise AssertionError(f"no python block after anchor in {md_path}")
    return match.group(1)


def _write_corrupt_facets(d: pathlib.Path) -> None:
    """Drop one valid + three malformed facets into `d`."""
    (d / "session-001-valid.json").write_text(
        json.dumps({"commands_used": ["/craft:do", "/craft:check", "/craft:do"]}),
        encoding="utf-8",
    )
    # truncated JSON
    (d / "session-002-truncated.json").write_text(
        '{"commands_used": ["/craft:do"', encoding="utf-8"
    )
    # binary garbage (UnicodeDecodeError on read)
    (d / "session-003-binary.json").write_bytes(b"\x00\x01\x02 not json at all \xff\xfe")
    # wrong shape — commands_used is not iterable-of-strings
    (d / "session-004-shape.json").write_text(
        json.dumps({"commands_used": 42}), encoding="utf-8"
    )


class TestHubFacetParserBehavior(unittest.TestCase):
    """Run the hub.md Step 1.7 snippet as a subprocess against corrupt fixtures."""

    def test_hub_snippet_survives_malformed_facets(self):
        snippet = _extract_python_block(HUB_MD, "### Step 1.7")

        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            facets = tmp / "facets"
            facets.mkdir()
            _write_corrupt_facets(facets)

            # Redirect the snippet's hard-coded facets path at the source.
            patched = snippet.replace(
                'os.path.expanduser("~/.claude/usage-data/facets/")',
                repr(str(facets)),
            )
            # Emit the resulting Counter so the test can verify it.
            patched += "\nimport json as _j\nprint(_j.dumps(dict(recent_commands)))\n"

            script = tmp / "snippet.py"
            script.write_text(patched, encoding="utf-8")

            proc = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # Subprocess must exit cleanly despite three malformed files.
            self.assertEqual(
                proc.returncode,
                0,
                msg=f"snippet crashed:\nstdout={proc.stdout}\nstderr={proc.stderr}",
            )

            counter = json.loads(proc.stdout.strip().splitlines()[-1])
            self.assertEqual(counter.get("/craft:do"), 2)
            self.assertEqual(counter.get("/craft:check"), 1)

            warnings = proc.stderr
            self.assertIn("warning: skipping malformed facet", warnings)
            self.assertIn("session-002-truncated.json", warnings)
            self.assertIn("session-003-binary.json", warnings)
            # Bad-shape file fails inside the inner for-loop (TypeError on int) —
            # must be caught by the same except block, not crash the snippet.
            self.assertIn("session-004-shape.json", warnings)


class TestFacetParserStructuralContract(unittest.TestCase):
    """Assert both real parsers document the defensive contract."""

    def _assert_contract(self, md_path: pathlib.Path, anchor: str) -> None:
        snippet = _extract_python_block(md_path, anchor)
        for exc_name in REQUIRED_EXCEPTIONS:
            self.assertIn(
                exc_name,
                snippet,
                msg=f"{md_path.name} {anchor!r} must catch {exc_name}",
            )
        self.assertIn(
            "file=sys.stderr",
            snippet,
            msg=f"{md_path.name} {anchor!r} must log warnings to stderr",
        )
        self.assertIn(
            "warning: skipping malformed facet",
            snippet,
            msg=f"{md_path.name} {anchor!r} must emit the canonical warning string",
        )

    def test_hub_md_documents_contract(self):
        self._assert_contract(HUB_MD, "### Step 1.7")

    def test_do_md_documents_contract(self):
        self._assert_contract(DO_MD, "### Step 1.5")

    def test_insights_md_publishes_contract(self):
        text = INSIGHTS_MD.read_text(encoding="utf-8")
        self.assertIn("Defensive Parsing Contract", text)
        for exc_name in REQUIRED_EXCEPTIONS:
            self.assertIn(exc_name, text)


if __name__ == "__main__":
    unittest.main()
