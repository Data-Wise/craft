#!/usr/bin/env python3
"""Add deprecated: true + replaced-by: frontmatter to Batch 2 source commands."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DEPRECATIONS: dict[str, str] = {
    # 2 → skills/check/
    "commands/check.md": "skills/check/",
    "commands/check/gen-validator.md": "skills/check/",
    # 4 → skills/orchestration/plan-orchestrator/
    "commands/orchestrate/plan.md": "skills/orchestration/plan-orchestrator/",
    "commands/plan/feature.md": "skills/orchestration/plan-orchestrator/",
    "commands/plan/roadmap.md": "skills/orchestration/plan-orchestrator/",
    "commands/plan/sprint.md": "skills/orchestration/plan-orchestrator/",
    # 2 → skills/workflow/brainstorm-insights/
    "commands/workflow/brainstorm.md": "skills/workflow/brainstorm-insights/",
    "commands/workflow/insights.md": "skills/workflow/brainstorm-insights/",
    # 1 → skills/code/demonstration-builder/
    "commands/code/demo.md": "skills/code/demonstration-builder/",
    # 1 → skills/testing/test-strategist/ (existing skill already covers this)
    "commands/code/coverage.md": "skills/testing/test-strategist/",
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
