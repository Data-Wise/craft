# Statistical Research Plugin - Private Installation

**For personal use only** - Not published to npm or Homebrew

---

## Quick Install

### Development Mode (Recommended)

Use this if you want to edit the plugin and see changes immediately:

```bash
cd ~/projects/dev-tools/claude-plugins/statistical-research
./install-private.sh --dev
```

This creates a symlink to the current directory. Any changes you make to commands, skills, or lib files will be immediately available in Claude Code.

### Production Mode

Use this for a stable copy:

```bash
cd ~/projects/dev-tools/claude-plugins/statistical-research
./install-private.sh
```

This copies files to `~/.claude/plugins/statistical-research/`. To update, run `./install-private.sh --force`.

---

## Installation Options

```bash
./install-private.sh [OPTIONS]

Options:
  --dev         Install in development mode (symlink)
  --force, -f   Force reinstall (remove existing)
  --help, -h    Show help message
```

---

## What Gets Installed

**Target location:** `~/.claude/plugins/statistical-research/`

**Contents:**
- 13 slash commands (literature, manuscript, simulation, research)
- 17 A-grade auto-activating skills
- 3 shell API wrappers (arXiv, Crossref, BibTeX)

---

## Available Commands

### Literature Search
- `/lit:arxiv` - Search arXiv papers
- `/lit:doi` - Lookup paper by DOI
- `/lit:bib-add` - Add citation to BibTeX
- `/lit:bib-search` - Search BibTeX library

### Manuscript Writing
- `/ms:methods` - Write methods section
- `/ms:results` - Write results section
- `/ms:proof` - Write mathematical proof
- `/ms:reviewer` - Respond to reviewers

### Simulation Studies
- `/sim:design` - Design simulation study
- `/sim:analysis` - Analyze simulation results

### Research Planning
- `/research:hypothesis` - Formulate hypotheses
- `/research:analysis-plan` - Create analysis plan
- `/research:lit-gap` - Find literature gaps

### Auto-Activating Skills (17)

**Mathematical (4 skills):**
- Asymptotic Theory
- Identification Theory
- Mathematical Foundations
- Proof Architect

**Implementation (5 skills):**
- Algorithm Designer
- Computational Inference
- Numerical Methods
- Simulation Architect
- Statistical Software QA

**Writing (3 skills):**
- Methods Communicator
- Methods Paper Writer
- Publication Strategist

**Research (5 skills):**
- Cross-Disciplinary Ideation
- Literature Gap Finder
- Mediation Meta-Analyst
- Method Transfer Engine
- Sensitivity Analyst

---

## Uninstall

```bash
cd ~/projects/dev-tools/claude-plugins/statistical-research
./uninstall-private.sh
```

Or manually:
```bash
rm -rf ~/.claude/plugins/statistical-research
```

---

## Development Workflow

### Using Development Mode

1. **Install in dev mode:**
   ```bash
   ./install-private.sh --dev
   ```

2. **Edit files directly:**
   ```bash
   # Edit a command
   vim commands/literature/arxiv.md

   # Edit a skill
   vim skills/mathematical/asymptotic-theory/SKILL.md

   # Edit API wrapper
   vim lib/arxiv-api.sh
   ```

3. **Changes are immediately active** - No need to reinstall!

4. **Test your changes** in Claude Code

### Switching from Dev to Production

```bash
# Remove dev installation
./uninstall-private.sh

# Install production copy
./install-private.sh
```

---

## Testing

Run unit tests to verify installation:

```bash
cd ~/projects/dev-tools/claude-plugins/statistical-research
./tests/test-plugin-structure.sh
```

**Expected output:**
```
✅ All tests passed!
📊 Summary:
  - Commands: 13
  - Skills: 17
  - API wrappers: 3
```

---

## Troubleshooting

### Plugin not showing up in Claude Code

1. Check installation:
   ```bash
   ls -la ~/.claude/plugins/statistical-research
   ```

2. Verify plugin.json exists:
   ```bash
   cat ~/.claude/plugins/statistical-research/.claude-plugin/plugin.json
   ```

3. Restart Claude Code

### Development mode changes not appearing

1. Verify symlink:
   ```bash
   ls -la ~/.claude/plugins/statistical-research
   # Should show: ... -> /Users/dt/projects/dev-tools/claude-plugins/statistical-research
   ```

2. If it's a directory instead of symlink:
   ```bash
   ./uninstall-private.sh
   ./install-private.sh --dev
   ```

### Permission errors

```bash
chmod +x install-private.sh uninstall-private.sh
chmod +x scripts/*.sh
chmod +x lib/*.sh
```

---

## File Structure

```
statistical-research/
├── .claude-plugin/
│   └── plugin.json             # Plugin metadata
├── commands/
│   ├── literature/             # 4 commands
│   ├── manuscript/             # 4 commands
│   ├── simulation/             # 2 commands
│   └── research/               # 3 commands
├── skills/                     # 17 A-grade skills
│   ├── mathematical/           # 4 skills
│   ├── implementation/         # 5 skills
│   ├── writing/                # 3 skills
│   └── research/               # 5 skills
├── lib/                        # Shell API wrappers
│   ├── arxiv-api.sh
│   ├── crossref-api.sh
│   └── bibtex-utils.sh
├── scripts/
│   ├── install.sh              # Standard installer (for npm)
│   └── uninstall.sh            # Standard uninstaller
├── tests/
│   └── test-plugin-structure.sh
├── install-private.sh          # 👈 Private installer (this guide)
├── uninstall-private.sh        # 👈 Private uninstaller
├── INSTALL-PRIVATE.md          # 👈 This file
├── package.json
├── README.md
└── LICENSE
```

---

## Why Private?

This plugin contains:
- Personal research workflows
- Domain-specific statistical knowledge
- Custom configurations for your work

It's designed for **your personal use** and not intended for public distribution.

The rforge-orchestrator plugin is the public-facing plugin published to Homebrew.

---

## Updating

### Development Mode
Changes are automatic - just edit and use!

### Production Mode
```bash
cd ~/projects/dev-tools/claude-plugins/statistical-research
./install-private.sh --force
```

---

## Related Plugins

- **rforge-orchestrator** - Public plugin for RForge MCP delegation
  - Install: `brew install data-wise/tap/rforge-orchestrator`
  - Repository: https://github.com/Data-Wise/claude-plugins

---

## Support

For issues or questions:
- Check tests: `./tests/test-plugin-structure.sh`
- Review logs: `~/.claude/logs/`
- Repository: https://github.com/Data-Wise/claude-plugins (private access)

---

**Installation command:**
```bash
cd ~/projects/dev-tools/claude-plugins/statistical-research
./install-private.sh --dev
```
