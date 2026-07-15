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
        # delete-git-dir moved OUT of hard_deny into left_to_branch_guard_smart_mode
        # 2026-07-14 (GRILL-branch-guard-target-resolution-2026-07-14.md decision 4):
        # hard_deny is classifier-enforced against command text only, with no git
        # execution context, so it cannot verify "same repo" — the confirm-not-block
        # carve-out this session locked in is unimplementable at that layer.
        # branch-guard.sh's own universal catastrophic check already confirms
        # `rm -rf .git` on every branch. 3 rules remain in hard_deny.
        self.assertGreaterEqual(
            len(self.data["rules"]), 3,
            msg="catalog must include at least 3 hard_deny rules — "
                "force-push-main, delete-github-repo, destroy-claude-config",
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
        for required in ("force-push-main", "delete-github-repo", "destroy-claude-config"):
            self.assertIn(
                required, ids,
                msg=f"spec acceptance criterion requires rule id {required!r}",
            )

    def test_delete_git_dir_moved_to_smart_mode_carryover(self):
        # Regression guard for the 2026-07-14 removal (see
        # test_hard_deny_rules_nonempty above for rationale): delete-git-dir
        # must NOT silently vanish — it must live in the carryover list with
        # a rationale explaining why, not just be deleted outright.
        hard_deny_ids = {e["id"] for e in self.data["rules"]}
        carryover_ids = {e["id"] for e in self.data["left_to_branch_guard_smart_mode"]}
        self.assertNotIn(
            "delete-git-dir", hard_deny_ids,
            msg="delete-git-dir should no longer be in the hard_deny (installed) rule set",
        )
        self.assertIn(
            "delete-git-dir", carryover_ids,
            msg="delete-git-dir must be documented in left_to_branch_guard_smart_mode, not deleted",
        )


if __name__ == "__main__":
    unittest.main()
