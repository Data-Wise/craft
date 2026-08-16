<!-- Must NOT flag: a line that DESCRIBES a TL;DR bug is not itself a TL;DR claim. -->
<!-- Found by dogfooding — the first build's contains-match flagged ADR-007's own context -->
<!-- table, which quotes the "8 specialized agents" line the ADR exists to explain. -->

# ADR-00N: some decision

## Context

| Bug | Why it was missed |
|---|---|
| `docs/skills-agents.md` — TL;DR claiming "8 specialized agents" above its own correct "2" | the intervening word broke the pattern |

Prose about the bug, quoting 8 specialized agents again for good measure.
