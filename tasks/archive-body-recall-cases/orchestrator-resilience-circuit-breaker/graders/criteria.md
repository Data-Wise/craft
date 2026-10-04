---
type: llm
weight: 2
---

The response says 3 consecutive failures trigger OPEN state, after a 60s cooldown the circuit goes HALF-OPEN (attempting 1 retry), and 2 consecutive successes return it to CLOSED. A vague or generic answer, or one that says it does not know, fails.
