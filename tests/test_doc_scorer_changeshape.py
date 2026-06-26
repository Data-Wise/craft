# tests/test_doc_scorer_changeshape.py
import pytest
from test_plugin_e2e import PLUGIN_DIR

pytestmark = [pytest.mark.unit, pytest.mark.docs]


def test_scorer_rubric_present():
    # The reused rubric (threshold >=3) must still live in docs/sync.md — not reimplemented.
    body = (PLUGIN_DIR / "commands/docs/sync.md").read_text(encoding="utf-8").lower()
    assert "refcard" in body and "tutorial" in body, \
        "doc-scorer rubric must remain the single source in commands/docs/sync.md"
