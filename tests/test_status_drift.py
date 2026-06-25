"""D1 (#205): status_drift checker — .STATUS claims must not drift from ground truth.

FIXTURE mode (an `expected.json` sidecar supplies ground truth → no git needed):
LIVE mode derives ground truth from the manifest + `git tag`. These tests exercise
the FIXTURE-mode contract plus the vacuous/usage edges. The committed
governance/fixtures/status-not-drift/{good,bad} dirs are validated separately via
run_rules.py --selftest.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
CHECK = REPO / "governance" / "checks" / "status_drift.py"


def _run(*args):
    return subprocess.run([sys.executable, str(CHECK), *map(str, args)],
                          capture_output=True, text=True, timeout=30)


def _fixture(root, status_text, expected):
    (root / ".STATUS").write_text(status_text)
    (root / "expected.json").write_text(json.dumps(expected))
    return root


@pytest.mark.integration
class TestStatusDrift:
    def test_usage_error_without_args(self):
        r = _run()
        assert r.returncode == 2, r.stdout

    def test_vacuous_when_no_status_file(self, tmp_path):
        r = _run(tmp_path)  # empty dir, no .STATUS
        assert r.returncode == 0, r.stdout
        assert "skip" in r.stdout.lower()

    def test_passes_when_version_matches_and_shipped_tag_exists(self, tmp_path):
        root = _fixture(
            tmp_path,
            "status: Active\nversion: 2.50.0\nmilestone: v2.50.0 SHIPPED 2026-06-25\n",
            {"manifest_version": "2.50.0", "tags": ["v2.50.0", "v2.49.0"]},
        )
        r = _run(root)
        assert r.returncode == 0, r.stdout

    def test_drift_when_version_disagrees_with_manifest(self, tmp_path):
        # The medrobust case: .STATUS claims a version the manifest does not carry.
        root = _fixture(
            tmp_path,
            "status: Active\nversion: 0.4.0\n",
            {"manifest_version": "0.1.0.9000", "tags": []},
        )
        r = _run(root)
        assert r.returncode == 1, r.stdout
        assert "version" in r.stdout.lower()

    def test_prose_version_tokens_do_not_false_positive(self, tmp_path):
        # Real .STATUS prose: a URL `…-v2.37.0.tar.gz` and a sentence-final `v2.37.0.`
        # must resolve to the real tag v2.37.0, not be flagged as missing tags.
        root = _fixture(
            tmp_path,
            "status: Active\nversion: 2.50.0\n"
            "milestone: v2.50.0 SHIPPED; prior v2.37.0. url craft-v2.37.0.tar.gz\n",
            {"manifest_version": "2.50.0", "tags": ["v2.50.0", "v2.37.0"]},
        )
        r = _run(root)
        assert r.returncode == 0, r.stdout

    def test_drift_when_shipped_version_has_no_tag(self, tmp_path):
        # .STATUS announces vX SHIPPED but no such tag exists (mis-stamped release).
        root = _fixture(
            tmp_path,
            "status: Active\nversion: 2.51.0\nmilestone: v2.51.0 SHIPPED 2026-07-01\n",
            {"manifest_version": "2.51.0", "tags": ["v2.50.0"]},
        )
        r = _run(root)
        assert r.returncode == 1, r.stdout
        assert "tag" in r.stdout.lower()
