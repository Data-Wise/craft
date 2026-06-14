---
description: "Triage a failing CI check: classify as diff-caused vs pre-existing/infra and recommend re-run / --admin / fix with evidence"
category: ci
arguments:
  - name: pr
    description: "PR number or URL (default = the current branch's open PR)"
    required: false
  - name: repo
    description: "Repo in OWNER/NAME form (default = Data-Wise/craft)"
    required: false
  - name: json
    description: Output structured JSON instead of the verdict box
    required: false
    default: false
related_commands: ci:status, code:ci-fix, git:unprotect
tags: ci, triage, debugging, release
---

# /craft:ci:triage - Failing-Check Triage

Classify a red (or stuck) CI check as **diff-caused**, **pre-existing**, or an
**infra flake**, and recommend the next move — *fix*, *re-run*, or *`--admin`* —
with evidence. This is the manual reasoning from the release post-mortems
(scan the failed log → "is this in my diff or pre-existing?") turned into a command.

## When to Use

- A PR check is red and you need to know whether YOUR change broke it.
- A check is stuck `PENDING` and you're deciding whether an `--admin` merge is safe.
- Before reaching for `--admin` — to confirm the failure is genuinely unrelated to the diff.

## Implementation

### Step 1: Identify failing / stuck checks

```bash
PR="${1:-}"                 # PR number/URL, or empty → current branch
REPO="${REPO:-Data-Wise/craft}"
# gh pr checks exits 8 when any check is pending/failed — capture, don't chain.
gh pr checks ${PR} --repo "$REPO" --json name,state,link > /tmp/ci-checks.json 2>/tmp/ci-err || true
if [ ! -s /tmp/ci-checks.json ]; then
  echo "No open PR found for this branch. Pass a PR explicitly: /craft:ci:triage <pr>"; exit 0
fi
```

Extract the `FAILURE` and `PENDING` checks and their run IDs (from the `link`
field, `runs/<id>`). `PENDING` is labelled **INFRA-STUCK** separately — a check
stuck pending (e.g. the "Validate Plugin Structure" runner queue) is an `--admin`
candidate after ~3 min, not a code failure.

### Step 2: Fetch each failing run's log

```bash
# --log-failed exits non-zero while a run is still in progress; tolerate it.
gh run view "$RUN_ID" --repo "$REPO" --log-failed 2>/dev/null | head -200 > /tmp/ci-log.txt || true
```

### Step 3: Get the PR's changed-file set

```bash
git diff origin/dev...HEAD --name-only 2>/dev/null > /tmp/ci-diff.txt \
  || gh pr diff ${PR} --repo "$REPO" --name-only > /tmp/ci-diff.txt
```

### Step 4: Classify (the core logic)

The log's error sites (`path:line`) are matched against the changed-file set.
This function is the single source of truth — `tests/test_ci_triage_unit.py`
extracts and exercises it directly.

```python
import re

INFRA_MARKERS = (
    "runner", "npm err", "rate limit", "timeout", "http 403", "http 429",
    "connection refused", "could not resolve host", "no space left",
)
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_FILE_RE = re.compile(r"([\w./-]+\.(?:py|sh|ya?ml|rb|md|js|ts)):(\d+)")

_RECOMMEND = {
    "DIFF-CAUSED": "Fix the failure in your code, then re-push.",
    "PRE-EXISTING": "--admin merge may be justified; confirm the failure is unrelated to your diff first.",
    "INFRA-FLAKE": "Re-run the failed jobs: gh run rerun <run-id> --failed.",
    "PARTIAL": "Mixed: fix the diff-owned failures, then re-evaluate the rest.",
}


def classify_failure(log_lines, diff_files):
    """Classify a failing CI run from its log against the PR's changed files.

    Returns {class, confidence, evidence, recommendation}. Pure / stdlib-only so
    it is unit-testable without a network or a live gh CLI.
    """
    diff = set(diff_files)
    text = "\n".join(_ANSI_RE.sub("", ln) for ln in log_lines)
    low = text.lower()
    infra = any(m in low for m in INFRA_MARKERS)

    sites = _FILE_RE.findall(text)  # [(path, lineno), ...]
    in_diff, out_diff, evidence = [], [], []
    for path, lineno in sites:
        norm = path.lstrip("./")
        evidence.append(f"{norm}:{lineno}")
        if any(norm == d or norm.endswith("/" + d) or d.endswith("/" + norm) for d in diff):
            in_diff.append(norm)
        else:
            out_diff.append(norm)

    if not sites:
        if not text.strip() or infra:
            cls = "INFRA-FLAKE"
        else:
            cls = "PRE-EXISTING"
        confidence = "LOW"
    elif in_diff and not out_diff:
        cls, confidence = "DIFF-CAUSED", "HIGH"
    elif out_diff and not in_diff:
        cls = "INFRA-FLAKE" if infra else "PRE-EXISTING"
        confidence = "HIGH"
    else:
        cls, confidence = "PARTIAL", "HIGH"

    return {
        "class": cls,
        "confidence": confidence,
        "evidence": evidence[:3],
        "recommendation": _RECOMMEND[cls],
    }
```

### Step 5: Render the verdict

```text
┌─ CI TRIAGE ─ Validate Plugin Structure ─────────────────────────┐
│ Verdict:    PRE-EXISTING   (confidence: HIGH)                    │
│ Evidence:   tests/test_mermaid_dogfood.py:42                     │
│             tests/test_mermaid_e2e.py:45                         │
│ Recommend:  --admin merge may be justified; confirm the         │
│             failure is unrelated to your diff first.            │
└─────────────────────────────────────────────────────────────────┘
```

Badge per class: **DIFF-CAUSED** (red), **PRE-EXISTING** / **INFRA-STUCK**
(yellow), **INFRA-FLAKE** (yellow), **PARTIAL** (yellow). Always print the
matched `file:line` evidence so the verdict is auditable, never a bare assertion.

### Step 6: `--json` mode

When `--json` is set, skip the box and emit:

```json
{
  "checks": [
    {"name": "...", "state": "FAILURE", "run_id": "123",
     "class": "PRE-EXISTING", "confidence": "HIGH",
     "evidence": ["tests/x.py:42"], "recommendation": "..."}
  ],
  "summary": {"diff_caused": 0, "pre_existing": 1, "infra_flake": 0, "partial": 0}
}
```

## Error Handling

- **No open PR** for the branch → tell the user to pass `<pr>` explicitly.
- **`gh pr checks` exit 8** → expected when checks are pending/failed; the output
  is still valid (see [[gh-pr-checks-exit-code-8-means-pending-or-failing]]).
- **Run still in progress** → `--log-failed` yields nothing; report INFRA-STUCK /
  "still running" rather than a false verdict.
- **All checks green** → report "nothing to triage".

## See Also

- `/craft:ci:status` — the broader cross-repo CI dashboard
- `/craft:code:ci-fix` — apply a fix once the cause is known (DIFF-CAUSED)
- `/craft:git:unprotect` — needed before an `--admin` merge on a protected branch
