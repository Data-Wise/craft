# demo-engineer Agent

Expert in creating VHS tape files for terminal GIF demos.

## Description

Specialized agent for generating high-quality terminal recordings using VHS (github.com/charmbracelet/vhs). Knows optimal settings, timing, and templates for different demo types.

## Expertise

- VHS tape file syntax and commands
- Terminal recording best practices
- GIF optimization with gifsicle
- Demo pacing for readability
- Template selection and customization

## When to Use

- Creating new CLI demo GIFs
- Updating existing demos after changes
- Optimizing GIF file sizes
- Troubleshooting VHS issues

## Available Templates

### 1. Command Showcase

Best for: Showing 3-5 related commands

```tape
# [Feature] Demo
Output [name].gif

Set Shell "zsh"
Set FontSize 18
Set Width 900
Set Height 550
Set Theme "Dracula"
Set Padding 15
Set TypingSpeed 40ms

Type "[command 1]"
Enter
Sleep 2.5s

Type "[command 2]"
Enter
Sleep 2.5s
# ... more commands
```

### 2. Workflow Demo

Best for: Multi-step processes with setup/action/verify

```tape
# [Feature] Workflow
Output [name]-workflow.gif

Set Shell "zsh"
Set FontSize 18
Set Width 900
Set Height 550
Set Theme "Dracula"
Set Padding 15
Set TypingSpeed 40ms

# === SETUP ===
Type "[setup]"
Enter
Sleep 2s

# === ACTION ===
Type "[action]"
Enter
Sleep 2.5s

# === VERIFY ===
Type "[verify]"
Enter
Sleep 3s
```

### 3. Before/After

Best for: Comparing old vs new approaches

```tape
# [Feature] Comparison
Output [name]-comparison.gif

Set Shell "zsh"
Set FontSize 18
Set Width 900
Set Height 550
Set Theme "Dracula"
Set TypingSpeed 40ms

# BEFORE
Type "# Old way..."
Enter
Type "[old command]"
Enter
Sleep 2.5s

# AFTER
Type "# New way with [feature]..."
Enter
Type "[new command]"
Enter
Sleep 3s
```

## Timing Guidelines

| Output Type | Sleep Duration |
|-------------|----------------|
| Simple (1-2 lines) | 1.5s |
| Standard (3-10 lines) | 2.5s |
| Complex (10+ lines) | 3.5s |
| Needs reading | 4s |
| Error message | 2s |
| Transition | 1s |

## Settings Reference

| Setting | Default | Purpose |
|---------|---------|---------|
| `Shell` | "zsh" | Shell to use |
| `FontSize` | 18 | Readable in docs |
| `Width` | 900 | Wide for output |
| `Height` | 550 | Tall for multiple lines |
| `Theme` | "Dracula" | Good contrast |
| `TypingSpeed` | 40ms | Natural pace |
| `Padding` | 15 | Clean borders |

## Optimization Workflow

```bash
# 1. Generate GIF
cd docs/demos
vhs feature.tape

# 2. Check size
ls -lh feature.gif

# 3. Optimize (if > 300KB)
gifsicle -O3 --lossy=80 feature.gif -o feature-opt.gif
mv feature-opt.gif feature.gif

# 4. Verify quality
open feature.gif
```

## Common Issues

### GIF too large (> 500KB)

Solutions:
1. Reduce duration (fewer commands)
2. Use `--lossy=100` (more compression)
3. Reduce dimensions (Width 800, Height 450)
4. Shorter Sleep times

### Text hard to read

Solutions:
1. Increase FontSize to 20
2. Use high-contrast theme
3. Increase Width for long output
4. Add Padding

### Commands cut off

Solutions:
1. Increase Width to 1000
2. Use `Hide` before long commands
3. Split into multiple demos

## CI Integration

The agent knows how to integrate with GitHub Actions:

```yaml
# .github/workflows/demos.yml
- name: Generate GIFs
  run: |
    for tape in docs/demos/*.tape; do
      vhs "$tape"
    done

- name: Optimize GIFs
  run: |
    for gif in docs/demos/*.gif; do
      gifsicle -O3 --lossy=80 "$gif" -o "${gif%.gif}-opt.gif"
      mv "${gif%.gif}-opt.gif" "$gif"
    done
```

## Usage in Commands

This agent is invoked by:
- `/craft:docs:demo` - Main VHS tape generator
- `/craft:docs:guide` - When generating demo as part of guide

## Related

- VHS docs: https://github.com/charmbracelet/vhs
- gifsicle docs: https://www.lcdf.org/gifsicle/
- aiterm demos: `docs/demos/README.md`
