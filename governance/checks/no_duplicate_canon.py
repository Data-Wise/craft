#!/usr/bin/env python3
"""R01 checker: exit 1 if any skill name appears in more than one canon.
Usage: no_duplicate_canon.py [<canon_skills_dir> ...]
Defaults to the savant + scholar skill dirs when no args are given."""
import os, sys

DEFAULT_CANONS = [
    os.path.expanduser("~/projects/dev-tools/savant/src/plugin-api/skills"),
    os.path.expanduser("~/projects/dev-tools/scholar/src/plugin-api/skills"),
]

def skills_in(d):
    out = set()
    if os.path.isdir(d):
        for n in os.listdir(d):
            if os.path.isfile(os.path.join(d, n, "SKILL.md")):
                out.add(n)
    return out

def main():
    canons = [os.path.expanduser(a) for a in sys.argv[1:]] or DEFAULT_CANONS
    seen, dups = {}, {}
    for c in canons:
        for s in skills_in(c):
            if s in seen:
                dups.setdefault(s, [seen[s]]).append(c)
            else:
                seen[s] = c
    for s, where in dups.items():
        print("  duplicate skill '%s' in: %s" % (s, ", ".join(where)))
    return 1 if dups else 0

if __name__ == "__main__":
    sys.exit(main())
