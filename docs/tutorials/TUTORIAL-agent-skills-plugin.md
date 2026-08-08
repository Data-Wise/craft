# Agent Skills Plugin Cheat Sheet

Run `claude plugin install agent-skills@addy-agent-skills`, then dispatch
one of its four review agents by name when you need a focused specialist
review.

## What it does

Supplies four specialist review agents for the `Agent` tool: `code-reviewer`
(correctness/readability/architecture/security/performance),
`security-auditor` (vulnerability + threat modeling), `test-engineer`
(test strategy/coverage), and `web-performance-auditor` (Core Web Vitals).

## Setup

```bash
claude plugin install agent-skills@addy-agent-skills
```

No further config — the review agents become available to the `Agent` tool
immediately.

## Gotchas

1. **Pick the agent by task, not by habit.** `code-reviewer` is the
   generalist; reach for `security-auditor` or `web-performance-auditor`
   specifically when the review needs that lens — a generic review can
   miss what a focused one catches.
2. **All four have full tool access.** They can read, write, and run
   commands — scope the dispatch prompt carefully if you only want a
   read-only review.
3. **Not a substitute for craft's own `code-reviewer` agent.** Craft ships
   its own review tooling (`/code-review`); this plugin's agents are an
   independent, complementary set — pick based on which framing fits, not
   by assuming one supersedes the other.
