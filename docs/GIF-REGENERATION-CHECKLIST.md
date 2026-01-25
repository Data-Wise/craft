# GIF Regeneration Checklist - asciinema Method

**Total GIFs to regenerate:** 11

## Prerequisites

- [x] gifsicle installed ✅
- [ ] asciinema installed (run: `brew install asciinema`)
- [ ] agg installed (run: `cargo install --git https://github.com/asciinema/agg`)

---

## 1. Teaching Workflow (docs/demos/teaching-workflow.gif)

**Commands:**

```
/craft:git:status
/craft:site:build
/craft:site:progress
/craft:site:publish --dry-run
/craft:site:publish
```

**Recording:**

```bash
asciinema rec docs/demos/teaching-workflow.cast
# Run commands above
# Ctrl+D to stop
agg --cols 100 --rows 30 --font-size 14 --fps 10 \
    docs/demos/teaching-workflow.cast \
    docs/demos/teaching-workflow-new.gif
gifsicle -O3 --colors 128 --lossy=80 \
    docs/demos/teaching-workflow-new.gif \
    -o docs/demos/teaching-workflow.gif
```

---

## 2. Workflow 01 (docs/gifs/workflow-01-*.gif)

**Command:** `/craft:docs:update`

**Recording:**

```bash
asciinema rec docs/gifs/workflow-01.cast
# Run: /craft:docs:update
# Ctrl+D to stop
agg --cols 100 --rows 30 --font-size 14 --fps 10 \
    docs/gifs/workflow-01.cast \
    docs/gifs/workflow-01-new.gif
gifsicle -O3 --colors 128 --lossy=80 \
    docs/gifs/workflow-01-new.gif \
    -o docs/gifs/workflow-01-docs-update.gif
```

---

## 3. Workflow 02 (docs/gifs/workflow-02-*.gif)

**Command:** `/craft:site:create --preset adhd-focus --quick`

---

## 4. Workflow 03 (docs/gifs/workflow-03-*.gif)

**Command:** `/craft:check --for release`

---

## 5. Workflow 04 (docs/gifs/workflow-04-*.gif)

**Command:** `/craft:do add user authentication with JWT`

---

## 6. Workflow 05 (docs/gifs/workflow-05-*.gif)

**Command:** `/craft:test:run debug`

---

## 7. Workflow 06 (docs/gifs/workflow-06-*.gif)

**Command:** `/craft:code:lint optimize`

---

## 8. Workflow 07 (docs/gifs/workflow-07-*.gif)

**Command:** `/craft:git:worktree add feature-auth`

---

## 9. Workflow 08 (docs/gifs/workflow-08-*.gif)

**Command:** `/craft:dist:homebrew setup`

---

## 10. Workflow 09 (docs/gifs/workflow-09-*.gif)

**Command:** `/craft:check --for commit`

---

## 11. Workflow 10 (docs/gifs/workflow-10-*.gif)

**Command:** `/craft:orchestrate 'prepare v2.0 release' release`

---

## Standard Workflow

For each GIF:

1. **Record:**

   ```bash
   asciinema rec docs/gifs/workflow-XX.cast
   ```

2. **Run command in Claude Code**
   (Wait for completion)

3. **Stop recording:**
   Press Ctrl+D

4. **Preview:**

   ```bash
   asciinema play docs/gifs/workflow-XX.cast
   ```

5. **Convert:**

   ```bash
   agg --cols 100 --rows 30 --font-size 14 --fps 10 \
       docs/gifs/workflow-XX.cast \
       docs/gifs/workflow-XX-new.gif
   ```

6. **Optimize:**

   ```bash
   gifsicle -O3 --colors 128 --lossy=80 \
       docs/gifs/workflow-XX-new.gif \
       -o docs/gifs/workflow-XX-<name>.gif
   ```

7. **Verify size:**

   ```bash
   ls -lh docs/gifs/workflow-XX-<name>.gif
   # Should be < 2MB
   ```

---

**Progress:** 0/11 completed
