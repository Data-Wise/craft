#!/usr/bin/env python3
"""R03 checker: exit 1 if a PUBLIC marketplace.json references a PRIVATE repo.

A PII-bearing plugin (savant carries research-profile PII) must be published
only to a *private* marketplace; the public Data-Wise marketplace must never
list it. This scans an in-repo ``marketplace.json`` and fails if any plugin
entry's source repo basename is in ``PRIVATE_REPOS``.

The denylist is a hardcoded constant on purpose: CI must decide this with no
network access (no querying GitHub for repo visibility), so "private" is a
curated, CI-portable set rather than a live lookup.

The argument may be the ``marketplace.json`` file itself OR a directory that
contains one (mirrors how ``{target}`` is a dir for no-broken-symlinks, so the
selftest can hand this checker a fixture DIR). An absent path prints a visible
``skip:`` line and returns 0 (mirrors no_duplicate_canon.py) -- a checker that
can't find its input must never masquerade as a green pass.

Usage: no_private_in_public_marketplace.py <marketplace.json | dir>"""
import json, os, sys

# Repos whose plugins carry PII and may live only on a PRIVATE marketplace.
# Hardcoded for CI portability (no network repo-visibility lookup). Compared
# against the *basename* of a "OWNER/NAME" repo ref, so owner is irrelevant.
PRIVATE_REPOS = {"savant"}


def resolve(path):
    """Return the marketplace.json path for a file-or-dir arg, or None if absent."""
    if os.path.isdir(path):
        cand = os.path.join(path, "marketplace.json")
        return cand if os.path.isfile(cand) else None
    return path if os.path.isfile(path) else None


def repo_refs(doc):
    """Yield (plugin_name, repo_ref) for every plugin source repo in the doc.

    Tolerant of the schema's shape: a plugin's ``source`` is normally
    ``{"source": "github", "repo": "OWNER/NAME"}``, but ``source`` may also be
    a bare string. Any ``repository`` URL on the entry is scanned too.
    """
    for p in doc.get("plugins") or []:
        name = p.get("name", "?")
        src = p.get("source")
        if isinstance(src, dict):
            ref = src.get("repo") or src.get("source")
            if isinstance(ref, str):
                yield name, ref
        elif isinstance(src, str):
            yield name, src
        repository = p.get("repository")
        if isinstance(repository, str):
            yield name, repository


def basename(ref):
    """Last path component of a repo ref, stripped of a trailing '.git'.

    Handles 'OWNER/NAME', a full 'https://github.com/OWNER/NAME(.git)' URL, and
    a bare 'NAME'. Returns the lowercased name for case-insensitive matching."""
    name = ref.rstrip("/").rsplit("/", 1)[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name.lower()


def offenders(doc):
    """Return [(plugin_name, repo_ref), ...] referencing a private repo."""
    deny = {r.lower() for r in PRIVATE_REPOS}
    return [(n, ref) for n, ref in repo_refs(doc) if basename(ref) in deny]


def main():
    if len(sys.argv) < 2:
        print("usage: no_private_in_public_marketplace.py <marketplace.json | dir>")
        return 2
    arg = os.path.expanduser(sys.argv[1])
    mpath = resolve(arg)
    if mpath is None:
        print("  skip: no marketplace.json at %s" % arg)
        return 0
    try:
        with open(mpath, encoding="utf-8") as f:
            doc = json.load(f)
    except (ValueError, OSError) as e:
        print("  error: cannot parse %s: %s" % (mpath, e))
        return 1
    bad = offenders(doc)
    for name, ref in bad:
        print("  private-repo ref in public marketplace: plugin '%s' -> %s" % (name, ref))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
