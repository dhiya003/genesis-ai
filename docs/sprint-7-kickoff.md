# Genesis Sprint 7 - Business Intelligence Platform

Release: v0.7.0

## Objective

Sprint 7 transforms Genesis from an execution platform into a continuous business intelligence partner.

Sprint 7 answers:

> How is my business performing, why is it performing that way, and what should I do next?

## Primary Deliverable

Business Intelligence Dashboard.

## Department

Analytics Department.

Department manager: Chief Business Analyst.

## Planned Employees

- Sales Analyst
- Marketing Analyst
- Customer Analyst
- Product Analyst
- Competitor Watch
- Trend Monitor
- Recommendation Engine
- Forecasting Engine

## Required Capabilities

- Continuous monitoring
- Business health scoring
- Opportunity detection
- Risk detection
- Learning engine
- Knowledge base
- Alerts
- Forecasting
- Founder dashboard
- Department dashboards
- Campaign, sales, inventory, marketing, and financial dashboards

## Sprint 7 Acceptance Direction

Genesis should stop waiting for prompts after launch. It should observe available metrics, explain performance, identify meaningful changes, recommend prioritized actions, and keep strategic decisions with the founder.

## Dependency On Sprint 6

Sprint 7 consumes the launch package, launch report, channel mappings, campaign plans, asset manifests, and future live execution events created by Sprint 6.

## Implemented Foundation

Genesis now supports deterministic metrics ingestion and continuous monitoring outputs:

- Business metric events
- Business Dashboard
- Department dashboards
- Campaign dashboard
- Sales dashboard
- Inventory dashboard
- Financial dashboard
- Business health refresh
- Alert generation
- Recommendation refresh
- Knowledge capture

## APIs

- `POST /businessos/{id}/metrics`
- `GET /businessos/{id}/dashboard`
- `GET /businessos/{id}/alerts`
- `GET /businessos/{id}/knowledge`
- `GET /businessos/{id}/metrics`

## CLI

```bash
python3 -m apps.cli.main businessos ingest-metrics <business-id> '{"revenue": 60000, "orders": 50, "adSpend": 40000, "inventoryOnHand": 12}'
python3 -m apps.cli.main businessos dashboard <business-id>
python3 -m apps.cli.main businessos alerts <business-id>
python3 -m apps.cli.main businessos knowledge <business-id>
python3 -m apps.cli.main businessos metrics <business-id>
```

The foundation accepts manual or integration-provided metrics. Live connectors can post into the same metric ingestion boundary later.
