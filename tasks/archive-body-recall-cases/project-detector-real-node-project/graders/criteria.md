---
type: llm
weight: 2
---

The response says a package.json is a real Node project if it has a main field, a bin field, a non-empty dependencies (not just devDependencies), or an exports field; a package.json with only devDependencies is just tooling, not a Node project. A vague or generic answer, or one that says it does not know, fails.
