"""Dist-doc accuracy guard (SPEC-dist-surface-hardening D6).

Closes the systemic gap (D2): before this, only commands/dist/homebrew.md was
guarded, so every other distribution-facing doc drifted on each release
(the 107→116 / 36→44 staleness the audit found across 6 files).

Strategy: compute the CANONICAL plugin counts from the tree, then assert that
every plugin-wide count CLAIM in the curated dist/doc files matches. The
threshold filters out incidental small numbers ("verify at least 3 commands")
so only full-inventory claims are checked — the test stays correct across
version bumps with no manual editing.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

# Files that make LIVE, plugin-wide count claims. Deliberately EXCLUDES:
#   - README.md — its top badge is maintained by bump-version.sh; its lower
#     half is release-history ("Total: 67 commands" per past version).
#   - commands/docs/claude-md/init.md — illustrative sample OUTPUT blocks with
#     intentionally-varied fake numbers (commands: 108 / skills: 21), not claims.
CURATED_FILES = [
    "commands/dist/homebrew.md",
    "commands/dist/marketplace.md",
    "commands/docs/quickstart.md",
    "skills/distribution/dist-extras/SKILL.md",
    "install.sh",
]

# A "commands" number >= this is a plugin-wide total (craft has ~116); smaller
# numbers ("at least 3 commands") are incidental and ignored.
CMD_CLAIM_MIN = 50
SKILL_CLAIM_MIN = 20


def canonical_counts() -> dict:
    commands = len(
        [
            p
            for p in (REPO / "commands").rglob("*.md")
            if p.name not in ("index.md", "README.md")
        ]
    )
    skills = len(list((REPO / "skills").rglob("SKILL.md")))
    agents = len(list((REPO / "agents").glob("*.md")))
    return {"commands": commands, "skills": skills, "agents": agents}


CANON = canonical_counts()


def _claims(text: str, noun: str, floor: int):
    """Yield (number, line) for '<N> <noun>' claims at or above floor.

    Uses `[ \\t]+` (not `\\s+`) so a match never spans a newline — otherwise
    'commands: 108\\n  skills:' would spuriously read as '108 skills'.
    """
    for m in re.finditer(rf"(\d+)[ \t]+{noun}\b", text):
        n = int(m.group(1))
        if n >= floor:
            line = text[: m.start()].count("\n") + 1
            yield n, line


@pytest.mark.parametrize("rel", CURATED_FILES)
def test_no_stale_command_count(rel):
    path = REPO / rel
    if not path.exists():
        pytest.skip(f"{rel} absent")
    text = path.read_text(encoding="utf-8")
    stale = [
        (n, ln) for n, ln in _claims(text, "commands", CMD_CLAIM_MIN)
        if n != CANON["commands"]
    ]
    assert not stale, (
        f"{rel}: stale command-count claim(s) {stale} "
        f"(canonical = {CANON['commands']})"
    )


@pytest.mark.parametrize("rel", CURATED_FILES)
def test_no_stale_skill_count(rel):
    path = REPO / rel
    if not path.exists():
        pytest.skip(f"{rel} absent")
    text = path.read_text(encoding="utf-8")
    stale = [
        (n, ln) for n, ln in _claims(text, "skills", SKILL_CLAIM_MIN)
        if n != CANON["skills"]
    ]
    assert not stale, (
        f"{rel}: stale skill-count claim(s) {stale} "
        f"(canonical = {CANON['skills']})"
    )


def test_no_phantom_scribe_formula():
    """The tap has `scribe-cli`, not `scribe`. Guard the distribution skills
    against re-introducing a bare `scribe` FORMULA reference (the `scribe`
    project name + `scribe` cask are a distinct namespace and allowed)."""
    mf = REPO / "skills/distribution/homebrew-multi-formula/SKILL.md"
    text = mf.read_text(encoding="utf-8")
    # In this skill, a lone `scribe` token in a formula-list/graph context is wrong.
    offenders = [
        text[: m.start()].count("\n") + 1
        for m in re.finditer(r"(?<![\w-])scribe(?![\w-])", text)
    ]
    assert not offenders, (
        f"homebrew-multi-formula: bare `scribe` at lines {offenders} — "
        f"use `scribe-cli` (the real tap formula)"
    )


def test_install_sh_uses_dynamic_counts():
    """install.sh banner must compute counts, never hardcode them (D1/D2)."""
    text = (REPO / "install.sh").read_text(encoding="utf-8")
    assert "${CMD_COUNT}" in text and "${SKILL_COUNT}" in text
    assert not re.search(r"\b\d+ commands \| \d+ agents", text)
