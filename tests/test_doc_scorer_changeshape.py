# tests/test_doc_scorer_changeshape.py
import pytest
from test_plugin_e2e import PLUGIN_DIR

pytestmark = [pytest.mark.unit, pytest.mark.docs]


def test_scorer_rubric_present():
    # The reused rubric (threshold >=3) lives in skills/orchestration/references/ since the
    # folio split moved commands/docs/sync.md out of craft (2026-07-12) — not reimplemented.
    body = (PLUGIN_DIR / "skills/orchestration/references/doc-impact-rubric.md").read_text(
        encoding="utf-8"
    ).lower()
    assert "refcard" in body and "demo" in body, \
        "doc-scorer rubric must remain the single source in " \
        "skills/orchestration/references/doc-impact-rubric.md"
