#!/usr/bin/env python3
"""Shared fenced-```python block extractor for classify_issue().

Both tests/test_issue_check_unit.py and utils/repo_triage_classify.py need
to pull the classify_issue() source out of commands/git/issue-check.md at
runtime. This module is the ONE place that regex lives, so a change to
issue-check.md's fence format only needs fixing once.

tests/test_repo_triage_classify_unit.py deliberately does NOT use this
module -- its own `_reference_extract()` is an intentionally independent
re-implementation, used to cross-check `load_classifier_source()` below and
catch a real divergence, not just agreement-with-itself.
"""

import re
from pathlib import Path


def extract_classifier_source(md_path: Path) -> str:
    """Return the exact fenced ```python block defining classify_issue()."""
    text = md_path.read_text(encoding="utf-8")
    blocks = re.findall(r"```python\n(.*?)```", text, re.DOTALL)
    src = next((b for b in blocks if "def classify_issue" in b), None)
    if src is None:
        raise RuntimeError(f"classify_issue block not found in {md_path}")
    return src
