---
description: "Check whether an open GitHub issue's premise still holds against current code, before implementing a fix it requests"
category: git
arguments:
  - name: issue
    description: "Issue number (e.g. 199)"
    required: true
  - name: repo
    description: "Repo in OWNER/NAME form (default = Data-Wise/craft)"
    required: false
  - name: json
    description: Output structured JSON instead of the verdict box
    required: false
    default: false
related_commands: ci:triage, orch:drive
tags: git, github, issue, triage, premise-check
---

# /craft:git:issue-check - Issue Premise Check

Before implementing a fix requested by an open GitHub issue, check whether
the issue's own premise still holds against current code. Returns a
structured verdict — **valid** (premise holds, the fix is still needed),
**moot** (already resolved, or the issue is closed), or **unclear** (cannot
be mechanically verified) — always with cited evidence, never a bare label.

**Advisory only.** This command never closes, edits, comments on, or
otherwise mutates the issue — it only reads.

## When to Use

- Before starting work driven by an open issue, to confirm it's not already
  fixed or overtaken by other changes.
- Before `/craft:orch:drive` runs a SPEC that cites a `#NNN` issue (the
  `orch:drive` pre-filter calls this command automatically — see
  Step 3 of `commands/orch/drive.md`).
- When triaging a backlog of open issues to see which still apply.

## Implementation

### Step 1: Fetch live issue state (never cached)

```bash
ISSUE="${1:?issue number required, e.g. /craft:git:issue-check 199}"
REPO="${REPO:-Data-Wise/craft}"
gh issue view "$ISSUE" --repo "$REPO" \
  --json number,title,body,state,updatedAt > /tmp/issue-check-issue.json
```

Every invocation re-fetches issue state fresh — no verdict is ever stored or
reused across runs, and no TTL/caching path exists anywhere in this command
(GRILL Branch 9). The `orch:drive` gate and a standalone run each re-fetch
independently.

### Step 2: Enumerate repo files (code-search input)

```bash
git ls-files > /tmp/issue-check-files.txt
```

This is the "code search" the classifier checks cited artifacts against —
deliberately just the tracked-file list (cheap, deterministic, no grep
false-positives from comments/strings).

### Step 3: Classify (the core logic)

The issue body's acceptance-criteria checkboxes (`- [ ]` / `- [x]`) are the
mechanical signal: unchecked boxes that cite a `/craft:*` command are
checked against whether that command file actually exists in the repo. This
function is the single source of truth — `tests/test_issue_check_unit.py`
extracts and exercises it directly, mirroring `commands/ci/triage.md`'s
`classify_failure()` pattern (pure, stdlib-only, no network calls).

```python
import re

_CHECKBOX_RE = re.compile(r"^- \[([ xX])\]\s*(.+)$", re.MULTILINE)
_SLASH_CMD_RE = re.compile(r"/craft:([a-zA-Z0-9_:-]+)")


def _extract_acceptance_criteria(body):
    """Parse '- [ ]' / '- [x]' checkbox lines from an issue body.

    Returns a list of (checked: bool, text: str) tuples in body order.
    """
    return [
        (m.group(1).lower() == "x", m.group(2).strip())
        for m in _CHECKBOX_RE.finditer(body or "")
    ]


def _cmd_ref_to_path(ref):
    """'dist:cowork' -> 'commands/dist/cowork.md' (the /craft: prefix is stripped by the regex)."""
    return "commands/" + ref.replace(":", "/") + ".md"


def classify_issue(issue, repo_files):
    """Classify whether an issue's premise still holds against current code.

    issue: {"number", "title", "body", "state", "updatedAt"} — the exact
        shape of `gh issue view <N> --json number,title,body,state,updatedAt`.
    repo_files: iterable of repo-relative paths (e.g. from `git ls-files`),
        used to check whether a criterion's cited command already ships.

    Returns {status: "valid"|"moot"|"unclear", evidence: [...], reasoning: str}.
    Never a bare label -- evidence always cites a file path, a criterion's
    text, or the issue's own state.
    """
    repo_files = set(repo_files)
    body = issue.get("body", "") or ""
    criteria = _extract_acceptance_criteria(body)

    if (issue.get("state") or "").upper() == "CLOSED":
        return {
            "status": "moot",
            "evidence": [{"file": None, "lines": None, "note": "issue state is CLOSED"}],
            "reasoning": "Issue is closed; premise is moot regardless of code state.",
        }

    if not criteria:
        return {
            "status": "unclear",
            "evidence": [{
                "file": None, "lines": None,
                "note": "no '- [ ]' acceptance-criteria checkboxes found in body",
            }],
            "reasoning": (
                "Cannot mechanically verify premise without checkbox-style "
                "acceptance criteria to check against the repo."
            ),
        }

    unmet = [text for checked, text in criteria if not checked]
    if not unmet:
        return {
            "status": "moot",
            "evidence": [{
                "file": None, "lines": None,
                "note": f"all {len(criteria)} acceptance criteria checked",
            }],
            "reasoning": "All acceptance criteria are already marked complete.",
        }

    missing_evidence, shipped_evidence = [], []
    for text in unmet:
        for ref in _SLASH_CMD_RE.findall(text):
            path = _cmd_ref_to_path(ref)
            if path in repo_files:
                shipped_evidence.append({
                    "file": path, "lines": None,
                    "note": f"cited by unmet criterion but already exists: {text[:80]}",
                })
            else:
                missing_evidence.append({
                    "file": path, "lines": None,
                    "note": f"cited command not found: {text[:80]}",
                })

    if missing_evidence:
        return {
            "status": "valid",
            "evidence": missing_evidence[:5],
            "reasoning": (
                f"{len(unmet)} of {len(criteria)} acceptance criteria unchecked; "
                "cited deliverable(s) not found in the repo."
            ),
        }

    if shipped_evidence:
        return {
            "status": "unclear",
            "evidence": shipped_evidence[:5],
            "reasoning": (
                "Cited deliverables already exist in the repo despite unchecked "
                "boxes; needs human review to confirm the criteria are truly unmet."
            ),
        }

    return {
        "status": "valid",
        "evidence": [{
            "file": None, "lines": None,
            "note": f"{len(unmet)} of {len(criteria)} criteria unchecked; no citable command reference to verify against repo",
        }],
        "reasoning": (
            "Unmet criteria present with no verifiable command reference; "
            "treating premise as still valid pending the unchecked boxes."
        ),
    }
```

### Step 4: Render the verdict

```text
┌─ ISSUE-CHECK ─ #199 ──────────────────────────────────────────────┐
│ Verdict:    VALID   (premise still holds)                         │
│ Evidence:   commands/dist/cowork.md — cited command not found:    │
│             "A craft command (e.g. `/craft:dist:cowork`...)"      │
│ Reasoning:  2 of 6 acceptance criteria unchecked; cited            │
│             deliverable(s) not found in the repo.                 │
└─────────────────────────────────────────────────────────────────┘
```

Badge per status: **valid** (red — fix still needed), **moot** (green —
nothing to do), **unclear** (yellow — needs human judgment). Always print
the cited evidence so the verdict is auditable, never a bare assertion.

### Step 5: `--json` mode

When `--json` is set, skip the box and emit the classifier's return value
directly, plus the issue number/repo:

```json
{
  "issue": 199,
  "repo": "Data-Wise/craft",
  "status": "valid",
  "evidence": [{"file": "commands/dist/cowork.md", "lines": null, "note": "..."}],
  "reasoning": "..."
}
```

## Non-Goals

- **Never mutates GitHub state.** No `gh issue close`, `gh issue edit`,
  `gh issue comment`, `gh issue reopen`, or any other mutating `gh issue`
  subcommand appears anywhere in this command. Read-only, advisory only.
- **Never blocks.** `/craft:orch:drive`'s pre-filter (its Step 2) surfaces
  this command's verdict when a driven task cites `#NNN`, but always
  proceeds regardless of the verdict.
- **Never caches.** No verdict is stored, memoized, or reused across
  invocations or trigger points (GRILL Branch 9).

## Error Handling

- **Issue not found / `gh issue view` fails** → report the error and exit 0
  (nothing to triage).
- **No acceptance-criteria checkboxes in the body** → `unclear`, not a
  forced `valid`/`moot` guess.
- **Issue closed** → `moot` unconditionally; closed issues are moot
  regardless of what the code contains.

## See Also

- `/craft:ci:triage` — the CI-failure analog this pattern mirrors
  (`classify_failure()` / `classify_issue()`).
- `/craft:orch:drive` — pre-filtered gate consumer (Step 2 there).
