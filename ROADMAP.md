# Craft Plugin Roadmap

## Current Version: 1.3.0

---

## v1.4.0 - Distribution Commands (Planned)

### New Commands

#### `/craft:dist:homebrew` - Homebrew Tap Management
Create and update Homebrew formula for projects:
- Detect project type (Python, Node, Go, Rust)
- Generate formula file with dependencies
- Calculate SHA256 for release tarballs
- Update existing formula for new versions
- Push to homebrew-tap repository

**Usage:**
```bash
/craft:dist:homebrew              # Create/update formula
/craft:dist:homebrew --tap user/tap  # Specify tap
/craft:dist:homebrew --version 1.2.3  # Specific version
```

#### `/craft:dist:curl-install` - Direct GitHub Installation
Generate curl-based installation scripts:
- Create `install.sh` for direct GitHub downloads
- Support multiple installation methods (binary, source)
- Include version detection and updates
- Add to README installation section

**Usage:**
```bash
/craft:dist:curl-install          # Generate install script
/craft:dist:curl-install --binary # Binary-only install
/craft:dist:curl-install --update-readme  # Add to README
```

**Example output:**
```bash
# One-liner installation
curl -fsSL https://raw.githubusercontent.com/user/repo/main/install.sh | bash

# Or with version
curl -fsSL https://github.com/user/repo/releases/download/v1.0.0/install.sh | bash
```

### Skills to Add
- `distribution-strategist` - Distribution channel recommendations
- `homebrew-formula-expert` - Formula best practices

---

## v1.5.0 - Release Automation (Future)

- `/craft:dist:pypi` - PyPI publishing workflow
- `/craft:dist:npm` - npm publishing workflow
- `/craft:dist:cargo` - Cargo publishing workflow
- `/craft:dist:release` - Multi-channel release orchestrator

---

## v1.6.0 - CI/CD Integration (Future)

- `/craft:ci:matrix` - Generate test matrix
- `/craft:ci:workflow` - Create GitHub Actions workflows
- `/craft:ci:badge` - Add/update README badges

---

## Ideas Backlog

- Monorepo support for distribution commands
- Version bumping automation
- Changelog-to-release-notes conversion
- Installation verification tests
- Cross-platform binary building

---

## Contributing

To request features, create an issue or add to this roadmap.
