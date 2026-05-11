#!/usr/bin/env python3
"""
Integration test for scripts/install-hard-deny.sh (v2.33.0).

Exercises the installer against a temporary settings.json (via the
HARD_DENY_SETTINGS_PATH env-var override) and verifies:
  - cold install adds $defaults + 4 craft rules
  - re-running is idempotent (zero changes)
  - uninstall removes ONLY craft rules ($defaults + user entries preserved)
  - existing top-level settings keys are preserved across install/uninstall
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tempfile
import unittest

import pytest

pytestmark = [pytest.mark.dogfood]

CRAFT_ROOT = pathlib.Path(__file__).resolve().parent.parent
INSTALLER = CRAFT_ROOT / "scripts" / "install-hard-deny.sh"
CATALOG = CRAFT_ROOT / "scripts" / "hard-deny-rules.json"


def _run(target_path: pathlib.Path, *args: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["HARD_DENY_SETTINGS_PATH"] = str(target_path)
    return subprocess.run(
        ["bash", str(INSTALLER), *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=15,
        check=False,
    )


class TestInstallHardDeny(unittest.TestCase):
    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.target = pathlib.Path(self._td.name) / "settings.json"

    def _catalog_rules(self) -> list[str]:
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
        return [
            e["rule"] for e in data["rules"] if e["category"] == "hard_deny"
        ]

    def test_cold_install_adds_defaults_and_craft_rules(self):
        rules = self._catalog_rules()

        proc = _run(self.target, "--install")
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertTrue(self.target.exists())

        settings = json.loads(self.target.read_text(encoding="utf-8"))
        installed = settings["autoMode"]["hard_deny"]
        self.assertEqual(installed[0], "$defaults", msg="$defaults must be first")
        for rule in rules:
            self.assertIn(rule, installed)
        self.assertEqual(len(installed), 1 + len(rules))

    def test_install_is_idempotent(self):
        _run(self.target, "--install")
        proc = _run(self.target, "--check", "--json")
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        # When --json is set, stdout is the structured report.
        report = json.loads(proc.stdout)
        self.assertEqual(report["would_add"], [])
        self.assertEqual(report["craft_rules_already_present"], len(self._catalog_rules()))

    def test_uninstall_preserves_user_entries(self):
        _run(self.target, "--install")
        # User adds their own rule and an unrelated top-level key.
        settings = json.loads(self.target.read_text(encoding="utf-8"))
        settings["autoMode"]["hard_deny"].append(
            "User custom rule: never run my-secret-script"
        )
        settings["otherTopLevel"] = {"keep": True}
        self.target.write_text(json.dumps(settings), encoding="utf-8")

        proc = _run(self.target, "--uninstall")
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)

        after = json.loads(self.target.read_text(encoding="utf-8"))
        remaining = after["autoMode"]["hard_deny"]
        self.assertIn("$defaults", remaining)
        self.assertIn("User custom rule: never run my-secret-script", remaining)
        for rule in self._catalog_rules():
            self.assertNotIn(rule, remaining)
        self.assertEqual(after.get("otherTopLevel"), {"keep": True})

    def test_check_on_missing_settings_file(self):
        # Target doesn't exist yet — check should still succeed and report
        # exactly the expected additions.
        self.assertFalse(self.target.exists())
        proc = _run(self.target, "--check", "--json")
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        report = json.loads(proc.stdout)
        self.assertEqual(report["current_count"], 0)
        # Would-add: $defaults + craft rules.
        self.assertEqual(len(report["would_add"]), 1 + len(self._catalog_rules()))
        # And the file was NOT created by --check.
        self.assertFalse(self.target.exists())

    def test_install_preserves_other_top_level_settings(self):
        # Pre-existing settings.json with unrelated content.
        seed = {
            "autoMode": {"hard_deny": ["Existing user rule: keep me"]},
            "permissions": {"allow": ["Bash(git status)"]},
        }
        self.target.write_text(json.dumps(seed), encoding="utf-8")

        proc = _run(self.target, "--install")
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)

        after = json.loads(self.target.read_text(encoding="utf-8"))
        self.assertIn("Existing user rule: keep me", after["autoMode"]["hard_deny"])
        self.assertEqual(after["permissions"], {"allow": ["Bash(git status)"]})
        self.assertEqual(after["autoMode"]["hard_deny"][0], "$defaults")


if __name__ == "__main__":
    unittest.main()
