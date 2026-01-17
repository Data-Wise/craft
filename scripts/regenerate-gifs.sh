#!/bin/bash
# GIF Regeneration Script
# Regenerates all workflow GIFs using VHS and optimizes with gifsicle

set -e  # Exit on error

echo "🎬 Craft GIF Regeneration Script"
echo "================================="
echo ""

# Check dependencies
echo "Checking dependencies..."
command -v vhs >/dev/null 2>&1 || { echo "❌ VHS not installed. Run: brew install charmbracelet/tap/vhs"; exit 1; }
command -v gifsicle >/dev/null 2>&1 || { echo "❌ gifsicle not installed. Run: brew install gifsicle"; exit 1; }
echo "✅ VHS and gifsicle are installed"
echo ""

# Configuration
DEMOS_DIR="docs/demos"
GIFS_DIR="docs/gifs"
BACKUP_DIR=".gif-backups-$(date +%Y%m%d-%H%M%S)"

# Function to regenerate a single GIF
regenerate_gif() {
    local tape_file="$1"
    local gif_file="${tape_file%.tape}.gif"
    local dir=$(dirname "$tape_file")
    local name=$(basename "$tape_file" .tape)

    echo "🎬 Generating: $name"
    echo "   Tape: $tape_file"

    # Generate with VHS
    cd "$dir" && vhs "$(basename "$tape_file")" && cd - > /dev/null

    if [ ! -f "$gif_file" ]; then
        echo "   ❌ Failed to generate GIF"
        return 1
    fi

    # Get original size
    local original_size=$(ls -lh "$gif_file" | awk '{print $5}')
    echo "   Generated: $original_size"

    # Optimize with gifsicle
    gifsicle -O3 --colors 128 --lossy=80 "$gif_file" -o "$gif_file"

    # Get optimized size
    local optimized_size=$(ls -lh "$gif_file" | awk '{print $5}')
    echo "   Optimized: $optimized_size"

    # Verify size is under 2MB
    local size_bytes=$(stat -f%z "$gif_file" 2>/dev/null || stat -c%s "$gif_file" 2>/dev/null)
    local size_mb=$(echo "scale=2; $size_bytes / 1048576" | bc)

    if (( $(echo "$size_mb > 2.0" | bc -l) )); then
        echo "   ⚠️  WARNING: GIF exceeds 2MB limit ($size_mb MB)"
        echo "   Consider reducing colors or resolution"
    else
        echo "   ✅ Size OK: $size_mb MB"
    fi

    echo ""
}

# Main execution
echo "Creating backup of existing GIFs..."
mkdir -p "$BACKUP_DIR"
cp -r "$DEMOS_DIR"/*.gif "$GIFS_DIR"/*.gif "$BACKUP_DIR/" 2>/dev/null || true
echo "✅ Backup created: $BACKUP_DIR"
echo ""

echo "Regenerating GIFs..."
echo "===================="
echo ""

# Regenerate teaching workflow
regenerate_gif "$DEMOS_DIR/teaching-workflow.tape"

# Regenerate all workflow GIFs
for i in {01..10}; do
    tape_file="$GIFS_DIR/workflow-$i-*.tape"
    if ls $tape_file 1> /dev/null 2>&1; then
        for tape in $tape_file; do
            regenerate_gif "$tape"
        done
    fi
done

echo "================================="
echo "✅ All GIFs regenerated!"
echo ""
echo "Summary:"
ls -lh "$DEMOS_DIR"/*.gif "$GIFS_DIR"/*.gif | awk '{print $9, "-", $5}'
echo ""
echo "Backup location: $BACKUP_DIR"
echo ""
echo "Next steps:"
echo "1. Review GIFs for readability"
echo "2. Verify output matches actual command behavior"
echo "3. Delete backup if satisfied: rm -rf $BACKUP_DIR"
