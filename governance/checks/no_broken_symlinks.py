#!/usr/bin/env python3
"""R02/R08 checker: exit 1 if the target dir contains any broken symlink.
Usage: no_broken_symlinks.py <dir>"""
import os, sys

def main():
    if len(sys.argv) < 2:
        print("usage: no_broken_symlinks.py <dir>"); return 2
    d = os.path.expanduser(sys.argv[1])
    if not os.path.isdir(d):
        print("skip: %s is not a directory" % d); return 0
    broken = []
    for name in sorted(os.listdir(d)):
        p = os.path.join(d, name)
        if os.path.islink(p) and not os.path.exists(p):
            broken.append((name, os.readlink(p)))
    for n, t in broken:
        print("  broken: %s -> %s" % (n, t))
    return 1 if broken else 0

if __name__ == "__main__":
    sys.exit(main())
