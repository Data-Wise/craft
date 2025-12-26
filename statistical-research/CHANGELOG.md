# Changelog - Statistical Research Plugin

All notable changes to the Statistical Research plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2025-12-26

### Added - Method Scout Command

Migrated unique research command from user commands into the plugin:

#### New Command
- **`/research:method-scout`** - Scout statistical methods for a research problem
  - Search across disciplines for relevant techniques
  - Identify method assumptions and requirements
  - Compare alternative approaches
  - Find seminal papers and tutorials
  - Integrates with MCP tools (arxiv_search, crossref_lookup)

### Changed
- **Total commands:** 13 → 14
- **Plugin installed via symlink** for easier development

---

## [1.0.0] - 2024-12-23

### Added - Initial Release

#### Commands (13 total)

**Literature Management (4 commands)**
- **`/research:arxiv`** - Search arXiv for statistical papers
- **`/research:doi`** - Look up paper metadata by DOI
- **`/research:bib:search`** - Search BibTeX files for entries
- **`/research:bib:add`** - Add BibTeX entries to bibliography

**Manuscript Writing (4 commands)**
- **`/research:manuscript:methods`** - Write methods sections
- **`/research:manuscript:results`** - Write results sections
- **`/research:manuscript:reviewer`** - Generate reviewer responses
- **`/research:manuscript:proof`** - Review mathematical proofs

**Simulation Studies (2 commands)**
- **`/research:simulation:design`** - Design Monte Carlo studies
- **`/research:simulation:analysis`** - Analyze simulation results

**Research Planning (3 commands)**
- **`/research:lit-gap`** - Identify literature gaps
- **`/research:hypothesis`** - Generate research hypotheses
- **`/research:analysis-plan`** - Create statistical analysis plans

#### Skills (17 A-Grade Skills)

**Mathematical (4 skills)**
- proof-architect, mathematical-foundations, identification-theory, asymptotic-theory

**Implementation (5 skills)**
- simulation-architect, algorithm-designer, numerical-methods, computational-inference, statistical-software-qa

**Writing (3 skills)**
- methods-paper-writer, publication-strategist, methods-communicator

**Research (5 skills)**
- literature-gap-finder, cross-disciplinary-ideation, method-transfer-engine, mediation-meta-analyst, sensitivity-analyst

#### Shell API Wrappers
- `arxiv-api.sh` - arXiv paper search and PDF download
- `crossref-api.sh` - DOI lookup and BibTeX retrieval
- `bibtex-utils.sh` - BibTeX file search, add, format

---

## Version History Summary

| Version | Date | Major Changes |
|---------|------|---------------|
| **1.1.0** | 2025-12-26 | Added method-scout command |
| **1.0.0** | 2024-12-23 | Initial release: 13 commands, 17 skills |

---

**Last Updated:** 2025-12-26
**Maintained By:** Data-Wise
**License:** MIT
