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
import os
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


# ---------------------------------------------------------------------------
# 6. SessionStart visibility hook (PR #2)
# ---------------------------------------------------------------------------

HOOK = GOV_DIR / "session_hook.py"


def _run_hook(env_overrides: dict, stdin: str = "") -> subprocess.CompletedProcess:
    env = dict(os.environ, GOVERNANCE_ENGINE=str(RUN), **env_overrides)
    return subprocess.run(
        [sys.executable, str(HOOK)], input=stdin,
        capture_output=True, text=True, timeout=20, env=env,
    )


class TestSessionHook:
    """SessionStart visibility hook: emits a RED-only summary into session
    context, silent when clean, no-op when the skills tree is absent, and
    mtime-cached. Hermetic — temp skills dirs + temp cache, never live ~/.claude."""

    def test_dead_symlink_emits_red_additionalcontext(self, tmp_path: Path):
        skills = tmp_path / "skills"; skills.mkdir()
        (skills / "dead").symlink_to("/nonexistent/target")
        r = _run_hook({"GOVERNANCE_SKILLS_DIR": str(skills),
                       "GOVERNANCE_CACHE": str(tmp_path / "cache.json")})
        assert r.returncode == 0, r.stderr
        ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
        assert "red" in ctx and "R08-no-dead-links" in ctx

    def test_clean_skills_is_silent(self, tmp_path: Path):
        skills = tmp_path / "skills"; skills.mkdir()
        (skills / "ok.txt").write_text("ok", encoding="utf-8")
        r = _run_hook({"GOVERNANCE_SKILLS_DIR": str(skills),
                       "GOVERNANCE_CACHE": str(tmp_path / "c.json")})
        assert r.returncode == 0 and r.stdout.strip() == ""

    def test_absent_skills_is_noop(self, tmp_path: Path):
        r = _run_hook({"GOVERNANCE_SKILLS_DIR": str(tmp_path / "nope"),
                       "GOVERNANCE_CACHE": str(tmp_path / "c.json")})
        assert r.returncode == 0 and r.stdout.strip() == ""

    def test_mtime_cache_written_and_reused(self, tmp_path: Path):
        skills = tmp_path / "skills"; skills.mkdir()
        (skills / "dead").symlink_to("/nonexistent")
        cache = tmp_path / "cache.json"
        r1 = _run_hook({"GOVERNANCE_SKILLS_DIR": str(skills), "GOVERNANCE_CACHE": str(cache)})
        assert cache.is_file()
        data = json.loads(cache.read_text(encoding="utf-8"))
        assert "mtime" in data and "red" in data["summary"]
        r2 = _run_hook({"GOVERNANCE_SKILLS_DIR": str(skills), "GOVERNANCE_CACHE": str(cache)})
        assert r1.stdout == r2.stdout, "unchanged tree should reuse the cached summary"


# ---------------------------------------------------------------------------
# 7. Soak-then-flip ledger + cross-repo wrapper (PR #3)
# ---------------------------------------------------------------------------

sys.path.insert(0, str(GOV_DIR))
import soak  # noqa: E402  (sibling module under governance/)

RUN_SH = GOV_DIR / "run.sh"


def _write_ledger(path: Path, rules: dict) -> None:
    path.write_text(json.dumps({"schema": soak.SCHEMA, "updated": "2026-07-01",
                                "rules": rules}), encoding="utf-8")


class TestSoakLedger:
    """Soak ledger: record_audit stamps dates; promotion_eligible gates on BOTH
    enough history AND no-recent-RED. All date math uses an injected `today`."""

    def test_record_stamps_first_seen_and_last_red(self, tmp_path: Path):
        led = tmp_path / "STATE.json"
        results = [{"id": "R01", "severity": "warn", "state": "PASS"},
                   {"id": "R08", "severity": "error", "state": "FAIL"}]
        soak.record_audit(str(led), results, today="2026-06-01")
        d = json.loads(led.read_text())
        assert d["rules"]["R01"]["first_seen"] == "2026-06-01"
        assert d["rules"]["R01"]["last_red"] is None          # PASS → no red stamp
        assert d["rules"]["R08"]["last_red"] == "2026-06-01"  # FAIL → red stamped

    def test_eligible_after_window_clean(self, tmp_path: Path):
        led = tmp_path / "STATE.json"
        _write_ledger(led, {"R01": {"first_seen": "2026-06-01", "last_red": None}})
        elig = soak.promotion_eligible(str(led), {"R01"}, today="2026-07-01", window_days=14)
        assert [e["id"] for e in elig] == ["R01"]

    def test_not_eligible_insufficient_history(self, tmp_path: Path):
        led = tmp_path / "STATE.json"
        _write_ledger(led, {"R01": {"first_seen": "2026-06-25", "last_red": None}})  # 6d old
        elig = soak.promotion_eligible(str(led), {"R01"}, today="2026-07-01", window_days=14)
        assert elig == []

    def test_not_eligible_recent_red(self, tmp_path: Path):
        led = tmp_path / "STATE.json"
        _write_ledger(led, {"R01": {"first_seen": "2026-06-01", "last_red": "2026-06-28"}})  # red 3d ago
        elig = soak.promotion_eligible(str(led), {"R01"}, today="2026-07-01", window_days=14)
        assert elig == []

    def test_error_rule_never_eligible(self, tmp_path: Path):
        """promotion_eligible only considers the warn-rule id set it's handed, so
        an error-severity rule (absent from warn_ids) can never be recommended."""
        led = tmp_path / "STATE.json"
        _write_ledger(led, {"R08": {"first_seen": "2026-01-01", "last_red": None}})
        elig = soak.promotion_eligible(str(led), {"R01"}, today="2026-07-01", window_days=14)
        assert elig == []  # R08 not in warn_ids → ignored even though soaked

    def test_record_audit_preserves_first_seen_across_runs(self, tmp_path: Path):
        """first_seen is the anchor for the soak window — a later audit must NOT
        reset it, or a long-clean rule would never accrue soak history."""
        led = tmp_path / "STATE.json"
        res = [{"id": "R01", "severity": "warn", "state": "PASS"}]
        soak.record_audit(str(led), res, today="2026-06-01")
        soak.record_audit(str(led), res, today="2026-06-20")
        entry = json.loads(led.read_text())["rules"]["R01"]
        assert entry["first_seen"] == "2026-06-01"  # anchored to the first sighting
        assert entry["last_seen"] == "2026-06-20"   # refreshed each run

    def test_record_audit_clears_then_restamps_red(self, tmp_path: Path):
        """A rule that goes RED then clean keeps its last_red at the RED date — the
        window is measured from when it was last bad, not from the latest audit."""
        led = tmp_path / "STATE.json"
        soak.record_audit(str(led), [{"id": "R01", "severity": "warn", "state": "FAIL"}], today="2026-06-10")
        soak.record_audit(str(led), [{"id": "R01", "severity": "warn", "state": "PASS"}], today="2026-06-20")
        assert json.loads(led.read_text())["rules"]["R01"]["last_red"] == "2026-06-10"

    def test_load_state_recovers_from_corrupt_ledger(self, tmp_path: Path):
        """A corrupt/old-schema ledger must degrade to a fresh empty state, never
        raise — soak is best-effort and can't break the hook that feeds it."""
        led = tmp_path / "STATE.json"
        led.write_text("{ not valid json", encoding="utf-8")
        st = soak.load_state(str(led))
        assert st["schema"] == soak.SCHEMA and st["rules"] == {}


class TestPromoteCheckCLI:
    """`run_rules.py --promote-check` — advisory, always exit 0."""

    def test_no_ledger_is_helpful_not_error(self, tmp_path: Path):
        r = _run(RUN, "--promote-check", "--state", str(tmp_path / "absent.json"))
        assert r.returncode == 0 and "no soak ledger yet" in r.stdout

    def test_lists_eligible_warn_rules(self, tmp_path: Path):
        led = tmp_path / "STATE.json"
        # R01 is a real warn-severity rule in RULES.yaml; soaked clean since January.
        _write_ledger(led, {"R01-single-source": {"first_seen": "2026-01-01", "last_red": None}})
        r = _run(RUN, "--promote-check", "--state", str(led), "--window", "14")
        assert r.returncode == 0
        assert "R01-single-source" in r.stdout and "ripe" in r.stdout


class TestCrossRepoWrapper:
    """governance/run.sh — one installed copy, invoked from any cwd (no drift)."""

    def test_run_sh_portable_from_foreign_cwd(self, tmp_path: Path):
        r = subprocess.run(["bash", str(RUN_SH), "--selftest"],
                           cwd=str(tmp_path), capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, r.stderr
        assert "SELFTEST" in r.stdout  # the engine actually ran, from a foreign cwd


# ---------------------------------------------------------------------------
# 8. Release pre-flight governance annotation (#184) — advisory, NEVER blocks
# ---------------------------------------------------------------------------

PRE_RELEASE = PLUGIN_DIR / "scripts" / "pre-release-check.sh"


class TestReleaseGuard184:
    """The governance step in pre-release-check.sh surfaces RED findings but must
    never gate the release (gentle-ramp). The non-blocking invariant is the whole
    point — lock it in so a later edit can't silently turn it into a gate."""

    def _governance_block(self) -> str:
        src = PRE_RELEASE.read_text(encoding="utf-8")
        assert "Governance (skill-ecosystem)" in src, "advisory block missing"
        start = src.index("Governance (skill-ecosystem) — ADVISORY")
        end = src.index("# Summary", start)
        return src[start:end]

    def test_block_present(self):
        assert "advisory, non-blocking" in self._governance_block()

    def test_block_never_increments_errors(self):
        """The advisory block must not touch $ERRORS — that's what keeps it from
        ever failing the release. If this fires, someone made governance a gate."""
        block = self._governance_block()
        assert "ERRORS=" not in block, "governance advisory must not modify $ERRORS"
        assert "exit 1" not in block, "governance advisory must not exit non-zero"


# ---------------------------------------------------------------------------
# 9. R04 content-drift checker (Phase 1 automation)
# ---------------------------------------------------------------------------

DRIFT_CHK = CHECKS / "no_drifted_copy.py"
DRIFT_GOOD = GOV_DIR / "fixtures" / "no-drifted-copy" / "good"
DRIFT_BAD = GOV_DIR / "fixtures" / "no-drifted-copy" / "bad"


class TestDriftedCopyChecker:
    """R04 automated as content drift: an installed SKILL.md must stay byte-identical
    to its canon. Distinct from R07 (version-pin) — this catches a hand-edited copy."""

    def test_identical_copy_passes(self):
        assert _run(DRIFT_CHK, str(DRIFT_GOOD)).returncode == 0

    def test_drifted_copy_is_flagged(self):
        r = _run(DRIFT_CHK, str(DRIFT_BAD))
        assert r.returncode == 1 and "drifted copy" in r.stdout

    def test_absent_consumer_skips(self, tmp_path: Path):
        r = _run(DRIFT_CHK, str(tmp_path / "nope"))
        assert r.returncode == 0 and "skip" in r.stdout

    def test_no_canon_is_vacuous_not_a_pass(self, tmp_path: Path):
        """With a consumer present but no canon, the check is vacuous — it must say
        so out loud (a clean exit that isn't mistaken for enforcement)."""
        consumer = tmp_path / "consumer"; consumer.mkdir()
        r = _run(DRIFT_CHK, str(consumer), str(tmp_path / "nocanon"))
        assert r.returncode == 0 and "vacuous" in r.stdout

    def test_live_env_never_errors(self):
        """Against the real surface, R04 must be clean or vacuously skip — never a
        false positive (a noisy WARN would stamp last_red and block soak promotion)."""
        assert _run(DRIFT_CHK, os.path.expanduser("~/.claude/skills")).returncode == 0
