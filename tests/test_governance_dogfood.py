#!/usr/bin/env python3
"""
Governance Engine Dogfood Tests
===============================
Runs the real governance engine (``governance/run_rules.py`` and the portable
checkers) against the in-repo fixtures and exercises the behaviours that the
PR-185 review hardened:

  * ``--selftest`` meta-validation passes and surfaces the external rule.
  * a clean target audits green; a broken-symlink target audits red and exits 1.
  * **fail-closed**: an error-rule whose checker is missing must gate (exit 1),
    not pass silently.
  * the symlink checker detects *nested* broken links (recursive).
  * the duplicate-canon checker announces a vacuous skip instead of passing
    silently when the canon dirs are absent.

Hermetic: every audit is pointed at fixtures / tmp dirs, never the live
``~/.claude`` environment.

Run with: python3 -m pytest tests/test_governance_dogfood.py -v
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = [pytest.mark.e2e, pytest.mark.dogfood, pytest.mark.governance]

PLUGIN_DIR = Path(__file__).parent.parent
GOV_DIR = PLUGIN_DIR / "governance"
RUN = GOV_DIR / "run_rules.py"
CHECKS = GOV_DIR / "checks"
GOOD_FX = GOV_DIR / "fixtures" / "no-broken-symlinks" / "good"
BAD_FX = GOV_DIR / "fixtures" / "no-broken-symlinks" / "bad"
# R03 checker scans a marketplace.json; its fixtures are a good/bad pair (good =
# no private-repo ref; bad = references the private savant repo). The FILE paths
# exercise the checker's production direct-file mode.
MKT_GOOD_FX = GOV_DIR / "fixtures" / "no-private-in-public" / "good" / "marketplace.json"
MKT_BAD_FX = GOV_DIR / "fixtures" / "no-private-in-public" / "bad" / "marketplace.json"


def _run(script: Path, *args, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True, text=True, timeout=timeout, cwd=str(GOV_DIR),
    )


# ---------------------------------------------------------------------------
# 1. Meta-validation (--selftest)
# ---------------------------------------------------------------------------

class TestSelftest:
    def test_selftest_passes(self):
        result = _run(RUN, "--selftest")
        assert result.returncode == 0, (
            f"selftest reported meta-failures:\n{result.stdout}\n{result.stderr}"
        )
        assert "0 meta-failure(s)" in result.stdout

    def test_selftest_surfaces_external_rule(self):
        """R07 is delegated to skills-audit.py; selftest must name it rather than
        skip it silently (PR-185 review #5)."""
        out = _run(RUN, "--selftest").stdout
        assert "R07-version-is-truth" in out
        assert "external auditor" in out

    def test_selftest_flags_fixtured_checkers(self):
        out = _run(RUN, "--selftest").stdout
        # R02/R08 both exercise their good+bad fixtures
        for rid in ("R02-no-hand-links", "R08-no-dead-links"):
            assert rid in out and "fixtures:" in out

    def test_selftest_flags_r03_as_fixtured_not_enforcement_gap(self):
        """After R03 moves manual -> script (PR #1), selftest must exercise its
        good+bad fixtures and report 'fixtures:' for it — and must NOT emit the
        'enforcement gap' warning it used to. This proves the gap is closed."""
        out = _run(RUN, "--selftest").stdout
        r03 = [ln for ln in out.splitlines() if "R03-private-marketplace" in ln]
        assert r03, "R03 should appear in selftest output"
        assert any("fixtures:" in ln for ln in r03), f"R03 should show fixtures: {r03}"
        assert not any("enforcement gap" in ln for ln in r03), (
            f"R03 must no longer be an enforcement gap: {r03}"
        )


class TestSelftestRedCases:
    """Red cases for --selftest: the meta-gate must FAIL when a checker passes its
    own *bad* fixture, or when a waiver lacks owner/expires. Without these, a
    regression making selftest always return 0 would pass the whole suite — and
    selftest is the only thing that proves the checkers actually detect violations.
    Calls run_rules.selftest(doc) in-process (same pattern as TestFailClosed) so a
    synthetic doc can drive the failure paths."""

    def _selftest(self, doc, capsys):
        sys.path.insert(0, str(GOV_DIR))
        try:
            import run_rules  # governance/run_rules.py
            rc = run_rules.selftest(doc)
            return rc, capsys.readouterr().out
        finally:
            sys.path.remove(str(GOV_DIR))

    def test_checker_passing_its_bad_fixture_is_a_meta_failure(self, capsys):
        """A checker whose `bad` fixture does NOT make it fail is misbehaving. Here
        the bad fixture points at the *good* dir, so the symlink checker exits 0 on
        input that should have failed → selftest must flag it (exit 1)."""
        doc = {"scope": "skills", "posture": "gentle-ramp", "rules": [{
            "id": "RZZ-misbehaves", "severity": "error", "status": "active",
            "gates": ["ci"],
            "check": {
                "kind": "script",
                "cmd": "checks/no_broken_symlinks.py {target}",
                "fixtures": {
                    "good": "fixtures/no-broken-symlinks/good",
                    "bad": "fixtures/no-broken-symlinks/good",  # wrong on purpose
                },
            },
            "waivers": [],
        }]}
        rc, out = self._selftest(doc, capsys)
        assert rc == 1, "a checker that passes its bad fixture must be a meta-failure"
        assert "misbehaves" in out

    def test_waiver_missing_owner_or_expires_is_a_meta_failure(self, capsys):
        """Waiver hygiene: a waiver without owner+expires must be flagged (exit 1)."""
        doc = {"scope": "skills", "posture": "gentle-ramp", "rules": [{
            "id": "RWW-badwaiver", "severity": "warn", "status": "active",
            "gates": ["session"],
            "check": {"kind": "manual"},
            "waivers": [{"reason": "no owner, no expiry"}],
        }]}
        rc, out = self._selftest(doc, capsys)
        assert rc == 1, "a waiver lacking owner/expires must be a meta-failure"
        assert "waiver missing" in out


# ---------------------------------------------------------------------------
# 2. Audit against fixtures (clean green, broken red)
# ---------------------------------------------------------------------------

class TestAuditFixtures:
    def test_clean_target_audits_green(self):
        result = _run(RUN, "--target", str(GOOD_FX), "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["red"] == 0, f"clean fixture should be 0 red: {data}"

    def test_broken_symlink_target_audits_red(self):
        """The bad fixture holds a dead symlink → R02 and R08 (both error) fire,
        so the audit must exit 1 with red >= 1."""
        result = _run(RUN, "--target", str(BAD_FX), "--index", str(BAD_FX), "--json")
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["red"] >= 1, f"broken fixture should gate: {data}"
        failed = {r["id"] for r in data["results"] if r["state"] == "FAIL"}
        assert {"R02-no-hand-links", "R08-no-dead-links"} <= failed, (
            f"expected R02+R08 to FAIL on broken fixture, got {failed}"
        )


# ---------------------------------------------------------------------------
# 3. Fail-closed: a missing checker on an error rule must gate (review #1)
# ---------------------------------------------------------------------------

class TestFailClosed:
    def _audit(self, doc):
        sys.path.insert(0, str(GOV_DIR))
        try:
            import run_rules  # governance/run_rules.py
            return run_rules.audit(doc, target="/tmp", index="/tmp", as_json=False)
        finally:
            sys.path.remove(str(GOV_DIR))

    def test_missing_checker_on_error_rule_fails_closed(self):
        doc = {"scope": "skills", "posture": "gentle-ramp", "rules": [{
            "id": "RXX-broken", "severity": "error", "status": "active",
            "gates": ["ci"],
            "check": {"kind": "script", "cmd": "checks/does_not_exist.py {target}"},
            "waivers": [],
        }]}
        assert self._audit(doc) == 1, "broken checker on error rule must exit 1"

    def test_missing_checker_on_warn_rule_does_not_gate(self):
        doc = {"scope": "skills", "posture": "gentle-ramp", "rules": [{
            "id": "RYY-broken", "severity": "warn", "status": "active",
            "gates": ["ci"],
            "check": {"kind": "script", "cmd": "checks/does_not_exist.py {target}"},
            "waivers": [],
        }]}
        assert self._audit(doc) == 0, "broken checker on warn rule should not gate"


# ---------------------------------------------------------------------------
# 4. Checker behaviours: recursive symlinks + visible canon skip
# ---------------------------------------------------------------------------

class TestCheckers:
    def test_broken_symlink_detected_when_nested(self, tmp_path: Path):
        """Review #4: detection must be recursive, not top-level only."""
        nested = tmp_path / "skillA"
        nested.mkdir()
        (nested / "dead-ref").symlink_to("/nonexistent/deep/target")
        result = _run(CHECKS / "no_broken_symlinks.py", str(tmp_path))
        assert result.returncode == 1
        assert "skillA/dead-ref" in result.stdout

    def test_clean_tree_passes(self, tmp_path: Path):
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "ok.txt").write_text("ok", encoding="utf-8")
        assert _run(CHECKS / "no_broken_symlinks.py", str(tmp_path)).returncode == 0

    def test_archive_and_hidden_dead_links_are_ignored(self, tmp_path: Path):
        """Finding F: dead links inside `archive/` or dot-dirs are intentional
        (not load-bearing) and must NOT gate — only live broken links do."""
        for sub in ("live", "archive", ".hidden"):
            (tmp_path / sub).mkdir()
            (tmp_path / sub / "dead").symlink_to("/nonexistent")
        result = _run(CHECKS / "no_broken_symlinks.py", str(tmp_path))
        assert result.returncode == 1
        assert "live/dead" in result.stdout
        assert "archive/dead" not in result.stdout
        assert ".hidden/dead" not in result.stdout

    def test_duplicate_canon_announces_vacuous_skip(self, tmp_path: Path):
        """Review #2: when canon dirs are absent the check must say so out loud
        and pass, not pass silently."""
        result = _run(
            CHECKS / "no_duplicate_canon.py",
            str(tmp_path / "absent1"), str(tmp_path / "absent2"),
        )
        assert result.returncode == 0
        assert "skip:" in result.stdout
        assert "vacuous" in result.stdout

    def test_duplicate_canon_detects_real_duplicate(self, tmp_path: Path):
        """Two canons each containing a skill of the same name → exit 1."""
        for canon in ("canonA", "canonB"):
            skill = tmp_path / canon / "shared-skill"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("x", encoding="utf-8")
        result = _run(
            CHECKS / "no_duplicate_canon.py",
            str(tmp_path / "canonA"), str(tmp_path / "canonB"),
        )
        assert result.returncode == 1
        assert "shared-skill" in result.stdout


# ---------------------------------------------------------------------------
# 5. R03 private-marketplace checker behaviours (PR #1)
# ---------------------------------------------------------------------------

class TestPrivateMarketplaceChecker:
    """R03: a PUBLIC marketplace.json must never reference a private repo
    (PRIVATE_REPOS = {'savant'}). The checker is dual-mode (accepts a
    marketplace.json FILE or a DIR containing one); bad (savant ref) -> exit 1,
    good -> 0, absent path -> visible 'skip:' + 0 (the vacuous-skip contract)."""

    CHK = CHECKS / "no_private_in_public_marketplace.py"

    def test_bad_marketplace_with_private_ref_gates(self):
        result = _run(self.CHK, str(MKT_BAD_FX))
        assert result.returncode == 1, f"{result.stdout}\n{result.stderr}"
        assert "savant" in result.stdout

    def test_good_marketplace_passes(self):
        assert _run(self.CHK, str(MKT_GOOD_FX)).returncode == 0

    def test_absent_path_announces_visible_skip(self, tmp_path: Path):
        result = _run(self.CHK, str(tmp_path / "nope" / "marketplace.json"))
        assert result.returncode == 0
        assert "skip:" in result.stdout

    def test_in_repo_marketplace_is_clean(self):
        """craft's own public marketplace.json must reference no private repo —
        the live (non-fixture) enforcement check."""
        live = PLUGIN_DIR / ".claude-plugin" / "marketplace.json"
        assert _run(self.CHK, str(live)).returncode == 0
