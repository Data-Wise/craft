#!/usr/bin/env python3
"""
End-to-End Governance Contract Tests
====================================
Validates the *internal consistency* of the skill-ecosystem governance system
(``governance/``): that RULES.yaml is well-formed, every automatable rule wires
to a checker that exists, every fixtured rule has its good+bad pair, and the
generated ``CLAUDE-rules.md`` block stays in sync with RULES.yaml (the
rules-drift gate).

These are static/contract checks — they read files and shell out to the two
engine scripts, but never touch the live ``~/.claude`` environment, so they are
hermetic and machine-independent.

Run with: python3 -m pytest tests/test_governance_e2e.py -v
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

pytestmark = [pytest.mark.e2e, pytest.mark.governance]

PLUGIN_DIR = Path(__file__).parent.parent
GOV_DIR = PLUGIN_DIR / "governance"
RULES_YAML = GOV_DIR / "RULES.yaml"
CLAUDE_RULES = GOV_DIR / "CLAUDE-rules.md"
RENDER = GOV_DIR / "render_rules.py"

REQUIRED_RULE_KEYS = {
    "id", "statement", "rationale", "severity",
    "owner", "status", "added", "gates", "check", "waivers",
}
VALID_SEVERITIES = {"error", "warn", "advisory"}
VALID_GATES = {"author", "ci", "release", "install", "session", "runtime"}
VALID_CHECK_KINDS = {"script", "external", "manual"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_rules() -> dict:
    return yaml.safe_load(RULES_YAML.read_text(encoding="utf-8"))


def _active_rules() -> list[dict]:
    return [r for r in _load_rules()["rules"] if r.get("status") == "active"]


def _run(script: Path, *args, **kw) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True, text=True, timeout=30, cwd=str(GOV_DIR), **kw,
    )


# ---------------------------------------------------------------------------
# 1. RULES.yaml is well-formed
# ---------------------------------------------------------------------------

class TestRulesYamlSchema:
    def test_top_level_keys(self):
        doc = _load_rules()
        for key in ("version", "scope", "posture", "rules"):
            assert key in doc, f"RULES.yaml missing top-level key: {key}"
        assert isinstance(doc["rules"], list) and doc["rules"], "rules must be a non-empty list"

    def test_every_rule_has_required_keys(self):
        for r in _load_rules()["rules"]:
            missing = REQUIRED_RULE_KEYS - set(r)
            assert not missing, f"{r.get('id', '<no id>')} missing keys: {missing}"

    def test_rule_ids_unique_and_well_formed(self):
        ids = [r["id"] for r in _load_rules()["rules"]]
        assert len(ids) == len(set(ids)), f"duplicate rule ids: {ids}"
        for rid in ids:
            assert re.match(r"^R\d+-[a-z0-9-]+$", rid), f"malformed rule id: {rid}"

    def test_severity_and_gates_valid(self):
        for r in _load_rules()["rules"]:
            assert r["severity"] in VALID_SEVERITIES, f"{r['id']}: bad severity {r['severity']}"
            gates = r.get("gates") or []
            assert isinstance(gates, list), f"{r['id']}: gates must be a list"
            bad = set(gates) - VALID_GATES
            assert not bad, f"{r['id']}: unknown gates {bad}"

    def test_check_kinds_valid(self):
        for r in _load_rules()["rules"]:
            kind = (r.get("check") or {}).get("kind", "manual")
            assert kind in VALID_CHECK_KINDS, f"{r['id']}: bad check kind {kind}"


# ---------------------------------------------------------------------------
# 2. Rules wire to real checkers + fixtures (no dangling references)
# ---------------------------------------------------------------------------

class TestCheckerWiring:
    def test_script_checks_reference_existing_files(self):
        for r in _active_rules():
            chk = r.get("check") or {}
            if chk.get("kind") != "script":
                continue
            rel = chk["cmd"].split()[0]  # 'checks/foo.py {target}' -> 'checks/foo.py'
            assert (GOV_DIR / rel).exists(), f"{r['id']}: checker missing: {rel}"

    def test_fixtured_rules_have_good_and_bad(self):
        for r in _active_rules():
            fx = (r.get("check") or {}).get("fixtures")
            if not fx:
                continue
            for kind in ("good", "bad"):
                assert (GOV_DIR / fx[kind]).is_dir(), f"{r['id']}: missing {kind} fixture {fx[kind]}"

    def test_error_rules_are_enforceable_or_delegated(self):
        """An error rule must be backed by a script/external check — not 'manual'
        with no plan. R03 is the one known gap (manual, Phase 1); assert it stays
        the *only* one so a new silent error-rule can't slip in."""
        manual_error = [
            r["id"] for r in _active_rules()
            if r["severity"] == "error" and (r.get("check") or {}).get("kind") == "manual"
        ]
        assert manual_error == ["R03-private-marketplace"], (
            f"unexpected manual error-rules (enforcement gaps): {manual_error}"
        )

    def test_r02_r08_share_one_mechanism(self):
        """R02 and R08 intentionally share the symlink checker (documented in
        RULES.yaml). Guard the invariant so a future edit doesn't silently split
        them and leave one unenforced."""
        rules = {r["id"]: r for r in _active_rules()}
        c02 = rules["R02-no-hand-links"]["check"]["cmd"]
        c08 = rules["R08-no-dead-links"]["check"]["cmd"]
        assert c02 == c08, "R02 and R08 are expected to share one checker cmd"


# ---------------------------------------------------------------------------
# 3. Generated CLAUDE-rules.md stays in sync (rules-drift gate)
# ---------------------------------------------------------------------------

class TestRulesDriftGate:
    def test_claude_rules_in_sync(self):
        """render_rules.py --check must report the committed block matches a
        fresh render. This is the CI drift gate."""
        result = _run(RENDER, "--check", str(CLAUDE_RULES))
        assert result.returncode == 0, (
            "CLAUDE-rules.md drifted from RULES.yaml — run "
            "`python3 governance/render_rules.py --apply governance/CLAUDE-rules.md`\n"
            f"{result.stdout}\n{result.stderr}"
        )

    def test_every_active_rule_appears_in_generated_block(self):
        text = CLAUDE_RULES.read_text(encoding="utf-8")
        for r in _active_rules():
            assert r["id"] in text, f"{r['id']} missing from generated CLAUDE-rules.md"

    def test_check_with_no_file_is_an_error(self):
        """Minor hardening: `--check` with no FILE must not pass vacuously."""
        result = _run(RENDER, "--check")
        assert result.returncode == 2, (
            f"--check with no file should return 2, got {result.returncode}"
        )

    def test_render_apply_is_idempotent(self, tmp_path: Path):
        """Applying the block to a fresh marked file, then again, yields no drift."""
        target = tmp_path / "C.md"
        target.write_text(
            "# Test\n\n"
            "<!-- RULES:BEGIN (generated from governance/RULES.yaml — do not edit by hand) -->\n"
            "stale\n"
            "<!-- RULES:END -->\n",
            encoding="utf-8",
        )
        assert _run(RENDER, "--apply", str(target)).returncode == 0
        assert _run(RENDER, "--check", str(target)).returncode == 0

    def test_check_detects_drifted_block(self, tmp_path: Path):
        """Red case for the drift gate: a marked block whose body differs from a
        fresh render must be reported as DRIFT (exit 1). Without this, a broken
        check() that always returned OK would pass the whole suite green — and
        since the engine is not yet wired as a live CI/hook gate, this suite is
        the only thing guarding the drift checker."""
        target = tmp_path / "C.md"
        target.write_text(
            "# Test\n\n"
            "<!-- RULES:BEGIN (generated from governance/RULES.yaml — do not edit by hand) -->\n"
            "stale — deliberately not a fresh render\n"
            "<!-- RULES:END -->\n",
            encoding="utf-8",
        )
        result = _run(RENDER, "--check", str(target))
        assert result.returncode == 1, f"drifted block must fail --check:\n{result.stdout}"
        assert "DRIFT" in result.stdout

    def test_check_missing_file_fails(self, tmp_path: Path):
        """--check against a nonexistent path must fail (not pass vacuously)."""
        result = _run(RENDER, "--check", str(tmp_path / "nope.md"))
        assert result.returncode == 1
        assert "MISSING" in result.stdout

    def test_check_file_without_markers_fails(self, tmp_path: Path):
        """--check against a file lacking the RULES markers must fail."""
        target = tmp_path / "no_markers.md"
        target.write_text("# Just a doc, no managed block here.\n", encoding="utf-8")
        result = _run(RENDER, "--check", str(target))
        assert result.returncode == 1
        assert "NO-MARKERS" in result.stdout
