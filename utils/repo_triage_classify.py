#!/usr/bin/env python3
"""Issue-triage runner for the repo-triage skill (Phase 1 of
ORCHESTRATE-repo-triage.md).

Loads classify_issue() by extracting the fenced ```python block from
commands/git/issue-check.md at runtime -- the exact same mechanism
tests/test_issue_check_unit.py uses to exercise it -- so repo-triage's
issue-triage step provably runs the SAME classifier, never a parallel copy
(GRILL Decision 9, Acceptance Criterion 2). tests/test_repo_triage_classify_unit.py
asserts source identity between this loader and the one in
tests/test_issue_check_unit.py.

Loops over ALL open issues with no pre-filter and no concurrency cap
(GRILL Decision 10 -- direct-import classification is cheap enough that the
cap this session considered hedges against a cost that doesn't exist).
A `gh issue view`/classification failure on one issue is skipped and
recorded, never aborts the run (GRILL Decision 14).
"""

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ISSUE_CHECK_MD = REPO_ROOT / "commands" / "git" / "issue-check.md"


def load_classifier_source():
    """Return the exact fenced ```python block defining classify_issue()."""
    text = ISSUE_CHECK_MD.read_text(encoding="utf-8")
    blocks = re.findall(r"```python\n(.*?)```", text, re.DOTALL)
    src = next((b for b in blocks if "def classify_issue" in b), None)
    if src is None:
        raise RuntimeError(f"classify_issue block not found in {ISSUE_CHECK_MD}")
    return src


def load_classifier():
    src = load_classifier_source()
    ns: dict = {}
    exec(compile(src, str(ISSUE_CHECK_MD), "exec"), ns)  # noqa: S102 -- same trusted in-repo file as the test suite
    return ns["classify_issue"]


def fetch_repo_files():
    try:
        out = subprocess.run(
            ["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
        )
        return set(out.stdout.splitlines())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return set()


def fetch_open_issues(repo):
    out = subprocess.run(
        [
            "gh", "issue", "list", "--repo", repo, "--state", "open",
            "--json", "number,title,body,state,updatedAt", "--limit", "1000",
        ],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)


def triage_issues(issues, repo_files, classify_issue):
    """Classify every issue; skip-and-record on a per-issue failure."""
    results = []
    errors = []
    for issue in issues:
        try:
            verdict = classify_issue(issue, repo_files)
        except Exception as exc:  # noqa: BLE001 -- deliberate skip-and-continue, Decision 14
            errors.append({"number": issue.get("number"), "error": str(exc)})
            continue
        results.append({"number": issue.get("number"), "title": issue.get("title"), **verdict})
    return results, errors


def main(argv):
    repo = argv[1] if len(argv) > 1 else "Data-Wise/craft"
    classify_issue = load_classifier()
    repo_files = fetch_repo_files()

    try:
        issues = fetch_open_issues(repo)
    except subprocess.CalledProcessError as exc:
        print(json.dumps({"results": [], "errors": [], "fatal": f"gh issue list failed: {exc.stderr}"}))
        return 1
    except FileNotFoundError:
        print(json.dumps({"results": [], "errors": [], "fatal": "gh CLI not found"}))
        return 1

    results, errors = triage_issues(issues, repo_files, classify_issue)
    print(json.dumps({"results": results, "errors": errors}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
