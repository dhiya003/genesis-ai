# Local Development

## Prerequisites
- Docker Desktop
- Git

## Start services

```bash
docker compose -f infrastructure/docker-compose.yml up -d
```

## Database
PostgreSQL: localhost:5432

Adminer: http://localhost:8080

Load schema from:
- database/schema.sql

Seed data:
- database/seeds/001_departments.sql
- database/seeds/002_employees.sql
