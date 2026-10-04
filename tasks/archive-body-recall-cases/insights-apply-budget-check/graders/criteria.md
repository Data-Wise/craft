---
type: llm
weight: 2
---

The response says the budget is 200 lines, the check is python3 utils/claude_md_optimizer.py ~/.claude/CLAUDE.md --check, and if over budget it offers options such as running the optimizer to trim P2 content, keeping as-is (it will be truncated at 200 lines), or manual editing. A vague or generic answer, or one that says it does not know, fails.
