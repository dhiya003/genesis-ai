# Genesis Sprint 6 - Business Execution & Publishing Engine

Release: v0.6.0

## Objective

Sprint 6 transforms Genesis from a planning platform into an approval-gated execution platform.

Sprint 6 answers:

> Take everything we planned and execute it safely.

## Primary Deliverable

Business Launch Package.

The package is generated from the Sprint 5 Marketing Pack and contains the execution plan, approval gates, asset manifest, launch checklist, publishing actions, notification plan, rollback plan, and launch report.

## Department

Publishing Department.

Department manager: Business Launch Manager.

Responsibilities:

- Launch coordination
- Publishing preparation
- Listing management
- Approval workflow
- Launch validation
- Rollback planning

## Employees

- EMP-201 Marketplace Publisher
- EMP-202 Social Publisher
- EMP-203 Content Scheduler
- EMP-204 Asset Manager
- EMP-205 Store Manager
- EMP-206 Campaign Launcher
- EMP-207 Approval Manager
- EMP-208 Notification Manager

Each employee includes input schema, output schema, prompt contract, retry policy, timeout, validation gates, metrics, confidence, and risk tracking.

## Implemented MVP Scope

The v0.6.0 deterministic MVP prepares execution-ready launch artifacts. It does not publish live content, spend ad budget, or mutate marketplace/store/social accounts without future live integrations and founder approval.

Implemented:

- Business Launch Package generation
- Marketplace publishing plan
- Social publishing plan
- Content schedule with timezone
- Asset repository manifest
- Store management plan
- Campaign launch plan
- Approval gates
- Notification plan
- Rollback plan
- Launch validation
- Launch report
- Persistence for package, checklist, asset manifest, publishing plan, and launch report
- API and CLI retrieval
- Unit, integration, and HTTP e2e tests

## APIs

- `POST /launch/generate`
- `GET /launch/{id}`
- `GET /launch/{id}/package`
- `GET /launch/{id}/status`
- `GET /launch/{id}/assets`
- `GET /launch/{id}/report`
- `GET /launch/{id}/checklist`

## CLI

```bash
python3 -m apps.cli.main launch generate <marketing-id>
python3 -m apps.cli.main launch package <launch-id>
python3 -m apps.cli.main launch status <launch-id>
python3 -m apps.cli.main launch assets <launch-id>
python3 -m apps.cli.main launch report <launch-id>
python3 -m apps.cli.main launch checklist <launch-id>
```

## Founder Acceptance Test

Input flow:

```text
Founder idea
-> Research Report
-> Product Blueprint
-> Creative Pack
-> Marketing Pack
-> Business Launch Package
```

Expected outcome:

- Marketplace listings prepared
- Social publishing actions prepared
- Content schedule generated
- Asset manifest generated
- Store catalog/pricing/inventory plan generated
- Campaign launch drafts prepared
- Approval gates generated
- Founder notifications prepared
- Rollback plan generated
- Launch report generated
- No live publishing or spend occurs without approval

## Live Integration Boundary

Live execution will require provider credentials for Shopify, Meta/Instagram/Facebook, Amazon, email, WhatsApp, Google Drive, and ad platforms. Until those credentials and approval policies are active, Genesis remains in deterministic draft-and-approval mode.

