#!/usr/bin/env python3
"""R02/R08 checker: exit 1 if the target dir contains any broken symlink.

Walks the target *recursively* (not just the top level) so a dead link nested
inside a skill — not only the common ``~/.claude/skills/<name>`` top-level
layout — is still caught. Symlinked directories are not descended into
(``followlinks=False``), which both flags broken links and avoids link cycles.

Usage: no_broken_symlinks.py <dir>"""
import os, sys

def find_broken(d):
    """Return [(relpath, target), ...] for every broken symlink under d."""
    broken = []
    for root, dirs, files in os.walk(d, followlinks=False):
        # A broken symlink can't be stat'd as a dir, so os.walk classifies it
        # under `files`; scan both lists to be safe across platforms.
        for name in sorted(dirs + files):
            p = os.path.join(root, name)
            if os.path.islink(p) and not os.path.exists(p):
                broken.append((os.path.relpath(p, d), os.readlink(p)))
    return broken

def main():
    if len(sys.argv) < 2:
        print("usage: no_broken_symlinks.py <dir>"); return 2
    d = os.path.expanduser(sys.argv[1])
    if not os.path.isdir(d):
        print("skip: %s is not a directory" % d); return 0
    broken = find_broken(d)
    for n, t in broken:
        print("  broken: %s -> %s" % (n, t))
    return 1 if broken else 0

if __name__ == "__main__":
    sys.exit(main())
