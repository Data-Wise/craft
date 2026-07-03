# Scaffold Templates

Canonical templates for test plans and documentation sections.
All spec producers (brainstorm-insights, orchestrate) point here (D9b).

---

## Test plan (TDD)

Template from SPEC §3.2 — red-first, contract-asserting:

```markdown
## N. Test plan (TDD)
Tier selection (auto): e2e + dogfood. unit N/A — no new parser/script.
integration N/A — single-command. Markers: e2e, dogfood.

### Na. e2e — structural, no execution (tests/test_<feat>_e2e.py)
- [ ] **test_<feat>_scope** (EDIT/NEW): assert the COMPLETE declarer set (any add/remove breaks it).
- [ ] **<contract> declared**: new contract present AND old/inverted contract absent.

### Nb. dogfood — behavioral, real invocation (tests/test_<feat>_dogfood.py)
- [ ] **<behavior> fires**: invoke on a fixture → assert real output/side-effect.
- [ ] **<opt-out> skips**: same invocation with the disable flag → effect absent.

Red-first: write Na/Nb FAILING first; implement to green; run via /craft:test.
```

---

## Documentation & Discoverability

Template lifted verbatim from `commands/workflow/brainstorm.md:407-418`:

**REQUIRED SECTION — Documentation & Discoverability:** Every captured spec MUST include a `## Documentation & Discoverability` section so docs are never an afterthought. Code is not "done" until users can find and learn it. Mirror the surface a shipped craft feature carries (tailor to what the feature actually touches; mark N/A explicitly):

```markdown
## Documentation & Discoverability

- [ ] Tutorial (`docs/tutorials/TUTORIAL-<topic>.md`)
- [ ] Help + command reference pages (`docs/help/<topic>.md`, `docs/commands/<topic>.md`)
- [ ] REFCARD entry (`docs/REFCARD.md`; dedicated `docs/reference/REFCARD-<TOPIC>.md` if large)
- [ ] Help hub / discovery (`/craft:hub` auto-surfaces via frontmatter; add `commands/smart-help.md` entry)
- [ ] Website (`mkdocs.yml` nav + guides; `mkdocs build`) and `docs/skills-agents.md` catalog row
- [ ] CHANGELOG `[Unreleased]` + count bumps; `validate-counts.sh` + `docs-staleness-check.sh` clean
```

---

## Site Consistency

Advisory checklist for structural site checks — **not a hard gate**. The release pipeline already
hard-gates docs staleness (`docs-staleness-check.sh --non-interactive`, release Step 3b); this
block exists so structural drift is checked *during* feature work too, without adding a second
blocking gate. Each box names the real tool that performs the check — never manual recall.

```markdown
## Site Consistency

- [ ] mkdocs nav updated (new pages added to `mkdocs.yml` nav)?
- [ ] index file updated (if new top-level doc)?
- [ ] `/craft:site:update` / `docs-staleness-check.sh` run?
```
