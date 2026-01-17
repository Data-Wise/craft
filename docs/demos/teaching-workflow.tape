# VHS tape for teaching workflow demonstration
# Generate GIF: vhs teaching-workflow.tape

Output docs/demos/teaching-workflow.gif

Set FontSize 14
Set Width 1200
Set Height 700
Set Padding 20
Set Theme "Catppuccin Mocha"

Type "# Teaching Workflow Demo"
Sleep 1s
Enter

Type "# Step 1: Check teaching mode status"
Sleep 500ms
Enter
Type "/craft:git:status"
Sleep 500ms
Enter
Sleep 3s

Type ""
Enter
Type "# Step 2: Preview changes on dev branch"
Sleep 500ms
Enter
Type "/craft:site:build"
Sleep 500ms
Enter
Sleep 4s

Type ""
Enter
Type "# Step 3: Check semester progress"
Sleep 500ms
Enter
Type "/craft:site:progress"
Sleep 500ms
Enter
Sleep 4s

Type ""
Enter
Type "# Step 4: Validate before publishing"
Sleep 500ms
Enter
Type "/craft:site:publish --dry-run --validate-only"
Sleep 500ms
Enter
Sleep 5s

Type ""
Enter
Type "# Step 5: Publish to production (if validation passed)"
Sleep 500ms
Enter
Type "/craft:site:publish"
Sleep 500ms
Enter
Sleep 6s

Type ""
Enter
Type "# Done! Site published, auto-switched back to dev"
Sleep 2s
