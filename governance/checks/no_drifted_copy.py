#!/usr/bin/env python3
"""R04 checker: a consumer copy of a canon skill must not have DRIFTED from canon.

R04-consume-not-copy, automated as CONTENT drift — and deliberately distinct from
R07-version-is-truth. R07 checks *version-pin* equality (metadata); R04 checks the
actual `SKILL.md` *bytes*. A skill can carry a matching version pin yet have a
hand-edited body — R07 stays green, R04 catches it. If a skill is present on a
consumer surface AND in a canon repo, their `SKILL.md` must be byte-identical;
a divergence means the copy was edited (or copied then drifted) instead of being
consumed via `plugin update`. The installer is the only writer; a drifted copy is
the visible symptom of bypassing it.

Two modes (mirrors the R03 checker):
  - FIXTURE: <root> contains `consumer/` and `canon/` subdirs (self-contained, so
    selftest — which passes one path for every token — can exercise it).
  - LIVE: <consumer_dir> is the surface (e.g. ~/.claude/skills); canons default to
    the savant + scholar skill dirs (override with extra args).

Needs a consumer surface and >= 1 canon present; on a runner without the canon
repos the check is vacuous — say so out loud, never a silent pass.

Usage: no_drifted_copy.py <consumer_dir_or_fixture_root> [<canon_dir> ...]
"""
import os, sys

DEFAULT_CANONS = [
    os.path.expanduser("~/projects/dev-tools/savant/src/plugin-api/skills"),
    os.path.expanduser("~/projects/dev-tools/scholar/src/plugin-api/skills"),
]


def skill_md(d, name):
    p = os.path.join(d, name, "SKILL.md")
    return p if os.path.isfile(p) else None


def canon_index(canon_dirs):
    """{skill_name: SKILL.md path} across the given canon dirs (first wins)."""
    out = {}
    for c in canon_dirs:
        if os.path.isdir(c):
            for n in sorted(os.listdir(c)):
                p = skill_md(c, n)
                if p:
                    out.setdefault(n, p)
    return out


def _read(p):
    with open(p, "rb") as f:
        return f.read()


def resolve(arg):
    """Return (consumer_dir, canon_dirs). FIXTURE mode when arg has consumer/ +
    canon/ subdirs; else LIVE mode (default canons, or extra argv canons)."""
    consumer_sub, canon_sub = os.path.join(arg, "consumer"), os.path.join(arg, "canon")
    if os.path.isdir(consumer_sub) and os.path.isdir(canon_sub):
        return consumer_sub, [canon_sub]
    canons = [os.path.expanduser(a) for a in sys.argv[2:]] or DEFAULT_CANONS
    return arg, [c for c in canons if os.path.isdir(c)]


def main():
    if len(sys.argv) < 2:
        print("usage: no_drifted_copy.py <consumer_dir_or_fixture_root> [<canon_dir> ...]")
        return 2
    consumer, canons = resolve(sys.argv[1])
    if not os.path.isdir(consumer):
        print("  skip: consumer dir absent: %s" % consumer)
        return 0
    if not canons:
        print("  skip: no canon dir present -> drift check is vacuous here")
        return 0
    drifted = []
    for name, canon_md in sorted(canon_index(canons).items()):
        cons_md = skill_md(consumer, name)
        if not cons_md:
            continue  # not installed here (or structured differently) — not a drifted copy
        if _read(cons_md) != _read(canon_md):
            drifted.append(name)
            print("  drifted copy: '%s' SKILL.md differs from canon — re-consume via `plugin update`" % name)
    if drifted:
        return 1
    print("  ok: no consumer skill has drifted from its canon SKILL.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
