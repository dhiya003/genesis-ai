# Repository Structure

Version: 0.1.0
Sprint: 1D

```text
.github/workflows/       CI pipelines
api/                     OpenAPI contracts
architecture/            Mermaid and C4 diagrams
database/migrations/     PostgreSQL migrations
database/seeds/          Seed data
docs/                    Engineering docs and sprint notes
ops/                     Operating guides and local setup
prompts/                 AI workforce prompt library
schemas/                 JSON schemas
tests/fixtures/          Sample validation fixtures
```

## Naming conventions

- Markdown docs use kebab-case.
- JSON schemas use `<domain>.schema.json`.
- Migrations use `NNNN_description.sql`.
- Prompt files use employee or agent names in kebab-case.

## Traceability

Each artifact must map to a sprint deliverable and be referenced from README or sprint documentation.
