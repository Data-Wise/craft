#!/usr/bin/env python3
"""Count-drift tripwire (item #2).

Phase 7 of docs-staleness-check.sh now scans README.md, so any LIVE count string
(`**110 commands**`, intro, link section) that drifts from discovery fails CI,
while the README's embedded changelog (historical release totals) stays excluded.
validate-counts.sh carries a faster README-badge guard for local pre-flight.

Every mutating test runs an ISOLATED copy of the plugin tree (the scripts cd to
their own script-relative root), so writes never touch the real source tree —
per the v2.36.0 test-mutation post-mortem.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.docs]

PLUGIN_DIR = Path(__file__).parent.parent

# The subtree both scripts need to compute counts and scan docs.
_ISOLATION_PATHS = (
    "scripts", "docs", "commands", "skills", "agents",
    "mkdocs.yml", "CLAUDE.md", "README.md", ".claude-plugin",
)


def _isolated(dst: Path) -> Path:
    """Copy the needed subtree into dst; return the tree root.

    docs-staleness-check.sh / validate-counts.sh both `cd` to their own
    SCRIPT_DIR/.. , so running the COPY operates on the copied tree.
    """
    dst.mkdir(parents=True, exist_ok=True)
    for name in _ISOLATION_PATHS:
        src = PLUGIN_DIR / name
        if not src.exists():
            continue
        target = dst / name
        if src.is_dir():
            shutil.copytree(src, target)
        else:
            shutil.copy(src, target)
    return dst


def _drift_badge(readme: Path, noun: str) -> tuple[str, str]:
    """Rewrite README's `**N <noun>**` badge to a wrong, above-threshold value.

    Derives N from the file (never hardcoded — these are drift tests, so a
    hardcoded count would itself silently rot on the next count bump). Returns
    (live, stale). The stale value stays well above Phase 7's 40% threshold so
    it is always flagged, and differs from the live value.
    """
    import re
    text = readme.read_text()
    m = re.search(rf"\*\*(\d+) {noun}\*\*", text)
    assert m, f"no `**N {noun}**` badge in README.md"
    live = m.group(1)
    stale = "777" if live != "777" else "888"
    readme.write_text(text.replace(f"**{live} {noun}**", f"**{stale} {noun}**", 1))
    return live, stale


def _phase7_findings(tree: Path):
    """Run the staleness check (JSON) and return (count_consistency findings, proc)."""
    proc = subprocess.run(
        ["bash", str(tree / "scripts" / "docs-staleness-check.sh"), "--json"],
        capture_output=True, text=True, timeout=120,
    )
    data = json.loads(proc.stdout)
    return data["phases"]["count_consistency"]["findings"], proc


class TestCountDriftTripwire:
    """Phase 7 + validate-counts now police README.md live counts."""

    def test_phase7_catches_stale_readme_command_count(self, tmp_path):
        """A drifted README command badge surfaces as a Phase 7 finding."""
        tree = _isolated(tmp_path / "iso")
        rm = tree / "README.md"
        live, stale = _drift_badge(rm, "commands")
        findings, _ = _phase7_findings(tree)
        blob = json.dumps(findings)
        assert "README.md" in blob and f"{stale} commands" in blob, (
            f"Phase 7 did not flag README command count {live}->{stale}:\n{blob[:600]}"
        )

    def test_phase7_catches_stale_readme_skill_count(self, tmp_path):
        """A drifted README skill badge surfaces as a Phase 7 finding."""
        tree = _isolated(tmp_path / "iso")
        rm = tree / "README.md"
        live, stale = _drift_badge(rm, "skills")
        findings, _ = _phase7_findings(tree)
        blob = json.dumps(findings)
        assert "README.md" in blob and f"{stale} skills" in blob, (
            f"Phase 7 did not flag README skill count {live}->{stale}:\n{blob[:600]}"
        )

    def test_phase7_readme_historical_counts_are_excluded(self, tmp_path):
        """The unmodified README's changelog totals must NOT be flagged."""
        tree = _isolated(tmp_path / "iso")
        findings, _ = _phase7_findings(tree)
        readme = [f for f in findings if "README.md" in json.dumps(f)]
        assert readme == [], (
            f"historical README counts leaked into Phase 7 findings: {readme}"
        )

    def test_validate_counts_catches_readme_badge_drift(self, tmp_path):
        """validate-counts.sh fails when the README badge count drifts."""
        tree = _isolated(tmp_path / "iso")
        rm = tree / "README.md"
        _drift_badge(rm, "commands")
        proc = subprocess.run(
            ["bash", str(tree / "scripts" / "validate-counts.sh")],
            capture_output=True, text=True, timeout=60,
        )
        assert proc.returncode == 1, f"expected exit 1, got {proc.returncode}\n{proc.stdout}"
        assert "README badge commands" in proc.stdout, proc.stdout

    def test_real_tree_phase7_is_green_for_readme(self):
        """Sanity: the real tree's live README counts are all consistent."""
        findings, _ = _phase7_findings(PLUGIN_DIR)
        readme = [f for f in findings if "README.md" in json.dumps(f)]
        assert readme == [], f"real-tree README drift detected: {readme}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
