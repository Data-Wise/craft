# Teaching Workflow Demo - Optimized
# Generate: vhs teaching-workflow.tape

Output docs/demos/teaching-workflow.gif

Set FontSize 12
Set Width 900
Set Height 500
Set Padding 10
Set Theme "Dracula"

# Title
Type "# Teaching Workflow Demo"
Sleep 1s
Enter
Enter

# Step 1
Type "$ /craft:git:status"
Enter
Sleep 300ms
Type "Branch: dev (Preview) | Students see: Week 7 (main)"
Enter
Type "✅ Safe to experiment"
Sleep 1.5s
Enter
Enter

# Step 2
Type "$ /folio:site:build"
Enter
Sleep 300ms
Type "Course: STAT 545 Fall 2024 | Week 8/15 (53%)"
Enter
Type "✓ Built successfully"
Sleep 1.5s
Enter
Enter

# Step 3
Type "$ /folio:site:progress"
Enter
Sleep 300ms
Type "████████░░░░░░░ 8/15 weeks (53%)"
Enter
Type "Weeks 1-7: ✅  Week 8: 🔄  Weeks 9-15: 📝"
Sleep 1.5s
Enter
Enter

# Step 4
Type "$ /folio:site:publish --dry-run"
Enter
Sleep 300ms
Type "✓ Schedule validated | ✓ Syllabus complete"
Enter
Type "✅ SAFE TO PUBLISH"
Sleep 1.5s
Enter
Enter

# Step 5
Type "$ /folio:site:publish"
Enter
Sleep 300ms
Type "✓ Switch to main | ✓ Build | ✓ Deploy"
Enter
Type "🎉 Week 8 published!"
Sleep 2s
Enter
Enter

# Done
Type "⏱  3 min (was 15 min manually) | 🎯 80% faster"
Sleep 2s
