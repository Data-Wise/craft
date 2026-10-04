---
type: llm
weight: 2
---

The response says there is a soft cap of 2 concurrent orchestrate-dispatch dispatches per session; a 3rd or later concurrent dispatch requires an explicit AskUserQuestion confirmation before calling Agent; and the counter tracks only background Agent calls made via the orchestrate-dispatch flow, not unrelated background Agent calls (research agents, doc agents, etc.). A vague or generic answer, or one that says it does not know, fails.
