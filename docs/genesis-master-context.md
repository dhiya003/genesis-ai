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
Founder
  -> CEO
  -> Departments
  -> Managers
  -> Employees
```

The operating model is not:

```text
User
  -> AI Agent
```

It is:

```text
CEO
  -> Departments
  -> Managers
  -> Employees
  -> Tasks
  -> Deliverables
```

Not prompts. Not agents. Actual virtual employees.

Genesis is not a SaaS product in the ordinary sense. Genesis is an AI Company. Software is one tool Genesis uses, but the thing Genesis creates is businesses.

All future design decisions should be judged against this question:

```text
Does this make Genesis a better AI Business Operating System?
```

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
- Manufacturing
- Procurement
- Branding
- Design
- Packaging
- Creative
- Marketing
- Publishing
- Sales
- Customer Success
- Analytics
- Finance
- Inventory
- CRM
- Operations
- Legal
- HR
- Strategy
- Customer Support

Every department follows the same contract:

```text
Mission
  -> Manager
  -> Employees
  -> Internal Workflow
  -> Deliverables
  -> Quality Validation
  -> Approval
  -> Output
```

Every future department should inherit this architecture unless a deliberate architecture decision says otherwise.

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

## 8.1 Employee Contract

Every employee must have:

- Employee ID
- Name
- Department
- Role
- Responsibilities
- Input schema
- Output schema
- Prompt contract
- Tool permissions
- Retry policy
- Timeout
- Memory scope
- KPIs
- Cost tracking
- Confidence score
- Evidence
- Validation

This contract applies to Research employees and all future employees across Product, Manufacturing, Creative, Marketing, Publishing, Analytics, Finance, Legal, Operations, and Customer Support.

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
  -> Product Design
  -> Manufacturing
  -> Creative
  -> Marketing
  -> Publishing
  -> Sales
  -> Analytics
  -> Optimization
```

without human intervention.

The deeper Product Factory vision is:

```text
Research
  -> Product Design
  -> Manufacturing
  -> Creative
  -> Marketing
  -> Publishing
  -> Sales
  -> Analytics
  -> Optimization
```

Everything revolves around building businesses, not generating isolated artifacts.

Genesis should be a universal business engine. It must not be specialized only for Amazon, Instagram, Shopify, Qikink, or any single provider. It should eventually support any viable business category, including:

- Amazon businesses
- Instagram businesses
- Shopify businesses
- Rental businesses
- Manufacturing businesses
- Toy companies
- Fashion brands
- Food brands
- Service businesses
- Local businesses

The long-term vision is:

```text
The operating system for starting and running businesses.
```

The personal founder vision is:

```text
Build the world's best AI Business Operating System, not just another agent framework.
```

## 16.1 AI Workforce Hierarchy

Genesis should evolve toward a company-like AI workforce hierarchy:

```text
CEO
  -> COO
  -> CTO
  -> Department Managers
  -> Senior Employees
  -> Junior Employees
```

This hierarchy is not decorative. It defines responsibility, escalation, approval, validation, and accountability.

## 16.2 Genesis Thinking Model

Genesis should not answer immediately.

Genesis should think and operate through this model:

```text
Receive Goal
  -> Understand Goal
  -> Plan
  -> Assign Department
  -> Assign Employees
  -> Collect Outputs
  -> Validate
  -> Improve
  -> Deliver
```

Planning-first execution is fundamental. Any implementation that jumps directly from founder input to final answer is architecturally incomplete.

## 16.3 Founder Mode

The founder should not micromanage the system.

Founder Mode means:

- Founder gives the business goal.
- Genesis plans and executes the operating work.
- Founder approves strategic decisions.
- Genesis handles research, analysis, production steps, validation, and iteration.

Approval gates should exist for strategic decisions, spend, publishing, legal/compliance, brand direction, and other high-impact choices.

## 16.4 Continuous Improvement Loop

Genesis is never a one-time execution engine.

Every business should feed a learning loop:

```text
Business
  -> Results
  -> Analytics
  -> Knowledge Base
  -> Better Future Decisions
```

Genesis should always ask:

```text
Can this business become better?
  -> Research again
  -> Improve
  -> Repeat
```

Every completed business, launch, campaign, and product should become training data for future decisions.

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

Sprint never ends with "code written." A sprint ends only after:

```text
Code
  -> Tests
  -> Validation
  -> CI
  -> Documentation
  -> Handbook
  -> Release
  -> Complete
```

## Instructions To Codex

You are the lead software engineer for the Genesis AI project. Continue implementation from the current repository state rather than rebuilding existing functionality. Work incrementally, create production-quality code, keep the repository buildable after every commit, maintain tests and documentation, and complete the remaining sprint deliverables before moving to the next sprint. Treat this context as the authoritative project brief unless superseded by the repository itself.
