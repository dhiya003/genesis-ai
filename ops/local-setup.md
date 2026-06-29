# Local Setup Guide

Version: 0.1.0
Sprint: 1D

## Prerequisites

- Git
- Docker Desktop or Docker Engine
- PostgreSQL client tools optional

## Setup

```bash
git clone https://github.com/dhiya003/genesis-ai.git
cd genesis-ai
cp .env.example .env
docker compose up -d
```

## Database initialization

```bash
psql "$DATABASE_URL" -f database/migrations/0001_initial_schema.sql
psql "$DATABASE_URL" -f database/seeds/0001_seed_ai_workforce.sql
```

## Health check

```bash
docker compose ps
pg_isready -h localhost -p 5432 -U genesis -d genesis
```

## Sprint 1D validation checklist

- Repository clones successfully.
- Docker Compose starts without errors.
- Database schema applies successfully.
- Seed scripts execute successfully.
- JSON schemas are syntactically valid.
- Mermaid diagrams render correctly.
- OpenAPI specification validates.
- CI pipeline passes.
