#!/usr/bin/env python3
"""Add deprecated: true + replaced-by: frontmatter to Batch 1 source commands.

Idempotent: skips files that already have a `deprecated:` key.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Mapping: source command (relative path) → replacement skill path
DEPRECATIONS: dict[str, str] = {
    # 7 → skills/workflow/adhd-workflow/
    "commands/workflow/done.md": "skills/workflow/adhd-workflow/",
    "commands/workflow/focus.md": "skills/workflow/adhd-workflow/",
    "commands/workflow/next.md": "skills/workflow/adhd-workflow/",
    "commands/workflow/recap.md": "skills/workflow/adhd-workflow/",
    "commands/workflow/refine.md": "skills/workflow/adhd-workflow/",
    "commands/workflow/spec-review.md": "skills/workflow/adhd-workflow/",
    "commands/workflow/stuck.md": "skills/workflow/adhd-workflow/",
    # 14 → skills/dev/git/ (10 git/* + 4 git/docs/*)
    "commands/git/branch.md": "skills/dev/git/",
    "commands/git/clean.md": "skills/dev/git/",
    "commands/git/git-recap.md": "skills/dev/git/",
    "commands/git/init.md": "skills/dev/git/",
    "commands/git/protect.md": "skills/dev/git/",
    "commands/git/protect-baseline.md": "skills/dev/git/",
    "commands/git/status.md": "skills/dev/git/",
    "commands/git/sync.md": "skills/dev/git/",
    "commands/git/unprotect.md": "skills/dev/git/",
    "commands/git/worktree.md": "skills/dev/git/",
    "commands/git/docs/learning-guide.md": "skills/dev/git/",
    "commands/git/docs/refcard.md": "skills/dev/git/",
    "commands/git/docs/safety-rails.md": "skills/dev/git/",
    "commands/git/docs/undo-guide.md": "skills/dev/git/",
    # 3 → skills/workflow/task-management/
    "commands/workflow/task-cancel.md": "skills/workflow/task-management/",
    "commands/workflow/task-output.md": "skills/workflow/task-management/",
    "commands/workflow/task-status.md": "skills/workflow/task-management/",
}


def patch_file(path: Path, replaced_by: str) -> str:
    """Add deprecation keys to a file's YAML frontmatter.

    Returns one of: 'patched', 'already-deprecated', 'no-frontmatter', 'missing'.
    """
    if not path.exists():
        return "missing"
    text = path.read_text()
    if not text.startswith("---\n"):
        return "no-frontmatter"
    end = text.find("\n---\n", 4)
    if end == -1:
        return "no-frontmatter"
    fm_block = text[4:end]
    if "\ndeprecated:" in "\n" + fm_block:
        return "already-deprecated"
    # Insert at the end of the frontmatter block, before the closing ---
    new_fm = fm_block.rstrip() + f"\ndeprecated: true\nreplaced-by: \"{replaced_by}\"\n"
    new_text = "---\n" + new_fm + "---\n" + text[end + 5:]
    path.write_text(new_text)
    return "patched"


def main() -> int:
    counts: dict[str, int] = {}
    for rel_path, replaced_by in DEPRECATIONS.items():
        result = patch_file(REPO_ROOT / rel_path, replaced_by)
        counts[result] = counts.get(result, 0) + 1
        marker = {"patched": "✓", "already-deprecated": "·",
                  "no-frontmatter": "?", "missing": "✗"}[result]
        print(f"  {marker} {rel_path}  →  {replaced_by}  [{result}]")
    print()
    print(f"Summary: {counts}")
    return 0 if counts.get("missing", 0) == 0 and counts.get("no-frontmatter", 0) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
