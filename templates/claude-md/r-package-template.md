# CLAUDE.md - {package_name}

> **TL;DR**: {package_title}

**Package Type**: R package | **Minimum R**: {r_version}
**Status:** {status} | **Progress:** {progress}%

## Quick Reference

**Main Branch**: `main` | **Dev Branch**: `dev`

### Essential Commands

```r
# Development
devtools::load_all()     # Load package
devtools::document()     # Update docs (roxygen)
devtools::test()         # Run tests
devtools::check()        # R CMD check
devtools::build()        # Build package

# Documentation
pkgdown::build_site()    # Build website
pkgdown::preview_site()  # Preview locally

# Testing
testthat::test_local()   # Run all tests
covr::package_coverage() # Coverage report
```

## Package Structure

```text
{package_name}/
├── R/                   # Package functions
{r_files}
├── man/                 # Documentation (auto-generated)
├── tests/testthat/      # Unit tests
{test_files}
├── vignettes/           # Long-form documentation
{vignette_files}
├── data/                # Package data
├── DESCRIPTION          # Package metadata
├── NAMESPACE            # Exports (auto-generated)
├── _pkgdown.yml         # Website configuration
└── README.md            # Package overview
```

## Development Workflow

1. Write function in R/
2. Add roxygen docs (@param, @return, @examples)
3. Run `devtools::document()` to update man/
4. Add tests in tests/testthat/test-*.R
5. Run `devtools::test()`
6. Run `devtools::check()` before commit
7. Build website: `pkgdown::build_site()`

## Roxygen Patterns

```r
#' Function Title
#'
#' Function description.
#'
#' @param x Description of parameter x
#' @param y Description of parameter y
#' @return Description of return value
#' @export
#' @examples
#' my_function(1, 2)
my_function <- function(x, y) {
  # implementation
}
```

## Testing Workflow

```r
# Create test file
usethis::use_test("function-name")

# Write tests
test_that("function does what it should", {
  result <- my_function(1, 2)
  expect_equal(result, 3)
})

# Run tests
devtools::test()

# Check coverage
covr::package_coverage()
```

## pkgdown Configuration

Website sections:

- **Reference**: Auto-generated from roxygen
- **Articles**: From vignettes/
- **News**: From NEWS.md
- **Getting Started**: From README.md

## Dependencies

{dependencies}

## Key Functions

{function_table}

## Related Packages

{related_packages}

## Common Issues

| Issue | Fix |
|-------|-----|
| Check fails | `devtools::check()` |
| Missing docs | `devtools::document()` |
| Test errors | `devtools::test()` |

## References

-> Package site: [{package_name}]({pkgdown_url})
-> GitHub: [{package_name}]({repo_url})
-> CRAN: [{package_name}]({cran_url})
