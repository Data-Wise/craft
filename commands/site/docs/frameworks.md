# Documentation Framework Comparison

Choosing between MkDocs, Quarto, and pkgdown for your project.

## Quick Decision Guide

**R Package?**
→ pkgdown (standard) or Quarto (modern alternative)

**Python/Node/DevTools?**
→ MkDocs (recommended)

**Academic/Research?**
→ Quarto (supports R, Python, Julia)

**Need speed?**
→ MkDocs (fastest setup)

---

## Framework Comparison

| Feature | MkDocs | Quarto | pkgdown |
|---------|--------|--------|---------|
| **Best for** | Dev tools, Python, Node | Research, multi-language | R packages |
| **Setup time** | 2 minutes | 5 minutes | 3 minutes |
| **Language** | Python | R/Python/Julia | R only |
| **Theme** | Material (beautiful) | Bootstrap | Bootstrap |
| **Code execution** | No | Yes (R, Python) | Yes (R vignettes) |
| **GitHub Pages** | Easy | Easy | Built-in |
| **Learning curve** | Low | Medium | Low |
| **Flexibility** | High | Very high | Medium |

---

## MkDocs

**What it is:**
- Python-based static site generator
- Material theme (beautiful, modern)
- Fast and simple

**Pros:**
✅ Fastest setup (2 minutes)
✅ Beautiful Material theme
✅ Great navigation
✅ Works with any project type
✅ Easy to deploy
✅ Extensive plugin ecosystem

**Cons:**
❌ Doesn't execute code
❌ Requires Python
❌ Not standard for R packages

**Best for:**
- Dev tools
- Python packages
- Node.js projects
- Quick documentation needs

**Setup:**
```bash
/site:mkdocs:init        # Quick setup
/site:mkdocs:preview     # Preview
/site:deploy             # Deploy
```

**Commands:**
- `/site:mkdocs:init` - Initialize MkDocs
- `/site:mkdocs:preview` - Quick preview
- `/site:mkdocs:status` - Check status

---

## Quarto

**What it is:**
- Next-generation scientific publishing
- Supports R, Python, Julia
- Can execute code in documents

**Pros:**
✅ Executes R/Python/Julia code
✅ Scientific publishing features
✅ Beautiful output
✅ Multi-language support
✅ Active development (from RStudio)
✅ Great for reproducible research

**Cons:**
❌ Slower than MkDocs
❌ More complex configuration
❌ Larger learning curve
❌ Overkill for simple docs

**Best for:**
- Research projects
- Academic papers
- Data science portfolios
- Multi-language projects
- When you need code execution

**Setup:**
```bash
# Create _quarto.yml manually
/site:init              # Detects Quarto
/site:preview           # Preview
/site:deploy            # Deploy
```

**Manual init example:**
```yaml
project:
  type: website
  output-dir: _site

website:
  title: "My Project"
  navbar:
    left:
      - href: index.qmd
        text: Home
```

---

## pkgdown

**What it is:**
- R package documentation builder
- Standard for R packages
- Automatically generates from R code

**Pros:**
✅ Standard for R packages
✅ Auto-generates from R docs
✅ R community standard
✅ Vignette integration
✅ Function reference auto-generated

**Cons:**
❌ R packages only
❌ Less flexible than others
❌ Bootstrap theme (older style)
❌ Requires R environment

**Best for:**
- R packages (obvious choice)
- When you want R standard approach

**Setup:**
```r
# In R console
usethis::use_pkgdown()
pkgdown::build_site()
```

**Commands:**
- Use `/site:init` (detects R package)
- Or use R directly

---

## Feature Comparison

### Code Execution

**MkDocs:** ❌ No
- Markdown only
- Show code examples, but don't run them

**Quarto:** ✅ Yes
- Execute R, Python, Julia
- Show code + output
- Reproducible documents

**pkgdown:** ✅ Yes (R only)
- Vignettes executed
- Examples run and tested

### Themes

**MkDocs:**
- Material theme (modern, beautiful)
- Highly customizable
- Mobile-responsive

**Quarto:**
- Multiple themes available
- Scientific paper layouts
- Customizable CSS

**pkgdown:**
- Bootstrap theme
- R package standard look
- Limited customization

### Deployment

**All three:** Easy GitHub Pages deployment

**MkDocs:**
```bash
/site:deploy            # Automated
```

**Quarto:**
```bash
/site:deploy            # Automated
```

**pkgdown:**
```r
pkgdown::build_site()
# Then push _site/ to gh-pages
```

---

## Migration Between Frameworks

### MkDocs → Quarto
- Rename `docs/` → `*.qmd` files
- Create `_quarto.yml`
- Add code chunks if needed

### Quarto → MkDocs
- Convert `*.qmd` → `*.md`
- Remove code execution chunks
- Create `mkdocs.yml`

### pkgdown → Quarto
- Keep R package structure
- Add `_quarto.yml`
- Convert vignettes to Quarto
- Use `altdoc` package for integration

---

## Recommendations by Project Type

### R Package
**1st choice:** pkgdown
- Standard, expected by R users
- Auto-generates from R docs
- `/site:init` detects automatically

**Alternative:** Quarto + altdoc
- Modern approach
- More flexibility
- Good for research-heavy packages

### Python Package
**1st choice:** MkDocs
- Python ecosystem standard
- Beautiful Material theme
- `/site:mkdocs:init` for quick setup

### Node.js / Dev Tools
**1st choice:** MkDocs
- Fast setup
- Great for developer tools
- `/site:mkdocs:init`

### Research / Academic
**1st choice:** Quarto
- Code execution
- Scientific publishing
- Multi-language support

### Multi-Language Project (R + Python)
**1st choice:** Quarto
- Supports both
- Unified documentation
- Reproducible

---

## Our Command Structure

**Generic (auto-detect):**
```bash
/site:init         # Detects best framework
/site:preview      # Preview any framework
/site:deploy       # Deploy any framework
```

**MkDocs-specific (fast, no questions):**
```bash
/site:mkdocs:init      # Force MkDocs
/site:mkdocs:preview   # Quick preview
/site:mkdocs:status    # Status check
```

**Why both?**
- Generic commands: Flexibility, auto-detection
- MkDocs commands: Speed, opinionated (ADHD-friendly)

---

## Decision Matrix

**Choose MkDocs if:**
- ✅ You want fast setup
- ✅ It's a dev tool or Python/Node project
- ✅ You don't need code execution
- ✅ You want beautiful docs quickly

**Choose Quarto if:**
- ✅ You need to execute code
- ✅ It's research or academic
- ✅ You work with R, Python, or Julia
- ✅ You want reproducible documents

**Choose pkgdown if:**
- ✅ It's an R package
- ✅ You want the standard approach
- ✅ You want auto-generated docs from R code
- ✅ You're targeting R users

---

## Get Started

**Not sure?**
```bash
/site:init              # Let it auto-detect
```

**Want MkDocs (fast)?**
```bash
/site:mkdocs:init       # Quick setup
```

**Need help deciding?**
```bash
/hub                    # Context-aware suggestions
```

---

**See also:**
- `/site` - Site command hub
- `/site:init` - Initialize site (auto-detect)
- `/site:mkdocs:init` - Quick MkDocs setup
- `/help workflows` - Documentation workflows
