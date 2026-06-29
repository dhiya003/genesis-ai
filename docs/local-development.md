# Local Development Guide

## Prerequisites

- Git
- Docker Desktop
- Node.js LTS (for future app work)

## Clone

```bash
git clone https://github.com/dhiya003/genesis-ai.git
cd genesis-ai
```

## Environment

Copy the environment template:

```bash
cp .env.example .env
```

Do not commit real secrets.

## Start local services

```bash
docker compose -f infrastructure/docker-compose.yml up -d
```

This starts:

- PostgreSQL on port `5432`
- Adminer at `http://localhost:8080`

## Database schema

The schema is mounted into the PostgreSQL container on first database initialization from:

```text
database/schema.sql
```

## Seed data

Seed files are stored in:

```text
database/seeds/001_departments.sql
database/seeds/002_employees.sql
```

Apply them in order when initializing development data.

## Validation

Run CI-equivalent checks locally:

```bash
python -m json.tool testing/prompt-regression/research-trend-cases.json
python -m json.tool testing/fixtures/sample-project.json
python -m json.tool testing/fixtures/sample-trend-report.json
```

## Sprint 2 readiness

Sprint 2 begins when:

- Docker database starts
- Schema applies
- Seed data loads
- Prompt files are available
- Sample fixtures are available
- Research report schema is ready
