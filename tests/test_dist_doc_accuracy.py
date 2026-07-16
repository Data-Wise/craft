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
#   - skills/docs/claude-md/references/init.md (was commands/docs/claude-md/init.md
#     before the v4 consolidation) — illustrative sample OUTPUT blocks with
#     intentionally-varied fake numbers (commands: 108 / skills: 21), not claims.
CURATED_FILES = [
    "commands/dist/homebrew.md",
    "commands/dist/marketplace.md",
    "commands/docs/quickstart.md",
    "skills/distribution/dist-extras/SKILL.md",
    "skills/distribution/distribution-strategist/SKILL.md",
    "skills/distribution/homebrew-formula-expert/SKILL.md",
    "skills/distribution/homebrew-multi-formula/SKILL.md",
    "skills/distribution/homebrew-setup-wizard/SKILL.md",
    "skills/distribution/homebrew-workflow-expert/SKILL.md",
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
    Case-insensitive: headline copy often reads "**45 Skills**" (Title Case),
    which a case-sensitive match silently misses (caught by an H2 planted-defect
    test: a stale "44 Skills" in docs/index.md went undetected until this fix).
    """
    for m in re.finditer(rf"(\d+)[ \t]+{noun}\b", text, re.IGNORECASE):
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


# --- H2 (SPEC-docs-site-hardening-consolidation-2026-07-02): site-wide guard ---
#
# Unlike CURATED_FILES above (a hand-picked dist-doc list), H2 scans ALL of
# docs/**/*.md for live plugin-wide count claims, per GRILL G-4: full breadth
# without the false-positive firehose. Historical contexts (changelogs,
# version-history, dated spec/plan/brainstorm/internal artifacts) legitimately
# cite past counts ("v2.34.0 had 108 commands") and must be excluded — only
# CURRENT-state claim pages get checked.

DOCS_EXCLUDE_DIRS = {
    "specs", "plans", "internal", "archive", ".archive",
    "brainstorm", "adr", "orch", "superpowers",
}
DOCS_EXCLUDE_FILENAMES = {"CHANGELOG.md", "VERSION-HISTORY.md"}

# Empirically-verified false positives from the first H2 sweep (2026-07-04):
# each is either (a) a versioned/dated snapshot doc ("**Version**: v1.24.0 |
# **Last Updated**: ...") frozen at an old release, or (b) tutorial/reference
# content illustrating the count-drift DETECTOR itself using example numbers
# ("'99 commands' -> '100'") — not a live claim about the current plugin.
# Grow this list if a future sweep finds more of the same class; if a file
# here starts making a genuine current-state claim, move it back into scope.
DOCS_EXCLUDE_RELPATHS = {
    "API-REFERENCE-COMMANDS.md",  # dated snapshot: Version v1.24.0, 2026-01-17
    "FEATURE-RELEASE-CLAUDE-MD.md",  # synthetic scaling-benchmark example (10/60/150 commands)
    "REFCARD.md",  # count_counts detector example row: "99 commands" -> "100"
    "api/DISCOVERY-API.md",  # cache-timing benchmark example, not a live total
    "architecture/HUB-V2-ARCHITECTURE.md",  # historical HUB-V2 design doc
    "cookbook/troubleshooting/claude-md-out-of-sync.md",  # deliberately shows a stale-vs-current example
    "dev/CONTRIBUTING-HUB-V2.md",  # example git commit message in a contributing guide
    "examples/docs-update-interactive-example.md",  # interactive-session transcript example
    "reference/ERROR-SCENARIOS.md",  # dated snapshot: Version v1.24.0, 2026-01-17
    "reference/REFCARD-DOCS-STALENESS.md",  # documents the detector's own exclusion-pattern examples
    "reference/REFCARD-DOCS-UPDATE.md",  # detector example table + sample transcript
    "tutorials/TUTORIAL-post-merge-pipeline.md",  # "'97 commands' when you now have 100" — illustrative
    "tutorials/claude-md-workflows.md",  # terminal-output transcript example
    "tutorials/interactive-docs-update-tutorial.md",  # before/after diff example
    "tutorials/TUTORIAL-first-10-minutes.md",  # dated UI mockup screenshot: "v2.22.0" / 107 Commands
    "guide/check-command-mastery.md",  # illustrative /craft:check output: deliberately shows
    # a stale-count WARNING ("CLAUDE.md shows '70 commands' — actual count is 107") to
    # demonstrate the detector catching drift; frozen scenario, not a live claim.
}


def _docs_site_files():
    docs_dir = REPO / "docs"
    for p in sorted(docs_dir.rglob("*.md")):
        rel = p.relative_to(docs_dir)
        if rel.parts and rel.parts[0] in DOCS_EXCLUDE_DIRS:
            continue
        if p.name in DOCS_EXCLUDE_FILENAMES:
            continue
        if str(rel) in DOCS_EXCLUDE_RELPATHS:
            continue
        yield p


DOCS_SITE_FILES = list(_docs_site_files())


@pytest.mark.parametrize("path", DOCS_SITE_FILES, ids=lambda p: str(p.relative_to(REPO)))
def test_no_stale_docs_site_command_count(path):
    text = path.read_text(encoding="utf-8")
    stale = [
        (n, ln) for n, ln in _claims(text, "commands", CMD_CLAIM_MIN)
        if n != CANON["commands"]
    ]
    assert not stale, (
        f"{path.relative_to(REPO)}: stale command-count claim(s) {stale} "
        f"(canonical = {CANON['commands']})"
    )


@pytest.mark.parametrize("path", DOCS_SITE_FILES, ids=lambda p: str(p.relative_to(REPO)))
def test_no_stale_docs_site_skill_count(path):
    text = path.read_text(encoding="utf-8")
    stale = [
        (n, ln) for n, ln in _claims(text, "skills", SKILL_CLAIM_MIN)
        if n != CANON["skills"]
    ]
    assert not stale, (
        f"{path.relative_to(REPO)}: stale skill-count claim(s) {stale} "
        f"(canonical = {CANON['skills']})"
    )
