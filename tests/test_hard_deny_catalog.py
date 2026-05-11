#!/usr/bin/env python3
"""
Contract test for scripts/hard-deny-rules.json (v2.33.0).

The catalog is the canonical source consumed by /craft:git:protect (Phase 3)
to merge prose rules into ~/.claude/settings.json autoMode.hard_deny.
A broken catalog breaks the installer, so we lock the shape here.
"""

from __future__ import annotations

import json
import pathlib
import unittest

import pytest

pytestmark = [pytest.mark.dogfood]

CRAFT_ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG = CRAFT_ROOT / "scripts" / "hard-deny-rules.json"

REQUIRED_RULE_KEYS = {"id", "rule", "category", "rationale", "patterns_caught"}
REQUIRED_CARRYOVER_KEYS = {"id", "category", "rationale", "patterns_caught"}
VALID_CATEGORIES = {"hard_deny", "branch-guard-smart"}


class TestHardDenyCatalog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CATALOG.read_text(encoding="utf-8"))

    def test_top_level_shape(self):
        for key in ("version", "applies_to", "inherits_defaults",
                    "defaults_marker", "rules", "left_to_branch_guard_smart_mode"):
            self.assertIn(key, self.data, msg=f"missing top-level key: {key}")
        self.assertTrue(self.data["inherits_defaults"])
        self.assertEqual(self.data["defaults_marker"], "$defaults")

    def test_hard_deny_rules_nonempty(self):
        self.assertGreaterEqual(
            len(self.data["rules"]), 4,
            msg="catalog must include at least 4 hard_deny rules — the spec "
                "enumerates force-push-main, delete-git-dir, delete-github-repo, "
                "destroy-claude-config",
        )

    def test_each_rule_has_required_keys(self):
        for entry in self.data["rules"]:
            missing = REQUIRED_RULE_KEYS - entry.keys()
            self.assertFalse(
                missing,
                msg=f"rule {entry.get('id')!r} missing keys: {missing}",
            )
            self.assertEqual(entry["category"], "hard_deny")
            self.assertTrue(
                entry["rule"].startswith("Never") or entry["rule"].startswith("Refuse"),
                msg=f"rule {entry['id']!r} prose should start with 'Never' or 'Refuse'",
            )
            self.assertGreaterEqual(
                len(entry["patterns_caught"]), 1,
                msg=f"rule {entry['id']!r} must enumerate at least 1 example pattern",
            )

    def test_carryover_entries_have_required_keys(self):
        for entry in self.data["left_to_branch_guard_smart_mode"]:
            missing = REQUIRED_CARRYOVER_KEYS - entry.keys()
            self.assertFalse(
                missing,
                msg=f"carryover {entry.get('id')!r} missing keys: {missing}",
            )
            self.assertEqual(entry["category"], "branch-guard-smart")

    def test_all_ids_unique(self):
        all_ids = (
            [e["id"] for e in self.data["rules"]]
            + [e["id"] for e in self.data["left_to_branch_guard_smart_mode"]]
        )
        self.assertEqual(
            len(all_ids), len(set(all_ids)),
            msg=f"duplicate ids in catalog: {all_ids}",
        )

    def test_all_categories_valid(self):
        for entry in self.data["rules"] + self.data["left_to_branch_guard_smart_mode"]:
            self.assertIn(
                entry["category"], VALID_CATEGORIES,
                msg=f"entry {entry['id']!r} has invalid category {entry['category']!r}",
            )

    def test_required_canonical_rules_present(self):
        ids = {e["id"] for e in self.data["rules"]}
        for required in ("force-push-main", "delete-git-dir", "delete-github-repo"):
            self.assertIn(
                required, ids,
                msg=f"spec acceptance criterion requires rule id {required!r}",
            )


if __name__ == "__main__":
    unittest.main()
