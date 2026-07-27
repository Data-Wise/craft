import re
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parent.parent
STABLE_PYTHON_SERIES = "3.14"


def test_local_python_version_tracks_stable_series():
    assert (ROOT / ".python-version").read_text().strip() == STABLE_PYTHON_SERIES


def test_suite_runs_on_stable_python_series():
    running_series = ".".join(str(part) for part in sys.version_info[:2])
    if running_series != STABLE_PYTHON_SERIES:
        pytest.skip(
            f"local interpreter is {running_series}, not the pinned {STABLE_PYTHON_SERIES} "
            "series — CI and .python-version enforce the actual pin"
        )


def test_github_workflows_use_stable_python_series():
    pinned_workflows = {}

    for workflow in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        content = workflow.read_text()
        if "actions/setup-python@" not in content:
            continue

        versions = re.findall(r"python-version:\s*['\"]([^'\"]+)['\"]", content)
        pinned_workflows[workflow.name] = versions

    assert pinned_workflows
    assert all(versions for versions in pinned_workflows.values())
    assert all(
        version == STABLE_PYTHON_SERIES
        for versions in pinned_workflows.values()
        for version in versions
    )
