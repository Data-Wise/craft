#!/usr/bin/env python3
"""R09 checker: load-bearing `.STATUS` claims must not have DRIFTED from git/manifest reality.

The governance thesis is *generated/audited beats hand-stamped prose* — which is why
`CLAUDE.md` rule blocks render from `RULES.yaml`. `.STATUS` is the next-most load-bearing
artifact still hand-stamped per PR, and it drifts. This checks the two claims that actually
mislead a future session if wrong:

  A. `version:` — the `.STATUS` version field must equal the manifest source-of-truth
     (`plugin.json` / `DESCRIPTION` / `package.json`, first found).
  B. shipped-tag — any `vX.Y.Z` named on a `SHIPPED`/`tagged` line must exist as a git tag.

It deliberately does NOT validate the prose body — only these two claims, to stay
false-positive-resistant. `severity: warn`.

Two modes (mirrors the R03/R04 checkers):
  - FIXTURE: <root> contains an `expected.json` sidecar — ground truth is supplied as data
    ({"manifest_version": ..., "tags": [...]}), so selftest can exercise it with no git.
  - LIVE: <root> is a repo; manifest version is read from the manifest and tags from
    `git -C <root> tag`.

When `.STATUS` is absent, or neither claim can be evaluated, the check is vacuous — say so
out loud, never a silent pass.

Usage: status_drift.py <repo_root_or_fixture_root>
"""
import json
import os
import re
import subprocess
import sys

_VER_FIELD = re.compile(r"^version:\s*(\S+)", re.MULTILINE)
# Plain semver only (vMAJOR.MINOR.PATCH). Deliberately does NOT capture a trailing
# suffix: craft tags are clean `vX.Y.Z`, and a greedy suffix swallows prose like a
# sentence-final `v2.37.0.` or a URL `…-v2.37.0.tar.gz` into phantom tag names.
_SHIPPED_TAG = re.compile(r"v\d+\.\d+\.\d+")


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def status_version(status_text):
    m = _VER_FIELD.search(status_text)
    return m.group(1) if m else None


def shipped_tags(status_text):
    """vX.Y.Z tokens appearing on a line that also says SHIPPED or tagged."""
    out = []
    for line in status_text.splitlines():
        if "SHIPPED" in line or "tagged" in line:
            out.extend(_SHIPPED_TAG.findall(line))
    # de-dup, preserve order
    seen, uniq = set(), []
    for t in out:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    return uniq


def manifest_version(root):
    """First of plugin.json / DESCRIPTION / package.json that carries a version."""
    pj = os.path.join(root, ".claude-plugin", "plugin.json")
    if os.path.isfile(pj):
        try:
            return json.loads(_read(pj)).get("version")
        except Exception:
            pass
    desc = os.path.join(root, "DESCRIPTION")
    if os.path.isfile(desc):
        m = re.search(r"^Version:\s*(\S+)", _read(desc), re.MULTILINE)
        if m:
            return m.group(1)
    npm = os.path.join(root, "package.json")
    if os.path.isfile(npm):
        try:
            return json.loads(_read(npm)).get("version")
        except Exception:
            pass
    return None


def git_tags(root):
    try:
        out = subprocess.run(["git", "-C", root, "tag"], capture_output=True,
                             text=True, timeout=10)
        return set(out.stdout.split()) if out.returncode == 0 else None
    except Exception:
        return None


def ground_truth(root):
    """(manifest_version, tags_set). FIXTURE mode when expected.json is present."""
    sidecar = os.path.join(root, "expected.json")
    if os.path.isfile(sidecar):
        data = json.loads(_read(sidecar))
        return data.get("manifest_version"), set(data.get("tags") or [])
    return manifest_version(root), git_tags(root)


def main():
    if len(sys.argv) < 2:
        print("usage: status_drift.py <repo_root_or_fixture_root>")
        return 2
    root = sys.argv[1]
    status_path = os.path.join(root, ".STATUS")
    if not os.path.isfile(status_path):
        print("  skip: no .STATUS at %s -> drift check is vacuous here" % root)
        return 0

    text = _read(status_path)
    claimed_version = status_version(text)
    claimed_tags = shipped_tags(text)
    truth_version, truth_tags = ground_truth(root)

    drift = []
    evaluated = False

    # Check A: version field vs manifest source-of-truth.
    if claimed_version is not None and truth_version is not None:
        evaluated = True
        if claimed_version != truth_version:
            drift.append(
                "  version drift: .STATUS says version %s but manifest is %s"
                % (claimed_version, truth_version)
            )

    # Check B: every shipped/tagged vX.Y.Z claim must have a real tag.
    if claimed_tags and truth_tags is not None:
        evaluated = True
        for t in claimed_tags:
            if t not in truth_tags:
                drift.append(
                    "  released-claim drift: .STATUS announces %s SHIPPED/tagged but no such git tag exists"
                    % t
                )

    if not evaluated:
        print("  skip: no comparable claim (manifest/tags unavailable) -> vacuous")
        return 0
    if drift:
        for d in drift:
            print(d)
        return 1
    print("  ok: .STATUS version + release claims match git/manifest reality")
    return 0


if __name__ == "__main__":
    sys.exit(main())
