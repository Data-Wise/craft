---
name: openapi-spec-generation
description: Generate and maintain OpenAPI 3.1 specifications from code, design-first specs, and validation patterns. Use when creating API documentation, generating SDKs, or ensuring API contract compliance.
---

# OpenAPI Spec Generation

Comprehensive patterns for creating, maintaining, and validating OpenAPI 3.1 specifications for RESTful APIs.

## When to Use This Skill

- Creating API documentation from scratch
- Generating OpenAPI specs from existing code
- Designing API contracts (design-first approach)
- Validating API implementations against specs
- Generating client SDKs from specs
- Setting up API documentation portals

## Core Concepts

### 1. OpenAPI 3.1 Structure

```yaml
openapi: 3.1.0
info:
  title: API Title
  version: 1.0.0
servers:
  - url: https://api.example.com/v1
paths:
  /resources:
    get: ...
components:
  schemas: ...
  securitySchemes: ...
```

### 2. Design Approaches

| Approach | Description | Best For |
|----------|-------------|----------|
| **Design-First** | Write spec before code | New APIs, contracts |
| **Code-First** | Generate spec from code | Existing APIs |
| **Hybrid** | Annotate code, generate spec | Evolving APIs |

## Templates

### Template 1: Complete API Specification

Full YAML spec for a User Management API with paths, components, schemas, parameters, responses, examples, and security schemes.

See [references/complete-api-spec-template.md](references/complete-api-spec-template.md).

### Template 2 & 3: Code-First Generation

Annotated code examples for FastAPI (Python) and tsoa (TypeScript/Express) that auto-generate OpenAPI specs from type annotations and decorators.

See [references/code-first-generation.md](references/code-first-generation.md).

### Template 4: Validation & Linting

```bash
# Install validation tools
npm install -g @stoplight/spectral-cli
npm install -g @redocly/cli

# Spectral ruleset (.spectral.yaml)
cat > .spectral.yaml << 'EOF'
extends: ["spectral:oas", "spectral:asyncapi"]

rules:
  # Enforce operation IDs
  operation-operationId: error

  # Require descriptions
  operation-description: warn
  info-description: error

  # Naming conventions
  operation-operationId-valid-in-url: true

  # Security
  operation-security-defined: error

  # Response codes
  operation-success-response: error

  # Custom rules
  path-params-snake-case:
    description: Path parameters should be snake_case
    severity: warn
    given: "$.paths[*].parameters[?(@.in == 'path')].name"
    then:
      function: pattern
      functionOptions:
        match: "^[a-z][a-z0-9_]*$"

  schema-properties-camelCase:
    description: Schema properties should be camelCase
    severity: warn
    given: "$.components.schemas[*].properties[*]~"
    then:
      function: casing
      functionOptions:
        type: camel
EOF

# Run Spectral
spectral lint openapi.yaml

# Redocly config (redocly.yaml)
cat > redocly.yaml << 'EOF'
extends:
  - recommended

rules:
  no-invalid-media-type-examples: error
  no-invalid-schema-examples: error
  operation-4xx-response: warn
  request-mime-type:
    severity: error
    allowedValues:
      - application/json
  response-mime-type:
    severity: error
    allowedValues:
      - application/json
      - application/problem+json

theme:
  openapi:
    generateCodeSamples:
      languages:
        - lang: curl
        - lang: python
        - lang: javascript
EOF

# Run Redocly
redocly lint openapi.yaml
redocly bundle openapi.yaml -o bundled.yaml
redocly preview-docs openapi.yaml
```

## SDK Generation

```bash
# OpenAPI Generator
npm install -g @openapitools/openapi-generator-cli

# Generate TypeScript client
openapi-generator-cli generate \
  -i openapi.yaml \
  -g typescript-fetch \
  -o ./generated/typescript-client \
  --additional-properties=supportsES6=true,npmName=@myorg/api-client

# Generate Python client
openapi-generator-cli generate \
  -i openapi.yaml \
  -g python \
  -o ./generated/python-client \
  --additional-properties=packageName=api_client

# Generate Go client
openapi-generator-cli generate \
  -i openapi.yaml \
  -g go \
  -o ./generated/go-client
```

## Best Practices

### Do's

- **Use $ref** - Reuse schemas, parameters, responses
- **Add examples** - Real-world values help consumers
- **Document errors** - All possible error codes
- **Version your API** - In URL or header
- **Use semantic versioning** - For spec changes

### Don'ts

- **Don't use generic descriptions** - Be specific
- **Don't skip security** - Define all schemes
- **Don't forget nullable** - Be explicit about null
- **Don't mix styles** - Consistent naming throughout
- **Don't hardcode URLs** - Use server variables

## Resources

- [OpenAPI 3.1 Specification](https://spec.openapis.org/oas/v3.1.0)
- [Swagger Editor](https://editor.swagger.io/)
- [Redocly](https://redocly.com/)
- [Spectral](https://stoplight.io/open-source/spectral)
