---
type: llm
weight: 2
---

The response states the two filters: (1) a breadth threshold, the pair shares 3 or more basenames; (2) structural namespace containment, where one plugin's own name exactly matches a subdirectory name under another plugin's commands/ or skills/ tree, which is enough with just one match. A pair is reported if at least one fires. A vague or generic answer, or one that says it does not know, fails.
