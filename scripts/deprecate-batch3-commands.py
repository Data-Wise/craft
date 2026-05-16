#!/usr/bin/env python3
"""Add deprecated: true + replaced-by: frontmatter to Batch 3 source commands."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DEPRECATIONS: dict[str, str] = {
    # 3 → skills/docs/claude-md/
    "commands/docs/claude-md/init.md": "skills/docs/claude-md/",
    "commands/docs/claude-md/sync.md": "skills/docs/claude-md/",
    "commands/docs/claude-md/edit.md": "skills/docs/claude-md/",
    # 3 → skills/docs/navigation/
    "commands/docs/nav-update.md": "skills/docs/navigation/",
    "commands/site/add.md": "skills/docs/navigation/",
    "commands/site/nav.md": "skills/docs/navigation/",
    # 13 → skills/docs/site-management/
    "commands/site/audit.md": "skills/docs/site-management/",
    "commands/site/build.md": "skills/docs/site-management/",
    "commands/site/check.md": "skills/docs/site-management/",
    "commands/site/consolidate.md": "skills/docs/site-management/",
    "commands/site/create.md": "skills/docs/site-management/",
    "commands/site/deploy.md": "skills/docs/site-management/",
    "commands/site/init.md": "skills/docs/site-management/",
    "commands/site/preview.md": "skills/docs/site-management/",
    "commands/site/progress.md": "skills/docs/site-management/",
    "commands/site/publish.md": "skills/docs/site-management/",
    "commands/site/status.md": "skills/docs/site-management/",
    "commands/site/theme.md": "skills/docs/site-management/",
    "commands/site/update.md": "skills/docs/site-management/",
    # 3 → skills/distribution/dist-extras/
    "commands/dist/pypi.md": "skills/distribution/dist-extras/",
    "commands/dist/curl-install.md": "skills/distribution/dist-extras/",
    "commands/dist/marketplace.md": "skills/distribution/dist-extras/",
}


def patch_file(path: Path, replaced_by: str) -> str:
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
