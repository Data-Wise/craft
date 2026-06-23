"""Ledger path + cross-link helpers for /craft:grill.

grill ALWAYS owns GRILL-<slug>-<date>.md and never rewrites a brainstorm SPEC body.
The only touch to a SPEC is an idempotent, atomic one-line back-link.
"""
import glob
import os
import re

_BACKLINK = "> Interrogated by grill — see [{name}]({name})\n"


def _slug(topic):
    """Filesystem-safe slug: lowercase, [a-z0-9] runs -> '-', no traversal, capped."""
    s = re.sub(r"[^a-z0-9]+", "-", str(topic).strip().lower()).strip("-")
    return (s or "untitled")[:60]


def _atomic_write(path, text):
    """Write via temp + os.replace so a crash never leaves a truncated file."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def resolve_ledger_path(topic, date, specs_dir):
    """Always return grill's own file path; never the brainstorm SPEC."""
    return os.path.join(specs_dir, f"GRILL-{_slug(topic)}-{date}.md")


def spec_crosslink(topic, specs_dir):
    """Return the latest brainstorm SPEC filename for this slug (any date), or None."""
    matches = glob.glob(os.path.join(specs_dir, f"SPEC-{_slug(topic)}-*.md"))
    if not matches:
        return None
    return os.path.basename(max(matches, key=os.path.getmtime))


def add_backlink(spec_path, grill_filename):
    """Insert an idempotent, atomic one-line back-link into the SPEC (no body rewrite)."""
    with open(spec_path, encoding="utf-8") as f:
        body = f.read()
    if grill_filename in body:
        return
    _atomic_write(spec_path, body.rstrip("\n") + "\n\n" + _BACKLINK.format(name=grill_filename))
