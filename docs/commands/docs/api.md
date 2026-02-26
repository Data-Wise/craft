# /craft:docs:api

> **OpenAPI/Swagger documentation generator with auto-detection and SDK support**

---

## Synopsis

```bash
/craft:docs:api [action] [options]
```

**Quick examples:**

```bash
# Analyze project and suggest API documentation approach
/craft:docs:api

# Generate OpenAPI 3.1 spec from code
/craft:docs:api generate

# Validate an existing spec
/craft:docs:api validate

# Generate a Python client SDK
/craft:docs:api sdk python
```

---

## Description

Detects your API framework (FastAPI, Flask, Express, Hono, Gin, plumber), analyzes route definitions, and generates an OpenAPI 3.1 specification. Supports interactive documentation setup via Swagger UI or Redoc, and client SDK generation for multiple languages.

When run without arguments, it scans the project, reports detected endpoints and frameworks, and presents options. With an explicit action, it proceeds directly to generation, validation, or SDK output.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `generate` | Generate OpenAPI spec from code | - |
| `validate` | Validate an existing OpenAPI spec | - |
| `sdk <lang>` | Generate client SDK (python, typescript, go, ruby, java) | - |
| `--interactive` | Set up Swagger UI or Redoc | `false` |
| `--output PATH` | Custom output path for the spec file | `openapi.yaml` |

---

## How It Works

1. **Detect framework** — scans for FastAPI, Flask, Express, Hono, Gin, or plumber markers in project files.
2. **Generate spec** — extracts routes, parameters, response schemas, and security schemes into an OpenAPI 3.1 YAML file.
3. **Interactive docs** (optional) — offers Swagger UI, Redoc, Stoplight Elements, or RapiDoc setup.
4. **Validate** — runs Spectral linting, reports errors and warnings, offers to fix issues.
5. **SDK generation** (optional) — uses openapi-generator-cli to produce typed clients in the target language.

### Supported Frameworks

| Framework | Language | Auto-detect |
|-----------|----------|-------------|
| FastAPI | Python | Built-in OpenAPI |
| Flask | Python | Via flask-smorest |
| Express | Node.js | Via swagger-jsdoc |
| Hono | Node.js | Via @hono/swagger |
| Gin | Go | Via swaggo |
| plumber | R | Via annotations |

---

## See Also

- [/craft:docs:check](check.md) — Documentation health check
- [/craft:docs:update](update.md) — Update documentation
- [/craft:docs:sync](sync.md) — Smart documentation detection
