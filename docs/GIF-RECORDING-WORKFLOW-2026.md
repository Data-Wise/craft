# GIF Recording Workflow 2026

**Standard tools for capturing Claude Code CLI sessions**

---

## Default Method: asciinema + agg

**Why this is the standard for Craft commands:**

- Records REAL Claude Code output (not simulated)
- Works for both bash commands AND plugin commands
- Captures actual formatting, colors, timing
- Easy to re-record if output changes
- High-quality GIF conversion with gifski

**Alternative:** VHS for scripted/repeatable demos (`/craft:docs:demo --method vhs`)

---

## Setup

```bash
# Install asciinema (terminal recorder)
brew install asciinema

# Install agg (asciinema → GIF converter)
cargo install --git https://github.com/asciinema/agg

# Or download prebuilt binary
curl -LO https://github.com/asciinema/agg/releases/latest/download/agg-$(uname -m)-apple-darwin
chmod +x agg-$(uname -m)-apple-darwin
mv agg-$(uname -m)-apple-darwin /usr/local/bin/agg

# Verify installation
asciinema --version
agg --version

# Keep gifsicle for final optimization
brew install gifsicle
```

---

## Workflow: Record → Convert → Optimize

### Step 1: Record Claude Code Session

```bash
# Start recording
asciinema rec teaching-workflow.cast

# Now run your /craft commands in Claude Code:
/craft:git:status
/craft:site:build
/craft:site:progress
# ... etc

# Stop recording (Ctrl+D or exit)
exit
```

**Recording captured to:** `teaching-workflow.cast`

### Step 2: Convert to GIF

```bash
# Basic conversion
agg teaching-workflow.cast teaching-workflow.gif

# With customization
agg \
  --cols 100 \
  --rows 30 \
  --font-size 16 \
  --theme dracula \
  --fps 10 \
  teaching-workflow.cast teaching-workflow.gif
```

### Step 3: Optimize GIF

```bash
# Optimize with gifsicle
gifsicle -O3 --colors 128 --lossy=80 teaching-workflow.gif -o teaching-workflow.gif

# Check size
ls -lh teaching-workflow.gif
```

---

## Advanced Options

### agg Customization

```bash
# Terminal dimensions
--cols 100        # Width (default: 80)
--rows 30         # Height (default: 24)

# Appearance
--font-size 16    # Font size (default: 14)
--theme dracula   # Theme (monokai, solarized-dark, etc.)
--line-height 1.4 # Line spacing

# Performance
--fps 10          # Frames per second (default: 20)
--speed 1.5       # Playback speed (1.0 = normal)

# Quality
--quality 100     # GIF quality (1-100, default: 100)
```

### Edit Recording Before Converting

```bash
# Play recording to check it
asciinema play teaching-workflow.cast

# Trim beginning/end
# Edit the .cast file (it's JSON)
# Or use asciinema upload → edit on web → download
```

---

## Complete Example: Teaching Workflow GIF

```bash
# 1. Record actual Claude Code session
asciinema rec docs/demos/teaching-workflow.cast

# In Claude Code, run:
# /craft:git:status
# /craft:site:build
# /craft:site:progress
# /craft:site:publish --dry-run
# /craft:site:publish
# Ctrl+D to stop

# 2. Preview the recording
asciinema play docs/demos/teaching-workflow.cast

# 3. Convert to GIF (optimized settings)
agg \
  --cols 100 \
  --rows 30 \
  --font-size 14 \
  --theme dracula \
  --fps 10 \
  docs/demos/teaching-workflow.cast \
  docs/demos/teaching-workflow.gif

# 4. Optimize
gifsicle -O3 --colors 128 --lossy=80 \
  docs/demos/teaching-workflow.gif \
  -o docs/demos/teaching-workflow.gif

# 5. Check size (should be < 2MB)
ls -lh docs/demos/teaching-workflow.gif
```

---

## Batch Recording Script

```bash
#!/bin/bash
# record-all-workflows.sh

DEMOS=(
    "teaching-workflow:/craft:git:status /craft:site:build /craft:site:progress"
    "workflow-01:/craft:docs:update"
    "workflow-02:/craft:site:create --preset adhd-focus --quick"
    # ... etc
)

for demo in "${DEMOS[@]}"; do
    IFS=':' read -r name commands <<< "$demo"

    echo "📹 Recording: $name"
    echo "Commands to run:"
    echo "$commands"
    echo ""
    echo "Press Enter when ready to start recording..."
    read

    asciinema rec "docs/demos/$name.cast"

    echo "✅ Recorded: $name.cast"
    echo ""
done

echo "🎬 Converting all recordings to GIF..."
for cast in docs/demos/*.cast; do
    gif="${cast%.cast}.gif"
    echo "Converting: $(basename $cast)"

    agg --cols 100 --rows 30 --font-size 14 --theme dracula --fps 10 \
        "$cast" "$gif"

    gifsicle -O3 --colors 128 --lossy=80 "$gif" -o "$gif"

    echo "✅ $(basename $gif) ($(ls -lh $gif | awk '{print $5}'))"
done
```

---

## VHS vs asciinema Comparison

| Feature | VHS | asciinema + agg |
|---------|-----|-----------------|
| **Recording** | Scripted (Type commands) | Real terminal session |
| **Accuracy** | Must manually match output | Captures exact output |
| **Editing** | Edit .tape file | Edit .cast JSON |
| **Quality** | Very good | Excellent (gifski) |
| **Automation** | Excellent (CI/CD) | Good (requires real session) |
| **Use Case** | Repeatable, scriptable demos | One-time accurate captures |

**Recommendation:**

- Use **asciinema + agg** for Craft plugin commands (need real output)
- Use **VHS** for pure CLI tools (can script Type commands)

---

## Troubleshooting

### GIF is too large

```bash
# Reduce FPS
agg --fps 8 input.cast output.gif

# Reduce colors during optimization
gifsicle -O3 --colors 64 --lossy=100 input.gif -o input.gif

# Reduce terminal size
agg --cols 80 --rows 24 input.cast output.gif
```

### Text is blurry

```bash
# Increase font size
agg --font-size 16 input.cast output.gif

# Use less aggressive optimization
gifsicle -O3 --colors 256 --lossy=60 input.gif -o input.gif
```

### Recording has mistakes

```bash
# Play recording to find timestamp
asciinema play recording.cast

# Upload to asciinema.org → edit → download
asciinema upload recording.cast
# Edit on web interface
# Download edited version
```

---

## Sources

- [asciinema documentation](https://docs.asciinema.org/)
- [agg - asciinema gif generator](https://docs.asciinema.org/manual/agg/)
- [GitHub: asciinema/agg](https://github.com/asciinema/agg)
- [awesome-terminal-recorder](https://github.com/orangekame3/awesome-terminal-recorder)
- [VHS documentation](https://github.com/charmbracelet/vhs)

---

**Last Updated**: 2026-01-17
**Recommended Stack**: asciinema + agg + gifsicle
