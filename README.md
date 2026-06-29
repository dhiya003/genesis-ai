# Genesis AI

Genesis AI is the founder/CEO intelligence layer for building the AI Product Factory first, then scaling into a full Business OS.

## Current build direction

1. Finish AI Product Factory first.
2. Keep Phase 1 lean and executable without paid infrastructure.
3. Add Supabase, Meta API, VPS, Cloudflare, and deeper automation in Phase 2.
4. Store decisions, prompts, workflows, and sprint assets in GitHub.

## Sprint 1D status

Sprint 1D is complete against the Engineering Design Pack baseline.

Committed foundation assets include:

- CEO AI answer-source model
- CEO AI system prompt
- AI Product Factory agent prompt
- Genesis Orchestrator prompt
- Research employee prompts EMP-001 to EMP-004
- PostgreSQL/Supabase-ready database schema
- Database seed data
- Migration structure
- ER diagram
- OpenAPI contract
- JSON schemas for research, product, creative, marketing, publishing, analytics, and errors
- Architecture diagrams
- Sequence diagrams
- State machines
- Docker Compose local environment
- CI validation workflow
- Prompt regression dataset
- Sample fixtures
- Local development guide
- Sprint 2 kickoff plan

## Repo structure

```text
api/
  openapi.yaml
  schemas/
architecture/
  sequences/
  state-machines/
database/
  migrations/
  seeds/
docs/
  adr/
implementation/
infrastructure/
prompts/
  orchestrator/
  research/
testing/
  fixtures/
  prompt-regression/
```

## Operating principle

Genesis AI should not guess business truth. It answers from:

1. Approved Genesis strategy and project memory
2. GitHub repository assets
3. Connected tools and live business data
4. Model reasoning, clearly marked as recommendation when no source exists
