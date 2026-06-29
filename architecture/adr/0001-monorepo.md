# ADR-0001: Monorepo Architecture

## Status
Accepted

## Decision
Genesis AI will use a monorepo to keep applications, prompts, documentation, database assets and infrastructure in a single versioned repository.

## Rationale
- Shared types
- Easier refactoring
- Unified versioning
- Simpler onboarding

## Consequences
Future modules will be added under apps/, packages/, infrastructure/, prompts/, database/ and docs/.
