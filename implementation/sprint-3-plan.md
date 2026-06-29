# Sprint 3 Implementation Plan - Product Intelligence & Engineering

Release: v0.3.0
Status: Ready for Phase 1 implementation

## Goal

Implement the Product Department so Genesis can convert a validated Sprint 2 Research Report into production intelligence and, by the end of Sprint 3, a complete Product Blueprint.

## Phase 1 scope

Phase 1 implements Product Definition.

Deliverables:

- Product Definition Document
- Product Opportunity Report
- Product Variant Matrix
- Product Roadmap
- Product Constraints Report
- Product Success Metrics
- Product Risk Register
- Product Approval Checklist

## Phase 1 epics

### EPIC-S3-001 Product Department Skeleton

Create the Product Department package and manager orchestration.

Tasks:

- Add `apps/product` package.
- Add Product Department manager.
- Add deterministic Product Intelligence provider.
- Add Product Manager validation step.
- Route Product Department execution from a stored Research Report.

Acceptance criteria:

- Product Department can run without external API credentials.
- Output is deterministic in tests.
- Department execution records workflow, task, audit, execution history, and deliverable entries.

Priority: P0

### EPIC-S3-002 Product Definition Engine

Transform a Research Report into a Product Definition Document.

Tasks:

- Read validated research report fields.
- Select best opportunity.
- Generate product name, category, purpose, problem solved, target customer, age group, use case, story, differentiator, variants, and roadmap.
- Preserve evidence and assumptions.

Acceptance criteria:

- Product Definition Document contains all required fields.
- Missing or invalid research report input fails with a standard error.
- Output can be stored and retrieved.

Priority: P0

### EPIC-S3-003 Opportunity Ranking & Product Metrics

Score each product opportunity.

Tasks:

- Add ranking dimensions with 0-100 scores.
- Add Overall Opportunity Score.
- Add product metrics with 0-100 scores.
- Add rejection reasons for weak alternatives.

Acceptance criteria:

- All ranking and metric fields are present.
- Scores are bounded between 0 and 100.
- At least one rejected alternative is persisted with a reason.

Priority: P0

### EPIC-S3-004 Variants, Roadmap, Constraints, Risks, and Approval

Create the remaining Phase 1 deliverables.

Tasks:

- Add Product Variant Matrix.
- Add Product Roadmap.
- Add Product Constraints Report.
- Add Product Success Metrics.
- Add Product Risk Register.
- Add Product Approval Checklist.

Acceptance criteria:

- Variants include starter, standard, premium, bundle, subscription, accessories, and expansion packs.
- Constraints include budget, country, MOQ, manufacturing capability, shipping, storage, safety, margin, and time to market.
- Approval checklist validates problem clarity, manufacturability, shipping, scalability, branding, and product-family potential.

Priority: P0

### EPIC-S3-005 Product Knowledge Base

Persist institutional product intelligence.

Tasks:

- Store generated products.
- Store rejected products.
- Store alternatives and rejection reasons.
- Store lessons learned and future improvements.

Acceptance criteria:

- Knowledge base entries are written during Product Department execution.
- Entries are retrievable for a project.
- Tests prove both generated and rejected products are persisted.

Priority: P1

### EPIC-S3-006 API, CLI, Validation, and CI

Expose and verify Sprint 3 Phase 1.

Tasks:

- Add API endpoint to run Product Department from a project or report.
- Add API endpoint to retrieve Product Definition outputs.
- Add CLI command to run Product Department.
- Add CLI command to retrieve Product Definition outputs.
- Add JSON schema for Product Definition output.
- Add validation script.
- Add unit, integration, and e2e tests.
- Extend `scripts/verify.py`.

Acceptance criteria:

- API and CLI paths work end to end.
- Validation script passes against fixture data.
- `python3 scripts/verify.py` passes locally.
- GitHub Actions passes after push.

Priority: P0

## Sprint 3 Definition of Done

Sprint 3 is complete when:

- Product Department consumes a Sprint 2 Research Report.
- Product Department generates all Phase 1 through Phase 4 deliverables.
- Final Product Blueprint is schema-validated.
- API and CLI can run and retrieve Product Department outputs.
- Product Knowledge Base persists generated and rejected products.
- Local verification passes.
- GitHub Actions is green.
- Sprint 3 documentation is committed.
