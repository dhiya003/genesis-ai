# Database

Version: 0.1.0
Sprint: 1D

## Purpose

This folder stores the PostgreSQL data model for Genesis AI.

## Migration structure

```text
database/migrations/0001_initial_schema.sql
database/migrations/0002_epic_01_founder_business_management.sql
database/seeds/0001_seed_ai_workforce.sql
```

## Naming conventions

- Tables use plural snake_case names.
- Primary keys use `id`.
- Foreign keys use `<table_singular>_id`.
- Timestamps use `created_at`, `updated_at`, `started_at`, `completed_at`.
- Status fields use explicit `CHECK` constraints.
- JSON payloads use `JSONB`.

## Index strategy

Indexes are added for:

- project status lookup
- workflow project lookup
- workflow state lookup
- report lookup by project
- business idempotency lookup by founder and idempotency key

## Constraints

- Status values are constrained.
- Priority values are constrained between 1 and 5.
- Employees have explicit authority levels.
- Child records cascade when projects are deleted.
- Epic 01 business context stores founder profile, business vision, goals, constraints, budget, success metrics, and approval policies.
