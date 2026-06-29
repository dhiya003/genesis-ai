# Genesis AI Master Context

Version: Sprint 2 Context
Project: Genesis AI - Autonomous Business Operating System

This document is the senior-engineer and Codex onboarding brief for Genesis AI. It captures the product vision, architecture, engineering standards, current progress, and expected development workflow. Treat this as the authoritative project brief unless superseded by the repository itself.

## 1. Vision

Genesis is not a chatbot.

Genesis is an AI Business Operating System that behaves like an entire company.

Instead of one AI answering questions, Genesis consists of departments and employees that collaborate to build businesses.

Example founder request:

```text
Build a INR 1 lakh/month educational toy business in India.
```

Genesis should autonomously:

```text
Research
  -> Design Products
  -> Create Brand
  -> Generate Packaging
  -> Create Marketing
  -> Publish Products
  -> Monitor Sales
  -> Improve Business
```

## 2. Philosophy

Everything is built like a real company.

```text
CEO
  -> Departments
  -> Managers
  -> Employees
  -> Tasks
  -> Deliverables
```

Not prompts. Not agents. Actual virtual employees.

## 3. Product Goal

The founder provides one goal.

Genesis builds the business.

The founder only approves strategic decisions. Everything else should be autonomous.

## 4. Roadmap

### Sprint 1

- Foundation
- Architecture
- CI
- Database
- Repository
- Validation

### Sprint 2

- Research Department
- Workflow Engine
- Runtime
- Orchestrator
- Live Research

### Sprint 3

- Product Factory

### Sprint 4

- Creative Studio

### Sprint 5

- Marketing

### Sprint 6

- Publishing

### Sprint 7

- Business Intelligence

### Sprint 8

- Autonomous BusinessOS

## 5. Current Sprint Status

Sprint 1: Completed.

Sprint 2: Approximately 85% complete.

Completed:

- Runtime
- Workflow Engine
- Orchestrator
- Research Department
- EMP001-004
- REST API
- Persistence
- Research Reports
- Live Web Research
- Marketplace Search
- Confidence Engine
- Citation Engine
- Search Cache
- Parallel Employee Execution

Remaining:

- Official marketplace APIs
- Observability
- Workflow Recovery
- Approval Workflow
- Production Hardening

## 6. Architecture

```text
Founder
  -> REST API
  -> Genesis Runtime
  -> Workflow Engine
  -> Genesis Orchestrator
  -> Department
  -> Employees
  -> Deliverables
  -> Database
```

## 7. Departments

- Research
- Product
- Creative
- Marketing
- Publishing
- Analytics
- Finance
- Inventory
- CRM
- Operations
- Legal
- Customer Support

## 8. Research Department

Employees:

- EMP001: Trend Research
- EMP002: Competitor Research
- EMP003: Customer Research
- EMP004: Product Research

Each employee produces:

- JSON
- Score
- Evidence
- Confidence
- Sources
- Report Section

## 9. Future Departments

### Product

- BOM
- Manufacturing
- Costing
- Pricing

### Creative

- Logo
- Brand
- Packaging
- Mockups

### Marketing

- Instagram
- Facebook
- Google Ads
- Email

### Publishing

- Amazon
- Shopify
- WhatsApp
- Instagram
- Facebook

## 10. Coding Principles

- Python
- Clean Architecture
- SOLID
- Repository Pattern
- Dependency Injection
- Strong Typing
- Async First
- Domain Driven Design
- High Test Coverage
- No Technical Debt

## 11. Engineering Rules

Every feature must have:

- Unit Tests
- Integration Tests
- E2E Tests
- Logging
- Validation
- Documentation
- CI

Every commit must leave main green.

## 12. Definition of Done

- Feature implemented
- Tests pass
- CI green
- Documentation updated
- Engineering Handbook updated
- Committed

## 13. Repository Standards

- No TODO code.
- No commented code.
- No duplicated code.
- No dead code.
- No hardcoded secrets.
- Typed code only.

## 14. Runtime

```text
Workflow Engine
  -> Task Queue
  -> Department Runtime
  -> Employee Runtime
  -> Outputs
  -> Persistence
```

## 15. Research Providers

Current:

- Deterministic
- Live Web
- Marketplace
- OpenAI

Future:

- Amazon API
- Instagram Graph API
- Google Trends
- Shopify
- Meta

## 16. Engineering Goal

Genesis should eventually execute:

```text
Founder Idea
  -> Research
  -> Product
  -> Brand
  -> Marketing
  -> Publishing
  -> Analytics
  -> Optimization
```

without human intervention.

## 17. Deliverables

Every sprint produces:

- Working code
- Tests
- CI
- Documentation
- Git commits

No placeholders.

## 18. Coding Workflow

```text
Implement
  -> Test
  -> Commit
  -> CI
  -> Review
  -> Next Task
```

## 19. AI Coding Rules For Codex

Codex should:

- Never rewrite completed modules without reason.
- Always preserve backward compatibility unless explicitly approved.
- Work in small incremental commits, one feature per commit.
- Keep the project buildable after every commit.
- Prefer composition over inheritance.
- Use dependency injection for external services.
- Keep provider interfaces swappable, including deterministic, live web, OpenAI, and marketplace.
- Never commit secrets or API keys.
- Update tests with every feature.
- Update documentation with every feature.
- Treat the Engineering Handbook as the source of truth.

## 20. Sprint Completion Policy

A sprint is complete only when:

- All planned deliverables are implemented.
- Unit, integration, and E2E tests pass.
- GitHub Actions is green.
- Documentation is updated.
- Engineering Handbook is updated.
- No known critical defects remain.

## Instructions To Codex

You are the lead software engineer for the Genesis AI project. Continue implementation from the current repository state rather than rebuilding existing functionality. Work incrementally, create production-quality code, keep the repository buildable after every commit, maintain tests and documentation, and complete the remaining sprint deliverables before moving to the next sprint. Treat this context as the authoritative project brief unless superseded by the repository itself.
