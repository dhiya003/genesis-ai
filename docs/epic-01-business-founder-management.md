# Epic 01 - Business & Founder Management

Status: Implemented deterministic v1 foundation

Epic 01 establishes the first-class founder and business context required before Genesis departments execute.

## Implemented Stories

- US-00001 Create Business
- US-00002 Configure Founder Profile
- US-00003 Define Business Vision
- US-00004 Define Business Goals
- US-00005 Define Business Constraints
- US-00006 Define Budget
- US-00007 Define Success Metrics
- US-00008 Configure Approval Policy
- US-00009 Create First Project
- US-00010 Launch Project Planning

## Runtime Capabilities

- Business creation with globally unique ID
- Mandatory business name, country, currency, and primary market validation
- Active or draft business status
- Creator and timestamps recorded
- Idempotency key support for duplicate business submissions
- Business dashboard with projects, vision, goals, constraints, budget, success metrics, approval policy, planning readiness, and audit history
- Founder profile create/edit with version history
- Business vision create/edit with active version and retained previous versions
- Multiple goals with target value, unit, target date, priority, editing, and archive support
- Versioned business constraints inherited by projects
- Budget categories with allocated, spent, remaining, and total remaining budget
- Success metrics with progress calculation
- Approval rules with thresholds and approval history
- Business projects default to draft and preserve founder profile, vision, and constraint snapshots
- Project planning validates business, vision, goals, and constraints before creating a planning workflow

## API

- `POST /businesses`
- `GET /businesses`
- `GET /businesses/{businessId}`
- `GET /businesses/{businessId}/dashboard`
- `POST /businesses/{businessId}/vision`
- `GET /businesses/{businessId}/vision`
- `POST /businesses/{businessId}/goals`
- `POST /businesses/{businessId}/goals/{goalId}`
- `GET /businesses/{businessId}/goals`
- `POST /businesses/{businessId}/constraints`
- `POST /businesses/{businessId}/constraints/{constraintId}`
- `GET /businesses/{businessId}/constraints`
- `POST /businesses/{businessId}/budget`
- `GET /businesses/{businessId}/budget`
- `POST /businesses/{businessId}/success-metrics`
- `GET /businesses/{businessId}/success-metrics`
- `POST /businesses/{businessId}/approval-policy`
- `GET /businesses/{businessId}/approval-policy`
- `POST /businesses/{businessId}/projects`
- `POST /businesses/{businessId}/projects/{projectId}/start-planning`
- `POST /founder/profile`
- `GET /founder/profile`

## CLI

```bash
python3 -m apps.cli.main founder create-business '{"name":"Luma Toys","country":"India","currency":"INR","primaryMarket":"Parents"}'
python3 -m apps.cli.main founder profile '{"name":"Dhiya","language":"en","timeZone":"Asia/Kolkata","currency":"INR"}'
python3 -m apps.cli.main founder dashboard <business-id>
python3 -m apps.cli.main founder vision <business-id> "Build India's best educational toy company."
python3 -m apps.cli.main founder goal <business-id> '{"type":"Revenue","targetValue":100000,"unit":"INR/month","targetDate":"2026-12-31"}'
python3 -m apps.cli.main founder constraint <business-id> '{"type":"Budget","description":"Keep first batch below INR 50000"}'
python3 -m apps.cli.main founder budget <business-id> '{"currency":"INR","categories":[{"category":"Research","allocated":10000,"spent":0}]}'
python3 -m apps.cli.main founder success-metric <business-id> '{"name":"Monthly revenue","unit":"INR","targetValue":100000,"currentValue":0,"timeHorizon":"monthly"}'
python3 -m apps.cli.main founder approval-policy <business-id> '{"rules":[{"type":"Budget","mode":"Manual","budgetThreshold":10000}]}'
python3 -m apps.cli.main founder project <business-id> '{"title":"Educational Wooden Toys"}'
python3 -m apps.cli.main founder start-planning <business-id> <project-id>
```

## Tests

Covered by `tests/test_founder_management.py`.

The tests verify business creation, idempotency, validation messages, dashboard visibility, profile versioning, vision versioning, goal editing, constraint versioning, budget remaining calculation, success metric progress, approval history, project inheritance, planning preconditions, workflow creation, API behavior, and CLI behavior.
