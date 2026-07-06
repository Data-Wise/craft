# /craft:docs:generate

> **Unified router across all 9 documentation generator commands**

---

## Synopsis

```bash
/craft:docs:generate <type>
```

---

## Description

Thin router for `api`, `guide`, `help`, `prompt`, `quickstart`, `site`, `tutorial`, `website`, and `workflow` — each generator has genuinely distinct logic, so this command dispatches to the canonical file rather than reimplementing any of them. The 9 direct commands remain fully functional.

## Examples

```bash
/craft:docs:generate guide        # Orchestrated feature guide + demo + refcard
/craft:docs:generate api          # OpenAPI/Swagger spec generation
/craft:docs:generate quickstart   # 5-minute quickstart guide
```

## See Also

- [/craft:docs:api](api.md), [/craft:docs:guide](guide.md), [/craft:docs:help](help.md), [/craft:docs:prompt](prompt.md), [/craft:docs:quickstart](quickstart.md), [/craft:docs:site](site.md), [/craft:docs:tutorial](tutorial.md), [/craft:docs:website](website.md), [/craft:docs:workflow](workflow.md) — the 9 canonical generators
