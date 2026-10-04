---
type: llm
weight: 2
---

The response says pass 1 is git branch --merged (fast-forward and merge-commit merges) and pass 2 is is_squash_merged from lib/git-utils.sh, which uses git cherry (exact patch-ID match) with a tree-diff fallback for multi-commit squashes. A vague or generic answer, or one that says it does not know, fails.
