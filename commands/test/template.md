---
description: Manage Jinja2 templates for test generation
arguments:
  - name: action
    description: "Action: list, show, validate, render, create, edit, delete"
    required: true
  - name: template
    description: "Template path or type (e.g., plugin/test_structure, cli/conftest)"
    required: false
  - name: type
    description: "Project type filter: plugin, zsh, cli, mcp, _base"
    required: false
  - name: output
    description: Output path for render action
    required: false
---

# /craft:test:template - Template Lifecycle Manager

Manage the Jinja2 templates that power `/craft:test:gen`. List, inspect,
validate, render, and customize templates for all 4 project types.

## Quick Start

```bash
/craft:test:template list                       # List all templates
/craft:test:template list --type plugin         # List plugin templates
/craft:test:template show plugin/test_structure  # Show template source
/craft:test:template validate                    # Validate all templates
/craft:test:template render plugin/test_structure --output preview.py
```

## Actions

### list - Show Available Templates

```bash
/craft:test:template list
/craft:test:template list --type plugin
```

```
Templates
Type        Template              Tiers       Variables
plugin      test_structure.py.j2  smoke,unit  project_name, commands, skills
plugin      test_commands.py.j2   unit        commands, categories
plugin      test_skills.py.j2     unit        skills
plugin      test_agents.py.j2     unit        agents
plugin      test_content.py.j2    integration docs_dir, commands
plugin      test_lifecycle.py.j2  e2e         project_name, plugin_json
plugin      conftest.py.j2        -           project_name, test_dir
zsh         test_sourcing.sh.j2   smoke       plugin_file, functions
zsh         test_functions.sh.j2  unit        functions, aliases
zsh         test_completions.sh.j2 unit       completions
zsh         test_aliases.sh.j2    unit        aliases
zsh         test_e2e.sh.j2        e2e         plugin_file
cli         test_smoke.py.j2      smoke       entry_points, cli_name
cli         test_commands.py.j2   unit        commands, subcommands
cli         test_args.py.j2       unit        commands, flags
cli         test_errors.py.j2     integration cli_name
cli         test_output.py.j2     integration commands
cli         test_e2e.py.j2        e2e         cli_name, workflows
cli         conftest.py.j2        -           cli_name, entry_points
mcp         test_protocol.py.j2   unit        server_name
mcp         test_tools.py.j2      integration tools
mcp         test_resources.py.j2  integration resources
mcp         test_errors.py.j2     unit        server_name
mcp         conftest.py.j2        -           server_name, transport
_base       conftest_shared.py.j2 -           project_name
_base       helpers.py.j2         -           project_type
_base       bash_header.sh.j2     -           project_name
```

### show - Display Template Source

```bash
/craft:test:template show plugin/test_structure
```

Shows the raw Jinja2 template with syntax highlighting.

### validate - Check Template Integrity

```bash
/craft:test:template validate                    # All templates
/craft:test:template validate --type plugin      # Plugin templates only
/craft:test:template validate plugin/test_structure  # Specific template
```

Validates:

- Jinja2 syntax is valid (no unclosed tags)
- Required variables are documented in registry.json
- Rendered output is valid Python/Bash (parseable)
- Template file naming convention matches (`*.py.j2` or `*.sh.j2`)

```
Template Validation
  plugin/test_structure.py.j2    OK  (syntax, vars, output)
  plugin/test_commands.py.j2     OK  (syntax, vars, output)
  plugin/conftest.py.j2          WARN: missing variable 'agents' in registry
  zsh/test_sourcing.sh.j2        OK  (syntax, vars, output)
  cli/test_smoke.py.j2           OK  (syntax, vars, output)
  ...

Result: 23/24 passed, 1 warning
```

### render - Preview Rendered Output

```bash
/craft:test:template render plugin/test_structure
/craft:test:template render plugin/test_structure --output preview.py
```

Renders a template with sample variables from `registry.json` and shows the
output. Useful for previewing what `/craft:test:gen` will produce.

### create - Add a New Template

```bash
/craft:test:template create plugin/test_hooks
```

Creates a new template file in the appropriate directory with boilerplate
Jinja2 structure and registers it in `registry.json`.

### edit - Modify Existing Template

```bash
/craft:test:template edit plugin/test_structure
```

Opens the template for editing and re-validates after save.

### delete - Remove a Template

```bash
/craft:test:template delete plugin/test_hooks
```

Removes the template file and its registry entry. Requires confirmation.

## Template Directory Structure

```
templates/
  _base/                   # Shared partials (included by other templates)
    conftest_shared.py.j2  # Common conftest boilerplate
    helpers.py.j2          # Shared test helper functions
    bash_header.sh.j2      # Bash test script header
  plugin/                  # Claude Code plugin templates
    test_structure.py.j2
    test_commands.py.j2
    test_skills.py.j2
    test_agents.py.j2
    test_content.py.j2
    test_lifecycle.py.j2
    conftest.py.j2
  zsh/                     # ZSH plugin templates
    test_sourcing.sh.j2
    test_functions.sh.j2
    test_completions.sh.j2
    test_aliases.sh.j2
    test_e2e.sh.j2
  cli/                     # Python/Node CLI templates
    test_smoke.py.j2
    test_commands.py.j2
    test_args.py.j2
    test_errors.py.j2
    test_output.py.j2
    test_e2e.py.j2
    conftest.py.j2
  mcp/                     # MCP server templates
    test_protocol.py.j2
    test_tools.py.j2
    test_resources.py.j2
    test_errors.py.j2
    conftest.py.j2
  registry.json            # Template metadata and detection rules
```

## Registry Schema

The `templates/registry.json` file defines:

```json
{
  "types": {
    "plugin": {
      "detect": [".claude-plugin/plugin.json"],
      "templates": ["test_structure", "test_commands", ...],
      "variables": {
        "project_name": {"source": "plugin.json:name"},
        "commands": {"source": "find:commands/**/*.md"}
      }
    }
  }
}
```

See `/craft:test:gen` for full variable documentation.

## Integration

- `/craft:test:gen` - Uses templates to generate tests
- `/craft:test` - Runs generated tests
- `/craft:check` - Pre-flight validation
